---
name: connection-pending-state-tracker
description: Monitors and notifies user for connections stuck in provisioning or deprovisioning states.
---

# Connection Pending State Tracker Agent

## Overview
This agent analyzes the lifecycle state of Equinix Fabric connections to identify those stuck in provisioning or deprovisioning state longer than a configured threshold, proactively notifying the user when action may be needed.
This agent runs once immediately by default unless scheduled by user. Recommended schedule: every 4 hours. Only sends email if connections exceed the timeout threshold.

## Prerequisites
None

## Capabilities
- Search for all connections currently in a pending (provisioning or deprovisioning) state
- Deliver a plain-English summary via email

## Instructions

1. Search for connections. Follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/operation/equinixStatus", "operator": "=", "values": ["PROVISIONING", "DEPROVISIONING"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 },
  "sort": [
    {
      "direction": "DESC",
      "property": "/changeLog/updatedDateTime"
    }
  ]
}
```

If the `search_connections` call fails, retry up to 5 attempts total. Before each retry, `wait` briefly, then call `search_connections` again with the same payload. Stop retrying as soon as a call succeeds, and continue to Step 2 with that result. Only give up after all 5 attempts fail.

2. Filter connections by timeout threshold. Calculate the time each connection has been in pending state (`now - updatedDateTime`). Keep only connections where `minutes_in_pending_state > pending_state_timeout_minutes` (default: 30 minutes). If no connections exceed the threshold, stop here and do not send an email. Otherwise, proceed to Step 3 with the filtered list.

3. Structure the report below:
### Section content
- **Summary**: 3–5 sentences — count of connections exceeding timeout, headline finding, insights.
- **Connection Activity**: Include name, uuid, state, project, created and updated dates. Also include how long has it been in pending state in hours. Put values under Data Row.

```
<div class="header">
    <h1>Connection Pending State Tracker Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Connection Activity</h2>
    <div class="content">
        <div class="table-container">
            <!-- Header Row -->
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>State</li>
                <li>Created Date</li>
                <li>Updated Date</li>
                <li>Hours in Pending State</li>
            </ul>

          <!-- Data Row-->
          <ul class="table-row">

          </ul>
        </div>
    </div>
</div>

```

4. Use `send_email_notification` to send the report to `recipient_email_addresses`. Follow the email rules below:
- `pdfContent`: the full report text from Step 3.
- `body`: one-paragraph summary of connections exceeding timeout threshold and recommended actions.
- `pdfTitle`: `ConnectionPendingStates`

## Available Tools
- **`search_connections`**: Searches for connections.
- **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Only send email if connections exceed the timeout threshold. Do not send email if all connections are within acceptable time.
- If `search_connections` fails on all 5 attempts, do not send email.
- Always use the configured `pending_state_timeout_minutes` value; if not provided, default to 30 minutes.

## Configuration
- **`recipient_email_addresses`**: Required. List of email addresses to receive the report.
- **`pending_state_timeout_minutes`**: Optional. Threshold in minutes; only connections exceeding this time in provisioning/deprovisioning state are reported. If not provided, defaults to 30 minutes.
