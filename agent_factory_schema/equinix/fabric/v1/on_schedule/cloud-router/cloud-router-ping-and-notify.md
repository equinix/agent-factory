---
name: cloud-router-ping-and-notify
description: Initiates a PING command on a Fabric Cloud Router.
---

# Cloud Router Ping and Report Agent

## Overview
An Equinix agent that initiates a PING command on a Fabric Cloud Router in order to perform a network connectivity check.
Once the PING operation is completed, the resulting output is collected and used to generate an email notification.
The email is then sent to the specified recipient, ensuring that the results of the connectivity test are communicated clearly and promptly.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- PING command on Fabric Cloud Router
- Email notification with PING results
- Log all actions and decisions

## Prerequisites
Fabric Cloud Router and Connections associated with it should be in PROVISIONED state to be eligible for ping command.

## Instructions
1. Start by fetching details of the router given the uuid. Stop if router does not exist.
2. Search for the existing connection given the connection uuid. Verify if the aside router uuid of the connection matches the router uuid from the first step. Stop if they do not match.
3. Then initiate a PING command on the Fabric Cloud Router to test network connectivity to verify that the specified destination is reachable. Use the project of the router as the input project of the ping command.
4. After the PING operation completes, capture the results of the command, including any success or failure details. Use the connection uuid provided as the source connection uuid for the PING command.
5. Repeat this step 5 times or until the PING command is no longer in pending state.
    - a. Wait for 10000 milliseconds to ensure the PING command has sufficient time to complete before attempting to retrieve the results.
    - b. Search for the PING command using the router uuid. Limit the result to 1.
6. Next, send an email notification to the recipient email addresses, using the outcome of the search router command as the email body so the recipient is clearly informed of the connectivity status and any relevant diagnostic information.

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`search_connections`**: Searches for an existing connection.
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
* **`destination_ip_address`**: < A valid ip address > - Required - User should specify a destination IP address to ping.
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the report.
