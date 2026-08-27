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
import next_action


class NextActionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write(".agentic/generated-project.json", {"resolved_profiles": ["obsolete"]})
        self.write(".agentic/project.json", {"profiles": ["web-next"]})
        for name in ("core", "web-next", "mobile-expo"):
            self.write(f".agentic/profiles/{name}.json", {"id": name})
        self.write(".agentic/design.json", {"status": "needs_approval"})
        self.ledger()
        self.prerequisite = mock.patch.object(next_action, "web_prerequisite", return_value=None).start()
        self.real_git_branch = next_action.git_branch
        self.branch = mock.patch.object(next_action, "git_branch", return_value="main").start()
        self.addCleanup(mock.patch.stopall)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def ledger(self, *tasks):
        path = self.root / "docs/40-execution/TASKS.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(task) + "\n" for task in tasks))

    def task(self, identity="T-101", status="ready", dependencies=None):
        return {"id": identity, "status": status, "depends_on": dependencies or [],
                "tracking": {"mode": "not_required", "issues": [], "reason": "Reviewed local pilot."}}

    def approve(self):
        self.write(".agentic/design.json", {"status": "approved", "approved_direction": "editorial-signal"})
        path = self.root / "packages/design-tokens/generated/direction.css"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("/* Approved direction: Editorial Signal (editorial-signal). */\n")

    def test_source_checkout_routes_to_create(self):
        (self.root / ".agentic/generated-project.json").unlink()
        self.assertEqual("./agentic setup create", next_action.next_action(self.root)[1])

    def test_guidance_continues_past_tokens_into_feature_planning(self):
        self.prerequisite.return_value = ("Install", "pnpm install --frozen-lockfile")
        self.assertEqual("pnpm install --frozen-lockfile", next_action.next_action(self.root)[1])
        self.prerequisite.return_value = None
        self.assertEqual("pnpm dev", next_action.next_action(self.root)[1])
        self.write(".agentic/design.json", {"status": "approved", "approved_direction": "editorial-signal"})
        self.assertEqual("./agentic tokens build", next_action.next_action(self.root)[1])
        self.approve()
        title, action = next_action.next_action(self.root)
        self.assertIn("first useful feature", title)
        self.assertIn("FIRST_FEATURE.md", action)
        self.assertIn("Do not implement until", action)

    def test_current_profile_overrides_creation_history(self):
        self.write(".agentic/project.json", {"profiles": ["core"]})
        self.assertEqual("Open docs/00-vision/NORTH_STAR.md", next_action.next_action(self.root)[1])
        self.prerequisite.assert_not_called()

    def test_mobile_is_honest_and_never_routes_web(self):
        self.write(".agentic/project.json", {"profiles": ["mobile-expo"]})
        self.assertIn("not a runnable", next_action.next_action(self.root)[0])
        self.prerequisite.assert_not_called()

    def test_malformed_unknown_and_conflicting_profiles_fail_closed(self):
        for profiles in (None, "web-next", [], [7], ["unknown"]):
            self.write(".agentic/project.json", {"profiles": profiles})
            with self.assertRaises(next_action.NextActionError):
                next_action.next_action(self.root)
        self.write(".agentic/profiles/web-next.json", {"id": "web-next", "conflicts": ["mobile-expo"]})
        self.write(".agentic/project.json", {"profiles": ["web-next", "mobile-expo"]})
        with self.assertRaisesRegex(next_action.NextActionError, "Conflicting"):
            next_action.next_action(self.root)

    def test_task_lifecycle_has_distinct_actions_and_never_mutates(self):
        self.approve()
        expected = {"backlog": "task plan T-101", "ready": "task start T-101",
                    "in_progress": "verify web", "review": "approval does not authorize merge",
                    "blocked": "smallest decision", "needs_human": "smallest decision",
                    "failed_safe": "smallest decision", "done": "task closeout T-101"}
        for status, fragment in expected.items():
            with self.subTest(status=status):
                self.ledger(self.task(status=status))
                before = (self.root / "docs/40-execution/TASKS.jsonl").read_bytes()
                action = next_action.next_action(self.root, "T-101")[1]
                self.assertIn(fragment, action)
                self.assertNotIn("--yes", action)
                self.assertEqual(before, (self.root / "docs/40-execution/TASKS.jsonl").read_bytes())

    def test_dependencies_route_before_successor(self):
        self.approve()
        self.ledger(self.task("T-101", "review"), self.task("T-102", dependencies=["T-101"]))
        self.assertEqual("./agentic next --task T-101", next_action.next_action(self.root, "T-102")[1])

    def test_parallel_selection_and_branch_ownership(self):
        self.approve()
        self.ledger(self.task("T-101", "in_progress"), self.task("T-102", "review"))
        self.assertIn("--task <TASK-ID>", next_action.next_action(self.root)[1])
        self.branch.return_value = "feat/T-102-something"
        self.assertEqual("Review T-102's result", next_action.next_action(self.root)[0])

    def test_finished_main_routes_to_next_feature_but_branch_to_closeout(self):
        self.approve()
        self.ledger(self.task(status="done"))
        self.assertIn("next useful improvement", next_action.next_action(self.root)[0])
        self.branch.return_value = "feat/T-101-first-feature"
        self.assertIn("task closeout T-101", next_action.next_action(self.root)[1])

    def test_no_git_routes_to_source_only_checkpoint(self):
        self.approve()
        self.ledger(self.task())
        self.branch.return_value = None
        self.assertIn("source-only commit", next_action.next_action(self.root)[1])

    def test_git_detection_rejects_parent_detached_and_unborn_repositories(self):
        with mock.patch.object(next_action.subprocess, "run") as run:
            result = lambda code, value="": subprocess.CompletedProcess([], code, value, "")
            for responses in (
                [result(0, str(self.root.parent))],
                [result(0, str(self.root)), result(1)],
                [result(0, str(self.root)), result(0), result(1)],
                [result(1)],
            ):
                run.side_effect = responses
                self.assertIsNone(self.real_git_branch(self.root))
            run.side_effect = [result(0, str(self.root)), result(0), result(0, "main\n")]
            self.assertEqual("main", self.real_git_branch(self.root))

    def test_source_explicit_task_does_not_force_web_verification(self):
        (self.root / ".agentic/generated-project.json").unlink()
        self.write(".agentic/project.json", {"profiles": ["core"]})
        self.ledger(self.task(status="in_progress"))
        action = next_action.next_action(self.root, "T-101")[1]
        self.assertIn("verify full", action)
        self.assertNotIn("verify web", action)

    def test_explicit_task_survives_a_change_to_core_or_mobile(self):
        self.ledger(self.task(status="review"))
        for profile in ("core", "mobile-expo"):
            self.write(".agentic/project.json", {"profiles": [profile]})
            self.assertIn("T-101 approved", next_action.next_action(self.root, "T-101")[1])
        self.prerequisite.assert_not_called()

    def test_cli_reports_malformed_state_without_traceback(self):
        actual_next = next_action.next_action
        malformed = self.task()
        malformed["tracking"]["mode"] = []
        for kind in ("design", "tracking"):
            self.approve()
            self.ledger()
            if kind == "design":
                self.write(".agentic/design.json", {"status": []})
            else:
                self.ledger(malformed)
            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", ["next-action"]), mock.patch.object(next_action, "next_action", side_effect=lambda task_id: actual_next(self.root, task_id)), contextlib.redirect_stderr(stderr):
                self.assertEqual(1, next_action.main())
            self.assertIn("Next-action error:", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_invalid_tasks_cannot_become_commands(self):
        self.approve()
        for tasks in ([{"id": "T-101; echo bad"}], [self.task(status=[])],
                      [self.task(dependencies=["T-999"])], [self.task(), self.task()], [7],
                      [self.task("T-101", dependencies=["T-102"]), self.task("T-102", dependencies=["T-101"])]):
            self.ledger(*tasks)
            with self.assertRaises(next_action.NextActionError):
                next_action.next_action(self.root)

    def test_unknown_task_and_invalid_design_fail_closed(self):
        self.approve()
        with self.assertRaisesRegex(next_action.NextActionError, "Task not found"):
            next_action.next_action(self.root, "T-999")
        self.write(".agentic/design.json", {"status": "approved", "approved_direction": "../bad"})
        with self.assertRaises(next_action.NextActionError):
            next_action.next_action(self.root)
        self.write(".agentic/design.json", {"status": []})
        with self.assertRaisesRegex(next_action.NextActionError, "Invalid design status"):
            next_action.next_action(self.root)
        self.approve()
        malformed = self.task()
        malformed["tracking"]["mode"] = []
        self.ledger(malformed)
        with self.assertRaisesRegex(next_action.NextActionError, "Repair the task ledger"):
            next_action.next_action(self.root)


if __name__ == "__main__":
    unittest.main()
