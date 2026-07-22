---
name: connection-upgrade-bw-secondary
description: Monitors Equinix Fabric connections and maintains bandwidth parity between redundant connection pairs.
---

# Connection Bandwidth Monitoring and Upgrade Redundant Connection Agent

## Overview
This automated agent monitors Equinix Fabric connections and maintains bandwidth parity between redundant connection pairs. 
When bandwidth utilization on a primary connection reaches a configured threshold, the agent automatically upgrades the secondary connection to match the primary connection's bandwidth, ensuring consistent performance across the redundant pair.
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

## Instructions
1. When a cloud event is received, validate the equinixalert attribute.
2. Stop if equinixalert value is clear.
3. Stop if severitytext is WARN.
4. Check whether target_connection_uuids is provided in Configuration. If yes, check whether the connection UUID is in the target_connection_uuids list. If the connection UUID is found in the list, continue. Otherwise, stop and mark the agent activity as completed. If target_connection_uuids is not provided, continue.
5. Parse the cloud event message to identify the alert rule.
6. Using the alert rule UUID extracted from the event, check whether a corresponding alert rule already exists.
7. Locate the associated primary connection using the subject connection UUID provided in the cloud event message.
8. Locate the secondary connection by filtering priority as SECONDARY and redundant_group as the redundant_group of the primary connection. If connection is not found, Stop.
9. Obtain the bandwidth to be used for upgrading. If the user provided a `bandwidth_in_mb` value in Configuration, use it directly. Otherwise, use the current primary connection bandwidth value.
10. Upgrade the secondary connection to the newly determined bandwidth tier.
11. Search for the connection again to confirm the bandwidth now matches the newly selected value. Success criteria: the secondary connection's bandwidth equals the newly selected value and no errors were logged during the process.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`target_connection_uuids`**: < list of connection UUIDs > - Optional - User can specify a list of connection uuids.
* **`bandwidth_in_mb`**: < bandwidth in MB > - Optional - User can specify a certain bandwidth in MB.
