---
name: cloud-router-bgp-route-mismatch-report
description: Reads the routes a Fabric Cloud Router advertises to, receives from, and holds in its route table for a BGP connection, flags routes that are missing or not installed, and emails a diagnostic report on likely filtering or BGP configuration issues.
categories: ["Monitor & Report Agents"]
---

# Cloud Router BGP Route Mismatch Report Agent

## Overview
An Equinix agent that detects route mismatches on a connection whose A-side is a Fabric Cloud Router (FCR) with a BGP routing protocol. A mismatch typically indicates route filtering or a BGP configuration issue.
The agent needs no prefix lists from the user. It retrieves the FCR's active route table, the routes the FCR receives from the BGP peer, and the routes the FCR advertises to the BGP peer, all from the Fabric API, and compares them with each other. It cross-checks the BGP routing protocol configuration and attached route filters, classifies each mismatch as a likely filtering issue or a likely BGP configuration issue, and emails one diagnostic report with recommended next actions.
The agent sees the FCR's view only. It cannot see the peer router's own route table, so a prefix the FCR advertises is reported as advertised, not as confirmed received by the peer. A prefix that the peer never announced and the FCR never learned cannot be detected without an expected list.
This agent is diagnostic only. It never modifies a connection, routing protocol, route filter, or route aggregation; recommendations are for the network operator to action manually.
This agent runs once when started, unless the user provides a schedule.

## Capabilities
- Resolve the target connection and its A-side Fabric Cloud Router
- Retrieve the FCR route table and the routes the FCR advertises to and receives from the peer, per IP family
- Identify routes in the FCR route table that are not advertised to the peer
- Identify routes received from the peer that are not installed in the FCR route table
- Read the BGP routing protocol configuration (session state, address-family enablement, peer IP and ASN) to explain each mismatch
- Classify each mismatch as a likely filtering issue or a likely BGP configuration issue, with the supporting evidence
- Recommend a concrete next action for the operator for every mismatch
- Email a report as a PDF
- Log all actions and decisions

## Prerequisites
The target connection must be provisioned (`state` is `ACTIVE` and `operation.equinixStatus` is `PROVISIONED`), have a Fabric Cloud Router (FCR) as the A-side, and have a BGP routing protocol configured.
Only a connection UUID and recipient email addresses are required. The BGP session should be established; if the session is not established, the agent reports the session state as the likely cause rather than comparing route sets.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Finds a connection by UUID and resolves its name, `state`, `operation.equinixStatus`, `aSide.accessPoint.type`, and the A-side router UUID at `aSide.accessPoint.router.uuid`.
* **`list_routing_protocols`**: Fetches routing protocols for a connection; used to read BGP `customerPeerIp`, `customerAsn`, and for each address family (`bgpIpv4`, `bgpIpv6`) the `enabled` flag and `operation.operationalStatus`.
* **`search_routes`**: Searches the routing table of a Fabric Cloud Router. Requires `router_uuid`. `route_type` is `active` for the FCR route table (no `connection_uuid` needed), `advertised` for routes sent to the peer, and `received` for routes learned from the peer; `advertised` and `received` also require `connection_uuid`. Filter on `/type` with `=` and the value `IPv4_BGP_ROUTE` or `IPv6_BGP_ROUTE` to select BGP routes of an IP family. Each returned route exposes a `prefix` field (the CIDR entry).
* **`search_route_filter_attachments_for_fcr`**: Lists route filters attached to the router; used to detect filters that may explain mismatches. Takes `fcr_uuid` (the router UUID), not `router_uuid`.
* **`get_email_template`**: Get email template.
* **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Instructions
1. Confirm the inputs. `connection_uuid` and `recipient_email_addresses` are required. If either is missing, stop and report which input is missing. Do not guess or fabricate a UUID or an email address.
2. Call `search_connections` for `connection_uuid` with `limit` 1. Confirm the connection is provisioned, meaning `state` is `ACTIVE` and `operation.equinixStatus` is `PROVISIONED` (both must hold; `state` alone is never `PROVISIONED`). Confirm `aSide.accessPoint.type` is `CLOUD_ROUTER`, and record `aSide.accessPoint.router.uuid` as `router_uuid`. If the connection cannot be found or its A-side is not a Fabric Cloud Router, stop and report this.
3. Call `list_routing_protocols` for the connection with `limit` 20 and locate the BGP routing protocol. Record the peer IP, the peer ASN, and for each of `bgpIpv4` and `bgpIpv6` whether it is enabled and its `operation.operationalStatus`. The routing protocol `state` of `PROVISIONED` only means the configuration is applied; it does not mean the session is up. A session is established only when `operationalStatus` is `UP`. `UNKNOWN`, `DOWN`, or a missing value means not established.
   - If no BGP routing protocol exists, stop and report "no BGP routing protocol".
   - If no enabled address family has `operationalStatus` `UP`, stop the route comparison and report "BGP session not established" as the likely cause of missing routes, with the observed `operationalStatus` for each address family.
   - Compare only the address families that are enabled and `UP`.
4. For each address family to compare, retrieve three route sets with `search_routes`, passing `router_uuid` and a `/type` filter of `IPv4_BGP_ROUTE` for `bgpIpv4` or `IPv6_BGP_ROUTE` for `bgpIpv6`:
   - **Advertised**: `route_type` = `advertised`, with `connection_uuid`.
   - **Received**: `route_type` = `received`, with `connection_uuid`.
   - **Active**: `route_type` = `active`, without `connection_uuid`, filtered to the same `/type`.
   Use `pagination` `offset` = 0, `limit` = 20 and page through additional offsets until all routes are collected. Collect the `prefix` of each route.
5. Compute the mismatches per address family:
   - **Received but not installed**: prefixes in the received set that are absent from the active set. The FCR learned them from the peer but did not install them.
   - **Not advertised**: prefixes in the active set that are absent from the advertised set, excluding prefixes that are in the received set (a route is not sent back to the peer it came from). These are routes the FCR holds that it does not send to this peer.
   Compare prefixes exactly as returned. Do not compute differences by reasoning about CIDR containment, and do not treat an aggregate and its more-specific routes as mismatched.
6. For each address family that has a mismatch, gather supporting evidence and classify it:
   - Call `search_route_filter_attachments_for_fcr` with `fcr_uuid` = `router_uuid`. For **received but not installed**, an attached inbound filter makes it **likely filtering**; for **not advertised**, an attached outbound filter makes it **likely filtering**. If a filter is attached but its direction is not reported, still classify as **likely filtering** and say the direction could not be confirmed. Name the attached filter.
   - For **received but not installed** with no attached filter, classify as **likely BGP configuration** (for example, a better path from another source or an invalid next hop) and state what could not be verified.
   - For **not advertised** with no attached filter, classify as **likely BGP configuration** (for example, outbound policy or aggregation on the FCR side) and state what could not be verified.
   - If no determination can be made, classify as **undetermined** and say so. Never present a classification as certain.
7. Retrieve the email template with `get_email_template`.
8. Compose `pdfContent` in memory, structured using the email template from step 7:
   - **Header**: **BGP Route Mismatch Report**
   - **Summary**: connection UUID and name, router UUID, BGP peer IP and ASN, session state per address family, route counts (advertised, received, active) per address family, and the number of mismatches found per address family.
   - **Mismatches**: for each address family, list the received-but-not-installed prefixes and the not-advertised prefixes, the classification (likely filtering / likely BGP configuration / undetermined), the evidence, and the recommended next action. If none, state "No route mismatches detected."
   - **Not verifiable**: state that receipt of advertised prefixes by the peer cannot be confirmed from the FCR, and that prefixes the peer never announced cannot be detected.
9. Send the report with `send_email_notification`:
   - `pdfContent`: the report from step 8.
   - `body`: a one-paragraph summary stating the connection, how many mismatches were found, and the most common classification.
   - `pdfTitle`: `BGP_Route_Mismatch_Report`
   - `recipients`: `recipient_email_addresses`
   If the BGP session was not established, send the report stating that cause. If no mismatches were found and `send_email_on_clean_run` is not `true`, do not send an email; report the clean result in the run log instead.

## Guidelines
* **Read-only**: Never modify a connection, routing protocol, route filter, route aggregation, or router. Recommendations are advisory only.
* **No User-Supplied Routes**: Take every route from the Fabric API. Never ask the user for prefixes and never fabricate one.
* **Exact Comparison**: Report prefixes exactly as returned by `search_routes`. Do not normalize, aggregate, or fabricate prefixes.
* **FCR View Only**: Describe results as what the FCR advertises, receives, and holds. Never claim the peer did or did not receive a prefix.
* **Honest Classification**: Label every classification as "likely" and list the evidence. Use "undetermined" when evidence is insufficient.
* **Pagination**: Paginate `search_routes` until all results are collected before comparing.
* **Error Handling**: If parameters are invalid or any operation fails, log the error and stop the process.
* **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified before making a tool call. Never fabricate a router or connection UUID.
* **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading. In the report, list at most 50 prefixes per category and state the total count when truncated.

## Configuration
* **`connection_uuid`**: < A connection UUID > - Required - The connection, with a Fabric Cloud Router as the A-side, whose BGP routes are checked.
* **`recipient_email_addresses`**: < list of email addresses > - Required - Recipients for the report.
* **`send_email_on_clean_run`**: < boolean > - Optional - Send the report even when no mismatches are found; default `false`.
