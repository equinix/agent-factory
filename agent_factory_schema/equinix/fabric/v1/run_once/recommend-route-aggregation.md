---
name: recommend-route-aggregation
description: Recommends aggregate (supernet) routes for a Fabric Cloud Router based on its active route table entries.
---


# Cloud Router route aggregation recommendation agent
## Overview
This definition sets up and activates an Equinix agent that recommends, or suggests, aggregate routes for a Fabric Cloud Router (also referred to as FCR or router).
The agent analyzes the router's active route table entries and suggests an optimized set of aggregate (supernet) IPv4 routes to simplify route advertisement and reduce route table size.
A router UUID is required, and a connection UUID is optional but recommended for more accurate, connection-scoped aggregation.
This agent runs once immediately by default unless scheduled by user.


## Capabilities
- Recommend an optimized set of aggregate (supernet) IPv4 routes for a Fabric Cloud Router based on its active route table entries.
- Optionally scope the recommendation to a specific connection on the router for higher accuracy.
- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.

## Prerequisites
The Fabric Cloud Router must exist and be in a PROVISIONED state with active IPv4 route table entries.
A router UUID is required. A connection UUID is optional but recommended: it improves the accuracy of the route aggregation and makes it easier to attach the recommended aggregation to that connection later.

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches for an existing Fabric Cloud Router. Used to confirm the router UUID before generating recommendations.
*   **`search_routes`**: Searches the routing table of a Fabric Cloud Router. Use `route_type` = `active` to retrieve the router's active route table entries, optionally scoped to a connection via `connection_uuid`. Each returned route exposes a `prefix` field (the CIDR entry) to feed into aggregation.
*   **`recommend_route_aggregation`**: Recommends or suggests aggregate routes. Given a list of route prefixes (`routePrefixes`) and an optional `connectionUuid`, it excludes IPv6 prefixes, performs deterministic CIDR aggregation on the IPv4 prefixes, and returns the recommended aggregate IPv4 routes.

## Instructions
1. Determine the target router. The `router_uuid` is required. If it was not provided, ask the user which Fabric Cloud Router (FCR) they are referring to and confirm the UUID before proceeding. Do not guess or fabricate a router UUID.
2. Confirm the router exists by searching for it with `search_routers` using the provided `router_uuid`. If the router cannot be found, stop and report this to the user.
3. Check for a connection UUID. The `connection_uuid` is optional. If it was not provided, gently let the user know that although it is optional, providing it is recommended for better accuracy in route aggregation and that it also helps later when attaching the recommended aggregation to that connection. Proceed without it if the user does not provide one.
4. Retrieve the router's active route table entries with `search_routes`, passing `router_uuid`, `route_type` = `active`, and the `connection_uuid` when one was provided. Use the default query (no filter; `pagination` `offset` = 0, `limit` = 20) unless the user requests a narrower scope, and page through additional offsets until all active entries are collected. Collect the `prefix` value from each returned route.
   - When a `connection_uuid` is provided, the routes are scoped to that connection on the router.
   - When no `connection_uuid` is provided, all active routes for the router are used.
5. Call `recommend_route_aggregation` with the collected prefixes as `routePrefixes` (and the `connection_uuid` as `connectionUuid` when available) to obtain the recommended aggregate routes. The tool excludes IPv6 prefixes and aggregates the IPv4 prefixes deterministically.
6. Present the recommended aggregate IPv4 routes back to the user clearly. If no routes are returned (for example, when there are no active IPv4 entries), report that no aggregation is recommended.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified and confirmed from the user's request before making the tool call. Never fabricate a router or connection UUID.
*   **IPv4 only**: Route aggregation applies to IPv4 prefixes only; IPv6 prefixes are excluded from the recommendation.
*   **Deterministic Aggregation**: Rely on `recommend_route_aggregation` for the actual CIDR aggregation. Do not attempt to compute or alter aggregate routes through reasoning — present exactly what the tool returns.
*   **Error Handling**: If parameters are invalid or any operation fails, log the error and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`router_uuid`**: < A Fabric Cloud Router UUID > - Required - The FCR (Fabric Cloud Router) UUID for which to recommend aggregate routes.
* **`connection_uuid`**: < A connection UUID > - Optional - Recommended for more accurate, connection-scoped aggregation; also enables attaching the recommended aggregation to that connection later.
