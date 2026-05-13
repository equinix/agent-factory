---
name: creating-fabric-cloud-router
description: Creates a new Equinix Fabric Cloud Router (FCR) by gathering metro, package, and project requirements, then validating successful provisioning. Use when a user wants to create, provision, or deploy a Fabric Cloud Router or FCR.
---
# Fabric Cloud Router creator agent
## Objective
Create a new Equinix Fabric Cloud Router (FCR) with the user's specified metro, package, and project configuration.

## Definition of Done
- Router UUID returned from the creation call
- Router state is `Provisioned` or `Provisioning`
- Configuration matches user requirements

## Constraints
- **Lab tier**: maximum **3 Lab routers per organization** (across all projects)
- **IAM role required**: `Fabric Cloud Router Manager` or `Fabric Manager`
- Available in all 64+ Equinix Fabric markets
- A new billing account may take up to 24 hours to activate before it can be used

### Package Limits (for Step 3 comparison)
| Package | Max Connections | Max Routes (IPv4/IPv6) | Max VC Bandwidth | Notes |
|---|---|---|---|---|
| **Lab** | 10 | 50 / 50 | 50 Mbps | Max 3 per org; no other L2 service profiles |
| **Basic** | ~15 (recommended) | 250 / 50 | 1 Gbps | |
| **Standard** | ~25 (recommended) | 1,000 / 100 | 10 Gbps | |
| **Advanced** | ~35 (recommended) | 4,000 / 250 | 100 Gbps | |

## Steps

### 1. Check Existing Routers
List all FCRs in the user's account. Note the count of Lab-tier routers across the org (hard limit: 3 per org), existing naming conventions, and active metros. Use this to suggest a project if the user hasn't specified one.

### 2. Gather Requirements
Collect or infer and confirm:
- **Metro**: e.g. `SV`, `NY`, `AM`
- **Package**: to be validated in Step 3
- **Router name**: optional but recommended
- **Project ID**: if user wants Lab tier, confirm org hasn't already reached the 3-Lab limit

### 3. Validate Metro and Packages
1. Verify the metro exists and supports FCR
2. If the user has not specified a package, or wants to compare options, call `get_router_package` for each available package code (`LAB`, `BASIC`, `STANDARD`, `ADVANCED`) to fetch details — bandwidth, routing capabilities, and any limits — then present a comparison to help the user choose
3. If the user has already specified a package code, call `get_router_package` with that code to validate it exists and confirm its details before proceeding
4. Confirm the final package selection with the user

### 4. Create the Router
Call the create router operation with: metro code, package code, router name, project ID.
Capture: router UUID, creation status, initial state.

Handle any errors gracefully and surface clear feedback.

### 5. Confirm Provisioning
Retrieve the router by UUID. Confirm state is `Provisioned` or `Provisioning` and display UUID, name, metro, package, state, and timestamp.
    
## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Error Handling
- **Lab limit reached**: Inform user of the 3-Lab-per-org cap; suggest using Basic or higher, or deleting an existing Lab router
- **Metro not found**: List available metros via `list_metro`
- **Package unavailable**: Show the four valid packages (LAB, BASIC, STANDARD, ADVANCED)
- **Creation failed**: Surface the error message with remediation steps
- **Authorization error**: Verify user has `Fabric Cloud Router Manager` or `Fabric Manager` role

## Available Tools
This skill can use the following tools:
*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`create_router`**: Creats a fabric cloud router. 
