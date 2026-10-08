---
name: network-health-scorecard
description: Scores and ranks the health of every connection on a Fabric Cloud Router (rate-exceeded packet drops, packet errors, utilization, latency) and emails a prioritized remediation scorecard.
categories: ["Monitor & Report Agents"]
---

# Network Health Scorecard Agent

## Overview

An Equinix Agent that gives operators a single-pane health view of the network built around one Equinix Fabric Cloud Router. Given a Cloud Router UUID, it resolves the router, fetches every connection attached to it, collects per-connection performance metrics, computes a composite 0 to 100 health score for each connection, ranks them, flags any connection with an obvious measurable issue, and recommends remediation for every flagged connection.
This agent helps troubleshooting effort on a Cloud Router's network be prioritized where it matters most. The result is delivered as a PDF scorecard via email.
This agent is advisory only. It reads telemetry and writes recommendations into a report; it never modifies the Cloud Router, a connection, its bandwidth, its rate limit, or any routing configuration.
This agent runs once immediately by default unless scheduled by user.

## Success Criteria & Termination

- **Success**: at least one connection on the Cloud Router was scored on at least one component and the scorecard email was accepted by `send_email_notification`. The run ends after Step 10.
- **Partial success (still a completed run)**: some connections were scored and others were skipped — no metric data over the window, or a metric call failed. The agent scores what it can, states in the Summary the exact count scored and the count skipped with the reason, sends the email, and ends. A connection that could not be measured is **excluded from the ranking, never scored 0** — absence of data is not evidence of poor health.
- **No report sent**: the run ends with no email in exactly five cases, and in each one the agent states the reason in the conversation and stops: (1) `recipient_email_addresses` is empty or contains no syntactically valid address (Step 1a); (2) `get_timestamps` failed, so no scoring window could be established (Step 1b); (3) `cloud_router_uuid` is missing, `search_routers` failed, or the Cloud Router does not exist or is not in `PROVISIONED` state (Step 2); (4) the Cloud Router has zero PROVISIONED connections, none of the supplied `connection_uuids` resolved to a PROVISIONED connection on this Cloud Router, or `search_connections` failed on the first page (Step 3); (5) zero connections produced any usable metric data, so no score can be computed (Step 4). An empty or all-blank scorecard is never emailed.

## Prerequisites

- The Cloud Router identified by `cloud_router_uuid` must exist and be in `PROVISIONED` state.
- Connections should be in `PROVISIONED` state to be scored.
- Metric data is only available for connections that have been live over the scoring window, and only for assets attached to a Fabric stream. Freshly provisioned connections with no metrics are skipped and counted in the Summary.
- **The Cloud Router is always the A-side.** On a Cloud Router connection the A-side access point is the Cloud Router itself and has no port UUID. Packet errors are therefore read from the **Z-side port** only, and only when the Z-side access point is a port (`COLO`). A Z-side that is a service profile (cloud provider), a Network, or a virtual device contributes no error data — the error component is excluded for that connection. A service profile Z-side may expose the provider's port UUID; ignore it, since that port is not the customer's.
- **Provisioned bandwidth must be present and non-zero** for the utilization component; it is the denominator. Where it is absent, the utilization component is excluded and the remaining weights are renormalized per Step 5.
- **Latency is inter-metro.** Latency is read from the Fabric metro-to-metro latency series between the Cloud Router's metro and the connection's Z-side metro. The origin metro must be subscribed to a stream for the series to exist. A connection whose Z-side is in the same metro as the Cloud Router has no inter-metro latency series and its latency component is excluded.
- The agent's Fabric API credentials must have permission to read the Cloud Router, to read connections in the Cloud Router's project, to read stream metrics for those connections, their ports, and the relevant metros, and to send email notifications. Missing metric-read permission is indistinguishable from missing data at the API level and will present as a run in which every connection is skipped.
- `recipient_email_addresses` must contain at least one syntactically valid email address — the scorecard is the run's only output and cannot be delivered otherwise.

## Capabilities

- Resolve a Fabric Cloud Router and its location, package, and state
- Enumerate all PROVISIONED connections on that Cloud Router (or a user-specified subset of them)
- Collect rate-exceeded packet drops, packet errors, utilization, and inter-metro latency per connection
- Compute a reproducible composite 0–100 health score per connection
- Rank all connections and flag any with an obvious measurable issue
- Recommend concrete remediation for every flagged connection
- Deliver a prioritized scorecard as a PDF report via email

## Instructions

1. **Validate configuration and determine the metrics time window.**
   1a. Confirm `recipient_email_addresses` is present and contains at least one syntactically valid email address. If not, stop immediately — before any other tool call — and inform the user: "No valid recipient email address was provided. The scorecard cannot be delivered." Do not collect metrics for a report that cannot be sent. In the same check, confirm `cloud_router_uuid` is present; if it is not, stop and inform the user: "No Cloud Router UUID was provided. There is no network to score."
   1b. Convert `scoring_window` to a duration string (e.g. 24 hours -> "24h", 30 days -> "30d"; default to `"24h"`), then call `get_timestamps` with that duration. Save the returned `from` and `to` (ISO 8601 UTC) as the reporting window — use them with the `BETWEEN` operator on `/time` for every `search_metrics` / `get_metric` call in Step 4, and record the window length in hours as `window_hours` for Step 5. If `get_timestamps` fails, stop and report that the scoring window could not be established; no window means no comparable metric query.

2. **Resolve the Cloud Router.** Call `search_routers` filtered on `cloud_router_uuid`. Filter on the UUID only — do not add a state filter, so that a Cloud Router in a non-PROVISIONED state is returned and reported as such rather than appearing not to exist:

   ```json
   {
     "filter": {
       "and": [
         { "property": "/uuid", "operator": "=", "values": ["<cloud_router_uuid>"] }
       ]
     },
     "pagination": { "offset": 0, "limit": 1 }
   }
   ```

   From the single result, capture the Cloud Router **name**, **UUID**, **state**, **package code**, **metro code** (`/location/metroCode`), and **project ID**. The metro code is the origin metro for every latency lookup in Step 4.

   - **Failure handling for this step:**
     * If `search_routers` fails, times out, or returns no Cloud Router for the UUID, stop. Report in the conversation that the Cloud Router could not be retrieved, including the error detail. Send no email.
     * If the Cloud Router is in any state other than `PROVISIONED`, stop and inform the user of its current state. Send no email.
     * If the Cloud Router has no metro code, continue — the latency component is excluded for every connection and the report says so once, in the Summary.

3. **Resolve the connection set on the Cloud Router.** Call `search_connections` for all PROVISIONED connections whose A-side is this Cloud Router. Follow the request payload below (paginate with increasing `offset` until all results are retrieved):

   ```json
   {
     "filter": {
       "and": [
         { "property": "/aSide/accessPoint/router/uuid", "operator": "=", "values": ["<cloud_router_uuid>"] },
         { "property": "/operation/equinixStatus", "operator": "=", "values": ["PROVISIONED"] }
       ]
     },
     "pagination": { "offset": 0, "limit": 100 }
   }
   ```

   - If `connection_uuids` is provided, score only the connections in that list that are also returned by the search above. Attempt metric collection for **every** resolved UUID in the list — do not truncate, sample, or re-order it. A listed UUID that is not a PROVISIONED connection on this Cloud Router is reported as unresolved, not silently dropped.
   - For each connection, capture the **connection UUID**, **name**, **provisioned bandwidth in Mbps**, **Z-side access point type** (`/zSide/accessPoint/type`), **Z-side port UUID** (`/zSide/accessPoint/port/uuid`) where the Z-side is a port, **Z-side metro code** (`/zSide/accessPoint/location/metroCode`), and the **Z-side destination label** (port name, service profile name, network name, or virtual device name — whichever applies). Provisioned bandwidth is the denominator for utilization in Step 5; the Z-side port UUID is the resource for the packet-error metrics in Step 4; the Z-side metro code is the destination metro for latency in Step 4. A Z-side that is not a port has no port UUID: record it as "no port". **Never invent or infer a port UUID or a metro code.**
   - Every connection in the resolved set is scored. Do not sample, truncate, or re-order the set — the scorecard covers the whole set it resolved, so two runs on the same Cloud Router score the same connections.
   - **Failure handling for this step:**
     * If `search_connections` fails or times out on the first page, stop. Report in the conversation that the Cloud Router's connection inventory could not be retrieved, including the error detail. Send no email — there is nothing to score.
     * If it fails on a later page, do not retry. Treat the pages already retrieved as the full scope, and state in the Summary that the inventory is incomplete ("pages 1 through k of an unknown total were retrieved") before any count, so a partial inventory is never mistaken for the Cloud Router's whole network.
     * If the search returns zero PROVISIONED connections, stop and inform the user that the Cloud Router has no connections in scope. Send no email.
     * If `connection_uuids` was provided and none of the listed UUIDs resolve to a PROVISIONED connection on this Cloud Router, stop and inform the user which UUIDs did not resolve. Send no email. If some resolve, score those and list the unresolved UUIDs in the Summary.

4. **Collect metrics per connection** over the `from`–`to` window from Step 1 using `search_metrics`, applying the `BETWEEN` operator on `/time`. Issue one call per resource; if a response is too large to process, split the metric names across multiple calls, or use `get_metric` for a single series (e.g. drops in one call, utilization in another). Collect:

   - **Rate-exceeded packet drops** (connection): `equinix.fabric.connection.packets_dropped_rx_aside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_rx_zside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_tx_aside_rateexceeded.count`, `equinix.fabric.connection.packets_dropped_tx_zside_rateexceeded.count`. These count only packets dropped because traffic exceeded the connection's provisioned rate limit — this is **not** general packet loss.
   - **Utilization** (connection): `equinix.fabric.connection.bandwidth_rx.usage_summary` and `equinix.fabric.connection.bandwidth_tx.usage_summary` — use the inbound/outbound p95 usage values against the provisioned bandwidth. Always apply the `/interval=PT0M` filter.
   - **Packet errors** (port): `equinix.fabric.port.packets_erred_rx.count` and `equinix.fabric.port.packets_erred_tx.count` on the Z-side port resolved in Step 3. (A connection-level error metric is not exposed, and the Cloud Router A-side has no port — see Guidelines.)

     **Collect port errors once per distinct port UUID**, not once per connection. Build the set of distinct Z-side port UUIDs across all selected connections, issue one call per distinct port, and reuse the result for every connection on that port. This is both a call-count reduction and a correctness requirement: the same port must contribute the same error count to every connection on it within a run.

   - **Latency** (metro): `equinix.fabric.metro.<origin>_<destination>.latency` on the metro resource `<ORIGIN>`, where `<origin>` is the Cloud Router metro code from Step 2 and `<destination>` is the connection's Z-side metro code from Step 3, both lowercased in the metric name (e.g. Cloud Router in `SV`, Z-side in `DC` -> `equinix.fabric.metro.sv_dc.latency` on metro `SV`). Read the window `mean` and `max` (milliseconds) from the series summary; if the summary is absent, compute the mean and max of the returned datapoint values.

     **Collect latency once per distinct metro pair**, not once per connection. Build the set of distinct (Cloud Router metro, Z-side metro) pairs, issue one `get_metric` call per pair, and reuse the result for every connection with that pair. A connection whose Z-side metro equals the Cloud Router metro, or whose Z-side metro is unknown, has no latency series — mark the component "local, not measured" or "no metro" respectively, and do not issue a call for it.

   **Failure handling for this step:**

   - If the connection-level call fails for one connection, mark its drop and utilization components as no data, record the error, and continue to the next connection. Do not retry, and do not fall back to a different metric or a shorter window.
   - If a port call fails, mark the error component as no data for every connection on that port, record which port failed once rather than once per connection, and continue.
   - If a metro-pair latency call fails or returns no datapoints, mark the latency component as no data for every connection with that pair, record which metro pair failed once rather than once per connection, and continue.
   - If a connection ends up with no usable component at all, it is not scored — exclude it from the ranking and count it in the skipped tally with its reason. Do not score it 0.
   - If no connection produced any usable component, stop. Report in the conversation that no connection on the Cloud Router could be scored and why. Send no email — an all-blank scorecard is worse than no scorecard.

5. **Compute a composite 0–100 health score** per connection, where 100 = perfect health. Every sub-score is a table lookup that returns an integer — do not interpolate between rows and do not substitute a continuous formula. An integer lookup is what makes the score reproducible; a curve would not be.

   First derive the inputs:

   - `window_hours` = the length of the Step 1 window in hours (`24h` -> 24, `7d` -> 168, `30d` -> 720).
   - `drops_per_hour` = (sum of all four rate-exceeded counters over the window) / `window_hours`. Sum the rx-aside, rx-zside, tx-aside, and tx-zside counters into one total — do not score directions separately and do not take the maximum.
   - `errors_per_hour` = (`packets_erred_rx.count` + `packets_erred_tx.count` on the Z-side port) / `window_hours`. Because the A-side is always the Cloud Router, a Z-side-only error reading is the complete reading for a Cloud Router connection — do not label it partial data.
   - `utilization_pct` = max(p95 rx usage, p95 tx usage) / provisioned bandwidth x 100. Convert both to the same unit before dividing — `usage_summary` values are reported in bits per second and provisioned bandwidth in Mbps, so divide the p95 value by 1,000,000 before dividing by the bandwidth. Use the **maximum** of the two directions, not the average: a connection saturated inbound is saturated. If provisioned bandwidth is absent or zero, this component has no data.
   - `latency_mean_ms` and `latency_max_ms` = the window mean and max for the connection's metro pair. `latency_spike_ms` = `latency_max_ms` − `latency_mean_ms`. `latency_spike_pct` = `latency_spike_ms` / `latency_mean_ms` x 100. If `latency_mean_ms` is zero or absent, this component has no data.

   Counters are normalized by time because Fabric exposes no per-connection packet-total metric — see the known limitations in the Guidelines. Normalizing by time also keeps a score comparable across scoring windows: without it, a `30d` window would score every connection worse than a `24h` window on identical traffic.

   Latency is scored on **stability, not distance**. Absolute inter-metro latency is set by geography (a trans-Atlantic pair will always be far slower than an in-region pair), so scoring the raw value would permanently penalize every long-haul connection for something no operator can fix. The latency sub-score measures how far the window's worst reading rose above its own average.

   **Rate-exceeded packet drops — 30% weight**

   | `drops_per_hour`    | Sub-score | What it means                                                                     |
   | ------------------- | --------- | --------------------------------------------------------------------------------- |
   | 0                   | 100       | No traffic exceeded the rate limit over the window.                               |
   | > 0 and < 1,000     | 90        | Under ~0.3 packets/second — occasional microbursts, not usually actionable.       |
   | 1,000 to < 10,000   | 70        | ~0.3–3 packets/second — recurring clipping that applications will notice.         |
   | 10,000 to < 100,000 | 40        | ~3–28 packets/second — sustained clipping.                                        |
   | 100,000 or more     | 0         | Above ~28 packets/second sustained — the rate limit is systematically undersized. |

   **Packet errors — 25% weight**

   | `errors_per_hour` | Sub-score | What it means                                                           |
   | ----------------- | --------- | ----------------------------------------------------------------------- |
   | 0                 | 100       | Clean physical layer on the Z-side port.                                |
   | > 0 and < 10      | 75        | Within the noise floor of a healthy optic.                              |
   | 10 to < 100       | 40        | Marginal optic or connector — worth scheduling a maintenance window.    |
   | 100 or more       | 0         | Roughly one error every 36 seconds or worse — an active physical fault. |

   **Utilization headroom — 25% weight**

   | `utilization_pct`             | Sub-score | What it means                                                                                                |
   | ----------------------------- | --------- | ------------------------------------------------------------------------------------------------------------ |
   | 50% or below                  | 100       | Full headroom — can absorb a doubling of load.                                                               |
   | > 50% up to and including 70% | 85        | Comfortable, worth watching.                                                                                 |
   | > 70% up to and including 80% | 70        | Approaching capacity — the point to start planning an upgrade.                                               |
   | > 80% up to and including 90% | 40        | Little headroom left; this is also the band that triggers the flag in Step 6.                                |
   | > 90% and < 100%              | 15        | Effectively saturated.                                                                                       |
   | 100% or above                 | 0         | p95 usage is at or above the provisioned rate, so the rate limit was clipping for at least 5% of the window. |

   **Latency stability — 20% weight**

   Apply the rows top to bottom and use the first row that matches.

   | Condition                                | Sub-score | What it means                                                                  |
   | ---------------------------------------- | --------- | ------------------------------------------------------------------------------ |
   | `latency_spike_ms` < 2                   | 100       | Any rise above the average is under 2 ms — measurement noise, not a signal.    |
   | `latency_spike_pct` 10% or below         | 100       | Stable path — the worst reading stayed within 10% of the average.              |
   | > 10% up to and including 25%            | 80        | Minor variation, typical of normal backbone load.                              |
   | > 25% up to and including 50%            | 50        | Noticeable spikes; this is also the band that triggers the flag in Step 6.     |
   | > 50% up to and including 100%           | 20        | Severe spikes — latency-sensitive traffic on this path will have been affected.|
   | > 100%                                   | 0         | The worst reading was more than double the average — a path event or reroute.  |

   - **Composite**: the weighted average of the available sub-scores — drops 30%, packet errors 25%, utilization headroom 25%, latency stability 20% — rounded to the nearest whole number with exact halves rounded up. Report whole numbers only.
   - **Missing components**: if a component has no data, drop it and renormalize the remaining weights to sum to 100%. Worked example — if the packet-error component has no data (e.g. the Z-side is a cloud service profile), the composite is `(0.30 x drops_subscore + 0.25 x utilization_subscore + 0.20 x latency_subscore) / 0.75`. Name every excluded component for that connection in the report, with the reason ("no Z-side port", "local, not measured", "no data", or the metric call error).
   - **No components**: if all four components have no data, the connection is **not scored** — it is excluded from the ranking and counted in the skipped tally with its reason. Never rank an unmeasured connection as 0; that would put a metrics gap at the top of the remediation list and send an operator to investigate a network fault that does not exist.
   - **Tie-breaking**: table lookups make exact ties common — many healthy connections will score 100. Break ties deterministically, in this order: lower `utilization_pct` ranks healthier, then lower `drops_per_hour`, then lower `errors_per_hour`, then lower `latency_spike_pct`, then connection UUID ascending in lexicographic order. A missing input sorts after any present value at that step. The UUID tie-break is the final backstop and guarantees the ranking is a total order, so two runs on identical data produce the same ranking.

6. **Rank** all scored connections from highest (healthiest) to lowest, breaking ties by the rule in Step 5. **Flag** (a simple yes/no) every connection that has at least one obvious, measurable issue over the window:

   - Any non-zero rate-exceeded packet drops, or
   - Any non-zero packet errors on the Z-side port, or
   - p95 rx or tx usage exceeding 80% of provisioned bandwidth, or
   - `latency_spike_pct` above 25% with `latency_spike_ms` of 2 ms or more, or
   - `latency_mean_ms` above `latency_threshold_ms`, when `latency_threshold_ms` is configured. This condition flags the connection but does not change its score.

   A connection with none of these is not flagged. A connection that was not scored is neither flagged nor unflagged — it is reported as skipped.

7. **Recommend remediation for every flagged connection** (from Step 6), tied to the issue(s) present. These are recommendations for a human to action manually — the agent never applies them, so there is no change for it to verify afterwards:

   - Rate-exceeded drops or utilization above 80% → recommend a bandwidth upgrade / review of the connection's rate limit. Where several flagged connections on the same Cloud Router are all capacity-bound, also recommend reviewing whether the Cloud Router package supports the aggregate throughput required.
   - Packet errors → recommend physical-layer / port investigation (cabling, optics) on the affected Z-side port.
   - Latency spikes → recommend opening a case with Equinix Support citing the metro pair, the window, and the mean and max readings, and checking whether the spikes line up with application-level complaints on that path.
   - Mean latency above `latency_threshold_ms` → recommend reviewing Cloud Router placement or the Z-side location, since the latency is a property of the metro pair rather than of the connection.

8. **Retrieve the email template that will be used for the report.** Call `get_email_template`.

9. **Build the report.** Structure the report below using the email template from the previous step. Populate the Summary, the Cloud Router overview, the ranked scorecard table, the flagged-connections section, and the remediation section. Skip any component or section that has no data — no placeholder text.

   ### Header
   **Network Health Scorecard**: `<Cloud Router name>`

   ### Section content
   - **Summary**: 4–6 sentences — the Cloud Router name and metro; the scoring window; the number of connections on the Cloud Router in scope; the number scored; the number skipped for no metric data, with the most common reason; average and median score; the number flagged; and the headline finding. If the connection inventory itself was incomplete (see the failure handling in Step 3), say so before any counts, so no reader mistakes a partial inventory for the Cloud Router's whole network.
   - **Cloud Router Overview**: Cloud Router Name, Cloud Router UUID, Metro, Package, State, and the count of connections by Z-side type (port, cloud service provider, network, virtual device).
   - **Scorecard Ranking**: every scored connection ranked by score. Include Rank, Connection Name, Connection UUID, Z-side Destination, Health Score, and the Top Deductions (which components cost the most points).
   - **Flagged Connections**: every connection with at least one measurable issue (per Step 6), with the primary issue. Include Rank, Connection Name, Connection UUID, Health Score, and Primary Issue. Include only if any exist.
   - **Recommended Remediation**: every flagged connection with its recommended action. Include Rank, Connection Name, Connection UUID, Health Score, Dominant Factor, and Recommended Action. Include only if any exist.
   - **Scoring Method**: one short paragraph stating the weights, the scoring window, and every connection with excluded components and the reason.

10. **Send the report** with `send_email_notification` to `recipient_email_addresses`. Follow the email rules below:

    - `recipients`: `recipient_email_addresses`.
    - `pdfContent`: the full report text from Step 9.
    - `body`: one-paragraph summary of the Cloud Router's overall network health, the coverage actually achieved (scored / skipped counts), and the headline finding.
    - `pdfTitle`: `NetworkHealthScorecard`

    Also present the Summary and the ranked scorecard directly in the conversation, so the run's output survives even if delivery fails. If `send_email_notification` fails, do not retry: print the full Step 9 report text and the delivery error into the conversation, state that the report was produced but not delivered, and end the run.

    Sending this email is the agent's terminal action. Once it is sent the run is complete — do not re-collect metrics, re-score, re-rank, or send a second email, and do not re-check the Cloud Router or any connection. The agent runs again only when its schedule next fires.

## Available Tools

This skill can use the following tools:

- **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"24h"`, `"7d"`).
- **`search_routers`**: Looks up the Cloud Router by UUID and returns its name, state, package, metro, and project.
- **`search_connections`**: Enumerates PROVISIONED connections on the Cloud Router and resolves per-connection context (Z-side access point type, Z-side port UUID, Z-side metro, provisioned bandwidth).
- **`search_metrics`**: Retrieves connection, port, and metro metrics over the scoring window.
- **`get_metric`**: Retrieves a single metric series when a targeted lookup is needed, including each inter-metro latency series.
- **`get_email_template`**: Get email template.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines

- **Advisory only — no remediation actions**: "recommend remediation" in Step 7 means writing a recommended action into the report. This agent performs no restart, reset, failover, bandwidth change, package change, route change, or configuration change of any kind, so no step has an outcome to wait for or poll.
- **One Cloud Router per run**: the agent scores the connections of exactly one Cloud Router. To score several Cloud Routers, create one agent per Cloud Router.
- **Single-resource metric calls**: each `search_metrics` / `get_metric` call can request metrics for only one resource (one connection, port, or metro). Execute one call per resource. If a response is too large to process, split the request by metric name across multiple calls.
- **Default window**: if `scoring_window` is not provided, score over the last 24 hours.
- **Reproducibility**: apply the Step 5 lookup tables, weights, renormalization rule, rounding rule, and tie-break order exactly as written, so the same inputs always produce the same score and the same ranking. State the weights and any renormalization (excluded components) in the report.
- **No retries and no waiting**: every tool call is issued at most once per resource per run. `wait` is intentionally not among the declared tools and no step polls, sleeps, or re-issues a call. Every call this agent makes is a read against telemetry that was already recorded before the run began, so re-issuing a failed call cannot make missing data appear — and the agent takes no action whose outcome would need to be waited on. When a call fails, mark that resource's component as no data, disclose it in the report, and move on. Re-run the agent to pick up a transient failure.
- **Error handling**: failure handling is specified per step in the Instructions, and the conditions under which the run halts without sending an email are enumerated in **Success Criteria & Termination**. Every failure not listed there degrades gracefully — score what returned data, skip the rest, and report the gap.
- **Connection-level error metric is not exposed**: derive packet errors from the Z-side port metrics. The Cloud Router A-side has no port and contributes no error data.
- **Flag anomalies**: call out any non-zero rate-exceeded packet drops, packet errors, or latency spikes as warnings in the report.
- **Known limitation — rate-exceeded drops are not general packet loss**: these counters increment only when offered traffic exceeded the connection's provisioned rate limit. They say nothing about loss caused by a fault in the path.
- **Known limitation — port errors are shared, not per-connection**: a Fabric port carries many connections, and no connection-level error metric is exposed. Every connection on the same Z-side port therefore receives an identical packet-error sub-score, and one dirty port will depress the ranking of every connection on it. When several rows in the scorecard share a port, treat that as one port-level investigation rather than as N independent connection faults, and say so in the Recommended Remediation section, naming the shared port UUID.
- **Known limitation — latency is metro-to-metro, not per-connection**: the latency series measures the Fabric backbone between two metros, not the end-to-end path of an individual connection, and it does not include local access or the cloud provider's own network beyond the Fabric edge. Every connection with the same metro pair receives an identical latency sub-score. When several flagged rows share a metro pair, treat that as one backbone observation, say so in the Recommended Remediation section, and name the metro pair. Connections whose Z-side is in the Cloud Router's own metro are never latency-scored.
- **Known limitation — drops and errors are not loss percentages**: Fabric exposes no per-connection packet-total metric, so these counters are normalized by time only, never by traffic volume. A 50 Mbps and a 10 Gbps connection with the same drops per hour receive the same sub-score even though the fraction of affected traffic differs by orders of magnitude. Do not present or read the drop sub-score as a loss rate.
- **Known limitation — p95 hides bursts**: `usage_summary` p95 excludes the busiest 5% of the window by construction, so a connection saturated for up to roughly 1.2 hours of a 24-hour window can still show a p95 well under 80%. Rate-exceeded drops are the complementary signal: a connection with no utilization flag but non-zero rate-exceeded drops is burst-saturated, and the report should say so rather than presenting the two components as independent.
- **Known limitation — no historical baseline**: every run scores its window in isolation, with no durable state carried between runs. A score is a snapshot, not a trend, and a connection that is newly degrading cannot be distinguished from one that has always been poor. Never describe a score as improving or worsening.
- **Plain English**: no API jargon, no raw metric strings in the narrative, full UUIDs always. Favor insight over raw counts — explain what the score means and why a connection is unhealthy.
- **Graceful skips**: skip connections that have no metric data over the window; note how many were skipped in the Summary. Skip empty sections entirely.
- **Token efficiency**: only call tools when all necessary parameters are present, avoiding unnecessary context loading.

## Configuration

- **`recipient_email_addresses`**: < A list of email addresses > - Required. List of email addresses to receive the scorecard report.
- **`cloud_router_uuid`**: < A Cloud Router UUID > - Required. The Fabric Cloud Router whose connections are scored.
- **`connection_uuids`**: < A list of connection UUIDs > - Optional. Restrict scoring to a specific subset of the Cloud Router's connections. If omitted, all PROVISIONED connections on the Cloud Router are scored.
- **`scoring_window`**: < A time range, e.g. "last 24 hours" > - Optional. The window over which metrics are collected. Default last 24 hours.
- **`latency_threshold_ms`**: < A number of milliseconds > - Optional. If set, any connection whose mean inter-metro latency over the window exceeds this value is flagged. Does not affect the score.
