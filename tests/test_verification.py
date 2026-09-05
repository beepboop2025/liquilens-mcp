from __future__ import annotations

import ast
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pin = load_script("verify_core_pin")
live = load_script("smoke_live_mcp")


class StaticPinTests(unittest.TestCase):
    def test_composed_inventory_is_read_without_executing_values(self):
        tree = ast.parse("TOOLS = {**BANK_TOOLS, 'existing': do_not_execute()}")
        self.assertEqual(pin._mapping_keys(tree, "TOOLS", {"BANK_TOOLS": ["bank"]}),
                         ["bank", "existing"])

    def test_unknown_dynamic_and_duplicate_expansions_fail(self):
        for source in (
            "TOOLS = {**UNKNOWN}",
            "TOOLS = {**load_tools()}",
            "TOOLS = {**BANK_TOOLS, 'bank': None}",
            "TOOLS = {'tool': None, 'tool': None}",
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                pin._mapping_keys(ast.parse(source), "TOOLS", {"BANK_TOOLS": ["bank"]})

    def test_exact_source_pin_manifest_and_import_are_required(self):
        contract = json.loads((ROOT / "contract.json").read_text())
        manifest = json.loads((ROOT / "server.json").read_text())
        with tempfile.TemporaryDirectory() as temporary:
            core = Path(temporary)
            backend = core / "backend"
            backend.mkdir()
            # Only inventory keys are inspected; application handlers never execute.
            bank_tools = [n for n in contract["tools"] if n.startswith("bank")]
            bank_prompts = ["bank_asset_quality_brief"]
            bank_source = (f"BANK_TOOLS = {dict.fromkeys(bank_tools)!r}\n"
                           f"BANK_PROMPTS = {dict.fromkeys(bank_prompts)!r}\n")
            server_source = (
                "from mcp_bank_tools import BANK_TOOLS, BANK_PROMPTS\n"
                f"TOOLS = {{**BANK_TOOLS, {', '.join(repr(n) + ': None' for n in contract['tools'] if n not in bank_tools)}}}\n"
                f"PROMPTS = {{**BANK_PROMPTS, {', '.join(repr(n) + ': None' for n in contract['prompts'] if n not in bank_prompts)}}}\n"
            )
            (backend / "mcp_bank_tools.py").write_text(bank_source)
            (backend / "mcp_server.py").write_text(server_source)
            versions = contract["protocolVersions"]
            (backend / "mcp_protocol.py").write_text(
                f"MODERN_PROTOCOL_VERSION = {versions[0]!r}\n"
                f"PROTOCOL_VERSION = {versions[1]!r}\n"
                f"LEGACY_PROTOCOL_VERSIONS = (PROTOCOL_VERSION, {versions[2]!r}, {versions[3]!r})\n"
                f"SERVER_VERSION = {contract['serverVersion']!r}\n"
            )
            (core / "server.json").write_text(json.dumps(manifest))
            with patch.object(pin.subprocess, "check_output", return_value=contract["canonical"]["releaseCommit"]), redirect_stdout(io.StringIO()):
                pin.verify(core)
                changed = dict(manifest, description="Stale description")
                (core / "server.json").write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, "core server manifest"):
                    pin.verify(core)
                (core / "server.json").write_text(json.dumps(manifest))
                (backend / "mcp_server.py").write_text(server_source.replace("from mcp_bank_tools", "from unrelated"))
                with self.assertRaisesRegex(ValueError, "must import"):
                    pin.verify(core)
            with patch.object(pin.subprocess, "check_output", return_value="0" * 40):
                with self.assertRaisesRegex(ValueError, "listing pins"):
                    pin.verify(core)


class Response(io.BytesIO):
    status = 200


class LiveProtocolTests(unittest.TestCase):
    def rpc(self, body):
        with patch.object(live.urllib.request, "urlopen", return_value=Response(json.dumps(body).encode())):
            return live._rpc("https://api.liquilens.in/mcp", "tools/list", {}, 1,
                             protocol="2026-07-28")

    def test_json_rpc_failures_are_not_success(self):
        for body in (
            {"jsonrpc": "1.0", "id": 1, "result": {}},
            {"jsonrpc": "2.0", "id": True, "result": {}},
            {"jsonrpc": "2.0", "id": 2, "result": {}},
            {"jsonrpc": "2.0", "id": 1, "error": {"code": -32600}},
            {"jsonrpc": "2.0", "id": 1, "result": []},
        ):
            with self.subTest(body=body), self.assertRaises(RuntimeError):
                self.rpc(body)

    def test_http_and_response_limits_fail(self):
        for status, body in ((503, b"{}"), (200, b"x" * (live.MAX_RESPONSE_BYTES + 1))):
            response = Response(body)
            response.status = status
            with self.subTest(status=status), patch.object(live.urllib.request, "urlopen", return_value=response), self.assertRaises(RuntimeError):
                live._rpc("https://api.liquilens.in/mcp", "tools/list", {}, 1,
                          protocol="2026-07-28")

    def test_modern_and_legacy_smoke_are_labelled_and_check_tool_errors(self):
        contract = json.loads((ROOT / "contract.json").read_text())
        requests = []
        tool_error = False

        def respond(request, timeout):
            self.assertEqual(timeout, 20)
            headers = {k.lower(): v for k, v in request.header_items()}
            self.assertEqual(headers["x-liquilens-traffic-class"], "synthetic")
            self.assertEqual(headers["user-agent"], "LiquiLens-Operator-Growth-Audit/1.0")
            body = json.loads(request.data)
            requests.append(body)
            method = body["method"]
            self.assertEqual(headers["mcp-method"], method)
            if method == "initialize":
                self.assertEqual(body["params"]["clientInfo"]["name"], live.OPERATOR_CLIENT)
                result = {"serverInfo": {"version": contract["serverVersion"]}}
            else:
                meta = body["params"]["_meta"]
                self.assertEqual(meta["io.modelcontextprotocol/clientInfo"]["name"], live.OPERATOR_CLIENT)
                self.assertEqual(meta["io.modelcontextprotocol/protocolVersion"], headers["mcp-protocol-version"])
                result = {
                    "server/discover": {"supportedVersions": contract["protocolVersions"]},
                    "tools/list": {"tools": [{"name": n} for n in contract["tools"]]},
                    "prompts/list": {"prompts": [{"name": n} for n in contract["prompts"]]},
                    "resources/templates/list": {"resourceTemplates": []},
                    "tools/call": {"structuredContent": {"availability": "historical"}, "isError": tool_error},
                }[method]
                if method == "tools/call":
                    self.assertEqual(headers["mcp-name"], "evidence_markets")
            return Response(json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": result}).encode())

        with patch.object(live.urllib.request, "urlopen", side_effect=respond), redirect_stdout(io.StringIO()):
            live.smoke("https://api.liquilens.in/mcp")
            self.assertEqual(len(requests), 6)
            tool_error = True
            with self.assertRaisesRegex(RuntimeError, "structured content"):
                live.smoke("https://api.liquilens.in/mcp")


if __name__ == "__main__":
    unittest.main()
