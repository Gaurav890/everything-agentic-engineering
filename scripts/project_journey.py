#!/usr/bin/env python3
"""Show the complete project journey and one exact next action without mutation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

import next_action
import project_brief


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_PATH = Path("docs/10-product/RESEARCH.md")


class JourneyError(ValueError):
    """Raised when project journey state cannot be trusted."""


def read_tasks(root: Path) -> list[dict[str, Any]]:
    path = root / "docs/40-execution/TASKS.jsonl"
    if path.is_symlink() or path.parent.is_symlink():
        raise JourneyError("Task state cannot follow symlinks")
    if not path.is_file():
        return []
    tasks: list[dict[str, Any]] = []
    try:
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            task = json.loads(line)
            if not isinstance(task, dict) or not isinstance(task.get("status"), str):
                raise JourneyError("Task ledger contains an invalid record")
            tasks.append(task)
    except (OSError, json.JSONDecodeError) as error:
        raise JourneyError(f"Cannot read the task ledger: {error}") from error
    return tasks


def research_status(root: Path, enabled: bool) -> tuple[str, str]:
    if not enabled:
        return "skipped", "Current-web research was not selected; enable it only if evidence would change the product."
    path = root / RESEARCH_PATH
    if path.is_symlink() or path.parent.is_symlink():
        raise JourneyError("Research state cannot follow symlinks")
    if not path.is_file():
        return "selected", "Perplexity-first research is selected; create the source ledger before relying on research claims."
    try:
        content = path.read_text()
    except OSError as error:
        raise JourneyError(f"Cannot read research state: {error}") from error
    complete = re.search(r"(?mi)^Status:\s*Complete\s*$", content) is not None
    if complete:
        return "complete", "The research ledger declares a synthesized result; product decisions must still cite it."
    return "selected", "Perplexity is preferred when configured; primary-source/manual research is the supported fallback."


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

    research_enabled = bool(brief.get("research_enabled", False) or "research-enabled" in profiles)
    research_state, research_detail = research_status(root, research_enabled)
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
        if design["status"] == "approved":
            design_state = "complete"
            design_detail = "A reviewed direction is approved; compile and preserve its canonical tokens."
        elif product_complete:
            design_state = "active"
            design_detail = "Build and compare live product-specific directions; palette-only variation is insufficient."
        else:
            design_state = "waiting"
            design_detail = "Confirm the first useful journey before design approval."

    tasks = read_tasks(root)
    statuses = {task["status"] for task in tasks}
    if "done" in statuses:
        build_state, build_detail = "complete", "At least one bounded task is recorded done; inspect its evidence before trusting the claim."
    elif statuses.intersection({"in_progress", "review"}):
        build_state, build_detail = "active", "A bounded implementation task is active or under review."
    else:
        build_state, build_detail = "waiting", "Create one traced task only after product and design scope are accepted."

    if "review" in statuses:
        verify_state, review_state = "active", "active"
    elif "done" in statuses:
        verify_state, review_state = "complete", "complete"
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
            {"id": "product", "status": "complete" if product_complete else "active", "detail": "The audience, promise, first journey, and recovery states need direct product-owner confirmation." if not product_complete else "The brief records a confirmed first useful outcome."},
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
