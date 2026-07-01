---
name: project-lifecycle-activities-insight
description: Analyzes all cloud events within a given Equinix Fabric project and delivers a summarized status report over a specified time range
---

# Project Lifecycle Activities Insight Report Agent

## Overview
This reporting agent analyzes all cloud events within a given Equinix Fabric project over a specified time range and delivers a plain-English operational health summary report via email. This agent runs once immediately by default unless scheduled by user.

## Prerequisites
A valid Equinix Fabric project UUID must be available. The project must have cloud events enabled and assets attached to it.

## Capabilities
- Analyze all cloud events within a given Equinix Fabric project over a specified time range
- Detect BGP/routing instability, provisioning churn, and critical events
- Deliver a plain-English operational health summary via email as a summarized report in PDF format

## Instructions

### Step 1 — Establish Reporting Window
1a. Determine which inputs have been provided and follow exactly one branch below. Do not compute or hardcode timestamps manually — always use the `get_timestamps` MCP tool when any timestamp is missing. By default (when neither timestamp is provided), `from` is 24 hours before the current UTC time and `to` is the current UTC time.

| Inputs provided                                  | Action                                                                                                                        |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Neither** `from_timestamp` nor `to_timestamp`  | Call `get_timestamps` with `duration` = `"24h"`. Set `from_timestamp` = `from` field, `to_timestamp` = `to` field.            |
| **Only** `from_timestamp` provided               | Call `get_timestamps` with `duration` = `"24h"`. Set `to_timestamp` = `to` field. Keep the provided `from_timestamp` as-is.   |
| **Only** `to_timestamp` provided                 | Call `get_timestamps` with `duration` = `"24h"`. Set `from_timestamp` = `from` field. Keep the provided `to_timestamp` as-is. |
| **Both** timestamps provided                     | Skip `get_timestamps`. Use both values as-is.                                                                                 |

`get_timestamps` returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Only extract the field(s) you need per the branch above.

**On any retry or failure at any subsequent step, do not reuse previously obtained timestamps. Call `get_timestamps` again with the same `duration` values (i.e. `from` and `to` fields) that was originally used to obtain a fresh `from_timestamp` and `to_timestamp` (for whichever field(s) were originally derived from the tool) before retrying.**

1b. Both timestamps must be ISO 8601 strings (e.g., `2026-02-24T10:00:00.000Z`). Date-only strings are not valid.

1c. Validate:
- `from_timestamp` must be strictly less than 90 days before `to_timestamp` (i.e., the difference must be less than 90 days at the second level of precision). If it is 90 days or more, reset and note the adjustment.
- `to_timestamp` must not be in the future. If it is, reset to the `to` value from `get_timestamps` with `duration` = `"24h"`.
- `from_timestamp` must be earlier than `to_timestamp`. If not, stop and report an error.

### Step 2 — Retrieve All Cloud Events
Using `from_timestamp` and `to_timestamp` established in Step 1, call `search_cloud_events` with:

```json
{
  "filter": {
    "and": [
      { "property": "/equinixproject", "operator": "=", "values": ["<project_uuid>"] },
      { "property": "/time", "operator": ">=", "values": ["<from_timestamp>"] },
      { "property": "/time", "operator": "<=", "values": ["<to_timestamp>"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 }
}
```
Replace `<project_uuid>` with the configured project UUID, `<from_timestamp>` with the value set in Step 1, and `<to_timestamp>` with the value set in Step 1. Do not use any other timestamp source.

If total events exceed the page limit, repeat with incremented offsets until all events are collected or 500 events maximum are reached.

### Step 3 — Normalize and Classify Events
Build the following in-memory groupings:

#### 3a. Classify each event:
- **Routing / BGP Health**: `equinix.fabric.connection_bgpipv4_session.status.*`, `equinix.fabric.connection_bgpipv6_session.status.*`, `equinix.fabric.routing_protocol_action.state.*`
- **Connection Lifecycle**: `equinix.fabric.connection.state.*`, `equinix.fabric.connection.attribute.*`
- **Router Events**: `equinix.fabric.router.*`, `equinix.fabric.router_action.state.*`, `equinix.fabric.router_command.state.*`
- **Port Events**: `equinix.fabric.port.*`, `equinix.fabric.physical_port.*`
- **Provisioning Lifecycle**: event type contains `.state.provisioning`, `.state.reprovisioning`, `.state.deprovisioning`, `.state.failed`
- **Administrative / Low-Signal**: `equinix.fabric.service_token.*` or `severitynumber` <= 9

#### 3b. Group BGP/Routing events by session:
- Key: connection UUID + routing protocol UUID (from subject path `/fabric/v4/connections/<conn-uuid>/routingProtocols/<rp-uuid>`). Always use the full UUID in the report.
- Sort events by timestamp ascending, track ordered state transitions.
- Extract neighbor IP from `data.message` where present.
- Extract and retain `data.resource.name` for the asset where present.

#### 3c. Group provisioning events by asset:
- Key: subject UUID
- Track count of provisioning, reprovisioning, deprovisioning, and failed transitions per asset.
- Extract and retain `data.resource.name` for the asset where present.
- For user-initiated events, extract and retain `data.auth.name` (human-readable name) alongside `authid` from the event root.

After completing 3a–3c, discard all raw event payloads. Carry forward only in-memory groupings and derived summaries. Do not pass raw event data into any downstream step.

### Step 4 — Detect Behavioral Patterns

#### 4a. BGP / Routing Session Flap Detection
For each session group:
- Count idle↔connect oscillation cycles and determine the instability window.
- Determine the final state from the last observed event type suffix.
- Classify: 0–1 transitions = routine, 2–3 = transient instability, 4+ = flapping.
- If final state is `idle` or `failed` and last event is >5 min before `to_timestamp`: session may still be down.

#### 4b. Provisioning Churn Detection
- Flag any asset with 3+ provisioning-type transitions as elevated churn.
- Determine if churn is isolated (few assets) or systemic (many assets).

#### 4c. Overall Health Assessment
Assign one label — do not expose scoring in the report:
- **"All Clear"** — No WARN/CRIT events, no BGP instability, no provisioning churn
- **"Active Change Window"** — High provisioning activity, no routing issues
- **"Routing Instability Detected"** — One or more BGP sessions flapping or in failed/idle final state
- **"Elevated Risk"** — Routing instability + provisioning churn present, or any CRIT-level event
- **"Migration in Progress"** — High provisioning/deprovisioning churn, low/no WARN events

### Step 5 — Compose the Intelligence Report
Do NOT write the report as prose in your response text. Compose in-memory only, then immediately call `send_email_notification`. The report must only appear as the `pdfContent` parameter — never in the response body.

**Do not respond to the user between Step 5 and Step 6. Proceed directly to calling `send_email_notification`.**

Structure the report using these sections. Do not include any section numbers in the headings. Use the separator formatting shown below exactly. **If a section has no content, omit both the section label and its separator entirely — do not write the heading, do not write placeholder or filler text such as "No events were detected" or "None". The only exception is "What You Should Do", which must always be included.**

```
<div class="header">
    <h1>Project Lifecycle Activities Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Project & User Activity</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Fabric Cloud Router Activity</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Connection Activity</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Routing Protocol & BGP Health</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Events That Need Your Attention</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>What You Should Do</h2>
    <div class="content">
    </div>
</div>
```

Section content rules:
- **Summary**: State the Project UUID and reporting period, then 3–5 sentences — total events, asset types active, headline finding, routine or needs attention.
- **Project & User Activity**: Include only if human/API actors or administrative events exist — otherwise omit entirely. List active users as `<data.auth.name> (id: <authid>)` with event counts and plain English description of their activity. Note service token expirations as informational only.
- **Fabric Cloud Router Activity**: Include only if router events exist — otherwise omit entirely. Note churn (3+ transitions) as elevated. List each router as `<data.resource.name> (<full-uuid>)` with plain English description of activity.
- **Connection Activity**: Include only if connection events exist — otherwise omit entirely. Note churn (3+ transitions). List each connection as `<data.resource.name> (<full-uuid>)` with description and last observed state.
- **Routing Protocol & BGP Health**: Include only if BGP/routing events exist — otherwise omit entirely. Reference sessions using both the connection name/full UUID and routing protocol full UUID. Per session: state 0–1 transitions = routine, 2–3 = transient but recovered, 4+ = flapping. Always state final observed session state.
- **Events That Need Your Attention**: Include only if WARN/CRIT events exist — otherwise omit entirely. List up to 10, humanized — no raw event type strings. Format: `[WARN] <time UTC> - <description>`, Asset (use name + full UUID), Detail, Severity.
- **What You Should Do**: 1–3 plain English recommendations based only on detected findings. If nothing needs action, always end with: "No issues were detected and no action is required at this time. I will continue monitoring any new events for you."

Rules:
- Plain English always. No raw event type strings, no API jargon.
- Always use both the human-readable name AND the full UUID when referencing any asset (router, connection, port, routing protocol) or user. Format: `<name> (<full-uuid>)` for assets and `<data.auth.name> (id: <authid>)` for users. If a name is not available, fall back to the full UUID only.
- Final observed state must be stated for any asset with multiple transitions.

### Step 6 — Send the Report
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
- Separate WARN/CRIT from INFO. Never let service token expirations inflate the health assessment.
- If the search API fails, stop without sending.

## Configuration
- **`project_uuid`**: Required. A valid Equinix Fabric project UUID.
- **`recipient_email_addresses`**: Required. List of email addresses to receive the report.
- **`from_timestamp`**: Optional. ISO 8601 (e.g., `2026-02-24T10:00:00.000Z`). If not provided, `get_timestamps` is called in Step 1 to derive it (defaults to 24 hours before current UTC).
- **`to_timestamp`**: Optional. ISO 8601 (e.g., `2026-02-24T10:00:00.000Z`). If not provided, `get_timestamps` is called in Step 1 to derive it (defaults to current UTC).
