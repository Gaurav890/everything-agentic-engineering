#!/usr/bin/env python3
"""Verify post-merge task truth and report cleanup without mutation."""

from __future__ import annotations

import argparse
import base64
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import github_task_sync  # noqa: E402


TRANSIENT_SECTIONS = {"Current goal", "In progress", "Exact next action"}
TRANSIENT_PATTERN = re.compile(
    r"\b(merge|merged|merging|review|reviewed|pending|feature branch|pull request|PR)\b",
    re.IGNORECASE,
)
WRITE_WORDS = {
    "create",
    "delete",
    "edit",
    "merge",
    "close",
    "reopen",
    "comment",
    "label",
    "approve",
    "push",
    "update-ref",
}


class CloseoutError(RuntimeError):
    """Raised when closeout cannot safely establish its inputs."""


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
        raise CloseoutError(f"Read-only command failed: {' '.join(command)}\n{detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CloseoutError(
            f"Command returned invalid JSON: {' '.join(command)}"
        ) from exc


def run_text(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise CloseoutError(f"Read-only command failed: {' '.join(command)}\n{detail}")
    return completed.stdout


def remote_file(
    repository: str,
    branch: str,
    path: str,
    github_runner: Callable[[list[str]], Any],
) -> str:
    endpoint = (
        f"repos/{repository}/contents/{quote(path, safe='/')}?ref="
        f"{quote(branch, safe='')}"
    )
    payload = github_runner(["gh", "api", "--method", "GET", endpoint])
    if payload.get("encoding") != "base64" or not isinstance(payload.get("content"), str):
        raise CloseoutError(f"Unexpected GitHub contents response for {path}")
    try:
        return base64.b64decode(payload["content"]).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise CloseoutError(f"Could not decode GitHub contents for {path}") from exc


def parse_tasks(text: str, source: str) -> list[dict[str, Any]]:
    tasks = []
    seen = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CloseoutError(
                f"Invalid task JSON at {source}:{line_number}: {exc}"
            ) from exc
        task_id = task.get("id")
        if not isinstance(task_id, str) or not github_task_sync.TASK_ID_PATTERN.fullmatch(task_id):
            raise CloseoutError(f"Invalid task id at {source}:{line_number}: {task_id!r}")
        if task_id in seen:
            raise CloseoutError(f"Duplicate task id in {source}: {task_id}")
        seen.add(task_id)
        tasks.append(task)
    return tasks


def markdown_sections(text: str) -> dict[str, list[tuple[int, str]]]:
    sections: dict[str, list[tuple[int, str]]] = {}
    current = ""
    for line_number, line in enumerate(text.splitlines(), 1):
        heading = re.fullmatch(r"##\s+(.+?)\s*", line)
        if heading:
            current = heading.group(1)
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append((line_number, line))
    return sections


def transient_handoff_claims(
    text: str, task_id: str | None = None
) -> list[dict[str, Any]]:
    claims = []
    for section, lines in markdown_sections(text).items():
        if section not in TRANSIENT_SECTIONS:
            continue
        for line_number, line in lines:
            task_ids = github_task_sync.TASK_ID_PATTERN.findall(line)
            if (
                task_ids
                and (task_id is None or task_id in task_ids)
                and TRANSIENT_PATTERN.search(line)
            ):
                claims.append(
                    {
                        "section": section,
                        "line": line_number,
                        "task_ids": task_ids,
                        "text": line.strip(),
                    }
                )
    return claims


def stale_handoff_claims(text: str, task_id: str) -> list[dict[str, Any]]:
    return transient_handoff_claims(text, task_id)


def parse_worktrees(text: str) -> list[dict[str, str]]:
    worktrees = []
    current: dict[str, str] = {}
    for line in [*text.splitlines(), ""]:
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return worktrees


def local_cleanup(
    branch: str,
    text_runner: Callable[[list[str]], str],
) -> dict[str, Any]:
    local_branches = {
        line.strip()
        for line in text_runner(
            ["git", "branch", "--format=%(refname:short)"]
        ).splitlines()
        if line.strip()
    }
    matching_worktrees = []
    commands = []
    for worktree in parse_worktrees(text_runner(["git", "worktree", "list", "--porcelain"])):
        if worktree.get("branch") != f"refs/heads/{branch}":
            continue
        path = worktree.get("worktree", "")
        clean = not text_runner(["git", "-C", path, "status", "--porcelain"]).strip()
        managed = "/.claude/worktrees/" in path
        matching_worktrees.append(
            {"path": path, "clean": clean, "managed": managed}
        )
        if clean and managed:
            commands.append(f"git worktree remove {shlex.quote(path)}")

    worktrees_removable = all(
        item["clean"] and item["managed"] for item in matching_worktrees
    )
    if branch in local_branches and worktrees_removable:
        commands.append(f"git branch -d {shlex.quote(branch)}")

    return {
        "branch": branch,
        "local_branch_exists": branch in local_branches,
        "worktrees": matching_worktrees,
        "commands": commands,
        "commands_executed": False,
    }


def task_prs(
    repository: str,
    default_branch: str,
    task_id: str,
    github_runner: Callable[[list[str]], Any],
) -> list[dict[str, Any]]:
    payload = github_runner(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            repository,
            "--state",
            "merged",
            "--search",
            f"{task_id} in:title",
            "--json",
            "number,title,body,state,url,mergedAt,headRefName,baseRefName",
        ]
    )
    matches = []
    for candidate in payload:
        try:
            candidate_id = github_task_sync.title_task_id(candidate.get("title", ""))
        except github_task_sync.TaskSyncError:
            continue
        if candidate_id == task_id and candidate.get("baseRefName") == default_branch:
            matches.append(candidate)
    return matches


def issue_statuses(
    repository: str,
    task: dict[str, Any],
    contract: dict[str, Any] | None,
    github_runner: Callable[[list[str]], Any],
) -> list[dict[str, Any]]:
    statuses = []
    relation_by_ref = {
        relation["ref"]: relation["verb"]
        for relation in (contract or {}).get("relations", [])
    }
    for issue_ref in github_task_sync.task_issue_refs(task):
        issue_repo, issue_number = github_task_sync.split_issue_ref(issue_ref, repository)
        payload = github_runner(
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--repo",
                issue_repo,
                "--json",
                "number,title,state,url,closedAt",
            ]
        )
        statuses.append(
            {
                "ref": issue_ref,
                "repository": issue_repo,
                "relationship": relation_by_ref.get(issue_ref),
                "live": payload,
            }
        )
    return statuses


def closeout(
    task_id: str,
    *,
    github_runner: Callable[[list[str]], Any] = run_json,
    text_runner: Callable[[list[str]], str] = run_text,
) -> dict[str, Any]:
    if shutil.which("gh") is None:
        raise CloseoutError("GitHub CLI 'gh' is required for post-merge closeout")

    repository_payload = github_runner(
        ["gh", "repo", "view", "--json", "nameWithOwner,defaultBranchRef"]
    )
    repository = repository_payload["nameWithOwner"]
    default_branch = repository_payload["defaultBranchRef"]["name"]
    tasks_text = remote_file(
        repository,
        default_branch,
        "docs/40-execution/TASKS.jsonl",
        github_runner,
    )
    handoff_text = remote_file(
        repository,
        default_branch,
        "docs/40-execution/HANDOFF.md",
        github_runner,
    )
    tasks = parse_tasks(tasks_text, f"{repository}@{default_branch}:TASKS.jsonl")
    github_task_sync.validate_ledger(tasks)
    task = github_task_sync.get_task(tasks, task_id)
    findings = []

    if task.get("status") != "done":
        findings.append(
            f"Authoritative {default_branch} records {task_id} as {task.get('status')!r}, not 'done'"
        )

    pull_requests = task_prs(
        repository, default_branch, task_id, github_runner
    )
    selected_pr = pull_requests[0] if len(pull_requests) == 1 else None
    if not pull_requests:
        findings.append(f"No merged {default_branch} pull request found for {task_id}")
    elif len(pull_requests) > 1:
        findings.append(
            f"Multiple merged {default_branch} pull requests found for {task_id}; closeout is ambiguous"
        )

    contract = None
    tracking = github_task_sync.validate_task_tracking(task)
    if selected_pr and tracking is not None:
        try:
            validated = github_task_sync.validate_pr(
                selected_pr["title"], selected_pr.get("body", ""), tasks, ready=True
            )
            contract = validated["contract"]
        except github_task_sync.TaskSyncError as exc:
            findings.append(f"Merged PR contract is invalid: {exc}")

    issues = issue_statuses(repository, task, contract, github_runner)
    for issue in issues:
        if issue["relationship"] == "closes" and issue["live"].get("state") != "CLOSED":
            findings.append(
                f"{issue['ref']} should be closed by the merged PR but is {issue['live'].get('state')}"
            )

    stale_claims = stale_handoff_claims(handoff_text, task_id)
    if selected_pr and stale_claims:
        findings.append(
            f"HANDOFF.md contains {len(stale_claims)} transient post-merge claim(s) for {task_id}"
        )

    cleanup = local_cleanup(selected_pr["headRefName"], text_runner) if selected_pr else None
    return {
        "task_id": task_id,
        "repository": repository,
        "default_branch": default_branch,
        "main_task": {"title": task.get("title"), "status": task.get("status")},
        "pull_request": selected_pr,
        "pull_request_candidates": len(pull_requests),
        "issues": issues,
        "handoff": {"stale_claims": stale_claims},
        "cleanup": cleanup,
        "findings": findings,
        "verdict": "PASS" if not findings else "ATTENTION",
        "read_only": True,
    }


def print_report(result: dict[str, Any]) -> None:
    print(f"Post-merge closeout: {result['task_id']}")
    print(f"Verdict: {result['verdict']}")
    print(
        f"Authoritative {result['default_branch']} task state: "
        f"{result['main_task']['status']}"
    )
    pull_request = result["pull_request"]
    if pull_request:
        print(
            f"Merged PR #{pull_request['number']}: {pull_request['title']} "
            f"({pull_request['url']})"
        )
    for issue in result["issues"]:
        print(
            f"Issue {issue['ref']}: {issue['live'].get('state')} "
            f"({issue['relationship'] or 'historical'})"
        )
    claims = result["handoff"]["stale_claims"]
    print(f"Transient handoff claims: {len(claims)}")
    for claim in claims:
        print(
            f"- {claim['section']} line {claim['line']}: {claim['text']}"
        )

    cleanup = result["cleanup"]
    if cleanup:
        print(f"Local branch present: {cleanup['local_branch_exists']}")
        for worktree in cleanup["worktrees"]:
            state = "clean" if worktree["clean"] else "DIRTY — preserve"
            ownership = "managed" if worktree["managed"] else "UNMANAGED — preserve"
            print(f"Worktree: {worktree['path']} ({state}; {ownership})")
        if cleanup["commands"]:
            print("Optional local cleanup commands (not executed):")
            for command in cleanup["commands"]:
                print(f"  {command}")

    if result["findings"]:
        print("Attention required:")
        for finding in result["findings"]:
            print(f"- {finding}")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("task_id", nargs="?")
    value.add_argument("--json", action="store_true")
    value.add_argument(
        "--validate-handoff",
        action="store_true",
        help="Reject task-specific PR/merge claims in volatile handoff sections",
    )
    return value


def main() -> int:
    try:
        args = parser().parse_args()
        if args.validate_handoff:
            handoff = (ROOT / "docs/40-execution/HANDOFF.md").read_text()
            claims = transient_handoff_claims(handoff)
            if args.json:
                print(json.dumps({"claims": claims, "valid": not claims}, indent=2))
            elif claims:
                print("Transient task lifecycle claims found in HANDOFF.md:")
                for claim in claims:
                    print(
                        f"- {claim['section']} line {claim['line']}: {claim['text']}"
                    )
            else:
                print("HANDOFF.md contains no transient task lifecycle claims")
            return 0 if not claims else 1
        if not args.task_id:
            raise CloseoutError("A task ID is required unless --validate-handoff is used")
        result = closeout(args.task_id)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_report(result)
        return 0 if result["verdict"] == "PASS" else 1
    except (CloseoutError, github_task_sync.TaskSyncError) as exc:
        print(f"Post-merge closeout error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
