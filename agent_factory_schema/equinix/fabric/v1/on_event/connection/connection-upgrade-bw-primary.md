---
name: connection-upgrade-bw-primary
description: Automatically upgrades the bandwidth of a connection when usage reaches a certain threshold.
categories: ["Deploy & Change Agents"]
---

# Connection Bandwidth Monitoring and Upgrade Agent

## Overview
An Equinix agent that automatically upgrades the bandwidth of a connection when usage reaches a certain threshold. 
This agent only executes once.

## Capabilities
- Monitor real-time network event streams
- Detect bandwidth threshold alerts
- Analyze connection utilization patterns
- Automatically upgrade connection bandwidth
- Log all actions and decisions
- Send notifications for critical events

## Prerequisites
To receive alerts from your connections, you must first set up alert rules in a stream.
If you don't have one yet, start by creating a stream, attach your connection resources to it, and then configure alert rules for those resources.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches for an existing connection.
* **`get_stream_alert_rule_details`**: Searches for an existing alert rule.
* **`update_connection`**: Update connection. Used to upgrade bandwidth. Returns success once the change request is accepted (e.g., `APPROVED`) — the connection's actual `bandwidth` value does not update until the platform finishes provisioning the change.
* **`get_next_available_bandwidth_tier`**: Fetches the next available billing tier based on a bandwidth input.
* **`wait`**: Waits for a specified number of milliseconds before the next action.

## Instructions
1. When a cloud event is received, validate the equinixalert attribute. 
2. Stop if equinixalert value is clear.
3. Stop if severitytext is WARN.
4. Check whether target_connection_uuids is provided in Configuration. If yes, check whether the connection UUID is in the target_connection_uuids list. If the connection UUID is found in the list, continue. Otherwise, stop and mark the agent activity as completed. If target_connection_uuids is not provided, continue.
5. Parse the cloud event message to identify the alert rule.
6. Using the alert rule UUID extracted from the event, check whether a corresponding alert rule already exists.
7. Locate the associated connection using the subject connection UUID provided in the cloud event message.
8. Obtain the current bandwidth from the connection details. If the user provided a `bandwidth_in_mb` value in Configuration, use it directly. Otherwise, determine the next available bandwidth tier based on the current bandwidth value. If no higher bandwidth tier is available, log this as a critical event — this serves as the notification for critical events — and stop.
9. Upgrade the connection to the newly determined bandwidth tier by calling `update_connection`. If the call itself fails (e.g., a 4xx/5xx error, such as the once-per-24-hours billing restriction), log the failure with the error details as a critical event and stop. This is a single upgrade request — do not call `update_connection` again for this event, even if verification in Step 10 does not immediately show the new value.
10. Wait for the bandwidth change to take effect, since `update_connection` only confirms the request was accepted — it does not mean the change has finished applying:
    a. Repeat up to 10 times (10 × 30000 ms = 300 seconds / 5 minutes maximum) or until the connection's bandwidth equals the newly selected value:
       - Call `wait` for 30000 milliseconds.
       - Call `search_connections` filtering by the connection UUID, and check the returned `bandwidth` value (and, if present, the embedded change record's `status`).
       - Break early once `bandwidth` equals the newly selected value, or once the change record shows `status: COMPLETED` with the expected value.
    b. If after 10 retries (300 seconds) the bandwidth still does not match the newly selected value, log this as a critical event describing the change as "submitted and accepted but not yet applied after 300 seconds" (include the change UUID and its last known `status`, e.g. `APPROVED`) — this is expected propagation delay, not a call failure, so do not resubmit the upgrade. Success criteria: the connection's bandwidth equals the newly selected value within the retry window and no errors were logged during the process.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Single upgrade attempt**: Call `update_connection` at most once per event. A pending/slow-to-apply change (Step 10) is not grounds for a second upgrade call — only a failed `update_connection` call itself (Step 9) is logged as a critical event.
*   **Polling discipline**: Always wait between state polls in Step 10. Never skip the wait step even if the bandwidth appears to update quickly.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`target_connection_uuids`**: < list of connection UUIDs > - Optional - User can specify a list of connection uuids.
* **`bandwidth_in_mb`**: < bandwidth in MB > - Optional - User can specify a certain bandwidth in MB.
