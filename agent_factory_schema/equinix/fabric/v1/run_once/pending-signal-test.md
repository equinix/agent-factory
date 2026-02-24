# Alert Rule Manager

## Overview
An Equinix agent that fetches a connection.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Fetches a connection an send details to email.
- Log all actions and decisions

## Prerequisites
Resources should be in PROVISIONING or PROVISIONED state to be eligible for alert setup.

## Available Tools
This skill can use the following tools:

* **`search_connection`**: Searches for an existing connection.

## Follow the action step by step below:
Main Instructions
1. Search for the existing connection given the connection uuid. Stop if the router is not found.
2. Check if state is in PROVISIONED state. Otherwise, stop and return pending signal.
3. Send an email with the connection details to the provided email address.

Instructions when connection event is received.
1. When a cloud event is received, return success if the event mentions the router is in PROVISIONED state. Otherwise, return pending signal.
2. Search for the existing connection given the connection uuid.
3. Send an email with the connection details to the provided email address.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Name guidelines** Limit names to 15 characters when creating routers to ensure compatibility.

## Configuration
* **`connection_uuid`**: < A connection UUID > - Required - User should specify a connection uuid.
* **`emails`**: < list of valid email addresses to send notification to > - Optional - User may specify an email address.
