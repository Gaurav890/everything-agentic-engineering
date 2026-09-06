#!/usr/bin/env python3
"""Show the complete project journey and one exact next action without mutation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

import next_action
import project_brief
import github_task_sync


ROOT = Path(__file__).resolve().parents[1]
class JourneyError(ValueError):
    """Raised when project journey state cannot be trusted."""


def read_tasks(root: Path) -> list[dict[str, Any]]:
    path = root / "docs/40-execution/TASKS.jsonl"
    if path.is_symlink() or path.parent.is_symlink():
        raise JourneyError("Task state cannot follow symlinks")
    if not path.is_file():
        return []
    try:
        tasks = github_task_sync.load_tasks(path)
        github_task_sync.validate_ledger(tasks)
    except (OSError, github_task_sync.TaskSyncError, AttributeError, TypeError) as error:
        raise JourneyError(f"Cannot trust the task ledger: {error}") from error
    index = {task["id"]: task for task in tasks}
    for task in tasks:
        if task.get("status") not in next_action.STATUSES:
            raise JourneyError(f"Invalid status for {task['id']}")
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) and item in index and item != task["id"]
            for item in dependencies
        ):
            raise JourneyError(f"Invalid or missing dependency for {task['id']}")
        acceptance_ids = task.get("acceptance_ids", [])
        if not isinstance(acceptance_ids, list) or not all(
            isinstance(item, str) and item for item in acceptance_ids
        ):
            raise JourneyError(f"Invalid acceptance criteria for {task['id']}")
        requirement_ids = task.get("requirement_ids", [])
        if not isinstance(requirement_ids, list) or not all(
            isinstance(item, str) and item for item in requirement_ids
        ):
            raise JourneyError(f"Invalid requirements for {task['id']}")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise JourneyError(f"Circular task dependency at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in index[task_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in index:
        visit(task_id)
    return tasks


def research_status(root: Path, enabled: bool) -> tuple[str, str]:
    if not enabled:
        return "skipped", "Current-web research was not selected; enable it only if evidence would change the product."
    try:
        state = project_brief.load_research_state(root, selected=True)
    except project_brief.BriefError as error:
        raise JourneyError(str(error)) from error
    if state["status"] == "complete":
        return "complete", "Validated research state records a synthesized result; product decisions must still cite it."
    if state.get("migration_required"):
        return "active", "Research is selected; start the guided handoff to create and complete the structured research state."
    return "active", "Perplexity is preferred when configured; primary-source/manual research is the supported fallback."


def build(root: Path = ROOT, task_id: str | None = None) -> dict[str, Any]:
    generated = root / ".agentic/generated-project.json"
    brief_path = root / project_brief.BRIEF_PATH
    if not generated.is_file() or not brief_path.is_file():
        title, action = next_action.next_action(root, task_id)
        return {
            "schema_version": 1,
            "project": "New project",
            "promise": "Turn an idea into a distinctive, researched, working product slice with evidence.",
            "stages": [
                {"id": "research", "status": "decision", "detail": "Choose Perplexity-first current research or the no-research fast path during creation."},
                {"id": "product", "status": "waiting", "detail": "Capture the audience, promise, and first useful journey."},
                {"id": "design", "status": "waiting", "detail": "Compare live product-specific directions before token approval."},
                {"id": "build", "status": "waiting", "detail": "Implement one approved vertical slice."},
                {"id": "verify", "status": "waiting", "detail": "Test the running behavior and collect evidence."},
                {"id": "review", "status": "waiting", "detail": "Use an evaluator separate from the builder, then obtain human review."},
            ],
            "next": {"title": title, "action": action},
            "mutation_performed": False,
        }

    try:
        brief = project_brief.load(root)
        profiles = set(next_action.active_profiles(root))
    except (project_brief.BriefError, next_action.NextActionError) as error:
        raise JourneyError(str(error)) from error

    research_enabled = project_brief.research_selected(profiles)
    research_state, research_detail = research_status(root, research_enabled)
    research_complete = research_state in {"complete", "skipped"}
    product_complete = brief["status"] == "ready"

    design_state = "skipped"
    design_detail = "This project does not include the design-critical profile."
    if "design-critical" in profiles:
        design_path = root / ".agentic/design.json"
        if design_path.is_symlink() or design_path.parent.is_symlink():
            raise JourneyError("Design state cannot follow symlinks")
        try:
            design = json.loads(design_path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise JourneyError(f"Cannot read design state: {error}") from error
        if not isinstance(design, dict) or design.get("status") not in {"needs_approval", "approved"}:
            raise JourneyError("Design state is invalid")
        if design["status"] == "approved" and product_complete and research_complete:
            design_state = "complete"
            design_detail = "A reviewed direction is approved; compile and preserve its canonical tokens."
        elif design["status"] == "approved":
            design_state = "waiting"
            design_detail = "Finish research and confirm the product journey, then re-check whether the approved direction remains valid."
        elif product_complete and research_complete:
            design_state = "active"
            design_detail = "Build and compare live product-specific directions; palette-only variation is insufficient."
        else:
            design_state = "waiting"
            design_detail = "Confirm the first useful journey before design approval."

    tasks = read_tasks(root)
    slice_tasks = [
        task for task in tasks
        if "FR-001" in task.get("requirement_ids", [])
        and "AC-001" in task.get("acceptance_ids", [])
    ]
    statuses = {task["status"] for task in slice_tasks}
    if statuses.intersection({"in_progress"}):
        build_state, build_detail = "active", "The AC-001 vertical-slice task is in progress."
    elif statuses.intersection({"review", "done"}):
        build_state, build_detail = "complete", "The AC-001 vertical slice is implemented; its evidence and merge state remain separate."
    else:
        build_state, build_detail = "waiting", "Create one AC-001-traced task only after product and design scope are accepted."

    if "review" in statuses:
        verify_state, review_state = "complete", "active"
    elif "done" in statuses:
        verify_state = "complete"
        branch = next_action.git_branch(root)
        review_state = "complete" if branch in {"main", "master"} else "ready_for_human"
    else:
        verify_state, review_state = "waiting", "waiting"

    try:
        title, action = next_action.next_action(root, task_id)
    except next_action.NextActionError as error:
        raise JourneyError(str(error)) from error

    return {
        "schema_version": 1,
        "project": brief["name"],
        "promise": brief["promise"],
        "stages": [
            {"id": "research", "status": research_state, "detail": research_detail},
            {"id": "product", "status": "complete" if product_complete and research_complete else "active" if research_complete else "waiting", "detail": "Finish selected research before product scope is treated as active." if not research_complete else "The audience, promise, first journey, and recovery states need direct product-owner confirmation." if not product_complete else "The brief records a confirmed first useful outcome."},
            {"id": "design", "status": design_state, "detail": design_detail},
            {"id": "build", "status": build_state, "detail": build_detail},
            {"id": "verify", "status": verify_state, "detail": "Run behavior, accessibility, responsive, and applicable visual checks against the implemented slice."},
            {"id": "review", "status": review_state, "detail": "Builder and evaluator stay separate; human approval and merge remain distinct."},
        ],
        "next": {"title": title, "action": action},
        "mutation_performed": False,
    }


def render(result: dict[str, Any]) -> str:
    lines = [f"PROJECT JOURNEY — {result['project']}", result["promise"], ""]
    for index, stage in enumerate(result["stages"], start=1):
        lines.append(f"{index}. [{stage['status'].upper()}] {stage['id'].upper()}")
        lines.append(f"   {stage['detail']}")
    lines.extend(["", "NEXT", result["next"]["title"], f"  {result['next']['action']}"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", help="Select a task when several workstreams exist")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = build(task_id=args.task)
    except (JourneyError, OSError) as error:
        print(f"Project journey error: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
