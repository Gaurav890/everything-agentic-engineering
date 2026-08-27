#!/usr/bin/env python3
"""Return one project-appropriate next action without mutating the workspace."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import github_task_sync
from project_checks import ProjectCheckError, active_profiles, load_object, web_prerequisite

ROOT = Path(__file__).resolve().parents[1]


NextActionError = ProjectCheckError
STATUSES = {"backlog", "ready", "in_progress", "review", "done", "blocked", "needs_human", "failed_safe"}


def git_branch(root: Path) -> str | None:
    # A parent repository is not this generated project's version history.
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True, timeout=5)
        if top.returncode or Path(top.stdout.strip()).resolve() != root.resolve():
            return None
        checkpoint = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=root, capture_output=True, text=True, timeout=5)
        if checkpoint.returncode:
            return None
        branch = subprocess.run(["git", "symbolic-ref", "--short", "HEAD"], cwd=root, capture_output=True, text=True, timeout=5)
        return branch.stdout.strip() if branch.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def task_action(root: Path, task_id: str | None = None) -> tuple[str, str]:
    try:
        tasks = github_task_sync.load_tasks(root / "docs/40-execution/TASKS.jsonl")
        github_task_sync.validate_ledger(tasks)
    except (github_task_sync.TaskSyncError, AttributeError, TypeError, OSError) as error:
        raise NextActionError(f"Repair the task ledger before continuing: {error}") from error
    index = {task["id"]: task for task in tasks}
    for task in tasks:
        if not isinstance(task.get("status"), str) or task["status"] not in STATUSES:
            raise NextActionError(f"Invalid status for {task['id']}")
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list) or not all(isinstance(item, str) and item in index and item != task["id"] for item in dependencies):
            raise NextActionError(f"Invalid or missing dependency for {task['id']}")
    visiting, visited = set(), set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise NextActionError(f"Circular task dependency at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in index[task_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for identity in index:
        visit(identity)
    branch = git_branch(root)
    branch_match = re.fullmatch(r"[^/]+/(T-\d{3,})-[a-z0-9-]+", branch or "")
    if task_id is None and branch_match and branch_match[1] in index:
        task_id = branch_match[1]
    if task_id is not None and task_id not in index:
        raise NextActionError(f"Task not found: {task_id}")
    if task_id is None:
        candidates = [task for task in tasks if task["status"] in {"in_progress", "review"}]
        if not candidates:
            candidates = [task for task in tasks if task["status"] in {"ready", "backlog"} and all(index[item]["status"] == "done" for item in task.get("depends_on", []))]
        if not candidates:
            candidates = [task for task in tasks if task["status"] != "done"]
        if len(candidates) > 1:
            choices = ", ".join(task["id"] for task in candidates)
            return "Choose one workstream", f"Choose a task from {choices}, then run ./agentic next --task <TASK-ID>."
        if not candidates:
            return (
                "Plan your first useful feature" if not tasks else "Plan the next useful improvement",
                "Ask your coding assistant: Read docs/10-product/FIRST_FEATURE.md, help me choose one useful change, and prepare its requirement, acceptance criteria, and task plan. Do not implement until I accept the scope.",
            )
        task_id = candidates[0]["id"]
    task = index[task_id]
    status = task["status"]
    if status == "done":
        return f"Confirm the merged state of {task_id}", f"./agentic task closeout {task_id}"
    if status in {"blocked", "needs_human", "failed_safe"}:
        return f"Resolve the recorded blocker for {task_id}", f"Ask your coding assistant to explain {task_id}'s blocker and the smallest decision needed. Do not change permissions or task status just to bypass it."
    waiting = [item for item in task.get("depends_on", []) if index[item]["status"] != "done"]
    if waiting:
        return f"Resolve dependencies before {task_id}", f"./agentic next --task {waiting[0]}"
    if status == "review":
        return f"Review {task_id}'s result", f"Review the draft PR and its running-product, visual, and independent-review evidence. Request changes, or explicitly say '{task_id} approved' after review. Do not edit task status; approval does not authorize merge."
    if status == "in_progress":
        verification = "./agentic verify web" if "web-next" in active_profiles(root) else "./agentic verify full plus the task's applicable application checks"
        return f"Continue {task_id} in its task workspace", f"Ask your coding assistant to continue {task_id}, preserve the approved design, run {verification}, and collect applicable visual and independent-review evidence. Use ./agentic task finish {task_id} after verification and keep its PR draft for human review."
    if status == "backlog":
        return f"Review the scope of {task_id}", f"./agentic task plan {task_id}"
    if branch is None:
        return "Prepare version control for the accepted feature", "Ask your coding assistant to follow the version-control section of docs/60-tooling/FIRST_PROJECT.md. Review the source-only commit and remote decision before starting the task; do not include credentials."
    return f"Preview the isolated workspace for {task_id}", f"./agentic task start {task_id}"


def next_action(root: Path = ROOT, task_id: str | None = None) -> tuple[str, str]:
    generated_path = root / ".agentic/generated-project.json"
    if not generated_path.is_file():
        if task_id:
            return task_action(root, task_id)
        return "Create your first project", "./agentic setup create"

    profiles = active_profiles(root)
    if task_id and "web-next" not in profiles:
        return task_action(root, task_id)
    if "web-next" in profiles:
        prerequisite = web_prerequisite(root)
        if prerequisite:
            return prerequisite
        design_path = root / ".agentic/design.json"
        design = load_object(design_path)
        if not isinstance(design.get("status"), str) or design["status"] not in {"needs_approval", "approved"}:
            raise NextActionError("Invalid design status; run ./agentic design check")
        if design.get("status") != "approved":
            return (
                "Compare the live directions, then explicitly approve your choice",
                "pnpm dev",
            )
        direction_path = root / "packages/design-tokens/generated/direction.css"
        approved_direction = design.get("approved_direction")
        if not isinstance(approved_direction, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", approved_direction):
            raise NextActionError("Approved design needs a valid direction; run ./agentic design check")
        compiled = direction_path.read_text() if direction_path.is_file() else ""
        if (
            not isinstance(approved_direction, str)
            or not approved_direction
            or f"({approved_direction})" not in compiled
        ):
            return (
                "Compile the approved direction into the canonical token outputs",
                "./agentic tokens build",
            )
        return task_action(root, task_id)

    if "mobile-expo" in profiles:
        return (
            "Mobile is a planning scaffold, not a runnable native starter",
            "Open docs/60-tooling/FIRST_PROJECT.md and follow the mobile readiness path.",
        )
    return (
        "Define the product outcome before creating the first requirement",
        "Open docs/00-vision/NORTH_STAR.md",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", help="Select a workstream when several tasks are active")
    args = parser.parse_args()
    try:
        title, command = next_action(task_id=args.task)
    except (NextActionError, OSError) as error:
        print(f"Next-action error: {error}", file=sys.stderr)
        return 1
    print("NEXT")
    print(title)
    print(f"\n  {command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
