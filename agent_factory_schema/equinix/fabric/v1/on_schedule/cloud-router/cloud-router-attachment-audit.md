---
name: router-attachment-audit
description: Scans all Fabric Cloud Routers for missing stream attachments, then automatically attaches
  unattached routers (up to 5) to a user-specified stream and emails a report of attached and
  unattached routers on completion.
---

# Router Attachment Audit Agent

## Overview
An Equinix agent that audits Fabric Cloud Routers to detect routers that are unmonitored and attach to stream.
After collecting the full inventory of PROVISIONED routers, excluding those that are already 
attached to streams, the agent automatically attaches the unattached routers to the stream provided in configuration prompt:
attaching all routers if there are fewer than 5, or only the first 5 routers if there are more — without asking the
user to confirm. It then sends an email report listing which routers were attached and which were left
unattached. This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Paginate through all Fabric Cloud Routers 
- Use `search_attached_assets` across every stream to determine which routers are already attached
- Identify unattached (unmonitored) routers by cross-referencing router UUIDs against attached assets
- Automatically attach unattached routers (up to a maximum of 5) to the configured stream, without user confirmation
- Send an email report listing every router that was attached and every router that was left unattached

## Prerequisites
- A target stream UUID must be provided in configuration (`stream_uuid`). The stream must already exist and be in PROVISIONED state.
- Routers must be in PROVISIONED state to be eligible for stream attachment.

## Available Tools
This skill can use the following tools:

- **`search_routers`**: Searches for existing provisioned Fabric Cloud Routers with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`search_attached_assets`**: Returns all routers attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a router to a stream by asset UUID and stream UUID with `"metrics_enabled": false`.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Configuration
1a. Read `stream_uuid` from configuration. This is **required**. If it is missing or empty, stop immediately and inform the user:
> "No `stream_uuid` was provided in configuration. Please supply the UUID of the stream to attach routers to."

1b. Call `list_streams` and confirm that a stream with the given `stream_uuid` exists and is in `PROVISIONED` state.
Retain its `name` for use in the report. If no matching stream is found, stop and inform the user that the provided `stream_uuid` is invalid.

### Step 2 — Collect All Routers
2a. Call `search_routers` with pagination:
```json
{
  "pagination": { "offset": 0, "limit": 100 }
}
```
2b. If the total exceeds the page limit, repeat with incremented offsets until all routers are collected (maximum 500).

2c. Retain only: `uuid`, `name`, `state`, `location.metroCode`, `package.code`. Discard all other fields.

2d. Filter out routers not in `PROVISIONED` state — they are ineligible for stream attachment.

### Step 3 — Collect Existing Stream Attachments
3a. Using the streams returned by `list_streams` in Step 1b, call `search_attached_assets` with "asset_type: router" 
for **each** stream UUID
to get the list of routers currently attached to that stream.
Collect all returned router UUIDs into a single in-memory set: `attached_asset_uuids`.

### Step 4 — Identify Unattached Routers
4a. For each router collected in Step 2, check whether its UUID is present in `attached_asset_uuids`.
If it is **not** present, add it to the `unattached_routers` list (preserving the order in which routers were collected).

4b. If `unattached_routers` is empty, skip attachment. Proceed to Step 6 and report that no action was needed.

### Step 5 — Attach Routers Automatically (No Confirmation)
Do **not** ask the user for confirmation. Apply the following rule based on the number of unattached routers:

5a. Determine the routers to attach:
- If `unattached_routers` contains **fewer than 5** routers, select **all** of them.
- If `unattached_routers` contains **50 or more** routers, select only the **first 5** (by collection order).
Call the selected set `routers_to_attach`. 
Put unattached routers beyond the first 5 to form `routers_over_limit`
and will be reported as left unattached (reason: exceeded 5-router attachment limit).

5b. For each router in `routers_to_attach`, in order:
- Call `attach_stream_asset` with the router UUID, the configured `stream_uuid`, and `"metrics_enabled": false`.
- Record the outcome (success or error) alongside the router name and UUID.
- Call `wait` for 3000 milliseconds after each attachment.

5c. If any attachment fails, record the error and continue with the remaining routers.
Do not abort the run on a single failure.

5d. After all attempts, tally:
- `attached`: routers successfully attached to the stream.
- `failed`: routers whose attachment failed, with error details.
- `left_unattached`: `routers_over_limit` (skipped due to the 5-router limit) plus every router in `failed`.

### Step 6 — Send Email Report
6a. Compose the completion report in memory:

```
<div class="header">
    <h1>Router Attachment Audit Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Attached Routers</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Router Name</li>
                <li>Router UUID</li>
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
    <h2>Unattached Routers</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Router Name</li>
                <li>Router UUID</li>
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
- **Summary**: Total routers audited, count unattached found, count successfully attached, count left unattached. Name the target stream. State the overall outcome in 2–4 sentences.
- **Attached Routers**: One row per successfully attached router — name, full UUID, metro, target stream name, target stream full UUID. If none were attached, note "None."
- **Unattached Routers**: One row per router left unattached — name, full UUID, metro, and reason ("Exceeded 50-router attachment limit" or the specific attachment error). If none, note "None."
- **Next Steps**: 1–3 plain-English recommendations (e.g., re-run the audit to attach routers that exceeded the 50-router limit, set up alert rules on the newly monitored routers, investigate any failed attachments).

6b. If `recipient_email_addresses` is provided and non-empty, call `send_email_notification` with:
- `pdfContent`: the full report from Step 6a.
- `body`: one-paragraph summary of the audit outcome, including counts of attached and unattached routers.
- `pdfTitle`: `FabricRouterAudit_<YYYY-MM-DD>_Complete`
- `recipients`: `recipient_email_addresses`

6c. Also present the same summary (attached and unattached router lists) directly in the conversation, so the outcome is visible even when no email recipients are configured.

## Guidelines
- **Autonomous attachment**: Do not ask the user to confirm attachments. Once unattached routers are identified, attach them per the rules in Step 5 automatically.
- **50-router cap**: Never attach more than 5 routers in a single run. Routers beyond the first 5 must be reported as left unattached with the limit reason.
- **Partial success**: A failure on one attachment must not abort the remaining attachments — continue and report all outcomes.
- **Pagination discipline**: Always paginate routers fully before cross-referencing. Call `search_attached_assets` for every stream returned by `list_streams` before building `attached_asset_uuids` — an incomplete inventory will produce false negatives.
- **Configuration required**: `stream_uuid` is mandatory. Never guess or invent a stream UUID; stop and ask if it is missing or invalid.
- **Name length**: No generated names should exceed 24 characters.
- **Token efficiency**: After cross-referencing in Step 4, discard the raw router payloads. Carry forward only the curated `unattached_routers`, target stream details, and attachment outcomes.
- **Plain English**: All user-facing text and report sections must use plain English — no raw API field names or event type strings.

## Configuration
- **`stream_uuid`**: `"<uuid>"` — **Required**. UUID of the target stream that unattached routers will be attached to. Must reference an existing PROVISIONED stream.
- **`recipient_email_addresses`**: `["<email>", ...]` — Optional. List of email addresses to receive the completion report. If omitted, the summary is presented in the conversation only.
