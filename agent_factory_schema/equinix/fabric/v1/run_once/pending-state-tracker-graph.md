---
execution_mode: graph
graph_pattern: dag
name: pending-state-tracker-graph
description: Monitors and notifies user for long running Fabric assets in provisioning or deprovisioning states.
---

# Pending State Tracker Agent

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
4. Structure the report below:
### Section content
- **Summary**: 3–5 sentences — total count, headline finding, insights.
- **Fabric Cloud Router Activity**: Include only if routers exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date in hours. Put values under Data Row.
- **Connection Activity**: Include only if connections exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date in hours. Put values under Data Row.
- **Port Activity**: Include only if connections exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date in hours. Put values under Data Row.

```
<div class="header">
    <h1>Pending State Tracker Report</h1>
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
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>State</li>
                <li>Created Date</li>
                <li>Updated Date</li>
                <li>Hours Since Creation</li>
            </ul>
          
          <!-- Data Row-->
          <ul class="table-row">

          </ul>
        </div>
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
                <li>Hours Since Creation</li>
            </ul>
          
          <!-- Data Row-->
          <ul class="table-row">
          </ul>
                              <li>xd</li>
                <li>UUID</li>
                <li>State</li>
                <li>Created Date</li>
                <li>Updated Date</li>
                <li>Hours Since Creation</li>
        </div>
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
                <li>Hours Since Creation</li>
            </ul>
          
          <!-- Data Row-->
          <ul class="table-row">
          </ul>
        </div>
    </div>
</div>

```

5. Use `send_email_notification` to send the report to `recipient_email_addresses`. Follow the email rules below:
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricPendingStates`

## Available Tools
- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Skip empty sections entirely — no placeholder text. If no results found, send email with "No activity detected".
- If any of the tool call fail, do not send email.


## Configuration
**`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the report.
