# Project Lifecycle Activities Insight Agent

## Overview
This definition sets up and activates an Equinix Fabric CloudEvent Intelligence Agent that analyzes all cloud events within a given project over a user-specified time range and delivers a clear, plain-English operational health summary via email. The report is designed to be read in under two minutes — telling the customer exactly what happened, whether anything needs attention, and what action (if any) to take. This agent can only run once.

## Prerequisites
A valid Equinix Fabric project UUID must be available. The project must have cloud events enabled and assets (connections, ports, routers, service tokens, etc.) attached to it.

## Capabilities
- Search all cloud events for a project over a specified time range
- Detect BGP and routing protocol session instability by analyzing state oscillation patterns
- Identify provisioning churn and distinguish planned lifecycle changes from potential automation or configuration issues
- Separate high-signal operational events (WARN/CRIT) from low-signal administrative noise (INFO token expiry, system heartbeats)
- Determine current asset health by analyzing the final observed state of each asset
- Classify the overall operational posture of the project in plain language
- Generate a concise, human-readable intelligence summary
- Send the summary as an email notification to the designated recipient

## Follow the action step by step below:

### Step 1 — Establish Reporting Window
1a. Determine the current UTC time dynamically at the moment this agent runs. Do not assume, guess, or use any hardcoded or previously seen timestamp as the current time. Always derive it from the system clock at execution time.

1b. Apply the following logic to set the reporting window:
- If the user provided both `from_timestamp` and `to_timestamp`, use them as-is.
- If the user provided only `from_timestamp`, set `to_timestamp` to the current UTC time.
- If the user provided only `to_timestamp`, set `from_timestamp` to exactly 24 hours before `to_timestamp`.
- If the user provided neither, set `to_timestamp` to the current UTC time and set `from_timestamp` to exactly 24 hours before `to_timestamp`.

1c. Both timestamps must be formatted as ISO 8601 strings (e.g., `2026-02-24T10:00:00.000Z`). Do not omit the time component — date-only strings are not valid.

1d. Validate the final window before proceeding:
- `from_timestamp` must not be more than 89 days before the current UTC time. If it is, reset `from_timestamp` to 89 days before the current UTC time and note this adjustment in the report.
- `to_timestamp` must not be in the future beyond the current UTC time. If it is, reset it to the current UTC time.
- `from_timestamp` must be earlier than `to_timestamp`. If not, stop and report an error.

### Step 2 — Retrieve All Cloud Events
Search for all cloud events for the given project UUID using the `search_cloud_events` tool with the following filter:

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

If total events exceed the page limit, repeat with incremented offsets until all events are collected or 500 events maximum are reached.

### Step 3 — Normalize and Classify Events
From the collected events, build the following in-memory groupings:

#### 3a. Classify each event into one of these categories:
- **Routing / BGP Health**: event type matches `equinix.fabric.connection_bgpipv4_session.status.*`, `equinix.fabric.connection_bgpipv6_session.status.*`, `equinix.fabric.routing_protocol_action.state.*`
- **Connection Lifecycle**: event type matches `equinix.fabric.connection.state.*`, `equinix.fabric.connection.attribute.*`
- **Router Events**: event type matches `equinix.fabric.router.*`, `equinix.fabric.router_action.state.*`, `equinix.fabric.router_command.state.*`
- **Port Events**: event type matches `equinix.fabric.port.*`, `equinix.fabric.physical_port.*`
- **Provisioning Lifecycle**: event type contains `.state.provisioning`, `.state.reprovisioning`, `.state.deprovisioning`, `.state.failed`
- **Administrative / Low-Signal**: event type matches `equinix.fabric.service_token.*` or `severitynumber` <= 9 (INFO level)

#### 3b. Group BGP/Routing events by session:
- Key: composite of connection UUID + routing protocol UUID (both parsed from the subject path, e.g., `/fabric/v4/connections/<conn-uuid>/routingProtocols/<rp-uuid>`)
- For each session, sort events by timestamp ascending and track the ordered sequence of state transitions
- Extract neighbor IP from `data.message` where present (e.g., "Neighbor 169.254.96.1 address session state changed to Connect")

#### 3c. Group provisioning events by asset:
- Key: subject UUID
- Track count of provisioning, reprovisioning, deprovisioning, and failed state transitions per asset

### Step 4 — Detect Behavioral Patterns

#### 4a. BGP / Routing Session Flap Detection
For each routing session group:
- Identify oscillation: alternating transitions between states such as `status.connect` → `status.idle` → `status.connect` → `status.idle`
- Count the number of idle↔connect or equivalent oscillation cycles
- Determine the instability window: time between the first and last transition
- Determine the final state: the suffix of the last observed event type (`connect` = session currently up, `idle` or `failed` = session currently down)
- Classify the session as follows:
  - 0–1 transitions: routine state change, no concern
  - 2–3 oscillations: transient instability, worth monitoring
  - 4+ oscillations: session is flapping — needs investigation
  - Final state is `idle` or `failed` and the last event is more than 5 minutes before `to_timestamp`: session may still be down at the end of the window

#### 4b. Provisioning Churn Detection
- Flag any asset with 3 or more provisioning-type transitions as showing elevated churn
- Count how many distinct assets are flagged
- Determine whether the churn is concentrated on a few assets (isolated) or spread across many (systemic)

#### 4c. Overall Health Assessment
Assign one of the following plain-English labels based on observed patterns. Do not expose any formula or scoring in the report output:
- **"All Clear"** — No WARN/CRIT events, no BGP instability, no provisioning churn
- **"Active Change Window"** — High provisioning activity but no routing issues; likely planned work
- **"Routing Instability Detected"** — One or more BGP sessions are flapping or in a failed/idle final state
- **"Elevated Risk"** — Both routing instability and provisioning churn are present, or any CRIT-level event was observed
- **"Migration in Progress"** — High provisioning/deprovisioning churn, low or no WARN events, pattern consistent with a planned migration

### Step 5 — Compose the Intelligence Report
Write the report in plain, conversational English. Do not include raw JSON, full UUIDs (use the first 8 characters only), or technical jargon without explanation. Use the hierarchical structure below exactly — starting from the broadest summary and drilling down to the most specific routing-level detail:

```
Fabric Operational Health Summary
Project : <project_uuid>
Period  : <from_timestamp> -> <to_timestamp> (UTC)

==========================================
Overall Status: <plain English label from Step 4c>
==========================================

------------------------------------------
1. Summary
------------------------------------------
<Write 3-5 sentences summarizing the entire period in plain English. Cover:
total events observed, how many distinct asset types were active, the headline
operational finding, and whether the period appears routine or warrants
attention. This section must give the customer a complete picture at a glance
without needing to read further.
Example: "A total of 34 events were recorded across your project during this
window. Activity spanned routers, connections, and routing protocols. The
majority of events reflect provisioning lifecycle changes consistent with an
active deployment. One routing protocol session showed repeated instability
and may require your attention. All other assets appear healthy.">

------------------------------------------
2. Project & User Activity
------------------------------------------
INCLUDE THIS SECTION ONLY if there are human/API-authenticated user events
OR administrative events (e.g. service token expirations) to report.
If all events are purely system-generated AND there are no administrative
events, skip this entire section including its heading.

<If this section is included:>

<If any human or API actors are present (excluding "equinix" system actor):>
Users Active This Period:
- <authid>: <N> events - primarily <short description, e.g., "connection
  provisioning and bandwidth configuration changes">

<If all events were system-generated (include only when section is kept due
to administrative events):>
All activity in this window was initiated by Equinix system processes.
No user-driven changes were detected.

<If any administrative events (service token expirations, system
notifications) were observed:>
Administrative Events (No Action Required):
<N> low-signal administrative events were recorded (e.g., service token
expirations, system notifications). These are informational only and have
no impact on the health assessment above.

------------------------------------------
3. Fabric Cloud Router Activity
------------------------------------------
INCLUDE THIS SECTION ONLY if router events were observed in this window.
If no router events exist, skip this entire section including its heading.

<If this section is included:>
<N> routers recorded activity during this period.

<If provisioning churn detected on any router (3+ provisioning transitions):>
"<N> router(s) show an elevated number of provisioning lifecycle changes.
This may indicate a planned migration, repeated configuration retries, or an
automation workflow cycling through states. If this activity was not
intentional, it is worth reviewing your automation or deployment pipeline."

<List routers with notable activity:>
- Router <uuid-first-8>: <N> events - <plain English description of what
  this router was doing, e.g., "went through repeated provisioning and
  reprovisioning cycles" / "received configuration attribute updates" /
  "executed router action commands">

<If no churn and activity is routine:>
"Router activity appears normal and consistent with routine infrastructure
management."

------------------------------------------
4. Connection Activity
------------------------------------------
INCLUDE THIS SECTION ONLY if connection events were observed in this window.
If no connection events exist, skip this entire section including its heading.

<If this section is included:>
<N> connections recorded activity during this period.

<If provisioning churn detected on any connection (3+ transitions):>
"<N> connection(s) show an unusually high number of provisioning changes.
This level of activity can indicate a planned migration, repeated
configuration retries, or an automation workflow cycling through states.
If this activity was not intentional, it is worth reviewing your automation
or deployment pipeline for this project."

<List connections with notable activity:>
- Connection <uuid-first-8>: <N> events - <plain English description, e.g.,
  "went through provisioning and deprovisioning cycles" / "bandwidth
  configuration was updated" / "connection state changed to Active">
  Last observed state: <state if determinable, e.g., Active / Deprovisioned>

<If no churn and activity is routine:>
"Connection activity appears normal and consistent with routine
infrastructure management."

------------------------------------------
5. Routing Protocol & BGP Health
------------------------------------------
INCLUDE THIS SECTION ONLY if routing protocol or BGP session events were
observed in this window. If no such events exist, skip this entire section
including its heading.

<If this section is included:>
<For each routing session with any transitions, write a plain English block:>

  Connection <uuid-first-8> / Routing Protocol <rp-uuid-first-8>
  <If neighbor IP available:> Neighbor: <neighbor-ip>

  <Choose the appropriate narrative based on Step 4a classification:>

  If session is flapping (4+ oscillations):
  "This BGP session changed state <N> times over <duration>, alternating
  repeatedly between Connect and Idle. This pattern — known as session
  flapping — indicates the session is struggling to stay established.
  The session was last seen in an Idle (down) state, meaning it may still
  be down. This is worth investigating promptly."

  If transient instability (2-3 oscillations) but recovered:
  "This BGP session experienced <N> state changes but recovered and was
  last observed in a Connected (up) state. No sustained downtime was
  detected. Worth keeping an eye on over the next reporting window."

  If single routine transition:
  "This routing protocol session recorded a single state change during
  the window. This is consistent with normal operational activity and
  requires no action."

------------------------------------------
6. Events That Need Your Attention
------------------------------------------
INCLUDE THIS SECTION ONLY if there are WARN or higher severity events to
report. If no WARN/CRIT events were observed, skip this entire section
including its heading.

<If this section is included, list up to 10 WARN/CRIT events. For each,
write a plain English one-liner — not a raw event type string:>
[WARN] <time (UTC)> - <humanized description of what happened>
   Asset   : <asset-type> <uuid-first-8>
   Detail  : <data.message if available, otherwise a plain English description>
   Severity: <severitytext>

------------------------------------------
7. What You Should Do
------------------------------------------
<Write 1-3 plain English, asset-specific recommendations based only on what
was actually detected. If nothing needs action, say so clearly.>

If BGP flapping detected and session is still down:
-> Your BGP session on connection <uuid-first-8> (neighbor <neighbor-ip>)
   appears to still be down. We recommend checking the BGP configuration on
   your edge device — specifically keepalive timers, MD5 authentication
   settings, and interface reachability to the neighbor address.

If BGP flapping but session has since recovered:
-> Your BGP session on connection <uuid-first-8> flapped during this window
   but has since recovered. No immediate action is needed, but keep an eye
   on this session over the next 24 hours to confirm it remains stable.

If provisioning churn detected:
-> Several assets show repeated provisioning activity. If this was part of
   a planned migration or deployment, no action is needed. If it was
   unexpected, review your automation workflows or recent deployment scripts
   for this project.

If all clear:
-> No action required. Your project infrastructure appears healthy and
   stable during this reporting window.

==========================================
```
### Step 6 — Send the Report
Use the `send_email_notification` tool to send the composed report to the `recipient_email_address`.

- Pass the full report text composed in Step 5 as the `pdfContent` parameter. The tool will automatically generate and attach a PDF version of the report.
- Use a brief one-paragraph summary of the overall status and headline finding as the `body` parameter (the email body visible without opening the attachment).
- Set `pdfTitle` to:
  ```
  Fabric Cloud Event Insight Report - <project_uuid first 8 chars> - <reporting period date> - <Overall Status label>
  ```

## Available Tools
This skill can use the following tools:

*   **`search_cloud_events`**: Searches for Equinix Fabric cloud events using advanced filtering and pagination. Use `/equinixproject` `=` combined with `/time` `>=` and `/time` `<=` to scope the search to the target project and time window.
*   **`send_email_notification`**: Sends an email notification given an email address and email body. Pass `pdfTitle` and `pdfContent` (as a plain text string — the tool handles PDF generation internally) to automatically generate and attach a PDF version of the report to the email.

## Guidelines
*   **Plain English Always**: Every sentence in the report must be readable by a non-technical customer. Avoid raw event type strings, API jargon, and numeric scoring in the output. Translate technical signals into business-relevant language.
*   **Insight Over Data**: Do not report raw counts as the primary finding. Derive meaning from patterns — a BGP session that changed state 6 times is not "6 events", it is a flapping session. A router with 7 provisioning transitions is not "7 events", it is showing unusual churn.
*   **Signal Over Noise**: Always separate WARN/CRIT operational events from INFO-level administrative events. Never let service token expirations or system heartbeats inflate the health assessment.
*   **Final State Always**: For any asset with multiple transitions, always determine and report its final observed state. The customer needs to know whether the issue is ongoing or has resolved itself.
*   **Skip Empty Sections**: Sections 2 through 6 must be omitted entirely — heading and all — if there is nothing to report for that section. Do not write placeholder text such as "No events were recorded" or "Nothing to report" inside a section. If a section has no content, it does not appear in the output.
*   **Conciseness**: The email body must be scannable in under two minutes. Use the structured format in Step 5 exactly. No raw JSON. No full UUIDs.
*   **Error Handling**: If no events are found, send the email with a clear "No activity detected" message. If the search API fails, log the error and stop without sending.
*   **Token Efficiency**: Summarize all event data in-memory. Do not pass raw event payloads into downstream tool calls.

## Configuration
*   **`project_uuid`**: < A project UUID > - Required - User should specify a project UUID.
*   **`recipient_email_address`**: < An email address > - Required - User should specify a recipient email address to receive the report.
*   **`from_timestamp`**: < An ISO 8601 timestamp > - Optional - User may specify a from timestamp for the start of the reporting period. Defaults to 24 hours before the current UTC time if not provided.
*   **`to_timestamp`**: < An ISO 8601 timestamp > - Optional - User may specify a to timestamp for the end of the reporting period. Defaults to the current UTC time if not provided.
