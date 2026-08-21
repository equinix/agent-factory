---
name: cloud-router-management
description: Creates a Fabric Cloud Router based on user-provided parameters and notifies on completion.
categories: ["Deploy & Change Agents"]
---

# Cloud Router Management Agent

## Overview
An Equinix agent that creates a Fabric Cloud Router with user-specified parameters.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- Automatically create a Fabric Cloud Router with user-defined configuration
- Validate router package availability before creation
- Notify the user upon successful creation or failure
- Log all actions and decisions

## Prerequisites
- User must have appropriate IAM permissions to create cloud routers.
- A valid Equinix project ID and account number are required.
- The selected router package must be available in the target metro.

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches for existing cloud routers. Used to check for duplicates and to confirm post-creation status.
*   **`create_router`**: Creates a new Fabric Cloud Router with the specified configuration.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.

## Instructions
1. Determine the `package_code` from the user's request; if none is provided, default to `"STANDARD"`.
2. Use `search_routers` to check whether a router with the same name already exists in the user's account to avoid duplicates. If a duplicate is found, log a warning and stop.
3. Use `create_router` to create the cloud router. The tool takes a `router_request` object
   with this structure (note: `accountNumber` is an **integer**):
    ```json
    {
      "router_request": {
        "type": "XF_ROUTER",
        "name": "<name>",
        "location": {
          "metroCode": "<metro_code>"
        },
        "package": {
          "code": "<package_code>"
        },
        "notifications": [
          {
            "type": "ALL",
            "emails": ["<email1>", "<email2>"]
          }
        ],
        "account": {
          "accountNumber": <account_number>
        },
        "project": {
          "projectId": "<project_id>"
        }
      }
    }
    ```
4. After creation, use `search_routers` to confirm the router was successfully provisioned and retrieve its UUID and status.
5. Next, send an email notification to the recipient email addresses specified in `notifications`,
   using the router details (UUID, name, metro, package, status, and creation timestamp) as the
   email body, so the recipient is clearly informed of the outcome using `send_email_notification`.

## Guidelines
*   **Prioritize Clarity**: Ensure all required parameters are clearly identified from the user's request before making the tool call.
*   **Duplicate Prevention**: Always search for an existing router with the same name before creating a new one.
*   **Error Handling**: If parameters are invalid or the creation fails, log errors clearly and stop the process. Do not retry automatically.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Notification**: Always confirm the final state of the router back to the user with actionable details (UUID, status).

## Configuration
* **`name`**: < Router name > — Required — A descriptive name for the cloud router.
* **`type`**: < Router type > — Optional — The router type. Defaults to `"XF_ROUTER"`.
* **`metro_code`**: < Metro code, e.g. `"SV"`, `"DC"`, `"AM"` > — Required — The Equinix metro where the router will be deployed.
* **`package_code`**: < Package code, e.g. `"STANDARD"`, `"PREMIUM"`, `"LAB"` > — Optional — Defaults to `"STANDARD"` if not specified.
* **`account_number`**: < Equinix account number (integer) > — Required — The billing account number to associate with the router.
* **`project_id`**: < Project ID > — Required — The Equinix project to associate the router with.
* **`notifications`**: < Comma-separated email addresses > — Required — Email addresses to receive provisioning status notifications (notification type defaults to `"ALL"`).
