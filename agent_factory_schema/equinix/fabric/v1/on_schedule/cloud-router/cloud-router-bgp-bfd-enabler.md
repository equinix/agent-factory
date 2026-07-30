---
name: cloud-router-bgp-bfd-enabler
description: Finds FCR connections whose bandwidth exceeds a configurable threshold (default 1 Gbps) that have a BGP routing protocol and enables BFD on those BGP sessions, then sends a completion report.
categories: ["Deployment & Change Agents"]
---

# Cloud Router BGP BFD Enabler Agent

## Overview
An Equinix agent that scans all provisioned Fabric Cloud Router (FCR) connections whose bandwidth exceeds a configurable threshold (default 1 Gbps), identifies those with an existing BGP routing protocol where BFD is not yet enabled, enables BFD on each qualifying BGP session, and sends a completion email report summarizing all changes made.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Search for all provisioned FCR connections exceeding a configurable bandwidth threshold (default 1 Gbps)
- Inspect each connection's routing protocols and identify BGP sessions with BFD disabled
- Enable BFD on qualifying BGP routing protocols using a configurable interval
- Skip connections where BFD is already enabled or where no BGP routing protocol exists
- Send a completion email report listing updated, skipped, and failed connections

## Prerequisites
- IAM role required: `Fabric Cloud Router Manager` or `Fabric Manager`
- Target connections must be FCR-backed and in `PROVISIONED` state with bandwidth exceeding `min_bandwidth_mbps`
- Each qualifying connection must have at least one BGP routing protocol

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches for provisioned FCR connections filtered by bandwidth.
* **`list_routing_protocols`**: Lists all routing protocols for a given connection.
* **`replace_routing_protocol`**: Replaces a routing protocol configuration; used here to enable BFD on an existing BGP session while preserving all other fields.
* **`wait`**: Waits for a specified number of milliseconds before the next action.
* **`send_email_notification`**: Sends an email notification with an optional PDF report.

## Instructions

### Step 1 — Find Qualifying FCR Connections
Call `search_connections` to retrieve all provisioned FCR connections with bandwidth greater than `min_bandwidth_mbps` (default `1000` Mbps).

- Filter: `/operation/equinixStatus` = `PROVISIONED`, connection type must be FCR-backed (`aSide` device type `CLOUD_ROUTER`), `bandwidth` > `min_bandwidth_mbps`.
- Paginate until all results are collected.
- If no connections are found, skip to Step 4 and report that no qualifying connections were found.

### Step 2 — Inspect Routing Protocols
For each connection from Step 1, call `list_routing_protocols` with the `connection_uuid`.

- Collect all routing protocols with `type` = `BGP`.
- For each BGP routing protocol found:
  - If `bfd.enabled` is already `true`, mark the connection as **skipped** (reason: BFD already enabled).
  - If `bfd.enabled` is `false` or absent, add the connection and routing protocol UUID to the **to-update** list.
- If a connection has no BGP routing protocol, mark it as **skipped** (reason: no BGP routing protocol).

### Step 3 — Enable BFD on Qualifying BGP Routing Protocols
For each BGP routing protocol in the **to-update** list:

3a. Construct the updated BGP payload from the existing routing protocol fields, preserving all current values and setting:
- `bfd.enabled`: `true`
- `bfd.interval`: from `bfd_interval` configuration (default `100`)

3b. Call `replace_routing_protocol` with:
- `connection_uuid`: the connection UUID
- `routing_protocol_uuid`: the BGP routing protocol UUID
- `routing_protocol_request`: the updated payload from 3a

3c. On success, record the connection UUID and routing protocol UUID as **updated**.
3d. On failure, record the connection UUID, routing protocol UUID, and error message as **failed**.
3e. Call `wait` for 2000 milliseconds between each `replace_routing_protocol` call to avoid rate limiting.

A failure on one connection must not stop processing of the remaining connections.

### Step 4 — Send Completion Report
4a. Compose `pdfContent` in memory. When inserting a single line break, use `<br/>` instead of `<br>`.

```
<div class="header">
    <h1>BGP BFD Enabler Completion Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Updated Connections</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Skipped Connections</h2>
    <div class="content">
    </div>
</div>
<div class="section">
    <h2>Failed Updates</h2>
    <div class="content">
    </div>
</div>
```

Section content rules for `pdfContent`:
- **Summary**: Total connections scanned, count updated, count skipped, count failed, and the BFD interval applied.
- **Updated Connections**: For each updated connection, list: connection UUID, BGP routing protocol UUID, and BFD interval set.
- **Skipped Connections**: For each skipped connection, list: connection UUID and reason (BFD already enabled / no BGP routing protocol). If none, state "No connections skipped."
- **Failed Updates**: For each failure, list: connection UUID, routing protocol UUID, and error message. If none, state "No failures."

4b. Call `send_email_notification` with:
- `pdfContent`: the report from 4a.
- `body`: a one-paragraph summary of the operation covering how many connections were scanned, updated, skipped, and failed.
- `pdfTitle`: `BGP_BFD_Enabler_Report`
- `recipients`: `recipient_email_addresses`

## Guidelines
- **Non-Destructive Reads First**: Always read the existing routing protocol before replacing it; preserve all fields not explicitly changed.
- **Idempotency**: Skip connections where BFD is already enabled — do not overwrite an active BFD configuration.
- **Pagination**: Paginate `search_connections` until all results are collected before proceeding to Step 2.
- **Rate Limiting**: Insert a 2-second wait between `replace_routing_protocol` calls.
- **Error Isolation**: A failure on one connection must not stop processing of the remaining connections.
- **Prioritize Clarity**: Report all outcomes — updated, skipped, and failed — in the completion email.

## Configuration
* **`min_bandwidth_mbps`**: <integer> — Optional — Minimum connection bandwidth in Mbps to qualify for BFD enablement; default `1000` (1 Gbps).
* **`bfd_interval`**: <integer> — Optional — BFD detection interval in milliseconds; default `100`.
* **`recipient_email_addresses`**: <list of email addresses> — Required — Recipients for the completion report.
