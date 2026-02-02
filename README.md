# Equinix Agent Factory

Equinix published md agents

Definitive "source of truth" for the Equinix Agent Factory

## Equinix Agent Factory in this repository

The following md files are supported for Equinix Agent Factory

<!-- CATALOG_GENERATION_START -->

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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/ping-and-notify.md">Ping FCR agent<br>[ping-and-notify.md]</a></td>
		<td>This definition sets up and activates an Equinix agent that initiates a PING command on a Fabric Cloud Router in order to perform a network connectivity check.
Once the PING operation is completed, the resulting output is collected and used to generate an email notification.
The email is then sent to the specified recipient, ensuring that the results of the connectivity test are communicated clearly and promptly.
This agent can only run once.</td>
		<td>- PING command on Fabric Cloud Router<br>- Email notification with PING results<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`search_connection`**: Searches for an existing connection.
*   **`create_router_commands`**: Initiate a PING command on a Fabric Cloud Router by UUID.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_router_commands`**: Search for commands (e.g., PING) on a Fabric Cloud Router.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/alert-rule-management.md">Alert Rule Manager<br>[alert-rule-management.md]</a></td>
		<td>This definition sets up and activate an Equinix agent that sets up an alert to a connection.
This agent can only run once.</td>
		<td>- Automatically creates an alert rule based on user-defined parameters<br>- Instantly creates a stream if one does not exist and attaches the resource to it<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_connection`**: Searches for an existing connection.
*   **`get_stream_details`**: Fetches stream details given a stream uuid.
*   **`create_stream`**: Create a stream.
*   **`attach_stream_asset`**: Attach a resource to a stream.
*   **`create_stream_alert_rule`**: Create an alert rule given a stream uuid.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/run_once/upgrade-bw-primary-connection.md">Bandwidth upgrader agent<br>[upgrade-bw-primary-connection.md]</a></td>
		<td>This definition sets up and activate an Equinix agent that upgrades the bandwidth of a connection.
This agent can only run once.</td>
		<td>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_connection`**: Searches for an existing connection.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
</table>


---
### Equinix Fabric   Scheduled

<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
		<th>Release Status</th>
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/scheduled/ping-and-notify.md">Ping FCR agent<br>[ping-and-notify.md]</a></td>
		<td>This definition sets up and activates an Equinix agent that initiates a PING command on a Fabric Cloud Router in order to perform a network connectivity check.
Once the PING operation is completed, the resulting output is collected and used to generate an email notification.
The email is then sent to the specified recipient, ensuring that the results of the connectivity test are communicated clearly and promptly.
This agent is triggered at 10am every day.</td>
		<td>- PING command on Fabric Cloud Router<br>- Email notification with PING results<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`search_connection`**: Searches for an existing connection.
*   **`create_router_commands`**: Initiate a PING command on a Fabric Cloud Router by UUID.
*   **`wait`**: Wait for a while. An optional parameter can be provided to specify the wait time in milliseconds.
*   **`search_router_commands`**: Search for commands (e.g., PING) on a Fabric Cloud Router.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/scheduled/upgrade-fcr-package.md">Cloud Router upgrade package agent<br>[upgrade-fcr-package.md]</a></td>
		<td>This definition sets up and activates an Equinix agent that upgrades the package of a Fabric Cloud Router. 
When the route usage exceeds a predefined threshold, the agent automatically upgrades the Fabric Cloud Router package to ensure sufficient capacity and uninterrupted operation.
This agent is triggered at 6pm on the 15th of February 2026.</td>
		<td>- Automatically upgrade Fabric Cloud Router packages as needed to ensure adequate capacity and prevent service disruption.<br>- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.</td>
		<td>This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`get_next_available_router_package `**: Fetches the next available Fabric Cloud Router package based on a package input.
*   **`update_router`**: Update connection. Used to upgrade bandwidth.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/scheduled/upgrade-bw-primary-connection.md">Scheduled bandwidth upgrader agent<br>[upgrade-bw-primary-connection.md]</a></td>
		<td>This definition sets up and activate an Equinix agent that upgrades the bandwidth of a connection.
This agent is triggered at 3pm every Monday and Wednesday each month.</td>
		<td>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`search_connection`**: Searches for an existing connection.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
</table>


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
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-bw-on-packet-drop-alert.md">Network connection packets drop monitoring and upgrade agent<br>[upgrade-bw-on-packet-drop-alert.md]</a></td>
		<td>This skill sets up and activate an Equinix agent that automatically upgrades the bandwidth of a connection when there are packets drop due to traffic over bw threshold.</td>
		<td>- Monitor real-time network event streams<br>- Detect packet drop alerts<br>- Analyze connection utilization patterns<br>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions<br>- Send notifications for critical events</td>
		<td>This skill can use the following tools:

*   **`search_connection`**: Searches for an existing connection `.
*   **`get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-fcr-package.md">Cloud Router monitoring and upgrade package agent<br>[upgrade-fcr-package.md]</a></td>
		<td>This definition sets up and activates an Equinix agent that continuously monitors route usage on a Fabric Cloud Router. 
When the route usage exceeds a predefined threshold, the agent automatically upgrades the Fabric Cloud Router package to ensure sufficient capacity and uninterrupted operation.</td>
		<td>- Continuously monitor real-time network event streams to maintain visibility into network activity and performance.<br>- Detect and evaluate alerts triggered when route usage reaches or exceeds defined threshold limits.<br>- Automatically upgrade Fabric Cloud Router packages as needed to ensure adequate capacity and prevent service disruption.<br>- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.<br>- Send timely notifications for critical events to ensure stakeholders are informed and can respond promptly.</td>
		<td>This skill can use the following tools:

*   **`search_router`**: Searches for an existing fabric cloud router.
*   **`get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`get_next_available_router_package `**: Fetches the next available Fabric Cloud Router package based on a package input.
*   **`update_router`**: Update connection. Used to upgrade bandwidth.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-bw-primary-connection.md">Network Bandwidth monitoring and upgrade agent<br>[upgrade-bw-primary-connection.md]</a></td>
		<td>This definition sets up and activate an Equinix agent that automatically upgrades the bandwidth of a connection when usage reaches a certain threshold.</td>
		<td>- Monitor real-time network event streams<br>- Detect bandwidth threshold alerts<br>- Analyze connection utilization patterns<br>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions<br>- Send notifications for critical events</td>
		<td>This skill can use the following tools:

* **`search_connection`**: Searches for an existing connection.
* **`get_stream_alert_rule_details`**: Searches for an existing alert rule.
* **`update_connection`**: Update connection. Used to upgrade bandwidth.
* **`get_next_available_bandwidth_tier`**: Fetches the next available billing tier based on a bandwidth input.</td>
		<td>preview
	</tr>
	<tr>
		<td><a href="https://raw.githubusercontent.com/equinix/agent-factory/refs/heads/main/agent_factory_schema/equinix/fabric/v1/event_driven/upgrade-bw-secondary-connection.md">Network Bandwidth monitoring and upgrade agent<br>[upgrade-bw-secondary-connection.md]</a></td>
		<td>This automated agent monitors Equinix Fabric connections and maintains bandwidth parity between redundant connection pairs. 
When bandwidth utilization on a primary connection reaches a configured threshold, the agent automatically upgrades the secondary connection to match the primary connection's bandwidth, ensuring consistent performance across the redundant pair.</td>
		<td>- Real-time Event Monitoring: Continuously monitors network event streams for bandwidth alerts<br>- Threshold Detection: Identifies when connections exceed configured bandwidth utilization thresholds<br>- Redundancy Analysis: Automatically discovers redundant connection pairs and identifies primary/secondary relationships<br>- Intelligent Bandwidth Matching: Upgrades secondary connection bandwidth to match primary connection specifications<br>- Comprehensive Logging: Records all actions, decisions, and state changes for audit and troubleshooting- Monitor real-time network event streams</td>
		<td>This skill can use the following tools:

*   **`search_connection`**: Searches for an existing connection `.
*   **`get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.</td>
		<td>preview
	</tr>
</table>

<!-- CATALOG_GENERATION_END -->