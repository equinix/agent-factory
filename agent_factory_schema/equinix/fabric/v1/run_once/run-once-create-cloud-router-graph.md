---
name: run-once-create-cloud-router-graph
description: GRAPH/DAG version — creates a Fabric Cloud Router from free-text parameters via a deterministic graph (one llm node parses params, then typed tool steps validate, create, and confirm).
execution_mode: GRAPH
graph_pattern: DAG
---

# Cloud Router Creator Agent (GRAPH / DAG)

## Overview
The deterministic graph version of the Cloud Router Creator. A single `llm` node parses the
user's free-text parameters into a structured JSON object; the rest of the workflow runs as
typed graph nodes (validate package → create router → confirm) with no further LLM control.
This is the DAG counterpart of `run-once-create-cloud-router` (the SEQUENTIAL version) — same
task, but tool order is fixed by the graph rather than decided by the model each turn.

## Available Tools
This skill can use the following tools:

*   **`search_routers`**: Searches Fabric Cloud Routers; used here to confirm the new router.
*   **`create_router`**: Creates a new Fabric Cloud Router.

## Instructions
You receive the user's request containing the cloud-router parameters as free text
(for example: "name: my-fcr, metro: SV, account: 123456, project: 18857..., emails: a@x.com").
Extract those parameters and respond with **ONLY** a single JSON object — no prose, no code
fences — with exactly these keys:

```json
{
  "name": "<router name>",
  "metro_code": "<metro code, e.g. SV>",
  "package_code": "<package code; STANDARD if not provided>",
  "account_number": <account number as an integer>,
  "project_id": "<project id>",
  "emails": ["<email1>", "<email2>"]
}
```

Rules for the extraction:
- `package_code` defaults to `"STANDARD"` when the user does not specify one.
- `account_number` MUST be a JSON number (integer), not a string.
- `emails` MUST be a JSON array of strings (split a comma-separated list).
- Do not invent values; if a required field is genuinely missing, use an empty string or
  empty array and let the downstream tool surface the error.

The graph then creates the router and confirms it — see `## Steps`.

## Guidelines
*   **Deterministic flow**: tool order is fixed by the graph; the LLM only parses parameters.
*   **Error Handling**: any tool error routes to a FAILED terminal; creation is retried at most
    twice on transient failures, never re-run automatically beyond that.
*   **Note**: hard duplicate-prevention (stop if a same-named router already exists) needs a
    transform node to inspect search results and is intentionally omitted from this DAG; the
    `confirm` step reports the final provisioned state instead.

## Steps
```yaml
state:
  params: map
  created: string
  report: string
entry: parse_params
nodes:
  - id: parse_params
    action: llm
    parseJson: true
    reads: [prompt]
    output: params
    edges:
      onSuccess: create
      onError: end_error
  - id: create
    action: tool
    tool: create_router
    input:
      router_request:
        type: "XF_ROUTER"
        name: "${state.params.name}"
        location:
          metroCode: "${state.params.metro_code}"
        package:
          code: "${state.params.package_code}"
        notifications:
          - type: "ALL"
            emails: "${state.params.emails}"
        account:
          accountNumber: "${state.params.account_number}"
        project:
          projectId: "${state.params.project_id}"
    output: created
    retry: { max: 2, backoffMs: 1000 }
    edges:
      onSuccess: confirm
      onError: end_error
  - id: confirm
    action: tool
    tool: search_routers
    input:
      query:
        filter:
          and:
            - property: "/name"
              operator: "="
              values: ["${state.params.name}"]
            - property: "/project/projectId"
              operator: "="
              values: ["${state.params.project_id}"]
        pagination:
          limit: 5
    output: report
    edges:
      onSuccess: end_ok
      onEmpty: end_ok
      onError: end_error
terminals:
  - { id: end_ok,    status: COMPLETED }
  - { id: end_error, status: FAILED }
```

## Configuration
Parameters are supplied as free text in the agent's `configuration.prompt`; the `parse_params`
node extracts them into the JSON object above.

* **`name`**: Required — a descriptive name for the cloud router.
* **`metro_code`**: Required — the Equinix metro (e.g. `"SV"`, `"DC"`, `"AM"`).
* **`package_code`**: Optional — defaults to `"STANDARD"`.
* **`account_number`**: Required — the Fabric account number (integer).
* **`project_id`**: Required — the Fabric project ID.
* **`notifications`**: Required — comma-separated email addresses (notification type `"ALL"`).
