# Equinix Agent Factory

Equinix published md agents

Definitive "source of truth" for the Equinix Agent Factory

## Equinix Agent Factory in this repository

The following md files are supported for Equinix Agent Factory

<!-- CATALOG_GENERATION_START -->

---
## Equinix Fabric On Event Agents

Equinix Fabric Agent Factory Event-Driven Scenarios


### Cloud Router Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_event/cloud-router/cloud-router-upgrade-package.md">Cloud Router Monitoring and Upgrade Package Agent<br>[cloud-router-upgrade-package.md]</a></td>
		<td>An Equinix agent that continuously monitors route usage on a Fabric Cloud Router. 
When the route usage exceeds a predefined threshold, the agent automatically upgrades the Fabric Cloud Router package to ensure sufficient capacity and uninterrupted operation.
This agent only executes once.</td>
		<td>- Continuously monitor real-time network event streams to maintain visibility into network activity and performance.<br>- Detect and evaluate alerts triggered when route usage reaches or exceeds defined threshold limits.<br>- Automatically upgrade Fabric Cloud Router packages as needed to ensure adequate capacity and prevent service disruption.<br>- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.<br>- Send timely notifications for critical events to ensure stakeholders are informed and can respond promptly.</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`get_next_available_router_package `**: Fetches the next available Fabric Cloud Router package based on a package input.
*   **`update_router`**: Update router. Used to upgrade the fabric cloud router.</td>
		<td>preview
	</tr>
</table>

</details>


### Connection Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-high-latency-runbook.md">Connection High Latency Auto-Runbook Agent<br>[connection-high-latency-runbook.md]</a></td>
		<td>An Equinix agent that runs an automated diagnostic runbook when a metro latency alert fires.

It identifies every connection sharing the alerting metro pair, of any connection type. For the subset whose A-side is a Fabric Cloud Router (FCR), it runs a targeted live ping for connectivity readings; other connection types (for example port-to-port or IPWAN-to-port) have no BGP peer to ping and are skipped for this check, with the gap noted in the brief. Bandwidth/utilization headroom is checked for every connection in the blast radius regardless of type. From those per-connection signals, weighed against the shared metro-latency backdrop, it classifies whether the spike is isolated to one connection or metro-wide. It then emails a one-page incident brief with a clearly-labeled likely contributing factor and a recommended next-best action. This agent is diagnostic only. It never modifies a connection, route, or bandwidth setting, and recommendations are for the NOC to action manually.</td>
		<td>- Detect metro high-latency alert cloud events<br>- Identify the full blast radius of connections sharing the alerting metro pair, across all connection types<br>- For connections backed by a Fabric Cloud Router (FCR), resolve the BGP peer IP and run a targeted live ping for connectivity readings; other connection types have no BGP peer to ping and are skipped for this check only<br>- Check bandwidth/utilization headroom per affected connection, regardless of connection type<br>- Classify isolated vs. metro-wide from per-connection ping and headroom signals, against the shared metro-latency backdrop<br>- Produce a diagnostic incident brief with a labeled "likely contributing factor"<br>- Recommend a concrete next-best action for the NOC to take manually<br>- Email the brief as a PDF report<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"1h"`, `"6h"`). Used to establish the recent lookback window for this agent.
*   **`get_stream_alert_rule_details`**: Fetches the full details of an alert rule (thresholds, window size). Takes the **stream UUID** and the **alert-rule UUID** as two separate arguments — both are parsed from `data.alertRule` on the event.
*   **`search_connections`**: Searches for connections by A-side/Z-side metro code to resolve the blast radius, and resolves provisioned bandwidth and A-side router UUID per connection.
*   **`list_routing_protocols`**: Fetches routing protocols for a connection; used to read the BGP `customerPeerIp` as the default FCR ping destination.
*   **`create_router_commands`**: Initiates a PING command on a Fabric Cloud Router by UUID.
*   **`search_router_commands`**: Searches for commands (e.g. PING) on a Fabric Cloud Router.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_metrics`**: Retrieves connection bandwidth-usage and metro-latency time series over the lookback window.
*   **`get_metric`**: Retrieves a single metric series when a targeted lookup is needed.
*   **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-metro-latency-notify.md">Metro Latency Spikes and Connections Over Metros Report Agent<br>[connection-metro-latency-notify.md]</a></td>
		<td>An Equinix agent that automatically email a list of connections that are over the metros where latency spike.</td>
		<td>- Detect metro latency alerts<br>- Identify the source and destination metros<br>- Identify the active connections over the metros<br>- Email notification with the connections list<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`search_connections`**: Searches for active connections with aside and zside metro codes
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-upgrade-bw-on-packet-drop-alert.md">Connection Packet Drop Monitoring and Upgrade Agent<br>[connection-upgrade-bw-on-packet-drop-alert.md]</a></td>
		<td>An Equinix agent that automatically boosts connection bandwidth to mitigate traffic-induced packet loss.
This agent only executes once.</td>
		<td>- Monitor real-time network event streams<br>- Detect packet drop alerts<br>- Analyze connection utilization patterns<br>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions<br>- Send notifications for critical events</td>
		<td>This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection `.
*   **`get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-upgrade-bw-primary.md">Connection Bandwidth Monitoring and Upgrade Agent<br>[connection-upgrade-bw-primary.md]</a></td>
		<td>An Equinix agent that automatically upgrades the bandwidth of a connection when usage reaches a certain threshold. 
This agent only executes once.</td>
		<td>- Monitor real-time network event streams<br>- Detect bandwidth threshold alerts<br>- Analyze connection utilization patterns<br>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions<br>- Send notifications for critical events</td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches for an existing connection.
* **`get_stream_alert_rule_details`**: Searches for an existing alert rule.
* **`update_connection`**: Update connection. Used to upgrade bandwidth.
* **`get_next_available_bandwidth_tier`**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-upgrade-bw-secondary.md">Connection Bandwidth Monitoring and Upgrade Redundant Connection Agent<br>[connection-upgrade-bw-secondary.md]</a></td>
		<td>This automated agent monitors Equinix Fabric connections and maintains bandwidth parity between redundant connection pairs. 
When bandwidth utilization on a primary connection reaches a configured threshold, the agent automatically upgrades the secondary connection to match the primary connection's bandwidth, ensuring consistent performance across the redundant pair.
This agent only executes once.</td>
		<td>- Monitor real-time network event streams<br>- Detect bandwidth threshold alerts<br>- Analyze connection utilization patterns<br>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions<br>- Send notifications for critical events</td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches for an existing connection.
* **`get_stream_alert_rule_details`**: Searches for an existing alert rule.
* **`update_connection`**: Update connection. Used to upgrade bandwidth.</td>
		<td>preview
	</tr>
</table>

</details>


---
## Equinix Fabric On Schedule Agents

Equinix Fabric Agent Factory On Schedule and On Demand Scenarios


### Asset Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/asset/asset-change-daily-logger.md">Daily Asset Change Report Agent<br>[asset-change-daily-logger.md]</a></td>
		<td>An Equinix Agent that identifies connections, ports, cloud routers, networks, internet access, and network edge change events in past 24 hours.
This agent compile change summary with owners and distribute a daily report.</td>
		<td>- Analyze all cloud events within a given Equinix Fabric project over the past 24 hours<br>- Deliver a plain-English daily report for changed assets summary via email as a summarized report in PDF format</td>
		<td>- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
- **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` with `/time` `>=` and `<=` to scope by project and time window.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/asset/asset-create-daily-report.md">Daily Asset Creation Report Agent<br>[asset-create-daily-report.md]</a></td>
		<td>An Equinix Agent that identifies connections, ports, cloud routers, networks, internet access, and network edge creation events in past 24 hours.
This agent compile creation summary with owners and distribute a daily report.</td>
		<td>- Analyze all cloud events within a given Equinix Fabric project over the past 24 hours<br>- Deliver a plain-English daily report for created assets summary via email as a summarized report in PDF format</td>
		<td>- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
- **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` with `/time` `>=` and `<=` to scope by project and time window.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/asset/asset-pending-state-tracker.md">Asset Pending State Tracker Agent<br>[asset-pending-state-tracker.md]</a></td>
		<td>This agent actively analyzes the lifecycle state of Equinix Fabric assets to identify those stuck in provisioning or deprovisioning phases for an extended period, proactively notifying user.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Analyze all pending connections, ports, and routers over a specified time range<br>- Deliver a plain-English summary via email as a PDF report</td>
		<td>- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/asset/project-lifecycle-activities.md">Project Lifecycle Activities Insight Report Agent<br>[project-lifecycle-activities.md]</a></td>
		<td>This reporting agent analyzes all cloud events within a given Equinix Fabric project over a specified time range and delivers a plain-English operational health summary report via email. This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Analyze all cloud events within a given Equinix Fabric project over a specified time range<br>- Detect BGP/routing instability, provisioning churn, and critical events<br>- Deliver a plain-English operational health summary via email as a summarized report in PDF format</td>
		<td>- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
- **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` with `/time` `>=` and `<=` to scope by project and time window.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/asset/resource-stuck-state-timeout-notifier.md">Resource Stuck State Timeout Notifier Agent<br>[resource-stuck-state-timeout-notifier.md]</a></td>
		<td>This agent identifies Equinix Fabric connections, ports, and routers stuck in a PROVISIONING or DEPROVISIONING state past a configurable timeout.
This agent runs once immediately by default unless scheduled by user, and emails a report of the affected resources.
This agent is read-only — it never modifies, upgrades, or cancels any resource.

Differs from `asset-pending-state-tracker` and `connection-pending-state-tracker`: this agent applies separate
configurable timeouts for `PROVISIONING` vs. `DEPROVISIONING`, and enriches each stuck connection/port with its
most recent related cloud event for extra context.</td>
		<td>- Analyze all connections, ports, and routers currently in a provisioning or deprovisioning state<br>- Flag only the resources that have exceeded a state-specific timeout<br>- Deliver a plain-English summary via email as a PDF report</td>
		<td>- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`search_cloud_events_by_asset`**: Retrieves recent cloud events for a given connection or port UUID. Not supported for routers.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`). Use the `to` field as the current UTC time reference for calculating elapsed minutes. Do not compute or hardcode the current time manually.
- **`wait`**: Wait for a while before retrying a failed search call. An optional parameter can be provided to specify the wait time in milliseconds.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
</table>

</details>


### Cloud Router Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-attachment-audit.md">Cloud Router Attachment Audit Agent<br>[cloud-router-attachment-audit.md]</a></td>
		<td>An Equinix agent that audits Fabric Cloud Routers to detect routers that are unmonitored and attach to stream.
After collecting the full inventory of PROVISIONED routers, excluding those that are already attached to streams, the agent automatically attaches the unattached routers to the stream provided in configuration prompt:
attaching all routers if there are fewer than 5, or only the first 5 routers if there are more — without asking the
user to confirm. It then sends an email report listing which routers were attached and which were left
unattached. This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Paginate through all Fabric Cloud Routers <br>- Use `search_attached_assets` across every stream to determine which routers are already attached<br>- Identify unattached (unmonitored) routers by cross-referencing router UUIDs against attached assets<br>- Automatically attach unattached routers (up to a maximum of 5) to the configured stream, without user confirmation<br>- Send an email report listing every router that was attached and every router that was left unattached</td>
		<td>This skill can use the following tools:

- **`search_routers`**: Searches for existing provisioned Fabric Cloud Routers with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`search_attached_assets`**: Returns all routers attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a router to a stream by asset UUID and stream UUID with `"metrics_enabled": false`.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-bgp-bfd-enabler.md">Cloud Router BGP BFD Enabler Agent<br>[cloud-router-bgp-bfd-enabler.md]</a></td>
		<td>An Equinix agent that scans all provisioned Fabric Cloud Router connections whose bandwidth exceeds a configurable threshold, identifies those with an existing BGP routing protocol where BFD is not yet enabled, enables BFD on each qualifying BGP session, and sends a completion email report summarizing all changes made.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Search for all provisioned FCR connections exceeding a configurable bandwidth threshold (default 1 Gbps)<br>- Inspect each connection's routing protocols and identify BGP sessions with BFD disabled<br>- Enable BFD on qualifying BGP routing protocols using a configurable interval<br>- Skip connections where BFD is already enabled or where no BGP routing protocol exists<br>- Send a completion email report listing updated, skipped, and failed connections</td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches for provisioned FCR connections filtered by bandwidth.
* **`list_routing_protocols`**: Lists all routing protocols for a given connection.
* **`replace_routing_protocol`**: Replaces a routing protocol configuration; used here to enable BFD on an existing BGP session while preserving all other fields.
* **`wait`**: Waits for a specified number of milliseconds before the next action.
* **`send_email_notification`**: Sends an email notification with an optional PDF report.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-bgp-boostrap-provisioner.md">Cloud Router BGP Bootstrap Provisioner Agent<br>[cloud-router-bgp-boostrap-provisioner.md]</a></td>
		<td>An Equinix agent targets a connection that is pending interface configuration, sets up a standard BGP routing protocol, and sends a completion notification with final execution outcome.
The agent is set up BGP routing protocol using ASN, BFD enabled, or MD5 authentication.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Detect new or updated connections missing routing protocol configuration<br>- Create a baseline BGP routing protocol with required defaults<br>- Enable BFD as part of the standard BGP profile<br>- Configure MD5 authentication for BGP sessions<br>- Send completion notifications with success/failure outcomes</td>
		<td>This skill can use the following tools:

* **`search_connections`**: Retrieves connection details.
* **`list_routing_protocols`**: Retrieves existing routing protocols for a connection.
* **`create_routing_protocol`**: Creates a routing protocol for the target connection.
* **`wait`**: Waits for a specified number of milliseconds before the next action.
* **`send_email_notification`**: Sends an email notification.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-connection-bgp-health-report.md">Cloud Router Connection BGP Session Restart Agent (Scheduled Batch)<br>[cloud-router-connection-bgp-health-report.md]</a></td>
		<td>An Equinix scheduled agent that evaluates BGP session health for Fabric Cloud Router backed connections and performs narrow bounded remediation only when needed.

This run is initiated by schedule and discovers unhealthy sessions from live API state rather than from a triggering BGP status event.

Because BGP is a self-healing protocol, the agent first waits and observes for a bounded grace period before attempting any restart. It attempts exactly one remediation tier per affected session/address family: a soft restart by toggling the routing protocol address family's `enabled` flag (disable, then re-enable). It never retries this toggle in the same run, never performs peer reset, and never performs path failover.

This agent runs once immediately by default unless scheduled by the user. It sends at most one batched email report at the end of a run: always when unhealthy BGP sessions are detected, and optionally on clean runs when `send_email_on_clean_run` is enabled.

All tool-facing request details that matter for execution — including the `search_connections` filter shape, the `search_cloud_events` filter operators, and the HTML report template — are intentionally kept explicit below and should be preserved.</td>
		<td>- Run on schedule and evaluate BGP health across a scoped set of FCR-attached connections<br>- Support optional `connection_uuid` override to target one connection<br>- Support optional `fcr_uuid` to scope discovery to connections attached to that cloud router<br>- Discover BGP routing protocols and evaluate both `bgpIpv4` and `bgpIpv6` families when present<br>- Skip non-actionable states (still provisioning, administratively disabled, already healthy)<br>- Detect flap storms from recent cloud events before remediation<br>- Wait for natural BGP recovery (self-heal grace period) before restarting<br>- Attempt one soft restart (disable/wait/enable/wait) only for the affected unhealthy session family<br>- Verify post-restart recovery within bounded polling limits<br>- Aggregate all findings/actions into one batched incident email with PDF attachment per notification policy (`send_email_on_clean_run`)<br>- Log all per-item decisions, actions, and errors</td>
		<td>This skill can use the following tools:

* **`search_connections`**: Finds connections by UUID or by scoped filter and reads connection state.
* **`list_routing_protocols`**: Reads routing protocols for a connection, including `state`, family `enabled`, and operation status fields.
* **`get_timestamps`**: Produces UTC `from`/`to` timestamps from a duration (for flap-storm lookback).
* **`search_cloud_events`**: Counts recent BGP status events for a connection to detect flap storms. Use `/equinixproject` with `=` plus `/subject` with `IN` and `/type` with `LIKE`.
* **`update_routing_protocol`**: Applies JSON Patch operations for `enabled` toggles.
* **`wait`**: Sleeps between checks and restart phases.
* **`send_email_notification`**: Sends exactly one batched email report with attached PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-management.md">Cloud Router Management Agent<br>[cloud-router-management.md]</a></td>
		<td>An Equinix agent that creates a Fabric Cloud Router with user-specified parameters.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically create a Fabric Cloud Router with user-defined configuration<br>- Validate router package availability before creation<br>- Notify the user upon successful creation or failure<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for existing cloud routers. Used to check for duplicates and to confirm post-creation status.
*   **`create_router`**: Creates a new Fabric Cloud Router with the specified configuration.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-ping-and-notify.md">Cloud Router Ping and Report Agent<br>[cloud-router-ping-and-notify.md]</a></td>
		<td>An Equinix agent that initiates a PING command on a Fabric Cloud Router in order to perform a network connectivity check.
Once the PING operation is completed, the resulting output is collected and used to generate an email notification.
The email is then sent to the specified recipient, ensuring that the results of the connectivity test are communicated clearly and promptly.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- PING command on Fabric Cloud Router<br>- Email notification with PING results<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`search_connections`**: Searches for an existing connection.
*   **`create_router_commands`**: Initiate a PING command on a Fabric Cloud Router by UUID.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_router_commands`**: Search for commands (e.g., PING) on a Fabric Cloud Router.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-route-aggregation-recommendation.md">Cloud Router Route Aggregation Recommendation Agent<br>[cloud-router-route-aggregation-recommendation.md]</a></td>
		<td>An Equinix agent that recommends, or suggests, aggregate routes for a Fabric Cloud Router.
The agent analyzes the router's active route table entries and suggests an optimized set of aggregate (supernet) IPv4 routes to simplify route advertisement and reduce route table size.
A router UUID is required, and a connection UUID is optional but recommended for more accurate, connection-scoped aggregation.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Recommend an optimized set of aggregate (supernet) IPv4 routes for a Fabric Cloud Router based on its active route table entries.<br>- Optionally scope the recommendation to a specific connection on the router for higher accuracy.<br>- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for an existing Fabric Cloud Router. Used to confirm the router UUID before generating recommendations.
*   **`search_routes`**: Searches the routing table of a Fabric Cloud Router. Use `route_type` = `active` to retrieve the router's active route table entries, optionally scoped to a connection via `connection_uuid`. Each returned route exposes a `prefix` field (the CIDR entry) to feed into aggregation.
*   **`recommend_route_aggregation`**: Recommends or suggests aggregate routes. Given a list of route prefixes (`routePrefixes`) and an optional `connectionUuid`, it excludes IPv6 prefixes, performs deterministic CIDR aggregation on the IPv4 prefixes, and returns the recommended aggregate IPv4 routes.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-traceroute-and-notify.md">Cloud Router Traceroute and Report Agent<br>[cloud-router-traceroute-and-notify.md]</a></td>
		<td>An Equinix agent that initiates a TRACEROUTE command on a Fabric Cloud Router in order to perform a network connectivity check.
Once the TRACEROUTE operation is completed, the resulting output is collected and used to generate an email notification.
The email is then sent to the specified recipient, ensuring that the results of the connectivity test are communicated clearly and promptly.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- TRACEROUTE command on Fabric Cloud Router<br>- Email notification with TRACEROUTE results<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`search_connections`**: Searches for an existing connection.
*   **`create_router_commands`**: Initiate a TRACEROUTE command on a Fabric Cloud Router by UUID.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_router_commands`**: Search for commands (e.g., TRACEROUTE) on a Fabric Cloud Router.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-upgrade-package.md">Cloud Router Upgrade Package Agent<br>[cloud-router-upgrade-package.md]</a></td>
		<td>This definition sets up and activates an Equinix agent that upgrades the package of a Fabric Cloud Router. 
When the route usage exceeds a predefined threshold, the agent automatically upgrades the Fabric Cloud Router package to ensure sufficient capacity and uninterrupted operation.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically upgrade Fabric Cloud Router packages as needed to ensure adequate capacity and prevent service disruption.<br>- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for an existing fabric cloud router.
*   **`get_next_available_router_package `**: Fetches the next available Fabric Cloud Router package based on a package input.
*   **`update_router`**: Update router. Used to upgrade the fabric cloud router.</td>
		<td>preview
	</tr>
</table>

</details>


### Connection Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/connection/connection-attachment-audit.md">Connection Attachment Audit Agent<br>[connection-attachment-audit.md]</a></td>
		<td>An Equinix agent that audits Fabric connections to detect that are unmonitored and attach to stream.
After collecting the full inventory of PROVISIONED connections, excluding those that are already attached to streams, the agent automatically attaches the unattached connections to the stream provided in configuration prompt:
attaching all connections if there are fewer than 5, or only the first 5 connections if there are more — without asking the
user to confirm. It then sends an email report listing which connections were attached and which were left
unattached. This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Paginate through all Fabric Connections <br>- Use `search_attached_assets` across every stream to determine which connections are already attached<br>- Identify unattached (unmonitored) connections by cross-referencing connection UUIDs against attached assets<br>- Automatically attach unattached connections (up to a maximum of 5) to the configured stream, without user confirmation<br>- Send an email report listing every connection that was attached and every connection that was left unattached</td>
		<td>This skill can use the following tools:

- **`search_connections`**: Searches for existing provisioned Fabric Connections with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`search_attached_assets`**: Returns all connections attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a connection to a stream by asset UUID and stream UUID with `"metrics_enabled": true`.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/connection/connection-health-scorecard.md">Connection Health Scorecard Agent<br>[connection-health-scorecard.md]</a></td>
		<td>An Equinix Agent that gives operators a single-pane health view across Equinix Fabric connections. It collects per-connection performance metrics, computes a composite 0 to 100 health score for each connection, ranks them, flags any connection with an obvious measurable issue, and recommends remediation for every flagged connection.
This agent helps troubleshooting effort so it can be prioritized where it matters most. The result is delivered as a PDF scorecard via email.
This agent is advisory only. It reads telemetry and writes recommendations into a report; it never modifies a connection, its bandwidth, or its rate limit.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Enumerate all PROVISIONED connections (or a user-specified subset)<br>- Collect rate-exceeded packet drops, packet errors, and utilization metrics per connection<br>- Compute a reproducible composite 0–100 health score per connection<br>- Rank all connections and flag any with an obvious measurable issue<br>- Recommend concrete remediation for every flagged connection<br>- Deliver a prioritized scorecard as a PDF report via email</td>
		<td>This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"24h"`, `"7d"`).
*   **`search_connections`**: Enumerates PROVISIONED connections and resolves per-connection context (A-side and Z-side port UUIDs, provisioned bandwidth).
*   **`search_metrics`**: Retrieves connection and port metrics over the scoring window.
*   **`get_metric`**: Retrieves a single metric series when a targeted lookup is needed.
*   **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/connection/connection-pending-state-tracker.md">Connection Pending State Tracker Agent<br>[connection-pending-state-tracker.md]</a></td>
		<td>This agent analyzes the lifecycle state of Equinix Fabric connections to identify those stuck in provisioning or deprovisioning state longer than a configured threshold, proactively notifying the user when action may be needed.
This agent runs once immediately by default unless scheduled by user. Recommended schedule: every 4 hours. Only sends email if connections exceed the timeout threshold.</td>
		<td>- Search for all connections currently in a pending (provisioning or deprovisioning) state<br>- Deliver a plain-English summary via email</td>
		<td>- **`search_connections`**: Searches for connections.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a required duration string (e.g., `"24h"`, `"7d"`). `to` is always the current UTC time; `from` is `to` minus the duration. Use the `to` field as the current UTC time reference for calculating time-in-state. Do not compute or hardcode the current time manually.
- **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/connection/connection-upgrade-bw-primary.md">Connection Bandwidth Upgrade Agent<br>[connection-upgrade-bw-primary.md]</a></td>
		<td>An Equinix agent that upgrades the bandwidth of a connection.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
</table>

</details>


### Network Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/network/network-connection-orchestrator.md">Network Connection Orchestrator Agent<br>[network-connection-orchestrator.md]</a></td>
		<td>Creates a Fabric Network of a supported type and connects a caller-supplied list of existing access points to it, then waits for each connection to provision, attaches the provisioned connections to an observability stream, and sends a completion report.

Supported network types are EVPLAN, EPLAN, EVPTREE, EPTREE, and IPWAN. Access points are Ports for the Layer2 network types and existing Cloud Routers for IPWAN. Unlike agents that provision the far-end resource themselves (for example the IPWAN and Cloud Router Network Setup agent, which creates its own Cloud Router), this agent never creates a Port or Cloud Router; it only accepts UUIDs of resources that already exist. This keeps its scope to network, connections, and observability, and avoids duplicating router or port provisioning logic owned elsewhere.

The agent creates the Network, waits for it to become `ACTIVE`, then creates one connection per listed access point (Port→Network for Layer2 types, Cloud Router→Network for IPWAN), waits for each connection's `operation.equinixStatus` to reach `PROVISIONED`, attaches the successfully provisioned connections to a stream (creating one if needed — the Network itself cannot be attached to a stream), and sends a single completion report covering every item's outcome.

This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Create a Fabric Network of type `EPLAN`, `EVPLAN`, `EPTREE`, `EVPTREE`, or `IPWAN`<br>- Accept a list of existing access points (Ports for Layer2 network types; existing Cloud Routers for IPWAN) and create one connection per entry, linking each to the new Network<br>- Poll the Network and every created connection independently until each reaches its ready state, or times out<br>- Create a stream automatically if no stream UUID is provided, then attach every successfully provisioned connection to it (Networks cannot be attached to a stream; pre-existing source Ports/Cloud Routers are never attached — only the connections this run creates)<br>- Send a single email completion report itemizing the outcome of the Network and every requested connection</td>
		<td>This skill can use the following tools:

- **`create_network`**: Creates a Fabric Network. Accepts name, type, scope (`LOCAL`, `REGIONAL`, or `GLOBAL`), location (region or metro code, as applicable to scope), notifications (mandatory), and project UUID.
- **`search_networks`**: Searches for existing Fabric Networks by filter, used to poll state.
- **`create_connection`**: Creates a connection. Used to create one connection per source access point, linking it to the Network. Accepts notifications.
- **`search_connections`**: Searches for existing connections by filter, used to poll provisioning state via `/operation/equinixStatus`.
- **`get_stream_details`**: Fetches stream details given a stream UUID.
- **`create_stream`**: Creates a new stream. Accepts a stream type (for example TELEMETRY_STREAM), name, description, and project UUID.
- **`attach_stream_asset`**: Attaches an asset to a stream. Accepts the stream UUID, an asset type (set it to "connection"), the asset UUID (the connection's UUID), and a request body that enables metrics collection. Networks cannot be attached to a stream — there is no network asset type.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/network/ipwan-fcr-network-setup.md">IPWAN & Cloud Router Network Setup Agent<br>[ipwan-fcr-network-setup.md]</a></td>
		<td>An Equinix agent that provisions a single IPWAN-based network topology with FCR. 
It creates one Network, one Cloud Router at a user-specified metro location, and one IPWAN connection linking the Cloud Router to the network. After the Cloud Router and connection reach PROVISIONED state the agent attaches them to a stream (creating one if needed; the Network itself cannot be attached to a stream) and sends a completion summary via email.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Create a Fabric Network of type IPWAN scoped to a project<br>- Create one Cloud Router at the specified metro location with a configurable package<br>- Create one IPWAN connection between the Cloud Router and the network<br>- Poll all resources until they reach PROVISIONED state before proceeding<br>- Create a stream automatically if no stream UUID is provided, then attach the provisioned Cloud Router and connection to it (networks cannot be attached to a stream)<br>- Send an email completion report summarizing all created resources and their states</td>
		<td>This skill can use the following tools:

- **`create_network`**: Creates a Fabric Network. Accepts name, type (`IPWAN`), scope (`REGIONAL` or `GLOBAL`), location (region or metro code), notifications (mandatory), and project UUID.
- **`search_networks`**: Searches for existing Fabric Networks by filter.
- **`create_router`**: Creates a Fabric Cloud Router. Accepts name, location (metro code), package, billing account number, notifications (mandatory), and project UUID.
- **`search_routers`**: Searches for existing Fabric Cloud Routers by filter to check provisioning state.
- **`create_connection`**: Creates a connection. Used to create IPWAN connections between a Cloud Router and a Network. Accepts notifications.
- **`search_connections`**: Searches for existing connections to verify provisioning state.
- **`get_stream_details`**: Fetches stream details given a stream UUID.
- **`create_stream`**: Creates a new stream given a name and project UUID.
- **`attach_stream_asset`**: Attaches a resource (router or connection) to a stream by UUID. Networks cannot be attached to a stream.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.</td>
		<td>preview
	</tr>
</table>

</details>


### Port Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/port/port-attachment-audit.md">Port Attachment Audit Agent<br>[port-attachment-audit.md]</a></td>
		<td>An Equinix agent that audits all Fabric Ports to detect ports that are unmonitored then attachs them to stream. 
After collecting the full inventory of PROVISIONED ports, excluding those that are already attached to streams, the agent automatically attaches the unattached ports to the stream provided in configuration prompt:
attaching all ports if there are fewer than 5, or only the first 5 ports if there are more — without asking the
user to confirm. It then sends an email report listing which ports were attached and which were left
unattached. This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Paginate through all Fabric Ports <br>- Use `search_attached_assets` across every stream to determine which ports are already attached<br>- Identify unattached (unmonitored) ports by cross-referencing port UUIDs against attached assets<br>- Automatically attach unattached ports (up to a maximum of 5) to the configured stream, without user confirmation<br>- Send an email report listing every port that was attached and every port that was left unattached</td>
		<td>This skill can use the following tools:

- **`search_ports`**: Searches for existing provisioned Fabric Ports with pagination support.
- **`list_streams`**: Lists all streams available in the account.
- **`search_attached_assets`**: Returns all ports attached to a given stream UUID.
- **`attach_stream_asset`**: Attaches a port to a stream by asset UUID and stream UUID with `"metrics_enabled": true`.
- **`wait`**: Waits for a specified number of milliseconds before the next action.
- **`send_email_notification`**: Sends an email notification to a list of recipients with an optional PDF attachment.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/port/port-pending-state-tracker.md">Port Pending State Tracker Agent<br>[port-pending-state-tracker.md]</a></td>
		<td>This agent analyzes the lifecycle state of Equinix Fabric ports to identify those stuck in provisioning or deprovisioning state longer than a configured threshold, proactively notifying the user when action may be needed.
This agent runs once immediately by default unless scheduled by user. Recommended schedule: every 4 hours. Only sends email if ports exceed the timeout threshold.</td>
		<td>- Search for all ports currently in a pending (provisioning or deprovisioning) state<br>- Deliver a plain-English summary via email</td>
		<td>- **`search_ports`**: Searches for ports.
- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a required duration string (e.g., `"24h"`, `"7d"`). `to` is always the current UTC time; `from` is `to` minus the duration. Use the `to` field as the current UTC time reference for calculating time-in-state. Do not compute or hardcode the current time manually.
- **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
</table>

</details>


### Stream Agents

<details>
<summary>Show agents</summary>

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/stream/alert-rule-management.md">Alert Rule Manager Agent<br>[alert-rule-management.md]</a></td>
		<td>An Equinix agent that sets up an alert rule for a connection.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically creates an alert rule based on user-defined parameters<br>- Instantly creates a stream if one does not exist and attaches the resource to it<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection.
*   **`get_stream_details`**: Fetches stream details given a stream uuid.
*   **`create_stream`**: Create a stream.
*   **`attach_stream_asset`**: Attach a resource to a stream.
*   **`create_stream_alert_rule`**: Create an alert rule given a stream uuid.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/stream/stream-attachment-connection-finder.md">Stream Attachment Connection Finder Agent<br>[stream-attachment-connection-finder.md]</a></td>
		<td>An Equinix agent that automatically detects new connections older than a certain amount of time and ensures they are at least connected to the default stream.</td>
		<td>- Detect older connections that are not attached to any stream<br>- Attach such connections to the default stream<br>- Email notification of this action to the user<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
*   **`search_connections`**: Search for any connections that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given connection.
*   **`attach_stream_asset`**: Attach the connection to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/stream/stream-attachment-port-finder.md">Stream Attachment Port Finder Agent<br>[stream-attachment-port-finder.md]</a></td>
		<td>An Equinix agent that automatically detects new ports older than a certain amount of time and ensures they are at least connected to the default stream.</td>
		<td>- Detect older ports that are not attached to any stream<br>- Attach such ports to the default stream<br>- Email notification of this action to the user<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
*   **`search_ports`**: Search for any ports that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given port.
*   **`attach_stream_asset`**: Attach the port to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/stream/stream-attachment-router-finder.md">Stream Attachment Cloud Router Finder Agent<br>[stream-attachment-router-finder.md]</a></td>
		<td>An Equinix agent that automatically detects new routers older than a certain amount of time and ensures they are at least connected to the default stream.</td>
		<td>- Detect older routers that are not attached to any stream<br>- Attach such routers to the default stream<br>- Email notification of this action to the user<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
*   **`search_routers`**: Search for any routers that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given router.
*   **`attach_stream_asset`**: Attach the router to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
</table>

</details>

<!-- CATALOG_GENERATION_END -->