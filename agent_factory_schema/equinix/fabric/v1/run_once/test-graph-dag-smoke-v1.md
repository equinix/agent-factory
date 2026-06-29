---
name: graph-dag-smoke
description: DAG runtime smoke — exercises typed edges, cross-node state carry-over, two TransformFn beans, an llm node, and a real email, using only real MCP tools.
execution_mode: GRAPH
graph_pattern: DAG
---

# GRAPH/DAG runtime smoke agent

## Overview
Verifies the GRAPH/DAG runtime (`GraphExecutorDispatcher` → `LangGraphDagExecutor`
→ `GraphBuilder`) end to end in the deployed artifact: a read-only connection
search feeds two deterministic transform functions, an llm node composes a short
report, and the report is emailed. The only mutating action is sending one email
to a fixed internal address.

## Instructions
Run the steps defined in the `## Steps` block. This agent reads connections,
scores and ranks them with built-in transforms, composes a short health summary,
and emails it. It performs no connection/router/port mutation.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches Fabric virtual connections (read-only).
* **`send_email_notification`**: Sends an email with the composed report.

## Guidelines
* **Read-only data access**: Only `search_connections` reads data; nothing is mutated.
* **Single pass**: One search, one email, then stop.

## Steps
```yaml
state:
  connections: list
  findings: list
  report: string
entry: fetch_connections
nodes:
  - id: fetch_connections
    action: tool
    tool: search_connections
    input:
      query: {}
    output: connections
    retry: { max: 2, backoffMs: 1000 }
    edges:
      onSuccess: compute_score
      onEmpty: compose
      onError: end_error
  - id: compute_score
    action: transform
    fn: compositeHealthScore
    reads: [connections, metrics]
    output: findings
    edges:
      onSuccess: rank_and_flag
      onEmpty: compose
  - id: rank_and_flag
    action: transform
    fn: rankAndFlag
    reads: [findings]
    output: findings
    edges:
      onSuccess: compose
      onEmpty: compose
  - id: compose
    action: llm
    promptRef: report_body
    reads: [findings]
    output: report
    edges:
      onSuccess: notify
      onError: end_error
  - id: notify
    action: tool
    tool: send_email_notification
    input:
      emailAddress: "ckuo@equinix.com"
      body: "DAG runtime smoke report:\n${state.report}"
    edges:
      onSuccess: end_ok
      onError: end_error
terminals:
  - { id: end_ok,    status: COMPLETED }
  - { id: end_error, status: FAILED }
```
