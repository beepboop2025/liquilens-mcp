#!/usr/bin/env python3
"""Verify this listing against the exact pinned LiquiLens source checkout."""

from __future__ import annotations

import argparse
import ast
import copy
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_METADATA_FIELDS = frozenset({
    "version", "repositoryUrl", "websiteUrl", "description", "title", "icons",
})
# Icons must come from the product's own domain (the registry schema asks
# consumers to prefer the server's domain) and be raster images: an SVG can
# carry script, so every client would need its own sanitiser.
ICON_HOST = "liquilens.in"
ICON_SUFFIXES = {
    "image/png": (".png",),
    "image/jpeg": (".jpg", ".jpeg"),
    "image/webp": (".webp",),
}
ICON_SIZE = re.compile(r"[1-9][0-9]{0,4}x[1-9][0-9]{0,4}")
ICON_FIELDS = frozenset({"src", "mimeType", "sizes", "theme"})


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


def _dash_punctuation(text: str) -> list[str]:
    """Return Unicode dash punctuation other than the ASCII hyphen-minus."""
    return sorted({f"U+{ord(char):04X}" for char in text
                   if char != "-" and unicodedata.category(char) == "Pd"})


def _display_text(label: str, value: Any) -> str:
    """Registry display copy: 1 to 100 characters, one line, no dash punctuation."""
    if not isinstance(value, str) or not 1 <= len(value) <= 100:
        raise ValueError(f"registry {label} must contain 1 to 100 characters")
    if value != value.strip() or any(char in value for char in "\r\n\t"):
        raise ValueError(f"registry {label} must be one trimmed line")
    dashes = _dash_punctuation(value)
    if dashes:
        raise ValueError(f"registry {label} contains dash punctuation {', '.join(dashes)}")
    return value


def _icons(value: Any) -> list[dict[str, Any]]:
    """Accept only first-party raster icons with declared type and pixel sizes."""
    if not isinstance(value, list) or not 1 <= len(value) <= 4:
        raise ValueError("registry icons must be a list of 1 to 4 icons")
    icons = []
    for icon in value:
        if (not isinstance(icon, dict)
                or not {"src", "mimeType", "sizes"} <= set(icon) <= ICON_FIELDS):
            raise ValueError("each registry icon declares src, mimeType and sizes, "
                             "and optionally theme")
        src, mime_type, sizes = icon["src"], icon["mimeType"], icon["sizes"]
        parsed = urlparse(src) if isinstance(src, str) else None
        if (parsed is None or len(src) > 255 or parsed.scheme != "https"
                or parsed.netloc != ICON_HOST or not parsed.path.startswith("/")
                or parsed.params or parsed.query or parsed.fragment):
            raise ValueError(f"registry icon src must be an https URL on {ICON_HOST}, "
                             "at most 255 characters, without query or fragment")
        if (mime_type not in ICON_SUFFIXES
                or not parsed.path.lower().endswith(ICON_SUFFIXES[mime_type])):
            raise ValueError("registry icon mimeType must be a raster type matching "
                             "the file extension")
        if (not isinstance(sizes, list) or not sizes or len(sizes) != len(set(sizes))
                or not all(isinstance(size, str) and ICON_SIZE.fullmatch(size)
                           for size in sizes)):
            raise ValueError("registry icon sizes must list distinct WIDTHxHEIGHT values")
        if "theme" in icon and icon["theme"] not in {"light", "dark"}:
            raise ValueError("registry icon theme must be light or dark")
        icons.append(copy.deepcopy(icon))
    if len({icon["src"] for icon in icons}) != len(icons):
        raise ValueError("registry icons must not repeat a source")
    return icons


def _public_registry_manifest(core: dict[str, Any],
                              metadata: dict[str, Any]) -> dict[str, Any]:
    """Project only the reviewed public metadata onto the exact core manifest."""
    if set(metadata) != PUBLIC_METADATA_FIELDS:
        raise ValueError("registryMetadata must declare exactly the six public metadata fields")
    versions = []
    for version in (core.get("version"), metadata["version"]):
        if not isinstance(version, str) or not re.fullmatch(
            r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version
        ):
            raise ValueError("registry and runtime versions must use numeric semantic versions")
        versions.append(tuple(int(part) for part in version.split(".")))
    if versions[1] < versions[0]:
        raise ValueError("registry metadata revision must not precede the pinned runtime version")
    if metadata["repositoryUrl"] != "https://github.com/beepboop2025/liquilens-mcp":
        raise ValueError("registry repository must be the public LiquiLens mirror")
    if metadata["websiteUrl"] != "https://liquilens.in/agents/":
        raise ValueError("registry website must be the public agent starter kit")
    description = _display_text("description", metadata["description"])
    title = _display_text("title", metadata["title"])
    icons = _icons(metadata["icons"])

    expected = copy.deepcopy(core)
    expected["version"] = metadata["version"]
    expected["repository"]["url"] = metadata["repositoryUrl"]
    expected["websiteUrl"] = metadata["websiteUrl"]
    expected["description"] = description
    expected["title"] = title
    expected["icons"] = icons
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
