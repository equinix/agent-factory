---
name: graph-runtime-smoke
description: Runtime smoke check — verifies the GRAPH execution runtime is wired and runs a read-only tool end to end.
execution_mode: GRAPH
graph_pattern: REACT
max_iterations: 2
---

# GRAPH runtime smoke agent

## Overview
Verifies that a template with `execution_mode: GRAPH` is routed to the GRAPH
runtime (`GraphExecutor` → `LangGraphReActExecutor`) and runs end to end against a
real, read-only tool. It performs a single read-only connection search and reports
the count. It never creates, updates, or deletes anything.

## Instructions
Call `search_connections` once to list connections, then report how many
connections were found in a single short sentence. Do not modify, create, or
delete anything. Stop after reporting the count.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches for connections (read-only).

## Guidelines
* **Read-only**: Only `search_connections` may be called. No mutating action is allowed.
* **Single pass**: Report the count once and stop. Do not loop or retry.

## Configuration
* (none) — this template takes no parameters.
