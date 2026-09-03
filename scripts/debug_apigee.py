#!/usr/bin/env python3
"""Temporary debug script — prints exact httpx request headers and status for the eval endpoint."""
import httpx
import json
import os

token = os.environ.get("DEBUG_TOKEN", "")
base_url = os.environ.get("AGENT_EVAL_SERVICE_URL", "").rstrip("/")

with open("agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-metro-latency-notify.md") as f:
    content = f.read()

print(f"Template size: {len(content)} chars")

resp = httpx.post(
    f"{base_url}/fabric/v4/eval/template-content",
    json={"templateMarkdown": content, "templatePath": "debug/small.md"},
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CORRELATION-ID": "debug-001",
    },
)
print(f"httpx status: {resp.status_code}")
print("httpx request headers sent:")
for k, v in resp.request.headers.items():
    if k.lower() == "authorization":
        print(f"  {k}: Bearer ***")
    else:
        print(f"  {k}: {v}")
