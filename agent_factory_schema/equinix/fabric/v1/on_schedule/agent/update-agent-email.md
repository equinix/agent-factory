---
name: update-agent-email
description: Scans all agent configuration prompts for an email address and replaces it with a new one, then reports what changed.
categories: ["Deploy & Change Agents"]
---

# Agent Email Update Agent

## Overview
An Equinix agent that scans every agent's configuration prompt for a specified email address and replaces it with a new one.
It validates both email addresses before making any changes, reports exactly which agents were updated and which failed, and runs once immediately.

## Capabilities
- Validate old and new email addresses before making any changes
- Scan all agent configuration prompts across the account
- Replace every occurrence of the old email with the new email in each matching prompt
- Report a change summary: how many agents were scanned, matched, updated, and failed
- Log all actions and decisions

## Prerequisites
- You must have operator-level or higher access to the Fabric account
- Both the old and new email addresses must be valid email format
- The old email must appear in at least one agent's configuration prompt for any changes to occur

## Available Tools
This skill can use the following tools:

* **`update_agent_email`**: Scans all agent configuration prompts for `old_email`, replaces every occurrence with `new_email`, and returns a JSON change report with fields: `scanned` (total agents checked), `matched` (agents containing the old email), `updated` (agents successfully patched), `failed` (list of `{uuid, error}` for agents that could not be patched), and `changes` (list of `{uuid, name}` for successfully updated agents).

## Instructions
1. Extract `old_email` and `new_email` from the Configuration. Both are required; stop and notify the user if either is missing or not a valid email format.
2. Call `update_agent_email` with `old_email` and `new_email`.
3. Parse the returned JSON report.
4. If `matched` is 0, inform the user that no agents contained the old email address — no changes were made.
5. If `updated` is greater than 0, report the list of updated agents by name and UUID.
6. If `failed` is non-empty, report each failed agent UUID and the associated error so the user can investigate manually.
7. Summarise the outcome: total scanned, total matched, total updated, total failed.

## Guidelines
* **Validate first**: Do not call `update_agent_email` if either email address is missing or malformed. Inform the user immediately.
* **Report failures clearly**: If some agents failed to patch, list them explicitly rather than reporting a partial success as a full success.
* **No retries**: This is a single-attempt operation. Do not retry failed agents automatically.
* **Read-back not required**: The tool patches and confirms in one call. Do not re-fetch agents to verify the change.
* **Token efficiency**: `update_agent_email` handles all pagination and patching internally. Make exactly one tool call.

## Configuration
* **`old_email`**: `<email address>` — Required — The email address to search for across all agent prompts.
* **`new_email`**: `<email address>` — Required — The replacement email address.
