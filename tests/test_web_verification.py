from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_checks
import web_verification


class WebVerificationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "apps/web").mkdir(parents=True)
        (self.root / "package.json").write_text(json.dumps({"packageManager": "pnpm@9.15.9"}))

    def test_prerequisites_are_actionable_without_installing(self):
        with mock.patch.object(project_checks.shutil, "which", return_value=None):
            self.assertIn("Node.js", project_checks.web_prerequisite(self.root)[0])
        with mock.patch.object(project_checks.shutil, "which", return_value="node"), mock.patch.object(project_checks.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "v18.20.0\n")
            self.assertIn("20.9", project_checks.web_prerequisite(self.root)[0])
            run.return_value = subprocess.CompletedProcess([], 0, "v22.12.0\n")
            self.assertEqual("pnpm install --frozen-lockfile", project_checks.web_prerequisite(self.root)[1])
            (self.root / "node_modules/.pnpm").mkdir(parents=True)
            (self.root / "node_modules/.modules.yaml").touch()
            self.assertIsNone(project_checks.web_prerequisite(self.root))
            self.assertTrue(all(call.args[0] == ["node", "--version"] for call in run.call_args_list))
        with mock.patch.object(project_checks.shutil, "which", side_effect=["node", None]), mock.patch.object(project_checks.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "v22.12.0\n")):
            self.assertIn("pnpm@9.15.9", project_checks.web_prerequisite(self.root)[1])

    def test_broken_and_timed_out_node_is_not_accepted(self):
        with mock.patch.object(project_checks.shutil, "which", return_value="node"), mock.patch.object(project_checks.subprocess, "run") as run:
            for output in ("garbage", "v22.0.0-beta", "v20.8.0"):
                run.return_value = subprocess.CompletedProcess([], 0, output)
                self.assertIsNotNone(project_checks.web_prerequisite(self.root))
            run.side_effect = subprocess.TimeoutExpired("node", 10)
            self.assertIsNotNone(project_checks.web_prerequisite(self.root))

    def run_verified(self, mode, *, browser_code=0):
        with mock.patch.object(web_verification, "active_profiles", return_value={"web-next"}), mock.patch.object(web_verification, "web_prerequisite", return_value=None), mock.patch.object(web_verification.subprocess, "run", return_value=subprocess.CompletedProcess([], browser_code)) as run, mock.patch.object(web_verification, "run_command") as checks:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                web_verification.verify(mode, self.root)
            return [call.args[0] for call in checks.call_args_list], output.getvalue(), run.call_args_list

    def test_web_runs_foundation_build_and_browser_but_never_claims_visual(self):
        commands, output, _ = self.run_verified("web")
        self.assertEqual(["bash", "scripts/verify.sh", "full"], commands[0])
        self.assertEqual(["pnpm", "--dir", "apps/web", "build"], commands[1])
        self.assertEqual(["--grep-invert", "@visual"], commands[2][-3:-1])
        self.assertFalse(any(part.endswith(".spec.ts") for part in commands[2]))
        self.assertEqual("--update-snapshots=none", commands[2][-1])
        self.assertIn("NOT RUN: visual comparison", output)
        self.assertIn("not certified", output)
        self.assertFalse(any("install" in part for command in commands for part in command))

    def test_missing_browser_fails_with_download_instruction_not_install(self):
        with self.assertRaisesRegex(project_checks.ProjectCheckError, "Nothing was installed"):
            self.run_verified("web", browser_code=1)

    def test_missing_baselines_fail_without_creating_files(self):
        with self.assertRaisesRegex(project_checks.ProjectCheckError, "No baseline was created"):
            self.run_verified("visual")
        self.assertFalse((self.root / "apps/web/tests/visual.spec.ts-snapshots").exists())

    def test_visual_is_comparison_only(self):
        folder = self.root / "apps/web/tests/features/queue.spec.ts-snapshots"
        folder.mkdir(parents=True)
        (folder / f"example-desktop-{sys.platform}.png").write_bytes(b"fixture")
        commands, output, _ = self.run_verified("visual")
        self.assertEqual(2, len(commands))
        self.assertEqual(["--grep", "@visual"], commands[-1][-3:-1])
        self.assertEqual("--update-snapshots=none", commands[-1][-1])
        self.assertIn("Baselines were not updated", output)

    def test_disabled_web_and_missing_dependencies_run_no_checks(self):
        with mock.patch.object(web_verification, "active_profiles", return_value={"core"}), mock.patch.object(web_verification, "run_command") as check:
            with self.assertRaisesRegex(project_checks.ProjectCheckError, "No active web"):
                web_verification.verify("web", self.root)
            check.assert_not_called()
        with mock.patch.object(web_verification, "active_profiles", return_value={"web-next"}), mock.patch.object(web_verification, "web_prerequisite", return_value=("Missing deps", "pnpm install --frozen-lockfile")), mock.patch.object(web_verification, "run_command") as check:
            with self.assertRaisesRegex(project_checks.ProjectCheckError, "Missing deps"):
                web_verification.verify("web", self.root)
            check.assert_not_called()

    def test_nonzero_and_timeout_are_not_success(self):
        with mock.patch.object(web_verification.subprocess, "run", return_value=subprocess.CompletedProcess([], 7)):
            with self.assertRaisesRegex(project_checks.ProjectCheckError, "Check failed"):
                web_verification.run_command(["test-command"], self.root)
        with mock.patch.object(web_verification.subprocess, "run", side_effect=subprocess.TimeoutExpired("test-command", 900)):
            with self.assertRaisesRegex(project_checks.ProjectCheckError, "could not complete"):
                web_verification.run_command(["test-command"], self.root)

    def test_unknown_scope_and_baseline_updates_are_rejected(self):
        root = Path(__file__).resolve().parents[1]
        for arguments in (["unknown"], ["visual", "--update-snapshots"]):
            result = subprocess.run(["bash", "scripts/verify.sh", *arguments], cwd=root, capture_output=True, text=True)
            self.assertEqual(2, result.returncode)


if __name__ == "__main__":
    unittest.main()
