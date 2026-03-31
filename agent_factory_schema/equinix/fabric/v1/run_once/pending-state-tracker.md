---
name: pending-state-tracker
description: Monitors and notifies user for long running Fabric assets in provisioning or deprovisioning states.
---

# Project Lifecycle Activities Insight Agent

## Overview
This agent actively analyzes the lifecycle state of Equinix Fabric assets to identify those stuck in provisioning or deprovisioning phases for an extended period, proactively notifying user.
This agent runs once immediately by default unless scheduled by user.

## Prerequisites
None

## Capabilities
- Analyze all pending connections, ports, and routers over a specified time range
- Deliver a plain-English summary via email as a PDF report

## Instructions

1. Search for connections. Follow ### search rules
2. Search for ports. Follow ### search rules
3. Search for routers. Follow ### search rules
4. Structure the report using this format in ### report format.
5. Use `send_email_notification` to send the report to `recipient_email_address`. Follow ### email rules.

### search rules:
Using from_timestamp and to_timestamp from `get_timestamps` response, follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/state", "operator": "=", "values": ["PROVISIONING", "DEPROVISIONING"] },
      { "property": "/time", "operator": ">=", "values": ["<from_timestamp>"] },
      { "property": "/time", "operator": "<=", "values": ["<to_timestamp>"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 }
}
```

### email rules:
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricPendingStates_<reporting period from date>_<reporting period to date>` — Use only the date portion (`YYYY-MM-DD`) of each timestamp, not the full ISO 8601 string.


### report format.
```
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Overall Status Report</title>

    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f6f9;
			margin: 0;
            padding: 30px;
            color: #333;
        }

        .container {
            max-width: 1000px;
            margin: auto;
        }

        .header {
            background: #d60404;
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
        }

        .section {
            background: white;
            border-radius: 8px;
            padding: 20px 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }

        .section h2 {
            margin-top: 0;
            font-size: 20px;
            color: #c40808;
            border-bottom: 2px solid #e6edf5;
            padding-bottom: 8px;
        }

        .content {
            margin-top: 15px;
            line-height: 1.6;
        }

        .footer {
            text-align: center;
            color: #777;
            margin-top: 30px;
            font-size: 12px;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 8px;
        }

        .badge.good {
            background: #d4edda;
            color: #155724;
        }

        .badge.warn {
            background: #fff3cd;
            color: #856404;
        }

        .badge.critical {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>Overall Status Report</h1>
        <p>System Operational Overview</p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <div class="content">
        </div>
    </div>
    
    <div class="section">
        <h2>Cloud Router Activity</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Connection Activity</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Port Activity</h2>
        <div class="content">
        </div>
    </div>
    <div class="footer">
        Generated System Status Report
    </div>

</div>

</body>
</html>
```

#### Section content rules:
- **Summary**: 3–5 sentences — total count, headline finding, insights.
- **Fabric Cloud Router Activity**: Include only if routers exist — otherwise omit entirely. Include uuid, name, description, state, project, created and updated dates. Also include how long has it been since created date.
- **Connection Activity**: Include only if connections exist — otherwise omit entirely. Include uuid, name, description, state, project, created and updated dates. Also include how long has it been since created date.
- **Port Activity**: Include only if connections exist — otherwise omit entirely. Include uuid, name, description, state, project, created and updated dates. Also include how long has it been since created date.

## Available Tools
- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Skip empty sections entirely — no placeholder text. If no results found, send email with "No activity detected".
- If the search APIs fail, stop without sending.

## Configuration
- **`recipient_email_address`**: Required. List of email addresses to receive the report.
- **`from_timestamp`**: Optional. ISO 8601 (e.g., `2026-02-24T10:00:00.000Z`). If not provided, `get_timestamps` is called in Steps 1,2, and 3 to derive it (defaults to 30 days before current UTC).
- **`to_timestamp`**: Optional. ISO 8601 (e.g., `2026-02-24T10:00:00.000Z`). If not provided, `get_timestamps` is called in Steps 1,2, and 3 to derive it (defaults to current UTC).
