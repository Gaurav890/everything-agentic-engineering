from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/github-task-sync"
sys.path.insert(0, str(ROOT / "scripts"))

import github_task_sync


def task(
    task_id: str,
    *,
    status: str = "ready",
    issues: list[str] | None = None,
    reason: str | None = None,
) -> dict:
    value = {
        "id": task_id,
        "title": f"Test {task_id}",
        "status": status,
    }
    if issues is not None:
        value["tracking"] = {"mode": "required", "issues": issues}
    elif reason is not None:
        value["tracking"] = {
            "mode": "not_required",
            "issues": [],
            "reason": reason,
        }
    return value


def body(task_id: str, issue: str) -> str:
    return f"## Linked work\n\n- Issue: {issue}\n- Task: {task_id}\n"


class GitHubTaskSyncTests(unittest.TestCase):
    def test_reviewed_fixtures_encode_intermediate_final_and_issue_free_work(self) -> None:
        tasks = github_task_sync.load_tasks(FIXTURES / "tasks.jsonl")
        github_task_sync.validate_ledger(tasks)
        intermediate = github_task_sync.validate_pr(
            "feat(T-910): add intermediate slice",
            (FIXTURES / "intermediate-pr.md").read_text(),
            tasks,
            ready=True,
        )
        self.assertEqual(intermediate["contract"]["relations"][0]["verb"], "relates")

        tasks[1]["status"] = "done"
        final = github_task_sync.validate_pr(
            "feat(T-911): finish issue outcome",
            (FIXTURES / "final-pr.md").read_text(),
            tasks,
            ready=True,
        )
        self.assertEqual(final["contract"]["relations"][0]["verb"], "closes")

        issue_free = github_task_sync.validate_pr(
            "docs(T-912): maintain fixture",
            (FIXTURES / "issue-free-pr.md").read_text(),
            tasks,
            ready=True,
        )
        self.assertEqual(issue_free["tracking"]["mode"], "not_required")

    def test_completed_historical_task_may_omit_tracking(self) -> None:
        tasks = [task("T-100", status="done")]
        github_task_sync.validate_ledger(tasks)
        plan = github_task_sync.tracking_plan("T-100", tasks)
        self.assertEqual(plan["mode"], "historical")

    def test_unfinished_task_requires_tracking_contract(self) -> None:
        with self.assertRaisesRegex(
            github_task_sync.TaskSyncError, "must define tracking"
        ):
            github_task_sync.validate_ledger([task("T-100")])

    def test_issue_free_task_requires_a_reason(self) -> None:
        value = task("T-100", reason="Tiny documentation-only correction")
        github_task_sync.validate_ledger([value])
        value["tracking"]["reason"] = ""
        with self.assertRaisesRegex(github_task_sync.TaskSyncError, "non-empty reason"):
            github_task_sync.validate_ledger([value])

    def test_ready_pr_requires_done_task(self) -> None:
        tasks = [task("T-100", status="review", issues=["#26"])]
        with self.assertRaisesRegex(github_task_sync.TaskSyncError, "not 'done'"):
            github_task_sync.validate_pr(
                "feat(T-100): add sync",
                body("T-100", "Closes #26"),
                tasks,
                ready=True,
            )

    def test_title_and_body_task_ids_must_match(self) -> None:
        tasks = [task("T-100", status="done", issues=["#26"])]
        with self.assertRaisesRegex(github_task_sync.TaskSyncError, "body references"):
            github_task_sync.validate_pr(
                "feat(T-100): add sync",
                body("T-101", "Closes #26"),
                tasks,
                ready=True,
            )

    def test_required_issue_refs_must_match_exactly(self) -> None:
        tasks = [task("T-100", status="done", issues=["#26", "org/repo#8"])]
        with self.assertRaisesRegex(github_task_sync.TaskSyncError, "do not match"):
            github_task_sync.validate_pr(
                "feat(T-100): add sync",
                body("T-100", "Closes #26"),
                tasks,
                ready=True,
            )
        result = github_task_sync.validate_pr(
            "feat(T-100): add sync",
            body("T-100", "Closes #26, Closes org/repo#8"),
            tasks,
            ready=True,
        )
        self.assertEqual(len(result["contract"]["relations"]), 2)

    def test_intermediate_task_cannot_close_shared_issue(self) -> None:
        tasks = [
            task("T-100", status="done", issues=["#26"]),
            task("T-101", status="ready", issues=["#26"]),
        ]
        with self.assertRaisesRegex(github_task_sync.TaskSyncError, "T-101"):
            github_task_sync.validate_pr(
                "feat(T-100): add sync",
                body("T-100", "Closes #26"),
                tasks,
                ready=True,
            )
        result = github_task_sync.validate_pr(
            "feat(T-100): add sync",
            body("T-100", "Relates to #26"),
            tasks,
            ready=True,
        )
        self.assertEqual(result["contract"]["relations"][0]["verb"], "relates")

    def test_final_task_may_close_shared_issue(self) -> None:
        tasks = [
            task("T-100", status="done", issues=["#26"]),
            task("T-101", status="done", issues=["#26"]),
        ]
        result = github_task_sync.validate_pr(
            "feat(T-101): finish sync",
            body("T-101", "Closes #26"),
            tasks,
            ready=True,
        )
        self.assertEqual(result["task_id"], "T-101")

    def test_issue_free_pr_reason_must_match_ledger(self) -> None:
        tasks = [
            task(
                "T-100",
                status="done",
                reason="Bounded documentation-only cleanup",
            )
        ]
        result = github_task_sync.validate_pr(
            "docs(T-100): clean up docs",
            body("T-100", "Not required — Bounded documentation-only cleanup"),
            tasks,
            ready=True,
        )
        self.assertEqual(result["tracking"]["mode"], "not_required")
        with self.assertRaisesRegex(github_task_sync.TaskSyncError, "does not match"):
            github_task_sync.validate_pr(
                "docs(T-100): clean up docs",
                body("T-100", "Not required — Different reason"),
                tasks,
                ready=True,
            )

    def test_live_status_uses_read_only_gh_commands(self) -> None:
        tasks = [task("T-100", status="done", issues=["#26"])]
        commands: list[list[str]] = []

        def runner(command: list[str]):
            commands.append(command)
            if command[1:3] == ["repo", "view"]:
                return {"nameWithOwner": "owner/repository"}
            if command[1:3] == ["issue", "view"]:
                return {
                    "number": 26,
                    "title": "Tracked issue",
                    "state": "CLOSED",
                    "url": "https://example.test/issues/26",
                }
            if command[1:3] == ["pr", "list"]:
                return [
                    {
                        "number": 27,
                        "title": "feat(T-100): add sync",
                        "state": "MERGED",
                        "isDraft": False,
                        "url": "https://example.test/pull/27",
                        "mergedAt": "2026-08-07T00:00:00Z",
                        "headRefName": "feat/T-100-sync",
                        "baseRefName": "main",
                    }
                ]
            self.fail(f"Unexpected command: {command}")

        with patch.object(github_task_sync.shutil, "which", return_value="/usr/bin/gh"):
            status = github_task_sync.live_status("T-100", tasks, runner=runner)
        self.assertTrue(status["read_only"])
        self.assertEqual(status["drift"], [])
        self.assertTrue(all(command[0] == "gh" for command in commands))
        self.assertFalse(
            any(
                token in {"create", "edit", "close", "merge", "comment", "delete"}
                for command in commands
                for token in command
            )
        )

    def test_done_task_with_open_pr_is_expected_pre_merge_state(self) -> None:
        tasks = [task("T-100", status="done", issues=["#26"])]

        def runner(command: list[str]):
            if command[1:3] == ["repo", "view"]:
                return {"nameWithOwner": "owner/repository"}
            if command[1:3] == ["issue", "view"]:
                return {
                    "number": 26,
                    "title": "Tracked issue",
                    "state": "OPEN",
                    "url": "https://example.test/issues/26",
                }
            if command[1:3] == ["pr", "list"]:
                return [
                    {
                        "number": 27,
                        "title": "feat(T-100): add sync",
                        "state": "OPEN",
                        "isDraft": False,
                        "url": "https://example.test/pull/27",
                        "mergedAt": None,
                        "headRefName": "feat/T-100-sync",
                        "baseRefName": "main",
                    }
                ]
            self.fail(f"Unexpected command: {command}")

        with patch.object(github_task_sync.shutil, "which", return_value="/usr/bin/gh"):
            status = github_task_sync.live_status("T-100", tasks, runner=runner)
        self.assertEqual(status["drift"], [])


if __name__ == "__main__":
    unittest.main()
