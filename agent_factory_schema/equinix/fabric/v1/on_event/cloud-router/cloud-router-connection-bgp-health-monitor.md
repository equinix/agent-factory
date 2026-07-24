---
name: cloud-router-connection-bgp-health-monitor
description: Reacts to a Fabric Cloud Router connection's native BGP session status event, waits to see if the session recovers on its own (BGP is a self-healing protocol), and — only if it does not recover within a grace period — attempts a single narrow-scope soft restart of the session before emailing an incident report with the outcome and a recommended next step if it did not resolve.
---

# Cloud Router Connection BGP Session Restart Agent

## Overview
An Equinix agent that reacts to a Fabric Cloud Router connection's BGP session status event — a native Equinix Fabric cloud event fired directly by the platform on every BGP session state transition, with no customer-configured alert rule required. Because BGP is a self-healing protocol (a session's finite-state machine continuously retries the connection on its own), this agent first waits and observes for a bounded grace period rather than acting immediately: most transient session drops resolve without any external intervention. Only if the session is still down after that grace period does the agent attempt a single automated remediation step: a soft restart of the affected BGP session (disable, then re-enable). It also rules out two situations where restarting would be wrong or pointless before ever reaching that point — a session still completing its initial provisioning, and a session an operator has intentionally left disabled. It emails an incident report in every case.

This agent performs exactly one remediation tier: a single enabled-flag toggle, attempted only after the grace period. The underlying routing protocol PATCH API supports no other remediation operation — there is no distinct "graceful restart", "peer reset", or "failover to a secondary path" call available to this agent. Because this agent has no visibility into the customer's own router, a restart can only help two narrow cases: the local (Equinix-side) session state is stuck, or the session is waiting out a retry backoff after the underlying issue already cleared — it cannot fix a fault that genuinely lives on the downstream/customer side. If the single restart attempt does not restore the session, the report recommends manual escalation instead of attempting anything further.

## Capabilities
- Detect a Fabric Cloud Router connection's BGP session status event and read the reported session state directly from the event `type`
- Ignore events reporting a healthy (`established`) transition — only act on a session leaving the established state
- Wait and observe for a bounded grace period to give BGP's own self-healing retry a chance before considering any restart
- Distinguish a genuine post-provisioning session flap from a session still completing initial provisioning
- Recognize and skip a session an operator has intentionally administratively disabled, rather than forcing it online
- Detect a flap storm (repeated recent session-status events for the same session) and escalate instead of repeatedly auto-restarting an unstable session
- Attempt one soft BGP session restart via the routing protocol's `enabled` flag (disable, then re-enable) — only after the session fails to recover on its own
- Verify whether the session returns to the `UP` operational state after the restart, within a bounded polling budget
- Email an incident report with the action taken (or the reason no action was taken) and the outcome
- Log all actions and decisions

## Prerequisites
- The connection must have a BGP routing protocol. BGP session health is a property of a connection's routing protocol, which only exists for Fabric Cloud Router (FCR)-backed connections — connections without a BGP routing protocol are out of scope for this agent.
- This agent is triggered directly by the platform's native `equinix.fabric.connection_bgpipv4_session.status.*` and `equinix.fabric.connection_bgpipv6_session.status.*` cloud events. These are fired automatically by Equinix Fabric on every BGP session state transition — no customer-configured stream or alert rule is required for them to exist.
- The connection's BGP routing protocol is expected to reach `PROVISIONED` state on its own during initial setup; this agent does not perform initial BGP provisioning and takes no action on a session that has not yet reached that state.

## Available Tools
This skill can use the following tools:

*   **`search_connections`**: Confirms the connection exists and reads its current state before acting.
*   **`list_routing_protocols`**: Reads the connection's routing protocols, including each BGP address family's `enabled` flag and `operation.operationalStatus`/`operation.sessionStatus`/`operation.opStatusChangedAt` (when present), and the routing protocol's own `state` (e.g. `PROVISIONED`). Used for the initial live check, the self-heal observation poll, and the post-restart recovery poll.
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"30m"`). Used to build the lookback window for the flap-storm check.
*   **`search_cloud_events`**: Searches Equinix Fabric cloud events by type, subject, and time range. Used to count recent BGP session status events for this session before remediating, to detect a flap storm.
*   **`update_routing_protocol`**: Updates a routing protocol via JSON Patch. Limited to toggling `/bgpIpv4/enabled` or `/bgpIpv6/enabled` — this is the only remediation lever this agent has, and is how the soft restart is performed.
*   **`wait`**: Waits for a specified number of milliseconds. Used during the self-heal grace period, between disabling and re-enabling the session, and between post-restart recovery-verification poll attempts.
*   **`send_email_notification`**: Sends the incident report as an email with an attached PDF.

## Instructions
1. Upon receiving the cloud event, parse the alerted BGP address family and the reported session state from the event `type`, which is of the form `equinix.fabric.connection_bgpipv4_session.status.<state>` or `equinix.fabric.connection_bgpipv6_session.status.<state>` (`<state>` may be `idle`, `active`, `connect`, `opensent`, `openconfirm`, `shutdown`, `closing`, `established`, or any other value the platform reports). Stop if the event type matches neither pattern — this agent only handles BGP session status events.
2. If `<state>` is `established` (case-insensitive), the session is healthy — this event reports a normal bring-up or recovery transition, not an incident. Log and stop; do not send an email. **Every other reported state is in scope for this agent** — there is nothing idle-specific about this check; any non-`established` transition continues to Step 3.
3. Resolve the connection UUID and the routing protocol UUID. If `connection_uuid` is configured (a manual override, useful for testing), use it and resolve `routing_protocol_uuid` in Step 5. Otherwise parse both from the event's `/subject`, which is of the form `/fabric/v4/connections/{connectionUuid}/routingProtocols/{routingProtocolUuid}`. Stop if a connection UUID cannot be determined either way.
4. Call `search_connections` for the resolved connection UUID to confirm it exists and read its current state. Stop and log if the connection cannot be found. If the connection is in a terminal or deprovisioning state, stop — do not attempt to restart BGP on a connection that is being torn down.
5. Call `list_routing_protocols` for the connection - this is the authoritative, live re-check; do not rely solely on the event's own payload, which may be stale by the time this step runs. From the returned items, find the one matching `routing_protocol_uuid` from Step 3 (or, if that was not available from the subject, the item with `type = BGP`). Stop and log if none is found - the triggering event may be stale, or the routing protocol may since have been deleted. From that item, capture:
   - `routing_protocol_uuid` = the item's `uuid` (needed for Step 9).
   - `routing_protocol_state` = the item's top-level `state`.
   - From the address-family block identified in Step 1 (`bgpIpv4` or `bgpIpv6`): `enabled`, `operation.operationalStatus`, `operation.sessionStatus` (if present), and `operation.opStatusChangedAt` (if present) — for the report.
6. Apply the following checks **in order**. The first one that matches ends the run at that point, without remediation and without sending an email:
   - **Still provisioning**: if `routing_protocol_state` is not `PROVISIONED`, this session has not completed initial bring-up yet. A non-`UP` status here is the expected starting state, not a flap. Log and stop.
   - **Administratively disabled**: if `routing_protocol_state` is `PROVISIONED` but the address family's `enabled` is `false`, an operator has intentionally turned this session off. Do not enable it automatically. Log and stop.
   - **Already healthy**: if `routing_protocol_state` is `PROVISIONED`, `enabled` is `true`, and `operationalStatus` is already `UP`, the session recovered on its own before this agent ran (the event may be stale by the time it was processed). Log and stop.

   If none of the above apply — `routing_protocol_state` is `PROVISIONED`, `enabled` is `true`, and `operationalStatus` is anything other than `UP` — this is a genuine post-provisioning session flap. Continue to Step 7.
7. **Check for a flap storm before doing anything further.** A session that has already reported status changes repeatedly in a short window is unstable in a way neither waiting nor a restart is likely to resolve:
   - Call `get_timestamps` with `flap_storm_lookback_window` (default `"30m"`) to get `from`/`to`.
   - Call `search_cloud_events` with `pagination.limit = 1` (only the count is needed) and a filter of:
     `{"and": [{"property": "/subject", "operator": "LIKE", "values": ["/fabric/v4/connections/<connection_uuid>/routingProtocols/<routing_protocol_uuid>*"]}, {"property": "/type", "operator": "IN", "values": ["equinix.fabric.connection_<family>_session.status.*"]}, {"property": "/time", "operator": "BETWEEN", "values": [from, to]}]}`, where `<family>` is `bgpipv4` or `bgpipv6` per Step 1.
   - Read `recent_flap_count` from the response's `pagination.total`. This counts every status-transition event for this session in the window, including brief `established` recoveries — still a valid instability signal, since a session bouncing between states repeatedly is unstable regardless of which states it bounces through.
   - If `recent_flap_count >= flap_storm_threshold` (default `3`), this is a flap storm: **skip Step 8, Step 9, and Step 10 entirely** (neither waiting nor restarting is likely to help) and go directly to Step 11 to report the storm and recommend escalation.
   - Otherwise, continue to Step 8.

   This is a windowed count on each run, not a persistent circuit breaker — it depends on prior events already being indexed and searchable, so treat `flap_storm_threshold` as a strong deterrent, not an exact guarantee. See Guidelines.
8. **Wait and observe for natural recovery (self-heal grace period).** BGP is a self-healing protocol — once a session is `enabled`, its state machine continuously retries the connection on its own, without any external action. Give it a chance before touching anything:
   - Repeat for up to `self_heal_grace_period` (default `3m`) total: call `wait` for `self_heal_poll_interval_ms` (default `20000`) milliseconds, then call `list_routing_protocols` again and read the address family's `operation.operationalStatus`.
   - Stop this loop as soon as `operationalStatus` is `UP`, or once `self_heal_grace_period` is exhausted, whichever comes first.
   - If it recovered on its own: record outcome `Self-Recovered — No Action Taken`. **Skip Step 9 and Step 10 entirely** — no restart is needed — and go directly to Step 11 to report it.
   - If it is still not `UP` once the grace period is exhausted: continue to Step 9.

   These defaults give the session at least one natural retry cycle to recover on its own; they are a reasonable starting point, not a value derived from a documented Equinix retry-timer specification — tune per observed behavior.
9. **Attempt one soft restart.** By this point the session has been confirmed as a genuine, non-flap-storm, post-provisioning flap (Steps 6–7); if the self-heal grace period (Step 8) is active, it will also have had a full chance to recover on its own without success. This restart is a narrow-scope nudge for a possibly-stuck *local* (Equinix-side) session state — it is not an attempted fix for a fault on the downstream/customer side, which this agent has no visibility into and cannot diagnose. The routing protocol PATCH API supports only toggling the `enabled` flag, so the restart is performed as disable, then re-enable:
   - Call `update_routing_protocol` with `connection_uuid`, `routing_protocol_uuid` (from Step 5), and `operations = [{"op": "replace", "path": "/<family>/enabled", "value": false}]`, where `<family>` is `bgpIpv4` or `bgpIpv6` per Step 1.
   - Call `wait` for `restart_toggle_wait_ms` (default `5000`) milliseconds to let the disable take effect.
   - **Confirm the routing protocol has settled before re-enabling.** Disabling briefly puts the routing protocol into a transient (non-`PROVISIONED`) state (e.g. reprovisioning) while the change is applied; calling re-enable while it is still in that transient state can be rejected. Repeat for up to `restart_reenable_max_wait_ms` (default `20000`) total: call `list_routing_protocols` again and read `routing_protocol_state` for this routing protocol. Stop this poll loop as soon as `routing_protocol_state` is `PROVISIONED`, or once the budget is exhausted, whichever comes first; if not yet exhausted and still not `PROVISIONED`, call `wait` for `restart_reenable_poll_interval_ms` (default `5000`) milliseconds and check again.
   - Call `update_routing_protocol` again with the same `connection_uuid`/`routing_protocol_uuid`, this time `operations = [{"op": "replace", "path": "/<family>/enabled", "value": true}]`. If the settle-check budget was exhausted while `routing_protocol_state` was still not `PROVISIONED`, attempt this call anyway (it is the only lever this agent has) and note in the report that the routing protocol had not fully settled when re-enable was attempted. If this call itself fails, follow the Error Handling guideline: log and stop.

   This agent performs exactly **one** restart attempt per invocation. It does not retry the toggle, does not perform a peer reset, and does not fail over to a secondary path — see Guidelines.
10. **Verify recovery.** Repeat up to `recovery_poll_attempts` (default `5`) times: call `wait` for `recovery_poll_interval_ms` (default `10000`) milliseconds, then call `list_routing_protocols` again and read the address family's `operation.operationalStatus`. Stop polling as soon as `operationalStatus` is `UP`, or once the attempt budget is exhausted, whichever comes first — this keeps the step within a bounded execution budget. Record the final `operationalStatus`, whether the session recovered, and how many poll attempts it took (or that it did not recover within the budget). This polling loop is not a halt point — it always falls through to Step 11 regardless of the outcome.
11. **Compose the incident report** using the HTML report block below, then call `send_email_notification` with `recipient_email_addresses`:
    - `pdfContent`: the composed report (populate every section from the data gathered above; skip a section only if it genuinely has no data).
    - `body`: a one-paragraph summary — connection UUID, address family, action taken (self-recovered, restarted, or skipped due to a flap storm), and outcome.
    - `pdfTitle`: `BgpSessionRestart_<connection_uuid>_<Restored|NotRestored|Skipped|SelfRecovered>`

    ```
    <div class="header">
        <h1>BGP Session Restart Incident Report</h1>
    </div>

    <div class="section">
        <h2>Alert Summary</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Session Before Restart</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Restart Action Taken</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Session After Restart</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Outcome</h2>
        <div class="content">
        </div>
    </div>

    <div class="section">
        <h2>Recommended Next Step</h2>
        <div class="content">
        </div>
    </div>
    ```

    Section content rules:
    - **Alert Summary**: connection UUID, address family (`bgpIpv4`/`bgpIpv6`), the reported session state from the event `type` in Step 1 (e.g. `idle`), the event's `message` and `severitytext` if present, and — when Step 7 ran — `recent_flap_count` and `flap_storm_lookback_window`.
    - **Session Before Restart**: `routing_protocol_state`, `enabled`, `operationalStatus`, `sessionStatus` (if present), and `opStatusChangedAt` (if present) as read in Step 5.
    - **Restart Action Taken**: if the session self-recovered (Step 8), state plainly that no restart was attempted since the session recovered on its own during the grace period. If skipped due to a flap storm (Step 7), state that plainly and give `recent_flap_count` vs `flap_storm_threshold`. Otherwise, the two `update_routing_protocol` calls made in Step 9, the wait applied between them, and — if the settle-check budget was exhausted before `routing_protocol_state` returned to `PROVISIONED` — note that re-enable was attempted while the routing protocol had not fully settled.
    - **Session After Restart**: if a restart was attempted, the final `operationalStatus` from Step 10 and how many poll attempts it took (or that the poll budget was exhausted). If self-recovered or skipped, state that this section does not apply.
    - **Outcome**: `Restored`, `Not Restored`, `Skipped — Flap Storm`, or `Self-Recovered — No Action Taken`, stated plainly.
    - **Recommended Next Step**:
      - `Self-Recovered — No Action Taken`: state that no further action is required; the session recovered on its own without intervention.
      - `Restored`: state that no further action is required at this time.
      - `Not Restored`: recommend manual escalation to network engineering for a peer-side reset or, if a secondary path exists for this connection, a manual failover — state explicitly that this agent does not perform either of those itself, and note that since neither the self-heal grace period nor the restart resolved it, the issue most likely lies on the connection's downstream/peer side, which this agent cannot see or fix.
      - `Skipped — Flap Storm`: recommend manual escalation to network engineering rather than continued automated restarts, since the repeated events indicate an issue neither waiting nor a single soft restart is likely to fix.

    Once the email has been sent, this agent's run for this alert is complete. Take no further action until the next cloud event triggers a new run.

## Guidelines
*   **This agent runs unattended — never ask a clarifying question.** It receives everything it needs (the triggering cloud event and the Configuration parameters) at invocation time; there is no human available to respond mid-run. If required data is not present in this invocation — the event's `type`/`subject` are missing and no `connection_uuid` override was configured, for example — follow the stop condition in the relevant step exactly: log clearly what was missing and stop. Do not pause the run to ask the user to supply it.
*   **Single remediation attempt only, and only as a last resort**: this agent performs exactly one disable/re-enable cycle per invocation, and only after the session has neither already been identified as a flap storm (Step 7) nor recovered on its own during the grace period (Step 8). It never retries the toggle within a run, and it never performs a peer reset or a failover — those are not operations this agent has available, and are surfaced only as a recommendation for a human in the report.
*   **A restart cannot fix a downstream fault**: this agent has no visibility into the customer's own router. A restart only helps two narrow cases — a stuck local (Equinix-side) session state, or skipping a retry backoff after the underlying issue already cleared. BGP's own self-healing retry is given the first chance (Step 8) precisely because a restart is not expected to help in most other cases, and bouncing a session that the peer side is already mid-recovering could interrupt that recovery instead of helping it.
*   **Flap-storm protection, not perfect deduplication**: there is no durable state store available in this environment, so this agent cannot maintain a persistent circuit breaker across runs. Instead, Step 7 counts recent status-transition events for the same session via `search_cloud_events` over `flap_storm_lookback_window`, each time it runs. If the count meets or exceeds `flap_storm_threshold`, it skips straight to escalating instead of continuing to act on an unstable session. This is windowed counting per run, not an exact guarantee — it depends on cloud events being indexed and searchable by the time this agent queries them.
*   **Do not override operator intent**: a session with `enabled=false` was deliberately turned off by an operator (Step 6). This agent never flips it back on automatically.
*   **Do not act on in-progress provisioning**: a routing protocol not yet in `PROVISIONED` state is expected to start non-`UP` (Step 6). This agent only remediates sessions that were previously healthy and later flapped.
*   **Scope — FCR-backed connections only**: BGP session health is read from the connection's routing protocol, which only exists on FCR-backed connections. Connections without a BGP routing protocol never reach this agent, since the triggering event itself is BGP-session-specific.
*   **Error Handling**: if a tool call fails, log the error with its context and stop; do not attempt further remediation on the same run.
*   **Token Efficiency**: only call the tools when all necessary parameters are known, avoiding unnecessary context loading.

## Configuration
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the incident report.
* **`connection_uuid`**: < A connection UUID > - Optional. Manual override for the connection to act on; useful for testing. If omitted (the default), both the connection and its routing protocol are resolved from the triggering event's `/subject`.
* **`flap_storm_lookback_window`**: < A duration string, e.g. "30m" > - Optional. Default `30m`. The recent window used to count prior BGP session status events for this session before proceeding (Step 7).
* **`flap_storm_threshold`**: < An integer > - Optional. Default `3`. If this many or more status-transition events for the same session are found within `flap_storm_lookback_window` (Step 7), the agent skips both the grace period and the restart and escalates instead.
* **`self_heal_grace_period`**: < A duration string, e.g. "3m" > - Optional. Default `3m`. How long to wait and observe for the session to recover on its own before attempting a restart (Step 8).
* **`self_heal_poll_interval_ms`**: < An integer > - Optional. Default `20000`. Milliseconds between recovery checks during the self-heal grace period (Step 8).
* **`restart_toggle_wait_ms`**: < An integer > - Optional. Default `5000`. Initial milliseconds to wait after disabling the BGP session, before checking whether it has settled, in Step 9.
* **`restart_reenable_max_wait_ms`**: < An integer > - Optional. Default `20000`. Maximum additional milliseconds to poll for the routing protocol to leave its transient post-disable state and return to `PROVISIONED` before re-enabling the session in Step 9.
* **`restart_reenable_poll_interval_ms`**: < An integer > - Optional. Default `5000`. Milliseconds between settle-check polls while waiting for the routing protocol to return to `PROVISIONED` in Step 9.
* **`recovery_poll_attempts`**: < An integer > - Optional. Default `5`. Maximum number of recovery-verification poll attempts in Step 10.
* **`recovery_poll_interval_ms`**: < An integer > - Optional. Default `10000`. Milliseconds to wait between recovery-verification poll attempts in Step 10.
