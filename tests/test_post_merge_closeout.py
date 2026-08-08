from __future__ import annotations

import base64
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import post_merge_closeout


def encoded(content: str) -> dict[str, str]:
    return {
        "encoding": "base64",
        "content": base64.b64encode(content.encode()).decode(),
    }


def task_line(
    task_id: str = "T-100",
    *,
    status: str = "done",
    tracking: dict | None = None,
) -> str:
    value = {
        "id": task_id,
        "title": f"Test {task_id}",
        "status": status,
    }
    if tracking is not None:
        value["tracking"] = tracking
    return json.dumps(value) + "\n"


def required_tracking(issue: str = "#77") -> dict:
    return {"mode": "required", "issues": [issue]}


def pull_request(
    task_id: str = "T-100",
    *,
    issue_line: str = "Closes #77",
    number: int = 101,
) -> dict:
    return {
        "number": number,
        "title": f"feat({task_id}): finish task",
        "body": f"- Issue: {issue_line}\n- Task: {task_id}\n",
        "state": "MERGED",
        "url": f"https://example.test/pull/{number}",
        "mergedAt": "2026-08-07T00:00:00Z",
        "headRefName": f"feat/{task_id}-example",
        "baseRefName": "main",
    }


class FakeGitHub:
    def __init__(
        self,
        *,
        tasks: str,
        handoff: str = "# Handoff\n\n## Current goal\n\nSelect the next bounded task.\n",
        prs: list[dict] | None = None,
        issue_state: str = "CLOSED",
    ) -> None:
        self.tasks = tasks
        self.handoff = handoff
        self.prs = prs if prs is not None else [pull_request()]
        self.issue_state = issue_state
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str]):
        self.commands.append(command)
        if command[1:3] == ["repo", "view"]:
            return {
                "nameWithOwner": "owner/repository",
                "defaultBranchRef": {"name": "main"},
            }
        if command[1] == "api":
            endpoint = command[-1]
            if endpoint.endswith("TASKS.jsonl?ref=main"):
                return encoded(self.tasks)
            if endpoint.endswith("HANDOFF.md?ref=main"):
                return encoded(self.handoff)
        if command[1:3] == ["pr", "list"]:
            return self.prs
        if command[1:3] == ["issue", "view"]:
            return {
                "number": 77,
                "title": "Tracked outcome",
                "state": self.issue_state,
                "url": "https://example.test/issues/77",
                "closedAt": "2026-08-07T00:00:01Z"
                if self.issue_state == "CLOSED"
                else None,
            }
        raise AssertionError(f"Unexpected command: {command}")


class FakeGit:
    def __init__(self, *, dirty: bool = False) -> None:
        self.dirty = dirty
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str]) -> str:
        self.commands.append(command)
        if command[:3] == ["git", "branch", "--format=%(refname:short)"]:
            return "feat/T-100-example\n"
        if command[:4] == ["git", "worktree", "list", "--porcelain"]:
            return (
                "worktree /repo/.claude/worktrees/t-100\n"
                "HEAD abc123\n"
                "branch refs/heads/feat/T-100-example\n\n"
            )
        if command[:3] == ["git", "-C", "/repo/.claude/worktrees/t-100"]:
            return " M user-file.md\n" if self.dirty else ""
        raise AssertionError(f"Unexpected command: {command}")


class PostMergeCloseoutTests(unittest.TestCase):
    def run_closeout(self, github: FakeGitHub, git: FakeGit | None = None, task_id: str = "T-100"):
        with patch.object(post_merge_closeout.shutil, "which", return_value="/usr/bin/gh"):
            return post_merge_closeout.closeout(
                task_id,
                github_runner=github,
                text_runner=git or FakeGit(),
            )

    def test_verified_closeout_passes_and_only_suggests_cleanup(self) -> None:
        github = FakeGitHub(tasks=task_line(tracking=required_tracking()))
        git = FakeGit()
        result = self.run_closeout(github, git)
        self.assertEqual(result["verdict"], "PASS")
        self.assertTrue(result["read_only"])
        self.assertEqual(result["main_task"]["status"], "done")
        self.assertEqual(result["issues"][0]["live"]["state"], "CLOSED")
        self.assertEqual(
            result["cleanup"]["commands"],
            [
                "git worktree remove /repo/.claude/worktrees/t-100",
                "git branch -d feat/T-100-example",
            ],
        )
        self.assertFalse(result["cleanup"]["commands_executed"])

    def test_stale_transient_handoff_claim_is_attention(self) -> None:
        handoff = (
            "# Handoff\n\n## Current goal\n\n"
            "Review and merge T-100 before continuing.\n"
        )
        github = FakeGitHub(
            tasks=task_line(tracking=required_tracking()), handoff=handoff
        )
        result = self.run_closeout(github)
        self.assertEqual(result["verdict"], "ATTENTION")
        self.assertEqual(len(result["handoff"]["stale_claims"]), 1)

    def test_handoff_lint_detects_any_transient_task_claim(self) -> None:
        handoff = (
            "# Handoff\n\n## In progress\n\n"
            "- T-100 is pending merge.\n\n"
            "## Completed\n\n- PR for T-099 merged successfully.\n"
        )
        claims = post_merge_closeout.transient_handoff_claims(handoff)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["task_ids"], ["T-100"])

    def test_authoritative_main_must_mark_task_done(self) -> None:
        github = FakeGitHub(
            tasks=task_line(status="review", tracking=required_tracking())
        )
        result = self.run_closeout(github)
        self.assertEqual(result["verdict"], "ATTENTION")
        self.assertTrue(any("not 'done'" in item for item in result["findings"]))

    def test_multiple_merged_prs_are_ambiguous(self) -> None:
        github = FakeGitHub(
            tasks=task_line(tracking=required_tracking()),
            prs=[pull_request(number=101), pull_request(number=102)],
        )
        result = self.run_closeout(github)
        self.assertEqual(result["verdict"], "ATTENTION")
        self.assertEqual(result["pull_request_candidates"], 2)

    def test_closing_relationship_requires_closed_issue(self) -> None:
        github = FakeGitHub(
            tasks=task_line(tracking=required_tracking()), issue_state="OPEN"
        )
        result = self.run_closeout(github)
        self.assertEqual(result["verdict"], "ATTENTION")
        self.assertTrue(any("should be closed" in item for item in result["findings"]))

    def test_issue_free_task_does_not_query_issue(self) -> None:
        reason = "Bounded maintenance with complete PR context"
        tracking = {"mode": "not_required", "issues": [], "reason": reason}
        github = FakeGitHub(
            tasks=task_line(tracking=tracking),
            prs=[pull_request(issue_line=f"Not required — {reason}")],
        )
        result = self.run_closeout(github)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["issues"], [])
        self.assertFalse(any(command[1:3] == ["issue", "view"] for command in github.commands))

    def test_historical_done_task_has_defined_behavior(self) -> None:
        github = FakeGitHub(tasks=task_line())
        result = self.run_closeout(github)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["issues"], [])

    def test_dirty_worktree_is_preserved(self) -> None:
        github = FakeGitHub(tasks=task_line(tracking=required_tracking()))
        result = self.run_closeout(github, FakeGit(dirty=True))
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["cleanup"]["commands"], [])
        self.assertFalse(result["cleanup"]["worktrees"][0]["clean"])

    def test_unmanaged_worktree_is_never_suggested_for_removal(self) -> None:
        github = FakeGitHub(tasks=task_line(tracking=required_tracking()))

        def unmanaged(command: list[str]) -> str:
            if command[:3] == ["git", "branch", "--format=%(refname:short)"]:
                return "feat/T-100-example\n"
            if command[:4] == ["git", "worktree", "list", "--porcelain"]:
                return (
                    "worktree /repo/product-checkout\n"
                    "HEAD abc123\n"
                    "branch refs/heads/feat/T-100-example\n\n"
                )
            if command[:3] == ["git", "-C", "/repo/product-checkout"]:
                return ""
            self.fail(f"Unexpected command: {command}")

        result = self.run_closeout(github, unmanaged)
        self.assertEqual(result["cleanup"]["commands"], [])
        self.assertFalse(result["cleanup"]["worktrees"][0]["managed"])

    def test_github_commands_are_read_only(self) -> None:
        github = FakeGitHub(tasks=task_line(tracking=required_tracking()))
        self.run_closeout(github)
        used = {token for command in github.commands for token in command}
        self.assertTrue(post_merge_closeout.WRITE_WORDS.isdisjoint(used))

    def test_missing_github_cli_fails_safely(self) -> None:
        github = FakeGitHub(tasks=task_line(tracking=required_tracking()))
        with patch.object(post_merge_closeout.shutil, "which", return_value=None):
            with self.assertRaisesRegex(post_merge_closeout.CloseoutError, "required"):
                post_merge_closeout.closeout(
                    "T-100", github_runner=github, text_runner=FakeGit()
                )


if __name__ == "__main__":
    unittest.main()
