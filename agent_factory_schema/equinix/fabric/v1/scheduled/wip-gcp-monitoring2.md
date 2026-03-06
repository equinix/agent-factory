# GCP Monitoring Agent

## Overview
An Equinix agent that sends gcp monitoring and equinix metrics to an email 
This agent is triggered every 1 hour.

## Capabilities
- An automated monitoring solution utilizing an Equinix-hosted agent to track and transmit real-time GCP performance metrics. 
- This system is designed to provide stakeholders with regular visibility into cloud health by delivering comprehensive metric reports directly to designated email recipients.

## Prerequisites

## Available Tools
This skill can use the following tools:
*   **`list_timeseries`**: Lists time series data from the Google Cloud Monitoring API. Parameter view is always FULL.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.
*   **`get_metrics`**: List metrics data of the connection uuid.

## Follow the action step by step below:
1. List the time series data from the Google Cloud Monitoring API using the specified parameters. Interval start and end time parameters should use ISO 8601 format.
2. Make a text report on the retrieved time series data by extracting key insights and trends based on the results. 
3. Next, send the results above to the designated email address,
4. List the connection metrics data using the specified parameters: Connection uuid, metric name parameter, and interval start and end time parameters can use the same as gcp.
5. Next, send the results above to the designated email address 

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.

## Configuration
* **`alignment_period`**: < string value in seconds > - Optional - Default value is 300s.
* **`filter`**: < string > - Required - The gcp aggregation filter.
* **`start_time`**: < time in ISO 8601 > - Required - The gcp aggregation start time.
* **`end_time`**: < time in ISO 8601 > - Required - The gcp aggregation end time.
* **`gcp_project_id`**: < string value > - Required - The gcp aggregation name.
* **`email`**: < email format string > - Required - The notification email.
* **`connection_uuid`**: < string > - Required - The equinix connection uuid.
* **`name`**: < string > - Required - The equinix metric name.
