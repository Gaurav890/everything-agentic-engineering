#!/usr/bin/env python3
"""Plan and safely start task-ledger work without implementing it."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "docs/40-execution/TASKS.jsonl"
sys.path.insert(0, str(ROOT / "scripts"))

import profile_engine  # noqa: E402
import github_task_sync  # noqa: E402
import agent_broker  # noqa: E402

ACTIVE_STATUSES = {"in_progress", "review"}
STARTABLE_STATUSES = {"backlog", "ready", "blocked"}
SHARED_STATE_PREFIX = "docs/40-execution/"

AGENT_BY_OWNER = {
    "orchestrator": "orchestrator",
    "product": "product",
    "architect": "architect",
    "frontend": "frontend",
    "backend": "backend",
    "mobile": "mobile",
    "researcher": "researcher",
    "security": "security",
    "qa-evaluator": "qa-evaluator",
    "integration-reviewer": "integration-reviewer",
}


class TaskError(Exception):
    pass


def load_tasks(path: Path = TASKS_PATH) -> list[dict]:
    tasks: list[dict] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TaskError(f"Invalid JSON on line {number}: {exc}") from exc
        task_id = task.get("id")
        if not task_id:
            raise TaskError(f"Task on line {number} has no id")
        if task_id in seen:
            raise TaskError(f"Duplicate task id: {task_id}")
        seen.add(task_id)
        tasks.append(task)
    return tasks


def task_index(tasks: list[dict]) -> dict[str, dict]:
    return {task["id"]: task for task in tasks}


def get_task(tasks: list[dict], task_id: str) -> dict:
    try:
        return task_index(tasks)[task_id]
    except KeyError as exc:
        raise TaskError(f"Task not found: {task_id}") from exc


def required_profile_groups(task: dict) -> list[tuple[str, set[str]]]:
    owner = task.get("owner", "orchestrator")
    files = task.get("files_owned", [])
    verification = " ".join(task.get("verification", [])).lower()
    groups: list[tuple[str, set[str]]] = []

    def require(label: str, profiles: set[str]) -> None:
        if (label, profiles) not in groups:
            groups.append((label, profiles))

    if owner == "frontend" or any(path.startswith(("apps/web", "apps/showcase")) for path in files):
        require("web surface", {"web-next"})
    if owner == "mobile" or any(path.startswith("apps/mobile") for path in files):
        require("mobile surface", {"mobile-expo"})
    if owner == "researcher" or "research" in verification:
        require("current-web research", {"research-enabled"})
    if owner == "backend":
        require("backend", {"backend-supabase", "backend-convex"})
    if (
        any(path.startswith("docs/20-design") for path in files)
        or any(term in verification for term in ("visual", "design critic", "accessibility"))
    ):
        require("design-critical workflow", {"design-critical"})
    return groups


def static_prefix(pattern: str) -> str:
    prefix = re.split(r"[*?[]", pattern, maxsplit=1)[0]
    return prefix.rstrip("/")


def patterns_overlap(left: str, right: str) -> bool:
    if left.startswith(SHARED_STATE_PREFIX) or right.startswith(SHARED_STATE_PREFIX):
        return False
    left_prefix = static_prefix(left)
    right_prefix = static_prefix(right)
    if not left_prefix or not right_prefix:
        return False
    return (
        left_prefix.startswith(right_prefix)
        or right_prefix.startswith(left_prefix)
        or fnmatch.fnmatch(left_prefix, right)
        or fnmatch.fnmatch(right_prefix, left)
    )


def ownership_collisions(task: dict, tasks: list[dict]) -> list[dict]:
    collisions: list[dict] = []
    for other in tasks:
        if other["id"] == task["id"] or other.get("status") not in ACTIVE_STATUSES:
            continue
        overlaps = sorted(
            {
                f"{mine} ↔ {theirs}"
                for mine in task.get("files_owned", [])
                for theirs in other.get("files_owned", [])
                if patterns_overlap(mine, theirs)
            }
        )
        if overlaps:
            collisions.append({"task_id": other["id"], "overlaps": overlaps})
    return collisions


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:48].rstrip("-") or "task"


def build_plan(task_id: str, tasks: list[dict], active_profiles: list[str]) -> dict:
    task = get_task(tasks, task_id)
    index = task_index(tasks)
    blockers: list[str] = []
    warnings: list[str] = []

    try:
        github_task_sync.validate_ledger(tasks)
        github_tracking = github_task_sync.tracking_plan(task_id, tasks)
    except github_task_sync.TaskSyncError as exc:
        github_tracking = {"mode": "invalid", "issues": [], "reason": str(exc)}
        blockers.append(f"GitHub tracking contract: {exc}")

    dependency_states = []
    for dependency_id in task.get("depends_on", []):
        dependency = index.get(dependency_id)
        state = dependency.get("status") if dependency else "missing"
        dependency_states.append({"id": dependency_id, "status": state})
        if state != "done":
            blockers.append(f"Dependency {dependency_id} is {state}, not done")

    if task.get("status") not in STARTABLE_STATUSES:
        blockers.append(f"Task status {task.get('status')} is not startable")

    profile_groups = required_profile_groups(task)
    profile_checks = []
    active = set(active_profiles)
    for label, alternatives in profile_groups:
        satisfied = bool(active.intersection(alternatives))
        profile_checks.append(
            {
                "capability": label,
                "acceptable_profiles": sorted(alternatives),
                "satisfied": satisfied,
            }
        )
        if not satisfied:
            blockers.append(
                f"{label} requires one of: {', '.join(sorted(alternatives))}"
            )

    collisions = ownership_collisions(task, tasks)
    for collision in collisions:
        blockers.append(f"File ownership overlaps active {collision['task_id']}")

    other_active = [
        item["id"]
        for item in tasks
        if item["id"] != task_id and item.get("status") in ACTIVE_STATUSES
    ]
    mode = "worktree" if other_active else "branch"
    if other_active:
        warnings.append(
            "Other active tasks exist; use an isolated worktree after ownership checks pass"
        )

    try:
        specialist_manifest = agent_broker.load_manifest(ROOT)
        project = agent_broker.load_project(ROOT)
        specialist_recommendations = agent_broker.recommend_for_task(
            task,
            specialist_manifest,
            active_profiles,
            project.get("specialists", []),
        )
    except agent_broker.BrokerError as exc:
        specialist_recommendations = []
        blockers.append(f"Specialist routing contract: {exc}")

    slug = slugify(task.get("title", task_id))
    return {
        "task": task,
        "recommended_agent": AGENT_BY_OWNER.get(task.get("owner"), task.get("owner")),
        "specialist_recommendations": specialist_recommendations,
        "github_tracking": github_tracking,
        "dependency_states": dependency_states,
        "profile_checks": profile_checks,
        "active_profiles": active_profiles,
        "ownership_collisions": collisions,
        "other_active_tasks": other_active,
        "recommended_mode": mode,
        "suggested_slug": slug,
        "warnings": warnings,
        "blockers": blockers,
        "ready": not blockers,
    }


def print_plan(plan: dict) -> None:
    task = plan["task"]
    print(f"Task plan: {task['id']} — {task['title']}")
    print(f"Status: {task.get('status')}")
    print(f"Owner / recommended agent: {task.get('owner')} / {plan['recommended_agent']}")
    print(f"Risk: {task.get('risk', 'unspecified')}")
    print(f"Goal: {task.get('goal', '')}")
    print(f"Requirements: {', '.join(task.get('requirement_ids', [])) or 'none'}")
    print(f"Acceptance: {', '.join(task.get('acceptance_ids', [])) or 'none'}")

    print("\nGitHub tracking:")
    tracking = plan["github_tracking"]
    if tracking["mode"] == "required":
        for issue in tracking["issues"]:
            relationship = "Closes" if issue["may_close"] else "Relates to"
            print(f"  - {issue['ref']}: {relationship}")
            if issue["other_unfinished_tasks"]:
                print(
                    "    Other unfinished tasks: "
                    + ", ".join(issue["other_unfinished_tasks"])
                )
    elif tracking["mode"] == "not_required":
        print(f"  - Not required: {tracking['reason']}")
    elif tracking["mode"] == "historical":
        print("  - Historical completed task; no migration required")
    else:
        print(f"  - INVALID: {tracking['reason']}")

    print("\nDependencies:")
    if plan["dependency_states"]:
        for dependency in plan["dependency_states"]:
            print(f"  - {dependency['id']}: {dependency['status']}")
    else:
        print("  - none")

    print("\nProfile compatibility:")
    if plan["profile_checks"]:
        for check in plan["profile_checks"]:
            mark = "PASS" if check["satisfied"] else "BLOCK"
            profiles = ", ".join(check["acceptable_profiles"])
            print(f"  - {mark}: {check['capability']} ({profiles})")
    else:
        print("  - PASS: core harness only")

    print("\nExclusive file ownership:")
    for path in task.get("files_owned", []):
        print(f"  - {path}")
    if plan["ownership_collisions"]:
        print("  Collisions:")
        for collision in plan["ownership_collisions"]:
            print(f"  - {collision['task_id']}")
            for overlap in collision["overlaps"]:
                print(f"      {overlap}")

    print("\nVerification gates:")
    for gate in task.get("verification", []):
        print(f"  - {gate}")

    print("\nSpecialist capabilities:")
    if plan["specialist_recommendations"]:
        for specialist in plan["specialist_recommendations"]:
            mark = "REQUIRED" if specialist["required"] else "RECOMMENDED"
            print(f"  - {mark}: {specialist['name']} ({specialist['id']})")
            print(f"    reason: {'; '.join(specialist['reason'])}")
            print(f"    mode: {specialist['mode']}; authority: {specialist['authority']}")
            print(
                "    local role(s): "
                + ", ".join(specialist["local_roles"])
                + f"; evaluator: {specialist['evaluator']}"
            )
    else:
        print("  - none justified by current task evidence")

    print(f"\nRecommended execution: {plan['recommended_mode']}")
    print(f"Suggested slug: {plan['suggested_slug']}")
    for warning in plan["warnings"]:
        print(f"Warning: {warning}")

    if plan["blockers"]:
        print("\nBLOCKED:")
        for blocker in plan["blockers"]:
            print(f"  - {blocker}")
    else:
        print("\nREADY")
        print(
            "Start after review:\n"
            f"  ./agentic task start {task['id']} "
            f"--slug {plan['suggested_slug']} --mode {plan['recommended_mode']} --yes"
        )


def current_resolved_profiles() -> list[str]:
    return profile_engine.resolve(profile_engine.current_profiles())["resolved_profiles"]


def run_start(args: argparse.Namespace, plan: dict) -> int:
    print_plan(plan)
    if not plan["ready"]:
        return 1
    if not args.yes:
        print("\nNo changes made. Re-run with --yes after reviewing the plan.")
        return 2

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    if status.strip():
        raise TaskError("Working tree is not clean")

    mode = plan["recommended_mode"] if args.mode == "auto" else args.mode
    slug = args.slug or plan["suggested_slug"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise TaskError("Slug must use lowercase kebab-case")

    if mode == "branch":
        command = [
            str(ROOT / "scripts/new-branch.sh"),
            args.type,
            plan["task"]["id"],
            slug,
            args.base,
        ]
        subprocess.run(command, cwd=ROOT, check=True)
    else:
        subprocess.run(["git", "fetch", "origin", args.base], cwd=ROOT, check=True)
        local_base = subprocess.run(
            ["git", "rev-parse", args.base],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        remote_base = subprocess.run(
            ["git", "rev-parse", f"origin/{args.base}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        if local_base != remote_base:
            raise TaskError(
                f"Local {args.base} is not synchronized with origin/{args.base}"
            )
        command = [
            str(ROOT / "scripts/create-worktree.sh"),
            plan["task"]["id"],
            slug,
            args.type,
            args.base,
        ]
        subprocess.run(command, cwd=ROOT, check=True)
        worktree = ROOT / ".claude/worktrees" / f"{plan['task']['id'].lower()}-{slug}"
        subprocess.run(
            [str(worktree / "scripts/start-task.sh"), plan["task"]["id"]],
            cwd=worktree,
            check=True,
        )
    print("\nTask workspace prepared. Implementation has not started automatically.")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan")
    plan.add_argument("task_id")
    plan.add_argument("--json", action="store_true")
    start = subparsers.add_parser("start")
    start.add_argument("task_id")
    start.add_argument("--slug")
    start.add_argument("--mode", choices=("auto", "branch", "worktree"), default="auto")
    start.add_argument(
        "--type",
        choices=("feat", "fix", "docs", "refactor", "test", "chore", "spike", "security", "hotfix", "agent"),
        default="feat",
    )
    start.add_argument("--base", default="main")
    start.add_argument("--yes", action="store_true")
    return value


def main() -> int:
    try:
        args = parser().parse_args()
        tasks = load_tasks()
        plan = build_plan(args.task_id, tasks, current_resolved_profiles())
        if args.command == "plan":
            if args.json:
                print(json.dumps(plan, indent=2))
            else:
                print_plan(plan)
            return 0 if plan["ready"] else 1
        return run_start(args, plan)
    except (TaskError, profile_engine.ProfileError, subprocess.CalledProcessError) as exc:
        print(f"Task launcher error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
