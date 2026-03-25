---
name: resource-hierarchy
description: Analyzes all Fabric Cloud Router related resources within a given Equinix Fabric project
---

# Cloud Router resource hierarchy agent

## Overview
This definition sets up and activates an Equinix agent that list the FCR (Fabric Cloud Routers) related resource hierarchy in a project. Summarize FCRs in a project and the FCR connections which are associated with each FCR. If FCRs are connected to IPWAN network via FCR to IPWAN connection, include IPWAN topology as well.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically list the Fabric Cloud Router and related resource hierarchy in a project.
- Deliver a plain-English resource hierarchy summary via email as a PDF report

## Prerequisites
Fabric Cloud router resources exist in the given project. A valid Equinix Fabric project UUID must be available.

## Instructions
### Step 1
Search for the existing fabric cloud router given the project uuid. Summarize the metro distribution, FCR statues and FCR package types based on the result. Stop if the router is not found.
### Step 2
For each of the cloud router, search for the connection by the cloud router UUID. Summarize connection count for each FCR.
### Step 3
### Step 4 - Compose the Resource Hierarchy Report
**Do not respond to the user between Step 4 and Step 5, Proceed directly to calling `send_email_notification`.**

Structure the report using these sections (omit any section with no content — no placeholder text). Do not include any section numbers in the headings. Use the separator formatting shown below exactly:

```
==========================================
Overall Resource Hierarchy:
==========================================

------------------------------------------
Summary
------------------------------------------
<content>

------------------------------------------
IPWAN Resources
------------------------------------------
<content>

------------------------------------------
Fabric Cloud Router Resources
------------------------------------------
1. Metro Distribution: Metro Location with Highest Number of FCRs is Silicon Valley in AMER region.
2. FCR Status: Most FCRs are in PROVISIONED state, there are several FCRs in error state, which may 
require your attention, FCR named xxx is in NOT_PROVISIONED state.
3. FCR Package: Your FCRs are primarily using the STANDARD package, also featuring BASIC and LAB 
package, note that you cannot create more than 5 FCRs with the Lab package.

------------------------------------------
Connection Resources
------------------------------------------
FCR Connections: There are several FCRs that don't have connections associated. You can create 
connection from FCR to your Equinix asset or cloud service provider.

------------------------------------------
What You Should Do
------------------------------------------
Most FCRs are in PROVISIONED state, there are several FCRs in error state, which may 
require your attention, FCR named xxx is in NOT_PROVISIONED state.
==========================================
```
### Step 5 — Send the Report
Use `send_email_notification` to send the report to `recipient_email_address`.
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of overall resource hierarchy and headline finding.
- `pdfTitle`: `FabricResourceHierarchy-<project_uuid first 8 chars>`

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`search_connections`**: Searches for an fabric cloud router connection w

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`project_uuid`**: < A project UUID > - Required - User should specify a project uuid.
* **`recipient_email_address`**: Required. Email address to receive the report.
