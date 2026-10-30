---
name: cloud-router-bgp-route-mismatch-report
description: Compares the routes a Fabric Cloud Router advertises to and receives from its BGP peer against the expected prefixes, flags gaps that indicate filtering or BGP configuration issues, and emails a diagnostic report.
categories: ["Monitor & Report Agents"]
---

# Cloud Router BGP Route Mismatch Report Agent

## Overview
An Equinix agent that detects routes that are not advertised to, or not received from, the BGP peer of a connection whose A-side is a Fabric Cloud Router (FCR). A gap in either direction typically indicates route filtering or a BGP configuration issue.
The agent reads the FCR's own advertised and received route sets for the connection, compares each against the expected prefixes supplied in configuration, cross-checks the BGP routing protocol configuration and attached route filters, classifies each gap as a likely filtering issue or a likely BGP configuration issue, and emails one diagnostic report with recommended next actions.
The agent sees the FCR's view only. It cannot see the peer router's own route table, so a prefix the FCR advertises is reported as advertised, not as confirmed received by the peer.
This agent is diagnostic only. It never modifies a connection, routing protocol, route filter, or route aggregation; recommendations are for the network operator to action manually.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Resolve the target connection and its A-side Fabric Cloud Router
- Retrieve the routes the FCR advertises to the peer and the routes it receives from the peer, per IP family
- Identify expected prefixes that the FCR does not advertise, and expected prefixes that the FCR does not receive
- Identify received prefixes that were not expected
- Read the BGP routing protocol configuration (state, address-family enablement, peer IP and ASN) to explain each gap
- Classify each gap as a likely filtering issue or a likely BGP configuration issue, with the supporting evidence
- Recommend a concrete next action for the operator for every gap
- Email a report as a PDF
- Log all actions and decisions

## Prerequisites
The target connection must be PROVISIONED, have a Fabric Cloud Router (FCR) as the A-side, and have a BGP routing protocol configured.
A connection UUID and at least one list of expected prefixes are required. The BGP session should be established; if the session is not established, the agent reports the session state as the likely cause rather than comparing route sets.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Finds a connection by UUID and resolves its name, state, and A-side router UUID.
* **`list_routing_protocols`**: Fetches routing protocols for a connection; used to read BGP state, `customerPeerIp`, `customerAsn`, and the `enabled` flag per address family (`bgpIpv4`, `bgpIpv6`).
* **`search_routes`**: Searches the routing table of a Fabric Cloud Router. Requires `router_uuid`. Use `route_type` = `advertised` for routes sent to the peer and `route_type` = `received` for routes learned from the peer; both also require `connection_uuid`. Filter on `/type` with `=` and the value `IPv4_BGP_ROUTE` or `IPv6_BGP_ROUTE` to select an IP family. Each returned route exposes a `prefix` field (the CIDR entry).
* **`search_route_filter_attachments_for_fcr`**: Lists route filters attached to the router; used to detect filters that may explain missing prefixes.
* **`get_email_template`**: Get email template.
* **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Instructions
1. Confirm the inputs. `connection_uuid` is required, and at least one of `expected_advertised_prefixes` or `expected_received_prefixes` is required. If any are missing, ask the user and confirm them before proceeding. Do not guess or fabricate a UUID or a prefix.
2. Call `search_connections` for `connection_uuid`. Confirm the connection is PROVISIONED and that its A-side is a Fabric Cloud Router, and record the A-side router UUID as `router_uuid`. If the connection cannot be found or its A-side is not a Fabric Cloud Router, stop and report this to the user.
3. Call `list_routing_protocols` for the connection and locate the BGP routing protocol. Record the BGP state, the peer IP, the peer ASN, and whether `bgpIpv4` and `bgpIpv6` are enabled.
   - If no BGP routing protocol exists, stop and report "no BGP routing protocol".
   - If the BGP session is not established, stop the route comparison and report "BGP session not established" as the likely cause of missing routes.
4. For each enabled address family, retrieve both route sets with `search_routes`, passing `router_uuid`, `connection_uuid`, and a `/type` filter of `IPv4_BGP_ROUTE` for `bgpIpv4` or `IPv6_BGP_ROUTE` for `bgpIpv6`:
   - once with `route_type` = `advertised`
   - once with `route_type` = `received`
   Use `pagination` `offset` = 0, `limit` = 20 and page through additional offsets until all routes are collected. Collect the `prefix` of each route.
5. Compute the differences per address family:
   - **Not advertised**: prefixes in `expected_advertised_prefixes` that are absent from the advertised set.
   - **Not received**: prefixes in `expected_received_prefixes` that are absent from the received set.
   - **Unexpected received**: prefixes in the received set that are absent from `expected_received_prefixes`, when that list was provided.
   Compare prefixes exactly as returned. Do not compute differences by reasoning about CIDR containment.
6. For each address family that has a gap, gather supporting evidence and classify it:
   - Call `search_route_filter_attachments_for_fcr` for `router_uuid`. If a route filter is attached that applies to the gap's direction (or its direction is not reported), classify the gap as **likely filtering** and name the attached filter.
   - If the address family is disabled (`enabled` = false) in the routing protocol, classify as **likely BGP configuration** (address family disabled).
   - For a not-advertised gap with no attached filter and the address family enabled, classify as **likely BGP configuration** (for example, the prefix is not originated or aggregated on the FCR side) and state what could not be verified.
   - For a not-received gap with no attached filter, classify as **likely BGP configuration on the peer side** (for example, peer not announcing the prefix or peer-side outbound policy) and state that the peer's route table cannot be checked from here.
   - If no determination can be made, classify as **undetermined** and say so. Never present a classification as certain.
7. Retrieve the email template with `get_email_template`.
8. Compose `pdfContent` in memory, structured using the email template from step 7:
   - **Header**: **BGP Route Mismatch Report**
   - **Summary**: connection UUID and name, router UUID, BGP peer IP and ASN, BGP state, and the number of gaps found per address family.
   - **Gaps**: for each address family and direction, list the not-advertised prefixes, not-received prefixes, and unexpected received prefixes, the classification (likely filtering / likely BGP configuration / undetermined), the evidence, and the recommended next action. If none, state "No route mismatches detected."
   - **Not verifiable**: state that receipt of advertised prefixes by the peer cannot be confirmed from the FCR.
9. Send the report with `send_email_notification`:
   - `pdfContent`: the report from step 8.
   - `body`: a one-paragraph summary stating the connection, how many gaps were found, and the most common classification.
   - `pdfTitle`: `BGP_Route_Mismatch_Report`
   - `recipients`: `recipient_email_addresses`
   If no gaps were found and `send_email_on_clean_run` is not `true`, do not send an email; report the clean result in the run log instead.

## Guidelines
* **Read-only**: Never modify a connection, routing protocol, route filter, route aggregation, or router. Recommendations are advisory only.
* **Exact Comparison**: Report prefixes exactly as returned by `search_routes`. Do not normalize, aggregate, or fabricate prefixes.
* **FCR View Only**: Describe results as what the FCR advertises and receives. Never claim the peer did or did not receive a prefix.
* **Honest Classification**: Label every classification as "likely" and list the evidence. Use "undetermined" when evidence is insufficient.
* **Pagination**: Paginate `search_routes` until all results are collected before comparing.
* **Error Handling**: If parameters are invalid or any operation fails, log the error and stop the process.
* **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified before making a tool call. Never fabricate a router or connection UUID.
* **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading. In the report, list at most 50 prefixes per category and state the total count when truncated.

## Configuration
* **`connection_uuid`**: < A connection UUID > - Required - The connection, with a Fabric Cloud Router as the A-side, whose BGP routes are checked.
* **`expected_advertised_prefixes`**: < list of CIDR prefixes > - Optional - Prefixes the FCR is expected to advertise to the peer. At least one of the two expected lists is required.
* **`expected_received_prefixes`**: < list of CIDR prefixes > - Optional - Prefixes the FCR is expected to receive from the peer. At least one of the two expected lists is required.
* **`recipient_email_addresses`**: < list of email addresses > - Required - Recipients for the report.
* **`send_email_on_clean_run`**: < boolean > - Optional - Send the report even when no gaps are found; default `false`.
