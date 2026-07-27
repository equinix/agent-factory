---
name: ipwan-fcr-network-setup
description: Creates one Network, one Cloud Router, and one IPWAN connection between them, attaches the Cloud Router and connection to a stream, and notifies on completion.
---

# IPWAN & Cloud Router Network Setup Agent

## Overview
An Equinix agent that provisions a single IPWAN-based network topology with FCR. 
It creates one Network, one Cloud Router at a user-specified metro location, and one IPWAN connection linking the Cloud Router to the network. After the Cloud Router and connection reach PROVISIONED state the agent attaches them to a stream (creating one if needed; the Network itself cannot be attached to a stream) and sends a completion summary via email.
This agent runs once immediately by default unless scheduled by user.

## Success Criteria & Termination
- **Success**: The Network, Cloud Router, and connection are all created and reach a ready state (`ACTIVE` for the Network, `PROVISIONED` for the Cloud Router and connection), the Cloud Router and connection are attached to the stream, and a completion email is sent. The run ends after Step 9 — no further action is taken.
- **Partial failure**: Any one of Steps 1–8 fails or times out. The agent stops attempting further creation/provisioning/attachment work immediately, reports exactly what succeeded and what failed (with the resource and error detail) in the completion email, and ends the run there. It never retries automatically and never leaves the run silently unfinished — every run terminates with exactly one completion email.
- **Escalation**: The agent does not escalate to a human directly. All success and failure outcomes are surfaced only via the Step 9 completion email to `recipient_email_addresses`; a human must read that email and re-run the agent (after remediating, per Guidelines below) if the outcome was a failure.

## Capabilities
- Create a Fabric Network of type IPWAN scoped to a project
- Create one Cloud Router at the specified metro location with a configurable package
- Create one IPWAN connection between the Cloud Router and the network
- Poll all resources until they reach PROVISIONED state before proceeding
- Create a stream automatically if no stream UUID is provided, then attach the provisioned Cloud Router and connection to it (networks cannot be attached to a stream)
- Send an email completion report summarizing all created resources and their states

## Prerequisites
- The agent's Fabric API credentials must have permission to create networks, cloud routers, and connections; to create and read streams and stream assets; and to send email notifications.
- `project_uuid` must be provided and must reference a project the credentials can access — `create_connection` requires it, so the Network, Cloud Router, connection, and stream are all scoped to this same project.
- The project's plan must have unused quota for at least 1 additional Network, 1 additional Cloud Router, and 1 additional connection — insufficient quota causes a 4xx error from `create_network`/`create_router`/`create_connection` and is treated as a creation failure (see Guidelines).
- `metro` must be a valid, currently-active Equinix Fabric metro code with Cloud Router availability (e.g., `SV`, `DC`, `LD`, `SG`) and must resolve to one of the three supported regions (`AMER`, `EMEA`, `APAC`).
- `account_number` must be a billing account number the requesting user/credentials are authorized to bill against; an unauthorized or nonexistent account number causes `create_router` to fail.
- `bandwidth_in_mbps`, if provided, must be a positive integer within the connection bandwidth tiers Fabric supports for `IPWAN_VC` (typically 50–10000 Mbps); values outside the supported range are rejected by `create_connection`.
- `fcr_package`, if provided, must be one of the package codes valid for the target metro (e.g., `LAB`, `BASIC`, `STANDARD`, `ADVANCED`, `PREMIUM`); an unsupported package code causes `create_router` to fail.
- `recipient_email_addresses` must contain at least one syntactically valid email address — the completion email cannot be sent otherwise, and the platform's per-resource `notifications` also require a non-empty list.

## Available Tools
This skill can use the following tools:

- **`create_network`**: Creates a Fabric Network. Accepts name, type (`IPWAN`), scope (`REGIONAL` or `GLOBAL`), location (region or metro code), notifications (mandatory), and project UUID.
- **`search_networks`**: Searches for existing Fabric Networks by filter.
- **`create_router`**: Creates a Fabric Cloud Router. Accepts name, location (metro code), package, billing account number, notifications (mandatory), and project UUID.
- **`search_routers`**: Searches for existing Fabric Cloud Routers by filter to check provisioning state.
- **`create_connection`**: Creates a connection. Used to create IPWAN connections between a Cloud Router and a Network. Accepts notifications.
- **`search_connections`**: Searches for existing connections to verify provisioning state.
- **`get_stream_details`**: Fetches stream details given a stream UUID.
- **`create_stream`**: Creates a new stream given a name and project UUID.
- **`attach_stream_asset`**: Attaches a resource (router or connection) to a stream by UUID. Networks cannot be attached to a stream.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.

## Instructions

### Step 1 — Validate Inputs
1a. Confirm that `metro` is a valid metro code. Stop and report an error if it is empty or missing.

1b. Confirm that `account_number` is provided. Stop and report an error if it is empty or missing.

1c. Confirm that `project_uuid` is provided. Stop and report an error if it is empty or missing — `create_connection` requires it, so all resources must be scoped to the same project.

1d. Determine `region` from `metro`'s Equinix continental region — one of `AMER`, `EMEA`, or `APAC` (e.g., metros such as SV, DC, NY, CH, DA, MI map to `AMER`; LD, FR, AM, PA, MD, ML, ZH map to `EMEA`; SG, HK, TY, OS, SY map to `APAC`). Stop and report an error if the metro's region cannot be determined.

1e. Apply naming defaults if the optional name fields are not provided:
- `network_name` → `ipwan-network`
- `fcr_name` → `fcr`
- `stream_name` → `ipwan-stream`

1f. Apply numeric defaults if not provided:
- `bandwidth_in_mbps` → `1000`
- `fcr_package` → `STANDARD`

### Step 2 — Create the Network
2a. Call `create_network` with:
- `name`: `network_name`
- `type`: `IPWAN`
- `scope`: `REGIONAL`
- `location.region`: `region`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid`

2b. Record the returned network UUID as `network_uuid`. If creation fails, skip Steps 3–8 and go directly to Step 9 to send a completion email reporting the network creation failure and its error detail.

### Step 3 — Create the Fabric Cloud Router
3a. Call `create_router` with:
- `name`: `fcr_name`
- `location.metroCode`: `metro`
- `package.code`: `fcr_package`
- `account.accountNumber`: `account_number`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid`

3b. Record the returned router UUID as `fcr_uuid`. If creation fails, skip Steps 4–8 and go directly to Step 9 to send a completion email reporting the Network as created, the Cloud Router creation failure, and its error detail.

### Step 4 — Wait for the Cloud Router to Provision
4a. Repeat up to 30 times (30 × 15000 ms = 450 seconds / 7.5 minutes maximum) or until the Cloud Router is PROVISIONED:
- Call `wait` for 15000 milliseconds.
- Call `search_routers` filtering by `fcr_uuid` and check `state`.
- Break early once `state` = `PROVISIONED`.

4b. If the Cloud Router has not reached PROVISIONED after 30 retries (450 seconds), treat this as a provisioning timeout: skip Steps 5–8 and go directly to Step 9 to send a completion email reporting a timeout error identifying the Cloud Router that failed and the 450-second threshold exceeded.

### Step 5 — Wait for the Network to Provision
5a. Repeat up to 30 times (30 × 15000 ms = 450 seconds / 7.5 minutes maximum) or until the Network is ready:
- Call `wait` for 15000 milliseconds.
- Call `search_networks` filtering by `network_uuid` and check `state`.
- Break early once `state` = `ACTIVE` (Networks use `ACTIVE`/`INACTIVE`/`DELETED`, not `PROVISIONED`, as their state values).

5b. If the Network has not reached `ACTIVE` after 30 retries (450 seconds), treat this as a provisioning timeout: skip Steps 6–8 and go directly to Step 9 to send a completion email reporting a timeout error identifying the Network that failed and the 450-second threshold exceeded. Do not attempt to create the connection against a Network that is not yet `ACTIVE` — doing so can produce an opaque internal error from `create_connection` (e.g., `EQ-3142502`) instead of a clear validation error.

### Step 6 — Create the IPWAN Connection
6a. Call `create_connection` with:
- `name`: `conn-<metro>-ipwan`
- `type`: `IPWAN_VC`
- `bandwidth`: `bandwidth_in_mbps`
- `aSide.accessPoint.type`: `CLOUD_ROUTER`
- `aSide.accessPoint.router.uuid`: `fcr_uuid`
- `zSide.accessPoint.type`: `NETWORK`
- `zSide.accessPoint.network.uuid`: `network_uuid`
- `notifications`: `[{"type": "ALL", "emails": recipient_email_addresses}]`
- `project.projectId`: `project_uuid`

6b. Record the returned connection UUID as `connection_uuid`. If creation fails, skip Steps 7–8 and go directly to Step 9 to send a completion email reporting the Network and Cloud Router as created, the connection creation failure, and its error detail.

### Step 7 — Wait for the Connection to Provision
7a. Repeat up to 30 times (30 × 15000 ms = 450 seconds / 7.5 minutes maximum) or until the connection is PROVISIONED:
- Call `wait` for 15000 milliseconds.
- Call `search_connections` filtering by `connection_uuid` and check `state`.
- Break early once `state` = `PROVISIONED`.

7b. If the connection has not reached PROVISIONED after 30 retries (450 seconds), treat this as a provisioning timeout: skip Step 8 and go directly to Step 9 to send a completion email reporting a timeout error identifying the connection that failed and the 450-second threshold exceeded.

### Step 8 — Set Up Stream
8a. If `stream_uuid` is provided, call `get_stream_details` to verify the stream exists. Stop if it does not.

8b. If `stream_uuid` is not provided, call `create_stream` with:
- `name`: `stream_name`
- `project.projectId`: `project_uuid`

Record the returned UUID as `stream_uuid`.

8c. Attach the Cloud Router and connection to the stream in order (Networks cannot be attached to a stream):
1. Call `attach_stream_asset` with the `fcr_uuid` and `"metrics_enabled": false`.
2. Call `attach_stream_asset` with the `connection_uuid`.

Wait 3000 milliseconds after each attachment to allow the platform to register the asset.

### Step 9 — Send Completion Notification
9a. Compose the completion report in memory using the structure below.

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
                <li>Region</li>
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
- **Network**: One row — name, UUID, type (`IPWAN`), scope (`REGIONAL`), region, and final state. If the network was never created, state "Not created" and the error detail in place of UUID/state.
- **Fabric Cloud Router**: One row — name, UUID, metro, package, and final state. If the router was never created, state "Not created" and the error detail in place of UUID/state; if creation was skipped because the network failed, state "Skipped — network creation failed".
- **IPWAN Connection**: One row — name, UUID, the Cloud Router UUID it links, bandwidth, and final state. If the connection was never created, state "Not created" and the error detail in place of UUID/state; if creation was skipped because an earlier resource failed, state "Skipped — <resource> creation failed".
- **Stream Attachment**: If the Cloud Router and connection were successfully attached to stream UUID, confirm this and state whether the stream was newly created or pre-existing (note that the Network is not attached, as networks cannot be attached to a stream). If stream attachment was skipped due to an earlier failure, state that explicitly.
- **Next Steps**: If the run succeeded, give 1–3 plain-English recommendations (e.g., configure a BGP routing protocol on the Cloud Router, set up an alert rule on the connection, validate end-to-end connectivity with a PING command). If the run failed, state the specific remediation from the Guidelines' Remediation mapping that matches the reported error, and note that the agent must be re-run manually after remediating.

9b. Call `send_email_notification` with:
- `pdfContent`: the full report from Step 9a.
- `body`: one-paragraph summary of what was created and the final topology state.
- `pdfTitle`: `FabricIPWAN_<network_uuid>_Setup_Complete`
- `recipients`: `recipient_email_addresses`

## Guidelines
- **Prioritize Clarity**: Confirm all required parameters are present before making any tool call.
- **Error Handling**: If any creation or provisioning step fails, do not abort silently. Skip the remaining creation, provisioning, and stream-attachment steps, and go directly to Step 9 to send a completion email reporting the failing resource and its error detail.
- **No automatic retry**: The agent never automatically retries a failed creation call or re-runs after a timeout. Remediation and re-running are manual, human-driven steps triggered by reading the completion email.
- **Remediation mapping** — match the reported error to a specific fix before re-running:
  - Quota exceeded (4xx from `create_network`/`create_router`/`create_connection`): request a quota increase for the project, or delete unused resources, then re-run.
  - Invalid or unsupported `metro`/region, `fcr_package`, or `bandwidth_in_mbps`: correct the configuration value to one valid for the target metro, then re-run.
  - Invalid or unauthorized `account_number`: verify the billing account number and its authorization for the project, then re-run.
  - `notifications` or `recipient_email_addresses` empty/invalid: supply at least one valid recipient email address, then re-run.
  - Provisioning timeout (450 seconds exceeded) on the Network, Cloud Router, or connection: check Equinix Fabric platform status for the metro/region, then re-run once the resource either provisions on its own or is confirmed stuck and removed.
  - Internal system error from `create_connection` (e.g., `EQ-3142502`) immediately after network creation: this typically means the Network had not yet reached `ACTIVE` when the connection was attempted; confirm the Network's state via `search_networks`, wait for it to become `ACTIVE`, then re-run.
- **Polling discipline**: Always wait between state polls. Never skip the wait step even if a resource appears fast to provision.
- **Name length**: Keep all generated names to 24 characters or fewer for platform compatibility.
- **Token Efficiency**: Carry only UUIDs and state values forward between steps — do not pass full resource payloads downstream.
- **Plain English**: Report section text must use plain English with no raw API jargon.

## Configuration
- **`metro`**: `<metro_code>` — Required. Equinix metro code where the Cloud Router will be created (e.g., `SV`). Also used to derive the `region` (`AMER`, `EMEA`, or `APAC`) for the REGIONAL-scope Network.
- **`project_uuid`**: `<UUID>` — Required. Scopes the Network, Cloud Router, connection, and stream to the specified Equinix Fabric project (`create_connection` fails without it).
- **`fcr_package`**: `<package_code>` — Optional. Cloud Router package tier (default: `STANDARD`).
- `account_number`: < Equinix account number (integer) > — Required — The billing account number to associate with the router.
- **`bandwidth_in_mbps`**: `<number>` — Optional. Bandwidth for the IPWAN connection in Mbps (default: `1000`).
- **`network_name`**: `<name>` — Optional. Name for the created Network (default: `ipwan-network`; max 24 characters).
- **`fcr_name`**: `<name>` — Optional. Name for the created Cloud Router (default: `fcr`; max 24 characters).
- **`stream_uuid`**: `<UUID>` — Optional. UUID of an existing stream to attach resources to. If omitted, a new stream is created.
- **`stream_name`**: `<name>` — Optional. Name for the new stream when no `stream_uuid` is provided (default: `ipwan-stream`; max 24 characters).
- **`recipient_email_addresses`**: `["<email>", ...]` — Required. List of email addresses to receive the completion report email sent in Step 9. Note: the Fabric platform also sends its own separate notification for each of the Network, Cloud Router, and connection creation calls to this same list (its `notifications.emails` field cannot be empty), so recipients will see those in addition to the Step 9 report.
