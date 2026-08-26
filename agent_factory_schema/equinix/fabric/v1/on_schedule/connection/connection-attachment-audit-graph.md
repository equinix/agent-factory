---
name: connection-attachment-audit-graph
description: Scans all Fabric Connections for missing stream attachments, then automatically attaches
  unattached connections (up to 5) to a user-specified stream and emails a report of attached and
  unattached connections on completion.
categories: ["Monitor & Report Agents"]
execution_mode: graph
graph_pattern: dag
---

# Connection Attachment Audit Agent

## Overview
An Equinix agent that audits Fabric connections to detect that are unmonitored and attach to stream.
After collecting the full inventory of PROVISIONED connections, excluding those that are already attached to streams, the agent automatically attaches the unattached connections to the stream provided in configuration prompt:
attaching all connections if there are fewer than 5, or only the first 5 connections if there are more — without asking the
user to confirm. It then sends an email report listing which connections were attached and which were left
unattached. This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Paginate through all Fabric Connections 
- Use `search_attached_assets` across every stream to determine which connections are already attached
- Identify unattached (unmonitored) connections by cross-referencing connection UUIDs against attached assets
- Automatically attach unattached connections (up to a maximum of 5) to the configured stream, without user confirmation
- Send an email report listing every connection that was attached and every connection that was left unattached

## Prerequisites
- A target stream UUID must be provided in configuration (`stream_uuid`). The stream must already exist and be in PROVISIONED state.
- Connections must be in PROVISIONED state to be eligible for stream attachment.

## Available Tools
This skill can use the following tools:

- **`search_connections`**: Searches for existing provisioned Fabric Connections with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`search_attached_assets`**: Returns all connections attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a connection to a stream by asset UUID and stream UUID with `"metrics_enabled": true`.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Configuration
1a. Read `stream_uuid` from configuration. This is **required**. If it is missing or empty, stop immediately and inform the user:
> "No `stream_uuid` was provided in configuration. Please supply the UUID of the stream to attach connections to."

1b. Call `list_streams` and confirm that a stream with the given `stream_uuid` exists and is in `PROVISIONED` state.
Retain its `name` for use in the report. If no matching stream is found, stop and inform the user that the provided `stream_uuid` is invalid.

### Step 2 — Collect All Connections
2a. Call `search_connections` with pagination:
```json
{
  "pagination": { "offset": 0, "limit": 100 }
}
```
2b. If the total exceeds the page limit, repeat with incremented offsets until all connections are collected (maximum 500).

2c. Retain only: `uuid`, `name`, `state`, `type`, `bandwidth`. Discard all other fields.

2d. Filter out connections not in `PROVISIONED` state — they are ineligible for stream attachment.

### Step 3 — Collect Existing Stream Attachments
3a. Using the streams returned by `list_streams` in Step 1b, call `search_attached_assets` with "asset_type: connection" 
for **each** stream UUID
to get the list of connections currently attached to that stream.
Collect all returned connection UUIDs into a single in-memory set: `attached_asset_uuids`.

### Step 4 — Identify Unattached Connections
4a. For each connection collected in Step 2, check whether its UUID is present in `attached_asset_uuids`.
If it is **not** present, add it to the `unattached_connections` list (preserving the order in which connections were collected).

4b. If `unattached_connections` is empty, skip attachment. Proceed to Step 6 and report that no action was needed.

### Step 5 — Attach Connections Automatically (No Confirmation)
Do **not** ask the user for confirmation. Apply the following rule based on the number of unattached connections:

5a. Determine the connections to attach:
- If `unattached_connections` contains **fewer than 5** connections, select **all** of them.
- If `unattached_connections` contains **5 or more** connections, select only the **first 5** (by collection order).
Call the selected set `connections_to_attach`. 
Put unattached connections beyond the first 5 to form `connections_over_limit`
and will be reported as left unattached (reason: exceeded 5-connection attachment limit).

5b. For each connection in `connections_to_attach`, in order:
- Call `attach_stream_asset` with the connection UUID, the configured `stream_uuid`, and `"metrics_enabled": true`.
- Record the outcome (success or error) alongside the connection name and UUID.
- Call `wait` for 3000 milliseconds after each attachment.

5c. If any attachment fails, record the error and continue with the remaining connections.
Do not abort the run on a single failure.

5d. After all attempts, tally:
- `attached`: connections successfully attached to the stream.
- `failed`: connections whose attachment failed, with error details.
- `left_unattached`: `connections_over_limit` (skipped due to the 5-connection limit) plus every connection in `failed`.

### Step 6 — Send Email Report
6a. Compose the completion report in memory:

```
<div class="header">
    <h1>Connection Attachment Audit Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Attached Connections</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Connection Name</li>
                <li>Connection UUID</li>
                <li>Bandwidth (Mbps)</li>
                <li>Stream Name</li>
                <li>Stream UUID</li>
            </ul>
            <!-- Data Rows -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>Unattached Connections</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Connection Name</li>
                <li>Connection UUID</li>
                <li>Bandwidth (Mbps)</li>
                <li>Reason</li>
            </ul>
            <!-- Data Rows -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>Next Steps</h2>
    <div class="content">
    </div>
</div>
```

Section content rules:
- **Summary**: Total connections audited, count unattached found, count successfully attached, count left unattached. Name the target stream. State the overall outcome in 2–4 sentences.
- **Attached Connections**: One row per successfully attached connection — name, full UUID, bandwidth, target stream name, target stream full UUID. If none were attached, note "None."
- **Unattached Connections**: One row per connection left unattached — name, full UUID, bandwidth, and reason ("Exceeded 5-connection attachment limit" or the specific attachment error). If none, note "None."
- **Next Steps**: 1–3 plain-English recommendations (e.g., re-run the audit to attach connections that exceeded the 5-connection limit, set up alert rules on the newly monitored connections, investigate any failed attachments).

6b. If `recipient_email_addresses` is provided and non-empty, call `send_email_notification` with:
- `pdfContent`: the full report from Step 6a.
- `body`: one-paragraph summary of the audit outcome, including counts of attached and unattached connections.
- `pdfTitle`: `FabricConnectionAudit_<YYYY-MM-DD>_Complete`
- `recipients`: `recipient_email_addresses`

6c. Also present the same summary (attached and unattached connection lists) directly in the conversation, so the outcome is visible even when no email recipients are configured.

## Guidelines
- **Autonomous attachment**: Do not ask the user to confirm attachments. Once unattached connections are identified, attach them per the rules in Step 5 automatically.
- **5-connection cap**: Never attach more than 5 connections in a single run. Connections beyond the first 5 must be reported as left unattached with the limit reason.
- **Partial success**: A failure on one attachment must not abort the remaining attachments — continue and report all outcomes.
- **Pagination discipline**: Always paginate connections fully before cross-referencing. Call `search_attached_assets` for every stream returned by `list_streams` before building `attached_asset_uuids` — an incomplete inventory will produce false negatives.
- **Configuration required**: `stream_uuid` is mandatory. Never guess or invent a stream UUID; stop and ask if it is missing or invalid.
- **Name length**: No generated names should exceed 24 characters.
- **Token efficiency**: After cross-referencing in Step 4, discard the raw connection payloads. Carry forward only the curated `unattached_connections`, target stream details, and attachment outcomes.
- **Plain English**: All user-facing text and report sections must use plain English — no raw API field names or event type strings.

## Configuration
- **`stream_uuid`**: `"<uuid>"` — **Required**. UUID of the target stream that unattached connections will be attached to. Must reference an existing PROVISIONED stream.
- **`recipient_email_addresses`**: `["<email>", ...]` — Optional. List of email addresses to receive the completion report. If omitted, the summary is presented in the conversation only.
