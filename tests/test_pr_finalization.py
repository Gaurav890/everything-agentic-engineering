from __future__ import annotations

import json
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import finalize_pr


def task_record(status: str = "review") -> dict:
    return {
        "id": "T-100",
        "title": "Test finalization",
        "status": status,
        "tracking": {"mode": "required", "issues": ["#32"]},
    }


class FakeRunner:
    def __init__(
        self,
        root: Path,
        *,
        is_draft: bool = True,
        dirty_before: str = "",
        dirty_after: str = " M docs/40-execution/TASKS.jsonl",
    ) -> None:
        self.root = root
        self.is_draft = is_draft
        self.dirty_before = dirty_before
        self.dirty_after = dirty_after
        self.prepared = False
        self.calls: list[list[str]] = []

    def __call__(self, command: list[str]) -> str:
        self.calls.append(command)
        if command == ["git", "branch", "--show-current"]:
            return "feat/T-100-finalize"
        if command == ["git", "status", "--porcelain=v1"]:
            return self.dirty_after if self.prepared else self.dirty_before
        if command[:3] == ["gh", "pr", "view"]:
            return json.dumps(
                {
                    "number": 42,
                    "url": "https://example.test/pull/42",
                    "isDraft": self.is_draft,
                    "state": "OPEN",
                    "headRefName": "feat/T-100-finalize",
                    "baseRefName": "main",
                    "title": "feat(T-100): make finalization clear",
                    "body": "## Linked work\n\n- Issue: Closes #32\n- Task: T-100\n",
                }
            )
        if command[0:2] == ["bash", str(self.root / "scripts/prepare-merge.sh")]:
            path = self.root / finalize_pr.LEDGER
            record = json.loads(path.read_text().strip())
            record["status"] = "done"
            path.write_text(json.dumps(record) + "\n")
            self.prepared = True
            return "Prepared T-100 for merge."
        if command == ["git", "diff", "--cached", "--name-only"]:
            return str(finalize_pr.LEDGER)
        return ""


class PRFinalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / finalize_pr.LEDGER).parent.mkdir(parents=True)
        (self.root / "scripts").mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_task(self, status: str = "review") -> None:
        (self.root / finalize_pr.LEDGER).write_text(
            json.dumps(task_record(status)) + "\n"
        )

    def finalize(self, runner: FakeRunner, *, dry_run: bool = False) -> dict:
        with redirect_stdout(io.StringIO()):
            return finalize_pr.finalize(
                "T-100", root=self.root, runner=runner, dry_run=dry_run
            )

    def assert_no_approval_or_merge(self, calls: list[list[str]]) -> None:
        self.assertFalse(any(call[:3] == ["gh", "pr", "merge"] for call in calls))
        self.assertFalse(any(call[:3] == ["gh", "pr", "review"] for call in calls))

    def test_command_output_preserves_git_porcelain_status_columns(self) -> None:
        completed = SimpleNamespace(
            returncode=0,
            stdout=" M docs/40-execution/TASKS.jsonl\n",
            stderr="",
        )
        with patch.object(finalize_pr.subprocess, "run", return_value=completed):
            output = finalize_pr.run_command(["git", "status", "--porcelain=v1"])
        self.assertEqual(output, " M docs/40-execution/TASKS.jsonl\n")
        self.assertEqual(
            finalize_pr.changed_paths(output),
            {"docs/40-execution/TASKS.jsonl"},
        )

    def test_dry_run_performs_only_read_only_validation(self) -> None:
        self.write_task()
        runner = FakeRunner(self.root)
        result = self.finalize(runner, dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(
            json.loads((self.root / finalize_pr.LEDGER).read_text())["status"],
            "review",
        )
        forbidden = {"add", "commit", "push"}
        self.assertFalse(
            any(call[0] == "git" and len(call) > 1 and call[1] in forbidden for call in runner.calls)
        )
        self.assertFalse(any(call[:3] == ["gh", "pr", "ready"] for call in runner.calls))
        self.assert_no_approval_or_merge(runner.calls)

    def test_approved_draft_is_prepared_pushed_and_marked_ready(self) -> None:
        self.write_task()
        runner = FakeRunner(self.root, is_draft=True)
        result = self.finalize(runner)
        self.assertFalse(result["dry_run"])
        self.assertEqual(
            json.loads((self.root / finalize_pr.LEDGER).read_text())["status"],
            "done",
        )
        self.assertIn(["git", "add", "--", str(finalize_pr.LEDGER)], runner.calls)
        self.assertIn(["git", "push", "origin", "HEAD"], runner.calls)
        self.assertIn(["gh", "pr", "ready", "42"], runner.calls)
        self.assertIn(
            ["gh", "pr", "checks", "42", "--watch", "--fail-fast"], runner.calls
        )
        self.assert_no_approval_or_merge(runner.calls)

    def test_already_ready_pr_recovers_by_pushing_without_ready_transition(self) -> None:
        self.write_task()
        runner = FakeRunner(self.root, is_draft=False)
        self.finalize(runner)
        self.assertIn(["git", "push", "origin", "HEAD"], runner.calls)
        self.assertFalse(any(call[:3] == ["gh", "pr", "ready"] for call in runner.calls))
        self.assertIn(
            ["gh", "pr", "checks", "42", "--watch", "--fail-fast"], runner.calls
        )
        self.assert_no_approval_or_merge(runner.calls)

    def test_unrelated_post_verification_change_fails_before_staging(self) -> None:
        self.write_task()
        runner = FakeRunner(
            self.root,
            dirty_after=(
                " M docs/40-execution/TASKS.jsonl\n"
                " M README.md"
            ),
        )
        with self.assertRaisesRegex(
            finalize_pr.FinalizationError, "outside the task ledger"
        ):
            self.finalize(runner)
        self.assertFalse(any(call[0:2] == ["git", "add"] for call in runner.calls))
        self.assertFalse(any(call[0:2] == ["git", "commit"] for call in runner.calls))
        self.assert_no_approval_or_merge(runner.calls)

    def test_dirty_worktree_fails_before_github_or_task_mutation(self) -> None:
        self.write_task()
        runner = FakeRunner(self.root, dirty_before=" M README.md")
        with self.assertRaisesRegex(finalize_pr.FinalizationError, "must be clean"):
            self.finalize(runner)
        self.assertFalse(any(call[0] == "gh" for call in runner.calls))
        self.assertFalse(any("prepare-merge.sh" in " ".join(call) for call in runner.calls))

    def test_already_prepared_task_is_idempotent_and_does_not_recommit(self) -> None:
        self.write_task("done")
        runner = FakeRunner(self.root, is_draft=False)
        self.finalize(runner)
        self.assertFalse(any("prepare-merge.sh" in " ".join(call) for call in runner.calls))
        self.assertFalse(any(call[0:2] == ["git", "commit"] for call in runner.calls))
        self.assertIn(["git", "push", "origin", "HEAD"], runner.calls)
        self.assert_no_approval_or_merge(runner.calls)


if __name__ == "__main__":
    unittest.main()
