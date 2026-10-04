"""Keep the published instruction bundle connected to its permitted MCP tools."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "skills" / "liquilens-trading-research"


class ClawHubSkillTests(unittest.TestCase):
    def test_bundle_remains_instructions_and_configuration_only(self) -> None:
        self.assertEqual(
            {path.name for path in BUNDLE.iterdir()},
            {"SKILL.md", "openclaw.json", "LICENSE"},
        )
        self.assertTrue(all(path.is_file() and not path.is_symlink() for path in BUNDLE.iterdir()))
        skill = (BUNDLE / "SKILL.md").read_text()
        self.assertIn("\nlicense: MIT-0\n", skill)
        self.assertIn("MIT No Attribution", (BUNDLE / "LICENSE").read_text())
        self.assertIn("does not relicense those responses", skill)

    def test_topic_tools_are_selectable_without_widening_the_server_contract(self) -> None:
        config = json.loads((BUNDLE / "openclaw.json").read_text())
        self.assertEqual(set(config), {"mcp"})
        self.assertEqual(set(config["mcp"]), {"servers"})
        expected = {
            "seiche": (
                "https://api.seiche.info/mcp",
                {"data_health", "funding_stress_now", "money_market_context",
                 "market_workbench", "gift_city_context", "gold_inventory_carry"},
            ),
            "liquilens": (
                "https://api.liquilens.in/mcp",
                {"banking_specialisation_coverage", "bank_asset_quality_review",
                 "institution_review_packet", "universe_search"},
            ),
            "undertow": (
                "https://api.seiche.info/undertow/mcp",
                {"exit_cost", "venue_concentration", "gold_cash_realisation"},
            ),
        }
        servers = config["mcp"]["servers"]
        self.assertEqual(set(servers), set(expected))
        skill = (BUNDLE / "SKILL.md").read_text()
        for name, (url, tools) in expected.items():
            with self.subTest(server=name):
                server = servers[name]
                self.assertEqual(set(server), {"url", "transport", "toolFilter"})
                self.assertEqual(server["url"], url)
                self.assertEqual(server["transport"], "streamable-http")
                self.assertEqual(set(server["toolFilter"]), {"include"})
                selected = server["toolFilter"]["include"]
                self.assertEqual(len(selected), len(set(selected)))
                self.assertEqual(set(selected), tools)
                self.assertIn(f"mcp.servers.{name}.url", skill)

    def test_new_topic_instructions_preserve_input_and_currency_boundaries(self) -> None:
        skill = (BUNDLE / "SKILL.md").read_text()
        gift = skill.split("**GIFT City (`gift-city`)**", 1)[1].split("**Forex", 1)[0]
        forex = skill.split("**Forex (`forex`)**", 1)[1].split("**Gold", 1)[0]
        gold = skill.split("**Gold (`gold`)**", 1)[1].split("**Money markets", 1)[0]
        self.assertIn("gift_city_context()", gift)
        self.assertIn("market_workbench", forex)
        self.assertIn("AED is not an accepted market_workbench currency", forex)
        self.assertIn("gold_inventory_carry", gold)
        self.assertIn("gold_cash_realisation", gold)
        self.assertIn("Ask for missing assumptions", gold)
        self.assertIn("Keep hypothetical proceeds separate from cash admitted", gold)
        self.assertIn("Selecting or installing a profile does not run a scenario", skill)
        self.assertIn("https://liquilens.in/agents/profiles.json", skill)


if __name__ == "__main__":
    unittest.main()
