---
name: pre-flight-validator
description: Automatically check to see if a newly provisioned connection is attached to a stream and send and email if it is not
---

# Detect connections that are not attached to a stream and notify

## Overview
An Equinix agent that automatically detects new connections are not attached to a stream.

## Capabilities
- Detect connections that are not attached to any stream
- Email notification with the list of available streams
- Log all actions and decisions

## Prerequisites
Connections should be in PROVISIONED state

## Available Tools
This skill can use the following tools:
*   **`search_attached_assets`**: Searches for any streams which may be attached to a given asset.
*   **`list_streams`**: Retrieves a list of existing streams.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

list_streams

## Instructions
1. Once the cloud event is received, see if it is of the type `equinix.fabric.connection.state.provisioned`.  Only proceed further if it is.
2. Search for any streams that may be attached to the connection using the connection uuid.  Only proceed if none are found.
3. Retrieve the list of existing streams.
4. Next, send an email notification to the recipient email addresses, informing the user that the connection is not attached to any stream.  Ask if they would like to attach the connection to an existing stream from the list (include the stream name) or create a new stream.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the notification.
