---
execution_mode: graph
graph_pattern: dag
name: attach-unstreamed-routers-graph
description: Finds provisioned routers older than a given number of hours that are not attached to any stream, and attaches them to the default stream.
---

# Attach Unstreamed Routers to Default Stream

## Overview
An Equinix agent that reviews existing routers, finds any older than a specified number of hours
that are not yet attached to a stream, and attaches them to the default stream. This agent runs
once immediately by default unless scheduled by user.

## Capabilities
- Find routers older than a specified age that are not attached to any stream
- Attach such routers to the default stream
- Email notification of the action taken
- Log all actions and decisions

## Prerequisites
Routers should be in PROVISIONED state and older than the `hours` parameter.

## Available Tools
This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Always call this in Step 1 to obtain the reporting window.
*   **`search_routers`**: Search for any routers that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given router.
*   **`attach_stream_asset`**: Attach the router to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions
1. Using the `hours` parameter generate a duration string by suffixing an "h" (e.g. "12h" or "24h").
Use the `get_timestamps` tool to get a value save the `from` in the reply as the `lastDate` (this will be refenced later)
2. Search across the users existing routers for anything that is provisioned using the `search_routers` tool
Search by router status:
```
{
  "filter": {
    "and": [
        {"property": "/state", "operator": "=", "values": ["PROVISIONED"]},
        {"property":"/changeLog/updatedDateTime","operator":">","values":["{{lastDate}}"]}
        ]
  },
  "pagination": {
        "limit": 100
  }
}
```
If there are more than 100 results, do not handle more than that but report that information later in the emai.
Store the routers in a JSON list called `routerList` (this will be referenced later)
3. Search for any streams that may be attached to the router using the router uuid using the `search_attached_assets` tool.
We can search them all in a single call using the following:
```
{
    "filter": {
        "and": [
            {
                "property": "/uuid",
                "operator": "IN",
                "values": [
                    {{routerList}}
                ]
            }
        ]
    },
    "pagination": {
        "limit": 100
    }
}
```
If one or more streams are found for the router, remove that router `routerList`.
4. For each and every router remaining in `routerList`:  Attach that router to the default stream without metrics enabled.  Store the results.
5. Send an email notification describing all the routers that you attempted to attach to the default stream and the results each attempt.  If no attempts were made, do not send an emai.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`stream_uuid`**: < The uuid of the default stream > - Required.
* **`hours`**: < The maximum age of routers required to take action provided in hours > - Required.
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the notification.
