---
name: graph-seq-smoke
description: SEQUENTIAL counterpart of the DAG smoke — same task (search connections, compose a short report, email it) but LLM-driven with no Steps graph.
---

# SEQUENTIAL runtime smoke agent

## Overview
The SEQUENTIAL (default, LLM/ReAct-driven) counterpart of `graph-dag-smoke-v1`. Same
task and same tools, but with no `execution_mode` and no `## Steps` block, so the engine
runs it on the default SEQUENTIAL path where the LLM decides tool order. Used to compare
SEQUENTIAL vs DAG execution for the identical workload.

## Instructions
1. Call `search_connections` once to list Fabric virtual connections (read-only).
2. Compose a short plain-English health summary of what was found (one short paragraph).
3. Email that summary using `send_email_notification` with `emailAddress` =
   `ckuo@equinix.com` and `body` = the summary text.
4. Do not create, update, or delete anything. Stop after sending one email.

## Available Tools
This skill can use the following tools:

* **`search_connections`**: Searches Fabric virtual connections (read-only).
* **`send_email_notification`**: Sends an email. Pass `emailAddress` and `body`.

## Guidelines
* **Read-only data access**: Only `search_connections` reads data; nothing is mutated.
* **Single pass**: One search, one email, then stop. Do not loop.

## Configuration
* (none) — recipient is fixed to ckuo@equinix.com in the instructions.
