---
name: connection-route-aggregation-auto-attach
description: Automatically attaches the applicable route aggregation policy to a newly created BGP routing protocol, and reports the reduction in advertised routes.
categories: ["Deploy & Change Agents"]
---

# Connection Route Aggregation Auto-Attach Agent

## Overview
An Equinix agent that reacts to a newly created BGP routing protocol on a Fabric Cloud Router (FCR) connection and applies the route aggregation policy that connection is supposed to carry.
The agent resolves the connection from the cloud event, confirms it is FCR-backed with a BGP routing protocol, checks whether a route aggregation is already attached, selects the applicable policy deterministically from a caller-supplied policy map, measures the advertised route count before attaching, attaches the policy, verifies the attachment reached `ATTACHED`, re-measures the advertised route count, and emails a report.
Route aggregation policies that are applied by hand end up applied inconsistently across connections, so this agent applies them at routing-protocol creation time and shows the resulting route-count reduction.
This agent only executes once per cloud event.

## Capabilities
- Detect newly created BGP routing protocols and newly provisioned connections from the cloud event stream
- Resolve the connection and confirm it is FCR-backed with a BGP routing protocol eligible for aggregation
- Detect connections with no route aggregation policy attached
- Select the applicable route aggregation policy deterministically from an ordered policy map matched on connection type, A-side/Z-side metro, project, or connection name
- Validate the selected policy is provisioned, address-family compatible, and has at least one rule before attaching
- Attach the route aggregation policy, skipping connections that already have one (idempotent)
- Verify the attachment reached `ATTACHED` and report `PENDING_BGP_CONFIGURATION` or `FAILED` outcomes
- Measure the advertised route count before and after attachment and report the reduction
- Support a dry-run mode that reports the intended attachment without changing anything
- Log every action and decision, and email a completion report

## Prerequisites
- IAM role required: `Fabric Cloud Router Manager` or `Fabric Manager` (route aggregation attachment requires operator-or-above scope)
- To receive events from your connections you must first set up a stream, attach the connection resources to it, and subscribe to the routing-protocol and connection lifecycle event types (`equinix.fabric.routing_protocol_action.state.provisioned`, `equinix.fabric.connection.state.provisioned`)
- The route aggregation policies referenced in `route_aggregation_policy_map` must already exist, be in `PROVISIONED` state, and have their route aggregation rules created
- Route aggregation applies to BGP sessions on FCR-backed connections: the target connection must have an A-side Fabric Cloud Router and a BGP routing protocol whose address family matches the policy type (`BGP_IPv4_PREFIX_AGGREGATION` needs `bgpIpv4`, `BGP_IPv6_PREFIX_AGGREGATION` needs `bgpIpv6`)

## Available Tools
This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection. Used with the /uuid property to resolve the connection from the event and read its type, A-side/Z-side metro codes, A-side router UUID, project ID, name, and Equinix status.
*   **`list_routing_protocols`**: Lists all routing protocols for a connection. Used to confirm a BGP routing protocol exists and to read the bgpIpv4 and bgpIpv6 enabled flags for address-family matching.
*   **`list_route_aggregations_for_connection`**: Gets the route aggregations already attached to a connection. Each item exposes the policy UUID, type, and attachment status (ATTACHING, ATTACHED, DETACHING, DETACHED, FAILED, PENDING_BGP_CONFIGURATION). Used both for the idempotency check and for post-attach verification — pass a single route aggregation UUID to read just that attachment.
*   **`match_policy_rules`**: Selects which policy applies to a subject by walking an ordered rule list and returning the first rule whose criteria all hold, plus a trace of every rule examined. Used to pick the route aggregation policy for this connection — the selection must not be reasoned through by hand.
*   **`get_route_aggregation`**: Retrieves a route aggregation policy by UUID. Used to confirm the selected policy exists, is PROVISIONED, and to read its type.
*   **`list_route_aggregation_rules`**: Lists the rules under a route aggregation policy. Used to confirm the policy is not empty before attaching it.
*   **`search_routes`**: Searches the routing table of a Fabric Cloud Router. Used with route_type advertised and the connection UUID to read the advertised route count from the response pagination total, before and after attachment.
*   **`attach_route_aggregation`**: Attaches a route aggregation policy to a connection. Takes the connection UUID and the route aggregation UUID; unlike a route filter, it has no direction.
*   **`wait`**: Waits for a specified number of milliseconds before the next action.
*   **`send_email_notification`**: Sends an email notification. Pass a PDF title and PDF content to auto-generate and attach a PDF report.

## Instructions

### Step 1 — Parse the Cloud Event and Resolve the Connection
1a. Read the event `type`. Continue only for `equinix.fabric.routing_protocol_action.state.provisioned` and `equinix.fabric.connection.state.provisioned`. For any other event type, stop without action.

1b. Extract the connection UUID from the event `subject`:
- Routing protocol events: `/fabric/v4/connections/<connection-uuid>/routingProtocols/<routing-protocol-uuid>` — retain the routing protocol UUID for the report.
- Connection events: `/fabric/v4/connections/<connection-uuid>`

Never fabricate a connection UUID. If the subject cannot be parsed, log the raw subject and stop.

1c. Apply the configured scope gates. If `connection_uuids` is set and the event connection is not in that list, stop without action. If `connection_types` is set, the connection type must be in that list. If `project_uuid` is set, the connection must belong to that project (both verified in Step 1d).

1d. Call `search_connections` filtered on `/uuid` = the event connection UUID. Record `name`, `type`, `aSide/accessPoint/location/metroCode`, `zSide/accessPoint/location/metroCode`, `aSide/accessPoint/router/uuid`, `project/projectId`, and `operation/equinixStatus`. If the connection is not found, or `operation/equinixStatus` is not `PROVISIONED`, mark the run as **skipped** (reason: connection not found / not provisioned) and go to Step 8.

1e. If the connection has no A-side router UUID, mark the run as **skipped** (reason: not FCR-backed — route aggregation applies to Fabric Cloud Router connections) and go to Step 8. A port-to-port or IPWAN-to-port connection is not an error. Retain the router UUID as the FCR for Step 5.

### Step 2 — Confirm BGP Eligibility
2a. Call `list_routing_protocols` with the `connection_uuid`.

2b. Collect every routing protocol with `type` = `BGP` and note which address families are enabled (`bgpIpv4.enabled`, `bgpIpv6.enabled`).

2c. If there is no `BGP` routing protocol, mark the run as **skipped** (reason: no BGP routing protocol — route aggregation applies to BGP sessions only) and go to Step 8. A `DIRECT`-only connection is not an error.

### Step 3 — Check for an Existing Route Aggregation
3a. Call `list_route_aggregations_for_connection` with the `connection_uuid` and no `route_aggregation_uuid` to get every existing attachment.

3b. Treat a policy type as already covered when an attachment of that type has `attachmentStatus` of `ATTACHED`, `ATTACHING`, or `PENDING_BGP_CONFIGURATION`. Attachments in `DETACHED`, `DETACHING`, or `FAILED` do not count as covered.

3c. If the type the policy map would target is already covered, mark the run as **skipped** (reason: route aggregation already attached) and go to Step 8. Never detach or replace an existing route aggregation — this agent only fills gaps.

### Step 4 — Select and Validate the Applicable Policy
4a. Call `match_policy_rules` to select the policy. Do not compare the connection against the policy map by reasoning — the selection must be deterministic and auditable, so always take exactly what the tool returns. Pass:
- `attributes`: the connection facts from Step 1d, as `connectionType`, `aSideMetro`, `zSideMetro`, `projectId`, and `connectionName`. Omit an attribute the connection does not have rather than passing a placeholder.
- `rules`: `route_aggregation_policy_map` verbatim, in the order configured.

Retain the returned `trace` for the log and the report — it records why each rule was rejected and which one won.

4b. If the response has `matched` = `false`, mark the run as **skipped** (reason: no applicable route aggregation policy) and go to Step 8. Otherwise read `route_aggregation_uuid` from the returned `result`, and keep `ruleIndex` and `match` for the report.

4c. Validate the selected policy with `get_route_aggregation`:
- The policy must exist and be in `PROVISIONED` state; otherwise mark **failed** (reason: policy missing or not provisioned).
- Read the policy `type`. `BGP_IPv4_PREFIX_AGGREGATION` requires `bgpIpv4.enabled` = `true` on a BGP routing protocol from Step 2; `BGP_IPv6_PREFIX_AGGREGATION` requires `bgpIpv6.enabled` = `true`. On a mismatch, mark **skipped** (reason: address family mismatch).

4d. Call `list_route_aggregation_rules` with the policy UUID. If the policy has zero rules and `require_non_empty_rules` is `true` (the default), mark **skipped** (reason: route aggregation policy has no rules) — an empty policy aggregates nothing, so attaching it only creates the appearance of coverage. Only proceed with an empty policy when `require_non_empty_rules` is explicitly `false`.

### Step 5 — Measure the Advertised Route Count
5a. Call `search_routes` with the A-side `router_uuid` from Step 1e, `route_type` = `advertised`, the `connection_uuid`, and the default query (`pagination` `offset` = 0, `limit` = 20). Read the route count from the response `pagination` `total` — do not page through the entries; only the total is needed.

5b. Record this as the **before** count. If the call fails or returns no total, record the before count as unavailable and continue — the measurement is for the report, so it must never block the attachment.

### Step 6 — Attach and Verify
6a. If `dry_run` is `true`, record the intended attachment (connection UUID, policy UUID, policy type, and the matched rule index) as **dry-run** and go to Step 8 without calling `attach_route_aggregation`.

6b. Call `attach_route_aggregation` with the `connection_uuid` and the selected `route_aggregation_uuid`. On an error response, record connection UUID, policy UUID, and the error message as **failed** and go to Step 8.

6c. Call `wait` for `verification_wait_ms` milliseconds (default `5000`), then call `list_route_aggregations_for_connection` with the `connection_uuid` and the `route_aggregation_uuid` to read that single attachment's `attachmentStatus`.

6d. Repeat 6c up to `verification_attempts` times (default `6`) until the status settles:
- `ATTACHED` — record as **attached** and stop polling.
- `PENDING_BGP_CONFIGURATION` — record as **pending BGP configuration**: the attachment is accepted and will activate once BGP is configured. Stop polling; this is not a failure.
- `FAILED` — record as **failed** with the returned status and stop polling.
- `ATTACHING` — keep polling. If it is still `ATTACHING` after the last attempt, record as **pending verification** with the last observed status.

### Step 7 — Measure the Route-Count Reduction
7a. Only when Step 6 recorded **attached**. For any other outcome, skip this step and state in the report that no after count was taken because the aggregation was not active.

7b. Call `wait` for `route_count_settle_ms` milliseconds (default `30000`) to let the aggregated advertisement propagate.

7c. Repeat the Step 5a call unchanged and record the **after** count.

7d. Compute the reduction as before minus after, and the reduction percentage when the before count is greater than zero. Report all three figures. Do not present the reduction as a benefit when the after count is greater than or equal to the before count — state the observed numbers as they are, and note that aggregation may not yet have propagated.

### Step 8 — Send the Report
8a. Compose `pdfContent` in memory. When inserting a single line break, use `<br/>` instead of `<br>`.

```
<div class="header">
    <h1>Route Aggregation Auto-Attach Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Connection</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Action Taken</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Advertised Route Count</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Skipped or Failed</h2>
    <div class="content">
    </div>
</div>
```

Section content rules for `pdfContent`:
- **Summary**: The triggering event type, the outcome (attached / pending BGP configuration / pending verification / skipped / dry-run / failed), whether `dry_run` was in effect, and the policy-selection `trace` returned by `match_policy_rules`.
- **Connection**: Connection UUID, name, type, A-side and Z-side metro codes, A-side FCR UUID, project ID, the BGP routing protocol UUID(s) found, and the address families enabled.
- **Action Taken**: The matched policy-map rule index and its criteria, the route aggregation policy UUID and type, the rule count in the policy, and the final `attachmentStatus`. For a dry run, state the attachment that would have been made.
- **Advertised Route Count**: The before count, the after count, the reduction, and the reduction percentage. When either count is unavailable or Step 7 was skipped, state why.
- **Skipped or Failed**: The reason, using the exact reason recorded in Steps 1–6. If there is nothing to report, state "No skips or failures."

8b. Call `send_email_notification` with:
- `pdfContent`: the report from 8a.
- `body`: a one-paragraph summary naming the connection, the route aggregation policy, the outcome, and the advertised route count before and after.
- `pdfTitle`: `Route_Aggregation_Auto_Attach_Report`
- `emailAddresses`: `recipient_email_addresses`

## Guidelines
*   **Gap-Fill Only**: Never detach, replace, or modify an existing route aggregation attachment. The agent attaches a policy only where the policy type is uncovered.
*   **Idempotency**: Re-running on the same connection must not produce a second attachment. Always run the Step 3 check before Step 6, and treat `ATTACHED`, `ATTACHING`, and `PENDING_BGP_CONFIGURATION` as covered.
*   **Deterministic Policy Selection**: Rely on `match_policy_rules` for the policy-map walk. Do not compute, re-order, or second-guess the match through reasoning — attach exactly the policy the tool returns, and report its `trace` when explaining the decision.
*   **Validate Before Attaching**: Confirm the policy is `PROVISIONED`, address-family compatible, and non-empty. Attaching an empty or mismatched policy only creates the appearance of coverage.
*   **FCR and BGP Only**: Route aggregation applies to BGP sessions on FCR-backed connections. A connection with no A-side router or no BGP routing protocol is a skip, not a failure.
*   **Measurement Never Blocks**: The advertised route counts are reported, not gated on. A failed or unavailable `search_routes` call must not stop or reverse the attachment.
*   **Report Counts Honestly**: Report the observed before and after counts even when there is no reduction, and never infer a reduction that the counts do not show.
*   **Never Fabricate UUIDs**: Every connection, router, and route aggregation UUID must come from the cloud event, the configuration, or a tool response.
*   **Connection Tags Are Not Searchable**: Fabric connection tags are not exposed as a searchable connection property. Match policies on connection type, metro codes, project ID, or connection name instead.
*   **Error Handling**: If a tool call fails or a parameter is invalid, log the error with the connection UUID, record it in the report, and stop this run. Do not retry an `attach_route_aggregation` that returned an error.
*   **Rate Limiting**: Keep the `wait` between verification polls; do not poll `list_route_aggregations_for_connection` in a tight loop.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`route_aggregation_policy_map`**: < ordered list of policy rules > - Required - Passed straight to `match_policy_rules` as its `rules` argument, so each entry is an object with a `match` object of criteria and a `result` object holding `route_aggregation_uuid`. A criterion key is one of `connectionType`, `aSideMetro`, `zSideMetro`, `projectId`, or `connectionName`; its value is a string, an array of strings, or an operator object (`equals`, `notEquals`, `in`, `notIn`, `contains`, `notContains`). The first rule whose criteria all hold wins, and a final rule with an empty `match` acts as the default policy. Example:
    ```
    [
      {"match": {"aSideMetro": ["SV", "DA"], "connectionType": "EVPL_VC"},
       "result": {"route_aggregation_uuid": "201b7346-a9eb-42fe-ae7a-08148c71928d"}},
      {"match": {"connectionName": {"contains": "prod"}},
       "result": {"route_aggregation_uuid": "3f2a1c88-77bd-4e19-9c3a-5d1e8b40f6aa"}},
      {"match": {},
       "result": {"route_aggregation_uuid": "9c4e0d21-6a5b-4f70-b8d2-1e77a9c3b455"}}
    ]
    ```
* **`connection_uuids`**: < list of connection UUIDs > - Optional - When set, only events for these connections are acted on.
* **`connection_types`**: < list of connection types > - Optional - When set, only these connection types are acted on (for example `EVPL_VC`, `IP_VC`).
* **`project_uuid`**: < A project UUID > - Optional - When set, only connections in this project are acted on.
* **`require_non_empty_rules`**: `true` | `false` - Optional - Skip a route aggregation policy that has no rules; default `true`.
* **`dry_run`**: `true` | `false` - Optional - Report the intended attachment without calling `attach_route_aggregation`; default `false`.
* **`verification_attempts`**: <integer> - Optional - Maximum attachment-status polls after attaching; default `6`.
* **`verification_wait_ms`**: <integer> - Optional - Milliseconds to wait between attachment-status polls; default `5000`.
* **`route_count_settle_ms`**: <integer> - Optional - Milliseconds to wait after a successful attachment before re-measuring the advertised route count; default `30000`.
* **`recipient_email_addresses`**: < list of email addresses > - Required - Recipients for the completion report.
