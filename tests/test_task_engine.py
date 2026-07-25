from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import task_engine


def task(
    task_id: str,
    *,
    owner: str = "orchestrator",
    status: str = "ready",
    depends_on: list[str] | None = None,
    files: list[str] | None = None,
    verification: list[str] | None = None,
) -> dict:
    return {
        "id": task_id,
        "title": f"Add capability {task_id}",
        "goal": "Test task planning",
        "requirement_ids": ["FR-001"],
        "acceptance_ids": ["AC-001"],
        "owner": owner,
        "depends_on": depends_on or [],
        "status": status,
        "files_owned": files or ["scripts/example.py"],
        "verification": verification or ["unit tests"],
        "risk": "low",
    }


class TaskEngineTests(unittest.TestCase):
    def test_ready_core_task_recommends_branch(self) -> None:
        tasks = [task("T-100")]
        plan = task_engine.build_plan("T-100", tasks, ["core"])
        self.assertTrue(plan["ready"])
        self.assertEqual(plan["recommended_mode"], "branch")

    def test_incomplete_dependency_blocks_start(self) -> None:
        tasks = [
            task("T-100", status="in_progress"),
            task("T-101", depends_on=["T-100"]),
        ]
        plan = task_engine.build_plan("T-101", tasks, ["core"])
        self.assertFalse(plan["ready"])
        self.assertIn("Dependency T-100 is in_progress", plan["blockers"][0])

    def test_frontend_task_requires_web_profile(self) -> None:
        tasks = [task("T-100", owner="frontend", files=["apps/web/**"])]
        blocked = task_engine.build_plan("T-100", tasks, ["core"])
        ready = task_engine.build_plan("T-100", tasks, ["core", "web-next"])
        self.assertFalse(blocked["ready"])
        self.assertTrue(ready["ready"])

    def test_backend_accepts_either_backend_profile(self) -> None:
        tasks = [task("T-100", owner="backend", files=["packages/api/**"])]
        supabase = task_engine.build_plan(
            "T-100", tasks, ["core", "backend-supabase"]
        )
        convex = task_engine.build_plan("T-100", tasks, ["core", "backend-convex"])
        self.assertTrue(supabase["ready"])
        self.assertTrue(convex["ready"])

    def test_active_independent_task_recommends_worktree(self) -> None:
        tasks = [
            task("T-100", status="in_progress", files=["apps/web/**"]),
            task("T-101", files=["packages/api/**"]),
        ]
        plan = task_engine.build_plan("T-101", tasks, ["core"])
        self.assertTrue(plan["ready"])
        self.assertEqual(plan["recommended_mode"], "worktree")

    def test_overlapping_ownership_blocks_parallel_start(self) -> None:
        tasks = [
            task("T-100", status="in_progress", files=["packages/api/**"]),
            task("T-101", files=["packages/api/auth/**"]),
        ]
        plan = task_engine.build_plan("T-101", tasks, ["core"])
        self.assertFalse(plan["ready"])
        self.assertEqual(plan["ownership_collisions"][0]["task_id"], "T-100")

    def test_shared_execution_ledgers_do_not_create_false_collision(self) -> None:
        tasks = [
            task(
                "T-100",
                status="in_progress",
                files=["docs/40-execution/TASKS.jsonl"],
            ),
            task("T-101", files=["docs/40-execution/HANDOFF.md"]),
        ]
        plan = task_engine.build_plan("T-101", tasks, ["core"])
        self.assertTrue(plan["ready"])

    def test_design_evidence_requires_design_profile(self) -> None:
        tasks = [
            task(
                "T-100",
                owner="frontend",
                files=["apps/web/**"],
                verification=["visual QA"],
            )
        ]
        plan = task_engine.build_plan("T-100", tasks, ["core", "web-next"])
        self.assertFalse(plan["ready"])
        self.assertTrue(
            any("design-critical" in blocker for blocker in plan["blockers"])
        )

    def test_start_without_confirmation_is_read_only(self) -> None:
        tasks = [task("T-100")]
        plan = task_engine.build_plan("T-100", tasks, ["core"])
        args = SimpleNamespace(
            yes=False,
            mode="auto",
            slug=None,
            type="feat",
            base="main",
        )
        with redirect_stdout(StringIO()):
            result = task_engine.run_start(args, plan)
        self.assertEqual(result, 2)
        self.assertEqual(tasks[0]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
