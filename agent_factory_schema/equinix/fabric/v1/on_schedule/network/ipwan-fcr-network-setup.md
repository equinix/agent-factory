---
name: ipwan-fcr-network-setup
description: Creates one Network, one Cloud Router, and one IPWAN connection between them, attaches all resources to a stream, and notifies on completion.
---

# IPWAN & Cloud Router Network Setup Agent

## Overview
An Equinix agent that provisions a single IPWAN-based network topology with FCR. 
It creates one Network, one Cloud Router at a user-specified metro location, and one IPWAN connection linking the Cloud Router to the network. After all resources reach PROVISIONED state the agent attaches them to a stream (creating one if needed) and sends a completion summary via email.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Create a Fabric Network of type IPWAN scoped to a project
- Create one Cloud Router at the specified metro location with a configurable package
- Create one IPWAN connection between the Cloud Router and the network
- Poll all resources until they reach PROVISIONED state before proceeding
- Create a stream automatically if no stream UUID is provided, then attach every provisioned resource to it
- Send an email completion report summarizing all created resources and their states

## Prerequisites
- A valid Equinix Fabric project UUID must be available.
- The project must have sufficient quota for one Cloud Router and one connection.
- The target metro location must be a valid Equinix Fabric metro code.
- A valid Equinix billing account number must be available to associate with the Cloud Router.

## Available Tools
This skill can use the following tools:

- **`create_network`**: Creates a Fabric Network. Accepts name, type (`IPWAN`), scope (`REGIONAL` or `GLOBAL`), location (metro code), notifications (mandatory), and project UUID.
- **`search_networks`**: Searches for existing Fabric Networks by filter.
- **`create_router`**: Creates a Fabric Cloud Router. Accepts name, location (metro code), package, billing account number, notifications (mandatory), and project UUID.
- **`search_routers`**: Searches for existing Fabric Cloud Routers by filter to check provisioning state.
- **`create_connection`**: Creates a connection. Used to create IPWAN connections between a Cloud Router and a Network. Accepts notifications.
- **`search_connections`**: Searches for existing connections to verify provisioning state.
- **`get_stream_details`**: Fetches stream details given a stream UUID.
- **`create_stream`**: Creates a new stream given a name and project UUID.
- **`attach_stream_asset`**: Attaches a resource (network, router, or connection) to a stream by UUID.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Inputs
1a. Confirm that `metro` is a valid metro code. Stop and report an error if it is empty or missing.

1b. Confirm that `account_number` is provided. Stop and report an error if it is empty or missing.

1c. Apply naming defaults if the optional name fields are not provided:
- `network_name` → `ipwan-network`
- `fcr_name` → `fcr`
- `stream_name` → `ipwan-stream`

1d. Apply numeric defaults if not provided:
- `bandwidth_in_mbps` → `1000`
- `fcr_package` → `STANDARD`

### Step 2 — Create the Network
2a. Call `create_network` with:
- `name`: `network_name`
- `type`: `IPWAN`
- `scope`: `GLOBAL`
- `location.metroCode`: `metro`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid` (if provided)

2b. Record the returned network UUID as `network_uuid`. If creation fails, skip Steps 3–7 and go directly to Step 8 to send a completion email reporting the network creation failure and its error detail.

### Step 3 — Create the Fabric Cloud Router
3a. Call `create_router` with:
- `name`: `fcr_name`
- `location.metroCode`: `metro`
- `package.code`: `fcr_package`
- `account.accountNumber`: `account_number`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid` (if provided)

3b. Record the returned router UUID as `fcr_uuid`. If creation fails, skip Steps 4–7 and go directly to Step 8 to send a completion email reporting the Network as created, the Cloud Router creation failure, and its error detail.

### Step 4 — Wait for the Cloud Router to Provision
4a. Repeat up to 30 times or until the Cloud Router is PROVISIONED:
- Call `wait` for 15000 milliseconds.
- Call `search_routers` filtering by `fcr_uuid` and check `state`.
- Break early once `state` = `PROVISIONED`.

4b. If the Cloud Router has not reached PROVISIONED after 30 retries, skip Steps 5–7 and go directly to Step 8 to send a completion email reporting a timeout error identifying the Cloud Router that failed.

### Step 5 — Create the IPWAN Connection
5a. Call `create_connection` with:
- `name`: `conn-<metro>-ipwan`
- `type`: `IPWAN_VC`
- `bandwidth`: `bandwidth_in_mbps`
- `aSide.accessPoint.type`: `CLOUD_ROUTER`
- `aSide.accessPoint.router.uuid`: `fcr_uuid`
- `zSide.accessPoint.type`: `NETWORK`
- `zSide.accessPoint.network.uuid`: `network_uuid`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid` (if provided)

5b. Record the returned connection UUID as `connection_uuid`. If creation fails, skip Steps 6–7 and go directly to Step 8 to send a completion email reporting the Network and Cloud Router as created, the connection creation failure, and its error detail.

### Step 6 — Wait for the Connection to Provision
6a. Repeat up to 30 times or until the connection is PROVISIONED:
- Call `wait` for 15000 milliseconds.
- Call `search_connections` filtering by `connection_uuid` and check `state`.
- Break early once `state` = `PROVISIONED`.

6b. If the connection has not reached PROVISIONED after 30 retries, skip Step 7 and go directly to Step 8 to send a completion email reporting a timeout error identifying the connection that failed.

### Step 7 — Set Up Stream
7a. If `stream_uuid` is provided, call `get_stream_details` to verify the stream exists. Stop if it does not.

7b. If `stream_uuid` is not provided, call `create_stream` with:
- `name`: `stream_name`
- `project.projectId`: `project_uuid` (if provided)

Record the returned UUID as `stream_uuid`.

7c. Attach all resources to the stream in order:
1. Call `attach_stream_asset` with the `network_uuid` and `"metrics_enabled": false`.
2. Call `attach_stream_asset` with the `fcr_uuid` and `"metrics_enabled": false`.
3. Call `attach_stream_asset` with the `connection_uuid`.

Wait 3000 milliseconds after each attachment to allow the platform to register the asset.

### Step 8 — Send Completion Notification
8a. Compose the completion report in memory using the structure below.

```
<div class="header">
    <h1>IPWAN & Cloud Router Network Setup — Completion Report</h1>
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
    <h2>Fabric Cloud Router</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>Metro</li>
                <li>Package</li>
                <li>State</li>
            </ul>
            <!-- Data Row -->
            <ul class="table-row">
            </ul>
        </div>
    </div>
</div>

<div class="section">
    <h2>IPWAN Connection</h2>
    <div class="content">
        <div class="table-container">
            <ul class="table-row table-header">
                <li>Name</li>
                <li>UUID</li>
                <li>Cloud Router UUID</li>
                <li>Bandwidth (Mbps)</li>
                <li>State</li>
            </ul>
            <!-- Data Row -->
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
- **Summary**: State the metro and overall outcome in 3–5 sentences. If any resource failed to create or provision, name the failing resource, include its error detail, and state that stream attachment was skipped as a result.
- **Network**: One row — name, UUID, type (`IPWAN`), scope (`GLOBAL`), and final state. If the network was never created, state "Not created" and the error detail in place of UUID/state.
- **Fabric Cloud Router**: One row — name, UUID, metro, package, and final state. If the router was never created, state "Not created" and the error detail in place of UUID/state; if creation was skipped because the network failed, state "Skipped — network creation failed".
- **IPWAN Connection**: One row — name, UUID, the Cloud Router UUID it links, bandwidth, and final state. If the connection was never created, state "Not created" and the error detail in place of UUID/state; if creation was skipped because an earlier resource failed, state "Skipped — <resource> creation failed".
- **Stream Attachment**: If all resources were successfully attached to stream UUID, confirm this and state whether the stream was newly created or pre-existing. If stream attachment was skipped due to an earlier failure, state that explicitly.
- **Next Steps**: If the run succeeded, give 1–3 plain-English recommendations (e.g., configure a BGP routing protocol on the Cloud Router, set up an alert rule on the connection, validate end-to-end connectivity with a PING command). If the run failed, recommend remediation for the reported error and re-running the agent.

8b. Call `send_email_notification` with:
- `pdfContent`: the full report from Step 8a.
- `body`: one-paragraph summary of what was created and the final topology state.
- `pdfTitle`: `FabricIPWAN_<network_uuid>_Setup_Complete`
- `recipients`: `recipient_email_addresses`

## Guidelines
- **Prioritize Clarity**: Confirm all required parameters are present before making any tool call.
- **Error Handling**: If any creation or provisioning step fails, do not abort silently. Skip the remaining creation, provisioning, and stream-attachment steps, and go directly to Step 8 to send a completion email reporting the failing resource and its error detail.
- **Polling discipline**: Always wait between state polls. Never skip the wait step even if a resource appears fast to provision.
- **Name length**: Keep all generated names to 24 characters or fewer for platform compatibility.
- **Token Efficiency**: Carry only UUIDs and state values forward between steps — do not pass full resource payloads downstream.
- **Plain English**: Report section text must use plain English with no raw API jargon.

## Configuration
- **`metro`**: `<metro_code>` — Required. Equinix metro code where the Network and Cloud Router will be created (e.g., `SV`).
- **`project_uuid`**: `<UUID>` — Optional. Scopes all created resources to the specified Equinix Fabric project.
- **`fcr_package`**: `<package_code>` — Optional. Cloud Router package tier (default: `STANDARD`).
- `account_number`: < Equinix account number (integer) > — Required — The billing account number to associate with the router.
- **`bandwidth_in_mbps`**: `<number>` — Optional. Bandwidth for the IPWAN connection in Mbps (default: `1000`).
- **`network_name`**: `<name>` — Optional. Name for the created Network (default: `ipwan-network`; max 24 characters).
- **`fcr_name`**: `<name>` — Optional. Name for the created Cloud Router (default: `fcr`; max 24 characters).
- **`stream_uuid`**: `<UUID>` — Optional. UUID of an existing stream to attach resources to. If omitted, a new stream is created.
- **`stream_name`**: `<name>` — Optional. Name for the new stream when no `stream_uuid` is provided (default: `ipwan-stream`; max 24 characters).
- **`recipient_email_addresses`**: `["<email>", ...]` — Required. List of email addresses to receive the completion report, and used as the `notifications` emails on the Network, Cloud Router, and connection creation calls.
