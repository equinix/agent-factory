---
name: connection-order-status-tracker
description: Monitors a connection's provisioning lifecycle, tracks state transitions, and alerts when provisioning is stuck.
---

# Connection Order Status Tracker Agent

## Overview
An Equinix agent that monitors the provisioning lifecycle of a Fabric connection after it is created.
The agent tracks the connection's state transitions (DRAFT -> PROVISIONING -> PROVISIONED) and alerts the user when the connection appears stuck in a non-terminal state for too long.
This agent only executes once.

## Capabilities
- Monitor connection provisioning state in real time
- Track state transitions across the provisioning lifecycle (DRAFT -> PROVISIONING -> PROVISIONED)
- Detect connections stuck in a non-terminal provisioning state
- Alert the user when provisioning is stuck
- Log all observed states, transitions, and decisions

## Prerequisites
This agent is triggered by a connection creation cloud event. The connection referenced by the event must exist so its provisioning lifecycle can be monitored.
To receive this event, you must first create a stream and attach your connection resource (or its project) to it. Unlike threshold-based agents, no alert rule is required — lifecycle state-change events are delivered automatically once the resource is attached to a stream.

## Available Tools
This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection. Used to read the current provisioning status via `/operation/equinixStatus`.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`send_email_notification`**: Sends an email notification given a list of email addresses and email body.

## Instructions
1. When the connection creation cloud event is received, extract the subject connection UUID from the cloud event message.
2. Search for the connection using the connection UUID as `/uuid`, and read the current provisioning status from `/operation/equinixStatus`. Treat the expected lifecycle progression as DRAFT -> PROVISIONING -> PROVISIONED. Follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/uuid", "operator": "=", "values": ["<connection-uuid>"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 1 }
}
```
3. Record the observed status as the last known status and log it.
4. If the status is terminal, stop monitoring:
   - `PROVISIONED` indicates the connection completed provisioning successfully.
   - `FAILED` or `ERRORED` indicates provisioning failed.
5. If the status is non-terminal (for example `DRAFT` or `PROVISIONING`), `wait` for the configured `poll_interval_seconds`, then search for the connection again and read `/operation/equinixStatus`.
6. Compare the new status to the last known status. If it changed, log the transition and update the last known status.
7. Repeat steps 4 through 6 until the status reaches a terminal state or the total elapsed monitoring time reaches `stuck_threshold_minutes`.
8. If `stuck_threshold_minutes` is reached and the status is still non-terminal, treat the connection as stuck and send an email notification to `recipient_email_addresses`. Follow the email rules below:
- `body`: a one-paragraph, plain-English alert containing the full connection UUID, the last observed status, and how long the connection has been in that state.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the cloud event and configuration before making the tool call.
*   **Plain English**: Plain English, no API jargon, no raw event strings, full UUIDs always.
*   **Track Transitions**: Only log a transition when the observed status differs from the last known status, so the lifecycle history stays clean.
*   **Terminal States**: Stop polling as soon as a terminal state (`PROVISIONED`, `FAILED`, `ERRORED`) is observed. Do not send a stuck alert if the connection reaches a terminal state.
*   **Error Handling**: If any tool call fails, log the error and stop the process. Do not send an email.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`connection_uuids`**: < list of connection UUIDs > - Optional - User can specify a list of connection uuids to scope monitoring. If omitted, the connection is taken from the cloud event subject.
* **`stuck_threshold_minutes`**: < number of minutes > - Optional - Default 30. Maximum time a connection may remain in a non-terminal state before it is considered stuck.
* **`poll_interval_seconds`**: < number of seconds > - Optional - Default 60. Time to wait between status checks.
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the stuck-provisioning alert.
