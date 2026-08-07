from __future__ import annotations

import json
import os
import re
import subprocess
import unittest
from pathlib import Path

from scripts.validate_codex_agents import (
    EXPECTED_ROLES,
    AgentValidationError,
    load_restricted_toml,
    validate_role_directory,
)


ROOT = Path(__file__).resolve().parents[1]


class CodexAdapterTests(unittest.TestCase):
    def test_shared_skill_catalogs_resolve_to_canonical_source(self) -> None:
        canonical = (ROOT / ".claude/skills").resolve()
        self.assertTrue((ROOT / ".agents/skills").is_symlink())
        self.assertTrue((ROOT / "skills").is_symlink())
        self.assertEqual((ROOT / ".agents/skills").resolve(), canonical)
        self.assertEqual((ROOT / "skills").resolve(), canonical)

        expected = sorted(path.parent.name for path in canonical.glob("*/SKILL.md"))
        discovered = sorted(
            path.parent.name for path in (ROOT / ".agents/skills").glob("*/SKILL.md")
        )
        packaged = sorted(
            path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")
        )
        self.assertEqual(discovered, expected)
        self.assertEqual(packaged, expected)

    def test_public_codex_config_does_not_expand_authority(self) -> None:
        config = (ROOT / ".codex/config.toml").read_text()
        forbidden = {
            "approval_policy",
            "default_permissions",
            "model",
            "model_provider",
            "model_providers",
            "mcp_servers",
            "openai_base_url",
            "permissions",
            "sandbox_mode",
            "sandbox_workspace_write",
        }
        for key in forbidden:
            self.assertIsNone(
                re.search(
                    rf"(?m)^\s*(?:\[{re.escape(key)}(?:\.|\])|{re.escape(key)}\s*=)",
                    config,
                ),
                key,
            )
        self.assertRegex(
            config,
            r"(?m)^max_concurrent_threads_per_session\s*=\s*4\s*$",
        )
        self.assertRegex(config, r"(?m)^hooks\s*=\s*true\s*$")

    def test_plugin_is_skills_only_and_strict_semver(self) -> None:
        plugin = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(plugin["name"], "everything-agentic-engineering")
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        for key in ("hooks", "mcpServers", "apps"):
            self.assertNotIn(key, plugin)

    def test_codex_hooks_reuse_reviewed_safety_scripts(self) -> None:
        hooks = json.loads((ROOT / ".codex/hooks.json").read_text())
        serialized = json.dumps(hooks)
        self.assertIn("pre-tool-security.sh", serialized)
        self.assertIn("post-edit-secret-scan.sh", serialized)
        self.assertIn("PreToolUse", hooks["hooks"])
        self.assertIn("PostToolUse", hooks["hooks"])

    def test_codex_skill_metadata_is_discoverable(self) -> None:
        skill_root = ROOT / ".claude/skills/codex-adapter"
        text = (skill_root / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: codex-adapter", text)
        self.assertRegex(text, r"(?m)^description: .+")

        metadata = (skill_root / "agents/openai.yaml").read_text()
        self.assertIn("$codex-adapter", metadata)
        self.assertNotIn("TODO", text)
        self.assertNotIn("TODO", metadata)

    def test_project_codex_roles_are_complete_and_read_only(self) -> None:
        roles = validate_role_directory(ROOT / ".codex/agents")
        self.assertEqual(set(roles), EXPECTED_ROLES)
        for name, path in roles.items():
            role = load_restricted_toml(path)
            self.assertEqual(role["name"], name)
            self.assertEqual(role["sandbox_mode"], "read-only")
            self.assertEqual(
                set(role),
                {"name", "description", "developer_instructions", "sandbox_mode"},
            )

    def test_codex_role_validator_rejects_authority_expansion(self) -> None:
        fixture = ROOT / ".cache/test-codex-role.toml"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text(
            'name = "unsafe"\n'
            'description = "Unsafe test role"\n'
            'sandbox_mode = "workspace-write"\n'
            'model = "unreviewed"\n'
            'developer_instructions = """\nTest only.\n"""\n'
        )
        try:
            role = load_restricted_toml(fixture)
            self.assertIn("model", role)
            with self.assertRaises(AgentValidationError):
                validate_role_directory(fixture.parent)
        finally:
            fixture.unlink(missing_ok=True)

    def test_codex_roles_do_not_replace_worktrees_for_parallel_writes(self) -> None:
        agreement = (ROOT / "AGENTS.md").read_text()
        guide = (ROOT / "docs/70-collaboration/PARALLEL_TERMINALS.md").read_text()
        self.assertIn("In-session Codex subagents", agreement)
        self.assertIn("separate branch and worktree", agreement)
        self.assertIn("Subagents versus worktree workers", guide)
        self.assertIn("read-only", guide)

    def test_doctor_passes_without_requiring_a_runtime_install(self) -> None:
        environment = os.environ.copy()
        environment["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin"
        result = subprocess.run(
            [str(ROOT / "scripts/codex-doctor.sh")],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Codex adapter valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
