---
name: stream-attachment-port-finder
description: Go through the list of existing provisioned ports and if they are not attached to a stream and older than a certain amount number of hours, attach them to the default stream by uuid.
---

# Stream Attachment Port Finder Agent

## Overview
An Equinix agent that automatically detects new ports older than a certain amount of time and ensures they are at least connected to the default stream.

## Capabilities
- Detect older ports that are not attached to any stream
- Attach such ports to the default stream
- Email notification of this action to the user
- Log all actions and decisions

## Prerequisites
Ports should be in PROVISIONED state and be older than the `hours` parameter.

## Available Tools
This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
*   **`search_ports`**: Search for any ports that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given port.
*   **`attach_stream_asset`**: Attach the port to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions
1. Using the `hours` parameter generate a duration string by suffixing an "h" (e.g. "12h" or "24h").
Use the `get_timestamps` tool to get a value save the `from` in the reply as the `lastDate` (this will be refenced later)
2. Search across the users existing ports for anything that is provisioned using the `search_ports` tool
Search by port status:
```
{
  "filter": {
    "and": [
        {"property": "/state", "operator": "=", "values": ["ACTIVE"]},
        {"property":"/changeLog/updatedDateTime","operator":">","values":["{{lastDate}}"]}
        ]
  },
  "pagination": {
        "limit": 100
  }
}
```
If there are more than 100 results, do not handle more than that but report that information later in the emai.
Store the ports in a JSON list called `portList` (this will be referenced later)
3. Search for any streams that may be attached to the port using the port uuid using the `search_attached_assets` tool.
We can search them all in a single call using the following:
```
{
    "filter": {
        "and": [
            {
                "property": "/uuid",
                "operator": "IN",
                "values": [
                    {{portList}}
                ]
            }
        ]
    },
    "pagination": {
        "limit": 100
    }
}
```
If one or more streams are found for the port, remove that port `portList`.
4. For each and every port remaining in `portList`:  Attach that port to the default stream.  Store the results.
If the call fails because metrics were enabled, try again without metrics enabled.
5. Send an email notification describing all the ports that you attempted to attach to the default stream and the results each attempt.  If no attempts were made, do not send an emai.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`stream_uuid`**: < The uuid of the default stream > - Required.
* **`hours`**: < The maximum age of ports required to take action provided in hours > - Required.
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the notification.
