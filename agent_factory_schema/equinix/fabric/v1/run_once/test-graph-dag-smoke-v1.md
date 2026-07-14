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
This agent reads Fabric connections, scores and ranks them with built-in transforms,
composes a short health summary, and emails it. It performs no connection/router/port
mutation. Use `search_connections` to fetch connections, then the built-in transforms to
score and rank, then compose the summary and send it via `send_email_notification`.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches Fabric virtual connections (read-only).
* **`send_email_notification`**: Sends an email with the composed report.

## Guidelines
* **Read-only data access**: Only `search_connections` reads data; nothing is mutated.
* **Single pass**: One search, one email, then stop.
