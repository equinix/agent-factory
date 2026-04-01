---
name: pending-state-tracker
description: Monitors and notifies user for long running Fabric assets in provisioning or deprovisioning states.
---

# Project Lifecycle Activities Insight Agent

## Overview
This agent actively analyzes the lifecycle state of Equinix Fabric assets to identify those stuck in provisioning or deprovisioning phases for an extended period, proactively notifying user.
This agent runs once immediately by default unless scheduled by user.

## Prerequisites
None

## Capabilities
- Analyze all pending connections, ports, and routers over a specified time range
- Deliver a plain-English summary via email as a PDF report

## Instructions

1. Search for connections. Follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/operation/equinixStatus", "operator": "=", "values": ["PROVISIONING", "DEPROVISIONING"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 },
  "sort": [
    {
      "direction": "DESC",
      "property": "/changeLog/updatedDateTime"
    }
  ]
}
```
2. Search for ports. Follow the request payload below:
```json
{
  "filter": {
    "and": [
      { "property": "/state", "operator": "=", "values": ["PROVISIONING", "DEPROVISIONING"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 }
}
```
3. Search for routers. Follow the request payload below:

```json
{
  "filter": {
    "and": [
      { "property": "/state", "operator": "=", "values": ["PROVISIONING", "DEPROVISIONING"] }
    ]
  },
  "pagination": { "offset": 0, "limit": 100 }
}
```
4. Structure the report below:
### Section content
- **Summary**: 3–5 sentences — total count, headline finding, insights.
- **Fabric Cloud Router Activity**: Include only if routers exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date. Put values under Data Row.
- **Connection Activity**: Include only if connections exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date. Put values under Data Row.
- **Port Activity**: Include only if connections exist — otherwise omit entirely. Include name, uuid, state, project, created and updated dates. Also include how long has it been since created date. Put values under Data Row.

```
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Equinix Fabric</title>

    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f6f9;
			margin: 0;
            padding: 30px;
            color: #333;
        }

        .container {
            max-width: 1000px;
            margin: auto;
        }

        .header {
            float: left;
			background: #d60404;
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            margin-right: 35px;
            width: 600px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        
        .logo {
            float: left;
            padding-top: 30px;
        }
        
        .new-line {
        	clear: both;
        }

        .section {
            background: white;
            border-radius: 8px;
            padding: 20px 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }

        .section h2 {
            margin-top: 0;
            font-size: 20px;
            color: #c40808;
            border-bottom: 2px solid #e6edf5;
            padding-bottom: 8px;
        }

        .content {
            margin-top: 15px;
            line-height: 1.6;
            font-size: 10px;
        }

        .footer {
            text-align: center;
            color: #777;
            margin-top: 30px;
            font-size: 12px;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 8px;
        }

        .badge.good {
            background: #d4edda;
            color: #155724;
        }

        .badge.warn {
            background: #fff3cd;
            color: #856404;
        }

        .badge.critical {
            background: #f8d7da;
            color: #721c24;
        }
        .table-container {
          width: 100%;
          max-width: 900px;
        }
        
        .table-row {
          list-style: none;
          padding: 0;
          margin: 0;
          border-bottom: 1px solid #ddd;
          overflow: hidden; 
        }
        
        .table-row li {
          float: left;
  		  width: 15%;
  		  box-sizing: border-box;
  		  padding: 10px;
          overflow-wrap: break-word; 
          word-wrap: break-word;
          white-space: normal; 
        }
               
        .table-header {
          background-color: #d4edda;
          font-weight: bold;
          border-top: 2px solid #333;
        }

    </style>
</head>

<body>

<div class="container">

    <div>
    	<div class="header">
			<h1>Pending State Report</h1>
        	<p>Equinix Fabric</p>
    	</div>
    	<div class="logo">
    		<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" x="150px" y="0px" height="70px" viewBox="150 0 208 136" xml:space="preserve">
               <g>
                  <polygon fill="#FF0000" points="343.971,31.423 343.971,92.057 330.125,96.902 330.125,26.599 288.575,12.095 288.575,111.406
                     274.723,116.231 274.723,7.248 253.954,0 233.179,7.248 233.179,116.231 219.334,111.406 219.334,12.095 177.783,26.599
                     177.783,96.902 163.938,92.057 163.938,31.423 150.078,36.27 150.078,101.901 191.636,116.405 191.636,36.429 205.488,31.597
                     205.488,121.237 247.031,135.748 247.031,17.093 253.954,14.67 260.877,17.093 260.877,135.748 302.435,121.237 302.435,31.597
                     316.28,36.429 316.28,116.405 357.83,101.901 357.83,36.27 "></polygon>
               </g>
            </svg>
    	</div>
    </div>
    
    <div class="new-line"></div>

    <div class="section">
        <h2>Summary</h2>
        <div class="content">
        </div>
    </div>
    
	<div class="section">
        <h2>Cloud Router Activity</h2>
        <div class="content">
        	<div class="table-container">
                <!-- Header Row -->
                <ul class="table-row table-header">
                    <li>Name</li>
                    <li>UUID</li>
                    <li>State</li>
                    <li>Created Date</li>
                    <li>Updated Date</li>
					<li>Time Since Creation</li>
                </ul>
              
              <!-- Data Row-->
              <ul class="table-row">

              </ul>
        	</div>
        </div>
    </div>


    <div class="section">
        <h2>Connection Activity</h2>
        <div class="content">
        	<div class="table-container">
                <!-- Header Row -->
                <ul class="table-row table-header">
                    <li>Name</li>
                    <li>UUID</li>
                    <li>State</li>
                    <li>Created Date</li>
                    <li>Updated Date</li>
					<li>Time Since Creation</li>
                </ul>
              
              <!-- Data Row-->
              <ul class="table-row">
              </ul>
                                  <li>xd</li>
                    <li>UUID</li>
                    <li>State</li>
                    <li>Created Date</li>
                    <li>Updated Date</li>
					<li>Time Since Creation</li>
        	</div>
        </div>
    </div>

    <div class="section">
        <h2>Port Activity</h2>
        <div class="content">
        	<div class="table-container">
                <!-- Header Row -->
                <ul class="table-row table-header">
                    <li>Name</li>
                    <li>UUID</li>
                    <li>State</li>
                    <li>Created Date</li>
                    <li>Updated Date</li>
					<li>Time Since Creation</li>
                </ul>
              
              <!-- Data Row-->
              <ul class="table-row">
              </ul>
        	</div>
        </div>
    </div>
    <div class="footer">
        Generated System Status Report
    </div>

</div>

</body>
</html>
```

5. Use `send_email_notification` to send the report to `recipient_email_address`. Follow the email rules below:
- `pdfContent`: the full report text from Step 4.
- `body`: one-paragraph summary of overall status and headline finding.
- `pdfTitle`: `FabricPendingStates_<today>` — Use only the date portion (`YYYY-MM-DD`), not the full ISO 8601 string.

## Available Tools
- **`search_connections`**: Searches for connections.
- **`search_routers`**: Searches for fabric cloud routers.
- **`search_ports`**: Searches for ports.
- **`send_email_notification`**: Sends an email. Pass `pdfTitle` and `pdfContent` (plain text) to auto-generate and attach a PDF.

## Guidelines
- Plain English, no API jargon, no raw event strings, full UUIDs always. Insight over data — derive meaning from patterns, not raw counts.
- Skip empty sections entirely — no placeholder text. If no results found, send email with "No activity detected".
- If the search APIs fail, stop without sending.
- Section content rules of Report:

## Configuration
- **`recipient_email_address`**: Required. List of email addresses to receive the report.
