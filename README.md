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
		<td>This agent identifies Equinix Fabric connections, ports, and routers stuck in a `PROVISIONING` or `DEPROVISIONING` state past a configurable timeout.
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/on_schedule/cloud-router/cloud-router-dry-run.md">Fabric Cloud Router dry-run validator agent<br>[cloud-router-dry-run.md]</a></td>
		<td>Validate a new Equinix Fabric Cloud Router (FCR) request by calling the `create_router` tool with `dry_run: true`. This validates the full request — package availability in the target metro, quota limits, and account permissions — without creating the router. Return the dry-run result to the user. Do not proceed to real creation under any circumstances.</td>
		<td>- Execute the FCR validation (dry-run) API before creation<br>- Verify package availability in the target metro<br>- Check quota limits (e.g. the 3-Lab-per-org cap)<br>- Validate account permissions<br>- Surface errors early with clear remediation<br>- Never proceed to real creation — this skill is validation-only</td>
		<td>- **`create_router`**: Call with `dry_run: true` to validate without provisioning. This is the only call this skill makes.
- **`list_metro`**: Get available metro locations (used for remediation if metro check fails).
- **`get_router_package`**: Get fabric cloud router package details (used for remediation if package check fails).</td>
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
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Enumerate all PROVISIONED connections (or a user-specified subset)<br>- Collect rate-exceeded packet drops, packet errors, utilization, and latency metrics per connection<br>- Compute a reproducible composite 0–100 health score per connection<br>- Rank all connections and flag any with an obvious measurable issue<br>- Recommend concrete remediation for every flagged connection<br>- Deliver a prioritized scorecard as a PDF report via email</td>
		<td>This skill can use the following tools:

*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps (ISO 8601) from a duration string (e.g. `"24h"`, `"7d"`).
*   **`search_connections`**: Enumerates PROVISIONED connections and resolves connection context (A/Z ports, A/Z metro codes, provisioned bandwidth).
*   **`search_metrics`**: Retrieves connection, port, and metro metrics over the scoring window.
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