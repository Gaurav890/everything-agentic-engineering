from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_agent_plugin import (
    PLUGIN_SCHEMA,
    PluginValidationError,
    validate_plugin,
)


ROOT = Path(__file__).resolve().parents[1]


class AgentPluginTests(unittest.TestCase):
    def test_repository_portable_core_is_valid_and_skills_only(self) -> None:
        report = validate_plugin(ROOT)
        self.assertEqual(report["name"], "everything-agentic-engineering")
        self.assertGreater(len(report["skills"]), 0)
        self.assertFalse(report["mcp_manifest"])

    def test_portable_manifest_is_closed_and_does_not_inline_components(self) -> None:
        manifest = json.loads((ROOT / "plugin.json").read_text())
        package = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(manifest["$schema"], PLUGIN_SCHEMA)
        self.assertEqual(manifest["version"], package["version"])
        for field in ("skills", "mcpServers", "hooks", "commands", "interface"):
            self.assertNotIn(field, manifest)

    def test_codex_native_manifest_remains_a_separate_compatibility_surface(self) -> None:
        portable = json.loads((ROOT / "plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(codex["name"], portable["name"])
        self.assertEqual(codex["version"], portable["version"])
        self.assertEqual(codex["skills"], "./skills/")
        self.assertIn("interface", codex)

    def test_project_mcp_config_is_not_misrepresented_as_portable_mcp(self) -> None:
        self.assertTrue((ROOT / ".mcp.json").is_file())
        self.assertFalse((ROOT / "mcp.json").exists())

    def test_unknown_portable_manifest_field_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "plugin.json").write_text(
                json.dumps(
                    {
                        "$schema": PLUGIN_SCHEMA,
                        "name": "fixture-plugin",
                        "skills": "./skills/",
                    }
                )
            )
            with self.assertRaisesRegex(PluginValidationError, "non-portable"):
                validate_plugin(root)

    def test_skills_symlink_cannot_escape_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external:
            root = Path(temporary)
            outside = Path(external)
            (root / "plugin.json").write_text(
                json.dumps({"$schema": PLUGIN_SCHEMA, "name": "fixture-plugin"})
            )
            (outside / "example").mkdir()
            (outside / "example/SKILL.md").write_text(
                "---\nname: example\ndescription: fixture\n---\n"
            )
            (root / "skills").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(PluginValidationError, "outside"):
                validate_plugin(root)

    def test_nonempty_portable_mcp_requires_the_followup_compatibility_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "plugin.json").write_text(
                json.dumps({"$schema": PLUGIN_SCHEMA, "name": "fixture-plugin"})
            )
            (root / "mcp.json").write_text(
                json.dumps(
                    {
                        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
                        "mcpServers": {"unsafe": {"type": "stdio", "command": "npx"}},
                    }
                )
            )
            with self.assertRaisesRegex(PluginValidationError, "separately reviewed"):
                validate_plugin(root)


if __name__ == "__main__":
    unittest.main()
