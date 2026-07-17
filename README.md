# Equinix Agent Factory

Equinix published md agents

Definitive "source of truth" for the Equinix Agent Factory

## Equinix Agent Factory in this repository

The following md files are supported for Equinix Agent Factory

<!-- CATALOG_GENERATION_START -->

---
### Equinix Fabric   Event-Driven

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-fcr-package.md">Cloud Router monitoring and upgrade package agent<br>[upgrade-fcr-package.md]</a></td>
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
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-bw-on-packet-drop-alert.md">Network connection packets drop monitoring and upgrade agent<br>[upgrade-bw-on-packet-drop-alert.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/metro-latency-notify.md">Collect connections over metros with latency spikes and notify<br>[metro-latency-notify.md]</a></td>
		<td>An Equinix agent that automatically email a list of connections that are over the metros where latency spike.</td>
		<td>- Detect metro latency alerts<br>- Identify the source and destination metros<br>- Identify the active connections over the metros<br>- Email notification with the connections list<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`search_connections`**: Searches for active connections with aside and zside metro codes
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-bw-primary-connection.md">Network Bandwidth monitoring and upgrade agent<br>[upgrade-bw-primary-connection.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-bw-secondary-connection.md">Network Bandwidth monitoring and upgrade redundant connection agent<br>[upgrade-bw-secondary-connection.md]</a></td>
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


---
### Equinix Fabric   Run-Once

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/project-lifecycle-activities-graph.md">Project Lifecycle Activities Insight Report Agent<br>[project-lifecycle-activities-graph.md]</a></td>
		<td>This reporting agent analyzes all cloud events within a given Equinix Fabric project over a specified time range and delivers a plain-English operational health summary report via email. This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Analyze all cloud events within a given Equinix Fabric project over a specified time range<br>- Detect BGP/routing instability, provisioning churn, and critical events<br>- Deliver a plain-English operational health summary via email as a summarized report in PDF format</td>
		<td>- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
- **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` with `/time` `>=` and `<=` to scope by project and time window.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-graph-seq-smoke-v1.md">SEQUENTIAL runtime smoke agent<br>[test-graph-seq-smoke-v1.md]</a></td>
		<td>The SEQUENTIAL (default, LLM/ReAct-driven) counterpart of `graph-dag-smoke-v1`. Same
task and same tools, but with no `execution_mode` and no `## Steps` block, so the engine
runs it on the default SEQUENTIAL path where the LLM decides tool order. Used to compare
SEQUENTIAL vs DAG execution for the identical workload.</td>
		<td></td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches Fabric virtual connections (read-only).
* **`send_email_notification`**: Sends an email. Pass `emailAddress` and `body`.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/create-cloud-router.md">Cloud Router Creator Agent<br>[create-cloud-router.md]</a></td>
		<td>An Equinix agent that creates a Fabric Cloud Router with user-specified parameters.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically create a Fabric Cloud Router with user-defined configuration<br>- Validate router package availability before creation<br>- Notify the user upon successful creation or failure<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for existing cloud routers. Used to check for duplicates and to confirm post-creation status.
*   **`create_router`**: Creates a new Fabric Cloud Router with the specified configuration.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/ping-and-notify.md">Ping FCR agent<br>[ping-and-notify.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-poll-router-command.md">Poll Router Command Agent<br>[test-poll-router-command.md]</a></td>
		<td>A minimal agent that polls an existing Fabric Cloud Router command until it leaves the pending
state, then emails the final result. This agent runs once immediately by default.</td>
		<td></td>
		<td>*   **`search_router_commands`**: Search for commands (e.g. PING) on a Fabric Cloud Router by uuid.
*   **`send_email_notification`**: Sends an email notification given email addresses and a body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/upgrade-fcr-package.md">Cloud Router upgrade package agent<br>[upgrade-fcr-package.md]</a></td>
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
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/attach-unstreamed-routers-graph.md">Attach Unstreamed Routers to Default Stream<br>[attach-unstreamed-routers-graph.md]</a></td>
		<td>An Equinix agent that reviews existing routers, finds any older than a specified number of hours
that are not yet attached to a stream, and attaches them to the default stream. This agent runs
once immediately by default unless scheduled by user.</td>
		<td>- Find routers older than a specified age that are not attached to any stream<br>- Attach such routers to the default stream<br>- Email notification of the action taken<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Always call this in Step 1 to obtain the reporting window.
*   **`search_routers`**: Search for any routers that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given router.
*   **`attach_stream_asset`**: Attach the router to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-graph-runtime-smoke-v3.md">GRAPH runtime smoke agent<br>[test-graph-runtime-smoke-v3.md]</a></td>
		<td>Verifies that a template with `execution_mode: GRAPH` is routed to the GRAPH
runtime (`GraphExecutor` → `LangGraphReActExecutor`) and runs end to end against a
real, read-only tool. It performs a single read-only connection search and reports
the count. It never creates, updates, or deletes anything.</td>
		<td></td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches for connections (read-only).</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/project-lifecycle-activities.md">Project Lifecycle Activities Insight Report Agent<br>[project-lifecycle-activities.md]</a></td>
		<td>This reporting agent analyzes all cloud events within a given Equinix Fabric project over a specified time range and delivers a plain-English operational health summary report via email. This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Analyze all cloud events within a given Equinix Fabric project over a specified time range<br>- Detect BGP/routing instability, provisioning churn, and critical events<br>- Deliver a plain-English operational health summary via email as a summarized report in PDF format</td>
		<td>- **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Returns a JSON object with `from` and `to` as ISO 8601 UTC strings. Always call this in Step 1 to obtain the reporting window.
- **`search_cloud_events`**: Searches Equinix Fabric cloud events. Use `/equinixproject` `=` with `/time` `>=` and `<=` to scope by project and time window.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/ping-and-notify-graph.md">Ping FCR agent<br>[ping-and-notify-graph.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/default-new-connection-attachment-to-stream-graph.md">Detect connections that are not attached to a stream and notify<br>[default-new-connection-attachment-to-stream-graph.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/pending-state-tracker.md">Pending State Tracker Agent<br>[pending-state-tracker.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-graph-dag-smoke-v1.md">GRAPH/DAG runtime smoke agent<br>[test-graph-dag-smoke-v1.md]</a></td>
		<td>Verifies the GRAPH/DAG runtime (`GraphExecutorDispatcher` → `LangGraphDagExecutor`
→ `GraphBuilder`) end to end in the deployed artifact: a read-only connection
search feeds two deterministic transform functions, an llm node composes a short
report, and the report is emailed. The only mutating action is sending one email
to a fixed internal address.</td>
		<td></td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches Fabric virtual connections (read-only).
* **`send_email_notification`**: Sends an email with the composed report.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/pending-state-tracker-graph.md">Pending State Tracker Agent<br>[pending-state-tracker-graph.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-run-once-create-cloud-router-graph.md">Cloud Router Creator Agent (GRAPH / DAG)<br>[test-run-once-create-cloud-router-graph.md]</a></td>
		<td>The deterministic graph version of the Cloud Router Creator. A single `llm` node parses the
user's free-text parameters into a structured JSON object; the rest of the workflow runs as
typed graph nodes (validate package → create router → confirm) with no further LLM control.
This is the DAG counterpart of `run-once-create-cloud-router` (the SEQUENTIAL version) — same
task, but tool order is fixed by the graph rather than decided by the model each turn.</td>
		<td></td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches Fabric Cloud Routers; used here to confirm the new router.
*   **`create_router`**: Creates a new Fabric Cloud Router.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-qa3-graph-dryrun-smoke.md">GRAPH runtime smoke agent<br>[test-qa3-graph-dryrun-smoke.md]</a></td>
		<td>This template verifies that an agent template with `execution_mode: GRAPH` is
routed to the GRAPH runtime (`GraphExecutor` → `LangGraphReActExecutor`) and that
the executor runs end to end. It performs no mutating action: it lists one
read-only tool to satisfy template validation but instructs the agent never to
call it. A `COMPLETED` activity proves the GRAPH wiring is live.</td>
		<td></td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches for connections. Listed only to satisfy
  template validation; it must not be called by this smoke agent.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/gcp-monitoring.md">GCP Monitoring Agent<br>[gcp-monitoring.md]</a></td>
		<td>An Equinix agent that sends gcp monitoring metrics to an email.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- An automated monitoring solution utilizing an Equinix-hosted agent to track and transmit real-time GCP performance metrics. <br>- This system is designed to provide stakeholders with regular visibility into cloud health by delivering comprehensive metric reports directly to designated email recipients.</td>
		<td>This skill can use the following tools:

*   **`list_timeseries`**: Lists time series data from the Google Cloud Monitoring API.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/upgrade-bw-primary-connection.md">Bandwidth upgrader agent<br>[upgrade-bw-primary-connection.md]</a></td>
		<td>An Equinix agent that upgrades the bandwidth of a connection.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_connections`**: Searches for an existing connection.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/attach-unstreamed-routers.md">Attach Unstreamed Routers to Default Stream<br>[attach-unstreamed-routers.md]</a></td>
		<td>An Equinix agent that reviews existing routers, finds any older than a specified number of hours
that are not yet attached to a stream, and attaches them to the default stream. This agent runs
once immediately by default unless scheduled by user.</td>
		<td>- Find routers older than a specified age that are not attached to any stream<br>- Attach such routers to the default stream<br>- Email notification of the action taken<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:
*   **`get_timestamps`**: Generates `from` and `to` UTC timestamps based on a duration string (e.g., `"24h"`, `"7d"`, `"1M"`). Always call this in Step 1 to obtain the reporting window.
*   **`search_routers`**: Search for any routers that are already provisioned.
*   **`search_attached_assets`**: Search for any streams which may be attached to a given router.
*   **`attach_stream_asset`**: Attach the router to the default stream.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-run-once-create-cloud-router.md">Cloud Router Creator Agent<br>[test-run-once-create-cloud-router.md]</a></td>
		<td>An Equinix agent that creates a Fabric Cloud Router with user-specified parameters.
This agent runs once immediately by default unless scheduled by user.</td>
		<td>- Automatically create a Fabric Cloud Router with user-defined configuration<br>- Validate router package availability before creation<br>- Notify the user upon successful creation or failure<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_routers`**: Searches for existing cloud routers. Used to check for duplicates and to confirm post-creation status.
*   **`create_router`**: Creates a new Fabric Cloud Router with the specified configuration.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-poll-router-command-graph.md">Poll Router Command Agent (GRAPH / DAG)<br>[test-poll-router-command-graph.md]</a></td>
		<td>A minimal agent that polls an existing Fabric Cloud Router command until it leaves the pending
state, then emails the final result. This agent runs once immediately by default.</td>
		<td></td>
		<td>*   **`search_router_commands`**: Search for commands (e.g. PING) on a Fabric Cloud Router by uuid.
*   **`send_email_notification`**: Sends an email notification given email addresses and a body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/alert-rule-management.md">Alert Rule Manager<br>[alert-rule-management.md]</a></td>
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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/test-graph-runtime-smoke-v2.md">GRAPH runtime smoke agent<br>[test-graph-runtime-smoke-v2.md]</a></td>
		<td>This template verifies that an agent template with `execution_mode: GRAPH` is
routed to the GRAPH runtime (`GraphExecutor` → `LangGraphReActExecutor`) and that
the executor runs end to end. It performs no mutating action: it lists one
read-only tool to satisfy template validation but instructs the agent never to
call it. A `COMPLETED` activity proves the GRAPH wiring is live.</td>
		<td></td>
		<td>This skill can use the following tools:

* **`search_connections`**: Searches for connections. Listed only to satisfy
  template validation; it must not be called by this smoke agent.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/traceroute-and-notify.md">TRACEROUTE FCR agent<br>[traceroute-and-notify.md]</a></td>
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
</table>

<!-- CATALOG_GENERATION_END -->