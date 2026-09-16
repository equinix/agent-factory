---
name: connection-pending-state-tracker
description: Monitors and notifies user for connections stuck in provisioning or deprovisioning states.
categories: ["Monitor & Report Agents"]
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

2. Call `get_timestamps` with `duration` = `"24h"` to obtain the current UTC time. Use the `to` field as `now` (ignore `from`). For each connection from Step 1, calculate `minutes_in_pending_state` = `now` − `changeLog.updatedDateTime`, in minutes. Keep only connections where `minutes_in_pending_state > pending_state_timeout_minutes` (default: 30 minutes). If no connections exceed the threshold, stop here and do not send an email. Otherwise, proceed to Step 3 with the filtered list.

3. Retrieve the email template that will be used for the report.

4. Structure the report below using the email template from Step 3.
### Header
**Connection Pending State Tracker Report**:
### Section content
- **Summary**: 3–5 sentences — count of connections exceeding timeout, headline finding, insights.
- **Connection Activity**: Include Name, UUID, State, Project, Created Date, and Updated Date. Also include how long has it been in pending state in hours. Call it 'Hours in Pending State'. Put values under Data Row.

5. Use `send_email_notification` to send the report to `recipient_email_addresses`. Follow the email rules below:
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of connections exceeding timeout threshold and recommended actions.
- `pdfTitle`: `ConnectionPendingStates`

## Available Tools
- **`search_connections`**: Searches for connections.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a required duration string (e.g., `"24h"`, `"7d"`). `to` is always the current UTC time; `from` is `to` minus the duration. Use the `to` field as the current UTC time reference for calculating time-in-state. Do not compute or hardcode the current time manually.
- **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
- **`get_email_template`**: Get email template.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Only send email if connections exceed the timeout threshold. Do not send email if all connections are within acceptable time.
- If `search_connections` fails on all 5 attempts, do not send email.
- Always use the configured `pending_state_timeout_minutes` value; if not provided, default to 30 minutes.
- Never estimate or hardcode the current time — always call `get_timestamps` to get an authoritative `now` before calculating time-in-state.

## Configuration
- **`recipient_email_addresses`**: Required. List of email addresses to receive the report.
- **`pending_state_timeout_minutes`**: Optional. Threshold in minutes; only connections exceeding this time in provisioning/deprovisioning state are reported. If not provided, defaults to 30 minutes.
