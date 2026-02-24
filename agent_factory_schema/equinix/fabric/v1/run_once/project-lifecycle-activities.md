# Project Lifecycle Activities Insight agent

## Overview
This definition sets up and activates an Equinix agent that analyzes Fabric Cloud Events to generate a one-time cloud event intelligence report across assets including organizations, projects, Fabric Cloud Routers, ports, and connections.
The agent searches for all cloud events within a given project over a user-specified time range, distills the most important operational insights, and delivers a concise audit summary via email notification.
This agent can only run once.

## Prerequisites
A valid Equinix Fabric project UUID must be available. The project must have cloud events enabled and assets (connections, ports, routers, service tokens, etc.) attached to it.

## Capabilities
- Search cloud events across all asset types within a project for a user-specified time range
- Identify and categorize significant lifecycle events (creations, deletions, state changes, configuration updates)
- Detect asset churn and operational anomalies
- Generate a concise audit and operational insight report summarizing key event activity
- Send the intelligence report as an email notification to the designated recipient
- Log all actions and decisions

## Follow the action step by step below:
1. Accept the user-provided time range: use `from` and `to` timestamps as supplied. If no time range is provided, default `from` to 24 hours before the current UTC time and `to` to the current UTC time, both in ISO 8601 format.
2. Search for all cloud events for the given project UUID using the `search_cloud_events` tool. Use `/equinixproject` with operator `=` and the project UUID as the filter, combined with a `/time` `>=` filter for the `from` timestamp and a `/time` `<=` filter for the `to` timestamp. Set pagination limit to 100.
3. If the result set contains more pages (i.e., total events exceed the limit), repeat the search with incremented offsets until all events have been retrieved or a maximum of 500 events have been collected.
4. From the collected events, extract and summarize only the most important information:
   - **Total event count** for the period.
   - **Event breakdown by category**: count of configuration changes (attribute events), state/status changes, creations, and deletions.
   - **Top assets modified**: list the top 5 assets (by subject UUID) with the highest number of events, including the asset type (connection, port, router, service token, etc.) and number of events.
   - **Notable lifecycle events**: highlight any critical or warning severity events (`severitynumber` >= 13), expired tokens, BGP session failures, connection state changes, and router state changes.
   - **Top authenticated users**: list the top 3 `authid` values (excluding `"equinix"` system user unless no users exist) along with their event counts and a short description of actions performed.
   - **Event type distribution**: list the top 5 most frequent event type patterns observed.
   - Discard raw event payloads, duplicate events, and low-signal INFO-level system heartbeat events to keep the summary concise.
5. Compose the intelligence report in the following format:

   ```
   Fabric CloudEvent Intelligence Report – <date of the reporting period>

   Project: <project UUID>
   Period:  <from> to <to> (UTC)

   Total Events: <N>

   Event Breakdown:
   - Config Changes (attribute events): <N>
   - State/Status Changes:             <N>
   - Creations:                         <N>
   - Deletions:                         <N>
   - Other:                             <N>

   Top Assets Modified:
   - <asset-type> <asset-uuid-short> (<N> events)
   - ...

   Notable Events:
   - <event-type>: <brief description> (severity: <severitytext>, time: <time>)
   - ...

   Top Users:
   - <authid> (<N> events – <short action summary>)
   - ...

   Top Event Types:
   - <event-type-pattern>: <N> occurrences
   - ...
   ```

6. Send the composed report as an email notification to the designated recipient email address using the `send_email_notification` tool.

## Available Tools
This skill can use the following tools:

*   **`search_cloud_events`**: Searches for Equinix Fabric cloud events using advanced filtering and pagination. Supports filtering by `/equinixproject`, `/time`, `/type`, and `/subject`. Use `AND` combinations with `/equinixproject` `=` and `/time` `>=` / `<=` operators to scope events to the target project and time window.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If no events are found for the project in the given time window, include that information in the report body and still send the email. If the search fails, log the error and stop.
*   **Token Efficiency**: Only call the tools when all necessary information is present. Do not load unnecessary context. Summarize event data in memory rather than passing raw payloads downstream.
*   **Report Conciseness**: The final email body must be a human-readable summary only — do not include raw JSON event data. Focus on the most operationally significant insights as described in step 4.

## Configuration
* project_uuid: < project uuid > - Required - User must specify a project UUID
* recipient_email_address: < email address > - Required - User must specify a recipient email address to receive the report
* from_timestamp: < ISO 8601 timestamp > - Optional - User may specify a `from` timestamp to define the start of the reporting period. Defaults to 24 hours before the current UTC time if not provided.
* to_timestamp: < ISO 8601 timestamp > - Optional - User may specify a `to` timestamp to define the end of the reporting period. Defaults to the current UTC time if not provided.
