---
name: resource-hierarchy
description: Analyzes all Fabric Cloud Router related resources within a given Equinix Fabric project
---

# Cloud Router resource hierarchy agent

## Overview
This definition sets up and activates an Equinix agent that list the FCR related resource hierarchy in a project. 
List all FCRs in a project and the FCR connections and route filters which are associated with each FCR.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically list the FCR related resource hierarchy in a project.
- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.

## Prerequisites
Fabric Cloud router resources exist in the given project. A valid Equinix Fabric project UUID must be available.

## Instructions
Do NOT write the report as prose in your response text. Compose in-memory only, then immediately call `send_email_notification`. The report must only appear as the `pdfContent` parameter — never in the response body.
**Do not respond to the user, Proceed directly to calling `send_email_notification`.**

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
<content>

------------------------------------------
Connection Resources
------------------------------------------
<content>

------------------------------------------
Network Policy Resources
------------------------------------------
<content>

------------------------------------------
What You Should Do
------------------------------------------
<content>
==========================================
```
### Step 2— Send the Report
Use `send_email_notification` to send the report to `recipient_email_address`.
- `pdfContent`: the full report text from Step 5.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricInsights-<project_uuid first 8 chars>-<reporting period from date>-<reporting period to date>-<Overall Status label>`

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`search_connections`**: Searches for an existing fabric cloud router connection.
*   **`search_route_filters`**: Searches for an existing route filters attached to each fabric cloud router connection.
*   **`search_route_aggregations`**: Searches for an existing route aggregations attached to each fabric cloud router connection.

## Follow the action step by step below:
1. Search for the existing fabric cloud router given the project uuid. Stop if the router is not found.
2. Once the router details are retrieved, search for the existing fabric cloud router connection given the fcr uuid.
3. Once the fabric cloud router connection details are retrieved, search for the associated route filters and route aggregations given the fcr connection uuid.
4. Send 

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`project_uuid`**: < A project UUID > - Required - User should specify a project uuid.
* **`recipient_email_address`**: Required. Email address to receive the report.
