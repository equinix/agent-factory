#!/usr/bin/env python3
"""Temporary debug script — prints exact httpx request headers and status for the eval endpoint."""
import httpx
import os

token = os.environ.get("DEBUG_TOKEN", "")
base_url = os.environ.get("AGENT_EVAL_SERVICE_URL", "").rstrip("/")

with open("agent_factory_schema/equinix/fabric/v1/on_event/connection/connection-metro-latency-notify.md") as f:
    content = f.read()

print(f"Template size: {len(content)} chars")

# Build the request object first so we can inspect headers BEFORE sending
req = httpx.Request(
    "POST",
    f"{base_url}/fabric/v4/eval/template-content",
    json={"templateMarkdown": content, "templatePath": "debug/small.md"},
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CORRELATION-ID": "debug-001",
    },
)

print("=== Request headers httpx will send ===")
for k, v in req.headers.items():
    if k.lower() == "authorization":
        print(f"  {k}: Bearer ***")
    else:
        print(f"  {k}: {v}")

print("=== Sending request (40s timeout) ===")
try:
    with httpx.Client(timeout=40.0) as client:
        resp = client.send(req)
    print(f"httpx status: {resp.status_code}")
except httpx.TimeoutException as e:
    print(f"httpx TIMEOUT: {e}")
except Exception as e:
    print(f"httpx ERROR: {e}")
