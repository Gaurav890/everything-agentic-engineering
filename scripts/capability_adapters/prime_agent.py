#!/usr/bin/env python3
"""Read-only detection and inert setup planning for optional Prime Agent use."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

CAPABILITY_ID = "prime-agent"
SOURCE = {
    "repository": "https://github.com/PrimeIntellect-ai/prime-agent",
    "reviewed_commit": "71ca6cfd1a2f7205ca0ec1baa65d10d0ed88f6e8",
    "license": "MIT",
    "reviewed_at": "2026-08-10",
}


def doctor_report(command: str = "prime-agent") -> dict:
    """Locate a command without invoking it or reading runtime configuration."""
    resolved = shutil.which(command)
    return {
        "schema_version": 1,
        "capability_id": CAPABILITY_ID,
        "operation": "doctor",
        "status": "available_not_enabled" if resolved else "not_detected",
        "binary_detected": resolved is not None,
        "binary_path": str(Path(resolved).resolve()) if resolved else None,
        "binary_executed": False,
        "version": None,
        "version_probe_performed": False,
        "enabled_by_repository": False,
        "source": SOURCE,
        "warnings": [
            "Detection does not establish trust, compatibility, configuration, or permission to run.",
            "Prime Agent executes generated Python and commands with the user's permissions and is not a security sandbox.",
        ],
        "mutation_performed": False,
    }


def plan_report() -> dict:
    """Return a bounded human-review plan; never execute any plan item."""
    return {
        "schema_version": 1,
        "capability_id": CAPABILITY_ID,
        "operation": "plan",
        "status": "human_review_required",
        "mode": "plan_only",
        "automatic": False,
        "source": SOURCE,
        "security_boundary": {
            "is_security_sandbox": False,
            "warning": "Prime Agent executes model-generated Python and commands with the user's permissions; its workers and kernels are not a security sandbox.",
            "required_control": "Use an independently reviewed external sandbox for untrusted code or artifacts.",
        },
        "recommended_scope": {
            "workspace": "one explicitly named task worktree",
            "branch": "one short-lived task branch",
            "file_ownership": "exclusive paths declared before execution",
            "credentials": "none by default",
            "network": "disabled by default",
            "production": "forbidden",
            "merge_authority": "forbidden",
        },
        "budgets": {
            "max_session_minutes": 60,
            "max_attempts_per_failure": 3,
            "max_parallel_subagents": 3,
            "max_active_worktrees": 3,
            "max_scheduled_runs_without_review": 1,
            "idle_timeout_minutes": 10,
            "require_new_evidence_before_retry": True,
        },
        "stop_conditions": [
            "Acceptance criteria pass with recorded evidence.",
            "Any declared time, attempt, subagent, worktree, or idle budget is reached.",
            "An unapproved authority expansion is requested.",
            "The same failure repeats without new evidence or a changed hypothesis.",
            "A worker writes outside exclusive file ownership.",
            "A human requests stop or pause."
        ],
        "kill_switch": {
            "owner": "human operator",
            "actions": ["Stop the session and dedicated process group.", "Disable an approved schedule.", "Preserve logs and uncommitted work.", "Revoke only exact session-specific credentials after review."],
            "automatic_destructive_cleanup": False
        },
        "human_approvals": [
            "runtime installation or update",
            "login, credential, provider, or model configuration",
            "MCP registration, network access, or sandbox changes",
            "schedule or background-service activation",
            "production, deployment, billing, or external-write access",
            "destructive cleanup",
            "pull-request approval or merge"
        ],
        "instructions": [
            {"order": 1, "action": "Review the pinned upstream source, license, release artifacts, and checksums.", "execute": False, "requires_human_approval": True},
            {"order": 2, "action": "Create a dedicated task branch and isolated worktree with exclusive file ownership.", "execute": False, "requires_human_approval": False},
            {"order": 3, "action": "Record allowed tools, forbidden actions, budgets, stop conditions, evaluator, and rollback.", "execute": False, "requires_human_approval": False},
            {"order": 4, "action": "Request separate approval for every authority expansion.", "execute": False, "requires_human_approval": True},
            {"order": 5, "action": "Run independent verification and leave PR approval and merge to a human.", "execute": False, "requires_human_approval": False}
        ],
        "commands": [],
        "rollback": ["Stop the approved session and child process group.", "Disable approved schedules.", "Preserve evidence before cleanup.", "Remove only exact human-confirmed isolated paths and credentials.", "Leave main, approvals, and production unchanged."],
        "explicitly_not_performed": ["download", "installation", "update", "login", "daemon or service start", "schedule creation", "provider or model configuration", "credential access or modification", "MCP registration", "network or sandbox change", "production or deployment change", "approval or merge"],
        "mutation_performed": False,
    }


def print_human(report: dict) -> None:
    if report["operation"] == "doctor":
        message = f"FOUND  Prime Agent command at {report['binary_path']} (not executed)." if report["binary_detected"] else "INFO   Prime Agent command was not detected on PATH."
        print(message)
        print("       Optional capability remains disabled; no mutation performed.")
        return
    print("Prime Agent optional runtime plan (human review required)")
    print(f"Pinned source: {report['source']['reviewed_commit']}")
    print("No commands were executed and no runtime authority was changed.")
    print("Prime Agent is not a security sandbox; review the documented controls first.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect or plan optional Prime Agent use without mutation.")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    doctor = subparsers.add_parser("doctor", help="Locate Prime Agent without executing it.")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--command", default=os.environ.get("PRIME_AGENT_COMMAND", "prime-agent"))
    plan = subparsers.add_parser("plan", help="Print an inert, human-gated plan.")
    plan.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = doctor_report(args.command) if args.operation == "doctor" else plan_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
