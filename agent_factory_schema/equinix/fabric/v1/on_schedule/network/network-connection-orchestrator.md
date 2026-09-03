---
name: network-connection-orchestrator
description: Creates a Fabric Network of a supported type and connects a caller-supplied list of existing access points to it, then waits for each connection to provision, attaches the provisioned connections to an observability stream, and sends a completion report.
---

# Network Connection Orchestrator Agent

## Overview
Creates a Fabric Network of a supported type and connects a caller-supplied list of existing access points to it, then waits for each connection to provision, attaches the provisioned connections to an observability stream, and sends a completion report.

Supported network types are EVPLAN, EPLAN, EVPTREE, EPTREE, and IPWAN. Access points are Ports for the Layer2 network types and existing Cloud Routers for IPWAN. Unlike agents that provision the far-end resource themselves (for example the IPWAN and Cloud Router Network Setup agent, which creates its own Cloud Router), this agent never creates a Port or Cloud Router; it only accepts UUIDs of resources that already exist. This keeps its scope to network, connections, and observability, and avoids duplicating router or port provisioning logic owned elsewhere.

The agent creates the Network, waits for it to become `ACTIVE`, then creates one connection per listed access point (Port→Network for Layer2 types, Cloud Router→Network for IPWAN), waits for each connection's `operation.equinixStatus` to reach `PROVISIONED`, attaches the successfully provisioned connections to a stream (creating one if needed — the Network itself cannot be attached to a stream), and sends a single completion report covering every item's outcome.

This agent runs once immediately by default unless scheduled by user.

## Success Criteria & Termination
- **Success**: The Network reaches `ACTIVE`, and every listed access point results in a connection that reaches `PROVISIONED` and is attached to the stream. The run ends after the final step — no further action is taken.
- **Partial success (expected, not a failure)**: The Network is created successfully, but one or more individual access points fail to create a connection or time out during provisioning. Each item is processed independently — a failure on one access point never blocks or aborts processing of the others. The completion report itemizes every access point's outcome individually. The run still ends after exactly one completion email; no retries are attempted for any item.
- **Full failure**: The Network itself fails to create, or times out waiting for `ACTIVE` state. All connection creation is skipped entirely (there is nothing to connect to), and the completion email reports the network failure with no per-item detail.
- **Escalation**: The agent does not escalate to a human directly. All outcomes — success, partial success, and full failure — are surfaced only via the completion email to `recipient_email_addresses`; a human must read that email and re-run the agent (after remediating per-item issues, per Guidelines below) for any items that did not succeed.

## Capabilities
- Create a Fabric Network of type `EPLAN`, `EVPLAN`, `EPTREE`, `EVPTREE`, or `IPWAN`
- Accept a list of existing access points (Ports for Layer2 network types; existing Cloud Routers for IPWAN) and create one connection per entry, linking each to the new Network
- Poll the Network and every created connection independently until each reaches its ready state, or times out
- Create a stream automatically if no stream UUID is provided, then attach every successfully provisioned connection to it (Networks cannot be attached to a stream; pre-existing source Ports/Cloud Routers are never attached — only the connections this run creates)
- Send a single email completion report itemizing the outcome of the Network and every requested connection

## Prerequisites
- The agent's Fabric API credentials must have permission to create networks and connections; to search connections and networks; to create and read streams and stream assets; and to send email notifications.
- This agent does **not** create Ports or Cloud Routers. Every UUID passed in `source_access_points` must already exist and be accessible to the credentials in use. If a Cloud Router does not yet exist for an IPWAN request, provision one first (e.g. via the Cloud Router Manager agent) before running this agent.
- The `create_network` tool's `type` enum is `EPLAN`, `EVPLAN`, `EPTREE`, `EVPTREE`, `IPWAN` (verified against the tool schema). Point-to-point `EPLINE`/`EVPLINE` E-Line services are **not** Network types — they connect two access points directly and have no Network object, so they are out of scope for this agent.
- If `project_uuid` is provided, it must reference a project the credentials can access; if omitted, resources are created in the default project for the credentials.
- The project's plan must have unused quota for at least 1 additional Network and one additional connection per entry in `source_access_points` — insufficient quota causes a 4xx error from `create_network`/`create_connection` and is treated as a creation failure for that item (see Guidelines).
- For Layer2 network types (`EPLAN`/`EVPLAN`/`EPTREE`/`EVPTREE`), every entry in `source_access_points` must have `access_point_type: PORT` and a valid, accessible `uuid` for an existing Port. For `IPWAN`, every entry must have `access_point_type: CLOUD_ROUTER` and a valid, accessible `uuid` for an existing Cloud Router. Mixed access point types within a single run are not supported, since the Network's type fixes the required connection type for all its connections.
- `bandwidth_in_mbps`, whether set per-entry or via `default_bandwidth_in_mbps`, must be between 0 and 100000 Mbps (the range `create_connection` accepts); out-of-range values are rejected by `create_connection` for that item.
- `recipient_email_addresses` must contain at least one syntactically valid email address — the completion email cannot be sent otherwise, and the platform's per-resource `notifications` also require a non-empty list.

## Available Tools
This skill can use the following tools:

- **`create_network`**: Creates a Fabric Network. Accepts name, type, scope (`LOCAL`, `REGIONAL`, or `GLOBAL`), location (region or metro code, as applicable to scope), notifications (mandatory), and project UUID.
- **`search_networks`**: Searches for existing Fabric Networks by filter, used to poll state.
- **`create_connection`**: Creates a connection. Used to create one connection per source access point, linking it to the Network. Accepts notifications.
- **`search_connections`**: Searches for existing connections by filter, used to poll provisioning state via `/operation/equinixStatus`.
- **`get_stream_details`**: Fetches stream details given a stream UUID.
- **`create_stream`**: Creates a new stream. Accepts a stream type (for example TELEMETRY_STREAM), name, description, and project UUID.
- **`attach_stream_asset`**: Attaches an asset to a stream. Accepts the stream UUID, an asset type (set it to "connection"), the asset UUID (the connection's UUID), and a request body that enables metrics collection. Networks cannot be attached to a stream — there is no network asset type.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Inputs
1a. Confirm `network_type` is one of `EPLAN`, `EVPLAN`, `EPTREE`, `EVPTREE`, `IPWAN`. Stop and report an error if missing or invalid.

1b. Confirm `source_access_points` is a non-empty list. Stop and report an error if missing or empty.

1c. Determine the required `access_point_type` and connection `type` from `network_type`:
| `network_type` | required `access_point_type` | connection `type` |
|---|---|---|
| `EPLAN` | `PORT` | `EPLAN_VC` |
| `EVPLAN` | `PORT` | `EVPLAN_VC` |
| `EPTREE` | `PORT` | `EPTREE_VC` |
| `EVPTREE` | `PORT` | `EVPTREE_VC` |
| `IPWAN` | `CLOUD_ROUTER` | `IPWAN_VC` |

1d. Validate every entry in `source_access_points` has `access_point_type` matching the required type for this `network_type`, and a non-empty `uuid`. Reject (fail validation entirely, before any tool call) any entry with a mismatched `access_point_type` or missing `uuid` — do not silently skip it, since a mismatched type indicates a caller error worth surfacing immediately rather than partway through a run.

1e. For `PORT` entries, `vlan_tag` is optional; if provided, it is used with `linkProtocol.type: DOT1Q`. For `CLOUD_ROUTER` entries, no VLAN handling applies.

1f. Apply naming defaults if not provided:
- `network_name` → `network-conn-orch`
- `connection_name_prefix` → `conn`
- `stream_name` → `network-conn-stream`

1g. Apply numeric defaults if not provided:
- `default_bandwidth_in_mbps` → `1000` (used for any entry that omits its own `bandwidth_in_mbps`)

1h. If `network_scope` is `REGIONAL`, confirm `region` (`AMER`, `EMEA`, or `APAC`) is provided. Stop and report an error if missing. If `network_scope` is `LOCAL` or `GLOBAL`, `region` is not required.

### Step 2 — Create the Network
2a. Call `create_network` with:
- `name`: `network_name`
- `type`: `network_type`
- `scope`: `network_scope`
- `location.region`: `region` (only if `network_scope` is `REGIONAL`)
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid` (if provided)

2b. Record the returned network UUID as `network_uuid`. If creation fails, skip Steps 3–6 entirely and go directly to Step 7 to send a completion email reporting the network creation failure and its error detail — no per-item processing is attempted since there is no Network to connect to.

### Step 3 — Wait for the Network to Provision
3a. Repeat up to 30 times (30 × 15000 ms = 450 seconds / 7.5 minutes maximum) or until the Network is ready:
- Call `wait` for 15000 milliseconds.
- Call `search_networks` filtering by `/uuid` = `network_uuid` and check `/state`.
- Break early once `/state` = `ACTIVE` (Networks use `ACTIVE`/`INACTIVE`/`DELETED`, not `PROVISIONED`, as their state values).

3b. If the Network has not reached `ACTIVE` after 30 retries (450 seconds), treat this as a provisioning timeout: skip Steps 4–6 and go directly to Step 7 to send a completion email reporting a timeout error for the Network and the 450-second threshold exceeded. Do not attempt to create any connection against a Network that is not yet `ACTIVE` — doing so can produce an opaque internal error from `create_connection` (e.g. `EQ-3142502`) instead of a clear validation error.

### Step 4 — Create One Connection Per Access Point
For each entry in `source_access_points` (process independently — a failure on one entry does not stop processing of the remaining entries):

4a. Build the connection request:
- `name`: `<connection_name_prefix>-<index>` (max 24 characters)
- `type`: the connection type determined in Step 1c
- `bandwidth`: entry's `bandwidth_in_mbps`, or `default_bandwidth_in_mbps` if the entry omits it
- `aSide.accessPoint`:
  - If `access_point_type` is `PORT`: `{"type": "COLO", "port": {"uuid": entry.uuid}, "linkProtocol": {"type": "DOT1Q", "vlanTag": entry.vlan_tag} }` (omit `linkProtocol` if no `vlan_tag` provided)
  - If `access_point_type` is `CLOUD_ROUTER`: `{"type": "CLOUD_ROUTER", "router": {"uuid": entry.uuid}}`
- `zSide.accessPoint`: `{"type": "NETWORK", "network": {"uuid": network_uuid}}`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid` (if provided)

4b. Call `create_connection`. If it succeeds, record the returned connection UUID against this entry as `connection_uuid`. If it fails, record this entry's outcome as "creation failed" with the error detail, and move on to the next entry — do not retry and do not abort the overall run.

### Step 5 — Wait for All Created Connections to Provision
Poll every connection created in Step 4 in a **single shared loop** so the total provisioning wait stays bounded (~450 seconds) regardless of how many connections were requested — do not wait one connection out fully before starting to poll the next. Let `pending` be the set of entries that received a `connection_uuid` from Step 4; entries that failed creation are excluded and keep their "creation failed" outcome.

5a. Repeat up to 30 times (30 × 15000 ms = 450 seconds / 7.5 minutes maximum), or until `pending` is empty:
- Call `wait` for 15000 milliseconds.
- For each entry still in `pending`, call `search_connections` filtering by `/uuid` = `connection_uuid` and read `/operation/equinixStatus`. As an efficiency option, a single `search_connections` call filtering `/uuid IN [<all pending UUIDs>]` may be used in place of one call per pending entry.
- When an entry's `/operation/equinixStatus` = `PROVISIONED`, record it as provisioned and remove it from `pending`. (Note: `PROVISIONED` is an `operation.equinixStatus` value, not a `/state` value — a connection's `/state` never equals `PROVISIONED`, so polling `/state` here would never match.)

5b. Any entry still in `pending` when the loop ends (all 30 iterations elapsed without it reaching `PROVISIONED`) is recorded with outcome "provisioning timeout" and the 450-second threshold noted. This is not a run halt — always continue to Step 6.

### Step 6 — Set Up Stream & Attach Connections
6a. If `stream_uuid` is provided, call `get_stream_details` to verify the stream exists. If it does not exist or the lookup fails, do **not** halt — connections may already be provisioned and must still be reported. Record a stream error, skip all attachment in Step 6c, and continue to Step 7; the completion report notes that no connection could be attached because the supplied stream was not found.

6b. If `stream_uuid` is not provided, call `create_stream` with:
- `type`: `TELEMETRY_STREAM`
- `name`: `stream_name` (3–24 characters; only alphanumerics, `-`, and `_`; must not start or end with a space, `-`, or `_`)
- `project.projectId`: `project_uuid` (if provided)

Record the returned UUID as `stream_uuid`.

6c. For each entry whose connection reached `PROVISIONED` in Step 5 (skip entries with no provisioned connection — nothing to attach):
- Call `attach_stream_asset` with `stream_uuid` = `stream_uuid`, `asset_type` = `connection`, `asset_uuid` = the entry's `connection_uuid`, and request body `{"metrics_enabled": true}`.
- Wait 3000 milliseconds after each attachment to allow the platform to register the asset.

Only the connections created by this run are attached. The Network itself is never attached (unsupported), and the pre-existing source Ports/Cloud Routers are never attached — they belong to the caller and this agent does not modify resources it did not create.

### Step 7 — Send Completion Notification
7a. Compose the completion report in memory using the structure below.

```
<div class="header">
    <h1>Network Connection Orchestrator — Completion Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Network</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>Type</li>
                <li>Scope</li>
                <li>State</li>
            </ul>
            <!-- Data Row -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>Connections</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Source Type</li>
                <li>Source UUID</li>
                <li>Connection UUID</li>
                <li>Bandwidth (Mbps)</li>
                <li>Provisioning State</li>
                <li>Stream Attached</li>
            </ul>
            <!-- One Data Row Per Source Access Point -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>Stream</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Next Steps</h2>
    <div class="content">
    </div>
</div>
```

Section content rules (populate every section from the data collected; never leave a section containing only placeholder or template text — a section may be reduced to a single explanatory sentence when it has no tabular data, but it must never be left empty):
- **Summary**: State the network type and overall outcome in 3–5 sentences, including a count (e.g. "4 of 5 requested connections succeeded"). If the Network itself failed or timed out, state that clearly and note no connections were attempted.
- **Network**: One row — name, UUID, type, scope, and final state. If the network was never created or never reached `ACTIVE`, state "Not created" or "Timeout" and the error detail in place of UUID/state.
- **Connections**: One row per entry in `source_access_points`, in the order supplied. For each row, report source type, source UUID, and: connection UUID + bandwidth + provisioning state + attachment status if it got that far; or the specific failure point ("creation failed", "provisioning timeout", "not attached — connection not provisioned") with error detail otherwise. If the Network itself failed, every row reads "Skipped — network creation failed" or "Skipped — network provisioning timeout".
- **Stream**: State the stream UUID used, whether it was newly created or pre-existing, and how many connections were attached to it out of how many were provisioned. If a supplied `stream_uuid` could not be found (Step 6a), state that no stream was resolved and that no connections were attached, and note the provisioned connections can be attached manually on a re-run with a valid `stream_uuid`.
- **Next Steps**: If every item succeeded, give 1–3 plain-English recommendations (e.g. set up an alert rule on the new connections, verify end-to-end reachability on the far end). If any item failed, list the specific remediation from the Guidelines' Remediation mapping for each distinct failure type present in the report, and note that the agent must be re-run manually — only the failed entries need to be resupplied, not the entire request — after remediating.

7b. Call `send_email_notification` with:
- `pdfContent`: the full report from Step 7a.
- `body`: one-paragraph summary of the network created and the count of successful vs. failed connections.
- `pdfTitle`: `NetworkConnectionOrchestrator_<network_uuid>_Report`
- `recipients`: `recipient_email_addresses`

## Guidelines
- **Prioritize Clarity**: Confirm all required parameters — including per-entry `access_point_type` matching `network_type` — before making any tool call.
- **Per-item independence**: Every entry in `source_access_points` is processed on its own. A creation failure or provisioning timeout on one entry must never stop, skip, or alter processing of any other entry. The only run-wide abort condition is the Network itself failing to create or reach `ACTIVE`.
- **Halt points — when no completion email is sent**: The agent stops without sending any email **only during Step 1 input validation** (invalid or missing `network_type`, empty `source_access_points`, an entry whose `access_point_type` does not match `network_type` or is missing its `uuid`, or `REGIONAL` scope with no `region`) — all of which fail before any tool call is made. Every failure after the first tool call — network creation failure (Step 2b), network provisioning timeout (Step 3b), a supplied stream not being found (Step 6a), and any per-item connection creation failure or provisioning timeout — still produces exactly one completion email. There is never a case where a resource is created and the run ends silently.
- **Never create a Port or Cloud Router**: If a `CLOUD_ROUTER` or `PORT` UUID in `source_access_points` does not exist or is inaccessible, this is a per-item creation failure to report — it is never remediated by having this agent create the missing resource.
- **Never attach the Network to a stream**: unsupported by the platform. Only the connections created by this run are attached.
- **Never attach pre-existing source access points to a stream**: only resources created by this run (the connections) are attached; the caller's existing Ports/Cloud Routers are left untouched.
- **No automatic retry**: The agent never automatically retries a failed or timed-out item. Remediation and re-running are manual, human-driven steps triggered by reading the completion email; only the entries that need fixing must be resupplied on re-run.
- **Remediation mapping** — match the reported error to a specific fix before re-running the affected entry:
  - Quota exceeded (4xx from `create_network`/`create_connection`): request a quota increase for the project, or free up unused resources, then re-run.
  - Invalid or mismatched `access_point_type` for the given `network_type`: correct the entry to use the required type (`PORT` for Layer2 types, `CLOUD_ROUTER` for `IPWAN`), then re-run.
  - Invalid, nonexistent, or inaccessible source `uuid`: verify the Port or Cloud Router exists and is accessible to the credentials in use; if it doesn't exist yet, provision it first via the appropriate agent, then re-run.
  - Invalid or unsupported `bandwidth_in_mbps` for the connection type: correct the value to one valid for that connection type, then re-run.
  - `notifications` or `recipient_email_addresses` empty/invalid: supply at least one valid recipient email address, then re-run.
  - Provisioning timeout (450 seconds exceeded) on the Network or a connection: check Equinix Fabric platform status for the relevant metro/region, then re-run once confirmed either self-resolved or stuck and needing removal.
  - Internal system error from `create_connection` (e.g. `EQ-3142502`) immediately after network creation: this typically means the Network had not yet reached `ACTIVE` when a connection was attempted; confirm the Network's state via `search_networks`, wait for `ACTIVE`, then re-run.
- **Polling discipline**: Always wait between state polls. Never skip the wait step even if a resource appears fast to provision.
- **Name length**: Keep all generated names to 24 characters or fewer for platform compatibility.
- **Token Efficiency**: Carry only UUIDs and state/result values forward between steps — do not pass full resource payloads downstream.
- **Plain English**: Report section text must use plain English with no raw API jargon.

## Configuration
- **`network_type`**: `<EPLAN | EVPLAN | EPTREE | EVPTREE | IPWAN>` — Required. Determines the connection type used for every entry in `source_access_points` and the required `access_point_type` (see Step 1c table).
- **`network_scope`**: `<LOCAL | REGIONAL | GLOBAL>` — Required. `LOCAL` networks derive their metro from the first connection; `REGIONAL` requires `region`; `GLOBAL` requires neither.
- **`region`**: `<AMER | EMEA | APAC>` — Required only if `network_scope` is `REGIONAL`.
- **`network_name`**: `<name>` — Optional. Name for the created Network (default: `network-conn-orch`; max 24 characters).
- **`source_access_points`**: `[{"access_point_type": "<PORT|CLOUD_ROUTER>", "uuid": "<UUID>", "vlan_tag": <optional, PORT only>, "bandwidth_in_mbps": <optional>}, ...]` — Required. Non-empty list of existing access points to connect to the Network. `access_point_type` must match the type required by `network_type` for every entry.
- **`default_bandwidth_in_mbps`**: `<number>` — Optional. Used for any entry that omits its own `bandwidth_in_mbps` (default: `1000`).
- **`connection_name_prefix`**: `<name>` — Optional. Prefix for generated connection names (default: `conn`; combined with index, max 24 characters total).
- **`project_uuid`**: `<UUID>` — Optional. Scopes all created resources to the specified Equinix Fabric project.
- **`stream_uuid`**: `<UUID>` — Optional. UUID of an existing stream to attach connections to. If omitted, a new stream is created.
- **`stream_name`**: `<name>` — Optional. Name for the new stream when no `stream_uuid` is provided (default: `network-conn-stream`; max 24 characters).
- **`recipient_email_addresses`**: `["<email>", ...]` — Required. List of email addresses to receive the completion report email sent in Step 7. Note: the Fabric platform also sends its own separate notification for each Network and connection creation call to this same list (its `notifications.emails` field cannot be empty), so recipients will see those in addition to the Step 7 report.