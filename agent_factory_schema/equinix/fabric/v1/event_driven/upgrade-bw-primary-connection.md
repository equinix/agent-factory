---
name: upgrade-bw-primary-connection
description: Automatically upgrades the bandwidth of a connection when usage reaches a certain threshold.
---

# Network Bandwidth monitoring and upgrade agent

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
* **`update_connection`**: Update connection. Used to upgrade bandwidth.
* **`get_next_available_bandwidth_tier`**: Fetches the next available billing tier based on a bandwidth input.

## Instructions
1. When a cloud event is received, validate the equinixalert attribute. 
2. Stop if equinixalert value is clear.
3. Stop if severitytext is WARN.
4. Check whether target_connection_uuids is provided in Configuration. If yes, check whether the connection UUID is in the target_connection_uuids list. If the connection UUID is found in the list, continue. Otherwise, stop and mark the agent activity as completed. If target_connection_uuids is not provided, continue.
5. Parse the cloud event message to identify the alert rule.
6. Using the alert rule UUID extracted from the event, check whether a corresponding alert rule already exists.
7. Locate the associated connection using the subject connection UUID provided in the cloud event message.
8. Obtain the current bandwidth from the connection details. Check whether user entered "bandwith_in_mb" in Configuration. If yes, use this bandwidth value. Otherwise, determine the next available bandwidth tier based on the current bandwidth value.
9. Upgrade the connection to the newly determined bandwidth tier.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`target_connection_uuids`**: < list of connection UUIDs > - Optional - User can specify a list of connection uuids.
* **`bandwidth_in_mb`**: < bandwidth in MB > - Optional - User can specify a certain bandwidth in MB.
