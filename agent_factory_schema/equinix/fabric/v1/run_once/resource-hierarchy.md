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
Search for the existing fabric cloud router which are not in deprovisioned status, given the project uuid. Summarize the metro distribution, FCR statues and FCR package types based on the result. Stop if the router is not found. Follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/state", "operator": "=", "values": ["PROVISIONED"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 }
}
```

### Step 2
For each Fabric Cloud Router, search for FCR connections of it. Summarize the distribution of connection type, bandwidth. Follow the request payload below:
```json
{
  "filter": {
    "and": [
      { "property": "/operation/equinixStatus", "operator": "!=", "values": ["DEPROVISIONED"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 },
  "sort": [
    {
      "direction": "DESC",
      "property": "/changeLog/updatedDateTime"
    }
  ]
}
```
### Step 3
Search for all available route filters. For each route filter, search for connections attached to it. Summarize the percentage of FCR connections with route filter.
### Step 4
Generate a professional network topology diagram on a white background, drawn as a hierarchical tree with the root at the top and children branching downward. Use neat rectangular boxes, thin connector lines, and clear sans-serif labels. Show IPWAN network at the top as optional, then FABRIC_CLOUD_ROUTER, then L2_CONNECTION (A-SIDE FCR), then ROUTE_FILTER and ROUTE_AGGREGATION as sibling children. Clean, minimal, enterprise-style diagram, portrait layout.
### Step 5 - Compose the Resource Hierarchy Report

**Do not respond to the user between Step 5 and Step 6, Proceed directly to calling `send_email_notification`.**

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
Resources Hierarchy
------------------------------------------
<content>

------------------------------------------
What You Should Do
------------------------------------------
<content>
==========================================


```
Section content rules:
- **Fabric Cloud Router Resources**: List metro distribution, like metro location with highest number of FCRs, FCR package contribution and FCR statuses distribution.
- **Connection Resources**: Mention average connection counts per FCR, grouping by different FCR packages. Also include FCR connection distribution of various connetion type and bandwidth.
- **Network Policy Resources**: Mention percentages of connections with route filter or aggregations attached.
- **Resources Hierarchy**: Use a top-down hierarchy with boxes and connector lines. Preserve the exact parent-child structure provided by the user. Keep node labels exact and concise. Mark optional nodes clearly in the label. Do not add extra nodes, styling clutter, or unrelated annotations. Prefer a clean professional network-diagram look.
- **What You Should Do**: 1–3 plain English recommendations based only on detected findings. Like if any FCRs are error state or don't have any connections. If nothing needs action, always end with: "No issues were detected and no action is required at this time. I will continue monitoring resource hierarchy for you."

Rules:
- Plain English always. No raw event type strings, no API jargon.
- Always use both the human-readable name AND the full UUID when referencing any asset (router, connection, port, routing protocol) or user. Format: `<name> (<full-uuid>)` for assets and `<data.auth.name> (id: <authid>)` for users. If a name is not available, fall back to the full UUID only.
- Final observed state must be stated for any asset with multiple transitions.
### Step 6 — Send the Report
Use `send_email_notification` to send the report to `recipient_email_address`.
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of overall resource hierarchy and headline finding.
- `pdfTitle`: `FabricResourceHierarchy-<project_uuid first 8 chars>`

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`search_connections`**: Searches for an existing fabric cloud router connection.
*   **`search_route_filters`**: Searches for an existing route filters attached to each fabric cloud router connection.
*   **`search_route_aggregations`**: Searches for an existing route aggregations attached to each fabric cloud router connection.
*   **`service_get_rf_connections`**: Retrieves all connections attaching to a route filter.
*   **`send_email_notification`**: Sends an email. Pass pdfTitle and pdfContent (plain text) to auto-generate and attach a PDF.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`project_uuid`**: < A project UUID > - Required - User should specify a project uuid.
* **`recipient_email_address`**: Required. Email address to receive the report.
