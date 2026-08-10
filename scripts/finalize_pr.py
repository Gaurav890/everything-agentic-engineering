#!/usr/bin/env python3
"""Finalize an approved PR without approving or merging it."""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

import github_task_sync


ROOT = Path(__file__).resolve().parents[1]
LEDGER = Path("docs/40-execution/TASKS.jsonl")
TASK_PATTERN = re.compile(r"T-[0-9]{3,}")
PR_FIELDS = "number,url,isDraft,state,headRefName,baseRefName,title,body"
Runner = Callable[[list[str]], str]
Sleeper = Callable[[float], None]
CHECK_REGISTRATION_ATTEMPTS = 12
CHECK_REGISTRATION_DELAY_SECONDS = 5.0


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


def parse_tasks(raw: str, source: str) -> list[dict]:
    tasks: list[dict] = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FinalizationError(
                f"Invalid task JSON in {source} at line {line_number}: {exc}"
            ) from exc
        if not isinstance(task, dict):
            raise FinalizationError(
                f"Invalid task record in {source} at line {line_number}"
            )
        tasks.append(task)
    return tasks


def is_exact_prepared_transition(
    task_id: str, root: Path, runner: Runner, status: str
) -> bool:
    lines = [line for line in status.splitlines() if line.strip()]
    if len(lines) != 1 or changed_paths(status) != {str(LEDGER)}:
        return False

    # Accept only the two interruption points created by this finalizer: the
    # ledger was written but not staged, or staged but not committed.
    if lines[0][:2] not in {" M", "M "}:
        return False

    raw_head = runner(["git", "show", f"HEAD:{LEDGER.as_posix()}"])
    head_tasks = parse_tasks(raw_head, f"HEAD:{LEDGER}")
    working_tasks = read_tasks(root)
    if len(head_tasks) != len(working_tasks):
        return False

    try:
        head_task = github_task_sync.get_task(head_tasks, task_id)
        working_task = github_task_sync.get_task(working_tasks, task_id)
    except github_task_sync.TaskSyncError:
        return False

    expected_task = copy.deepcopy(head_task)
    expected_task["status"] = "done"
    if head_task.get("status") != "review" or working_task != expected_task:
        return False

    expected_tasks = copy.deepcopy(head_tasks)
    for index, candidate in enumerate(expected_tasks):
        if candidate.get("id") == task_id:
            expected_tasks[index] = expected_task
            break
    return working_tasks == expected_tasks


def worktree_state(task_id: str, root: Path, runner: Runner) -> str:
    status = runner(["git", "status", "--porcelain=v1"])
    if not status.strip():
        return "clean"
    if is_exact_prepared_transition(task_id, root, runner, status):
        return "prepared_ledger"

    paths = ", ".join(sorted(changed_paths(status))) or "unknown"
    raise FinalizationError(
        "The worktree must be clean before PR finalization, except for an exact "
        f"interrupted {task_id} review-to-done ledger transition. Inspect or "
        f"restore these changes first: {paths}"
    )


def current_context(
    task_id: str, root: Path, runner: Runner
) -> tuple[dict, dict, str, str]:
    if not TASK_PATTERN.fullmatch(task_id):
        raise FinalizationError("Task ID must use the form T-###")

    branch = runner(["git", "branch", "--show-current"]).strip()
    if not branch:
        raise FinalizationError("PR finalization requires a named task branch")
    if branch in {"main", "master"}:
        raise FinalizationError(f"Refusing to finalize from protected branch: {branch}")

    runner(["bash", str(root / "scripts/check-branch-name.sh"), branch])
    recovery_state = worktree_state(task_id, root, runner)

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

    return task, pull_request, branch, recovery_state


def print_plan(
    task_id: str,
    task: dict,
    pull_request: dict,
    branch: str,
    recovery_state: str,
) -> None:
    if recovery_state == "prepared_ledger":
        action = "re-verify and commit the exact interrupted task-ledger transition"
    elif task.get("status") == "review":
        action = "verify and prepare the task ledger, commit it, and push the branch"
    else:
        action = "push the already prepared branch"
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


def commit_prepared_ledger(task_id: str, runner: Runner) -> None:
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


def wait_for_registered_checks(
    pull_request_number: int,
    runner: Runner,
    *,
    sleeper: Sleeper,
    attempts: int = CHECK_REGISTRATION_ATTEMPTS,
    delay_seconds: float = CHECK_REGISTRATION_DELAY_SECONDS,
) -> None:
    if attempts < 1:
        raise FinalizationError("Check-registration attempts must be positive")

    for attempt in range(1, attempts + 1):
        raw = runner(
            [
                "gh",
                "pr",
                "view",
                str(pull_request_number),
                "--json",
                "statusCheckRollup",
            ]
        )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FinalizationError(
                "GitHub returned invalid required-check JSON"
            ) from exc
        checks = payload.get("statusCheckRollup")
        if isinstance(checks, list) and checks:
            return
        if attempt < attempts:
            sleeper(delay_seconds)

    wait_seconds = max(0, attempts - 1) * delay_seconds
    raise FinalizationError(
        "GitHub did not register any pull-request checks within "
        f"{wait_seconds:g} seconds. The branch remains pushed and unmerged; "
        "rerun this finalizer safely after GitHub registers the checks."
    )


def finalize(
    task_id: str,
    *,
    root: Path = ROOT,
    runner: Runner = run_command,
    sleeper: Sleeper = time.sleep,
    dry_run: bool,
) -> dict:
    task, pull_request, branch, recovery_state = current_context(
        task_id, root, runner
    )
    print_plan(task_id, task, pull_request, branch, recovery_state)
    if dry_run:
        print("Dry run complete. No mutation was performed.")
        return {"dry_run": True, "task_id": task_id, "pull_request": pull_request}

    if recovery_state == "prepared_ledger":
        output = runner(["bash", str(root / "scripts/verify.sh"), "full"])
        if output:
            print(output)
        commit_prepared_ledger(task_id, runner)
    elif task.get("status") == "review":
        output = runner(["bash", str(root / "scripts/prepare-merge.sh"), task_id])
        if output:
            print(output)
        prepared = read_task(root, task_id)
        if prepared.get("status") != "done":
            raise FinalizationError(
                f"prepare-merge.sh did not write status=done for {task_id}"
            )
        commit_prepared_ledger(task_id, runner)

    runner(["git", "push", "origin", "HEAD"])
    if pull_request.get("isDraft"):
        runner(["gh", "pr", "ready", str(pull_request["number"])])
    wait_for_registered_checks(pull_request["number"], runner, sleeper=sleeper)
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
