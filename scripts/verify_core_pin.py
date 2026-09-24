#!/usr/bin/env python3
"""Verify this listing against the exact pinned LiquiLens source checkout."""

from __future__ import annotations

import argparse
import ast
import copy
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _assignment(tree: ast.Module, name: str) -> ast.expr:
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == name and node.value is not None:
                return node.value
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name
                   for target in node.targets):
                return node.value
    raise ValueError(f"assignment {name} not found")


def _mapping_keys(tree: ast.Module, name: str,
                  expansions: dict[str, list[str]] | None = None) -> list[str]:
    value = _assignment(tree, name)
    if not isinstance(value, ast.Dict):
        raise ValueError(f"{name} must be a dictionary literal")
    keys = []
    for key, item in zip(value.keys, value.values):
        if key is not None:
            keys.append(ast.literal_eval(key))
        elif (isinstance(item, ast.Name) and expansions is not None
              and item.id in expansions):
            keys.extend(expansions[item.id])
        else:
            raise ValueError(f"{name} contains an unsupported dictionary expansion")
    if not all(isinstance(key, str) for key in keys):
        raise ValueError(f"{name} contains a non-string key")
    if len(keys) != len(set(keys)):
        raise ValueError(f"{name} contains a duplicate key")
    return keys


def _literal(tree: ast.Module, name: str) -> Any:
    return ast.literal_eval(_assignment(tree, name))


def _public_registry_manifest(core: dict[str, Any],
                              metadata: dict[str, Any]) -> dict[str, Any]:
    """Project only the reviewed public metadata onto the exact core manifest."""
    if set(metadata) != {"version", "repositoryUrl", "websiteUrl", "description"}:
        raise ValueError("registryMetadata must declare exactly the four public metadata fields")
    versions = []
    for version in (core.get("version"), metadata["version"]):
        if not isinstance(version, str) or not re.fullmatch(
            r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version
        ):
            raise ValueError("registry and runtime versions must use numeric semantic versions")
        versions.append(tuple(int(part) for part in version.split(".")))
    if versions[1] <= versions[0]:
        raise ValueError("registry metadata revision must be newer than the pinned runtime version")
    if metadata["repositoryUrl"] != "https://github.com/beepboop2025/liquilens-mcp":
        raise ValueError("registry repository must be the public LiquiLens mirror")
    if metadata["websiteUrl"] != "https://liquilens.in/agents/":
        raise ValueError("registry website must be the public agent starter kit")
    description = metadata["description"]
    if not isinstance(description, str) or not 1 <= len(description) <= 100:
        raise ValueError("registry description must contain 1 to 100 characters")

    expected = copy.deepcopy(core)
    expected["version"] = metadata["version"]
    expected["repository"]["url"] = metadata["repositoryUrl"]
    expected["websiteUrl"] = metadata["websiteUrl"]
    expected["description"] = description
    return expected


def verify(core: Path) -> None:
    contract = _json(ROOT / "contract.json")
    listing_server = _json(ROOT / "server.json")
    expected_sha = contract["canonical"]["releaseCommit"]
    actual_sha = subprocess.check_output(
        ["git", "-C", str(core), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_sha != expected_sha:
        raise ValueError(f"core checkout is {actual_sha}, listing pins {expected_sha}")

    server_tree = _module(core / "backend" / "mcp_server.py")
    protocol_tree = _module(core / "backend" / "mcp_protocol.py")
    core_server = _json(core / "server.json")

    # Resolve only the explicitly imported bank inventories, without importing or
    # executing the application. Unknown expansions and duplicate keys fail closed.
    bank_tree = _module(core / "backend" / "mcp_bank_tools.py")
    bank_imports = {
        alias.name for node in server_tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "mcp_bank_tools"
        and node.level == 0
        for alias in node.names if alias.asname is None
    }
    if not {"BANK_TOOLS", "BANK_PROMPTS"} <= bank_imports:
        raise ValueError("core must import BANK_TOOLS and BANK_PROMPTS from mcp_bank_tools")
    actual_tools = sorted(_mapping_keys(server_tree, "TOOLS", {
        "BANK_TOOLS": _mapping_keys(bank_tree, "BANK_TOOLS"),
    }))
    actual_prompts = sorted(_mapping_keys(server_tree, "PROMPTS", {
        "BANK_PROMPTS": _mapping_keys(bank_tree, "BANK_PROMPTS"),
    }))
    modern = _literal(protocol_tree, "MODERN_PROTOCOL_VERSION")
    primary = _literal(protocol_tree, "PROTOCOL_VERSION")
    legacy_node = _assignment(protocol_tree, "LEGACY_PROTOCOL_VERSIONS")
    if not isinstance(legacy_node, (ast.Tuple, ast.List)):
        raise ValueError("LEGACY_PROTOCOL_VERSIONS must be a literal sequence")
    legacy = [
        primary if isinstance(item, ast.Name) and item.id == "PROTOCOL_VERSION"
        else ast.literal_eval(item)
        for item in legacy_node.elts
    ]
    actual_protocols = [modern, *legacy]

    comparisons = {
        "tools": (actual_tools, contract["tools"]),
        "prompts": (actual_prompts, contract["prompts"]),
        "protocolVersions": (actual_protocols, contract["protocolVersions"]),
        "serverVersion": (
            _literal(protocol_tree, "SERVER_VERSION"),
            contract["serverVersion"],
        ),
        "core server manifest": (core_server, contract["canonical"]["serverManifest"]),
        "public registry manifest": (
            listing_server,
            _public_registry_manifest(
                contract["canonical"]["serverManifest"], contract["registryMetadata"]
            ),
        ),
    }
    mismatches = [
        f"{label}: core={actual!r}, listing={expected!r}"
        for label, (actual, expected) in comparisons.items()
        if actual != expected
    ]
    if mismatches:
        raise ValueError("listing/core contract mismatch:\n" + "\n".join(mismatches))

    print(
        f"core pin valid: {expected_sha} exposes {len(actual_tools)} tools, "
        f"{len(actual_prompts)} prompts and MCP {contract['serverVersion']}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", required=True, type=Path)
    args = parser.parse_args()
    verify(args.core.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
