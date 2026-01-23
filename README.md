# Equinix Agent Factory

Equinix published [CloudEvent](https://cloudevents.io/) Types

Definitive "source of truth" for the Equinix Agent Factory

## Equinix Agent Factory in this repository

The following data are the supported md files for Equinix Agent Factory

<!-- CATALOG_GENERATION_START -->
<table>
	<tr>
		<th>Name</th>
		<th>Overview</th>
		<th>Capabilities</th>
		<th>Agent Tools</th>
	</tr>
	<tr>
		<td>Bandwidth upgrader agent</td>
		<td>This definition sets up and activate an Equinix agent that upgrades the bandwidth of a connection.
This agent can only run once.</td>
		<td>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`fabric_search_connection`**: Searches for an existing connection.
*   **`fabric_update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`fabric_get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.
	</tr>
	<tr>
		<td>Cloud Router monitoring and upgrade package agent</td>
		<td>This definition sets up and activates an Equinix agent that continuously monitors route usage on a Fabric Cloud Router. 
When the route usage exceeds a predefined threshold, the agent automatically upgrades the Fabric Cloud Router package to ensure sufficient capacity and uninterrupted operation.</td>
		<td>- Continuously monitor real-time network event streams to maintain visibility into network activity and performance.<br>- Detect and evaluate alerts triggered when route usage reaches or exceeds defined threshold limits.<br>- Automatically upgrade Fabric Cloud Router packages as needed to ensure adequate capacity and prevent service disruption.<br>- Record and log all actions, decisions, and system events for auditing, troubleshooting, and analysis purposes.<br>- Send timely notifications for critical events to ensure stakeholders are informed and can respond promptly.</td>
		<td>This skill can use the following tools:

*   **`fabric_search_router`**: Searches for an existing fabric cloud router.
*   **`fabric_get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`fabric_get_next_available_router_package `**: Fetches the next available Fabric Cloud Router package based on a package input.
*   **`fabric_update_router`**: Update connection. Used to upgrade bandwidth.
	</tr>
	<tr>
		<td>Network Bandwidth monitoring and upgrade agent</td>
		<td>This definition sets up and activate an Equinix agent that automatically upgrades the bandwidth of a connection when usage reaches a certain threshold.</td>
		<td>- Monitor real-time network event streams<br>- Detect bandwidth threshold alerts<br>- Analyze connection utilization patterns<br>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions<br>- Send notifications for critical events</td>
		<td>This skill can use the following tools:

* **`fabric_search_connection`**: Searches for an existing connection.
* **`fabric_get_stream_alert_rule_details`**: Searches for an existing alert rule.
* **`fabric_update_connection`**: Update connection. Used to upgrade bandwidth.
* **`fabric_get_next_available_bandwidth_tier`**: Fetches the next available billing tier based on a bandwidth input.
	</tr>
	<tr>
		<td>Scheduled bandwidth upgrader agent</td>
		<td>This definition sets up and activate an Equinix agent that upgrades the bandwidth of a connection.
This agent is triggered at 3pm every Monday and Wednesday each month.</td>
		<td>- Automatically upgrade connection bandwidth<br>- Log all actions and decisions</td>
		<td>This skill can use the following tools:

*   **`fabric_search_connection`**: Searches for an existing connection.
*   **`fabric_update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`fabric_get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.
	</tr>
</table>

<!-- CATALOG_GENERATION_END -->