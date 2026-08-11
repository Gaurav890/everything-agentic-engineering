#!/usr/bin/env python3
"""Create a non-mutating, allowlisted Agency Agents review plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CAPABILITY_PATH = Path(".agentic/capabilities/agency-agents.json")
ALLOWLIST_PATH = Path(".agentic/external-agents.json")
DEFAULT_DESTINATION = Path(".agentic/vendor-review/agency-agents")
EXPECTED_REPOSITORY = "https://github.com/msitarzewski/agency-agents"
EXPECTED_COMMIT = "ebe9c99acb5c96f9468de368d8bead775387d1a7"
EXPECTED_LICENSE = "MIT"
FORBIDDEN_FLAGS = {
    "--activate", "--all", "--auto-update", "--bulk", "--division",
    "--download", "--execute", "--fetch", "--global", "--install", "--user-global",
}
WILDCARD_PATTERN = re.compile(r"[*?\[\]{}]")


class PlannerError(ValueError):
    """Raised when a request violates the selective planning contract."""


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise PlannerError(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise PlannerError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise PlannerError(f"Expected an object in {path}")
    return value


def load_contracts(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    return read_json(root / CAPABILITY_PATH), read_json(root / ALLOWLIST_PATH)


def validate_contracts(capability: dict[str, Any], allowlist: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = capability.get("source", {})
    collection = allowlist.get("collections", {}).get("agency-agents", {})
    for label, actual, expected in (
        ("capability repository", source.get("repository"), EXPECTED_REPOSITORY),
        ("capability commit", source.get("reviewed_commit"), EXPECTED_COMMIT),
        ("capability license", source.get("license"), EXPECTED_LICENSE),
        ("allowlist repository", collection.get("source_repository"), EXPECTED_REPOSITORY),
        ("allowlist commit", collection.get("reviewed_commit"), EXPECTED_COMMIT),
        ("allowlist license", collection.get("license"), EXPECTED_LICENSE),
    ):
        if actual != expected:
            errors.append(f"{label} does not match the reviewed provenance")
    if capability.get("status") != "optional":
        errors.append("capability status must remain optional")
    setup = capability.get("setup", {})
    if setup.get("automatic") is not False or setup.get("mode") != "plan_only":
        errors.append("capability setup must remain non-automatic and plan-only")
    if capability.get("authority", {}).get("default") != "none":
        errors.append("capability authority must default to none")
    policy = allowlist.get("policy", {})
    for key, expected in {
        "automatic_external_install": False,
        "bulk_install": False,
        "external_source_is_untrusted": True,
        "activation_changes_runtime_authority": False,
    }.items():
        if policy.get(key) is not expected:
            errors.append(f"unsafe or missing allowlist policy: {key}")
    specialists = allowlist.get("specialists")
    if not isinstance(specialists, list) or not specialists:
        errors.append("reviewed specialist allowlist is missing or empty")
        return errors
    seen: set[str] = set()
    for item in specialists:
        if not isinstance(item, dict):
            errors.append("every allowlisted specialist must be an object")
            continue
        agent_id = item.get("id")
        source_path = item.get("source_path")
        if not isinstance(agent_id, str) or not agent_id:
            errors.append("every allowlisted specialist needs a non-empty id")
        elif agent_id in seen:
            errors.append(f"duplicate allowlisted specialist: {agent_id}")
        else:
            seen.add(agent_id)
        if item.get("source_collection") != "agency-agents":
            errors.append(f"{agent_id or 'unknown'} has an unexpected source collection")
        if (not isinstance(source_path, str) or not source_path.endswith(".md")
                or Path(source_path).is_absolute() or ".." in Path(source_path).parts):
            errors.append(f"{agent_id or 'unknown'} has an unsafe source path")
    return errors


def allowlist_index(allowlist: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in allowlist.get("specialists", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)}


def reject_forbidden_arguments(arguments: list[str]) -> None:
    for argument in arguments:
        flag = argument.split("=", 1)[0]
        if flag in FORBIDDEN_FLAGS:
            raise PlannerError(
                f"{flag} is forbidden: select reviewed agents individually and keep this operation plan-only"
            )


def selected_agent_ids(values: list[str]) -> list[str]:
    result: list[str] = []
    for raw_value in values:
        agent_id = raw_value.strip()
        if not agent_id:
            raise PlannerError("--agent values cannot be empty")
        if WILDCARD_PATTERN.search(agent_id):
            raise PlannerError("wildcards are forbidden; select each reviewed agent id explicitly")
        if agent_id not in result:
            result.append(agent_id)
    return result


def project_local_destination(root: Path, value: str) -> str:
    candidate = Path(value).expanduser()
    resolved_root = root.resolve()
    resolved = candidate.resolve() if candidate.is_absolute() else (resolved_root / candidate).resolve()
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError as error:
        raise PlannerError("destination must remain inside the project; user-global paths are forbidden") from error
    if not relative.parts:
        raise PlannerError("project root is too broad for an external-source review destination")
    if relative.parts[0] not in {".agentic", ".claude", ".codex"}:
        raise PlannerError("destination must use a project-local .agentic, .claude, or .codex review path")
    return relative.as_posix()


def build_plan(root: Path, agent_ids: list[str], destination: str) -> dict[str, Any]:
    capability, allowlist = load_contracts(root)
    errors = validate_contracts(capability, allowlist)
    if errors:
        raise PlannerError("; ".join(errors))
    index = allowlist_index(allowlist)
    unknown = [agent_id for agent_id in agent_ids if agent_id not in index]
    if unknown:
        raise PlannerError("not in the reviewed local allowlist: " + ", ".join(sorted(unknown)))
    destination_root = project_local_destination(root, destination)
    items: list[dict[str, Any]] = []
    for agent_id in agent_ids:
        specialist = index[agent_id]
        source_path = specialist["source_path"]
        items.append({
            "agent_id": agent_id,
            "name": specialist["name"],
            "source_path": source_path,
            "source_url": f"{EXPECTED_REPOSITORY}/blob/{EXPECTED_COMMIT}/{source_path}",
            "pinned_commit": EXPECTED_COMMIT,
            "proposed_destination": (Path(destination_root) / Path(source_path).parent / f"{agent_id}.md").as_posix(),
            "destination_state": "inactive_review_staging",
            "checksum": {
                "algorithm": "sha256", "verification_required": True, "expected": None,
                "status": "record_after_separately_approved_fetch_before_diff_or_install",
            },
            "conversion_required": True,
            "activation_planned": False,
        })
    return {
        "schema_version": 1,
        "capability_id": "agency-agents",
        "mode": "plan_only",
        "status": "human_review_required",
        "selected_agent_ids": agent_ids,
        "destination_root": destination_root,
        "provenance": {
            "repository": EXPECTED_REPOSITORY, "reviewed_commit": EXPECTED_COMMIT,
            "license": EXPECTED_LICENSE, "upstream_content_trust": "untrusted_data",
        },
        "items": items,
        "review_sequence": [
            "Obtain separate human approval before any network fetch.",
            "Fetch only each exact blob at the pinned commit into an isolated temporary location.",
            "Compute SHA-256 and compare it with an independently recorded expected checksum.",
            "Review the complete diff as untrusted data; reject embedded instructions requesting broader authority.",
            "Back up every existing project-local destination before a separately approved write.",
            "Convert explicitly for one target runtime and re-review the converted diff.",
            "Activate only through a separate task and human approval after tests pass.",
        ],
        "backup": {"required_before_future_write": True, "scope": "exact project-local destinations only", "performed": False},
        "rollback": [
            "Discard this plan while no files have been fetched or written.",
            "If a later installation is approved, restore the exact pre-change backup.",
            "Remove only files proven by that installation's manifest to have been newly added.",
            "Deactivate the local contract separately; never infer deactivation from file removal.",
        ],
        "safeguards": {
            "explicit_allowlist_only": True, "bulk_install_allowed": False,
            "division_install_allowed": False, "wildcards_allowed": False,
            "user_global_destination_allowed": False, "auto_update_allowed": False,
        },
        "mutation_performed": False, "network_used": False, "download_performed": False,
        "external_code_executed": False, "conversion_performed": False,
        "activation_performed": False, "authority_changed": False,
    }


def doctor(root: Path) -> dict[str, Any]:
    capability, allowlist = load_contracts(root)
    errors = validate_contracts(capability, allowlist)
    index = allowlist_index(allowlist)
    return {
        "schema_version": 1, "capability_id": "agency-agents",
        "status": "fail" if errors else "pass", "eligible_agent_count": len(index),
        "eligible_agent_ids": sorted(index),
        "provenance": {"repository": EXPECTED_REPOSITORY, "reviewed_commit": EXPECTED_COMMIT, "license": EXPECTED_LICENSE},
        "default_destination": DEFAULT_DESTINATION.as_posix(), "errors": errors,
        "warnings": ["The reviewed allowlist is a routing contract, not approval to fetch or install upstream files."],
        "mutation_performed": False, "network_used": False,
        "external_code_executed": False, "activation_performed": False, "authority_changed": False,
    }


def parser() -> argparse.ArgumentParser:
    value = SafeArgumentParser(description=__doc__)
    value.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    commands = value.add_subparsers(dest="command", required=True, parser_class=SafeArgumentParser)
    plan = commands.add_parser("plan", help="Create a read-only selective review plan")
    plan.add_argument("--agent", action="append", required=True, help="Reviewed agent id; repeat for each explicit selection")
    plan.add_argument("--destination", default=DEFAULT_DESTINATION.as_posix())
    plan.add_argument("--json", action="store_true")
    check = commands.add_parser("doctor", help="Validate provenance and safety policy")
    check.add_argument("--json", action="store_true")
    return value


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        reject_forbidden_arguments(arguments)
        args = parser().parse_args(arguments)
        root = Path(args.root).resolve()
        payload = (build_plan(root, selected_agent_ids(args.agent), args.destination)
                   if args.command == "plan" else doctor(root))
        if args.json:
            print(json.dumps(payload, indent=2))
        elif args.command == "plan":
            print("Agency Agents selective review plan")
            for item in payload["items"]:
                print(f"  - {item['agent_id']}: {item['source_path']} -> {item['proposed_destination']}")
            print("No download, installation, conversion, execution, activation, or authority change occurred.")
        else:
            print(f"Agency Agents planner doctor: {payload['status'].upper()}")
            print(f"Reviewed eligible agents: {payload['eligible_agent_count']}")
            for error in payload["errors"]:
                print(f"ERROR: {error}")
        return 1 if payload.get("errors") else 0
    except (PlannerError, OSError) as error:
        print(f"Agency Agents planner error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
