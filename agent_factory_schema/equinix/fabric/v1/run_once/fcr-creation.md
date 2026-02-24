# Alert Rule Manager

## Overview
An Equinix agent that creates a Fabric Cloud Router.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically creates an alert rule based on user-defined parameters
- Instantly creates a stream if one does not exist and attaches the resource to it
- Log all actions and decisions

## Prerequisites
Resources should be in PROVISIONED state to be eligible for alert setup.

## Available Tools
This skill can use the following tools:

*   **`create_router`**: creates a Fabric Cloud Router.

## Follow the action step by step below:
Main Instructions
1. Create a fabric cloud router. Generate a random name for the router with a maximum length of 15 characters.
2. Search for the existing fabric cloud router given the router uuid. Stop if the router is not found.
3. Complete the operation and return success if the state is in PROVISIONED state. Otherwise, return pending.

Instructions when router event is received.
1. When a cloud event is received, return success if the event mentions the router is in PROVISIONED state. Otherwise, return pending.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Name guidelines** Limit names to 15 characters when creating routers to ensure compatibility.

## Configuration
* **`metro_code`**: < A 2 character code > - Required - User should specify a metro code.
* **`account_number`**: < A valid string > - Required - User should specify an account number in string format.
* **`package_code`**: < A valid code > - Optional - Default to BASIC.
* **`email`**: < A valid email address > - Required - User should specify an email.