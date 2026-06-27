---
name: qa3-graph-dryrun-smoke
description: QA3 smoke test — verifies the GRAPH execution runtime is wired and invoked, with zero downstream Fabric calls.
execution_mode: GRAPH
graph_pattern: REACT
max_iterations: 1
---

# GRAPH dry-run smoke agent (QA3 only)

## Overview
This template exists ONLY to verify, in QA3, that an agent template with
`execution_mode: GRAPH` is routed to the GRAPH runtime (`GraphExecutor` →
`LangGraphReActExecutor`) and that the executor runs end to end. It deliberately
makes **no Fabric API call**, so it is unaffected by the QA3 Fabric MCP server
apikey issue (EQ-3155110). A successful run proves the GRAPH wiring; it does NOT
prove real tool execution — that is validated in UAT.

## Why this is safe
- `execution_mode: GRAPH` is template-scoped data. Existing templates have no
  `execution_mode` and continue to use the default SEQUENTIAL path, so this
  template cannot affect any existing agent.
- The tool listed below (`graph_dryrun_probe`) intentionally does **not** match any
  registered MCP tool. It satisfies the engine's non-empty `supported_tools` guard
  (avoids `EMPTY_TOOLS`), but after name-filtering the executor receives **zero
  callable tools** — so no downstream Fabric request is ever possible.

## Instructions
1. Do NOT call any tool. No tool is available and none is needed.
2. Respond with exactly this single line and nothing else:
   `GRAPH_DRYRUN_OK`
3. The operation is complete once that line is returned.

## Available Tools
This skill can use the following tools:

* **`graph_dryrun_probe`**: A non-existent placeholder tool. It is listed only to
  satisfy the non-empty tool guard and must never be called.

## Guidelines
* **No side effects**: This agent must not call tools, fetch data, or mutate anything.
* **Deterministic output**: Always return the single line `GRAPH_DRYRUN_OK`.
* **Stop immediately**: Do not loop or retry; one response completes the run.

## Configuration
* (none) — this template takes no parameters.
