---
name: default-connection-attachment-to-stream
description: Go through the list of existing provisioned connections and if they are not attached to a stream and older than a certain amount number of hours, attach them to the default stream by uuid.
---

# Detect connections that are not attached to a stream and notify

## Overview
An Equinix agent that automatically detects new connections older than a certain amount of time and ensures they are at least connected to the default stream.

## Capabilities
- Detect older connections that are not attached to any stream
- Attach such connections to the default stream
- Email notification of this action to the user
- Log all actions and decisions

## Prerequisites
Connections should be in PROVISIONED state and be older than the `hours` parameter.

## Available Tools
This skill can use the following tools:
*   **`search_connections`**: Search for any connections that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given connection.
*   **`attach_stream_asset`**: Attach the connection to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions
1. Calculate a last possible date by taking the current time and subtracting the `hours` parameter save this as the `lastDate` (this will be refenced later)
2. Search across the users existing connections for anything that is provisioned using the `search_connections` tool
Search by connection status:
```
{
  "filter": {
    "and": [
        {"property": "/operation/equinixStatus", "operator": "=", "values": ["PROVISIONED"]},
        {"property":"/changeLog/updatedDateTime","operator":"<","values":["{{lastDate}}"]}
        ]
  },
  "pagination": {
        "limit": 100
  }
}
```
If there are more than 100 results, do not handle more than that but report that information later in the emai.
Store the connections in a list.
3. Search for any streams that may be attached to the connection using the connection uuid using the `search_attached_assets` tool.
We can search them all in a single call doing something like the following:
```
{
    "filter": {
        "and": [
            {
                "property": "/uuid",
                "operator": "IN",
                "values": [
                    "d4b78fcb-a8fc-43a7-a4b8-713b97e44dba",
                    "1de93aeb-9c9e-4d93-9d5a-af5efb084b24"
                ]
            }
        ]
    },
    "pagination": {
        "limit": 100
    }
}
```
If one or more streams are found for the connection, remove that connection from the list.
4. For each connection remaining in the list:  Attach that connection to the default stream.  Store the results.
5. Send an email notification describing all the connections that you attempted to attach to the default stream and the results each attempt.  If no attempts were made, do not send an emai.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`stream_uuid`**: < The uuid of the default stream > - Required.
* **`hours`**: < The minimum age of connections required to take action provided in hours > - Required.
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the notification.
