#!/usr/bin/env python3
"""Validate and inspect GitHub Issue ↔ task relationships without mutation."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_PATH = ROOT / "docs/40-execution/TASKS.jsonl"
TASK_ID_PATTERN = re.compile(r"T-[0-9]{3,}")
TITLE_TASK_PATTERN = re.compile(r"\((T-[0-9]{3,})\)")
LOCAL_ISSUE_PATTERN = re.compile(r"#([1-9][0-9]*)")
CROSS_REPO_ISSUE_PATTERN = re.compile(
    r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)#([1-9][0-9]*)"
)
TASK_LINE_PATTERN = re.compile(
    r"^\s*-?\s*Task:\s*(T-[0-9]{3,})\s*$", re.IGNORECASE | re.MULTILINE
)
ISSUE_LINE_PATTERN = re.compile(
    r"^\s*-?\s*Issue:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE
)
RELATION_PATTERN = re.compile(
    r"^(Relates\s+to|Closes)\s+(.+)$", re.IGNORECASE
)
NOT_REQUIRED_PATTERN = re.compile(
    r"^Not\s+required\s*(?::|—|-)\s*(.+)$", re.IGNORECASE
)
ALLOWED_TRACKING_FIELDS = {"mode", "issues", "reason"}
TRACKING_MODES = {"required", "not_required"}


class TaskSyncError(ValueError):
    """Raised when the issue/task contract is invalid or inconsistent."""


def load_tasks(path: Path = DEFAULT_TASKS_PATH) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    if not path.is_file():
        raise TaskSyncError(f"Task ledger not found: {path}")

    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TaskSyncError(
                f"Invalid JSONL at {path}:{line_number}: {exc}"
            ) from exc
        task_id = task.get("id")
        if not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(task_id):
            raise TaskSyncError(f"Invalid task id at {path}:{line_number}: {task_id!r}")
        if task_id in seen:
            raise TaskSyncError(f"Duplicate task id: {task_id}")
        seen.add(task_id)
        tasks.append(task)
    return tasks


def task_index(tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in tasks}


def get_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any]:
    try:
        return task_index(tasks)[task_id]
    except KeyError as exc:
        raise TaskSyncError(f"Task not found: {task_id}") from exc


def normalize_issue_ref(value: str) -> str:
    if not isinstance(value, str):
        raise TaskSyncError(f"Issue reference must be a string: {value!r}")
    candidate = value.strip()
    local = LOCAL_ISSUE_PATTERN.fullmatch(candidate)
    if local:
        return f"#{int(local.group(1))}"
    cross_repo = CROSS_REPO_ISSUE_PATTERN.fullmatch(candidate)
    if cross_repo:
        owner, repo, number = cross_repo.groups()
        return f"{owner.lower()}/{repo.lower()}#{int(number)}"
    raise TaskSyncError(
        f"Invalid issue reference {value!r}; use #123 or owner/repository#123"
    )


def normalize_reason(value: str) -> str:
    return " ".join(value.strip().split()).casefold()


def validate_task_tracking(task: dict[str, Any]) -> dict[str, Any] | None:
    task_id = task["id"]
    tracking = task.get("tracking")
    if tracking is None:
        if task.get("status") == "done":
            return None
        raise TaskSyncError(
            f"{task_id} is unfinished and must define tracking.mode plus issues or a reason"
        )
    if not isinstance(tracking, dict):
        raise TaskSyncError(f"{task_id} tracking must be an object")

    unknown = sorted(set(tracking).difference(ALLOWED_TRACKING_FIELDS))
    if unknown:
        raise TaskSyncError(
            f"{task_id} tracking has unsupported fields: {', '.join(unknown)}"
        )
    mode = tracking.get("mode")
    if mode not in TRACKING_MODES:
        raise TaskSyncError(
            f"{task_id} tracking.mode must be one of: {', '.join(sorted(TRACKING_MODES))}"
        )
    issues = tracking.get("issues")
    if not isinstance(issues, list):
        raise TaskSyncError(f"{task_id} tracking.issues must be a list")
    normalized = [normalize_issue_ref(issue) for issue in issues]
    if len(normalized) != len(set(normalized)):
        raise TaskSyncError(f"{task_id} tracking.issues contains duplicates")

    reason = tracking.get("reason")
    if mode == "required":
        if not normalized:
            raise TaskSyncError(f"{task_id} requires at least one issue reference")
        if reason not in (None, ""):
            raise TaskSyncError(
                f"{task_id} uses tracking.mode=required and must not define a reason"
            )
    else:
        if normalized:
            raise TaskSyncError(
                f"{task_id} uses tracking.mode=not_required and must not list issues"
            )
        if not isinstance(reason, str) or not reason.strip():
            raise TaskSyncError(
                f"{task_id} uses tracking.mode=not_required and needs a non-empty reason"
            )

    return {"mode": mode, "issues": normalized, "reason": reason}


def validate_ledger(tasks: list[dict[str, Any]]) -> None:
    for task in tasks:
        validate_task_tracking(task)


def tracking_plan(task_id: str, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    task = get_task(tasks, task_id)
    tracking = validate_task_tracking(task)
    if tracking is None:
        return {
            "mode": "historical",
            "issues": [],
            "reason": "Completed before the tracking contract was introduced",
        }

    issue_plans = []
    for issue_ref in tracking["issues"]:
        other_unfinished = sorted(
            candidate["id"]
            for candidate in tasks
            if candidate["id"] != task_id
            and candidate.get("status") != "done"
            and issue_ref in task_issue_refs(candidate)
        )
        issue_plans.append(
            {
                "ref": issue_ref,
                "other_unfinished_tasks": other_unfinished,
                "may_close": not other_unfinished,
            }
        )
    return {
        "mode": tracking["mode"],
        "issues": issue_plans,
        "reason": tracking.get("reason"),
    }


def task_issue_refs(task: dict[str, Any]) -> list[str]:
    tracking = task.get("tracking")
    if not isinstance(tracking, dict):
        return []
    issues = tracking.get("issues")
    if not isinstance(issues, list):
        return []
    refs = []
    for issue in issues:
        try:
            refs.append(normalize_issue_ref(issue))
        except TaskSyncError:
            continue
    return refs


def parse_pr_contract(body: str) -> dict[str, Any]:
    task_matches = TASK_LINE_PATTERN.findall(body or "")
    if len(task_matches) != 1:
        raise TaskSyncError(
            "PR body must contain exactly one '- Task: T-###' line"
        )

    issue_matches = ISSUE_LINE_PATTERN.findall(body or "")
    if len(issue_matches) != 1:
        raise TaskSyncError(
            "PR body must contain exactly one '- Issue: ...' line"
        )
    issue_value = issue_matches[0].strip()
    no_issue = NOT_REQUIRED_PATTERN.fullmatch(issue_value)
    if no_issue:
        return {
            "task_id": task_matches[0].upper(),
            "mode": "not_required",
            "reason": no_issue.group(1).strip(),
            "relations": [],
        }

    relations = []
    for raw_relation in issue_value.split(","):
        relation_match = RELATION_PATTERN.fullmatch(raw_relation.strip())
        if not relation_match:
            raise TaskSyncError(
                "Issue relationships must use 'Relates to #123' or 'Closes #123'"
            )
        verb, issue_ref = relation_match.groups()
        relations.append(
            {
                "verb": "closes" if verb.casefold() == "closes" else "relates",
                "ref": normalize_issue_ref(issue_ref),
            }
        )
    refs = [relation["ref"] for relation in relations]
    if len(refs) != len(set(refs)):
        raise TaskSyncError("PR body contains duplicate issue relationships")
    return {
        "task_id": task_matches[0].upper(),
        "mode": "required",
        "reason": None,
        "relations": relations,
    }


def title_task_id(title: str) -> str:
    match = TITLE_TASK_PATTERN.search(title or "")
    if not match:
        raise TaskSyncError(f"Could not extract a task ID from PR title: {title}")
    return match.group(1)


def validate_pr(
    title: str,
    body: str,
    tasks: list[dict[str, Any]],
    *,
    ready: bool,
) -> dict[str, Any]:
    validate_ledger(tasks)
    title_id = title_task_id(title)
    task = get_task(tasks, title_id)
    tracking = validate_task_tracking(task)
    if tracking is None:
        raise TaskSyncError(
            f"{title_id} predates issue tracking and cannot be reused for new PR work"
        )
    contract = parse_pr_contract(body)
    if contract["task_id"] != title_id:
        raise TaskSyncError(
            f"PR title references {title_id}, but PR body references {contract['task_id']}"
        )
    if ready and task.get("status") != "done":
        raise TaskSyncError(
            f"PR references {title_id}, but its status is {task.get('status')!r}, not 'done'. "
            f"Run finish-task.sh and prepare-merge.sh for {title_id} before final review."
        )

    if tracking["mode"] == "not_required":
        if contract["mode"] != "not_required":
            raise TaskSyncError(
                f"{title_id} records issue-free work, but the PR body links an issue"
            )
        if normalize_reason(contract["reason"]) != normalize_reason(tracking["reason"]):
            raise TaskSyncError(
                f"PR issue-free reason does not match {title_id}'s reviewed tracking reason"
            )
    else:
        if contract["mode"] != "required":
            raise TaskSyncError(
                f"{title_id} requires issue links, but the PR says no issue is required"
            )
        expected = set(tracking["issues"])
        actual = {relation["ref"] for relation in contract["relations"]}
        if expected != actual:
            raise TaskSyncError(
                f"PR issue references {sorted(actual)} do not match {title_id} {sorted(expected)}"
            )
        for relation in contract["relations"]:
            if relation["verb"] != "closes":
                continue
            blockers = sorted(
                candidate["id"]
                for candidate in tasks
                if candidate["id"] != title_id
                and candidate.get("status") != "done"
                and relation["ref"] in task_issue_refs(candidate)
            )
            if blockers:
                raise TaskSyncError(
                    f"PR cannot close {relation['ref']}; unfinished linked tasks remain: "
                    + ", ".join(blockers)
                )

    return {
        "task_id": title_id,
        "task_status": task.get("status"),
        "ready": ready,
        "tracking": tracking,
        "contract": contract,
    }


def split_issue_ref(issue_ref: str, current_repo: str) -> tuple[str, int]:
    local = LOCAL_ISSUE_PATTERN.fullmatch(issue_ref)
    if local:
        return current_repo, int(local.group(1))
    cross = CROSS_REPO_ISSUE_PATTERN.fullmatch(issue_ref)
    if not cross:
        raise TaskSyncError(f"Invalid normalized issue reference: {issue_ref}")
    owner, repo, number = cross.groups()
    return f"{owner}/{repo}", int(number)


def run_json(command: list[str]) -> Any:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise TaskSyncError(f"Read-only GitHub command failed: {' '.join(command)}\n{detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise TaskSyncError(
            f"GitHub command returned invalid JSON: {' '.join(command)}"
        ) from exc


def live_status(
    task_id: str,
    tasks: list[dict[str, Any]],
    *,
    runner: Callable[[list[str]], Any] = run_json,
) -> dict[str, Any]:
    if shutil.which("gh") is None:
        raise TaskSyncError("GitHub CLI 'gh' is required for live status")
    task = get_task(tasks, task_id)
    plan = tracking_plan(task_id, tasks)
    repo_payload = runner(["gh", "repo", "view", "--json", "nameWithOwner"])
    current_repo = repo_payload["nameWithOwner"]

    issues = []
    for issue in plan["issues"]:
        issue_repo, issue_number = split_issue_ref(issue["ref"], current_repo)
        payload = runner(
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--repo",
                issue_repo,
                "--json",
                "number,title,state,url",
            ]
        )
        issues.append({**issue, "repository": issue_repo, "live": payload})

    pull_requests = runner(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            current_repo,
            "--state",
            "all",
            "--search",
            f"{task_id} in:title",
            "--json",
            "number,title,state,isDraft,url,mergedAt,headRefName,baseRefName",
        ]
    )
    drift = []
    if task.get("status") != "done":
        for issue in issues:
            if issue["live"].get("state") == "CLOSED":
                drift.append(
                    f"{issue['ref']} is closed while {task_id} is {task.get('status')}"
                )
    has_merged_pr = any(pull_request.get("mergedAt") for pull_request in pull_requests)
    has_open_pr = any(
        pull_request.get("state") == "OPEN" for pull_request in pull_requests
    )
    if task.get("status") == "done" and not has_merged_pr and not has_open_pr:
        drift.append(f"{task_id} is done but no merged pull request was found")

    return {
        "task": task,
        "repository": current_repo,
        "tracking_plan": plan,
        "issues": issues,
        "pull_requests": pull_requests,
        "drift": drift,
        "read_only": True,
    }


def print_plan(task_id: str, tasks: list[dict[str, Any]]) -> None:
    task = get_task(tasks, task_id)
    plan = tracking_plan(task_id, tasks)
    print(f"GitHub task plan: {task_id} — {task.get('title', '')}")
    print(f"Task status: {task.get('status')}")
    print(f"Tracking mode: {plan['mode']}")
    if plan["mode"] == "not_required":
        print(f"Issue-free reason: {plan['reason']}")
    elif plan["mode"] == "historical":
        print("Historical completed task; no tracking migration required")
    else:
        for issue in plan["issues"]:
            relationship = "Closes" if issue["may_close"] else "Relates to"
            print(f"- {issue['ref']}: use '{relationship} {issue['ref']}'")
            if issue["other_unfinished_tasks"]:
                print(
                    "  Other unfinished tasks: "
                    + ", ".join(issue["other_unfinished_tasks"])
                )


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)

    def add_tasks_argument(command: argparse.ArgumentParser) -> None:
        command.add_argument("--tasks", type=Path, default=DEFAULT_TASKS_PATH)

    validate_ledger_parser = subparsers.add_parser("validate-ledger")
    add_tasks_argument(validate_ledger_parser)
    plan = subparsers.add_parser("plan")
    add_tasks_argument(plan)
    plan.add_argument("task_id")
    plan.add_argument("--json", action="store_true")
    validate = subparsers.add_parser("validate-pr")
    add_tasks_argument(validate)
    validate.add_argument("--title")
    validate.add_argument("--body")
    validate.add_argument("--ready", action="store_true")
    status = subparsers.add_parser("status")
    add_tasks_argument(status)
    status.add_argument("task_id")
    status.add_argument("--json", action="store_true")
    return value


def main() -> int:
    try:
        args = parser().parse_args()
        tasks = load_tasks(args.tasks)
        if args.command == "validate-ledger":
            validate_ledger(tasks)
            print(f"GitHub task tracking valid for {len(tasks)} tasks")
            return 0
        if args.command == "plan":
            plan = tracking_plan(args.task_id, tasks)
            if args.json:
                print(json.dumps(plan, indent=2))
            else:
                print_plan(args.task_id, tasks)
            return 0
        if args.command == "validate-pr":
            title = args.title if args.title is not None else os.getenv("PR_TITLE", "")
            body = args.body if args.body is not None else os.getenv("PR_BODY", "")
            ready = args.ready or os.getenv("PR_READY", "false").casefold() == "true"
            result = validate_pr(title, body, tasks, ready=ready)
            print(
                f"PR task and issue contract accepted: {result['task_id']} "
                f"({result['task_status']})"
            )
            return 0
        result = live_status(args.task_id, tasks)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_plan(args.task_id, tasks)
            print(f"Repository: {result['repository']}")
            for issue in result["issues"]:
                live = issue["live"]
                print(
                    f"Issue {issue['ref']}: {live.get('state')} — "
                    f"{live.get('title')} ({live.get('url')})"
                )
            for pull_request in result["pull_requests"]:
                print(
                    f"PR #{pull_request['number']}: {pull_request['state']} — "
                    f"{pull_request['title']} ({pull_request['url']})"
                )
            if result["drift"]:
                print("Drift:")
                for drift in result["drift"]:
                    print(f"- {drift}")
            else:
                print("Drift: none detected")
        return 0
    except TaskSyncError as exc:
        print(f"GitHub task sync error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
