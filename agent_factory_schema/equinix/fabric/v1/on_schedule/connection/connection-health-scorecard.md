---
name: connection-health-scorecard
description: Scores and ranks the health of Fabric connections (rate-exceeded packet drops, packet errors, utilization, latency) and emails a prioritized remediation scorecard.
categories: ["Monitor & Report Agents"]
---

# Connection Health Scorecard Agent

## Overview
An Equinix Agent that gives operators a single-pane health view across Equinix Fabric connections. It collects per-connection performance metrics, computes a composite 0 to 100 health score for each connection, ranks them, flags any connection with an obvious measurable issue, and recommends remediation for every flagged connection.
This agent helps troubleshooting effort so it can be prioritized where it matters most. The result is delivered as a PDF scorecard via email.
This agent is advisory only. It reads telemetry and writes recommendations into a report; it never modifies a connection, its bandwidth, or its rate limit.
This agent runs once immediately by default unless scheduled by user.

## Success Criteria & Termination
- **Success**: at least one in-scope connection was scored on at least one component and the scorecard email was accepted by `send_email_notification`. The run ends after Step 8.
- **Partial success (still a completed run)**: some connections were scored and others were skipped — no metric data over the window, or a metric call failed. The agent scores what it can, states in the Summary the exact count scored and the count skipped with the reason, sends the email, and ends. A connection that could not be measured is **excluded from the ranking, never scored 0** — absence of data is not evidence of poor health.
- **No report sent**: the run ends with no email in exactly four cases, and in each one the agent states the reason in the conversation and stops: (1) `recipient_email_addresses` is empty or contains no syntactically valid address (Step 1a); (2) `get_timestamps` failed, so no scoring window could be established (Step 1b); (3) the connection set resolves to zero PROVISIONED connections, none of the supplied `connection_uuids` resolved, or `search_connections` failed on the first page (Step 2); (4) zero connections produced any usable metric data, so no score can be computed (Step 3). An empty or all-blank scorecard is never emailed.

## Prerequisites
- Connections should be in `PROVISIONED` state to be scored.
- Metric data is only available for connections that have been live over the scoring window; freshly provisioned connections with no metrics are skipped and counted in the Summary.
- **Ports are only resolvable on port-backed sides.** Packet errors are read from the A-side and Z-side **port** UUIDs on the connection. A side whose access point is a Cloud Router, a Network, or a virtual device has no port UUID and contributes no error data — score errors from the side or sides that do resolve, and exclude the component entirely when neither does.
- **Provisioned bandwidth must be present and non-zero** for the utilization component; it is the denominator. Where it is absent, the utilization component is excluded and the remaining weights are renormalized per Step 4.
- The agent's Fabric API credentials must have permission to read connections in the target project or projects, to read stream metrics for those connections and their ports, and to send email notifications. Missing metric-read permission is indistinguishable from missing data at the API level and will present as a run in which every connection is skipped.
- `recipient_email_addresses` must contain at least one syntactically valid email address — the scorecard is the run's only output and cannot be delivered otherwise.

## Capabilities
- Enumerate all PROVISIONED connections (or a user-specified subset)
- Collect rate-exceeded packet drops, packet errors, and utilization metrics per connection
- Compute a reproducible composite 0–100 health score per connection
- Rank all connections and flag any with an obvious measurable issue
- Recommend concrete remediation for every flagged connection
- Deliver a prioritized scorecard as a PDF report via email

## Instructions

1. **Validate configuration and determine the metrics time window.**
   1a. Confirm `recipient_email_addresses` is present and contains at least one syntactically valid email address. If not, stop immediately — before any other tool call — and inform the user: "No valid recipient email address was provided. The scorecard cannot be delivered." Do not collect metrics for a report that cannot be sent.
   1b. Convert `scoring_window` to a duration string (e.g. 24 hours -> "24h", 30 days -> "30d"; default to `"24h"`), then call `get_timestamps` with that duration. Save the returned `from` and `to` (ISO 8601 UTC) as the reporting window — use them with the `BETWEEN` operator on `/time` for every `search_metrics` / `get_metric` call in Step 3, and record the window length in hours as `window_hours` for Step 4. If `get_timestamps` fails, stop and report that the scoring window could not be established; no window means no comparable metric query.

2. **Resolve the connection set.**
   - If `connection_uuids` is provided, score those connections and only those. Attempt metric collection for **every** UUID in the list — do not truncate, sample, or re-order it. A UUID that returns no metric data is reported as skipped with its reason, not silently dropped.
   - Otherwise, call `search_connections` for all PROVISIONED connections. Follow the request payload below (paginate with increasing `offset` until all results are retrieved):
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
   - For each connection, capture the **connection UUID**, **name**, **provisioned bandwidth in Mbps**, and the **A-side and Z-side port UUIDs** (`/aSide/accessPoint/port/uuid`, `/zSide/accessPoint/port/uuid`) where present. Provisioned bandwidth is the denominator for utilization in Step 4; the port UUIDs are the resources for the packet-error metrics in Step 3. A side whose access point is not a port — a Cloud Router, a Network, or a virtual device — has no port UUID: record it as "no port" and collect errors from the other side only. **Never invent or infer a port UUID.**
   - Every connection in the resolved set is scored. Do not sample, truncate, or re-order the set — the scorecard covers the whole set it resolved, so two runs on the same estate score the same connections.
   - **Failure handling for this step:**
     - If `search_connections` fails or times out on the first page, stop. Report in the conversation that the connection inventory could not be retrieved, including the error detail. Send no email — there is nothing to score.
     - If it fails on a later page, do not retry. Treat the pages already retrieved as the full scope, and state in the Summary that the inventory is incomplete ("pages 1 through k of an unknown total were retrieved") before any count, so a partial inventory is never mistaken for the whole estate.
     - If the search returns zero PROVISIONED connections, stop and inform the user that no connections are in scope. Send no email.
     - If `connection_uuids` was provided and none of the listed UUIDs resolve to a PROVISIONED connection, stop and inform the user which UUIDs did not resolve. Send no email. If some resolve, score those and list the unresolved UUIDs in the Summary.

3. **Collect metrics per connection** over the `from`–`to` window from Step 1 using `search_metrics`, applying the `BETWEEN` operator on `/time`. Issue one call per resource; if a response is too large to process, split the metric names across multiple calls, or use `get_metric` for a single series (e.g. drops in one call, utilization in another). Collect:
   - **Rate-exceeded packet drops** (connection): `equinix.fabric.connection.packets_dropped_rx_aside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_rx_zside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_tx_aside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_tx_zside_rateexceeded.count`. These count only packets dropped because traffic exceeded the connection's provisioned rate limit — this is **not** general packet loss.
   - **Utilization** (connection): `equinix.fabric.connection.bandwidth_rx.usage_summary` and `equinix.fabric.connection.bandwidth_tx.usage_summary` — use the inbound/outbound p95 usage values against the provisioned bandwidth. Always apply the /interval=PT0M filter.
   - **Packet errors** (port): `equinix.fabric.port.packets_erred_rx.count` and `equinix.fabric.port.packets_erred_tx.count` on the A-side and Z-side ports resolved in Step 2. (A connection-level error metric is not exposed — see Guidelines.)

   **Collect port errors once per distinct port UUID**, not once per connection. Build the set of distinct A-side and Z-side port UUIDs across all selected connections, issue one call per distinct port, and reuse the result for every connection on that port. This is both a call-count reduction and a correctness requirement: the same port must contribute the same error count to every connection on it within a run.

   **Failure handling for this step:**
   - If the connection-level call fails for one connection, mark its drop and utilization components as no data, record the error, and continue to the next connection. Do not retry, and do not fall back to a different metric or a shorter window.
   - If a port call fails, mark the error component as no data for every connection on that port, record which port failed once rather than once per connection, and continue.
   - If a connection ends up with no usable component at all, it is not scored — exclude it from the ranking and count it in the skipped tally with its reason. Do not score it 0.
   - If no connection produced any usable component, stop. Report in the conversation that no connection could be scored and why. Send no email — an all-blank scorecard is worse than no scorecard.

4. **Compute a composite 0–100 health score** per connection, where 100 = perfect health. Every sub-score is a table lookup that returns an integer — do not interpolate between rows and do not substitute a continuous formula. An integer lookup is what makes the score reproducible; a curve would not be.

   First derive the inputs:
   - `window_hours` = the length of the Step 1 window in hours (`24h` -> 24, `7d` -> 168, `30d` -> 720).
   - `drops_per_hour` = (sum of all four rate-exceeded counters over the window) / `window_hours`. Sum the rx-aside, rx-zside, tx-aside, and tx-zside counters into one total — do not score directions separately and do not take the maximum.
   - `errors_per_hour` = (sum of `packets_erred_rx.count` + `packets_erred_tx.count` across every resolved port for this connection) / `window_hours`. If only one side resolved to a port, sum that side only and mark the component "one side only" in the report — this is partial data, not missing data.
   - `utilization_pct` = max(p95 rx usage, p95 tx usage) / provisioned bandwidth x 100. Convert both to the same unit before dividing — `usage_summary` values are reported in bits per second and provisioned bandwidth in Mbps, so divide the p95 value by 1,000,000 before dividing by the bandwidth. Use the **maximum** of the two directions, not the average: a connection saturated inbound is saturated. If provisioned bandwidth is absent or zero, this component has no data.

   Counters are normalized by time because Fabric exposes no per-connection packet-total metric — see the known limitations in the Guidelines. Normalizing by time also keeps a score comparable across scoring windows: without it, a `30d` window would score every connection worse than a `24h` window on identical traffic.

   **Rate-exceeded packet drops — 35% weight**

   | `drops_per_hour` | Sub-score | What it means |
   |------------------|-----------|---------------|
   | 0 | 100 | No traffic exceeded the rate limit over the window. |
   | > 0 and < 1,000 | 90 | Under ~0.3 packets/second — occasional microbursts, not usually actionable. |
   | 1,000 to < 10,000 | 70 | ~0.3–3 packets/second — recurring clipping that applications will notice. |
   | 10,000 to < 100,000 | 40 | ~3–28 packets/second — sustained clipping. |
   | 100,000 or more | 0 | Above ~28 packets/second sustained — the rate limit is systematically undersized. |

   **Packet errors — 35% weight**

   | `errors_per_hour` | Sub-score | What it means |
   |-------------------|-----------|---------------|
   | 0 | 100 | Clean physical layer on every resolved port. |
   | > 0 and < 10 | 75 | Within the noise floor of a healthy optic. |
   | 10 to < 100 | 40 | Marginal optic or connector — worth scheduling a maintenance window. |
   | 100 or more | 0 | Roughly one error every 36 seconds or worse — an active physical fault. |

   **Utilization headroom — 30% weight**

   | `utilization_pct` | Sub-score | What it means |
   |-------------------|-----------|---------------|
   | 50% or below | 100 | Full headroom — can absorb a doubling of load. |
   | > 50% up to and including 70% | 85 | Comfortable, worth watching. |
   | > 70% up to and including 80% | 70 | Approaching capacity — the point to start planning an upgrade. |
   | > 80% up to and including 90% | 40 | Little headroom left; this is also the band that triggers the flag in Step 5. |
   | > 90% and < 100% | 15 | Effectively saturated. |
   | 100% or above | 0 | p95 usage is at or above the provisioned rate, so the rate limit was clipping for at least 5% of the window. |

   - **Composite**: the weighted average of the available sub-scores — drops 35%, packet errors 35%, utilization headroom 30% — rounded to the nearest whole number with exact halves rounded up. Report whole numbers only.
   - **Missing components**: if a component has no data, drop it and renormalize the remaining weights to sum to 100%. Worked example — if the packet-error component has no data, the composite is `(0.35 x drops_subscore + 0.30 x utilization_subscore) / 0.65`. Name every excluded component for that connection in the report.
   - **No components**: if all three components have no data, the connection is **not scored** — it is excluded from the ranking and counted in the skipped tally with its reason. Never rank an unmeasured connection as 0; that would put a metrics gap at the top of the remediation list and send an operator to investigate a network fault that does not exist.
   - **Tie-breaking**: table lookups make exact ties common — many healthy connections will score 100. Break ties deterministically, in this order: lower `utilization_pct` ranks healthier, then lower `drops_per_hour`, then lower `errors_per_hour`, then connection UUID ascending in lexicographic order. The UUID tie-break is the final backstop and guarantees the ranking is a total order, so two runs on identical data produce the same ranking.

5. **Rank** all scored connections from highest (healthiest) to lowest, breaking ties by the rule in Step 4. **Flag** (a simple yes/no) every connection that has at least one obvious, measurable issue over the window:
   - Any non-zero rate-exceeded packet drops, or
   - Any non-zero packet errors on the A-side or Z-side port, or
   - p95 rx or tx usage exceeding 80% of provisioned bandwidth.

   A connection with none of these is not flagged. A connection that was not scored is neither flagged nor unflagged — it is reported as skipped.

6. **Recommend remediation for every flagged connection** (from Step 5), tied to the issue(s) present. These are recommendations for a human to action manually — the agent never applies them, so there is no change for it to verify afterwards:
   - Rate-exceeded drops or utilization above 80% → recommend a bandwidth upgrade / review of the rate limit.
   - Packet errors → recommend physical-layer / port investigation (cabling, optics) on the affected port.

7. **Build the report.** Structure it using the HTML report block below. Populate the Summary, the ranked scorecard table, the flagged-connections section, and the remediation section. Skip any component or section that has no data — no placeholder text.

   ### Section content
   - **Summary**: 4–6 sentences — the scoring window; the number of connections in scope; the number scored; the number skipped for no metric data, with the most common reason; average and median score; the number flagged; and the headline finding. If the connection inventory itself was incomplete (see the failure handling in Step 2), say so before any counts, so no reader mistakes a partial inventory for the whole estate.
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
   - `recipients`: `recipient_email_addresses`.
   - `pdfContent`: the full report text from Step 7.
   - `body`: one-paragraph summary of overall connection health, the coverage actually achieved (scored / skipped counts), and the headline finding.
   - `pdfTitle`: `ConnectionHealthScorecard`

   Also present the Summary and the ranked scorecard directly in the conversation, so the run's output survives even if delivery fails. If `send_email_notification` fails, do not retry: print the full Step 7 report text and the delivery error into the conversation, state that the report was produced but not delivered, and end the run.

   Sending this email is the agent's terminal action. Once it is sent the run is complete — do not re-collect metrics, re-score, re-rank, or send a second email, and do not re-check any connection. The agent runs again only when its schedule next fires.

## Available Tools
This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"24h"`, `"7d"`).
*   **`search_connections`**: Enumerates PROVISIONED connections and resolves per-connection context (A-side and Z-side port UUIDs, provisioned bandwidth).
*   **`search_metrics`**: Retrieves connection and port metrics over the scoring window.
*   **`get_metric`**: Retrieves a single metric series when a targeted lookup is needed.
*   **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
*   **Advisory only — no remediation actions**: "recommend remediation" in Step 6 means writing a recommended action into the report. This agent performs no restart, reset, failover, bandwidth change, or configuration change of any kind, so no step has an outcome to wait for or poll.
*   **Single-resource metric calls**: each `search_metrics` / `get_metric` call can request metrics for only one resource (one connection or port). Execute one call per resource. If a response is too large to process, split the request by metric name across multiple calls.
*   **Default window**: if `scoring_window` is not provided, score over the last 24 hours.
*   **Reproducibility**: apply the Step 4 lookup tables, weights, renormalization rule, rounding rule, and tie-break order exactly as written, so the same inputs always produce the same score and the same ranking. State the weights and any renormalization (excluded components) in the report.
*   **No retries and no waiting**: every tool call is issued at most once per resource per run. `wait` is intentionally not among the declared tools and no step polls, sleeps, or re-issues a call. Every call this agent makes is a read against telemetry that was already recorded before the run began, so re-issuing a failed call cannot make missing data appear — and the agent takes no action whose outcome would need to be waited on. When a call fails, mark that resource's component as no data, disclose it in the report, and move on. Re-run the agent to pick up a transient failure.
*   **Error handling**: failure handling is specified per step in the Instructions, and the conditions under which the run halts without sending an email are enumerated in **Success Criteria & Termination**. Every failure not listed there degrades gracefully — score what returned data, skip the rest, and report the gap.
*   **Connection-level error metric is not exposed**: derive packet errors from the A-side and Z-side port metrics.
*   **Flag anomalies**: call out any non-zero rate-exceeded packet drops or packet errors as warnings in the report.
*   **Known limitation — rate-exceeded drops are not general packet loss**: these counters increment only when offered traffic exceeded the connection's provisioned rate limit. They say nothing about loss caused by a fault in the path.
*   **Known limitation — port errors are shared, not per-connection**: a Fabric port carries many connections, and no connection-level error metric is exposed. Every connection on the same port therefore receives an identical packet-error sub-score, and one dirty port will depress the ranking of every connection on it. When several adjacent rows in the scorecard share a port, treat that as one port-level investigation rather than as N independent connection faults, and say so in the Recommended Remediation section, naming the shared port UUID.
*   **Known limitation — drops and errors are not loss percentages**: Fabric exposes no per-connection packet-total metric, so these counters are normalized by time only, never by traffic volume. A 50 Mbps and a 10 Gbps connection with the same drops per hour receive the same sub-score even though the fraction of affected traffic differs by orders of magnitude. Do not present or read the drop sub-score as a loss rate.
*   **Known limitation — p95 hides bursts**: `usage_summary` p95 excludes the busiest 5% of the window by construction, so a connection saturated for up to roughly 1.2 hours of a 24-hour window can still show a p95 well under 80%. Rate-exceeded drops are the complementary signal: a connection with no utilization flag but non-zero rate-exceeded drops is burst-saturated, and the report should say so rather than presenting the two components as independent.
*   **Known limitation — no historical baseline**: every run scores its window in isolation, with no durable state carried between runs. A score is a snapshot, not a trend, and a connection that is newly degrading cannot be distinguished from one that has always been poor. Never describe a score as improving or worsening.
*   **Plain English**: no API jargon, no raw metric strings in the narrative, full UUIDs always. Favor insight over raw counts — explain what the score means and why a connection is unhealthy.
*   **Graceful skips**: skip connections that have no metric data over the window; note how many were skipped in the Summary. Skip empty sections entirely.
*   **Token efficiency**: only call tools when all necessary parameters are present, avoiding unnecessary context loading.

## Configuration
* **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the scorecard report.
* **`connection_uuids`**: < A list of connection UUIDs > - Optional. Restrict scoring to a specific subset of connections. If omitted, all PROVISIONED connections are scored.
* **`scoring_window`**: < A time range, e.g. "last 24 hours" > - Optional. The window over which metrics are collected. Default last 24 hours.
