from __future__ import annotations

import json
import re
import unicodedata
import unittest
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]


def _dash_punctuation(text: str) -> list[str]:
    """Unicode dash punctuation other than the ASCII hyphen-minus."""
    return sorted({f"U+{ord(char):04X}" for char in text
                   if char != "-" and unicodedata.category(char) == "Pd"})


def _strict_json(path: Path) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key in {path.name}: {key}")
            value[key] = item
        return value

    def reject_constant(value: str) -> None:
        raise ValueError(f"nonfinite JSON value in {path.name}: {value}")

    parsed = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
    )
    if not isinstance(parsed, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return parsed


def _section(markdown: str, heading: str, next_heading: str) -> str:
    start = markdown.index(heading)
    end = markdown.index(next_heading, start)
    return markdown[start:end]


class ListingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = _strict_json(ROOT / "contract.json")
        cls.server = _strict_json(ROOT / "server.json")
        cls.glama = _strict_json(ROOT / "glama.json")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_contract_shape_and_names_are_deterministic(self) -> None:
        self.assertEqual(
            set(self.contract),
            {
                "canonical",
                "serverVersion",
                "registryMetadata",
                "protocolVersions",
                "tools",
                "prompts",
                "resourceTemplates",
            },
        )
        self.assertRegex(self.contract["canonical"]["releaseCommit"], r"^[0-9a-f]{40}$")
        for field in ("tools", "prompts"):
            names = self.contract[field]
            self.assertEqual(names, sorted(set(names)))
            self.assertTrue(all(re.fullmatch(r"[a-z][a-z0-9_]+", n) for n in names))
        self.assertEqual(len(self.contract["tools"]), 23)
        self.assertEqual(len(self.contract["prompts"]), 5)
        self.assertEqual(self.contract["resourceTemplates"], [])

    def test_pin_sha_version_and_tools_stay_consistent(self) -> None:
        pin = self.contract["canonical"]["releaseCommit"]
        version = self.contract["serverVersion"]
        tools = self.contract["tools"]
        prompts = self.contract["prompts"]

        self.assertEqual(self.server["version"], self.contract["registryMetadata"]["version"])
        self.assertEqual(self.contract["canonical"]["serverManifest"]["version"], version)
        self.assertIn(pin, self.readme)
        self.assertIn(f"MCP {version}", self.readme)
        self.assertIn(
            f"{len(tools)} read-only tools and {len(prompts)} guided prompts",
            self.readme,
        )
        for name in (*tools, *prompts):
            self.assertIn(f"`{name}`", self.readme)

    def test_server_manifest_matches_the_canonical_contract(self) -> None:
        metadata = self.contract["registryMetadata"]
        self.assertEqual(self.server["version"], metadata["version"])
        self.assertEqual(metadata["version"], "1.8.1")
        self.assertEqual(self.contract["serverVersion"], "1.8.1")
        self.assertEqual(self.server["name"], "io.github.beepboop2025/liquilens")
        self.assertEqual(
            self.server["repository"]["url"],
            "https://github.com/beepboop2025/liquilens-mcp",
        )
        self.assertEqual(self.server["repository"]["url"], metadata["repositoryUrl"])
        self.assertEqual(self.server["websiteUrl"], "https://liquilens.in/agents/")
        self.assertEqual(self.server["websiteUrl"], metadata["websiteUrl"])
        self.assertEqual(self.server["description"], metadata["description"])
        self.assertEqual(
            self.contract["canonical"]["serverManifest"]["repository"]["url"],
            self.contract["canonical"]["repository"],
        )
        self.assertEqual(self.server["title"], metadata["title"])
        self.assertEqual(self.server["icons"], metadata["icons"])
        self.assertEqual(self.server["repository"]["source"], "github")
        self.assertLessEqual(len(self.server["description"]), 100)
        self.assertEqual(
            self.server["$schema"],
            "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
        )
        self.assertEqual(
            self.server["remotes"],
            [{"type": "streamable-http", "url": "https://api.liquilens.in/mcp"}],
        )
        for key in ("websiteUrl",):
            parsed = urlparse(self.server[key])
            self.assertEqual(parsed.scheme, "https")
            self.assertTrue(parsed.netloc)

    def test_readme_advertises_every_capability_exactly_once(self) -> None:
        tool_section = _section(self.readme, "## Tools", "## Prompts")
        prompt_section = _section(self.readme, "## Prompts", "## The governance line")
        table_pattern = re.compile(r"^\| `([a-z][a-z0-9_]+)` \|", re.MULTILINE)
        self.assertEqual(table_pattern.findall(tool_section), self.contract["tools"])
        self.assertEqual(
            table_pattern.findall(prompt_section), self.contract["prompts"]
        )
        self.assertIn("23 read-only tools and 5 guided prompts", self.readme)

    def test_readme_documents_versions_and_evidence_boundary(self) -> None:
        self.assertIn(f"MCP {self.contract['serverVersion']}", self.readme)
        for version in self.contract["protocolVersions"]:
            self.assertIn(version, self.readme)
        for token in (
            "PERIOD_END_PROXY_CONSTRUCTION_PIT",
            "CURRENT_AMENDED_CONSTRUCTION_PIT",
            "NAMED_CASE_FILES_CONSTRUCTION_PIT",
            "validated_backtest_eligible: false",
            "real_money_eligible: false",
        ):
            self.assertIn(token, self.readme)
        self.assertNotIn("MCP 1.5.0", self.readme)

    def test_registry_display_metadata_is_plain_and_first_party(self) -> None:
        # The hosted server answers initialize with this title (read 15 Nov 2026);
        # the registry card and the server should name the product the same way.
        self.assertEqual(self.server["title"], "LiquiLens Failure Radar")
        research = _strict_json(ROOT / "research-data-server.json")
        for label, text in (
            ("server title", self.server["title"]),
            ("server description", self.server["description"]),
            ("research title", research["title"]),
            ("research description", research["description"]),
        ):
            with self.subTest(field=label):
                self.assertEqual(_dash_punctuation(text), [], text)
        self.assertEqual(
            self.server["icons"],
            [{
                "src": "https://liquilens.in/brand/liquilens-mark-512.png",
                "mimeType": "image/png",
                "sizes": ["512x512"],
            }],
        )

    def test_shipped_listing_text_has_no_dash_punctuation(self) -> None:
        # GitHub's MCP Registry and VS Code show this repository's README as the
        # server page, so the listing text follows the no em or en dash rule.
        paths = sorted(
            {*ROOT.glob("*.md"), *ROOT.glob("skills/**/*.md")},
            key=lambda path: path.as_posix(),
        )
        self.assertIn(ROOT / "README.md", paths)
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(
                    _dash_punctuation(path.read_text(encoding="utf-8")), []
                )

    def test_license_scope_is_published_with_the_listing(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        notice = " ".join((ROOT / "NOTICE.md").read_text(encoding="utf-8").split())
        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("https://liquilens.in/terms/", notice)
        self.assertIn("https://api.liquilens.in/mcp", notice)
        self.assertIn("MIT No Attribution", notice)
        self.assertIn("[NOTICE.md](NOTICE.md)", self.readme)

    def test_secondary_registry_metadata_is_minimal(self) -> None:
        self.assertEqual(
            self.glama,
            {
                "$schema": "https://glama.ai/mcp/schemas/server.json",
                "maintainers": ["beepboop2025"],
            },
        )


if __name__ == "__main__":
    unittest.main()
