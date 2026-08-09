#!/usr/bin/env python3
"""Finalize an approved PR without approving or merging it."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

import github_task_sync


ROOT = Path(__file__).resolve().parents[1]
LEDGER = Path("docs/40-execution/TASKS.jsonl")
TASK_PATTERN = re.compile(r"T-[0-9]{3,}")
PR_FIELDS = "number,url,isDraft,state,headRefName,baseRefName,title,body"
Runner = Callable[[list[str]], str]


class FinalizationError(RuntimeError):
    """Raised when PR finalization cannot continue safely."""


def run_command(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise FinalizationError(
            f"Command failed: {' '.join(command)}" + (f"\n{detail}" if detail else "")
        )
    # Preserve porcelain output exactly. Leading spaces encode Git's index and
    # worktree status columns; stripping them corrupts path parsing.
    return completed.stdout


def read_tasks(root: Path) -> list[dict]:
    return github_task_sync.load_tasks(root / LEDGER)


def read_task(root: Path, task_id: str) -> dict:
    return github_task_sync.get_task(read_tasks(root), task_id)


def changed_paths(status: str) -> set[str]:
    paths: set[str] = set()
    for line in status.splitlines():
        if not line.strip():
            continue
        value = line[3:] if len(line) > 3 else line
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        paths.add(value.strip().strip('"'))
    return paths


def require_clean(runner: Runner) -> None:
    status = runner(["git", "status", "--porcelain=v1"])
    if status.strip():
        paths = ", ".join(sorted(changed_paths(status)))
        raise FinalizationError(
            "The worktree must be clean before PR finalization. "
            f"Commit or restore the current changes first: {paths}"
        )


def current_context(task_id: str, root: Path, runner: Runner) -> tuple[dict, dict, str]:
    if not TASK_PATTERN.fullmatch(task_id):
        raise FinalizationError("Task ID must use the form T-###")

    branch = runner(["git", "branch", "--show-current"]).strip()
    if not branch:
        raise FinalizationError("PR finalization requires a named task branch")
    if branch in {"main", "master"}:
        raise FinalizationError(f"Refusing to finalize from protected branch: {branch}")

    runner(["bash", str(root / "scripts/check-branch-name.sh"), branch])
    require_clean(runner)

    task = read_task(root, task_id)
    if task.get("status") not in {"review", "done"}:
        raise FinalizationError(
            f"Task {task_id} is {task.get('status')!r}. Run finish-task.sh, commit "
            "the review-state update, and complete human review first."
        )

    runner(["gh", "auth", "status", "--hostname", "github.com"])
    raw_pr = runner(["gh", "pr", "view", "--json", PR_FIELDS])
    try:
        pull_request = json.loads(raw_pr)
    except json.JSONDecodeError as exc:
        raise FinalizationError("GitHub returned invalid pull-request JSON") from exc

    if pull_request.get("state") != "OPEN":
        raise FinalizationError("The current branch must have an open pull request")
    if pull_request.get("headRefName") != branch:
        raise FinalizationError(
            "The open pull request head does not match the current branch: "
            f"{pull_request.get('headRefName')!r} != {branch!r}"
        )
    if pull_request.get("baseRefName") not in {"main", "master"}:
        raise FinalizationError(
            "The pull request must target the protected integration branch"
        )

    github_task_sync.validate_pr(
        pull_request.get("title", ""),
        pull_request.get("body", ""),
        read_tasks(root),
        ready=False,
    )
    if f"({task_id})" not in pull_request.get("title", ""):
        raise FinalizationError(f"The pull-request title must reference {task_id}")

    return task, pull_request, branch


def print_plan(task_id: str, task: dict, pull_request: dict, branch: str) -> None:
    action = (
        "verify and prepare the task ledger, commit it, and push the branch"
        if task.get("status") == "review"
        else "push the already prepared branch"
    )
    ready_action = (
        "mark the draft pull request ready for review"
        if pull_request.get("isDraft")
        else "leave the already-ready pull request ready and retrigger checks by pushing"
    )
    print(f"PR finalization plan for {task_id}")
    print(f"  Branch: {branch}")
    print(f"  Pull request: {pull_request.get('url')}")
    print(f"  Task state: {task.get('status')}")
    print(f"  1. {action}.")
    print(f"  2. {ready_action}.")
    print("  3. Wait for required checks.")
    print("  4. Stop. A human performs the squash merge separately.")
    print("  This command never approves or merges the pull request.")


def finalize(task_id: str, *, root: Path = ROOT, runner: Runner = run_command, dry_run: bool) -> dict:
    task, pull_request, branch = current_context(task_id, root, runner)
    print_plan(task_id, task, pull_request, branch)
    if dry_run:
        print("Dry run complete. No mutation was performed.")
        return {"dry_run": True, "task_id": task_id, "pull_request": pull_request}

    if task.get("status") == "review":
        output = runner(["bash", str(root / "scripts/prepare-merge.sh"), task_id])
        if output:
            print(output)
        prepared = read_task(root, task_id)
        if prepared.get("status") != "done":
            raise FinalizationError(
                f"prepare-merge.sh did not write status=done for {task_id}"
            )
        status = runner(["git", "status", "--porcelain=v1"])
        paths = changed_paths(status)
        if paths != {str(LEDGER)}:
            found = ", ".join(sorted(paths)) or "none"
            raise FinalizationError(
                "Final verification changed files outside the task ledger; refusing to "
                f"stage or commit. Changed paths: {found}"
            )
        runner(["git", "add", "--", str(LEDGER)])
        staged = set(
            filter(
                None,
                runner(["git", "diff", "--cached", "--name-only"]).splitlines(),
            )
        )
        if staged != {str(LEDGER)}:
            found = ", ".join(sorted(staged)) or "none"
            raise FinalizationError(
                "Only the task ledger may be staged by PR finalization. "
                f"Staged paths: {found}"
            )
        runner(
            [
                "git",
                "commit",
                "-m",
                f"docs({task_id}): prepare task for merge",
            ]
        )

    runner(["git", "push", "origin", "HEAD"])
    if pull_request.get("isDraft"):
        runner(["gh", "pr", "ready", str(pull_request["number"])])
    runner(["gh", "pr", "checks", str(pull_request["number"]), "--watch", "--fail-fast"])

    print("Required checks passed. The PR is prepared for a human squash merge.")
    print("Do not edit TASKS.jsonl manually and do not run an automated merge.")
    return {"dry_run": False, "task_id": task_id, "pull_request": pull_request}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finalize an approved task PR without approving or merging it."
    )
    parser.add_argument("task_id", help="Task ID such as T-026")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show the plan without mutation.",
    )
    mode.add_argument(
        "--yes",
        action="store_true",
        help="Run the approved finalization plan.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        finalize(args.task_id.upper(), dry_run=args.dry_run)
    except (FinalizationError, github_task_sync.TaskSyncError) as exc:
        print(f"PR finalization stopped safely: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
