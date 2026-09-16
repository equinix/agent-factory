---
name: asset-pending-state-tracker
description: Monitors and notifies user for long running Fabric assets in provisioning or deprovisioning states.
categories: ["Monitor & Report Agents"]
---

# Asset Pending State Tracker Agent

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
  "pagination": { "offset": 0, "limit": 100 }
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
  "pagination": { "offset": 0, "limit": 100 }
}
```
4. Retrieve the email template that will be used for the report.
5. Structure the report below using the email template from Step 4:
#### Header
**Pending State Tracker Report**:
#### Section content
- **Summary**: 3–5 sentences — total count, headline finding, insights.
- **Fabric Cloud Router Activity**: Include only if routers exist — otherwise omit entirely. Include Name, UUID, State, Project, Created Date, and Updated Date. Also include how long has it been in pending state in hours. Call it 'Hours in Pending State'. Put values under Data Row.
- **Connection Activity**: Include only if connections exist — otherwise omit entirely. Include Name, UUID, State, Project, Created Date, and Updated Date. Also include how long has it been in pending state in hours. Call it 'Hours in Pending State'. Put values under Data Row.
- **Port Activity**: Include only if connections exist — otherwise omit entirely. Include Name, UUID, State, Project, Created Date, and Updated Date. Also include how long has it been in pending state in hours. Call it 'Hours in Pending State'. Put values under Data Row.

6. Use `send_email_notification` to send the report to `recipient_email_addresses`. Follow the email rules below:
- `pdfContent`: the full report text from Step 5.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricPendingStates`

## Available Tools
- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`get_email_template`**: Get email template.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Skip empty sections entirely — no placeholder text. If no results found, send email with "No activity detected".
- If any of the tool call fail, do not send email.


## Configuration
**`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the report.
