---
name: port-pending-state-tracker
description: Monitors and notifies user for ports stuck in provisioning or deprovisioning states.
categories: ["Monitor & Report Agents""]
---

# Port Pending State Tracker Agent

## Overview
This agent analyzes the lifecycle state of Equinix Fabric ports to identify those stuck in provisioning or deprovisioning state longer than a configured threshold, proactively notifying the user when action may be needed.
This agent runs once immediately by default unless scheduled by user. Recommended schedule: every 4 hours. Only sends email if ports exceed the timeout threshold.

## Prerequisites
None

## Capabilities
- Search for all ports currently in a pending (provisioning or deprovisioning) state
- Deliver a plain-English summary via email

## Instructions

1. Search for ports. Follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/state", "operator": "=", "values": ["PROVISIONING", "DEPROVISIONING"] }
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

If the `search_ports` call fails, retry up to 5 attempts total. Before each retry, call `wait` with `waitInMilliseconds` = `3000` (3 seconds), then call `search_ports` again with the same payload. Stop retrying as soon as a call succeeds, and continue to Step 2 with that result. Only give up after all 5 attempts fail.

2. Call `get_timestamps` with `duration` = `"24h"` to obtain the current UTC time. If the call fails, do not send an email and stop processing. If the call succeeds, use the `to` field as `now` (ignore `from`). For each port from Step 1, calculate `minutes_in_pending_state` = `now` − `changeLog.updatedDateTime`, in minutes. Keep only ports where `minutes_in_pending_state > pending_state_timeout_minutes` (default: 30 minutes). If no ports exceed the threshold, stop here and do not send an email. Otherwise, proceed to Step 3 with the filtered list.

3. Structure the report below:
### Section content
- **Summary**: 3–5 sentences — count of ports exceeding timeout, headline finding, insights.
- **Port Activity**: Include name, uuid, state, project, created and updated dates. Also include how long has it been in pending state in hours. Put values under Data Row.

```
<div class="header">
    <h1>Port Pending State Tracker Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Port Activity</h2>
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
- `body`: one-paragraph summary of ports exceeding timeout threshold and recommended actions.
- `pdfTitle`: `PortPendingStates`

## Available Tools
- **`search_ports`**: Searches for ports.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a required duration string (e.g., `"24h"`, `"7d"`). `to` is always the current UTC time; `from` is `to` minus the duration. Use the `to` field as the current UTC time reference for calculating time-in-state. Do not compute or hardcode the current time manually.
- **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Only send email if ports exceed the timeout threshold. Do not send email if all ports are within acceptable time.
- If `search_ports` fails on all 5 attempts, do not send email.
- If `get_timestamps` fails at any point, do not send email — a reliable current time is essential for accurate time-in-state calculation.
- Always use the configured `pending_state_timeout_minutes` value; if not provided, default to 30 minutes.
- Never estimate or hardcode the current time — always call `get_timestamps` to get an authoritative `now` before calculating time-in-state.
- Wait 3 seconds between `search_ports` retry attempts to avoid overwhelming the API with rapid retries.

## Configuration
- **`recipient_email_addresses`**: Required. List of email addresses to receive the report.
- **`pending_state_timeout_minutes`**: Optional. Threshold in minutes; only ports exceeding this time in provisioning/deprovisioning state are reported. If not provided, defaults to 30 minutes.
