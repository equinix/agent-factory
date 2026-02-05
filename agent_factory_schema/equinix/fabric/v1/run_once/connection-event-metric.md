# List Active Connections and Retrieve CloudEvents and Bandwidth Metrics

## Overview
This skill lists 10 active connections and retrieves their CloudEvents and bandwidth metrics for monitoring and analysis.

## Prerequisites
- Active connections should exist in the system
- Connections should be in PROVISIONED state

## Capabilities
- List active connections (up to 3
- Retrieve CloudEvents for each connection
- Fetch bandwidth metrics for each connection
- Log all actions and results

## Follow the action step by step below:
1. Search for active connections with a limit of 3 results in  my project
2. For each connection found, retrieve the connection UUID
3. For each connection UUID, fetch the associated CloudEvents
4. For each connection UUID, retrieve the bandwidth metrics
5. Compile and present the results in a structured format

## Available Tools
This skill can use the following tools:
* **`search_connection`**: Searches for active connections in my project with optional filters and limits of 3 
* **`search_cloud_events`**: Retrieves CloudEvents for a specific connection UUID
* **`get_metrics`**: Fetches bandwidth tx ans rx  metrics for a specific connection UUID

## Guidelines
* **Prioritize Clarity**: Ensure connection UUIDs are properly extracted before fetching events and metrics
* **Error Handling**: If a connection lookup fails, log the error and continue with remaining connections
* **Token Efficiency**: Batch operations where possible to minimize API calls
* **Data Presentation**: Format the output clearly showing connection details, events, and metrics for easy analysis
* **Performance**: Process connections sequentially to avoid rate limiting issues

