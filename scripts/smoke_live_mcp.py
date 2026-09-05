#!/usr/bin/env python3
"""Scheduled, read-only end-to-end smoke for the public LiquiLens MCP."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAX_RESPONSE_BYTES = 2_000_000
OPERATOR_CLIENT = "LiquiLens-Operator-Growth-Audit"


def _rpc(endpoint: str, method: str, params: dict[str, Any], request_id: int,
         *, protocol: str, name: str | None = None) -> dict[str, Any]:
    payload = json.dumps({
        "jsonrpc": "2.0", "id": request_id, "method": method, "params": params,
    }, separators=(",", ":")).encode()
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": protocol,
        "Mcp-Method": method,
        "User-Agent": f"{OPERATOR_CLIENT}/1.0",
        "X-Liquilens-Traffic-Class": "synthetic",
    }
    if name is not None:
        headers["Mcp-Name"] = name
    request = urllib.request.Request(endpoint, data=payload, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if response.status != 200:
            raise RuntimeError(f"{method} returned HTTP {response.status}")
    if len(body) > MAX_RESPONSE_BYTES:
        raise RuntimeError(f"{method} exceeded the smoke response budget")
    value = json.loads(body)
    if (not isinstance(value, dict) or value.get("jsonrpc") != "2.0"
            or type(value.get("id")) is not int or value["id"] != request_id):
        raise RuntimeError(f"{method} returned an invalid JSON-RPC envelope")
    if "error" in value:
        raise RuntimeError(f"{method} returned JSON-RPC error {value['error']!r}")
    result = value.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"{method} returned no result object")
    return result


def modern_meta(protocol: str) -> dict[str, Any]:
    return {
        "io.modelcontextprotocol/protocolVersion": protocol,
        "io.modelcontextprotocol/clientInfo": {
            "name": OPERATOR_CLIENT, "version": "1.0.0",
        },
        "io.modelcontextprotocol/clientCapabilities": {},
    }


def smoke(endpoint: str) -> None:
    contract = json.loads((ROOT / "contract.json").read_text(encoding="utf-8"))
    legacy = "2025-11-25"
    initialized = _rpc(endpoint, "initialize", {
        "protocolVersion": legacy,
        "capabilities": {},
        "clientInfo": {"name": OPERATOR_CLIENT, "version": "1.0.0"},
    }, 1, protocol=legacy)
    if initialized.get("serverInfo", {}).get("version") != contract["serverVersion"]:
        raise RuntimeError("live server version differs from the listing")

    modern = contract["protocolVersions"][0]
    meta = modern_meta(modern)
    discovered = _rpc(endpoint, "server/discover", {"_meta": meta}, 2,
                      protocol=modern)
    if discovered.get("supportedVersions") != contract["protocolVersions"]:
        raise RuntimeError("live protocol inventory differs from the listing")

    tools = _rpc(endpoint, "tools/list", {"_meta": meta}, 3, protocol=modern)
    tool_names = [item.get("name") for item in tools.get("tools", [])]
    if tool_names != contract["tools"]:
        raise RuntimeError("live tool inventory differs from the listing")

    prompts = _rpc(endpoint, "prompts/list", {"_meta": meta}, 4, protocol=modern)
    prompt_names = [item.get("name") for item in prompts.get("prompts", [])]
    if prompt_names != contract["prompts"]:
        raise RuntimeError("live prompt inventory differs from the listing")

    templates = _rpc(endpoint, "resources/templates/list", {"_meta": meta}, 5,
                     protocol=modern)
    if templates.get("resourceTemplates") != contract["resourceTemplates"]:
        raise RuntimeError("live resource-template inventory differs from the listing")

    evidence = _rpc(endpoint, "tools/call", {
        "name": "evidence_markets", "arguments": {}, "_meta": meta,
    }, 6, protocol=modern, name="evidence_markets")
    if evidence.get("isError") or not isinstance(evidence.get("structuredContent"), dict):
        raise RuntimeError("evidence_markets did not return structured content")

    print(
        f"live MCP valid: {len(tool_names)} tools, {len(prompt_names)} prompts, "
        f"version {contract['serverVersion']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="https://api.liquilens.in/mcp")
    args = parser.parse_args()
    smoke(args.endpoint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
