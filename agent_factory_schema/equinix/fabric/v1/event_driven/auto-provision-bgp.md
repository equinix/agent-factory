---
name: auto-provision-bgp
description: Event-driven agent that detects new connections without a routing protocol then creates a standard BGP routing protocol and sends completion notifications.
---

# Automatic BGP bootstrap on new connection agent

## Overview
An Equinix event-driven agent that identifies newly created connections lacking routing protocol configuration, creates a standard BGP routing protocol (ASN, BFD enabled, MD5 authentication), and sends a completion notification with final execution outcome.
This agent only executes once.

## Capabilities
- Detect new or updated connections missing routing protocol configuration
- Create a baseline BGP routing protocol with required defaults
- Enable BFD as part of the standard BGP profile
- Configure MD5 authentication for BGP sessions
- Send completion notifications with success/failure outcomes

## Prerequisites
- A BGP baseline policy must be defined, including ASN standards, BFD expectations, and MD5 key management.  
- The target connection should be in `PENDING` state.
- The target connection's name should contain 'test-lyc'.
- The target connection endpoint must support BGP and permit routing updates.  
- The agent execution context must have permission to read connection details, create routing protocols, and send notifications.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Retrieves connection details.
* **`list_routing_protocols`**: Retrieves existing routing protocols for a connection.
* **`create_routing_protocol`**: Creates a routing protocol for the target connection.
* **`send_email_notification`**: Sends an email notification.

## Instructions

### Step 1 - Validate Event Applicability
1a. On receipt of a cloud event, extract the target `connection_uuid` from the event payload.  
1b. Confirm the event corresponds to a newly created or updated connection that is eligible for routing protocol configuration.  
1c. If the event does not contain a valid `connection_uuid`, stop and report an error.  
1d. If the event is not applicable to BGP bootstrap activity, stop without making changes.

### Step 2 - Retrieve Connection State
Call `search_connections` with `connection_uuid` and pagination (`offset: 0, limit: 1`) to retrieve the current state of the target connection.

2a. If the connection is found, continue to Step 3.  
2b. If the connection cannot be found or retrieved, stop and report an error.

### Step 3 - Check Existing Routing Protocols
Call `list_routing_protocols` with `connection_uuid` to retrieve existing routing protocols.

3a. If no routing protocols are found, continue to Step 4.  
3b. If routing protocols exist and none have `type = BGP`, continue to Step 4.  
3c. If one or more routing protocols already have `type = BGP`, stop without making changes.

### Step 4 - Build `create_routing_protocol` Request Payload (DIRECT and BGP)
Construct `routing_protocol_request` for `create_routing_protocol` by configuring DIRECT and BGP.

4a. For DIRECT body, set fields:
- `type`: `DIRECT`
- `directIpv4.equinixIfaceIp`: from `directIpv4_equinixIfaceIp`
- `directIpv6.equinixIfaceIp`: from `directIpv6_equinixIfaceIp`

4b. For DIRECT, validate before submission:
- Required: `type`.
- At least one address family must be configured: `directIpv4.equinixIfaceIp` or `directIpv6.equinixIfaceIp`.
- If validation fails, stop and report an error.

4c. For BGP body, set top-level fields:
- `type`: `BGP`
- `customerAsn`: from `customer_asn`
- `equinixAsn`: from `equinix_asn`
- `bgpAuthKey`: from `bgp_auth_key`
- `asOverrideEnabled`: from `as_override_enabled` (default `false`)

4d. For BGP body, set BFD fields:
- `bfd.enabled`: from `bfd_enabled` (default `true`)
- `bfd.interval`: from `bfd_interval` (default `100`)

4e. For BGP body, build `bgpIpv4` when `bgp_ipv4_customer_peer_ip` is provided:
- `customerPeerIp`: from `bgp_ipv4_customer_peer_ip`
- `enabled`: from `bgp_ipv4_enabled` (default `true`)
- `outboundASPrependCount`: from `bgp_ipv4_outbound_as_prepend_count` (optional)
- `inboundMED`: from `bgp_ipv4_inbound_med` (optional)
- `outboundMED`: from `bgp_ipv4_outbound_med` (optional)
- `routesMax`: from `bgp_ipv4_routes_max` (optional)

4f. For BGP body, build `bgpIpv6` when `bgp_ipv6_customer_peer_ip` is provided:
- `customerPeerIp`: from `bgp_ipv6_customer_peer_ip`
- `enabled`: from `bgp_ipv6_enabled` (default `true`)
- `outboundASPrependCount`: from `bgp_ipv6_outbound_as_prepend_count` (optional)
- `inboundMED`: from `bgp_ipv6_inbound_med` (optional)
- `outboundMED`: from `bgp_ipv6_outbound_med` (optional)
- `routesMax`: from `bgp_ipv6_routes_max` (optional)

4g. For BGP, validate before submission:
- Required: `type`, `customerAsn`, `equinixAsn`, `bgpAuthKey`, `bfd.enabled`, `bfd.interval`.
- At least one address family must be configured: `bgpIpv4` or `bgpIpv6`.
- If validation fails, stop and report an error.

### Step 5 - Create Routing Protocol
Call `create_routing_protocol` with:
- `connection_uuid`: target connection UUID
- `routing_protocol_request`: payload built in Step 4

5a. If the tool call fails, stop and report an error with failure details.  
5b. If successful, record returned routing protocol UUID as `routing_protocol_uuid`.

### Step 6 - Wait for Routing Protocol Provisioning
6a. Repeat up to 10 times or until the target routing protocol state is `PROVISIONED`:
- Wait for 15000 milliseconds.
- Call `list_routing_protocols` with `connection_uuid`.
- Filter by `routing_protocol_uuid` and check `state`.
- Break early once the target routing protocol reports `state = PROVISIONED`.

6b. If the routing protocol does not reach `PROVISIONED` after 10 retries, stop and report a timeout error.
6c. If attachment reaches `ATTACHED`, continue to Step 7.

### Step 7 - Send Completion Notification
7a. Compose `pdfContent` in memory.

```
<div class="header">
    <h1>Routing Protocol Auto Provisioner - Completion Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Routing Protocol and BGP Status</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Execution Checks and Retries</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>What You Should Do</h2>
    <div class="content">
    </div>
</div>
```

Section content rules for `pdfContent`:
- **Summary**: State `connection_uuid`, `routing_protocol_uuid` (if created), and overall execution outcome (`SUCCESS`, `PARTIAL_SUCCESS`, or `FAILURE`). In 2-4 sentences, summarize what was attempted and whether provisioning completed.
- **Routing Protocol and BGP Status**: Include final routing protocol state and key BGP configuration applied: `customerAsn`, `equinixAsn`, BFD (`enabled`, `interval`), and configured address families (`bgpIpv4`, `bgpIpv6`).
- **Execution Checks and Retries**: Include polling behavior and outcome: provisioning retry count used, and whether timeout thresholds were reached.
- **What You Should Do**: Provide 1-3 operational next actions based on final outcome. If outcome is `SUCCESS`, end with: "BGP auto provisioning completed successfully and no further action is required at this time."

7b. Call `send_email_notification` with:
- `pdfContent`: completion summary from Step 7a.
- `body`: one-paragraph operational summary of execution result (`SUCCESS`, `PARTIAL_SUCCESS`, or `FAILURE`) and any required follow-up action.
- `pdfTitle`: `AutoProvisionBGP_<connection_uuid>_<execution_result>`
- `recipients`: `recipient_email_addresses`

## Guidelines
* **Prioritize Clarity**: Confirm all required parameters are present before each tool call.
* **Input Validation**: Validate event fields and configuration values before mutating operations.
* **Non-Destructive Behavior**: Do not overwrite existing valid BGP configuration.
* **Sensitive Data Handling**: Never log plaintext MD5 authentication values.
* **Error Handling**: If a tool call fails or timeout is reached, stop and report explicit failure context.
* **Failure Visibility**: Include actionable remediation details in completion notifications for non-success outcomes.

## Configuration
* **`connection_uuid`**: <connection UUID> - Required - Target connection ID from event payload.
* **`directIpv4_equinixIfaceIp`**: <IPv4 string> - Optional - Maps to `directIpv4.equinixIfaceIp`.
* **`directIpv6_equinixIfaceIp`**: <IPv6 string> - Optional - Maps to `directIpv6.equinixIfaceIp`.
* **`customer_asn`**: <integer ASN> - Required - Maps to `customerAsn`.
* **`equinix_asn`**: <integer ASN> - Required - Maps to `equinixAsn`.
* **`bgp_auth_key`**: <secret reference> - Required - Secret reference used to resolve `bgpAuthKey` in the BGP payload.
* **`as_override_enabled`**: <true|false> - Optional - Maps to `asOverrideEnabled`; default `false`.
* **`bfd_enabled`**: <true|false> - Optional - Maps to `bfd.enabled`; default `true`.
* **`bfd_interval`**: <integer> - Optional - Maps to `bfd.interval`; default `100`.
* **`bgp_ipv4_customer_peer_ip`**: <IPv4 string> - Optional - Maps to `bgpIpv4.customerPeerIp`.
* **`bgp_ipv4_enabled`**: <true|false> - Optional - Maps to `bgpIpv4.enabled`; default `true`.
* **`bgp_ipv4_outbound_as_prepend_count`**: <integer> - Optional - Maps to `bgpIpv4.outboundASPrependCount`.
* **`bgp_ipv4_inbound_med`**: <integer> - Optional - Maps to `bgpIpv4.inboundMED`.
* **`bgp_ipv4_outbound_med`**: <integer> - Optional - Maps to `bgpIpv4.outboundMED`.
* **`bgp_ipv4_routes_max`**: <integer> - Optional - Maps to `bgpIpv4.routesMax`.
* **`bgp_ipv6_customer_peer_ip`**: <IPv6 string> - Optional - Maps to `bgpIpv6.customerPeerIp`.
* **`bgp_ipv6_enabled`**: <true|false> - Optional - Maps to `bgpIpv6.enabled`; default `true`.
* **`bgp_ipv6_outbound_as_prepend_count`**: <integer> - Optional - Maps to `bgpIpv6.outboundASPrependCount`.
* **`bgp_ipv6_inbound_med`**: <integer> - Optional - Maps to `bgpIpv6.inboundMED`.
* **`bgp_ipv6_outbound_med`**: <integer> - Optional - Maps to `bgpIpv6.outboundMED`.
* **`bgp_ipv6_routes_max`**: <integer> - Optional - Maps to `bgpIpv6.routesMax`.
* **`recipient_email_addresses`**: <list of email addresses> - Required - Recipients for completion notification.