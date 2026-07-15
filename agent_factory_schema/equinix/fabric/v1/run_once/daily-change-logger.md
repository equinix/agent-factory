---
name: daily-change-report
description: Identify connections, ports, cloud routers, networks, internet access, and network edge change events in past 24 hours; compile change summary with owners and distribute a daily report.
---

# Daily Asset Change Report Agent

## Overview
Identify connections, ports, cloud routers, networks, internet access, and network edge change events in past 24 hours; compile change summary with owners and distribute a daily report.

## Capabilities
- Analyze all cloud events within a given Equinix Fabric project over the past 24 hours
- Deliver a plain-English daily report for changed assets summary via email as a summarized report in PDF format

## Prerequisites
- Valid Equinix Fabric project UUIDs must be available. The project must have cloud events enabled and assets attached to it.

## Instructions

### Step 1 — Establish Reporting Window
1a. Determine which timestamps for 24 hours. Do not compute or hardcode timestamps manually — always use the `get_timestamps` MCP tool when any timestamp is missing. By default (when neither timestamp is provided), `from` is 24 hours before the current UTC time and `to` is the current UTC time.

`get_timestamps` returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Only extract the field(s) you need per the branch above.

**On any retry or failure at any subsequent step, do not reuse previously obtained timestamps. Call `get_timestamps` again with the same `duration` values (i.e. `from` and `to` fields) that was originally used to obtain a fresh `from_timestamp` and `to_timestamp` (for whichever field(s) were originally derived from the tool) before retrying.**

1b. Both timestamps must be ISO 8601 strings (e.g., `2026-02-24T10:00:00.000Z`). Date-only strings are not valid.

1c. Validate:
- `from_timestamp` must be strictly less than or equal to 24 hours before `to_timestamp` (i.e., the difference must be less than 90 days at the second level of precision).
- `to_timestamp` must not be in the future and use current timestamp. If it is, reset to the `to` value from `get_timestamps` with `duration` = `"24h"`.
- `from_timestamp` must be earlier than `to_timestamp`. If not, stop and report an error.

### Step 2 — Retrieve All Cloud Events
Using `from_timestamp` and `to_timestamp` established in Step 1, call `search_cloud_events` with:

```json
{
  "filter": {
    "and": [
      { "property": "/type", "operator": "IN", "values": [
        "equinix.fabric.connection.attribute.changed",
        "equinix.fabric.connection.state.deprovisioned",
        "equinix.fabric.connection.state.deprovisioning",
        "equinix.fabric.connection.state.reprovisioning",
        "equinix.fabric.port.state.deprovisioned",
        "equinix.fabric.port.state.deprovisioning",
        "equinix.fabric.port.state.inactive",
        "equinix.fabric.port.state.reprovisioning",
        "equinix.fabric.router.attribute.changed",
        "equinix.fabric.router.state.deprovisioned",
        "equinix.fabric.router.state.deprovisioning",
        "equinix.fabric.router.state.not_deprovisioned",
        "equinix.fabric.router.state.not_provisioned",
        "equinix.fabric.router.state.reprovisioning",
        "equinix.fabric.network.attribute.changed",
        "equinix.fabric.network.state.deprovisioned",
        "equinix.fabric.network.state.deprovisioning",
        "equinix.fabric.internet_access.attribute.changed",
        "equinix.fabric.internet_access.attribute.changing",
        "equinix.fabric.internet_access.attribute.failed",
        "equinix.fabric.internet_access.state.deprovisioned",
        "equinix.fabric.internet_access.state.deprovisioning",
        "equinix.network_edge.device.attribute.changed",
        "equinix.network_edge.device.reboot.completed",
        "equinix.network_edge.device.reboot.started",
        "equinix.network_edge.device.state.cancelled",
        "equinix.network_edge.device.state.deleted"
      ] },
      { "property": "/equinixproject", "operator": "IN", "values": ["<project_uuid>","<project_uuid>"] },
      { "property": "/time", "operator": ">=", "values": ["<from_timestamp>"] },
      { "property": "/time", "operator": "<=", "values": ["<to_timestamp>"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 }
}
```
Replace `<project_uuid>` with the configured project UUID or multiple project UUIDs, `<from_timestamp>` with the value set in Step 1, and `<to_timestamp>` with the value set in Step 1. Do not use any other timestamp source.

If total events exceed the page limit, repeat with incremented offsets until all events are collected or 500 events maximum are reached.

### Step 3 — Normalize and Classify Events
Build the following in-memory groupings:

#### 3a. Classify each creation event:
- **Connection Updated Events**: anything beginning with `equinix.fabric.connection.`
- **Port Updated Events**: anything beginning with `equinix.fabric.port.`
- **Cloud Router Updated Events**: anything beginning with `equinix.fabric.router.`
- **Network Updated Events**: anything beginning with `equinix.fabric.network.`
- **Internet Access Updated Events**: anything beginning with `equinix.fabric.internet_access.`
- **Network Edge Device Updated Events**: anything beginning with `equinix.network_edge.`

#### 3b. Group provisioned, provisioning, failed, pending, events by asset:
- Key: subject UUID
- Track count of deprovisioning, attribute changed, deprovisioned, reprovisioned, and failed transitions per asset.
- Extract and retain `data.resource.name` for the asset where present.
- For user-initiated events, extract and retain `data.auth.name` (human-readable name) alongside `authid` from the event root.

After completing 3a–3b, discard all raw event payloads. Carry forward only in-memory groupings and derived summaries. Do not pass raw event data into any downstream step.

### Step 4 — Compose the Intelligence Report
Do NOT write the report as prose in your response text. Compose in-memory only, then immediately call `send_email_notification`. The report must only appear as the `pdfContent` parameter — never in the response body.

**Do not respond to the user between Step 5 and Step 6. Proceed directly to calling `send_email_notification`.**

Structure the report using these sections. Do not include any section numbers in the headings. Use the separator formatting shown below exactly. **If a section has no content, omit both the section label and its separator entirely — do not write the heading, do not write placeholder or filler text such as "No events were detected" or "None". The only exception is "What You Should Do", which must always be included.**

```
<div class="header">
    <h1>Daily Equinix Updated Assets Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Connection Updated Events</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Port Updated Events</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Cloud Router Updated Events </h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Network Updated Events</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Internet Access Updated Events</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Network Edge Device Updated Events</h2>
    <div class="content">
    </div>
</div>
```

Section content rules:
- **Summary**: State the Project UUID and reporting period, then 3–5 sentences — total events, asset types active, headline finding, routine or needs attention.
- **Connection Created Activity**: Include only if connection events exist — otherwise omit entirely. Note churn (3+ transitions). List each connection as `<data.resource.name> (<full-uuid>)` with plain English description of activity.
- **Port Created Activity**: Include only if router events exist — otherwise omit entirely. Note churn (3+ transitions) as elevated. List each router as `<data.resource.name> (<full-uuid>)` with plain English description of activity.
- **Cloud Router Created Activity**: Include only if router events exist — otherwise omit entirely. Note churn (3+ transitions) as elevated. List each router as `<data.resource.name> (<full-uuid>)` with plain English description of activity.
- **Network Created Activity**: Include only if router events exist — otherwise omit entirely. Note churn (3+ transitions) as elevated. List each router as `<data.resource.name> (<full-uuid>)` with plain English description of activity.
- **Internet Access Created Activity**: Include only if router events exist — otherwise omit entirely. Note churn (3+ transitions) as elevated. List each router as `<data.resource.name> (<full-uuid>)` with plain English description of activity.
- **Network Edge Device Activity**: Include only if router events exist — otherwise omit entirely. Note churn (3+ transitions) as elevated. List each router as `<data.resource.name> (<full-uuid>)` with plain English description of activity.

Rules:
- Plain English always. No raw event type strings, no API jargon.
- Always use both the human-readable name AND the full UUID when referencing any asset (router, connection, port, routing protocol) or user. Format: `<name> (<full-uuid>)` for assets and `<data.auth.name> (id: <authid>)` for users. If a name is not available, fall back to the full UUID only.

### Step 5 — Send the Report
Use `send_email_notification` to send the report to `recipient_email_addresses`.
- `pdfContent`: the full report text from Step 5.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricInsights_<project_uuid>_<reporting period from date>_<reporting period to date>_<Overall Status label>` — Use only the date portion (`YYYY-MM-DD`) of each timestamp, not the full ISO 8601 string.

## Available Tools
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
- **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` with `/time` `>=` and `<=` to scope by project and time window.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Summarize all event data in-memory. Discard raw payloads after Step 3. Do not pass raw events downstream.
- Skip empty sections entirely — no placeholder text. If no events found, send email with "No activity detected".
- Never let service token expirations inflate the health assessment.
- If the search API fails, stop without sending.

## Configuration
- **`project_uuid`**: Required. A list of Fabric project UUID(s).
- **`recipient_email_addresses`**: Required. List of email addresses to receive the report.