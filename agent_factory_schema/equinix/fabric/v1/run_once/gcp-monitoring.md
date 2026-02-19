# GCP Monitoring Agent

## Overview
An Equinix agent that sends gcp monitoring metrics to an email.
This agent runs once immediately by default unless scheduled by user.

## Capabilities
- An automated monitoring solution utilizing an Equinix-hosted agent to track and transmit real-time GCP performance metrics. 
- This system is designed to provide stakeholders with regular visibility into cloud health by delivering comprehensive metric reports directly to designated email recipients.

## Prerequisites

## Available Tools
This skill can use the following tools:

*   **`list_timeseries`**: Lists time series data from the Google Cloud Monitoring API.
*   **`send_email_notification`**: Sends an email notification given an email address and email body.

## Follow the action step by step below:
1. List the time series data from the Google Cloud Monitoring API using the specified parameters.
2. Make a detailed report on  the retrieved time series data by extracting key insights and trends based on the results.
3. Next, send an email notification to the designated email address, using the outcome of the previous step as the email body so the recipient is clearly informed of the monitoring results and insights.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **Name guidelines** Limit names to 15 characters when creating streams and alert rules to ensure compatibility.

## Configuration
*   **Parameters** alignmentPeriod is 60s.
*   **Parameters** crossSeriesReducer is REDUCE_SUM.
*   **Parameters** filter: metric.type="logging.googleapis.com/log_entry_count" AND resource.type="global"
*   **Parameters** interval startTime: "2026-02-10T10:40:00Z"
*   **Parameters** interval endTime: "2026-02-12T16:00:00Z"
*   **Parameters** argument name is "projects/vision-fabric"
*   **Parameters** view is FULL
*   **Parameters** email address is cent-line@yekbvpgx.mailosaur.net
