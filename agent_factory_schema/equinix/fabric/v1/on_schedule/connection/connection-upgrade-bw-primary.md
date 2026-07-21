---
name: connection-upgrade-bw-primary
description: Upgrades the bandwidth of a connection.
---

# Connection Bandwidth Upgrade Agent

## Overview
An Equinix agent that upgrades the bandwidth of a connection.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically upgrade connection bandwidth
- Log all actions and decisions

## Prerequisites
Connections should be in PROVISIONED state to be eligible for bandwidth upgrade.

## Instructions
1. Search for the existing connection given the connection uuid.
2. Obtain the current bandwidth from the connection details. Check whether user entered "bandwith_in_mb" in Configuration. If yes, use this bandwidth value. Otherwise, determine the next available bandwidth tier based on the current bandwidth value.
3. Upgrade the bandwidth of the connection given the new bandwidth.


## Available Tools
This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`connection_uuid`**: < A connection UUID > - Required - User should specify a connection uuid.
* **`bandwith_in_mb`**: < bandwidth in MB > - Optional - User can specify if user wants to upgrade to a certain bandwidth in MB.
