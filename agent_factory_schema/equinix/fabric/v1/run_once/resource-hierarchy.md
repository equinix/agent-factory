# Cloud Router resource hierarchy agent

## Overview
This definition sets up and activates an Equinix agent that list the FCR related resource hierarchy in a project. 
List all FCRs in a project and the FCR connections and route filters which are associated with each FCR.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically list the FCR related resource hierarchy in a project.
- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.

## Prerequisites
Fabric Cloud router resources exist in the given project.

## Available Tools
This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`search_connection`**: Searches for an existing fabric cloud router connection.
*   **`search_route_filter`**: Searches for an existing route filter.

## Follow the action step by step below:
1. Search for the existing fabric cloud router given the project uuid. Stop if the router is not found.
2. Once the router details are retrieved, search for the existing fabric cloud router connection given the fcr uuid.
3. Once the fabric cloud router connection details are retrieved, search for the associated route filters given the fcr connection uuid.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`project_uuid`**: < A project UUID > - Required - User should specify a project uuid.
