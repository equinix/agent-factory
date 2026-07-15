---
name: test-poll-router-command
description: Poll a Fabric Cloud Router command until it is no longer pending, then email the result.
---

# Poll Router Command Agent

## Overview
A minimal agent that polls an existing Fabric Cloud Router command until it leaves the pending
state, then emails the final result. This agent runs once immediately by default.

## Instructions
1. Poll the router's commands using `search_router_commands` with the router uuid, limit 1. Repeat
   up to 5 times, waiting 10000 milliseconds between attempts, until the command is no longer in a
   PENDING or INITIATED state.
2. Send an email notification with the final command result using `send_email_notification`.

## Available Tools
*   **`search_router_commands`**: Search for commands (e.g. PING) on a Fabric Cloud Router by uuid.
*   **`send_email_notification`**: Sends an email notification given email addresses and a body.

## Guidelines
- Poll only; do not create anything. If the command is still pending after the attempts, email the
  last observed result anyway.

## Configuration
* **`router_uuid`**: < A router UUID > - Required.
* **`recipient_email_addresses`**: < A list of email addresses > - Required.
