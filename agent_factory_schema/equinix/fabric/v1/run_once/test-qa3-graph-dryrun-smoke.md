---
name: graph-runtime-smoke
description: Runtime smoke check — verifies the GRAPH execution runtime is wired and invoked end to end, with no mutating call.
execution_mode: GRAPH
graph_pattern: REACT
max_iterations: 1
---

# GRAPH runtime smoke agent

## Overview
This template verifies that an agent template with `execution_mode: GRAPH` is
routed to the GRAPH runtime (`GraphExecutor` → `LangGraphReActExecutor`) and that
the executor runs end to end. It performs no mutating action: it lists one
read-only tool to satisfy template validation but instructs the agent never to
call it. A `COMPLETED` activity proves the GRAPH wiring is live.

## Why this is safe
- `execution_mode: GRAPH` is template-scoped data. Existing templates have no
  `execution_mode` and continue to use the default SEQUENTIAL path, so this
  template cannot affect any existing agent.
- The only listed tool is read-only (`search_connections`) and the instructions
  forbid calling it, so no customer configuration is read or mutated.

## Instructions
This is a runtime availability check. Do not call any tool. Respond with exactly
one short sentence confirming that you are operational, then stop. The operation
is complete once that sentence is returned. Do not loop or retry.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches for connections. Listed only to satisfy
  template validation; it must not be called by this smoke agent.

## Guidelines
* **No side effects**: This agent must not call tools, fetch data, or mutate anything.
* **Single response**: Return one confirmation sentence; one response completes the run.
* **Stop immediately**: Do not loop or retry.

## Configuration
* (none) — this template takes no parameters.
