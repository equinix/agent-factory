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
2. Search for ports. Follow the request payload below:
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
3. Search for routers. Follow the request payload below:

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
4. Structure the report below:
### Section content
- **Summary**: 3–5 sentences — total count, headline finding, insights.
- **Fabric Cloud Router Activity**: Include only if routers exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date.
- **Connection Activity**: Include only if connections exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date.
- **Port Activity**: Include only if connections exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date.

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
        .table-container {
          width: 100%;
          max-width: 600px;
        }
        
        .table-row {
          display: flex;
          list-style: none;
          padding: 0;
          margin: 0;
          border-bottom: 1px solid #ddd;
        }
        
        .table-row li {
          flex: 1;
          padding: 10px;
        }
        
        .header {
          background-color: #f4f4f4;
          font-weight: bold;
          border-top: 2px solid #333;
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
            <div class="table-container">
                <!-- Header Row -->
                <ul class="table-row header">
                    <li>Name</li>
                    <li>UUID</li>
                    <li>Role</li>
                </ul>
              
              <!-- Data Row-->
              <ul class="table-row">
              </ul>
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

5. Use `send_email_notification` to send the report to `recipient_email_address`. Follow the email rules below:
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricPendingStates_<today>` — Use only the date portion (`YYYY-MM-DD`), not the full ISO 8601 string.

## Available Tools
- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Skip empty sections entirely — no placeholder text. If no results found, send email with "No activity detected".
- If the search APIs fail, stop without sending.
- Section content rules of Report:

## Configuration
- **`recipient_email_address`**: Required. List of email addresses to receive the report.
