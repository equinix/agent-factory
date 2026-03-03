# Cloud Router upgrade package agent

## Overview
This definition sets up and activates an Equinix agent that upgrades the package of a Fabric Cloud Router. 
When the route usage exceeds a predefined threshold, the agent automatically upgrades the Fabric Cloud Router package to ensure sufficient capacity and uninterrupted operation.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically upgrade Fabric Cloud Router packages as needed to ensure adequate capacity and prevent service disruption.
- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.

## Prerequisites
Fabric Cloud router should be in PROVISIONED state to be eligible for bandwidth upgrade.

## Available Tools
This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`get_next_available_router_package `**: Fetches the next available Fabric Cloud Router package based on a package input.
*   **`update_router`**: Update router. Used to upgrade the fabric cloud router.

## Instructions
1. Search for the existing fabric cloud router given the router uuid. Stop if the router is not found.
2. Once the router details are retrieved, determine the current package assigned to the router and identify the next available package tier based on that package.
3. Finally, upgrade the Fabric Cloud Router to the newly selected package tier to accommodate the increased route usage.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`router_uuid`**: < A router UUID > - Required - User should specify a router uuid.
