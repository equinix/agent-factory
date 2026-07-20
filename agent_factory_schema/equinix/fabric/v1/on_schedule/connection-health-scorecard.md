---
name: connection-health-scorecard
description: Scores and ranks the health of Fabric connections (rate-exceeded packet drops, packet errors, utilization, latency) and emails a prioritized remediation scorecard.
---

# Connection Health Scorecard Agent

## Overview
This agent gives operators a single-pane health view across Equinix Fabric connections. It collects per-connection performance metrics, computes a composite 0–100 health score for each connection, ranks them, flags any connection with an obvious measurable issue, and recommends remediation for every flagged connection — so troubleshooting effort can be prioritized where it matters most. The result is delivered as a PDF scorecard via email.
This agent runs once immediately by default unless scheduled by user.

## Prerequisites
- Connections should be in `PROVISIONED` state to be scored.
- Metric data is only available for connections that have been live over the scoring window; freshly provisioned connections with no metrics are skipped.

## Capabilities
- Enumerate all PROVISIONED connections (or a user-specified subset)
- Collect rate-exceeded packet drops, packet errors, utilization, and latency metrics per connection
- Compute a reproducible composite 0–100 health score per connection
- Rank all connections and flag any with an obvious measurable issue
- Recommend concrete remediation for every flagged connection
- Deliver a prioritized scorecard as a PDF report via email

## Instructions

1. **Determine the metrics time window.** Convert `scoring_window` to a duration string (e.g. 24 hours -> "24h", 30 days -> "30d"; default to `"24h"`), then call `get_timestamps` with that duration. Save the returned `from` and `to` (ISO 8601 UTC) as the reporting window — use them with the `BETWEEN` operator on `/time` for every `search_metrics` / `get_metric` call in Step 3.

2. **Resolve the connection set.**
   - If `connection_uuids` is provided, score only those connections.
   - Otherwise, search for all PROVISIONED connections. Follow the request payload below (paginate with increasing `offset` until all results are retrieved):
   ```json
   {
     "filter": {
       "and": [
         { "property": "/operation/equinixStatus", "operator": "=", "values": ["PROVISIONED"] }
       ]
     },
     "pagination": { "offset": 0, "limit": 100 }
   }
   ```
   - For each connection, capture the **A-side port UUID**, **Z-side port UUID**, **A-side metro code**, **Z-side metro code**, and **provisioned bandwidth** from the connection details. These are needed to compute utilization against capacity and to look up inter-metro latency.

3. **Collect metrics per connection** over the `from`–`to` window from Step 1 using `search_metrics`, applying the `BETWEEN` operator on `/time`. Issue one call per resource; if a response is too large to process, split the metric names across multiple calls (e.g. drops in one call, utilization in another). Collect:
   - **Rate-exceeded packet drops** (connection): `equinix.fabric.connection.packets_dropped_rx_aside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_rx_zside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_tx_aside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_tx_zside_rateexceeded.count`. These count only packets dropped because traffic exceeded the connection's provisioned rate limit — this is **not** general packet loss.
   - **Utilization** (connection): `equinix.fabric.connection.bandwidth_rx.usage` and `equinix.fabric.connection.bandwidth_tx.usage` — use the inbound/outbound usage values against the provisioned bandwidth.
   - **Packet errors** (port): `equinix.fabric.port.packets_erred_rx.count` and `equinix.fabric.port.packets_erred_tx.count` on the A-side and Z-side ports. (A connection-level error metric is not exposed — see Guidelines.)
   - **Latency** (metro): `equinix.fabric.metro.<aside>_<zside>.latency` using the A/Z metro codes. Retrieve the **time series over the window** (not just the latest point) so the current value can be compared against this connection's own prior values.

4. **Compute a composite 0–100 health score** per connection as a weighted blend of normalized sub-scores, where 100 = perfect health. Use the following default weights so results are reproducible:

   | Component | Weight | Scoring rule                                                                                                                                                                                                                                                                |
   |-----------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
   | Rate-exceeded packet drops | 30%    | Zero drops over the window = 100. Score degrades as the drop count rises; any non-zero drops cap the sub-score below 100.                                                                                                                                                   |
   | Packet errors | 20%    | Zero errors (A+Z ports) = 100. Score degrades as the error count rises.                                                                                                                                                                                                     |
   | Utilization headroom | 30%    | 100 when rx/tx usage is well below capacity. Sub-score degrades as usage approaches capacity and drops sharply once usage exceeds **80%** of provisioned bandwidth.                                                                                                         |
   | Latency | 20%    | Compare the current (latest) latency value to this connection's own prior values over the window. Steady or improving latency scores near 100; a sustained rise above the connection's earlier baseline lowers the sub-score. Do **not** compare against other connections. |

   - The composite score is the weighted average of the available sub-scores.
   - **Missing components**: if a component has no data, exclude it and renormalize the remaining weights so they sum to 100%. Note any excluded component in the report.

5. **Rank** all scored connections from highest (healthiest) to lowest. **Flag** (a simple yes/no) every connection that has at least one obvious, measurable issue over the window:
   - Any non-zero rate-exceeded packet drops, OR
   - Any non-zero packet errors (A or Z port), OR
   - rx/tx usage above 80% of provisioned bandwidth, OR
   - A sustained rise in latency above the connection's own earlier baseline.
   A connection with none of these is not flagged.

6. **Recommend remediation for every flagged connection** (from Step 5), tied to the issue(s) present:
   - Rate-exceeded drops or utilization above 80% → recommend a bandwidth upgrade / review of the rate limit.
   - Packet errors → recommend physical-layer / port investigation (cabling, optics) on the affected port.
   - Rising latency → recommend a path / metro review.

7. **Build the report.** Structure it using the HTML report block below. Populate the Summary, the ranked scorecard table, the flagged-connections section, and the remediation section. Skip any component or section that has no data — no placeholder text.

   ### Section content
   - **Summary**: 3–5 sentences — number of connections scored, average and median score, number of flagged connections, and the headline finding.
   - **Scorecard Ranking**: every scored connection ranked by score. Include rank, connection name, UUID, composite score, and the top deductions (which components cost the most points).
   - **Flagged Connections**: every connection with at least one measurable issue (per Step 5), with the primary issue. Include only if any exist.
   - **Recommended Remediation**: every flagged connection with its recommended action. Include only if any exist.

   ```
   <div class="header">
       <h1>Connection Health Scorecard</h1>
   </div>

   <div class="section">
       <h2>Summary</h2>
       <div class="content">
       </div>
   </div>

   <div class="section">
       <h2>Scorecard Ranking</h2>
       <div class="content">
           <div class="table-container">
               <!-- Header Row -->
               <ul class="table-row table-header">
                   <li>Rank</li>
                   <li>Connection Name</li>
                   <li>UUID</li>
                   <li>Health Score</li>
                   <li>Top Deductions</li>
               </ul>

               <!-- Data Row -->
               <ul class="table-row">
               </ul>
           </div>
       </div>
   </div>

   <div class="section">
       <h2>Flagged Connections</h2>
       <div class="content">
           <div class="table-container">
               <!-- Header Row -->
               <ul class="table-row table-header">
                   <li>Connection Name</li>
                   <li>UUID</li>
                   <li>Health Score</li>
                   <li>Primary Issue</li>
               </ul>

               <!-- Data Row -->
               <ul class="table-row">
               </ul>
           </div>
       </div>
   </div>

   <div class="section">
       <h2>Recommended Remediation</h2>
       <div class="content">
           <div class="table-container">
               <!-- Header Row -->
               <ul class="table-row table-header">
                   <li>Connection Name</li>
                   <li>UUID</li>
                   <li>Health Score</li>
                   <li>Dominant Factor</li>
                   <li>Recommended Action</li>
               </ul>

               <!-- Data Row -->
               <ul class="table-row">
               </ul>
           </div>
       </div>
   </div>
   ```

8. **Send the report** with `send_email_notification` to `recipient_email_addresses`. Follow the email rules below:
   - `pdfContent`: the full report text from Step 7.
   - `body`: one-paragraph summary of overall connection health and the headline finding.
   - `pdfTitle`: `ConnectionHealthScorecard`

## Available Tools
This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"24h"`, `"7d"`).
*   **`search_connections`**: Enumerates PROVISIONED connections and resolves connection context (A/Z ports, A/Z metro codes, provisioned bandwidth).
*   **`search_metrics`**: Retrieves connection, port, and metro metrics over the scoring window.
*   **`get_metric`**: Retrieves a single metric series when a targeted lookup is needed.
*   **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
*   **Single-resource metric calls**: each `search_metrics` / `get_metric` call can request metrics for only one resource (one connection, port, or metro). Execute one call per resource. If a response is too large to process, split the request by metric name across multiple calls.
*   **Default window**: if `scoring_window` is not provided, score over the last 24 hours.
*   **Reproducibility**: apply the default weights and normalization rules in Step 4 exactly so the same inputs always produce the same score. State the weights and any renormalization (excluded components) in the report.
*   **Connection-level error metric is not exposed**: derive packet errors from the A-side and Z-side port metrics.
*   **Flag anomalies**: call out any non-zero rate-exceeded packet drops or packet errors as warnings in the report. Remember rate-exceeded drops reflect traffic over the connection's rate limit, not general packet loss.
*   **Plain English**: no API jargon, no raw metric strings in the narrative, full UUIDs always. Favor insight over raw counts — explain what the score means and why a connection is unhealthy.
*   **Graceful skips**: skip connections that have no metric data over the window; note how many were skipped in the Summary. Skip empty sections entirely.
*   **Error handling**: if metric collection fails entirely (no connection could be scored), do not send the email. If only some connections fail, score the rest and note the gaps.
*   **Token efficiency**: only call tools when all necessary parameters are present, avoiding unnecessary context loading.

## Configuration
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the scorecard report.
* **`connection_uuids`**: < A list of connection UUIDs > - Optional. Restrict scoring to a specific subset of connections. If omitted, all PROVISIONED connections are scored.
* **`scoring_window`**: < A time range, e.g. "last 24 hours" > - Optional. The window over which metrics are collected. Default last 24 hours.
