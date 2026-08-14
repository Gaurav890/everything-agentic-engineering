from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_compatibility import MCPCompatibilityError, validate  # noqa: E402


class MCPCompatibilityTests(unittest.TestCase):
    def fixture(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".agentic").mkdir()
        shutil.copy(
            ROOT / ".agentic/mcp-compatibility.json",
            root / ".agentic/mcp-compatibility.json",
        )
        shutil.copy(ROOT / ".mcp.json", root / ".mcp.json")
        return temporary

    def test_repository_policy_is_valid_and_portable_packaging_is_blocked(self) -> None:
        report = validate(ROOT)
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["portable_packaging"], "blocked")
        self.assertEqual(report["root_mcp_manifest"], "absent")
        self.assertEqual(
            {"perplexity", "firecrawl", "playwright"},
            {server["name"] for server in report["servers"]},
        )
        self.assertFalse(report["server_execution_performed"])
        self.assertFalse(report["mutation_performed"])

    def test_json_doctor_is_machine_readable_and_does_not_echo_secrets(self) -> None:
        environment = os.environ.copy()
        environment["PERPLEXITY_API_KEY"] = "must-not-appear"
        environment["FIRECRAWL_API_KEY"] = "also-must-not-appear"
        completed = subprocess.run(
            [str(ROOT / "scripts/mcp-doctor.sh"), "--json"],
            cwd=ROOT,
            env=environment,
            check=True,
            text=True,
            capture_output=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["verdict"], "pass")
        self.assertNotIn("must-not-appear", completed.stdout)
        self.assertNotIn("also-must-not-appear", completed.stdout)
        self.assertFalse(report["server_execution_performed"])

    def test_literal_project_credential_fails_closed(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            project = json.loads((root / ".mcp.json").read_text())
            project["mcpServers"]["perplexity"]["env"]["PERPLEXITY_API_KEY"] = (
                "literal-secret"
            )
            (root / ".mcp.json").write_text(json.dumps(project))
            with self.assertRaisesRegex(MCPCompatibilityError, "environment reference"):
                validate(root)

    def test_project_server_drift_fails_closed(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            project = json.loads((root / ".mcp.json").read_text())
            project["mcpServers"]["unreviewed"] = {
                "command": "npx",
                "args": ["-y", "unreviewed"],
            }
            (root / ".mcp.json").write_text(json.dumps(project))
            with self.assertRaisesRegex(MCPCompatibilityError, "core servers drifted"):
                validate(root)

    def test_root_mcp_manifest_is_rejected_while_decision_is_blocked(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            (root / "mcp.json").write_text(
                json.dumps(
                    {
                        "$schema": (
                            "https://agent-plugins.org/schemas/1.0.0/"
                            "mcp.schema.json"
                        ),
                        "mcpServers": {},
                    }
                )
            )
            with self.assertRaisesRegex(MCPCompatibilityError, "must remain absent"):
                validate(root)

    def test_unverified_client_cannot_be_recorded_as_portable(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            policy = json.loads(
                (root / ".agentic/mcp-compatibility.json").read_text()
            )
            policy["clients"]["codex"]["portable_plugin_mcp_verified"] = True
            (root / ".agentic/mcp-compatibility.json").write_text(json.dumps(policy))
            with self.assertRaisesRegex(MCPCompatibilityError, "must remain unverified"):
                validate(root)


if __name__ == "__main__":
    unittest.main()
