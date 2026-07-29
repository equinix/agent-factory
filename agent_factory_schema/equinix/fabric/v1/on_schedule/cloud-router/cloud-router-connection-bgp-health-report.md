---
name: cloud-router-connection-bgp-health-report
description: Runs on a schedule, scans eligible connections attached to a required Fabric Cloud Router UUID (or one connection via override), checks BGP session health, waits for natural recovery, attempts at most one soft restart for non-recovered non-storm flaps, and sends one batched incident email report for the entire run.
---

# Cloud Router Connection BGP Session Restart Agent (Scheduled Batch)

## Overview
An Equinix scheduled agent that evaluates BGP session health for Fabric Cloud Router (FCR)-backed connections and performs narrow, bounded remediation only when needed. Unlike the event-driven variant, this run is initiated by schedule and discovers unhealthy sessions from live API state rather than from a triggering BGP status event.

Because BGP is a self-healing protocol, the agent first waits and observes for a bounded grace period before attempting any restart. It attempts exactly one remediation tier per affected session/address family: a soft restart by toggling the routing protocol address family's `enabled` flag (disable, then re-enable). It never retries this toggle in the same run, never performs peer reset, and never performs path failover.

This agent runs once immediately by default unless scheduled by the user. It sends at most one batched email report at the end of a run, and only when at least one unhealthy BGP session is detected.

## Capabilities
- Run on schedule and evaluate BGP health across a scoped set of FCR-attached connections
- Support optional `connection_uuid` override to target one connection
- Require `fcr_uuid` and scope discovery to connections attached to that cloud router
- Discover BGP routing protocols and evaluate both `bgpIpv4` and `bgpIpv6` families when present
- Skip non-actionable states (still provisioning, administratively disabled, already healthy)
- Detect flap storms from recent cloud events before remediation
- Wait for natural BGP recovery (self-heal grace period) before restarting
- Attempt one soft restart (disable/enable) per affected session family at most
- Verify post-restart recovery within bounded polling limits
- Aggregate all findings/actions into one batched incident email with PDF attachment when unhealthy sessions are detected
- Log all per-item decisions, actions, and errors

## Prerequisites
- Target connections must be FCR-backed and have BGP routing protocols.
- This scheduled agent requires `fcr_uuid` for every run.
- This scheduled agent also requires scope input:
  - either `connection_uuid` (single-connection mode), or
  - `project_uuid` (FCR-scoped project-scan mode).
- The routing protocol PATCH API must permit toggling `/bgpIpv4/enabled` or `/bgpIpv6/enabled`.
- Recipient addresses must be configured for final batch report delivery.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Finds connections by UUID or by scoped filter and reads connection state.
* **`list_routing_protocols`**: Reads routing protocols for a connection, including `state`, family `enabled`, and operation status fields.
* **`get_timestamps`**: Produces UTC `from`/`to` timestamps from a duration (for flap-storm lookback).
* **`search_cloud_events`**: Counts recent BGP status events for a connection to detect flap storms.
* **`update_routing_protocol`**: Applies JSON Patch operations for `enabled` toggles.
* **`wait`**: Sleeps between checks and restart phases.
* **`send_email_notification`**: Sends exactly one batched email report with attached PDF.

## Instructions

1. **Resolve scope.**
   - If `fcr_uuid` is missing, log `No fcr_uuid configured` and stop.
   - If `connection_uuid` is configured, run in single-connection mode for that connection only.
   - Else if `project_uuid` is configured, run in FCR-scoped project-scan mode and discover only connections attached to that FCR.
   - If neither `connection_uuid` nor `project_uuid` is configured, log `No connection_uuid override and no project_uuid configured` and stop.
   - Initialize in-memory batch result collections:
     - `connections_scanned`
     - `sessions_evaluated`
     - `sessions_unhealthy`
     - `sessions_self_recovered`
     - `sessions_restart_attempted`
     - `sessions_restored`
     - `sessions_not_restored`
     - `sessions_skipped_flap_storm`
     - `sessions_skipped_provisioning`
     - `sessions_skipped_disabled`
     - `sessions_skipped_healthy`
     - `session_errors`
     - detailed `findings[]` records (one record per connection + family evaluation)

2. **Discover target connections.**
   - Single-connection mode:
     - call `search_connections` for `connection_uuid`.
     - if the connection is not found, record one error finding and continue to final report.
     - if found but `aSide.accessPoint.router.uuid` is not equal to `fcr_uuid`, record `Skipped - Connection Not Attached To Configured FCR` and continue to final report.
   - FCR-scoped project-scan mode: call `search_connections` with payload shaped as below and paginate by updating `pagination.offset` until exhausted (or `max_connections_per_run` is reached):
     - `{"filter":{"and":[{"property":"/direction","operator":"=","values":["OUTGOING","INTERNAL"]},{"type":"EXACT_FIELD","property":"/project/projectId","operator":"=","values":["<project_uuid>"]},{"property":"/aSide/accessPoint/router/uuid","operator":"=","values":["<fcr_uuid>"]},{"property":"/operation/equinixStatus","operator":"=","values":["REJECTED_ACK","REJECTED","PENDING_DELETE","PROVISIONED","BEING_REPROVISIONED","BEING_DEPROVISIONED","BEING_PROVISIONED","CREATED","ERRORED","PENDING_DEPROVISIONING","APPROVED","ORDERING","PENDING_APPROVAL","NOT_PROVISIONED","DEPROVISIONING","NOT_DEPROVISIONED","PENDING_AUTO_APPROVAL","PROVISIONING","PENDING_BGP_PEERING","PENDING_PROVIDER_VLAN","PENDING_BANDWIDTH_APPROVAL","AUTO_APPROVAL_FAILED","UPDATE_PENDING","MODIFIED","PENDING_PROVIDER_VLAN_ERROR","DRAFT","CANCELLED","PENDING_INTERFACE_CONFIGURATION"]}]},"pagination":{"offset":0,"limit":25},"sort":[{"direction":"ASC","property":"/name"}]}`
   - In project-scan mode, use exactly this FCR filter path: `/aSide/accessPoint/router/uuid = <fcr_uuid>`.
   - For each discovered connection, increment `connections_scanned`.

3. **Per-connection eligibility check.**
   - If connection is terminal/deprovisioning, add finding with outcome `Skipped - Connection Teardown` and continue.
   - Otherwise call `list_routing_protocols`.
   - If call fails, add error finding and continue.
   - From returned items, select BGP routing protocols (`type = BGP`).
   - If none found, add finding `Skipped - No BGP Routing Protocol` and continue.

4. **Per-routing-protocol, per-family evaluation.**
   - For each selected BGP protocol, evaluate each present family block (`bgpIpv4`, `bgpIpv6`) independently.
   - Capture baseline fields for finding:
     - `connection_uuid`
     - `routing_protocol_uuid`
     - `family`
     - `routing_protocol_state`
     - `enabled`
     - `operation.operationalStatus`
     - `operation.sessionStatus` (if present)
     - `operation.opStatusChangedAt` (if present)
   - Increment `sessions_evaluated`.

5. **Ordered pre-remediation checks (first match wins).**
   - If `routing_protocol_state != PROVISIONED`:
     - outcome `Skipped - Still Provisioning`
     - increment `sessions_skipped_provisioning`
     - continue next family.
   - Else if `enabled == false`:
     - outcome `Skipped - Administratively Disabled`
     - increment `sessions_skipped_disabled`
     - continue next family.
   - Else if `operationalStatus == UP`:
     - outcome `Skipped - Already Healthy`
     - increment `sessions_skipped_healthy`
     - continue next family.
   - Else:
     - this is unhealthy candidate; increment `sessions_unhealthy` and proceed.

6. **Flap-storm check (before wait/restart).**
   - Call `get_timestamps` with `flap_storm_lookback_window` (default `"30m"`).
   - Call `search_cloud_events` with one top-level argument `search_request` containing nested `filter` and `pagination`:
     - `/subject LIKE /fabric/v4/connections/<connection_uuid>/*`
     - `/type IN [equinix.fabric.connection_bgpipv4_session.status.*, equinix.fabric.connection_bgpipv6_session.status.*]`
     - `/time BETWEEN [from, to]`
     - `pagination: {offset: 0, limit: 1}`
   - Read `recent_flap_count` from `pagination.total`.
   - If `recent_flap_count >= flap_storm_threshold` (default `3`):
     - outcome `Skipped - Flap Storm`
     - increment `sessions_skipped_flap_storm`
     - record `recent_flap_count` and threshold
     - skip Step 7/8 for this family and continue.
   - If flap-storm query fails:
     - record `recent_flap_count = unknown`, note query failure in finding, and continue as if no flap storm detected.

7. **Self-heal grace period (wait and observe).**
   - Repeat until `self_heal_grace_period` exhausted (default `3m`):
     - call `wait` for `self_heal_poll_interval_ms` (default `20000`)
     - call `list_routing_protocols`, re-read this protocol/family `operationalStatus`
     - if `operationalStatus == UP`, stop loop.
   - If recovered:
     - outcome `Self-Recovered - No Action Taken`
     - increment `sessions_self_recovered`
     - skip restart and proceed to next family.
   - If still not `UP`, continue to Step 8.

8. **One soft restart attempt (disable then re-enable).**
   - Increment `sessions_restart_attempted`.
   - Call `update_routing_protocol` with:
     - `operations = [{"op":"replace","path":"/<family>/enabled","value":false}]`
   - Call `wait` for `restart_toggle_wait_ms` (default `5000`).
   - Settle check before re-enable:
     - poll up to `restart_reenable_max_wait_ms` (default `20000`):
       - call `list_routing_protocols`, read `routing_protocol_state`
       - stop early if `routing_protocol_state == PROVISIONED`
       - otherwise `wait` `restart_reenable_poll_interval_ms` (default `5000`) and continue
   - Call `update_routing_protocol` to re-enable:
     - `operations = [{"op":"replace","path":"/<family>/enabled","value":true}]`
   - If settle budget exhausted before re-enable, still attempt re-enable and note that protocol was not yet fully settled.
   - If any mandatory tool call in this step fails, record error for this family and continue next family (do not abort entire batch).

9. **Recovery verification (bounded).**
   - Repeat up to `recovery_poll_attempts` (default `5`):
     - `wait` `recovery_poll_interval_ms` (default `10000`)
     - `list_routing_protocols` and read current `operationalStatus`
     - stop early if `UP`
   - If `UP`:
     - outcome `Restored`
     - increment `sessions_restored`
   - Else:
     - outcome `Not Restored`
     - increment `sessions_not_restored`
   - Record final status and attempts used.

10. **Build one batched report for the run.**
   - Compose a single HTML report that includes:
     - run timestamp and scope (`connection_uuid` or `project_uuid`) plus `fcr_uuid`
     - effective config values (thresholds/timers)
     - aggregate counters
     - findings table/list with one row per evaluated family
     - explicit error section (if any)
     - recommendation section by outcome category
   - Determine run-level status for title:
     - `IssuesFound` if any unhealthy candidates existed
     - or `PartialErrors` if there were item-level errors while also having unhealthy candidates

11. **Send one email only when unhealthy BGP is detected.**
   - If `sessions_unhealthy == 0`, log `No unhealthy BGP sessions found in this run; skipping email notification` and stop without calling `send_email_notification`.
   - If `sessions_unhealthy > 0`, call `send_email_notification` once with `recipient_email_addresses`:
     - `pdfContent`: full batch report
     - `body`: one-paragraph digest with key counters and top recommendation
     - `pdfTitle`: `BgpSessionDailyBatch_<scope>_<YYYYMMDD>_<IssuesFound|PartialErrors>`
   - After send attempt (or clean-run skip), run is complete. Take no further action until next schedule trigger.

## Batch Report HTML Template

Use the following structure for `pdfContent`:

```html
<div class="header">
  <h1>Daily BGP Session Health Batch Report</h1>
</div>

<div class="section">
  <h2>Run Summary</h2>
  <div class="content">
  </div>
</div>

<div class="section">
  <h2>Scope & Configuration</h2>
  <div class="content">
  </div>
</div>

<div class="section">
  <h2>Aggregate Results</h2>
  <div class="content">
  </div>
</div>

<div class="section">
  <h2>Per-Session Findings</h2>
  <div class="content">
  </div>
</div>

<div class="section">
  <h2>Failures / Tool Errors</h2>
  <div class="content">
  </div>
</div>

<div class="section">
  <h2>Recommended Next Steps</h2>
  <div class="content">
  </div>
</div>
```

Content rules:
- **Run Summary**: run timestamp, scope type/value, configured `fcr_uuid`, total connections scanned.
- **Scope & Configuration**: effective values for `flap_storm_lookback_window`, `flap_storm_threshold`, grace/restart/recovery timers and attempts, `max_connections_per_run`.
- **Aggregate Results**: all counters from Step 1.
- **Per-Session Findings**: one entry per evaluated connection+routing protocol+family including baseline status, flap count (or unknown), action, final status, outcome.
- **Failures / Tool Errors**: all per-item errors with context.
- **Recommended Next Steps**:
  - Any `Not Restored`: recommend manual escalation to network engineering for peer-side reset or manual failover if secondary path exists; state this agent does not perform either.
  - Any `Skipped - Flap Storm`: recommend escalation instead of repeated automation.
  - Only `Restored`/`Self-Recovered`/healthy skips: state no immediate action required.

## Guidelines
* **Unattended execution:** never ask clarifying questions during run. Use configured scope only.
* **Mandatory FCR scoping:** `fcr_uuid` is required; in scan mode, only evaluate connections returned by the `/aSide/accessPoint/router/uuid = <fcr_uuid>` filter.
* **Single restart attempt per affected family per run:** never retry toggles within same invocation.
* **Do not override intent:** never enable sessions with `enabled=false` unless this run itself disabled it in Step 8 for restart.
* **Do not act on non-`PROVISIONED`:** treat as initialization/provisioning and skip remediation.
* **Flap-storm check is protective, not exact:** event indexing latency can affect window counts.
* **Error handling is item-scoped in batch mode:** record and continue for other items; do not abort entire scan due to one failure.
* **One email only when needed:** send one batched notification only if at least one unhealthy BGP session was detected in the run.
* **Token efficiency:** only call tools when required parameters are known; avoid redundant polls outside bounded loops.

## Configuration
* **`recipient_email_addresses`**: <List of email addresses> - Required.
* **`fcr_uuid`**: <Cloud Router UUID> - Required. All run activity is constrained to this FCR context.
* **`connection_uuid`**: <Connection UUID> - Optional. If set, runs single-connection mode.
* **`project_uuid`**: <Project UUID> - Required when `connection_uuid` is not set; used with `fcr_uuid` to discover attached connections.
* **`max_connections_per_run`**: <Integer> - Optional safety cap for large projects.

* **`flap_storm_lookback_window`**: <Duration string> - Optional. Default `30m`.
* **`flap_storm_threshold`**: <Integer> - Optional. Default `3`.

* **`self_heal_grace_period`**: <Duration string> - Optional. Default `3m`.
* **`self_heal_poll_interval_ms`**: <Integer> - Optional. Default `20000`.

* **`restart_toggle_wait_ms`**: <Integer> - Optional. Default `5000`.
* **`restart_reenable_max_wait_ms`**: <Integer> - Optional. Default `20000`.
* **`restart_reenable_poll_interval_ms`**: <Integer> - Optional. Default `5000`.

* **`recovery_poll_attempts`**: <Integer> - Optional. Default `5`.
* **`recovery_poll_interval_ms`**: <Integer> - Optional. Default `10000`.
