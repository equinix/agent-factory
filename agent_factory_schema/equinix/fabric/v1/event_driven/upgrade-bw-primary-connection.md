# Network Bandwidth monitoring and upgrade agent

## Overview
An Equinix agent that automatically upgrades the bandwidth of a connection when usage reaches a certain threshold.

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

* **`search_connection`**: Searches for an existing connection.
* **`get_stream_alert_rule_details`**: Searches for an existing alert rule.
* **`update_connection`**: Update connection. Used to upgrade bandwidth.
* **`get_next_available_bandwidth_tier`**: Fetches the next available billing tier based on a bandwidth input.

## Follow the action step by step below:
1. When a cloud event is received, validate the equinixalert attribute. Continue if equinixalert value is raise. Stop if equinixalert value is clear.
2. Parse the cloud event message to identify the alert rule.
3. Using the alert rule UUID extracted from the event, check whether a corresponding alert rule already exists.
4. Locate the associated connection using the subject connection UUID provided in the cloud event message.
5. Obtain the current bandwidth from the connection details, then determine the next available bandwidth tier based on that value.
6. Upgrade the connection to the newly determined bandwidth tier.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`connection_uuids`**: <list of connection UUIDs> - Optional - User can specify a list of connection uuids.
* **`alert_rule_uuids`**: <list of  alert rule UUIDs> - Optional - User can specify a list of alert rule uuids.
* **`bandwith_in_mb`**: <bandwidth in MB> - Optional - User can specify if user wants to upgrade to a certain bandwidth in MB.
* **`maximum_bandwidth`**: <boolean. default is false> - Optional - User can specify if user wants to upgrade to the maximum bandwidth.
