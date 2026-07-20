---
name: bgp-health-monitor
description: Monitors BGP session state and automatically recovers from session flaps via graceful restart, peer reset, or failover to a secondary path.
---

# BGP Health Monitor Agent

## Overview
An Equinix agent that monitors BGP session health and automatically responds to session flaps by attempting graceful restart, then peer reset, then failover to a secondary path if recovery fails. Sends an incident summary and decision log on completion.

## Capabilities
- Monitor BGP session state changes in real time
- Detect session flaps and instability
- Automatically attempt graceful restart on flap detection
- Fall back to peer reset if graceful restart fails
- Trigger failover to a secondary path if peer reset is also unsuccessful
- Send incident context and decision log via email

## Prerequisites
BGP sessions must be pre-configured and attached to an active Equinix Fabric connection.

## Available Tools
This skill can use the following tools:

*   **`get_bgp_session`**: Retrieves the current state and details of a BGP session by UUID.
*   **`restart_bgp_session`**: Initiates a graceful restart for a BGP session.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Instructions

1. Upon receiving the cloud event, check the BGP session status.

2. If the session state is not ESTABLISHED, attempt a graceful restart using `restart_bgp_session`.

3. Check the BGP session again after the restart.

4. If the session is still not ESTABLISHED, do a peer reset and wait.

5. If the peer reset works, continue monitoring. If not, trigger failover to the secondary path.

6. Send an email with the incident details.

## Guidelines
*   **Error Handling**: If any operation fails, log the error and proceed to the next step.
*   **Token Efficiency**: Only call tools when all parameters are known.
*   **Logging**: Always log every action taken and the reason for it.

## Configuration
* **`bgp_session_uuid`**: < BGP session UUID > - Required - The UUID of the primary BGP session to monitor.
* **`recipient_email_addresses`**: < list of email addresses > - Required - Email recipients for incident notifications.
* **`secondary_path_uuid`**: < connection UUID > - Optional - UUID of the secondary path to fail over to.
