---
name: resource-stuck-state-timeout-notifier
description: Detects Fabric connections, ports, and routers stuck in provisioning or deprovisioning past a configurable timeout, and notifies user via email.
categories: ["Monitor & Report Agents"]
---

# Resource Stuck State Timeout Notifier Agent

## Overview
This agent identifies Equinix Fabric connections, ports, and routers stuck in a PROVISIONING or DEPROVISIONING state past a configurable timeout.
This agent runs once immediately by default unless scheduled by user, and emails a report of the affected resources.
This agent is read-only — it never modifies, upgrades, or cancels any resource.

Differs from `asset-pending-state-tracker` and `connection-pending-state-tracker`: this agent applies separate
configurable timeouts for `PROVISIONING` vs. `DEPROVISIONING`, and enriches each stuck connection/port with its
most recent related cloud event for extra context.

## Prerequisites
The `search_connections`, `search_ports`, `search_routers`, `search_cloud_events_by_asset`, `get_timestamps`, `wait`,
and `send_email_notification` tools must all be enabled for this agent.

## Capabilities
- Analyze all connections, ports, and routers currently in a provisioning or deprovisioning state
- Flag only the resources that have exceeded a state-specific timeout
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
If any of the searches in steps 1–3 fails, retry up to 5 attempts total for that search. Before each retry, `wait`
briefly, then call the same search tool again with the same payload. Stop retrying that search as soon as it
succeeds. If a search still fails after 5 attempts, abort the entire run — do not send a partial report, and do not
proceed to step 4.
4. Call `get_timestamps` with `duration` = `"24h"` to obtain the current UTC time. Use the `to` field as `now`
   (ignore `from`) — never estimate or hardcode the current time. For each resource returned in steps 1–3, determine
   its current state (`/operation/equinixStatus` for connections, `/state` for ports and routers) and compute
   elapsed minutes as `now - /changeLog/updatedDateTime` (fall back to `/changeLog/createdDateTime` if
   `updatedDateTime` is absent). Note: the search APIs do not expose a dedicated "entered this state at" timestamp,
   so `updatedDateTime` is used as the best available proxy for state-entry time.
5. Flag a resource as stuck only if:
   - state is `PROVISIONING` and elapsed minutes > `provisioning_timeout_minutes`, OR
   - state is `DEPROVISIONING` and elapsed minutes > `deprovisioning_timeout_minutes`.
   Discard resources within their timeout — they must not appear in the report.
6. For each stuck connection or port, call `search_cloud_events_by_asset` with the resource's `uuid` and a
   `fromDateTime` covering the elapsed window to retrieve the most recent related cloud event as extra context.
   Skip this step for routers — this tool does not support the router resource type. This lookup is best-effort and
   is not retried: if the call fails for a given resource, omit the "Last Related Event" field for that resource
   only — do not abort the run and do not omit the resource itself from the report.
7. Structure the report below:
### Section content
- **Summary**: 3–5 sentences — total stuck count by resource type, headline finding, insights.
- **Fabric Cloud Router Activity**: Include only if stuck routers exist — otherwise omit entirely. Include name, uuid, state, project, updated date, minutes over threshold.
- **Connection Activity**: Include only if stuck connections exist — otherwise omit entirely. Include name, uuid, state, project, updated date, minutes over threshold, last related event (if found in step 6).
- **Port Activity**: Include only if stuck ports exist — otherwise omit entirely. Include name, uuid, state, project, updated date, minutes over threshold, last related event (if found in step 6).

```
<div class="header">
    <h1>Stuck State Timeout Report</h1>
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
                <li>Updated Date</li>
                <li>Minutes Over Threshold</li>
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
                <li>Updated Date</li>
                <li>Minutes Over Threshold</li>
                <li>Last Related Event</li>
            </ul>

          <!-- Data Row-->
          <ul class="table-row">
          </ul>
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
                <li>Updated Date</li>
                <li>Minutes Over Threshold</li>
                <li>Last Related Event</li>
            </ul>

          <!-- Data Row-->
          <ul class="table-row">
          </ul>
        </div>
    </div>
</div>
```

8. Use `send_email_notification` to send the report to `recipient_email_addresses`. Follow the email rules below:
- `pdfContent`: the full report text from Step 7.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricStuckStateAlert`

## Available Tools
- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`search_cloud_events_by_asset`**: Retrieves recent cloud events for a given connection or port UUID. Not supported for routers.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`). Use the `to` field as the current UTC time reference for calculating elapsed minutes. Do not compute or hardcode the current time manually.
- **`wait`**: Wait for a while before retrying a failed search call. An optional parameter can be provided to specify the wait time in milliseconds.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Skip empty sections entirely — no placeholder text. If no resource exceeds its timeout, send email with "No resources exceeded timeout thresholds".
- Never call any tool that modifies, upgrades, cancels, or deletes a resource. This agent is strictly read-only.
- If any search in steps 1–3 still fails after 5 retries, do not send email.
- Never estimate or hardcode the current time — always call `get_timestamps` to get an authoritative `now` before calculating elapsed minutes in step 4.
- Known limitation — no cross-run deduplication: this agent has no durable state store or ticket-search tool available, so a resource that remains stuck across multiple runs will reappear in every report until it clears. Do not claim or imply deduplication.
- Known limitation — no owner resolution: there is no tool to resolve a resource's owner or account contact, so all reports go to the configured `recipient_email_addresses` rather than a per-resource owner.
- Known limitation — no ticket creation: there is no Jira or support-ticket tool available in this environment. This agent only emails a report; opening a ticket per stuck resource is out of scope until such a tool exists.

## Configuration
* **`provisioning_timeout_minutes`**: < integer > - Optional - Minutes a resource may remain in `PROVISIONING` before being flagged. Default `30`.
* **`deprovisioning_timeout_minutes`**: < integer > - Optional - Minutes a resource may remain in `DEPROVISIONING` before being flagged. Default `20`.
* **`recipient_email_addresses`**: < list of email addresses > - Required - List of email addresses to receive the report.
