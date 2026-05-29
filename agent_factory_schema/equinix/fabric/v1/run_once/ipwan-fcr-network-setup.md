---
name: ipwan-fcr-network-setup
description: Creates a Network, Fabric Cloud Routers (FCRs), and FCR2IPWAN connections to link regions or deploy globally, attaches all resources to a stream, and notifies on completion.
---

# IPWAN & FCR Network Setup Agent

## Overview
An Equinix agent that provisions a complete IPWAN-based network topology by creating a Network, one or more Fabric Cloud Routers (FCRs) at user-specified metro locations, and FCR2IPWAN connections to link each FCR to the network. When multiple metros are specified the topology spans regions; a single metro results in a regional deployment. After all resources reach PROVISIONED state the agent attaches them to a stream (creating one if needed) and sends a completion summary via email.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Create a Fabric Network of type IPWAN scoped to a project
- Create one FCR per specified metro location with a configurable package
- Create FCR2IPWAN connections between each FCR and the network
- Poll all resources until they reach PROVISIONED state before proceeding
- Create a stream automatically if no stream UUID is provided, then attach every provisioned resource to it
- Send an email completion report summarizing all created resources and their states

## Prerequisites
- A valid Equinix Fabric project UUID must be available.
- The project must have sufficient quota for the number of FCRs and connections requested.
- All target metro locations must be valid Equinix Fabric metro codes.

## Available Tools
This skill can use the following tools:

- **`create_network`**: Creates a Fabric Network. Accepts name, type (`IPWAN`), scope (`REGIONAL` or `GLOBAL`), location (metro code), and project UUID.
- **`search_networks`**: Searches for existing Fabric Networks by filter.
- **`create_router`**: Creates a Fabric Cloud Router. Accepts name, location (metro code), package, notifications, and project UUID.
- **`search_routers`**: Searches for existing Fabric Cloud Routers by filter to check provisioning state.
- **`create_connection`**: Creates a connection. Used to create FCR2IPWAN connections between an FCR and a Network.
- **`search_connections`**: Searches for existing connections to verify provisioning state.
- **`get_stream_details`**: Fetches stream details given a stream UUID.
- **`create_stream`**: Creates a new stream given a name and project UUID.
- **`attach_stream_asset`**: Attaches a resource (network, router, or connection) to a stream by UUID.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Inputs
1a. Confirm that `metros` contains at least one valid metro code. Stop and report an error if the list is empty or missing.

1b. Determine topology scope:
- 1 metro → `REGIONAL`
- 2 or more metros → `GLOBAL`

1c. Apply naming defaults if the optional name fields are not provided:
- `network_name` → `ipwan-network`
- `fcr_name_prefix` → `fcr`
- `stream_name` → `ipwan-stream`

1d. Apply numeric defaults if not provided:
- `bandwidth_in_mbps` → `1000`
- `fcr_package` → `STANDARD`

### Step 2 — Create the Network
2a. Call `create_network` with:
- `name`: `network_name`
- `type`: `IPWAN`
- `scope`: scope determined in Step 1b
- `location.metroCode`: first metro in `metros` list
- `project.projectId`: `project_uuid` (if provided)

2b. Record the returned network UUID as `network_uuid`. Stop if creation fails.

### Step 3 — Create Fabric Cloud Routers
For **each** metro in `metros`, create one FCR:

3a. Call `create_router` with:
- `name`: `<fcr_name_prefix>-<metro_code>` (e.g., `fcr-sv` for metro `sv`)
- `location.metroCode`: current metro
- `package.code`: `fcr_package`
- `project.projectId`: `project_uuid` (if provided)

3b. Record each returned router UUID in a list `fcr_uuids`. Stop if any creation fails.

### Step 4 — Wait for FCRs to Provision
4a. Repeat up to 30 times or until all FCRs are PROVISIONED:
- Call `wait` for 15000 milliseconds.
- For each UUID in `fcr_uuids`, call `search_routers` filtering by UUID and check `state`.
- Break early once all report `state` = `PROVISIONED`.

4b. If any FCR has not reached PROVISIONED after 30 retries, stop and report a timeout error identifying which FCR(s) failed.

### Step 5 — Create FCR2IPWAN Connections
For each UUID in `fcr_uuids`, create one FCR2IPWAN connection:

5a. Call `create_connection` with:
- `name`: `conn-<fcr_metro_code>-ipwan`
- `type`: `FCR2IPWAN`
- `bandwidth`: `bandwidth_in_mbps`
- `aSide.accessPoint.type`: `CLOUD_ROUTER`
- `aSide.accessPoint.router.uuid`: current FCR UUID
- `zSide.accessPoint.type`: `NETWORK`
- `zSide.accessPoint.network.uuid`: `network_uuid`
- `project.projectId`: `project_uuid` (if provided)

5b. Record each returned connection UUID in a list `connection_uuids`. Stop if any creation fails.

### Step 6 — Wait for Connections to Provision
6a. Repeat up to 30 times or until all connections are PROVISIONED:
- Call `wait` for 15000 milliseconds.
- For each UUID in `connection_uuids`, call `search_connections` filtering by UUID and check `state`.
- Break early once all report `state` = `PROVISIONED`.

6b. If any connection has not reached PROVISIONED after 30 retries, stop and report a timeout error identifying which connection(s) failed.

### Step 7 — Set Up Stream
7a. If `stream_uuid` is provided, call `get_stream_details` to verify the stream exists. Stop if it does not.

7b. If `stream_uuid` is not provided, call `create_stream` with:
- `name`: `stream_name`
- `project.projectId`: `project_uuid` (if provided)

Record the returned UUID as `stream_uuid`.

7c. Attach all resources to the stream in order:
1. Call `attach_stream_asset` with the `network_uuid`.
2. For each UUID in `fcr_uuids`, call `attach_stream_asset`.
3. For each UUID in `connection_uuids`, call `attach_stream_asset`.

Wait 3000 milliseconds after each attachment to allow the platform to register the asset.

### Step 8 — Send Completion Notification
8a. Compose the completion report in memory using the structure below.

```
<div class="header">
    <h1>IPWAN & FCR Network Setup — Completion Report</h1>
</div>

<div class="section">
    <h2>Summary</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Network</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>Type</li>
                <li>Scope</li>
                <li>State</li>
            </ul>
            <!-- Data Row -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>Fabric Cloud Routers</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>Metro</li>
                <li>Package</li>
                <li>State</li>
            </ul>
            <!-- Data Rows (one per FCR) -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>FCR2IPWAN Connections</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>FCR UUID</li>
                <li>Bandwidth (Mbps)</li>
                <li>State</li>
            </ul>
            <!-- Data Rows (one per connection) -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>Stream Attachment</h2>
    <div class="content">
    </div>
</div>

<div class="section">
    <h2>Next Steps</h2>
    <div class="content">
    </div>
</div>
```

Section content rules:
- **Summary**: State topology scope (REGIONAL or GLOBAL), total metros, total FCRs, total connections, and overall outcome in 3–5 sentences.
- **Network**: One row — name, UUID, type (`IPWAN`), scope, and final state.
- **Fabric Cloud Routers**: One row per FCR — name, UUID, metro, package, and final state.
- **FCR2IPWAN Connections**: One row per connection — name, UUID, the FCR UUID it links, bandwidth, and final state.
- **Stream Attachment**: Confirm all resources were successfully attached to stream UUID. State whether the stream was newly created or pre-existing.
- **Next Steps**: 1–3 plain-English recommendations (e.g., configure BGP routing protocols on the FCRs, set up alert rules on the connections, validate end-to-end connectivity with a PING command).

8b. Call `send_email_notification` with:
- `pdfContent`: the full report from Step 8a.
- `body`: one-paragraph summary of what was created and the final topology state.
- `pdfTitle`: `FabricIPWAN_<network_uuid>_Setup_Complete`
- `recipients`: `recipient_email_addresses`

## Guidelines
- **Prioritize Clarity**: Confirm all required parameters are present before making any tool call.
- **Error Handling**: If any creation or provisioning step fails, stop immediately and report the failing resource UUID and error detail. Do not proceed to stream attachment or notification.
- **Polling discipline**: Always wait between state polls. Never skip the wait step even if a resource appears fast to provision.
- **Name length**: Keep all generated names to 24 characters or fewer for platform compatibility.
- **Token Efficiency**: Carry only UUIDs and state values forward between steps — do not pass full resource payloads downstream.
- **Plain English**: Report section text must use plain English with no raw API jargon.

## Configuration
- **`metros`**: `["<metro_code>", ...]` — Required. List of Equinix metro codes where FCRs will be created (e.g., `["SV", "DC", "AM"]`). One FCR is created per metro. Two or more metros trigger a GLOBAL scope network.
- **`project_uuid`**: `<UUID>` — Optional. Scopes all created resources to the specified Equinix Fabric project.
- **`fcr_package`**: `<package_code>` — Optional. FCR package tier (default: `STANDARD`).
- **`bandwidth_in_mbps`**: `<number>` — Optional. Bandwidth for each FCR2IPWAN connection in Mbps (default: `1000`).
- **`network_name`**: `<name>` — Optional. Name for the created Network (default: `ipwan-network`; max 24 characters).
- **`fcr_name_prefix`**: `<prefix>` — Optional. Prefix for FCR names; metro code is appended automatically (default: `fcr`; total name max 24 characters).
- **`stream_uuid`**: `<UUID>` — Optional. UUID of an existing stream to attach resources to. If omitted, a new stream is created.
- **`stream_name`**: `<name>` — Optional. Name for the new stream when no `stream_uuid` is provided (default: `ipwan-stream`; max 24 characters).
- **`recipient_email_addresses`**: `["<email>", ...]` — Required. List of email addresses to receive the completion report.
