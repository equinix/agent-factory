---
name: ping-fcr-and-notify
description: Initiates a PING command on a Fabric Cloud Router.
---

# Ping FCR agent

## Overview
An Equinix agent that initiates a PING command on a Fabric Cloud Router in order to perform a network connectivity check.
Once the PING operation is completed, the resulting output is collected and used to generate an email notification.
The email is then sent to the specified recipient, ensuring that the results of the connectivity test are communicated clearly and promptly.
This agent runs once immediately by default unless scheduled by user.

## Prerequisites
Fabric Cloud Router and Connections associated with it should be in PROVISIONED state to be eligible for ping command.

## Capabilities
- PING command on Fabric Cloud Router
- Email notification with PING results
- Log all actions and decisions

## Instructions
1. Start by fetching details of the router given the uuid. Stop if router does not exist.
2. Search for the existing connection given the connection uuid. Verify if the aside router uuid of the connection matches the router uuid from the first step. Stop if they do not match.
3. Then initiate a PING command on the Fabric Cloud Router to test network connectivity to verify that the specified destination is reachable. Use the project of the router as the input project of the ping command.
4. After the PING operation completes, capture the results of the command, including any success or failure details. Use the connection uuid provided as the source connection uuid for the PING command.
5. Wait for 10000 milliseconds to ensure the PING command has sufficient time to complete before attempting to retrieve the results.
6. Search for the PING command using the router uuid. Limit the result to 1. 
7. If the response from the search command is in pending state, wait for another 10000 milliseconds.
8. Search again for the PING command using the router uuid. Limit the result to 1.
9. Next, send an email notification to the designated email address, using the outcome of the search router command as the email body so the recipient is clearly informed of the connectivity status and any relevant diagnostic information.

## Available Tools
This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`search_connection`**: Searches for an existing connection.
*   **`create_router_commands`**: Initiate a PING command on a Fabric Cloud Router by UUID.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_router_commands`**: Search for commands (e.g., PING) on a Fabric Cloud Router.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`router_uuid`**: < A router UUID > - Required - User should specify a router uuid.
* **`connection_uuid`**: < A connection UUID > - Required - User should specify a connection uuid.
* **`source_ip_address`**: < A valid ip address > - Required - User should specify a destination IP address to ping.
