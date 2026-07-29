---
name: cloud-router-dry-run
description: Validates an Equinix Fabric Cloud Router creation request via dry-run — checking package availability, quota limits, and account permissions — without provisioning the router.
---
# Fabric Cloud Router dry-run validator agent
## Overview
Validate a new Equinix Fabric Cloud Router (FCR) request by calling the `create_router` tool with `dry_run: true`. This validates the full request — package availability in the target metro, quota limits, and account permissions — without creating the router. Return the dry-run result to the user. Do not proceed to real creation under any circumstances.

## Prerequisites
- **IAM role required**: `Fabric Cloud Router Manager` or `Fabric Manager`
- **Lab tier**: maximum **3 Lab routers per organization** (across all projects)
- User-provided router name, metro code, project UUID, and package code
- A new billing account may take up to 24 hours to activate before it can be used

## Capabilities
- Execute the FCR validation (dry-run) API before creation
- Verify package availability in the target metro
- Check quota limits (e.g. the 3-Lab-per-org cap)
- Validate account permissions
- Surface errors early with clear remediation
- Never proceed to real creation — this skill is validation-only

## Instructions
### Definition of Done
- Dry-run call completed and its full result returned to the user
- On dry-run failure: all errors and remediation steps are reported
- On dry-run success: validation result reported; no router is created

### Package Limits (for reference)
| Package | Max Connections | Max Routes (IPv4/IPv6) | Max VC Bandwidth | Notes |
|---|---|---|---|---|
| **Lab** | 10 | 50 / 50 | 50 Mbps | Max 3 per org; no other L2 service profiles |
| **Basic** | ~15 (recommended) | 250 / 50 | 1 Gbps | |
| **Standard** | ~25 (recommended) | 1,000 / 100 | 10 Gbps | |
| **Advanced** | ~35 (recommended) | 4,000 / 250 | 100 Gbps | |

### 1. Gather Requirements
Collect or infer and confirm:
- **Metro**: e.g. `SV`, `NY`, `AM`
- **Package**: one of `LAB`, `BASIC`, `STANDARD`, `ADVANCED`
- **Router name**: optional but recommended
- **Project UUID**: required
- **Notification email(s)**: required

### 2. Execute Dry-Run Validation (gate)
Call `create_router` with all collected parameters and `dry_run: true`.

- The tool validates the full request server-side without provisioning anything.
- Return the complete dry-run response to the user.
- Return the complete dry-run response to the user regardless of outcome.
- Report any errors and remediation steps from the response.
- **Do not call `create_router` again.** This skill ends after returning the dry-run result.

## Guidelines
- **Validation only**: Call `create_router` exactly once with `dry_run: true`. Never call it without `dry_run: true`.
- **Return the dry-run result**: Always show the full dry-run response to the user.
- **Surface errors early**: Report all errors from the dry-run response together with remediation.
- **Prioritize Clarity**: Ensure all parameters are clearly identified from the user's request before making any tool call.

## Error Handling
When the dry-run fails, do not create the router. Report errors from the dry-run response:
- **Authorization error**: Verify the user has `Fabric Cloud Router Manager` or `Fabric Manager` role.
- **Metro not found / unsupported**: List available FCR metros via `list_metro`.
- **Package unavailable**: Show the four valid packages (LAB, BASIC, STANDARD, ADVANCED).
- **Lab quota reached**: Inform user of the 3-Lab-per-org cap; suggest Basic or higher, or deleting an existing Lab router.

## Available Tools
- **`create_router`**: Call with `dry_run: true` to validate without provisioning. This is the only call this skill makes.
- **`list_metro`**: Get available metro locations (used for remediation if metro check fails).
- **`get_router_package`**: Get fabric cloud router package details (used for remediation if package check fails).

## Configuration
* **`router_name`**: Required - User should specify name of the cloud router.
* **`metro_code`**: Required - User should specify metro code of the cloud router.
* **`notification_email`**: Required - List of email addresses to receive notification of the cloud router.
* **`project_uuid`**: Required - User should specify project of the cloud router.
* **`package_code`**: Required - User should specify package code of the cloud router.
