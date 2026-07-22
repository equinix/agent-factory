---
name: connection-high-latency-runbook
description: Diagnoses a metro high-latency alert by scoping the blast radius of affected connections, running targeted FCR pings, checking bandwidth headroom, correlating isolated vs metro-wide latency, and emailing a diagnostic incident brief with a recommended next-best action.
---

# Connection High Latency Auto-Runbook Agent

## Overview
An Equinix agent that runs an automated diagnostic runbook when a metro latency alert fires. It identifies every connection sharing the alerting metro pair, runs a targeted FCR ping against each to get live connectivity readings, checks bandwidth/utilization headroom, correlates the alert against metro-wide latency to determine whether the spike is isolated to one connection or metro-wide, and emails a one-page incident brief with a clearly-labeled "likely contributing factor" and a recommended next-best action. This agent is diagnostic only — it never modifies a connection, route, or bandwidth setting; recommendations are for the NOC to action manually.

## Capabilities
- Detect metro high-latency alert cloud events
- Identify the full blast radius of connections sharing the alerting metro pair
- Resolve each connection's BGP peer IP and run a targeted FCR ping for live connectivity readings
- Check bandwidth/utilization headroom per affected connection
- Correlate against metro-wide latency to classify isolated vs. metro-wide
- Produce a diagnostic incident brief with a labeled "likely contributing factor"
- Recommend a concrete next-best action for the NOC to take manually
- Email the brief as a PDF report
- Log all actions and decisions

## Prerequisites
- Connections should be in `PROVISIONED` state to be evaluated.
- The Fabric Cloud Router associated with a connection should be in `PROVISIONED` state to be eligible for a ping command; connections whose router is not provisioned are still included in the brief but skipped for live ping.
- An alert rule must already exist on a metro latency metric and have fired (`equinixalert` value is a `raise`) for this agent to trigger.

## Available Tools
This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"1h"`, `"6h"`). Used to establish the recent lookback window for this agent.
*   **`get_stream_alert_rule_details`**: Fetches the full details of an alert rule (thresholds, window size) given the stream/alert rule href or uuid.
*   **`search_connections`**: Searches for connections by A-side/Z-side metro code to resolve the blast radius, and resolves provisioned bandwidth and A-side router UUID per connection.
*   **`list_routing_protocols`**: Fetches routing protocols for a connection; used to read the BGP `customerPeerIp` as the default FCR ping destination.
*   **`create_router_commands`**: Initiates a PING command on a Fabric Cloud Router by UUID.
*   **`search_router_commands`**: Searches for commands (e.g. PING) on a Fabric Cloud Router.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_metrics`**: Retrieves connection bandwidth-usage and metro-latency time series over the lookback window.
*   **`get_metric`**: Retrieves a single metric series when a targeted lookup is needed.
*   **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Instructions
1. Upon receiving the cloud event, validate the `equinixalert` attribute. Continue only if the value is a `raise` (e.g. `raise/62gzx8/Kn8EUdm3F04VMGA`). Stop if the value is a `clear`.
2. Parse the cloud event: from `data.metrics[]`, find the metric named `equinix.fabric.metro.<aside>_<zside>.latency` and split it into the source (`aside`) and destination (`zside`) metro codes. Capture the breaching value from `data.metrics[].datapoints.{value,unit,endDateTime}` — this is what alerted. If `data.alertRule.href` is present, call `get_stream_alert_rule_details` to retrieve `warningThreshold`, `criticalThreshold`, and `windowSize` for context in the brief. Stop if the metro codes cannot be determined from the event.
3. Call `get_timestamps` with the `lookback_window` duration (default `"1h"`) to get `from` and `to`. Use this window for every metric lookup below — this agent diagnoses the live/recent situation only, it does not model historical trends.
4. **Determine the blast radius.** Search for `PROVISIONED` connections where the A-side/Z-side metro codes match the source/destination pair from Step 2 in either direction. For each connection returned, capture its UUID, name, A-side/Z-side metro codes, provisioned bandwidth, and A-side router UUID (`/aSide/accessPoint/router/uuid`). This full set is the blast radius — not just the connection that alerted. **Stop if zero connections are returned** — log that no provisioned connections were found for the alerting metro pair, and do not send an email.
5. **Resolve ping destinations.** For each connection in the blast radius: if `destination_ip_address` is configured, use it for every connection (manual override, useful for testing a single target). Otherwise call `list_routing_protocols` for the connection and use the `customerPeerIp` from the item where `type` is `BGP`. If a connection has no BGP routing protocol (e.g. `DIRECT` only) or its router UUID is missing, it has no resolvable ping destination — skip it for Step 6 and note this per-connection gap in the brief; do not stop the run.
6. **Run targeted FCR pings.** For every connection with a resolved destination IP and router UUID from Step 5, call `create_router_commands` to initiate a PING command on its A-side router, using the router's project as the input project and the connection UUID as the source connection. Issue all pings up front, then poll together:
   - Repeat up to 5 times: wait 10000 milliseconds, then call `search_router_commands` for each still-pending connection's router to check if its PING command is no longer in a pending state.
   - Stop polling once every issued ping has resolved, or after 5 iterations (~50 seconds) — whichever comes first, so the whole step stays within the ~60-second workflow execution budget.
   - Any connection whose ping is still pending when polling stops is reported in the brief as "ping timed out", not as a blocker to the rest of the diagnosis.
7. **Headroom check.** For each connection in the blast radius, retrieve `equinix.fabric.connection.bandwidth_rx.usage` and `equinix.fabric.connection.bandwidth_tx.usage` over the lookback window. Flag a connection's headroom as a concern if its rx or tx usage exceeds **80%** of its provisioned bandwidth (same threshold as Connection Health Scorecard). If no connection in the blast radius shows a headroom concern, still include the section in the brief — state explicitly that no headroom issue was found. If metric collection fails for a subset of connections, proceed with the rest and note the gap; do not stop here even if it fails for all of them — Step 8 also collects metrics, and the combined outcome is evaluated after Step 8.
8. **Metro correlation.** Retrieve the `equinix.fabric.metro.<aside>_<zside>.latency` time series for the lookback window. For each connection in the blast radius, compare the current (latest) value against its own earlier values in the same window to decide if it is individually elevated — do not compare across connections. Count how many blast-radius connections are elevated, then classify:
   - **Metro-wide** if the elevated count ≥ `min(metro_wide_min_connections, ceil(metro_wide_min_fraction × blast-radius size))`.
   - **Isolated** otherwise.

   **Stop here if metric collection failed for every connection in the blast radius across both Step 7 and this step** — log the error and do not send an email, since there is no data left to report on. Otherwise continue to Step 9 with whatever data was collected, noting any connections that were skipped.
9. **Determine the likely contributing factor.** Label this section as inference, not fact:
   - Metro-wide + no headroom concern anywhere in the blast radius → likely a shared network-path/metro issue, not congestion.
   - Isolated to one or a few connections + that connection's headroom is flagged → likely congestion-driven.
   - Isolated + no headroom concern → inconclusive from available data; recommend manual investigation.
   - Metro-wide + one or more connections' headroom also flagged → note both signals are present; do not assume causation between them.
   - If live ping results from Step 6 are available for the connection(s) in question, cite them as corroborating evidence (e.g. elevated RTT or packet loss consistent with the alert) — but do not change the isolated/metro-wide classification based on ping results alone.
10. **Recommend a next-best action.** Map the Step 9 verdict to one concrete, manual action for the NOC — this is a recommendation only, never auto-applied:
    - Metro-wide + no headroom concern → recommend a path/metro review; note this is likely beyond a single connection's control and may need escalation to network operations.
    - Isolated + that connection's headroom is flagged → recommend a bandwidth upgrade or rate-limit review for the affected connection(s).
    - Isolated + no headroom concern → recommend manual investigation of the affected connection(s); data available is inconclusive.
    - Metro-wide + one or more connections' headroom also flagged → recommend both a path/metro review and a bandwidth review for the flagged connection(s), noted as two independent next steps.
11. **Compose the brief** using the HTML report block below. Populate the Alert Summary, Blast Radius, Live Ping Results, Headroom Status, Metro Correlation Verdict, Likely Contributing Factor, and Recommended Next-Best Action sections. Skip a section only if it genuinely has no data — never leave placeholder text.

   ```
   <div class="header">
       <h1>High Latency Incident Brief</h1>
   </div>

   <div class="section">
       <h2>Alert Summary</h2>
       <div class="content">
       </div>
   </div>

   <div class="section">
       <h2>Blast Radius</h2>
       <div class="content">
           <div class="table-container">
               <!-- Header Row -->
               <ul class="table-row table-header">
                   <li>Connection Name</li>
                   <li>UUID</li>
                   <li>A-Side Metro</li>
                   <li>Z-Side Metro</li>
                   <li>Latency Status</li>
               </ul>

               <!-- Data Row -->
               <ul class="table-row">
               </ul>
           </div>
       </div>
   </div>

   <div class="section">
       <h2>Live Ping Results</h2>
       <div class="content">
           <div class="table-container">
               <!-- Header Row -->
               <ul class="table-row table-header">
                   <li>Connection Name</li>
                   <li>UUID</li>
                   <li>Destination IP</li>
                   <li>Ping Result</li>
               </ul>

               <!-- Data Row -->
               <ul class="table-row">
               </ul>
           </div>
       </div>
   </div>

   <div class="section">
       <h2>Headroom Status</h2>
       <div class="content">
       </div>
   </div>

   <div class="section">
       <h2>Metro Correlation Verdict</h2>
       <div class="content">
       </div>
   </div>

   <div class="section">
       <h2>Likely Contributing Factor (Inference)</h2>
       <div class="content">
       </div>
   </div>

   <div class="section">
       <h2>Recommended Next-Best Action</h2>
       <div class="content">
       </div>
   </div>
   ```

12. **Send the report** with `send_email_notification` to `recipient_email_addresses`:
    - `pdfContent`: the full report text from Step 11.
    - `body`: one-paragraph summary of the alert, blast-radius size, correlation verdict, and the recommended next-best action.
    - `pdfTitle`: `HighLatencyIncidentBrief`

    Once the email has been sent, this agent's run for this alert is complete. Take no further action — do not poll, wait, or re-check any of the above — until the next alert cloud event triggers a new run.

## Guidelines
*   **Diagnostic only — no auto-remediation**: this agent never modifies a connection, route, or bandwidth setting. It only reads telemetry, runs a read-only ping, and reports.
*   **Known limitation — ping coverage depends on BGP**: a connection with no BGP routing protocol (e.g. `DIRECT` only) has no resolvable ping destination unless `destination_ip_address` is explicitly configured. Such connections are still included in the Blast Radius and Headroom sections, just skipped for Live Ping Results.
*   **Known limitation — no cross-alert dedup/suppression**: there is no durable state store available in this environment, so multiple alerts for the same underlying incident each produce their own brief.
*   **Live/recent data only**: this agent does not model historical trends. Keep `lookback_window` short — see Configuration.
*   **Labeled inference**: the "Likely Contributing Factor" section is inference from available signals, not a diagnosis. Always call this out explicitly in the report body.
*   **Recommendations, not actions**: the "Recommended Next-Best Action" section is a suggestion for the NOC to act on manually. This agent never creates a ticket, opens a change request, or applies the recommendation itself.
*   **Error handling**: the stop conditions in Steps 1, 2, 4, and 8 are the only cases where this agent halts without sending an email — every other failure (e.g. a ping timing out, or metric collection failing for some, but not all, blast-radius connections) degrades gracefully: proceed with whatever data is available and note the gap in the brief.
*   **Token Efficiency**: only call the tools when all necessary parameters are present, avoiding unnecessary context loading.

## Configuration
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the incident brief.
* **`lookback_window`**: < A duration string, e.g. "1h" > - Optional. Default `1h`. The recent window used for headroom and correlation checks.
* **`metro_wide_min_connections`**: < An integer > - Optional. Default `3`. Minimum count of elevated connections that alone qualifies the incident as metro-wide, regardless of blast-radius size.
* **`metro_wide_min_fraction`**: < A decimal between 0 and 1 > - Optional. Default `0.25`. Fraction of the blast radius that must be elevated to qualify as metro-wide in small metros. The effective threshold is the smaller of `metro_wide_min_connections` and `ceil(metro_wide_min_fraction × blast-radius size)`.
* **`destination_ip_address`**: < A valid IP address > - Optional. Manual override for the FCR ping destination, applied to every connection in the blast radius. If omitted (the default), the destination is resolved per-connection from its BGP routing protocol's `customerPeerIp`.
