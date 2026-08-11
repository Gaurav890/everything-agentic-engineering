#!/usr/bin/env python3
"""Explain capability fit without installing, enabling, or executing it."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_DIR = ROOT / ".agentic" / "capabilities"
PROJECT_PATH = ROOT / ".agentic" / "project.json"
PROFILES_DIR = ROOT / ".agentic" / "profiles"
TASKS_PATH = ROOT / "docs" / "40-execution" / "TASKS.jsonl"

TOP_LEVEL_KEYS = {
    "schema_version",
    "id",
    "kind",
    "display_name",
    "status",
    "summary",
    "source",
    "recommend_when",
    "authority",
    "setup",
    "rollback",
    "risks",
}
SOURCE_KEYS = {"repository", "reviewed_commit", "license", "reviewed_at"}
RECOMMEND_KEYS = {
    "profiles_any_of",
    "task_terms_any_of",
    "task_owners_any_of",
    "file_patterns_any_of",
}
AUTHORITY_KEYS = {"default", "possible", "forbidden"}
SETUP_KEYS = {"automatic", "mode", "adapter", "detect"}
KINDS = {"built_in", "runtime", "external_collection", "skill", "integration", "tool", "service"}
STATUSES = {"built_in", "optional", "blocked"}
DECISION_STATES = {"built_in", "recommended", "optional", "missing", "blocked"}
ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
COMMAND_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*")


class CapabilityError(ValueError):
    """Raised when a capability contract is unsafe or inconsistent."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError as error:
        raise CapabilityError(f"Missing configuration: {path.relative_to(ROOT)}") from error
    except json.JSONDecodeError as error:
        raise CapabilityError(f"Invalid JSON in {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise CapabilityError(f"Expected an object in {path.relative_to(ROOT)}")
    return value


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing or unknown:
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if unknown:
            details.append("unknown " + ", ".join(unknown))
        raise CapabilityError(f"{label} has invalid fields: {'; '.join(details)}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CapabilityError(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise CapabilityError(f"{label} must be a list of non-empty strings")
    if nonempty and not value:
        raise CapabilityError(f"{label} must not be empty")
    if len(value) != len(set(value)):
        raise CapabilityError(f"{label} must not contain duplicates")
    return value


def _safe_relative_path(raw: str, label: str) -> Path:
    value = Path(raw)
    if value.is_absolute() or ".." in value.parts:
        raise CapabilityError(f"{label} must be a safe project-relative path")
    return value


def validate_manifest(manifest: dict[str, Any], path: Path, root: Path = ROOT) -> None:
    label = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    _require_exact_keys(manifest, TOP_LEVEL_KEYS, label)
    if manifest["schema_version"] != 1:
        raise CapabilityError(f"{label} uses an unsupported schema_version")

    capability_id = _require_string(manifest["id"], f"{label}.id")
    if ID_PATTERN.fullmatch(capability_id) is None:
        raise CapabilityError(f"{label}.id must use lowercase kebab-case")
    if path.stem != capability_id:
        raise CapabilityError(f"{label}.id must match its filename")
    if manifest["kind"] not in KINDS:
        raise CapabilityError(f"{label}.kind must be one of: {', '.join(sorted(KINDS))}")
    if manifest["status"] not in STATUSES:
        raise CapabilityError(f"{label}.status must be one of: {', '.join(sorted(STATUSES))}")
    if (manifest["kind"] == "built_in") != (manifest["status"] == "built_in"):
        raise CapabilityError(f"{label}.kind and status must agree on built_in")
    _require_string(manifest["display_name"], f"{label}.display_name")
    _require_string(manifest["summary"], f"{label}.summary")

    source = manifest["source"]
    if not isinstance(source, dict):
        raise CapabilityError(f"{label}.source must be an object")
    _require_exact_keys(source, SOURCE_KEYS, f"{label}.source")
    repository = _require_string(source["repository"], f"{label}.source.repository")
    if not repository.startswith("https://"):
        raise CapabilityError(f"{label}.source.repository must use https")
    commit = _require_string(source["reviewed_commit"], f"{label}.source.reviewed_commit")
    if SHA_PATTERN.fullmatch(commit) is None:
        raise CapabilityError(f"{label}.source.reviewed_commit must be a full lowercase commit SHA")
    _require_string(source["license"], f"{label}.source.license")
    reviewed_at = _require_string(source["reviewed_at"], f"{label}.source.reviewed_at")
    try:
        date.fromisoformat(reviewed_at)
    except ValueError as error:
        raise CapabilityError(f"{label}.source.reviewed_at must use YYYY-MM-DD") from error

    recommend = manifest["recommend_when"]
    if not isinstance(recommend, dict):
        raise CapabilityError(f"{label}.recommend_when must be an object")
    _require_exact_keys(recommend, RECOMMEND_KEYS, f"{label}.recommend_when")
    for key in sorted(RECOMMEND_KEYS):
        _require_string_list(recommend[key], f"{label}.recommend_when.{key}")
    for pattern in recommend["file_patterns_any_of"]:
        _safe_relative_path(pattern, f"{label}.recommend_when.file_patterns_any_of")

    authority = manifest["authority"]
    if not isinstance(authority, dict):
        raise CapabilityError(f"{label}.authority must be an object")
    _require_exact_keys(authority, AUTHORITY_KEYS, f"{label}.authority")
    if authority["default"] != "none":
        raise CapabilityError(f"{label}.authority.default must be 'none'")
    _require_string_list(authority["possible"], f"{label}.authority.possible")
    _require_string_list(authority["forbidden"], f"{label}.authority.forbidden", nonempty=True)

    setup = manifest["setup"]
    if not isinstance(setup, dict):
        raise CapabilityError(f"{label}.setup must be an object")
    _require_exact_keys(setup, SETUP_KEYS, f"{label}.setup")
    if setup["automatic"] is not False:
        raise CapabilityError(f"{label}.setup.automatic must be false")
    if setup["mode"] != "plan_only":
        raise CapabilityError(f"{label}.setup.mode must be 'plan_only'")
    adapter = setup["adapter"]
    if adapter is not None:
        if not isinstance(adapter, str):
            raise CapabilityError(f"{label}.setup.adapter must be a path or null")
        adapter_path = _safe_relative_path(adapter, f"{label}.setup.adapter")
        if adapter_path.parts[:2] != ("scripts", "capability_adapters") or adapter_path.suffix != ".py":
            raise CapabilityError(f"{label}.setup.adapter must be a Python file under scripts/capability_adapters/")
        if not (root / adapter_path).is_file():
            raise CapabilityError(f"{label}.setup.adapter does not exist: {adapter}")
    elif manifest["status"] != "built_in":
        raise CapabilityError(f"{label}.setup.adapter is required for non-built-in capabilities")

    detect = setup["detect"]
    if not isinstance(detect, list) or not detect:
        raise CapabilityError(f"{label}.setup.detect must be a non-empty list")
    for number, check in enumerate(detect, start=1):
        check_label = f"{label}.setup.detect[{number}]"
        if not isinstance(check, dict):
            raise CapabilityError(f"{check_label} must be an object")
        _require_exact_keys(check, {"type", "value"}, check_label)
        check_type = check["type"]
        value = _require_string(check["value"], f"{check_label}.value")
        if check_type == "path":
            _safe_relative_path(value, f"{check_label}.value")
        elif check_type == "command":
            if COMMAND_PATTERN.fullmatch(value) is None:
                raise CapabilityError(f"{check_label}.value must be a command name without a path")
        else:
            raise CapabilityError(f"{check_label}.type must be 'path' or 'command'")

    _require_string_list(manifest["rollback"], f"{label}.rollback", nonempty=True)
    _require_string_list(manifest["risks"], f"{label}.risks", nonempty=True)


def load_manifests(root: Path = ROOT) -> list[dict[str, Any]]:
    directory = root / ".agentic" / "capabilities"
    if not directory.is_dir():
        raise CapabilityError("Missing capability manifest directory: .agentic/capabilities")
    manifests: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.json")):
        manifest = _read_json(path) if root == ROOT else _read_json_at(path, root)
        validate_manifest(manifest, path, root)
        if manifest["id"] in seen:
            raise CapabilityError(f"Duplicate capability id: {manifest['id']}")
        seen.add(manifest["id"])
        manifests.append(manifest)
    if not manifests:
        raise CapabilityError("No capability manifests found in .agentic/capabilities")
    return manifests


def _read_json_at(path: Path, root: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise CapabilityError(f"Cannot read {path.relative_to(root)}: {error}") from error
    if not isinstance(value, dict):
        raise CapabilityError(f"Expected an object in {path.relative_to(root)}")
    return value


def _expand_profiles(selected: list[str], root: Path) -> list[str]:
    profiles: dict[str, dict[str, Any]] = {}
    for path in sorted((root / ".agentic" / "profiles").glob("*.json")):
        profile = _read_json_at(path, root)
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not profile_id:
            raise CapabilityError(f"Profile has no id: {path.relative_to(root)}")
        profiles[profile_id] = profile

    resolved: list[str] = []
    visiting: set[str] = set()

    def visit(profile_id: str) -> None:
        if profile_id not in profiles:
            raise CapabilityError(f"Unknown project profile: {profile_id}")
        if profile_id in visiting:
            raise CapabilityError(f"Circular profile dependency at: {profile_id}")
        if profile_id in resolved:
            return
        visiting.add(profile_id)
        dependencies = profiles[profile_id].get("requires", [])
        if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
            raise CapabilityError(f"Profile {profile_id} has invalid dependencies")
        for dependency in dependencies:
            visit(dependency)
        visiting.remove(profile_id)
        resolved.append(profile_id)

    for selected_id in selected:
        visit(selected_id)
    return resolved


def active_profiles(root: Path = ROOT) -> list[str]:
    project = _read_json_at(root / ".agentic" / "project.json", root)
    selected = project.get("profiles")
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        raise CapabilityError(".agentic/project.json profiles must be a string list")
    return _expand_profiles(selected, root)


def load_task(task_id: str | None, root: Path = ROOT) -> dict[str, Any] | None:
    if task_id is None:
        return None
    for number, line in enumerate((root / "docs" / "40-execution" / "TASKS.jsonl").read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError as error:
            raise CapabilityError(f"Invalid task JSON on line {number}: {error}") from error
        if task.get("id") == task_id:
            return task
    raise CapabilityError(f"Task not found: {task_id}")


def detect_capability(manifest: dict[str, Any], root: Path = ROOT) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    for check in manifest["setup"]["detect"]:
        if check["type"] == "path":
            present = (root / check["value"]).exists()
        else:
            present = shutil.which(check["value"]) is not None
        results.append({"type": check["type"], "value": check["value"], "present": present})
    return all(item["present"] for item in results), results


def _task_text(task: dict[str, Any] | None) -> str:
    if task is None:
        return ""
    fields: list[Any] = [
        task.get("title", ""),
        task.get("goal", ""),
        task.get("notes", ""),
        *task.get("verification", []),
        *task.get("requirement_ids", []),
        *task.get("acceptance_ids", []),
        *task.get("specialist_ids", []),
    ]
    return " ".join(str(item) for item in fields).lower()


def recommendation_evidence(
    manifest: dict[str, Any], profiles: Iterable[str], task: dict[str, Any] | None
) -> list[str]:
    rules = manifest["recommend_when"]
    active = set(profiles)
    evidence: list[str] = []
    matching_profiles = sorted(active.intersection(rules["profiles_any_of"]))
    if matching_profiles:
        evidence.append("active profile: " + ", ".join(matching_profiles))

    haystack = _task_text(task)
    matching_terms = sorted(term for term in rules["task_terms_any_of"] if term.lower() in haystack)
    if matching_terms:
        evidence.append("task evidence: " + ", ".join(matching_terms))

    if task is not None and task.get("owner") in rules["task_owners_any_of"]:
        evidence.append(f"task owner: {task['owner']}")

    matching_files: set[str] = set()
    if task is not None:
        for path in task.get("files_owned", []):
            for pattern in rules["file_patterns_any_of"]:
                if fnmatch.fnmatch(path, pattern):
                    matching_files.add(path)
    if matching_files:
        evidence.append("owned files: " + ", ".join(sorted(matching_files)))
    return evidence


def decide(
    manifest: dict[str, Any], profiles: list[str], task: dict[str, Any] | None, root: Path = ROOT
) -> dict[str, Any]:
    present, detection = detect_capability(manifest, root)
    evidence = recommendation_evidence(manifest, profiles, task)
    baseline = manifest["status"]

    if baseline == "blocked":
        state = "blocked"
        rationale = ["The reviewed capability contract explicitly blocks use."]
        next_action = "Do not use it. Resolve the documented risk through human review before changing this contract."
    elif baseline == "built_in" and present:
        state = "built_in"
        rationale = ["The capability is part of the repository and its local detection checks passed."]
        rationale.extend(evidence)
        next_action = "Use the committed local capability within the repository's existing authority."
    elif baseline == "built_in":
        state = "missing"
        rationale = ["A built-in capability is absent or incomplete according to its local detection checks."]
        next_action = "Restore the committed repository files; do not replace them with an external installation."
    elif evidence and present:
        state = "recommended"
        rationale = [*evidence, "The capability's non-executing detection checks passed."]
        next_action = "Review the capability contract and invoke its committed adapter manually if the task owner accepts the stated risks."
    elif evidence:
        state = "missing"
        rationale = [*evidence, "One or more non-executing detection checks did not find the capability."]
        next_action = "Review the plan-only adapter and request explicit human approval for any separate installation or authority change."
    else:
        state = "optional"
        rationale = ["Current project profiles and task evidence do not justify this capability."]
        next_action = "Keep it inactive. Reassess only when a concrete task or selected profile supplies matching evidence."

    if state not in DECISION_STATES:  # pragma: no cover - defensive assertion
        raise CapabilityError(f"Internal invalid decision state: {state}")
    return {
        "id": manifest["id"],
        "display_name": manifest["display_name"],
        "kind": manifest["kind"],
        "state": state,
        "present": present,
        "rationale": rationale,
        "safe_next_action": next_action,
        "authority": manifest["authority"],
        "setup": {
            "automatic": False,
            "mode": "plan_only",
            "adapter": manifest["setup"]["adapter"],
        },
        "detection": detection,
        "risks": manifest["risks"],
        "rollback": manifest["rollback"],
        "source": manifest["source"],
    }


def build_report(task_id: str | None = None, root: Path = ROOT) -> dict[str, Any]:
    profiles = active_profiles(root)
    task = load_task(task_id, root)
    decisions = [decide(manifest, profiles, task, root) for manifest in load_manifests(root)]
    return {
        "schema_version": 1,
        "mutation_performed": False,
        "active_profiles": profiles,
        "task": None if task is None else {"id": task["id"], "title": task.get("title", "")},
        "capabilities": decisions,
    }


def _select(report: dict[str, Any], capability_id: str | None) -> list[dict[str, Any]]:
    decisions = report["capabilities"]
    if capability_id is None:
        return decisions
    selected = [item for item in decisions if item["id"] == capability_id]
    if not selected:
        raise CapabilityError(f"Capability not found: {capability_id}")
    return selected


def _print_decisions(report: dict[str, Any], decisions: list[dict[str, Any]]) -> None:
    task = report["task"]
    print("Capability decisions (read-only)")
    print("Profiles: " + (", ".join(report["active_profiles"]) or "none"))
    print("Task: " + (f"{task['id']} — {task['title']}" if task else "project profiles only"))
    print()
    for item in decisions:
        print(f"{item['id']}: {item['state'].upper()}")
        print(f"  {item['display_name']} ({item['kind']})")
        print(
            "  source: "
            f"{item['source']['repository']} @ {item['source']['reviewed_commit'][:12]} "
            f"(reviewed {item['source']['reviewed_at']})"
        )
        for reason in item["rationale"]:
            print(f"  why: {reason}")
        print(f"  next: {item['safe_next_action']}")
        print("  authority: none by default")
        if item["authority"]["possible"]:
            print("  possible only after separate approval: " + ", ".join(item["authority"]["possible"]))
        print("  always forbidden here: " + ", ".join(item["authority"]["forbidden"]))
        for risk in item["risks"]:
            print(f"  risk: {risk}")
        for step in item["rollback"]:
            print(f"  rollback: {step}")
        print()
    print("No installation, execution, authentication, permission, provider, model, MCP, deployment, approval, or merge change was performed.")


def _emit(report: dict[str, Any], decisions: list[dict[str, Any]], as_json: bool) -> None:
    if as_json:
        payload = dict(report)
        payload["capabilities"] = decisions
        print(json.dumps(payload, indent=2))
    else:
        _print_decisions(report, decisions)


def command_list(args: argparse.Namespace, root: Path) -> int:
    report = build_report(args.task, root)
    _emit(report, report["capabilities"], args.json)
    return 0


def command_show(args: argparse.Namespace, root: Path) -> int:
    report = build_report(args.task, root)
    _emit(report, _select(report, args.capability), args.json)
    return 0


def command_plan(args: argparse.Namespace, root: Path) -> int:
    report = build_report(args.task, root)
    _emit(report, _select(report, args.capability), args.json)
    return 0


def command_doctor(args: argparse.Namespace, root: Path) -> int:
    report = build_report(None, root)
    decisions = report["capabilities"]
    _emit(report, decisions, args.json)
    broken_built_ins = [item["id"] for item in decisions if item["state"] == "missing" and item["kind"] == "built_in"]
    if broken_built_ins and not args.json:
        print("Doctor result: built-in capability attention required: " + ", ".join(broken_built_ins))
    return 1 if broken_built_ins else 0


def _common_flags(parser: argparse.ArgumentParser, *, task: bool = True) -> None:
    if task:
        parser.add_argument("--task", metavar="T-###", help="Use durable task evidence when deciding")
    parser.add_argument("--json", action="store_true", help="Emit stable machine-readable output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List all capability decisions")
    _common_flags(list_parser)
    list_parser.set_defaults(func=command_list)
    show_parser = subparsers.add_parser("show", help="Explain one capability")
    show_parser.add_argument("capability")
    _common_flags(show_parser)
    show_parser.set_defaults(func=command_show)
    plan_parser = subparsers.add_parser("plan", help="Plan the smallest justified capability set")
    plan_parser.add_argument("capability", nargs="?")
    _common_flags(plan_parser)
    plan_parser.set_defaults(func=command_plan)
    doctor_parser = subparsers.add_parser("doctor", help="Validate contracts and detect local availability")
    _common_flags(doctor_parser, task=False)
    doctor_parser.set_defaults(func=command_doctor)
    return parser


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    try:
        args = build_parser().parse_args(argv)
        return args.func(args, root)
    except CapabilityError as error:
        print(f"Capability error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
