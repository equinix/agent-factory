---
name: alert-rule-management-graph
description: Sets up an alert rule for a connection.
categories: ["Deploy & Change Agents"]
execution_mode: graph
graph_pattern: dag
---

# Alert Rule Manager Agent

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
2. Get the stream details given the stream uuid. If a stream uuid is not provided, create a new stream with specified parameter: stream_name.
3. Attach the connection resource to the stream.
4. Wait for 5000 milliseconds to ensure the connection is attached to the stream.
5. Create an alert rule in the stream with the user-defined parameters: alert_rule_name, operand, critical_threshold, and window_size.
6. Next, send an email notification to the designated email address, using the outcome of the alert rule creation tool as the email body.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Name guidelines** Limit names to 15 characters when creating streams and alert rules to ensure compatibility.
*   **Alert Rule guidelines** Default window size to PT15M.

## Configuration
* **`connection_uuid`**: < A connection UUID > - Required - User should specify a connection uuid.
* **`stream_uuid`**: < A stream UUID > - Optional - User can specify a stream uuid.
* **`stream_name`**: < A stream name between 3 and 24 characters > - Optional - User can specify a stream name or default auto-gen-stream.
* **`alert_rule_name`**: < An alert rule name between 3 and 24 characters > - Optional - User can specify an alert rule name or default auto-gen-alert.
* **`operand`**: < operand must be ABOVE or BELOW > - Required - User should specify an operand.
* **`critical_threshold`**: < numeric value for metric type from alert rule > - Required - User should a critical threshold.
* **`window_size`**: < numeric value for window size from alert rule > - Optional - User should a window size or default is PT15M.
