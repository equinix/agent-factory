---
name: connection-route-filter-auto-attach
description: Automatically attaches the applicable route filter policy to a newly provisioned connection or BGP routing protocol, closing the policy gap left when a route filter is forgotten.
categories: ["Deploy & Change Agents"]
---

# Connection Route Filter Auto-Attach Agent

## Overview
An Equinix agent that reacts to a newly provisioned connection or a newly created BGP routing protocol and makes sure the connection carries a route filter policy.
The agent resolves the connection from the cloud event, confirms it has a BGP routing protocol, checks whether a route filter is already attached, selects the applicable route filter policy from a caller-supplied policy map (matched deterministically on connection type, metro, project, or connection name), attaches it in the configured direction, verifies the attachment reached `ATTACHED`, and emails a report of what was attached, skipped, or failed.
Forgetting to attach a route filter to a new connection leaves an unfiltered BGP session, so this agent enforces the routing policy at provisioning time instead of at audit time.
This agent only executes once per cloud event.

## Capabilities
- Detect newly provisioned connections and newly created BGP routing protocols from the cloud event stream
- Resolve the connection and confirm it has a BGP routing protocol eligible for route filtering
- Detect connections with no route filter attached in the required direction
- Select the applicable route filter policy deterministically from an ordered policy map matched on connection type, A-side/Z-side metro, project, or connection name
- Validate the selected policy is provisioned, address-family compatible, and has at least one rule before attaching
- Attach the route filter policy in the configured direction, skipping connections that already have one (idempotent)
- Verify the attachment reached `ATTACHED` and report `PENDING_BGP_CONFIGURATION` or `FAILED` outcomes
- Support a dry-run mode that reports the intended attachment without changing anything
- Log every action and decision, and email a completion report

## Prerequisites
- IAM role required: `Fabric Cloud Router Manager` or `Fabric Manager` (route filter attachment requires operator-or-above scope)
- To receive events from your connections you must first set up a stream, attach the connection resources to it, and subscribe to the connection and routing-protocol lifecycle event types (`equinix.fabric.connection.state.provisioned`, `equinix.fabric.routing_protocol_action.state.provisioned`)
- The route filter policies referenced in `route_filter_policy_map` must already exist, be in `PROVISIONED` state, and have their route filter rules created
- Route filters apply to BGP sessions only: the target connection must have a BGP routing protocol whose address family matches the policy type (`BGP_IPv4_PREFIX_FILTER` needs `bgpIpv4`, `BGP_IPv6_PREFIX_FILTER` needs `bgpIpv6`)

## Available Tools
This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection. Used with the /uuid property to resolve the connection from the event and read its type, A-side/Z-side metro codes, project ID, name, and Equinix status.
*   **`list_routing_protocols`**: Lists all routing protocols for a connection. Used to confirm a BGP routing protocol exists and to read the bgpIpv4 and bgpIpv6 enabled flags for address-family matching.
*   **`list_route_filters_for_connection`**: Gets the route filters already attached to a connection. Each item exposes the policy UUID, type, direction, and attachment status (ATTACHING, ATTACHED, DETACHING, DETACHED, FAILED, PENDING_BGP_CONFIGURATION). Used both for the idempotency check and for post-attach verification — pass a single route filter UUID to read just that attachment.
*   **`search_route_filters`**: Searches route filter policies. Used with the /uuid property to confirm the selected policy exists, is PROVISIONED, and to read its type.
*   **`match_policy_rules`**: Selects which policy applies to a subject by walking an ordered rule list and returning the first rule whose criteria all hold, plus a trace of every rule examined. Used to pick the route filter policy for this connection — the selection must not be reasoned through by hand.
*   **`list_route_filter_rules`**: Lists the rules under a route filter policy. Used to confirm the policy is not empty before attaching it.
*   **`attach_route_filter`**: Attaches a route filter policy to a connection. Takes the connection UUID, the route filter UUID, and a direction of INBOUND or OUTBOUND.
*   **`wait`**: Waits for a specified number of milliseconds before the next action.
*   **`send_email_notification`**: Sends an email notification. Pass a PDF title and PDF content to auto-generate and attach a PDF report.

## Instructions

### Step 1 — Parse the Cloud Event and Resolve the Connection
1a. Read the event `type`. Continue only for `equinix.fabric.connection.state.provisioned` and `equinix.fabric.routing_protocol_action.state.provisioned`. For any other event type, stop without action.

1b. Extract the connection UUID from the event `subject`:
- Connection events: `/fabric/v4/connections/<connection-uuid>`
- Routing protocol events: `/fabric/v4/connections/<connection-uuid>/routingProtocols/<routing-protocol-uuid>` — retain the routing protocol UUID for the report.

Never fabricate a connection UUID. If the subject cannot be parsed, log the raw subject and stop.

1c. Apply the configured scope gates. If `connection_uuids` is set and the event connection is not in that list, stop without action. If `project_uuid` is set, the connection must belong to that project (verified in Step 1d). If `connection_types` is set, the connection type must be in that list.

1d. Call `search_connections` filtered on `/uuid` = the event connection UUID. Record `name`, `type`, `aSide/accessPoint/location/metroCode`, `zSide/accessPoint/location/metroCode`, `project/projectId`, and `operation/equinixStatus`. If the connection is not found, or `operation/equinixStatus` is not `PROVISIONED`, mark the run as **skipped** (reason: connection not found / not provisioned) and go to Step 6.

### Step 2 — Confirm BGP Eligibility
2a. Call `list_routing_protocols` with the `connection_uuid`.

2b. Collect every routing protocol with `type` = `BGP` and note which address families are enabled (`bgpIpv4.enabled`, `bgpIpv6.enabled`).

2c. If there is no `BGP` routing protocol, mark the run as **skipped** (reason: no BGP routing protocol — route filters apply to BGP sessions only) and go to Step 6. A `DIRECT`-only connection is not an error.

### Step 3 — Check for an Existing Route Filter
3a. Call `list_route_filters_for_connection` with the `connection_uuid` and no `route_filter_uuid` to get every existing attachment.

3b. Treat a `(type, direction)` slot as already covered when an attachment for that pair has `attachmentStatus` of `ATTACHED`, `ATTACHING`, or `PENDING_BGP_CONFIGURATION`. Attachments in `DETACHED`, `DETACHING`, or `FAILED` do not count as covered.

3c. If every `(type, direction)` pair the policy map would target is already covered, mark the run as **skipped** (reason: route filter already attached) and go to Step 6. Never detach or replace an existing route filter — this agent only fills gaps.

### Step 4 — Select and Validate the Applicable Policy
4a. Call `match_policy_rules` to select the policy. Do not compare the connection against the policy map by reasoning — the selection must be deterministic and auditable, so always take exactly what the tool returns. Pass:
- `attributes`: the connection facts from Step 1d, as `connectionType`, `aSideMetro`, `zSideMetro`, `projectId`, and `connectionName`. Omit an attribute the connection does not have rather than passing a placeholder.
- `rules`: `route_filter_policy_map` verbatim, in the order configured.

Retain the returned `trace` for the log and the report — it records why each rule was rejected and which one won.

4b. If the response has `matched` = `false`, mark the run as **skipped** (reason: no applicable route filter policy) and go to Step 6. Otherwise read `route_filter_uuid` and `direction` from the returned `result`, and keep `ruleIndex` and `match` for the report.

4c. Validate the selected policy with `search_route_filters` filtered on `/uuid`:
- The policy must exist and be in `PROVISIONED` state; otherwise mark **failed** (reason: policy missing or not provisioned).
- Read the policy `type`. `BGP_IPv4_PREFIX_FILTER` requires `bgpIpv4.enabled` = `true` on a BGP routing protocol from Step 2; `BGP_IPv6_PREFIX_FILTER` requires `bgpIpv6.enabled` = `true`. On a mismatch, mark **skipped** (reason: address family mismatch).

4d. Call `list_route_filter_rules` with the policy UUID. If the policy has zero rules and `require_non_empty_rules` is `true` (the default), mark **skipped** (reason: route filter policy has no rules) — attaching an empty filter can drop the routes the connection depends on. Only proceed with an empty policy when `require_non_empty_rules` is explicitly `false`.

4e. If `dry_run` is `true`, record the intended attachment (connection UUID, policy UUID, policy type, direction, and the matched rule index) as **dry-run** and go to Step 6 without calling `attach_route_filter`.

### Step 5 — Attach and Verify
5a. Call `attach_route_filter` with the `connection_uuid`, the selected `route_filter_uuid`, and the selected `direction`. On an error response, record connection UUID, policy UUID, direction, and the error message as **failed** and go to Step 6.

5b. Call `wait` for `verification_wait_ms` milliseconds (default `5000`), then call `list_route_filters_for_connection` with the `connection_uuid` and the `route_filter_uuid` to read that single attachment's `attachmentStatus`.

5c. Repeat 5b up to `verification_attempts` times (default `6`) until the status settles:
- `ATTACHED` — record as **attached** and stop polling.
- `PENDING_BGP_CONFIGURATION` — record as **pending BGP configuration**: the attachment is accepted and will activate once BGP is configured. Stop polling; this is not a failure.
- `FAILED` — record as **failed** with the returned status and stop polling.
- `ATTACHING` — keep polling. If it is still `ATTACHING` after the last attempt, record as **pending verification** with the last observed status.

### Step 6 — Send the Report
6a. Compose `pdfContent` in memory. When inserting a single line break, use `<br/>` instead of `<br>`.

```
<div class="header">
    <h1>Route Filter Auto-Attach Report</h1>
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
    <h2>Skipped or Failed</h2>
    <div class="content">
    </div>
</div>
```

Section content rules for `pdfContent`:
- **Summary**: The triggering event type, the outcome (attached / pending BGP configuration / pending verification / skipped / dry-run / failed), whether `dry_run` was in effect, and the policy-selection `trace` returned by `match_policy_rules`.
- **Connection**: Connection UUID, name, type, A-side and Z-side metro codes, project ID, the BGP routing protocol UUID(s) found, and the address families enabled.
- **Action Taken**: The matched policy-map rule index and its criteria, the route filter policy UUID and type, the direction attached, and the final `attachmentStatus`. For a dry run, state the attachment that would have been made.
- **Skipped or Failed**: The reason, using the exact reason recorded in Steps 1–5. If there is nothing to report, state "No skips or failures."

6b. Call `send_email_notification` with:
- `pdfContent`: the report from 6a.
- `body`: a one-paragraph summary naming the connection, the route filter policy, the direction, and the outcome.
- `pdfTitle`: `Route_Filter_Auto_Attach_Report`
- `emailAddresses`: `recipient_email_addresses`

## Guidelines
*   **Gap-Fill Only**: Never detach, replace, or modify an existing route filter attachment. The agent attaches a policy only where a `(type, direction)` slot is uncovered.
*   **Idempotency**: Re-running on the same connection must not produce a second attachment. Always run the Step 3 check before Step 5, and treat `ATTACHED`, `ATTACHING`, and `PENDING_BGP_CONFIGURATION` as covered.
*   **Validate Before Attaching**: Confirm the policy is `PROVISIONED`, address-family compatible, and non-empty. Attaching an empty or mismatched filter is worse than attaching nothing.
*   **BGP Only**: Route filters apply to BGP sessions. A connection with no BGP routing protocol is a skip, not a failure.
*   **Never Fabricate UUIDs**: Every connection and route filter UUID must come from the cloud event, the configuration, or a tool response.
*   **Deterministic Policy Selection**: Rely on `match_policy_rules` for the policy-map walk. Do not compute, re-order, or second-guess the match through reasoning — attach exactly the policy the tool returns, and report its `trace` when explaining the decision.
*   **Connection Tags Are Not Searchable**: Fabric connection tags are not exposed as a searchable connection property. Match policies on connection type, metro codes, project ID, or connection name instead.
*   **Error Handling**: If a tool call fails or a parameter is invalid, log the error with the connection UUID, record it in the report, and stop this run. Do not retry an `attach_route_filter` that returned an error.
*   **Rate Limiting**: Keep the `wait` between verification polls; do not poll `list_route_filters_for_connection` in a tight loop.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`route_filter_policy_map`**: < ordered list of policy rules > - Required - Passed straight to `match_policy_rules` as its `rules` argument, so each entry is an object with a `match` object of criteria and a `result` object holding `route_filter_uuid` and `direction` (`INBOUND` or `OUTBOUND`). A criterion key is one of `connectionType`, `aSideMetro`, `zSideMetro`, `projectId`, or `connectionName`; its value is a string, an array of strings, or an operator object (`equals`, `notEquals`, `in`, `notIn`, `contains`, `notContains`). The first rule whose criteria all hold wins, and a final rule with an empty `match` acts as the default policy. Example:
    ```
    [
      {"match": {"aSideMetro": ["SV", "DA"], "connectionType": "EVPL_VC"},
       "result": {"route_filter_uuid": "201b7346-a9eb-42fe-ae7a-08148c71928d", "direction": "INBOUND"}},
      {"match": {"connectionName": {"contains": "prod"}},
       "result": {"route_filter_uuid": "3f2a1c88-77bd-4e19-9c3a-5d1e8b40f6aa", "direction": "INBOUND"}},
      {"match": {},
       "result": {"route_filter_uuid": "9c4e0d21-6a5b-4f70-b8d2-1e77a9c3b455", "direction": "INBOUND"}}
    ]
    ```
* **`connection_uuids`**: < list of connection UUIDs > - Optional - When set, only events for these connections are acted on.
* **`connection_types`**: < list of connection types > - Optional - When set, only these connection types are acted on (for example `EVPL_VC`, `IP_VC`).
* **`project_uuid`**: < A project UUID > - Optional - When set, only connections in this project are acted on.
* **`require_non_empty_rules`**: `true` | `false` - Optional - Skip a route filter policy that has no rules; default `true`.
* **`dry_run`**: `true` | `false` - Optional - Report the intended attachment without calling `attach_route_filter`; default `false`.
* **`verification_attempts`**: <integer> - Optional - Maximum attachment-status polls after attaching; default `6`.
* **`verification_wait_ms`**: <integer> - Optional - Milliseconds to wait between attachment-status polls; default `5000`.
* **`recipient_email_addresses`**: < list of email addresses > - Required - Recipients for the completion report.
