---
name: port-packet-drop-alert
description: Notifies a user when a port packet drop alert is raised.
categories: ["Monitor & Report Agents"]
---

# Port Packet Drop Alert Agent

## Overview
An Equinix agent that monitors Fabric port packet drop counts and notifies a user when a packet drop alert is raised on a port.
This agent only executes once per event.

## Prerequisites
To receive alerts from your ports, you must first set up alert rules in a stream.
If you don't have one yet, start by creating a stream, attach your port resources to it, and then configure alert rules for those resources.

## Capabilities
- Monitor real-time network event streams for port packet drop counts
- Detect and validate packet drop alert rules raised on a port
- Resolve the affected port's details (name, metro, account)
- Send notifications for critical packet drop alerts

## Available Tools
This skill can use the following tools:

*   **`search_ports`**: Searches for an existing port.
*   **`get_stream_alert_rule_details`**: Searches for an existing alert rule.
*   **`send_email_notification`**: Sends an email.

## Instructions
1. Upon receiving the cloud event, validate the equinixalert attribute. Continue if equinixalert value is raise. Stop if equinixalert value is clear.
2. Parse the cloud event message to extract the packet drop alert rule.
3. Using the alert rule UUID obtained from the event, call `get_stream_alert_rule_details` to look up the alert rule and confirm it exists.
4. Locate the affected port using the subject port UUID provided in the cloud event message, via `search_ports`.
5. Compare the port UUID and metric against the values in `## Configuration`. If they don't match what this agent was configured to watch, stop and do not notify.
6. Send a notification via `send_email_notification` to `recipient_email_addresses`. Follow the email rules below:
   - `subject`: `Packet drop alert: {port name} {metric name} above threshold`
   - `body`: one paragraph containing the port name, metro, metric name, and the alert rule name and description.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **No Fabrication**: Never fabricate values. If `get_stream_alert_rule_details` or `search_ports` fails, report the failure instead of guessing.
*   **No Internal Identifiers in Notifications**: Never include hrefs, tokens, or internal UUIDs in the notification body — use human-readable names only.

## Configuration
* **`port_uuid`**: < port UUID > - Required - The UUID of the port to watch.
* **`metric`**: < packets_dropped_rx.count | packets_dropped_tx.count | both > - Optional - Defaults to both.
* **`recipient_email_addresses`**: < list of email addresses > - Required - Recipients for the alert notification.
