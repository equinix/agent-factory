---
name: port-attachment-audit
description: Scans all Fabric Ports for missing stream attachments, then automatically attaches
  unattached ports (up to 5) to a user-specified stream and emails a report of attached and
  unattached ports on completion.
categories: ["Monitor & Report Agents"]
---

# Port Attachment Audit Agent

## Overview
An Equinix agent that audits all Fabric Ports to detect ports that are unmonitored then attachs them to stream. 
After collecting the full inventory of PROVISIONED ports, excluding those that are already attached to streams, the agent automatically attaches the unattached ports to the stream provided in configuration prompt:
attaching all ports if there are fewer than 5, or only the first 5 ports if there are more — without asking the
user to confirm. It then sends an email report listing which ports were attached and which were left
unattached. This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Paginate through all Fabric Ports 
- Use `search_attached_assets` across every stream to determine which ports are already attached
- Identify unattached (unmonitored) ports by cross-referencing port UUIDs against attached assets
- Automatically attach unattached ports (up to a maximum of 5) to the configured stream, without user confirmation
- Send an email report listing every port that was attached and every port that was left unattached

## Prerequisites
- A target stream UUID must be provided in configuration (`stream_uuid`). The stream must already exist and be in PROVISIONED state.
- Ports must be in PROVISIONED state to be eligible for stream attachment.

## Available Tools
This skill can use the following tools:

- **`search_ports`**: Searches for existing provisioned Fabric Ports with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`search_attached_assets`**: Returns all ports attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a port to a stream by asset UUID and stream UUID with `"metrics_enabled": true`.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Configuration
1a. Read `stream_uuid` from configuration. This is **required**. If it is missing or empty, stop immediately and inform the user:
> "No `stream_uuid` was provided in configuration. Please supply the UUID of the stream to attach ports to."

1b. Call `list_streams` and confirm that a stream with the given `stream_uuid` exists and is in `PROVISIONED` state.
Retain its `name` for use in the report. If no matching stream is found, stop and inform the user that the provided `stream_uuid` is invalid.

### Step 2 — Collect All Ports
2a. Call `search_ports` with pagination:
```json
{
  "pagination": { "offset": 0, "limit": 100 }
}
```
2b. If the total exceeds the page limit, repeat with incremented offsets until all ports are collected (maximum 500).

2c. Retain only: `uuid`, `name`, `state`, `location.metroCode`. Discard all other fields.

2d. Filter out ports not in `PROVISIONED` state — they are ineligible for stream attachment.

### Step 3 — Collect Existing Stream Attachments
3a. Using the streams returned by `list_streams` in Step 1b, call `search_attached_assets` with "asset_type: port" 
for **each** stream UUID
to get the list of ports currently attached to that stream.
Collect all returned port UUIDs into a single in-memory set: `attached_asset_uuids`.

### Step 4 — Identify Unattached Ports
4a. For each port collected in Step 2, check whether its UUID is present in `attached_asset_uuids`.
If it is **not** present, add it to the `unattached_ports` list (preserving the order in which ports were collected).

4b. If `unattached_ports` is empty, skip attachment. Proceed to Step 6 and report that no action was needed.

### Step 5 — Attach Ports Automatically (No Confirmation)
Do **not** ask the user for confirmation. Apply the following rule based on the number of unattached ports:

5a. Determine the ports to attach:
- If `unattached_ports` contains **fewer than 5** ports, select **all** of them.
- If `unattached_ports` contains **5 or more** ports, select only the **first 5** (by collection order).
Call the selected set `ports_to_attach`. 
Put unattached ports beyond the first 5 to form `ports_over_limit`
and will be reported as left unattached (reason: exceeded 5-port attachment limit).

5b. For each port in `ports_to_attach`, in order:
- Call `attach_stream_asset` with the port UUID, the configured `stream_uuid`, and `"metrics_enabled": true`.
- Record the outcome (success or error) alongside the port name and UUID.
- Call `wait` for 3000 milliseconds after each attachment.

5c. If any attachment fails, record the error and continue with the remaining ports.
Do not abort the run on a single failure.

5d. After all attempts, tally:
- `attached`: ports successfully attached to the stream.
- `failed`: ports whose attachment failed, with error details.
- `left_unattached`: `ports_over_limit` (skipped due to the 5-port limit) plus every port in `failed`.

### Step 6 — Send Email Report
6a. Compose the completion report in memory:

```
<div class="header">
    <h1>Port Attachment Audit Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Attached Ports</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Port Name</li>
                <li>Port UUID</li>
                <li>Metro</li>
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
    <h2>Unattached Ports</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Port Name</li>
                <li>Port UUID</li>
                <li>Metro</li>
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
- **Summary**: Total ports audited, count unattached found, count successfully attached, count left unattached. Name the target stream. State the overall outcome in 2–4 sentences.
- **Attached Ports**: One row per successfully attached port — name, full UUID, metro, target stream name, target stream full UUID. If none were attached, note "None."
- **Unattached Ports**: One row per port left unattached — name, full UUID, metro, and reason ("Exceeded 5-port attachment limit" or the specific attachment error). If none, note "None."
- **Next Steps**: 1–3 plain-English recommendations (e.g., re-run the audit to attach ports that exceeded the 5-port limit, set up alert rules on the newly monitored ports, investigate any failed attachments).

6b. If `recipient_email_addresses` is provided and non-empty, call `send_email_notification` with:
- `pdfContent`: the full report from Step 6a.
- `body`: one-paragraph summary of the audit outcome, including counts of attached and unattached ports.
- `pdfTitle`: `FabricPortAudit_<YYYY-MM-DD>_Complete`
- `recipients`: `recipient_email_addresses`

6c. Also present the same summary (attached and unattached port lists) directly in the conversation, so the outcome is visible even when no email recipients are configured.

## Guidelines
- **Autonomous attachment**: Do not ask the user to confirm attachments. Once unattached ports are identified, attach them per the rules in Step 5 automatically.
- **5-port cap**: Never attach more than 5 ports in a single run. Ports beyond the first 5 must be reported as left unattached with the limit reason.
- **Partial success**: A failure on one attachment must not abort the remaining attachments — continue and report all outcomes.
- **Pagination discipline**: Always paginate ports fully before cross-referencing. Call `search_attached_assets` for every stream returned by `list_streams` before building `attached_asset_uuids` — an incomplete inventory will produce false negatives.
- **Configuration required**: `stream_uuid` is mandatory. Never guess or invent a stream UUID; stop and ask if it is missing or invalid.
- **Name length**: No generated names should exceed 24 characters.
- **Token efficiency**: After cross-referencing in Step 4, discard the raw port payloads. Carry forward only the curated `unattached_ports`, target stream details, and attachment outcomes.
- **Plain English**: All user-facing text and report sections must use plain English — no raw API field names or event type strings.

## Configuration
- **`stream_uuid`**: `"<uuid>"` — **Required**. UUID of the target stream that unattached ports will be attached to. Must reference an existing PROVISIONED stream.
- **`recipient_email_addresses`**: `["<email>", ...]` — Optional. List of email addresses to receive the completion report. If omitted, the summary is presented in the conversation only.
