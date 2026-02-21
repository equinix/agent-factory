# GCP Monitoring Agent

## Overview
An Equinix agent that sends gcp monitoring metrics to an email 
This agent runs once immediately by default unless scheduled by user.
This agent is triggered every 15 minutes.

## Capabilities
- An automated monitoring solution utilizing an Equinix-hosted agent to track and transmit real-time GCP performance metrics. 
- This system is designed to provide stakeholders with regular visibility into cloud health by delivering comprehensive metric reports directly to designated email recipients.

## Prerequisites

## Available Tools
This skill can use the following tools:

*   **`list_timeseries`**: Lists time series data from the Google Cloud Monitoring API.
*   **`send_email_notification`**: Sends an email notification given a list email of addresses and email body.

## Follow the action step by step below:
1. List the time series data from the Google Cloud Monitoring API using the specified parameters. Interval start and end time parameters should use ISO 8601 format.
2. Make a long detailed report on the retrieved time series data by extracting key insights and trends based on the results. 
3. Next, send the results above to the designated email address,

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Name guidelines** Limit names to 15 characters when creating streams and alert rules to ensure compatibility.

## Configuration
*   **Parameters** alignmentPeriod is 60s.
*   **Parameters** crossSeriesReducer is REDUCE_SUM.
*   **Parameters** User should specify gcp filter: metric.type="custom.googleapis.com/equinix/fabric/connection/connection_bandwidth_rx_bps" AND resource.type="global"
*   **Parameters** gcp interval startTime: "2026-02-20T00:00:00Z"
*   **Parameters** gcp interval endTime: "2026-02-20T23:59:59Z"
*   **Parameters** User should specify gcp project id:  projects/observability-459023
*   **Parameters** email address is cent-line@yekbvpgx.mailosaur.net
