#!/usr/bin/env python3
"""Fail-closed semantic validation for Product-to-Proof contract records.

JSON Schema owns record shape. This module owns cross-record invariants that
JSON Schema cannot express: DAG validity, wave membership, filesystem
containment, journal continuity, derived-state completion, and benchmark
consistency. It performs no mutation and launches no provider.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from datetime import datetime
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import ValidationError
    from referencing import Registry, Resource
except ImportError:  # pragma: no cover - production validation fails closed below
    Draft202012Validator = None
    FormatChecker = None
    ValidationError = Exception
    Registry = None
    Resource = None


SCHEMA_VERSION = "1.0.0"
REDUCER_VERSION = "1.0.0"
GLOB_RE = re.compile(r"[*?[]")
ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILES = {
    "action_registry": "action-registry.schema.json",
    "plan": "run-plan.schema.json",
    "event": "run-event.schema.json",
    "state": "run-state.schema.json",
    "decision": "human-decision.schema.json",
    "evidence": "run-evidence.schema.json",
    "benchmark": "benchmark-result.schema.json",
    "adapter": "adapter-operation.schema.json",
}


class ContractError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    """Canonicalize the closed ASCII-key event subset used by this contract.

    Event schemas use fixed ASCII keys and do not need floating-point values.
    Rejecting floats and non-ASCII keys avoids platform-dependent encodings.
    The T-056 journal implementation must use a conforming RFC 8785 encoder and
    prove byte parity with these fixtures before real execution is enabled.
    """

    def inspect(item: Any) -> None:
        if isinstance(item, float):
            raise ContractError("floating-point event values are not canonical in v1")
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str) or not key.isascii():
                    raise ContractError("event object keys must be ASCII strings")
                inspect(child)
        elif isinstance(item, list):
            for child in item:
                inspect(child)
        elif item is not None and not isinstance(item, (str, int, bool)):
            raise ContractError(f"unsupported canonical value: {type(item).__name__}")

    inspect(value)
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_schema_registry() -> tuple[dict[str, dict[str, Any]], Any]:
    require(
        Draft202012Validator is not None and Registry is not None and Resource is not None,
        "jsonschema and referencing are required for authoritative validation",
    )
    schemas = {
        kind: json.loads((ROOT / ".agentic/schemas" / filename).read_text())
        for kind, filename in SCHEMA_FILES.items()
    }
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
    )
    return schemas, registry


def validate_schema(kind: str, value: Any) -> None:
    schemas, registry = load_schema_registry()
    schema_kind = "event" if kind == "journal" else kind
    require(schema_kind in schemas, f"no schema for record kind {kind}")
    validator = Draft202012Validator(
        schemas[schema_kind], registry=registry, format_checker=FormatChecker()
    )
    records = value if kind == "journal" else [value]
    require(isinstance(records, list), "journal must be an array of events")
    for index, record in enumerate(records):
        try:
            validator.validate(record)
        except ValidationError as exc:
            location = "/".join(str(part) for part in exc.absolute_path) or "record"
            raise ContractError(f"{kind} schema violation at {index}:{location}: {exc.message}") from exc


def static_prefix(pattern: str) -> str:
    return GLOB_RE.split(pattern, maxsplit=1)[0].rstrip("/")


def normalize_owned_path(pattern: str) -> str:
    require(bool(pattern), "writable path must not be empty")
    require("\x00" not in pattern, "writable path contains NUL")
    require("\\" not in pattern, "writable path must use POSIX separators")
    value = PurePosixPath(pattern)
    require(not value.is_absolute(), f"absolute writable path is forbidden: {pattern}")
    require(".." not in value.parts, f"parent traversal is forbidden: {pattern}")
    normalized = str(value)
    require(normalized not in {"", "."}, "project-root ownership is forbidden")
    return normalized.casefold()


def paths_overlap(left: str, right: str) -> bool:
    left_normalized = normalize_owned_path(left)
    right_normalized = normalize_owned_path(right)
    left_prefix = static_prefix(left_normalized)
    right_prefix = static_prefix(right_normalized)
    return (
        left_prefix == right_prefix
        or left_prefix.startswith(right_prefix + "/")
        or right_prefix.startswith(left_prefix + "/")
        or fnmatch.fnmatch(left_prefix, right_normalized)
        or fnmatch.fnmatch(right_prefix, left_normalized)
    )


def validate_containment(root: Path, pattern: str) -> None:
    normalize_owned_path(pattern)
    root = root.resolve(strict=True)
    prefix = static_prefix(pattern)
    candidate = root / prefix
    current = candidate
    while not current.exists() and current != root:
        current = current.parent
    resolved = current.resolve(strict=True)
    require(resolved == root or root in resolved.parents, f"writable path escapes project root: {pattern}")
    if candidate.exists():
        resolved_candidate = candidate.resolve(strict=True)
        require(
            resolved_candidate == root or root in resolved_candidate.parents,
            f"writable path resolves outside project root: {pattern}",
        )


def validate_project_identity(record: dict[str, Any], expected_root: Path | None) -> Path:
    canonical = Path(record["canonical_path"])
    require(canonical.is_absolute(), "canonical project root must be absolute")
    require(canonical.exists() and canonical.is_dir(), "canonical project root must exist")
    resolved = canonical.resolve(strict=True)
    require(str(resolved) == record["canonical_path"], "canonical project root does not match realpath")
    stat = resolved.stat()
    require(stat.st_dev == record["device"], "project root device changed")
    require(stat.st_ino == record["inode"], "project root inode changed")
    if expected_root is not None:
        require(resolved == expected_root.resolve(strict=True), "plan targets an unexpected project root")
    return resolved


def validate_plan(
    plan: dict[str, Any],
    expected_root: Path | None = None,
    action_registry: dict[str, Any] | None = None,
    require_uncreated_worktrees: bool = True,
) -> None:
    require(plan.get("schema_version") == SCHEMA_VERSION, "unknown plan schema version")
    require(re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", plan.get("base_commit", "")) is not None, "base commit must be immutable")
    concurrency = plan.get("concurrency")
    require(isinstance(concurrency, int) and 1 <= concurrency <= 8, "invalid concurrency")
    root = validate_project_identity(plan["project_root"], expected_root)
    worktree_parent = validate_project_identity(plan["worktree_parent"], None)
    require(worktree_parent != root, "worktree parent must be separate from the source checkout")
    default_branch = plan["default_branch"]
    require(default_branch["ref"] == f"refs/heads/{default_branch['name']}", "default branch ref is not canonical")
    require(default_branch["commit"] == plan["base_commit"], "default branch and base commit differ")
    require(action_registry is not None, "authoritative plan validation requires the action registry")
    registry_sha256 = plan["runtime_policy"]["action_registry_sha256"]
    resolve_actions([], action_registry, registry_sha256)

    tasks = plan.get("tasks", [])
    ids = [task.get("task_id") for task in tasks]
    require(len(ids) == len(set(ids)), "task ids must be unique")
    index = {task["task_id"]: task for task in tasks}
    branch_names = [task["branch"].casefold() for task in tasks]
    worktree_paths = [str(Path(task["worktree"])) for task in tasks]
    require(len(branch_names) == len(set(branch_names)), "task branches must be unique")
    require(len(worktree_paths) == len(set(worktree_paths)), "task worktrees must be unique")
    default_aliases = {
        default_branch["name"].casefold(),
        default_branch["ref"].casefold(),
        f"origin/{default_branch['name']}".casefold(),
        f"refs/remotes/origin/{default_branch['name']}".casefold(),
    }
    provider_capabilities = {
        "manual": {"manual_packet", "workspace_write", "network_disabled", "mcp_disabled", "checkpoint_resume"},
        "claude-code": {"structured_stream", "session_resume", "process_interrupt", "checkpoint_resume", "workspace_write", "network_disabled", "mcp_disabled"},
        "codex": {"structured_stream", "session_resume", "process_interrupt", "checkpoint_resume", "workspace_write", "network_disabled", "mcp_disabled"},
    }
    for task in tasks:
        require(task["provider"] in plan["runtime_policy"]["allowed_providers"], f"provider not allowed for {task['task_id']}")
        capabilities = set(task["capability_ids"])
        require(capabilities <= provider_capabilities[task["provider"]], f"task {task['task_id']} requests capabilities unsupported by its provider")
        require(("workspace_write" in capabilities) == plan["runtime_policy"]["permissions"]["workspace_write"], f"task {task['task_id']} workspace capability differs from runtime policy")
        if plan["runtime_policy"]["network"]["mode"] == "disabled":
            require("network_disabled" in capabilities, f"task {task['task_id']} does not bind disabled network")
        if plan["runtime_policy"]["mcp"]["mode"] == "disabled":
            require("mcp_disabled" in capabilities, f"task {task['task_id']} does not bind disabled MCP")
        require(task["branch"].casefold() not in default_aliases, f"task {task['task_id']} targets the default branch")
        planned_worktree = Path(task["worktree"])
        require(planned_worktree.is_absolute(), f"task {task['task_id']} worktree is not absolute")
        require("\x00" not in task["worktree"] and "\\" not in task["worktree"] and ".." not in PurePosixPath(task["worktree"]).parts, f"task {task['task_id']} worktree path is unsafe")
        require(planned_worktree.parent.resolve(strict=True) == worktree_parent, f"task {task['task_id']} worktree is outside the reviewed parent")
        if require_uncreated_worktrees:
            require(not planned_worktree.exists(), f"task {task['task_id']} worktree already exists and must be reconciled")
        elif planned_worktree.exists():
            require(not planned_worktree.is_symlink(), f"task {task['task_id']} worktree cannot be a symlink")
            resolved_worktree = planned_worktree.resolve(strict=True)
            require(resolved_worktree.is_dir(), f"task {task['task_id']} worktree is not a directory")
            require(resolved_worktree.parent == worktree_parent, f"task {task['task_id']} worktree escaped the reviewed parent")
        for dependency in task.get("depends_on", []):
            require(dependency in index, f"missing dependency {dependency}")
            require(dependency != task["task_id"], f"self dependency {dependency}")
        for owned in task.get("writable_paths", []):
            validate_containment(root, owned)
        resolve_actions(task["check_action_ids"], action_registry, registry_sha256)
        resolve_actions(task["allowed_action_ids"], action_registry, registry_sha256)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        require(task_id not in visiting, f"dependency cycle includes {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in index[task_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(index):
        visit(task_id)

    owners: list[tuple[str, str]] = []
    for task in tasks:
        for owned in task["writable_paths"]:
            for other_task, other_path in owners:
                require(
                    not paths_overlap(owned, other_path),
                    f"writable ownership collision: {task['task_id']}:{owned} and {other_task}:{other_path}",
                )
            owners.append((task["task_id"], owned))

    waves = plan.get("waves", [])
    require([wave["wave"] for wave in waves] == list(range(1, len(waves) + 1)), "waves must be consecutive")
    assigned = [task_id for wave in waves for task_id in wave["task_ids"]]
    require(len(assigned) == len(set(assigned)), "a task appears in more than one wave")
    require(set(assigned) == set(ids), "waves must assign every task exactly once")
    wave_by_task = {task_id: wave["wave"] for wave in waves for task_id in wave["task_ids"]}
    for wave in waves:
        require(wave["task_ids"] == sorted(wave["task_ids"]), "tasks inside a wave must be task-id sorted")
        require(len(wave["task_ids"]) <= concurrency, "wave exceeds configured concurrency")
        require(wave.get("requires_human_continue") is True, "every wave requires human continuation")
    for task in tasks:
        for dependency in task["depends_on"]:
            require(wave_by_task[dependency] < wave_by_task[task["task_id"]], "dependency must be in an earlier wave")

    remaining = set(index)
    completed: set[str] = set()
    expected_waves: list[list[str]] = []
    while remaining:
        ready = sorted(
            task_id
            for task_id in remaining
            if set(index[task_id].get("depends_on", [])) <= completed
        )
        require(bool(ready), "dependency graph cannot produce a ready wave")
        selected = ready[:concurrency]
        expected_waves.append(selected)
        completed.update(selected)
        remaining.difference_update(selected)
    actual_waves = [wave["task_ids"] for wave in waves]
    require(actual_waves == expected_waves, "waves must use deterministic maximally filled ready sets")


def validate_journal(
    events: list[dict[str, Any]],
    plan: dict[str, Any],
    action_registry: dict[str, Any],
    expected_head_sha256: str | None = None,
    expected_last_sequence: int | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    validate_schema("plan", plan)
    validate_plan(plan, project_root, action_registry, require_uncreated_worktrees=False)
    plan_sha256 = digest(plan)
    action_index = {action["id"]: action for action in action_registry["actions"]}
    require(bool(events), "journal must not be empty")
    plan_tasks = {task["task_id"]: task for task in plan["tasks"]}
    plan_waves = {wave["wave"]: set(wave["task_ids"]) for wave in plan["waves"]}
    wave_by_task = {
        task_id: wave_number
        for wave_number, task_ids in plan_waves.items()
        for task_id in task_ids
    }
    event_ids: set[str] = set()
    run_id = events[0].get("run_id")
    require(run_id == plan["run_id"], "journal run id differs from the immutable plan")
    previous: dict[str, Any] | None = None
    status = "planned"
    current_wave = 0
    started_waves: set[int] = set()
    paused_waves: set[int] = set()
    workers: dict[str, dict[str, Any]] = {}
    worker_by_task: dict[str, str] = {}
    checks: dict[str, dict[str, Any]] = {}
    evidence_records: dict[str, dict[str, Any]] = {}
    decision_records: dict[str, dict[str, Any]] = {}
    resume_authorizations: dict[str, str] = {}
    gate_checkpoint_event_id: str | None = None
    gate_subject: dict[str, str] | None = None
    evidence_required: set[str] = set()
    human_gate = {"required": False, "kind": "none", "decision_event_id": None}
    terminal_statuses = {"completed", "failed_safe", "cancelled"}
    for expected_sequence, event in enumerate(events, start=1):
        require(event.get("schema_version") == SCHEMA_VERSION, "unknown event schema version")
        require(event.get("sequence") == expected_sequence, "event sequence is not contiguous")
        require(event.get("event_id") not in event_ids, "duplicate event id")
        event_ids.add(event["event_id"])
        require(event.get("run_id") == run_id, "journal mixes run ids")
        require(event.get("plan_sha256") == plan_sha256, "journal event is bound to another plan")
        if previous is None:
            require(event.get("type") == "run.planned", "first event must be run.planned")
            require(event.get("previous_event_sha256") is None, "genesis event must have a null previous hash")
            require(event.get("payload", {}).get("plan_sha256") == plan_sha256, "genesis payload is bound to another plan")
        else:
            require(event.get("previous_event_sha256") == digest(previous), "journal hash chain is invalid")
        event_type = event.get("type")
        require(status not in terminal_statuses, "terminal run cannot accept later events")
        if expected_sequence > 1:
            require(event_type != "run.planned", "run.planned may occur only at genesis")
        if event_type == "run.started":
            require(status == "planned", "run.started requires planned state")
            require(event.get("actor", {}).get("kind") == "human", "run.started actor must be human")
            decision_id = event.get("payload", {}).get("decision_id")
            decision = decision_records.get(decision_id)
            require(decision is not None, "run.started references a missing human decision")
            require(decision["gate_kind"] == "run_start", "run.started decision has the wrong gate")
            require(decision["disposition"] == "continue", "run.started decision does not authorize execution")
            require(decision["subject"]["kind"] == "run" and decision["subject"]["id"] == run_id, "run.started decision targets another run")
            status = "running"
        elif event_type == "wave.started":
            require(status == "running", "wave.started requires running state")
            wave_number = event.get("wave")
            require(wave_number == current_wave + 1, "waves must start consecutively")
            require(wave_number in plan_waves, "wave is absent from the immutable plan")
            require(set(event["payload"]["task_ids"]) == plan_waves[wave_number], "wave tasks differ from the immutable plan")
            current_wave = wave_number
            started_waves.add(wave_number)
        elif str(event_type).startswith("worker."):
            require(status == "running", "worker event requires running state")
            require(event.get("wave") in started_waves, "worker event references an unstarted wave")
            task_id = event.get("task_id")
            require(task_id in plan_tasks, "worker event references a task absent from the immutable plan")
            require(event.get("wave") == wave_by_task[task_id] == current_wave, "worker event is outside its planned wave")
        elif event_type == "check.completed":
            require(status == "running", "check event requires running state")
            task_id = event.get("task_id")
            require(task_id in plan_tasks, "check references a task absent from the immutable plan")
            require(wave_by_task[task_id] == current_wave, "check is outside its planned wave")
            payload = event["payload"]
            require(payload["action_id"] in plan_tasks[task_id]["check_action_ids"], "check action is absent from the task plan")
            require(payload["action_sha256"] == digest(action_index[payload["action_id"]]), "check action digest differs from the reviewed registry")
            require(payload["check_id"] not in checks, "duplicate check id")
            checks[payload["check_id"]] = {"task_id": task_id, **payload}
        elif event_type == "wave.paused":
            require(status == "running", "wave pause requires running state")
            require(event.get("wave") in started_waves, "cannot pause an unstarted wave")
            wave_number = event["wave"]
            require(wave_number == current_wave, "only the current wave can pause")
            wave_tasks = plan_waves[wave_number]
            completed_tasks = set(event["payload"]["completed_task_ids"])
            failed_tasks = set(event["payload"]["failed_task_ids"])
            require(not completed_tasks.intersection(failed_tasks), "wave task cannot be both completed and failed")
            require(completed_tasks.union(failed_tasks) == wave_tasks, "wave pause must partition every planned task")
            for task_id in completed_tasks:
                worker_id = worker_by_task.get(task_id)
                require(worker_id is not None and workers[worker_id]["status"] == "passed", f"completed task {task_id} lacks a passing worker")
                passed_actions = {
                    check["action_id"] for check in checks.values()
                    if check["task_id"] == task_id and check["status"] == "passed" and check["exit_code"] == 0
                }
                require(set(plan_tasks[task_id]["check_action_ids"]) <= passed_actions, f"completed task {task_id} lacks required passing checks")
                require(any(record.get("task_id") == task_id and record.get("verdict") == "pass" for record in evidence_records.values()), f"completed task {task_id} lacks passing evidence")
            for task_id in failed_tasks:
                worker_id = worker_by_task.get(task_id)
                require(worker_id is not None and workers[worker_id]["status"] in {"failed_safe", "cancelled", "needs_human"}, f"failed task {task_id} lacks a terminal failure")
            require(set(event["payload"]["evidence_ids"]) <= set(evidence_records), "wave pause references missing evidence")
            paused_waves.add(wave_number)
            status = "paused"
            human_gate = {"required": True, "kind": "wave_continue", "decision_event_id": None}
            gate_checkpoint_event_id = event["event_id"]
            gate_subject = {"kind": "wave", "id": str(wave_number), "sha256": digest(event)}
        elif event_type == "run.paused":
            require(status == "running", "run pause requires running state")
            status = "paused"
            human_gate = {"required": True, "kind": event.get("payload", {}).get("gate_kind"), "decision_event_id": None}
            gate_checkpoint_event_id = event["event_id"]
            subject_kind = {"wave_continue": "wave", "integration": "integration", "diagnosis": "failure"}[human_gate["kind"]]
            subject_id = str(current_wave) if subject_kind == "wave" else event["event_id"]
            gate_subject = {"kind": subject_kind, "id": subject_id, "sha256": digest(event)}
        elif event_type == "run.resumed":
            require(status in {"paused", "needs_human"}, "run.resume requires a paused or needs-human state")
            require(event.get("actor", {}).get("kind") == "human", "run.resume actor must be human")
            decision = decision_records.get(event["payload"]["decision_id"])
            require(decision is not None, "run.resume references a missing human decision")
            require(decision["disposition"] in {"approve", "continue", "acknowledge"}, "run.resume decision does not authorize continuation")
            require(resume_authorizations.get(event["payload"]["decision_id"]) == event["payload"]["checkpoint_event_id"], "run.resume decision is not bound to this gate checkpoint")
            status = "running"
            human_gate = {"required": False, "kind": "none", "decision_event_id": None}
            gate_checkpoint_event_id = None
            gate_subject = None
        elif event_type == "run.needs_human":
            require(status in {"running", "paused"}, "needs-human requires an active run")
            status = "needs_human"
            human_gate = {"required": True, "kind": event.get("payload", {}).get("gate_kind"), "decision_event_id": None}
            gate_checkpoint_event_id = event["event_id"]
            subject_kind = {"wave_continue": "wave", "integration": "integration", "diagnosis": "failure"}[human_gate["kind"]]
            subject_id = str(current_wave) if subject_kind == "wave" else event["event_id"]
            gate_subject = {"kind": subject_kind, "id": subject_id, "sha256": digest(event)}
        elif event_type == "run.cancelled":
            require(status in {"planned", "running", "paused", "needs_human"}, "run cannot be cancelled from this state")
            require(event.get("actor", {}).get("kind") == "human", "run.cancel actor must be human")
            decision = decision_records.get(event["payload"]["decision_id"])
            require(decision is not None and decision["disposition"] == "cancel", "run.cancel requires a recorded cancel decision")
            status = "cancelled"
        elif event_type == "run.failed_safe":
            require(status in {"planned", "running", "paused", "needs_human"}, "run cannot fail-safe from this state")
            status = "failed_safe"
        elif event_type == "run.completed":
            require(status in {"running", "paused"}, "run completion requires an active run")
            payload = event.get("payload", {})
            require(started_waves == set(plan_waves) and paused_waves == set(plan_waves), "completion requires every planned wave to start and pause")
            require(set(worker_by_task) == set(plan_tasks), "completion requires exactly one worker for every planned task")
            require(all(worker["status"] == "passed" for worker in workers.values()), "completion requires passing workers")
            require(bool(checks) and all(check["status"] == "passed" and check["exit_code"] == 0 for check in checks.values()), "completion requires only passing checks")
            for task_id, task_record in plan_tasks.items():
                passed_actions = {check["action_id"] for check in checks.values() if check["task_id"] == task_id and check["status"] == "passed" and check["exit_code"] == 0}
                require(set(task_record["check_action_ids"]) <= passed_actions, f"completion lacks required checks for {task_id}")
            require(bool(evidence_records) and all(record["verdict"] == "pass" for record in evidence_records.values()), "completion requires only passing evidence")
            require(all(any(record.get("task_id") == task_id and record["verdict"] == "pass" for record in evidence_records.values()) for task_id in plan_tasks), "completion requires passing evidence for every planned task")
            require(bool(decision_records), "completion requires a human decision")
            require(human_gate.get("required") is False, "completion cannot bypass an outstanding human gate")
            require(set(payload.get("worker_ids", [])) == set(workers), "completion worker references are incomplete")
            require(set(payload.get("check_ids", [])) == set(checks), "completion check references are incomplete")
            require(set(payload.get("evidence_ids", [])) == set(evidence_records), "completion evidence references are incomplete")
            require(set(payload.get("decision_ids", [])) == set(decision_records), "completion decision references are incomplete")
            require(payload.get("final_wave") == len(plan_waves), "completion final wave is incorrect")
            evidence_required = set(payload["evidence_ids"])
            status = "completed"
            human_gate = {"required": False, "kind": "none", "decision_event_id": None}
        if str(event.get("type", "")).startswith("worker."):
            for field in ("task_id", "worker_id", "wave", "attempt"):
                require(field in event, f"worker event is missing {field}")
            payload = event.get("payload", {})
            for field in ("status", "provider", "branch", "worktree", "session_id", "process_id", "resume_token_sha256", "result_sha256", "event_ids", "evidence_ids"):
                require(field in payload, f"worker event payload is missing {field}")
            task = plan_tasks[event["task_id"]]
            require(payload["provider"] == task["provider"], "worker provider differs from the immutable plan")
            require(payload["branch"] == task["branch"], "worker branch differs from the immutable plan")
            require(payload["worktree"] == task["worktree"], "worker worktree differs from the immutable plan")
            previous_worker = workers.get(event["worker_id"])
            prior_for_task = worker_by_task.get(event["task_id"])
            require(prior_for_task in {None, event["worker_id"]}, "planned task is assigned to multiple workers")
            require(previous_worker is None or previous_worker["task_id"] == event["task_id"], "worker changed planned task")
            transitions = {
                "worker.prepared": ({None}, "prepared"),
                "worker.launched": ({"prepared"}, "running"),
                "worker.streamed": ({"running"}, "running"),
                "worker.interrupted": ({"running"}, "interrupted"),
                "worker.reconciled": ({"running", "interrupted", "reconciling"}, "reconciling"),
                "worker.completed": ({"running", "interrupted", "reconciling"}, None),
            }
            allowed_previous, required_status = transitions[event_type]
            previous_status = previous_worker["status"] if previous_worker else None
            require(previous_status in allowed_previous, f"illegal worker lifecycle transition for {event['worker_id']}")
            if required_status is not None:
                require(payload["status"] == required_status, f"{event_type} has an invalid worker status")
            else:
                require(payload["status"] in {"passed", "failed_safe", "cancelled", "needs_human"}, "worker.completed needs a terminal status")
                if payload["status"] == "passed":
                    require(payload["result_sha256"] is not None, "passing worker needs a result digest")
            require(event["attempt"] <= task["retry_budget"] + 1, "worker attempt exceeds the immutable retry budget")
            require(previous_worker is None or event["attempt"] >= previous_worker["attempts"], "worker attempt moved backwards")
            worker_by_task[event["task_id"]] = event["worker_id"]
            workers[event["worker_id"]] = {
                "worker_id": event["worker_id"],
                "task_id": event["task_id"],
                "provider": payload["provider"],
                "session_id": payload["session_id"],
                "process_id": payload["process_id"],
                "resume_token_sha256": payload["resume_token_sha256"],
                "status": payload["status"],
                "branch": payload["branch"],
                "worktree": payload["worktree"],
                "attempts": event["attempt"],
            }
        if event.get("type") == "decision.recorded":
            require(event.get("actor", {}).get("kind") == "human", "decision event actor must be human")
            validate_decision(
                event.get("payload", {}),
                event_actor_id=event["actor"].get("id"),
                expected_run_id=run_id,
                expected_plan_sha256=plan_sha256,
                expected_journal_head_sha256=event.get("previous_event_sha256"),
                available_evidence_ids=set(evidence_records),
            )
            require(event["payload"]["decision_id"] not in decision_records, "duplicate decision id")
            decision_records[event["payload"]["decision_id"]] = event["payload"]
            if (
                human_gate.get("required")
                and event["payload"].get("gate_kind") == human_gate.get("kind")
                and event["payload"].get("disposition") in {"approve", "continue", "acknowledge"}
            ):
                require(gate_checkpoint_event_id is not None, "human gate lacks a checkpoint")
                require(gate_subject is not None and event["payload"]["subject"] == gate_subject, "human decision targets another gate subject")
                resume_authorizations[event["payload"]["decision_id"]] = gate_checkpoint_event_id
                human_gate = {"required": False, "kind": "none", "decision_event_id": None}
        if event.get("type") == "evidence.collected":
            validate_evidence(
                event.get("payload", {}),
                expected_run_id=run_id,
                expected_plan_sha256=plan_sha256,
                expected_journal_head_sha256=event.get("previous_event_sha256"),
                project_root=project_root,
            )
            require(event["payload"]["evidence_id"] not in evidence_records, "duplicate evidence id")
            if event["payload"].get("task_id") is not None:
                require(event["payload"]["task_id"] in plan_tasks, "evidence references a task absent from the immutable plan")
                producer = event["payload"]["producer"]
                if producer["kind"] == "check":
                    require(producer["id"] in checks, "evidence references a missing check")
                    producer_check = checks[producer["id"]]
                    require(producer_check["task_id"] == event["payload"]["task_id"], "evidence check belongs to another task")
                    require(producer["commit"] == producer_check["commit"], "evidence commit differs from its producer check")
                    require(event["payload"]["check"]["name"] == producer_check["action_id"], "evidence names another check action")
                    require(event["payload"]["check"]["command_sha256"] == producer_check["action_sha256"], "evidence command digest differs from its producer check")
                    require(event["payload"]["check"]["exit_code"] == producer_check["exit_code"], "evidence exit code differs from its producer check")
            evidence_records[event["payload"]["evidence_id"]] = event["payload"]
        previous = event
    if expected_last_sequence is not None:
        require(len(events) == expected_last_sequence, "journal is truncated or has unexpected events")
    if expected_head_sha256 is not None:
        require(digest(events[-1]) == expected_head_sha256, "journal head does not match the reconciled checkpoint")
    return {
        "run_id": run_id,
        "plan_sha256": plan_sha256,
        "journal_head_sha256": digest(events[-1]),
        "journal_head_event_id": events[-1]["event_id"],
        "last_sequence": len(events),
        "status": status,
        "current_wave": current_wave,
        "workers": sorted(workers.values(), key=lambda worker: worker["worker_id"]),
        "evidence": {"required": sorted(evidence_required), "collected": sorted(evidence_records), "complete": bool(evidence_required) and evidence_required <= set(evidence_records)},
        "decisions": sorted(decision_records),
        "human_gate": human_gate,
        "reconciliation_sha256": events[-1].get("payload", {}).get("reconciliation_sha256") if status == "completed" else None,
    }


def validate_decision(
    decision: dict[str, Any],
    event_actor_id: str | None = None,
    expected_run_id: str | None = None,
    expected_plan_sha256: str | None = None,
    expected_journal_head_sha256: str | None = None,
    available_evidence_ids: set[str] | None = None,
) -> None:
    require(decision.get("schema_version") == SCHEMA_VERSION, "unknown decision schema version")
    actor = decision.get("actor", {})
    require(actor.get("kind") == "human", "decision actor must be human")
    require(bool(actor.get("session_id")), "decision needs direct session provenance")
    require(bool(decision.get("rationale")), "decision rationale is required")
    if event_actor_id is not None:
        require(actor.get("id") == event_actor_id, "decision actor does not match event actor")
    if expected_run_id is not None:
        require(decision.get("run_id") == expected_run_id, "decision belongs to another run")
    if expected_plan_sha256 is not None:
        require(decision.get("plan_sha256") == expected_plan_sha256, "decision belongs to another plan")
    if expected_journal_head_sha256 is not None:
        require(decision.get("journal_head_sha256") == expected_journal_head_sha256, "decision uses a stale journal head")
    if available_evidence_ids is not None:
        require(set(decision.get("evidence_ids", [])) <= available_evidence_ids, "decision references missing evidence")
    allowed_dispositions = {
        "run_start": {"continue", "cancel"},
        "wave_continue": {"continue", "pause", "cancel"},
        "diagnosis": {"acknowledge", "pause", "cancel", "request_changes"},
        "research_decision": {"approve", "reject", "request_changes"},
        "product_scope": {"approve", "reject", "request_changes"},
        "design_direction": {"approve", "reject", "request_changes"},
        "canonical_tokens": {"approve", "reject", "request_changes"},
        "integration": {"approve", "reject", "request_changes"},
        "evidence_acceptance": {"approve", "reject", "request_changes"},
        "release": {"approve", "reject", "request_changes"},
        "deployment": {"approve", "reject", "request_changes"},
        "pull_request_approval": {"approve", "reject", "request_changes"},
        "merge": {"approve", "reject", "request_changes"},
    }
    require(decision.get("disposition") in allowed_dispositions.get(decision.get("gate_kind"), set()), "decision disposition is invalid for its gate")


def validate_evidence(
    evidence: dict[str, Any],
    expected_run_id: str | None = None,
    expected_plan_sha256: str | None = None,
    expected_journal_head_sha256: str | None = None,
    project_root: Path | None = None,
) -> None:
    require(evidence.get("schema_version") == SCHEMA_VERSION, "unknown evidence schema version")
    require(evidence.get("builder_id") != evidence.get("evaluator_id"), "builder and evaluator must differ")
    require(bool(evidence.get("artifacts")), "evidence must include an artifact")
    if evidence.get("verdict") == "pass":
        require(evidence.get("check", {}).get("exit_code") == 0, "passing evidence needs a zero exit code")
    if expected_run_id is not None:
        require(evidence.get("run_id") == expected_run_id, "evidence belongs to another run")
    if expected_plan_sha256 is not None:
        require(evidence.get("plan_sha256") == expected_plan_sha256, "evidence belongs to another plan")
    if expected_journal_head_sha256 is not None:
        require(evidence.get("journal_head_sha256") == expected_journal_head_sha256, "evidence uses a stale journal head")
    if project_root is not None:
        root = project_root.resolve(strict=True)
        for artifact in evidence.get("artifacts", []):
            candidate = root / artifact["path"]
            resolved = candidate.resolve(strict=True)
            require(resolved == root or root in resolved.parents, "evidence artifact escapes project root")
            current = root
            for part in Path(artifact["path"]).parts:
                current = current / part
                require(not current.is_symlink(), "evidence artifact cannot follow a symlink")
            require(resolved.is_file(), "evidence artifact is not a regular file")
            require(hashlib.sha256(resolved.read_bytes()).hexdigest() == artifact["sha256"], "evidence artifact digest mismatch")


def validate_state(state: dict[str, Any], journal_projection: dict[str, Any] | None = None) -> None:
    require(state.get("schema_version") == SCHEMA_VERSION, "unknown state schema version")
    require(state.get("reducer_version") == REDUCER_VERSION, "unknown reducer version")
    workers = state.get("workers", [])
    require(len({worker["worker_id"] for worker in workers}) == len(workers), "duplicate worker id")
    require(len({worker["task_id"] for worker in workers}) == len(workers), "duplicate worker task")
    evidence = state.get("evidence", {})
    if evidence.get("complete"):
        require(set(evidence.get("required", [])) <= set(evidence.get("collected", [])), "required evidence is missing")
    gate = state.get("human_gate", {})
    if gate.get("required"):
        require(gate.get("kind") != "none" and gate.get("decision_event_id") is None, "outstanding gate is contradictory")
    else:
        require(gate.get("kind") == "none" and gate.get("decision_event_id") is None, "inactive gate is contradictory")
    if state.get("status") == "completed":
        require(evidence.get("complete") is True, "completed state needs complete evidence")
        require(all(worker.get("status") == "passed" for worker in workers), "completed state has a non-passing worker")
        require(gate.get("required") is False, "completed state has an outstanding gate")
        reconciliation = state.get("reconciliation", {})
        for axis in ("git", "worktrees", "processes", "checks", "pull_requests"):
            require(reconciliation.get(axis) == "consistent", f"completed state has {axis} drift")
        require(reconciliation.get("stale_running_count") == 0, "completed state has stale workers")
        require(state.get("reconciliation_sha256") == digest(reconciliation), "reconciliation digest does not match state")
    if journal_projection is not None:
        compared_fields = (
            "run_id",
            "plan_sha256",
            "journal_head_sha256",
            "journal_head_event_id",
            "last_sequence",
            "status",
            "current_wave",
            "workers",
            "evidence",
            "decisions",
            "human_gate",
            "reconciliation_sha256",
        )
        for field in compared_fields:
            require(state.get(field) == journal_projection.get(field), f"state field {field} differs from deterministic journal replay")


def validate_benchmark(result: dict[str, Any]) -> None:
    require(result.get("schema_version") == SCHEMA_VERSION, "unknown benchmark schema version")
    reviewers = result.get("reviewers", [])
    require(len(reviewers) >= 2, "benchmark needs at least two reviewers")
    ids = [reviewer.get("id") for reviewer in reviewers]
    require(len(ids) == len(set(ids)), "benchmark reviewer ids must be unique")
    require(all(reviewer.get("blind") and reviewer.get("independent_from_builder") for reviewer in reviewers), "benchmark reviewers must be blind and independent")
    disallowed_reviewer_ids = {result.get("operator_id"), *result.get("builder_ids", [])}
    require(not set(ids).intersection(disallowed_reviewer_ids), "reviewer cannot be an operator or builder")
    sealed_at = [datetime.fromisoformat(reviewer["sealed_at"].replace("Z", "+00:00")) for reviewer in reviewers]
    reidentified_at = datetime.fromisoformat(result["reidentified_at"].replace("Z", "+00:00"))
    require(all(sealed <= reidentified_at for sealed in sealed_at), "arm was reidentified before reviews were sealed")
    dimensions = ("correctness", "design_specificity", "interaction_quality", "accessibility", "recovery")
    for dimension in dimensions:
        values = [float(reviewer["scores"][dimension]) for reviewer in reviewers]
        if len(values) == 2:
            require(max(values) - min(values) < 2, f"dimension {dimension} requires a third reviewer")
            expected = sum(values) / 2
        else:
            ordered = sorted(values)
            expected = ordered[len(ordered) // 2]
        require(float(result["aggregate_scores"][dimension]) == expected, f"aggregate score mismatch for {dimension}")
    for name, measurement in result.get("measurements", {}).items():
        if name == "cost":
            value = measurement.get("value")
        else:
            value = measurement.get("value")
        require((value is None) != (measurement.get("unknown_reason") is None), f"measurement {name} must have a value or an unknown reason")
    if result.get("verdict") == "pass":
        require(not result.get("violations"), "passing benchmark has policy violations")
        require(not result.get("exclusions"), "passing benchmark has exclusions")
        for name, measurement in result.get("measurements", {}).items():
            require(measurement.get("value") is not None, f"passing benchmark has unknown {name}")
        require(result.get("counts", {}).get("checks", 0) > 0, "passing benchmark needs checks")
        require(result.get("counts", {}).get("evidence_items", 0) > 0, "passing benchmark needs evidence")
    require(result.get("failures_published") is True, "benchmark failures must remain publishable")
    require(bool(result.get("artifacts")), "benchmark result needs artifacts")


def validate_adapter(
    operation: dict[str, Any],
    action_registry: dict[str, Any] | None = None,
    plan: dict[str, Any] | None = None,
    project_root: Path | None = None,
    journal_projection: dict[str, Any] | None = None,
) -> None:
    request = operation.get("request", {})
    action_ids = request.get("action_ids", [])
    require(action_registry is not None, "authoritative adapter validation requires the action registry")
    require(plan is not None, "authoritative adapter validation requires the immutable plan")
    validate_schema("plan", plan)
    validate_plan(plan, project_root, action_registry, require_uncreated_worktrees=False)
    require(operation.get("run_id") == plan["run_id"], "adapter belongs to another run")
    require(request.get("plan_sha256") == digest(plan), "adapter belongs to another plan")
    task_index = {task["task_id"]: task for task in plan["tasks"]}
    require(operation.get("task_id") in task_index, "adapter task is absent from the immutable plan")
    task = task_index[operation["task_id"]]
    require(request.get("provider") == task["provider"], "adapter provider differs from the immutable plan")
    require(request.get("provider_version") == task["provider_version"], "adapter provider version differs from the immutable plan")
    require(request.get("branch") == task["branch"], "adapter branch differs from the immutable plan")
    require(request.get("worktree") == task["worktree"], "adapter worktree differs from the immutable plan")
    require(request.get("writable_paths") == task["writable_paths"], "adapter writable paths differ from the immutable plan")
    require(request.get("permission_policy_sha256") == plan["runtime_policy"]["permissions"]["policy_sha256"], "adapter permission policy differs from the immutable plan")
    require(request.get("invocation_sha256") == task["invocation_sha256"], "adapter invocation differs from the immutable plan")
    require(request.get("timeout_seconds") == task["timeout_seconds"], "adapter timeout differs from the immutable plan")
    require(set(request.get("capabilities", [])) == set(task["capability_ids"]), "adapter capabilities differ from the immutable task plan")
    allowed_actions = set(task["allowed_action_ids"]) | set(task["check_action_ids"])
    require(set(action_ids) <= allowed_actions, "adapter actions exceed the immutable task plan")
    require(request.get("action_registry_sha256") == plan["runtime_policy"]["action_registry_sha256"], "adapter action registry differs from the immutable plan")
    resolve_actions(action_ids, action_registry, request.get("action_registry_sha256", ""))
    if operation.get("operation") in {"stream", "interrupt", "resume", "reconcile", "collect"}:
        require(journal_projection is not None, "continuation adapter operation requires deterministic journal state")
        require(journal_projection.get("run_id") == plan["run_id"] and journal_projection.get("plan_sha256") == digest(plan), "adapter continuation state belongs to another run or plan")
        worker = next((record for record in journal_projection.get("workers", []) if record["worker_id"] == operation.get("worker_id") and record["task_id"] == operation.get("task_id")), None)
        require(worker is not None, "adapter continuation worker is absent from deterministic journal state")
        target = request.get("target", {})
        supplied_targets = 0
        if target.get("session_id") is not None:
            supplied_targets += 1
            require(target["session_id"] == worker.get("session_id"), "adapter session target is not recorded for this worker")
            require("session_resume" in task["capability_ids"], "task does not authorize session continuation")
        if target.get("process_id") is not None:
            supplied_targets += 1
            require(target["process_id"] == worker.get("process_id"), "adapter process target is not recorded for this worker")
            require("process_interrupt" in task["capability_ids"], "task does not authorize process targeting")
        if target.get("checkpoint_event_id") is not None or target.get("journal_head_sha256") is not None:
            supplied_targets += 1
            require(target.get("checkpoint_event_id") == journal_projection.get("journal_head_event_id") and target.get("journal_head_sha256") == journal_projection.get("journal_head_sha256"), "adapter checkpoint target is not the verified journal head")
            require("checkpoint_resume" in task["capability_ids"], "task does not authorize checkpoint continuation")
        if target.get("resume_token_sha256") is not None:
            supplied_targets += 1
            require(target["resume_token_sha256"] == worker.get("resume_token_sha256"), "adapter resume token is not recorded for this worker")
            require("session_resume" in task["capability_ids"], "task does not authorize token continuation")
        require(supplied_targets > 0, "adapter operation needs a recorded session, process, checkpoint, or resume token target")


def validate_action_registry(registry: dict[str, Any]) -> None:
    actions = registry.get("actions", [])
    ids = [action.get("id") for action in actions]
    require(len(ids) == len(set(ids)), "action registry ids must be unique")
    for action in actions:
        require(action.get("shell") is False, f"action {action.get('id')} must not use a shell")
        require(action.get("network") == "disabled", f"action {action.get('id')} expands network authority")
        authority = action.get("authority", {})
        forbidden = ("deploy", "merge", "approve", "release", "write_default_branch", "sandbox_bypass", "expand_network")
        require(not any(authority.get(key) for key in forbidden), f"action {action.get('id')} expands authority")


def resolve_actions(action_ids: list[str], registry: dict[str, Any], expected_sha256: str) -> list[dict[str, Any]]:
    validate_schema("action_registry", registry)
    validate_action_registry(registry)
    require(digest(registry) == expected_sha256, "action registry digest mismatch")
    index = {action["id"]: action for action in registry["actions"]}
    missing = sorted(set(action_ids) - set(index))
    require(not missing, f"unknown action ids: {', '.join(missing)}")
    return [index[action_id] for action_id in action_ids]


VALIDATORS = {
    "plan": validate_plan,
    "journal": validate_journal,
    "state": validate_state,
    "decision": validate_decision,
    "evidence": validate_evidence,
    "benchmark": validate_benchmark,
    "adapter": validate_adapter,
    "action_registry": validate_action_registry,
}


def validate_record(kind: str, value: Any, **context: Any) -> Any:
    """Authoritative fail-closed entry point: schema first, semantics second."""

    validate_schema(kind, value)
    if kind == "plan":
        require(context.get("action_registry") is not None, "authoritative plan validation requires the action registry")
        return validate_plan(value, context.get("project_root"), context["action_registry"])
    if kind == "journal":
        require(context.get("project_root") is not None, "authoritative journal validation requires the canonical project root")
        require(context.get("plan") is not None, "authoritative journal validation requires the immutable plan")
        require(context.get("action_registry") is not None, "authoritative journal validation requires the action registry")
        return validate_journal(
            value,
            context["plan"],
            context["action_registry"],
            expected_head_sha256=context.get("expected_head_sha256"),
            expected_last_sequence=context.get("expected_last_sequence"),
            project_root=context.get("project_root"),
        )
    if kind == "state":
        require(context.get("journal_projection") is not None, "authoritative state validation requires deterministic journal replay")
        return validate_state(value, context.get("journal_projection"))
    if kind == "evidence":
        require(context.get("project_root") is not None, "authoritative evidence validation requires the canonical project root")
        return validate_evidence(value, project_root=context.get("project_root"))
    if kind == "adapter":
        require(context.get("action_registry") is not None, "authoritative adapter validation requires the action registry")
        require(context.get("plan") is not None, "authoritative adapter validation requires the immutable plan")
        require(context.get("project_root") is not None, "authoritative adapter validation requires the canonical project root")
        return validate_adapter(value, context["action_registry"], context["plan"], context["project_root"], context.get("journal_projection"))
    return VALIDATORS[kind](value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(VALIDATORS))
    parser.add_argument("path", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--plan-path", type=Path)
    parser.add_argument("--action-registry", type=Path, default=ROOT / ".agentic/run-actions.json")
    parser.add_argument("--expected-head-sha256")
    parser.add_argument("--expected-last-sequence", type=int)
    parser.add_argument("--journal-path", type=Path)
    args = parser.parse_args()
    value = json.loads(args.path.read_text())
    action_registry = json.loads(args.action_registry.read_text())
    try:
        if args.kind == "journal":
            require(args.plan_path is not None, "--plan-path is required for a journal")
            plan = json.loads(args.plan_path.read_text())
            validate_record(
                "journal",
                value,
                plan=plan,
                action_registry=action_registry,
                expected_head_sha256=args.expected_head_sha256,
                expected_last_sequence=args.expected_last_sequence,
                project_root=args.project_root,
            )
        elif args.kind == "state":
            require(args.journal_path is not None, "--journal-path is required for authoritative state validation")
            require(args.plan_path is not None, "--plan-path is required for authoritative state validation")
            journal = json.loads(args.journal_path.read_text())
            plan = json.loads(args.plan_path.read_text())
            projection = validate_record(
                "journal",
                journal,
                plan=plan,
                action_registry=action_registry,
                expected_head_sha256=value.get("journal_head_sha256"),
                expected_last_sequence=value.get("last_sequence"),
                project_root=args.project_root,
            )
            validate_record("state", value, journal_projection=projection)
        else:
            extra_context: dict[str, Any] = {}
            if args.plan_path is not None:
                extra_context["plan"] = json.loads(args.plan_path.read_text())
            if args.kind == "adapter" and args.journal_path is not None:
                require("plan" in extra_context, "--plan-path is required with adapter journal context")
                journal = json.loads(args.journal_path.read_text())
                extra_context["journal_projection"] = validate_record(
                    "journal",
                    journal,
                    plan=extra_context["plan"],
                    action_registry=action_registry,
                    project_root=args.project_root,
                )
            validate_record(args.kind, value, project_root=args.project_root, action_registry=action_registry, **extra_context)
    except (ContractError, KeyError, TypeError, OSError) as exc:
        print(f"Product-to-Proof contract error: {exc}")
        return 1
    print(f"Product-to-Proof {args.kind} contract valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
