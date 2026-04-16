---
name: metro-latency-notify
description: Automatically email a list of connections that are over the metros where latency spike.
---

# Collect connections over metros with latency spikes and notify

## Overview
An Equinix agent that automatically email a list of connections that are over the metros where latency spike.

## Capabilities
- Detect metro latency alerts
- Identify the source and destination metros
- Identify the active connections over the metros
- Email notification with the connections list
- Log all actions and decisions

## Prerequisites
Connections should be in PROVISIONED state

## Available Tools
This skill can use the following tools:
*   **`search_connections`**: Searches for active connections with aside and zside metro codes
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions
1. Once the cloud event is received, look at the metro latency alert, from type extract source and destination metro codes
2. Search for the active connections, using the source metro code as aside and destination metro code as aside
3. Next, send an email notification to the recipient email addresses, using the outcome of the search connection command as the email body so the recipient is clearly informed of the connections list to follow up.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`source_metro_code`**: < A 2 character metro code > - Required - User should specify source metro code.
* **`destination_metro_code`**: < A 2 character metro code > - Required - User should specify destination metro code.
  **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the report.
