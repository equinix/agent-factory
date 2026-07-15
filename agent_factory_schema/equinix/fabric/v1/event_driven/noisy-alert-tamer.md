---
name: noisy-alert-tamer
description: Detect overly-active threshold alert rules and email the customer a recommendation to retune the thresholds, reducing alert fatigue.
---

# Noisy Alert Rule Tamer

## Overview
An Equinix agent that monitors threshold-based alert cloud events and detects when a single `alertRule` is firing too often. When an alert rule is found to be overly-active, the agent emails the customer a professional recommendation to raise the rule's warning and critical thresholds above the value that keeps breaching, reducing alert fatigue. This agent is advisory only — it does not modify any alert rule.

## Capabilities
- Monitor event-driven alert cloud events
- Recognize suppressible patterns (the same alert rule being raised too often)
- Retrieve full alert rule details from the API
- Email the customer a professional threshold-retuning recommendation
- Log all actions and decisions

## Prerequisites
To receive alerts, the customer must first set up alert rules in a stream and have cloud events enabled on the project. If they don't have one yet, start by creating a stream, attaching resources to it, and configuring alert rules for those resources.

## Available Tools
This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"4d"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Call this to obtain the reporting window.
*   **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` and `/equinixalert` `=` together with `/time` `BETWEEN` to scope by project, alert, and time window.
*   **`service_get_stream_alert_rules`**: Fetches the full details of an alert rule given the alert rule href/uuid.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions
1. Upon receiving the cloud event, validate the `equinixalert` attribute. Continue if the `equinixalert` value is a `raise` (e.g. `raise/62gzx8/Kn8EUdm3F04VMGA`). Stop if the `equinixalert` value is a `clear` (e.g. `clear/62gzx8/Kn8EUdm3F04VMGA`).
2. Parse the cloud event message to extract the alert rule details (`name`, `uuid`, `href`). If there is no `alertRule` present, then stop.
3. Call the `get_timestamps` tool with a `duration` parameter of `4d` (4 days). Save the returned `from` and `to` (ISO 8601 UTC) as the reporting window — use them with the `BETWEEN` operator on `/time` for the `search_cloud_events` call in Step 4.
4. Extract the `equinixalert` and the `equinixproject` attributes from the cloud event. Use the `search_cloud_events` tool to get alert cloud events matching the same `equinixproject` + `equinixalert` from the last 4 days, scoping `/time` with the `BETWEEN` operator using the `from` and `to` from Step 3. Example API request:

```json
{
    "filter": {
        "and": [
            {
                "property": "/equinixproject",
                "operator": "=",
                "values": [
                    "188572000188973"
                ]
            },
            {
                "property": "/equinixalert",
                "operator": "=",
                "values": [
                    "raise/62gzx8/Kn8EUdm3F04VMGA"
                ]
            },
            {
                "property": "/time",
                "operator": "BETWEEN",
                "values": [
                    "2026-06-01T22:30:00.000Z",
                    "2026-07-28T22:40:00.000Z"
                ]
            }
        ]
    },
    "pagination": {
        "offset": 0,
        "limit": 1000
    }
}
```

Each matching event carries the value that breached the threshold at `data.metrics[].datapoints.value` (with `data.metrics[].unit` and `data.metrics[].datapoints.endDateTime`). Example response:

```json
{
    "pagination": {
        "offset": 0,
        "limit": 1000,
        "total": 1
    },
    "data": [
        {
            "specversion": "1.0",
            "source": "https://uatapi.equinix.com/fabric/v4/cloudevents",
            "id": "7c065589-26db-45f1-ab1d-ec9c26dce69e",
            "time": "2026-07-01T12:20:31.000Z",
            "type": "equinix.fabric.metro.am_so.latency",
            "subject": "/fabric/v4/metros/AM",
            "dataschema": "https://equinix.github.io/equinix-cloudevents/jsonschema/equinix/fabric/v1/MetricAlert.json",
            "datacontenttype": "application/json",
            "severitynumber": "13",
            "severitytext": "WARN",
            "equinixalert": "raise/62gzx8/Kn8EUdm3F04VMGA",
            "equinixproject": "188572000188973",
            "data": {
                "metrics": [
                    {
                        "type": "GAUGE",
                        "name": "equinix.fabric.metro.am_so.latency",
                        "unit": "ms",
                        "datapoints": {
                            "endDateTime": "2026-07-01T12:20:00.000Z",
                            "value": 53.9
                        }
                    }
                ],
                "message": "Abnormal detected for metro latency from Amsterdam to Sofia",
                "alertRule": {
                    "href": "https://uatapi.equinix.com/fabric/v4/streams/d2d173ae-7952-4f9a-addb-fb78f2da5730/alertRules/43738878-9e55-4be9-975f-60a641c9d475",
                    "type": "METRIC_ALERT",
                    "name": "test - AM",
                    "uuid": "43738878-9e55-4be9-975f-60a641c9d475",
                    "detectionMethod": {
                        "type": "OUTLIER"
                    }
                },
                "resource": {
                    "href": "https://uatapi.equinix.com/fabric/v4/metros/AM",
                    "code": "AM",
                    "type": "XF_METRO"
                }
            }
        }
    ]
}
```

5. Determine if this alert is overly-active: count the alert cloud events returned in Step 4 (`pagination.total`, or the length of `data`). If there are **fewer than 4** in the 4-day window, there is no need to send an email — stop here. If there are **4 or more**, continue. Retain the total count and the most recent breaching `data.metrics[].datapoints.value` (with its `unit` and `endDateTime`).
6. Take the alert rule `href` obtained from the event and use `service_get_stream_alert_rules` to get the full details of the alert rule from the API (`name`, `uuid`, `href`, `metricName`, `operand`, `warningThreshold`, `criticalThreshold`, `windowSize`, `resourceSelector`). Example response:

```json
{
    "href": "https://uatapi.equinix.com/fabric/v4/streams/0dd6eab9-ad77-40a2-bb16-c25101d8cf2c/alertRules/baa79611-fd16-401d-b7fa-b061cbff667e",
    "uuid": "baa79611-fd16-401d-b7fa-b061cbff667e",
    "type": "METRIC_ALERT",
    "name": "Metro alert test 1",
    "description": "Metro alert test 1",
    "state": "ACTIVE",
    "enabled": true,
    "resourceSelector": {
        "include": [
            "*/metros/DA"
        ]
    },
    "changeLog": {
        "createdBy": "amcrh008visionmanager",
        "createdDateTime": "2026-07-15T20:46:01.713724Z"
    },
    "metricName": "equinix.fabric.metro.da_dx.latency",
    "windowSize": "PT5M",
    "operand": "ABOVE",
    "warningThreshold": "209",
    "criticalThreshold": "210"
}
```

7. Send an email to `recipient_email_addresses` using `send_email_notification` with a professional plain-text body. The body must include:
   - The alert rule `name`, `uuid`, and `href`.
   - The data point value that triggered the alert (from `data.metrics[].datapoints.value`, with its `unit` and `endDateTime`).
   - The number of times this alert was raised in the 4-day window (the count from Step 5).
   - The current `warningThreshold` and `criticalThreshold`.
   - A recommendation to adjust the warning and critical thresholds above the data point value that triggered the alert, to reduce noise and alert fatigue.
   - A note that this message is advisory only — no changes have been made to the alert rule.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the cloud event before making the tool call.
*   **Error Handling**: If parameters are invalid or an API operation fails, log the error and stop the process without sending an email.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Plain English**: Write the email in plain English — no raw event-type strings or API jargon. Always reference the alert rule using its human-readable name and full UUID.
*   **Advisory Only**: This agent never modifies an alert rule; it only recommends threshold adjustments.

## Configuration
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the recommendation email.
