---
name: alert-rule-management
description: Sets up an alert rule for a connection.
---

# Alert Rule Manager

## Overview
An Equinix agent that sets up an alert rule for a connection.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically creates an alert rule based on user-defined parameters
- Instantly creates a stream if one does not exist and attaches the resource to it
- Log all actions and decisions

## Prerequisites
Resources should be in PROVISIONED state to be eligible for alert setup.

## Available Tools
This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection.
*   **`get_stream_details`**: Fetches stream details given a stream uuid.
*   **`create_stream`**: Create a stream.
*   **`attach_stream_asset`**: Attach a resource to a stream.
*   **`create_stream_alert_rule`**: Create an alert rule given a stream uuid.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions
1. Search for the existing connection given the connection uuid.
2. Get the stream details given the stream uuid. If stream uuid is not provided, create a new stream.
3. Attach the connection resource to the stream.
4. Wait for 5000 milliseconds to ensure the connection is attached to the stream.
5. Create an alert rule in the stream with the user-defined critical threshold.
6. Next, send an email notification to the designated email address, using the outcome of the alert rule creation tool as the email body.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Name guidelines** Limit names to 15 characters when creating streams and alert rules to ensure compatibility.
*   **Alert Rule guidelines** Default window size to PT15M.

## Configuration
* **`connection_uuid`**: < A connection UUID > - Required - User should specify a connection uuid.
* **`operand`**: < either ABOVE or BELOW > - Required - User should specify an operand.
* **`critical_threshold`**: < list of valid email addresses to send notification to > - Required - User should a critical threshold.
* **`stream_uuid`**: < A stream UUID > - Optional - User can specify a stream uuid.
