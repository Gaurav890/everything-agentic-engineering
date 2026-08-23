from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agentic_cli  # noqa: E402


class AgenticCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = agentic_cli.load_registry(ROOT)

    def test_every_shell_file_is_classified_exactly_once(self) -> None:
        actual = {
            path.relative_to(ROOT).as_posix()
            for directory in (ROOT / "scripts", ROOT / ".claude" / "hooks")
            for path in directory.glob("*.sh")
        }
        inventory = self.registry["shell_inventory"]
        registered = [item["path"] for item in inventory]
        self.assertEqual(len(registered), len(set(registered)))
        self.assertEqual(actual, set(registered))
        self.assertEqual(
            {"public", "internal", "compatibility", "security_hook"},
            {item["classification"] for item in inventory},
        )

    def test_public_commands_have_one_public_inventory_target(self) -> None:
        inventory = {item["path"]: item for item in self.registry["shell_inventory"]}
        command_names = {" ".join(item["path"]) for item in self.registry["commands"]}
        targets = []
        for command in self.registry["commands"]:
            target = command["target"]
            targets.append(target)
            self.assertEqual("public", inventory[target]["classification"])
            self.assertEqual(" ".join(command["path"]), inventory[target]["canonical_command"])
            self.assertTrue((ROOT / target).is_file())
            self.assertTrue(os.access(ROOT / target, os.X_OK))
        self.assertEqual(len(targets), len(set(targets)))
        self.assertEqual(
            command_names,
            {
                item["canonical_command"]
                for item in inventory.values()
                if item["classification"] == "public"
            },
        )

    def test_internal_and_hook_scripts_are_not_public_commands(self) -> None:
        targets = {item["target"] for item in self.registry["commands"]}
        for item in self.registry["shell_inventory"]:
            if item["classification"] in {"internal", "compatibility", "security_hook"}:
                self.assertNotIn(item["path"], targets)

    def test_top_help_is_grouped_and_hides_internal_scripts(self) -> None:
        out = io.StringIO()
        self.assertEqual(0, agentic_cli.main([], root=ROOT, out=out))
        help_text = out.getvalue()
        self.assertIn("./agentic <group> <command>", help_text)
        self.assertIn("task", help_text)
        self.assertIn("verify", help_text)
        self.assertNotIn("prepare-merge", help_text)
        self.assertNotIn("pre-tool-security", help_text)

    def test_group_and_command_help_do_not_execute_targets(self) -> None:
        out = io.StringIO()
        with mock.patch.object(agentic_cli.subprocess, "run") as run:
            self.assertEqual(0, agentic_cli.main(["profile"], root=ROOT, out=out))
            self.assertIn("profile select", out.getvalue())
            out.seek(0)
            out.truncate(0)
            self.assertEqual(
                0,
                agentic_cli.main(["profile", "select", "--help"], root=ROOT, out=out),
            )
            self.assertIn("comma-separated-profiles", out.getvalue())
            run.assert_not_called()

    def test_json_discovery_contains_only_public_commands(self) -> None:
        out = io.StringIO()
        self.assertEqual(
            0,
            agentic_cli.main(["commands", "--json"], root=ROOT, out=out),
        )
        payload = json.loads(out.getvalue())
        names = {item["command"] for item in payload["commands"]}
        self.assertIn("pr finalize", names)
        self.assertIn("workspace worktree", names)
        self.assertIn("agents", names)
        self.assertIn("capabilities", names)
        self.assertIn("doctor plugin", names)
        self.assertIn("setup create", names)
        self.assertIn("design", names)
        self.assertIn("evolve", names)
        self.assertNotIn("prepare merge", names)

    def test_arguments_are_forwarded_as_a_list_without_shell_evaluation(self) -> None:
        completed = subprocess.CompletedProcess(args=[], returncode=7)
        with mock.patch.object(agentic_cli.subprocess, "run", return_value=completed) as run:
            result = agentic_cli.main(
                ["profile", "select", "web-next,design-critical", "--yes"],
                root=ROOT,
            )
        self.assertEqual(7, result)
        run.assert_called_once_with(
            [
                str((ROOT / "scripts" / "profile-select.sh").resolve()),
                "web-next,design-critical",
                "--yes",
            ],
            cwd=ROOT,
            check=False,
        )

    def test_root_entrypoint_is_executable_and_runs_help(self) -> None:
        entrypoint = ROOT / "agentic"
        self.assertTrue(os.access(entrypoint, os.X_OK))
        completed = subprocess.run(
            [str(entrypoint), "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("Everything Agentic Engineering", completed.stdout)


if __name__ == "__main__":
    unittest.main()
