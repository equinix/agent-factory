# Equinix Agent Factory Contributors

Thanks for your interest! We're so glad you're here.

The Equinix Agent Factory Repo is a self-service contribution model that allows cross functional teams to manage their own
Agent Factory Schemas related to the md files and categories that will be published from their team.

Every Agent Factory Json Schema and MD Files are published to Github Pages through this repo on merges to the `main` branch. Contribution guidelines
for registration and promotion are provided in this document. Please read it thoroughly.

## Code of Conduct

Available via [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)

## MD Files Gating

Each Markdown (.md) file is created to support Agent Factory workflows.
The team responsible for the Agent Factory will add their Markdown files under the directory for their domain and one of the supported categories: `event_driven`, `run_once`, or `scheduled`.

Each Markdown file(.md) must contain the following sections:
* `# <High Level Title>` - The title of the Agent Factory.
* `## Overview` - A breif description of the Agent Factory Workflow
* `## Prerequisites` -  A description of the prerequisite scenarios and requirements needed for the workflow to execute.
* `## Capabilities` - A high-level description of the capabilities of the Agent Factory.
* `## Follow the action step by step below:` - The step-by-step workflow actions the Agent must perform.
* `## Available Tools` - The required Equinix MCP tools that the Agent Factory uses to execute the workflow to help with consistency of workflow.
* `## Guidelines` - Additional guidance for the Agent Factory, such as clarifications, error handling, appropriate context, and other workflow-specific attributes.

These sections in Markdown file (.md) make up the structure of Agent Factory, which will be retrieved automatically via Github Actions to generate the README and provide the Agent Factory APIs a way of Agent Factory retrival.
**Contributing teams are fully responsible for managing their Markdown (.md) files to ensure the proper gating is occuring for their Agent Factory.**

Example of complete use case for the Agent Factory Markdown(.md) Files:

```
# Network connection packets drop monitoring and upgrade agent

## Overview
This skill sets up and activate an Equinix agent that automatically upgrades the bandwidth of a connection when there are packets drop due to traffic over bw threshold.

## Prerequisites
To receive alerts from your connections, you must first set up alert rules in a stream.
If you don't have one yet, start by creating a stream, attach your connection resources to it, and then configure alert rules for those resources.

## Capabilities
- Monitor real-time network event streams
- Detect packet drop alerts
- Analyze connection utilization patterns
- Automatically upgrade connection bandwidth
- Log all actions and decisions
- Send notifications for critical events

## Follow the action step by step below:
1. Once the cloud event is received, look at the packet drop alert rule from the cloud event message.
2. Search for an existing alert rule given the alertRule uuid extracted from the cloud event message to find out if the alert rule exist.
3. Search for the existing connection given the subject connection uuid from the cloud event message.
4. Extract the bandwidth from the connection details, and then fetch the next available tier given the bandwidth extracted from the connection details.
5. Upgrade the bandwidth of the connection given the new bandwidth.


## Available Tools
This skill can use the following tools:

*   **`search_connection`**: Searches for an existing connection `.
*   **`get_stream_alert_rule_details `**: Searches for an existing alert rule.
*   **`update_connection`**: Update connection. Used to upgrade bandwidth.
*   **`get_next_available_bandwidth_tier `**: Fetches the next available billing tier based on a bandwidth input.

## Guidelines
*   **Prioritize Clarity**: Ensure all parameters for the MCP tools are clearly identified from the user's request before making the tool call.
*   **Error Handling**: If parameters are invalid or operations fail, log errors and stop the process.
*   **Token Efficiency**: Only call the tools when all necessary information is present, avoiding unnecessary context loading.
*   **User can specify alert rule uuid
*   **User can specify connection uuid
```

## Registering a Data Schema

---------------------
Each md file is created to support Agent Factory Workflows. The team responsible for the md files will update the json schema
and which environment the json schema and md file are ready to support by managing the `agentFactories` attributes in `EventDriven`, `RunOnce`, and
`Scheduled` JSON Files. Each md files contains a list of object with the following attributes: 

**Even if the data schema is not using metrics, or alerts, each attribute and sub attribute is required in the data
schema. The Github Action will fail if they are not present and the Pull Request will not be merged.**
---------------------



Each team will be adding data schemas in JSON format to their domain. The data schema will be used in the Agent Factory
envelope to specify the format of the data being streamed to customers.

The domains are added under `jsonschema/equinix` in the repository. Of the pattern
`jsonschema/equinix/<domain>/<major_version>` with a full example being `jsonschema/equinix/fabric/v1`.

Each data schema is created to support Agent Factory types, metrics, and alerts. Please ensure the
[Gating](#data-schema-gating-through-equinix-event-manager) section is read and properly understood to abide by those
rules.

Each contributed data schema requires the following attributes:
* "$id" - The fully resolved URL to the data schema for linking from Agent Factory envelope and for generating Github Pages
 Site
* "name" - The name of the Data Schema being registered. Should match the file name
* "examples" - Provided examples of what the data schema could contain in a streamed event. Can be an empty list `[]` to
start.
* "package" - The name of the package containing the data schema. Example: `equinix.fabric.v1`
* "datatype" - The full name of the datatype within the package. Example: `equinix.fabric.v1.ChangeEvent`
* "$schema" - The JSON Schema Specification used to draft the data schema. Use
`"http://json-schema.org/draft-04/schema#"` for all
* "$ref" - The reference to the definition provided for the data schema. Example: `#/definitions/Data`
* "definitions" - The JSON Schema definition that describes the contents of the data schema for what will be contained
 in the event, metric, or alert that is supported by this data schema
* "Agent FactoryTypes" - List of object with attribute `releaseStatus` that mark which environment the data schema is ready
 to suppport the given event type in. Mark `releaseStatus` as `released` if it is fully tested and ready for production.
 Mark `releaseStatus` as `preview` if it is under development and should only be available in DEV enviornment.
* "metricNames" - List of object with attributes `releaseStatus` that mark which environment the data schema is ready to
 suppport the given event type in. Mark `releaseStatus` as `released` if it is fully tested and ready for production.
 Mark `releaseStatus` as `preview` if it is under development and should only be available in DEV enviornment.
* "alertNames" - List of object with attributes `releaseStatus` that mark which environment the data schema is ready to
 suppport the given event type in. Mark `releaseStatus` as `released` if it is fully tested and ready for production.
 Mark `releaseStatus` as `preview` if it is under development and should only be available in DEV enviornment.

## Process for Upgrading Event/Metric/Alert from Development to Production

When adding a new event/metric/alert to a data schema always start by marking `releaseStatus` as `preview`. This
identifies *in development* items and is the starting point for new events/metrics/alerts being added into the repo.

Once an event/metric/alert has been thoroughly tested in lower environments you will mark `releaseStatus` as `released`.
This indicates that your item is ready to be consumed in production and the production Equinix Event Manager will pass
these items through to the consumers.

It is imperative that you understand the responsibility involved for managing your team's domain with regards to the
`releaseStatus` attribute in your data schema files. The [CODEOWNERS](#codeowners) section describes how responsibility
is managed within the repo. Please review it thoroughly.

## CODEOWNERS

CODEOWNERS file will be in place to establish a Github team (Synced with Equinix IAM) responsible for the files along
the domain path they are contributing to. This ensures that 1 member from each domain team and 1 architect will always
be necessary to approve a Pull Request before it can be merged.

This is critical because the responsibility of maintaining the `releaseStatus` attributes outlined
in the [Gating](#data-schema-gating-through-equinix-event-manager) section lies with the Domain owners and not the
architects. Should any production defect be found the Domain owner is responsible for resolution

When adding a new domain to the `jsonschema/equinix` directory, add an entry to the CODEOWNERS file signifying which
Github Team is responsible for reviewing/approving PRs that modify the domain directory being added

## Data Schema Versioning

Versioning for data schemas is only based on major versions; there are no minor or patch versions. The major versions
are determined by the directory structure containing the data schema.

If no breaking changes (only additions, no modifications or deletions) are made to the data_schema when it is updated it
can stay under the same major version; i.e. v1.

If a breaking change is made to the data_schema (deletion or modification) then it needs to be put into the next major
version in a new version directory; i.e. v2.

Not all data_schemas need to be moved to v2. Just the ones that have breaking changes.

## Repository Versioning

The self service contribution model is setup to ensure the repo is always in a stable state that can be released to
either DEV or production enviornment. Each time a Pull Request is merged into main a new version tag will be created
based on SemVar for the commit names present in the change. This tag will always be available to the Equinix Event
Manager for releases. This setup is possible because of our CODEOWNERSHIP model.

