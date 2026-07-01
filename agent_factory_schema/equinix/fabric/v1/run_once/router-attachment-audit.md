---
name: router-attachment-audit
description: Scans all Fabric Cloud Routers for missing stream attachments, identifies unmonitored routers,
  presents a curated selection to the user, and attaches chosen routers to the selected stream(s)
  with email notification on completion.
---

# Router Attachment Audit Agent

## Overview
An Equinix agent that audits all Fabric Cloud Routers to detect routers that are not attached to any stream
and are therefore unmonitored. After collecting the full inventory of routers and available streams, the agent presents the user
with a curated summary of unattached routers alongside a list of available streams to choose from.
Once the user confirms their selection, the agent attaches the chosen routers to the designated stream(s) and sends a completion notification.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Paginate through all Fabric Cloud Routers in the account
- Use `search_attached_assets` across every stream to determine which routers are already monitored
- Identify unattached (unmonitored) routers by cross-referencing router UUIDs against active subscriptions
- Present a structured, human-readable summary to the user for selection
- Attach user-selected routers to one or more chosen streams
- Send an email completion report listing every attachment made

## Prerequisites
- At least one stream must exist in the account, or the user must be willing to create one before proceeding.
- Routers must be in PROVISIONED state to be eligible for stream attachment.

## Available Tools
This skill can use the following tools:

- **`search_routers`**: Searches for existing Fabric Cloud Routers with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`create_stream`**: Creates a new stream with a given name. Used when no streams exist and the user opts to create one.
- **`search_attached_assets`**: Returns all assets currently attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a router to a stream by asset UUID and stream UUID.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Collect All Routers
1a. Call `search_routers` with:
```json
{
  "pagination": { "offset": 0, "limit": 100 }
}
```
1b. If the total exceeds the page limit, repeat with incremented offsets until all routers are collected (maximum 500).

1c. Retain only: `uuid`, `name`, `state`, `location.metroCode`, `package.code`. Discard all other fields.

1d. Filter out routers not in `PROVISIONED` state — they are ineligible for stream attachment and must not appear in the presented list.

### Step 2 — Collect All Streams and Their Attached Assets
2a. Call `list_streams` to retrieve all available streams. Retain `uuid`, `name`, and `state` per stream.

2b. For **each** stream UUID, call `search_attached_assets` to get the list of assets currently attached to that stream.
Collect all returned asset UUIDs into a single in-memory set: `attached_asset_uuids`.

2c. If no streams exist, ask the user whether they would like to create one:
> "No streams were found in your account. Would you like me to create a new stream? If yes, please provide a name for the stream."

If the user confirms, call `create_stream` with the provided name and record the returned UUID as the sole entry in the streams list. If the user declines, stop without making any changes.

### Step 3 — Identify Unattached Routers
3a. For each router collected in Step 1, check whether its UUID is present in `attached_asset_uuids`.
If it is **not** present, add it to the `unattached_routers` list.

3b. If `unattached_routers` is empty, stop and inform the user:
> "All PROVISIONED routers are already attached to a stream. No action is needed."

### Step 4 — Present Findings to the User
Present the following structured summary directly in the conversation. Do not send an email at this stage. Wait for the user's response before proceeding.

```
## Router Attachment Audit — Findings

### Unattached Routers (<count>)
| # | Name | UUID | Metro | Package |
|---|------|------|-------|---------|
| 1 | ...  | ...  | ...   | ...     |

### Available Streams (<count>)
| # | Name | UUID |
|---|------|------|
| 1 | ...  | ...  |

---
Please tell me which routers you would like to attach and to which stream(s).

You can respond in any of these ways:
- "Attach all to stream <name or UUID>"
- "Attach routers 1, 3, 5 to stream <name or UUID>"
- "Skip" to cancel without making any changes
```

Populate every table row from the in-memory lists built in Steps 1–3. Use the full UUID in every row.
If a list is empty, omit its table and note "None found."

### Step 5 — Parse the User's Selection
5a. Wait for the user to respond.

5b. Interpret the user's response to build an `attachment_plan`: a list of `(router_uuid, stream_uuid)` pairs.
Resolve stream references by name or UUID against the streams collected in Step 2a via `list_streams`.

5c. If the user responds "Skip" or indicates no action, stop without making any changes. Confirm cancellation to the user.

5d. If the user's response is ambiguous (e.g., a stream name matches multiple streams, or a router reference is unclear),
ask a single clarifying follow-up question before proceeding. Do not guess.

5e. Before executing, confirm the plan with the user by listing every intended attachment as a numbered checklist,
then ask for explicit approval:
> "I am about to make the following attachments — please confirm with 'Yes' to proceed or 'No' to cancel:
> 1. Attach router `<name> (<uuid>)` to stream `<name> (<uuid>)`
> 2. ..."

### Step 6 — Attach Routers to Stream(s)
Execute the `attachment_plan` confirmed in Step 5 in order:

6a. For each `(router_uuid, stream_uuid)` pair in the plan:
- Call `attach_stream_asset` with the router UUID and stream UUID.
- Record the outcome (success or error) alongside the router name and UUID.
- Call `wait` for 3000 milliseconds after each attachment.

6b. If any attachment fails, record the error and continue with the remaining items in the plan.
Do not abort the entire run on a single failure.

6c. After all attachments are attempted, tally:
- `succeeded`: list of router UUIDs successfully attached.
- `failed`: list of router UUIDs that failed, with error details.

### Step 7 — Send Completion Notification
7a. If `recipient_email_addresses` is not provided, skip the email and present the final summary directly in the conversation instead.

7b. Compose the completion report in memory:

```
<div class="header">
    <h1>Router Attachment Audit — Completion Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Successful Attachments</h2>
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
    <h2>Failed Attachments</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Skipped Routers</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Next Steps</h2>
    <div class="content">
    </div>
</div>
```

Section content rules:
- **Summary**: Total routers audited, count unattached found, count successfully attached, count failed. State overall outcome in 2–4 sentences.
- **Successful Attachments**: One row per successful attachment — router name, full UUID, metro, stream name, stream full UUID. Omit section if none succeeded.
- **Failed Attachments**: List each failed router as `<name> (<full-uuid>)` with the error detail. Omit section if no failures.
- **Skipped Routers**: List any unattached routers the user chose not to attach. Omit section if none were skipped.
- **Next Steps**: 1–3 plain-English recommendations (e.g., set up alert rules on the newly monitored routers, re-run the audit after provisioning new routers, investigate any failed attachments).

7c. Call `send_email_notification` with:
- `pdfContent`: the full report from Step 7b.
- `body`: one-paragraph summary of the audit outcome and attachment results.
- `pdfTitle`: `FabricRouterAudit_<YYYY-MM-DD>_Complete`
- `recipients`: `recipient_email_addresses`

## Guidelines
- **Interactive first**: Never skip Step 4 or Step 5 — always present findings to the user and obtain explicit approval before making any changes.
- **Non-destructive audit**: Steps 1–4 are read-only. No modifications are made until the user confirms in Step 5.
- **Partial success**: A failure on one attachment must not abort the remaining plan — continue and report all outcomes.
- **Pagination discipline**: Always paginate routers fully before cross-referencing. Call `search_attached_assets` for every stream returned by `list_streams` before building `attached_asset_uuids` — an incomplete inventory will produce false negatives.
- **Clarity over completeness**: If the user's selection is ambiguous, ask before acting. Never guess which stream or router was intended.
- **Name length**: No generated names should exceed 24 characters.
- **Token efficiency**: After cross-referencing in Step 3, discard the raw router payloads. Carry forward only the curated `unattached_routers`, stream list, and `attachment_plan`.
- **Plain English**: All user-facing text and report sections must use plain English — no raw API field names or event type strings.

## Configuration
- **`recipient_email_addresses`**: `["<email>", ...]` — Optional. List of email addresses to receive the completion report. If omitted, the final summary is presented in the conversation only.
