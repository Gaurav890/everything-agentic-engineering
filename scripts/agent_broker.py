#!/usr/bin/env python3
"""Discover, route, and explicitly activate reviewed specialist contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / ".agentic" / "external-agents.json"
PROJECT_PATH = ROOT / ".agentic" / "project.json"
TASKS_PATH = ROOT / "docs" / "40-execution" / "TASKS.jsonl"

sys.path.insert(0, str(ROOT / "scripts"))
import profile_engine  # noqa: E402


class BrokerError(ValueError):
    """Raised when specialist policy or requested routing is invalid."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise BrokerError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise BrokerError(f"Expected an object in {path}")
    return value


def available_profile_ids(root: Path) -> set[str]:
    return {path.stem for path in (root / ".agentic" / "profiles").glob("*.json")}


def validate_manifest(manifest: dict[str, Any], root: Path = ROOT) -> None:
    if manifest.get("schema_version") != 1:
        raise BrokerError("Unsupported external-agent schema version")

    policy = manifest.get("policy")
    if not isinstance(policy, dict):
        raise BrokerError("External-agent policy must be an object")
    required_safe_policy = {
        "automatic_external_install": False,
        "bulk_install": False,
        "external_source_is_untrusted": True,
        "local_contract_first": True,
        "single_accountable_owner": True,
        "independent_evaluator": True,
        "activation_requires_confirmation": True,
        "activation_changes_runtime_authority": False,
    }
    for key, expected in required_safe_policy.items():
        if policy.get(key) is not expected:
            raise BrokerError(f"Unsafe or missing external-agent policy: {key}")

    collections = manifest.get("collections")
    specialists = manifest.get("specialists")
    if not isinstance(collections, dict) or not collections:
        raise BrokerError("At least one external-agent collection is required")
    if not isinstance(specialists, list) or not specialists:
        raise BrokerError("At least one specialist contract is required")

    profile_ids = available_profile_ids(root)
    seen: set[str] = set()
    allowed_activation = {
        "recommended_contract",
        "risk_routed_contract",
        "profile_routed_contract",
        "explicit_or_incident_contract",
    }
    for item in specialists:
        if not isinstance(item, dict):
            raise BrokerError("Every specialist must be an object")
        specialist_id = item.get("id")
        if not isinstance(specialist_id, str) or not specialist_id:
            raise BrokerError("Every specialist needs a non-empty id")
        if specialist_id in seen:
            raise BrokerError(f"Duplicate specialist id: {specialist_id}")
        seen.add(specialist_id)

        collection_id = item.get("source_collection")
        if collection_id not in collections:
            raise BrokerError(f"Unknown source collection for {specialist_id}")
        source_path = item.get("source_path")
        if (
            not isinstance(source_path, str)
            or not source_path.endswith(".md")
            or source_path.startswith("/")
            or ".." in Path(source_path).parts
        ):
            raise BrokerError(f"Unsafe source path for {specialist_id}")
        if item.get("activation") not in allowed_activation:
            raise BrokerError(f"Invalid activation mode for {specialist_id}")
        if not isinstance(item.get("required_review_when_matched"), bool):
            raise BrokerError(f"Missing required-review policy for {specialist_id}")
        if not isinstance(item.get("priority"), int):
            raise BrokerError(f"Missing numeric priority for {specialist_id}")

        profiles = item.get("profiles_any_of")
        if not isinstance(profiles, list) or not profiles:
            raise BrokerError(f"Missing profile routing for {specialist_id}")
        unknown_profiles = set(profiles).difference(profile_ids)
        if unknown_profiles:
            raise BrokerError(
                f"Unknown profiles for {specialist_id}: {', '.join(sorted(unknown_profiles))}"
            )

        for field in ("domains", "local_roles", "deliverables"):
            value = item.get(field)
            if not isinstance(value, list) or not value or not all(
                isinstance(entry, str) and entry.strip() for entry in value
            ):
                raise BrokerError(f"{specialist_id} requires non-empty {field}")
        if not item.get("trigger_terms") and not item.get("trigger_paths"):
            raise BrokerError(f"{specialist_id} has no routing triggers")
        if not isinstance(item.get("when_not_to_use"), str) or not item["when_not_to_use"].strip():
            raise BrokerError(f"{specialist_id} needs a when-not-to-use rule")


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    manifest = read_json(root / ".agentic" / "external-agents.json")
    validate_manifest(manifest, root)
    return manifest


def specialist_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in manifest["specialists"]}


def source_url(item: dict[str, Any], manifest: dict[str, Any]) -> str:
    collection = manifest["collections"][item["source_collection"]]
    return (
        f"{collection['source_repository']}/blob/"
        f"{collection['reviewed_commit']}/{item['source_path']}"
    )


def load_project(root: Path = ROOT) -> dict[str, Any]:
    project = read_json(root / ".agentic" / "project.json")
    profiles = project.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise BrokerError("Project manifest needs at least one profile")
    specialists = project.get("specialists", [])
    if not isinstance(specialists, list) or not all(isinstance(item, str) for item in specialists):
        raise BrokerError("Project specialists must be a string list")
    return project


def resolved_profiles(project: dict[str, Any], root: Path = ROOT) -> list[str]:
    original_root = profile_engine.ROOT
    original_config = profile_engine.CONFIG_DIR
    original_profiles = profile_engine.PROFILES_DIR
    original_project = profile_engine.PROJECT_PATH
    original_resources = profile_engine.RESOURCES_PATH
    original_mcp = profile_engine.MCP_PATH
    try:
        profile_engine.ROOT = root
        profile_engine.CONFIG_DIR = root / ".agentic"
        profile_engine.PROFILES_DIR = root / ".agentic" / "profiles"
        profile_engine.PROJECT_PATH = root / ".agentic" / "project.json"
        profile_engine.RESOURCES_PATH = root / ".agentic" / "resources.json"
        profile_engine.MCP_PATH = root / ".mcp.json"
        return profile_engine.resolve(project["profiles"])["resolved_profiles"]
    finally:
        profile_engine.ROOT = original_root
        profile_engine.CONFIG_DIR = original_config
        profile_engine.PROFILES_DIR = original_profiles
        profile_engine.PROJECT_PATH = original_project
        profile_engine.RESOURCES_PATH = original_resources
        profile_engine.MCP_PATH = original_mcp


def load_tasks(root: Path = ROOT) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for number, line in enumerate(
        (root / "docs" / "40-execution" / "TASKS.jsonl").read_text().splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError as error:
            raise BrokerError(f"Invalid task JSON on line {number}: {error}") from error
        if not isinstance(task, dict) or not task.get("id"):
            raise BrokerError(f"Invalid task record on line {number}")
        tasks.append(task)
    return tasks


def get_task(task_id: str, root: Path = ROOT) -> dict[str, Any]:
    for task in load_tasks(root):
        if task["id"] == task_id:
            return task
    raise BrokerError(f"Task not found: {task_id}")


def task_search_text(task: dict[str, Any]) -> str:
    fields: list[str] = []
    for key in ("title", "goal", "notes", "owner", "risk"):
        value = task.get(key)
        if isinstance(value, str):
            fields.append(value)
    for key in ("verification", "files_owned", "requirement_ids", "acceptance_ids"):
        value = task.get(key, [])
        if isinstance(value, list):
            fields.extend(str(item) for item in value)
    return "\n".join(fields).casefold()


def path_matches(pattern: str, files: Iterable[str]) -> bool:
    normalized = pattern.casefold().rstrip("*")
    return any(normalized in file.casefold() for file in files)


def recommend_for_task(
    task: dict[str, Any],
    manifest: dict[str, Any],
    active_profiles: Iterable[str],
    activated_ids: Iterable[str],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    index = specialist_index(manifest)
    explicit = task.get("specialist_ids", [])
    if not isinstance(explicit, list) or not all(isinstance(item, str) for item in explicit):
        raise BrokerError("Task specialist_ids must be a string list")
    unknown = set(explicit).difference(index)
    if unknown:
        raise BrokerError(f"Task references unknown specialists: {', '.join(sorted(unknown))}")

    text = task_search_text(task)
    files = [str(item) for item in task.get("files_owned", [])]
    active = set(active_profiles)
    activated = set(activated_ids)
    candidates: list[dict[str, Any]] = []

    for item in manifest["specialists"]:
        specialist_id = item["id"]
        explicit_match = specialist_id in explicit
        profile_match = bool(active.intersection(item["profiles_any_of"]))
        if not profile_match and not explicit_match:
            continue

        matched_terms = sorted(
            term for term in item.get("trigger_terms", []) if term.casefold() in text
        )
        matched_paths = sorted(
            pattern
            for pattern in item.get("trigger_paths", [])
            if path_matches(pattern, files)
        )
        if not explicit_match and not matched_terms and not matched_paths:
            continue

        score = item["priority"]
        score += len(matched_terms) * 12
        score += len(matched_paths) * 7
        score += 5 if specialist_id in activated else 0
        score += 1000 if explicit_match else 0
        reasons: list[str] = []
        if explicit_match:
            reasons.append("explicit task specialist")
        if matched_terms:
            reasons.append("terms: " + ", ".join(matched_terms))
        if matched_paths:
            reasons.append("paths: " + ", ".join(matched_paths))
        if specialist_id in activated:
            reasons.append("activated in project manifest")

        candidates.append(
            {
                "id": specialist_id,
                "name": item["name"],
                "required": bool(item["required_review_when_matched"]),
                "mode": "activated_contract" if specialist_id in activated else "local_contract",
                "score": score,
                "reason": reasons,
                "accountable_owner": item["accountable_owner"],
                "local_roles": item["local_roles"],
                "evaluator": item["evaluator"],
                "authority": item["authority"],
                "deliverables": item["deliverables"],
                "source_url": source_url(item, manifest),
            }
        )

    candidates.sort(key=lambda value: (not value["required"], -value["score"], value["id"]))
    required = [item for item in candidates if item["required"]]
    optional = [item for item in candidates if not item["required"]]
    return required + optional[: max(0, limit - len(required))]


def task_recommendations(task: dict[str, Any], root: Path = ROOT) -> list[dict[str, Any]]:
    manifest = load_manifest(root)
    project = load_project(root)
    return recommend_for_task(
        task,
        manifest,
        resolved_profiles(project, root),
        project.get("specialists", []),
    )


def filtered_specialists(
    manifest: dict[str, Any], *, domain: str | None, source: str | None
) -> list[dict[str, Any]]:
    result = []
    for item in manifest["specialists"]:
        if domain and domain not in item["domains"]:
            continue
        if source and source != item["source_collection"]:
            continue
        result.append(item)
    return sorted(result, key=lambda value: (value["domains"][0], value["name"]))


def print_list(args: argparse.Namespace, manifest: dict[str, Any], project: dict[str, Any]) -> int:
    items = filtered_specialists(manifest, domain=args.domain, source=args.source)
    activated = set(project.get("specialists", []))
    if args.json:
        payload = {
            "schema_version": 1,
            "specialists": [
                {
                    "id": item["id"],
                    "name": item["name"],
                    "domains": item["domains"],
                    "activation": item["activation"],
                    "activated": item["id"] in activated,
                    "required_review_when_matched": item["required_review_when_matched"],
                    "source_url": source_url(item, manifest),
                }
                for item in items
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print("Reviewed specialist capability contracts")
    print("Contracts are routed locally; upstream agents are not bulk-installed or executed.\n")
    for item in items:
        state = "activated" if item["id"] in activated else "available"
        required = "required on match" if item["required_review_when_matched"] else "advisory"
        print(f"{item['id']:<28} {state:<10} {required:<18} {item['name']}")
        print(f"  domains: {', '.join(item['domains'])}")
    for collection_id, collection in manifest["collections"].items():
        if args.source and args.source != collection_id:
            continue
        print(f"\nFull upstream roster: {collection['catalog_url']}")
        print(collection["full_catalog_note"])
    return 0


def specialist_payload(item: dict[str, Any], manifest: dict[str, Any], activated: bool) -> dict[str, Any]:
    payload = dict(item)
    payload["schema_version"] = 1
    payload["activated"] = activated
    payload["source_url"] = source_url(item, manifest)
    return payload


def print_show(args: argparse.Namespace, manifest: dict[str, Any], project: dict[str, Any]) -> int:
    try:
        item = specialist_index(manifest)[args.specialist_id]
    except KeyError as error:
        raise BrokerError(f"Unknown specialist: {args.specialist_id}") from error
    payload = specialist_payload(
        item, manifest, args.specialist_id in set(project.get("specialists", []))
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"{payload['name']} ({payload['id']})")
    print(f"State: {'activated' if payload['activated'] else 'available'}")
    print(f"Domains: {', '.join(payload['domains'])}")
    print(f"Authority: {payload['authority']}")
    print(f"Local roles: {', '.join(payload['local_roles'])}")
    print(f"Independent evaluator: {payload['evaluator']}")
    print(f"Required when matched: {'yes' if payload['required_review_when_matched'] else 'no'}")
    print("Deliverables:")
    for deliverable in payload["deliverables"]:
        print(f"  - {deliverable}")
    print(f"When not to use: {payload['when_not_to_use']}")
    print(f"Reviewed source: {payload['source_url']}")
    return 0


def print_recommend(args: argparse.Namespace, root: Path) -> int:
    task = get_task(args.task_id, root)
    recommendations = task_recommendations(task, root)
    payload = {
        "schema_version": 1,
        "task_id": task["id"],
        "recommendations": recommendations,
        "routing_note": "One accountable owner remains responsible; specialist contracts advise or evaluate within their declared authority.",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Specialist routing: {task['id']} — {task.get('title', '')}")
    if not recommendations:
        print("No additional specialist contract is justified by current task evidence.")
        return 0
    for item in recommendations:
        mark = "REQUIRED" if item["required"] else "RECOMMENDED"
        print(f"\n{mark}: {item['name']} ({item['id']})")
        print(f"  mode: {item['mode']}")
        print(f"  reason: {'; '.join(item['reason'])}")
        print(f"  local role(s): {', '.join(item['local_roles'])}")
        print(f"  evaluator: {item['evaluator']}")
        print(f"  authority: {item['authority']}")
        print("  required deliverable:")
        for deliverable in item["deliverables"]:
            print(f"    - {deliverable}")
    print("\nActivation is optional and never installs upstream code:")
    print("  ./agentic agents activate <specialist-id> --dry-run")
    return 0


def update_activation(
    specialist_id: str,
    *,
    activate: bool,
    yes: bool,
    root: Path,
) -> int:
    manifest = load_manifest(root)
    if specialist_id not in specialist_index(manifest):
        raise BrokerError(f"Unknown specialist: {specialist_id}")
    project = load_project(root)
    current = set(project.get("specialists", []))
    action = "activate" if activate else "deactivate"
    changed = specialist_id not in current if activate else specialist_id in current
    print(f"Specialist contract: {specialist_id}")
    print(f"Action: {action}")
    print("Effect: update .agentic/project.json only")
    print("External installation: none")
    print("Runtime authority change: none")
    if not changed:
        print(f"No change required; specialist is already {'active' if activate else 'inactive'}.")
        return 0
    if not yes:
        print("\nPreview complete. Re-run with --yes to apply this reversible manifest change.")
        return 0
    if activate:
        current.add(specialist_id)
    else:
        current.remove(specialist_id)
    project["specialists"] = sorted(current)
    (root / ".agentic" / "project.json").write_text(json.dumps(project, indent=2) + "\n")
    print(f"\n{specialist_id} {action}d. No external code was installed or executed.")
    return 0


def run_doctor(args: argparse.Namespace, root: Path) -> int:
    manifest = load_manifest(root)
    project = load_project(root)
    index = specialist_index(manifest)
    active_profiles = set(resolved_profiles(project, root))
    activated = project.get("specialists", [])
    errors: list[str] = []
    warnings: list[str] = []
    for specialist_id in activated:
        item = index.get(specialist_id)
        if item is None:
            errors.append(f"Unknown activated specialist: {specialist_id}")
            continue
        if not active_profiles.intersection(item["profiles_any_of"]):
            warnings.append(
                f"{specialist_id} is activated but none of its profiles are active: "
                + ", ".join(item["profiles_any_of"])
            )
    payload = {
        "schema_version": 1,
        "status": "fail" if errors else "pass",
        "catalog_count": len(index),
        "activated": activated,
        "active_profiles": sorted(active_profiles),
        "errors": errors,
        "warnings": warnings,
        "external_installation_performed": False,
        "runtime_authority_changed": False,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Specialist broker doctor: {payload['status'].upper()}")
        print(f"Reviewed contracts: {payload['catalog_count']}")
        print(f"Activated contracts: {', '.join(activated) if activated else 'none'}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("External installation performed: no")
        print("Runtime authority changed: no")
    return 1 if errors else 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List reviewed specialist contracts")
    list_parser.add_argument("--domain")
    list_parser.add_argument("--source")
    list_parser.add_argument("--json", action="store_true")

    show = subparsers.add_parser("show", help="Show one specialist contract")
    show.add_argument("specialist_id")
    show.add_argument("--json", action="store_true")

    recommend = subparsers.add_parser("recommend", help="Recommend specialists for a task")
    recommend.add_argument("task_id")
    recommend.add_argument("--json", action="store_true")

    for name in ("activate", "deactivate"):
        action = subparsers.add_parser(name, help=f"{name.title()} a local specialist contract")
        action.add_argument("specialist_id")
        decision = action.add_mutually_exclusive_group()
        decision.add_argument("--dry-run", action="store_true")
        decision.add_argument("--yes", action="store_true")

    doctor = subparsers.add_parser("doctor", help="Validate broker policy and activation")
    doctor.add_argument("--json", action="store_true")
    return value


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    try:
        args = parser().parse_args(argv)
        if args.command == "recommend":
            return print_recommend(args, root)
        if args.command == "activate":
            return update_activation(args.specialist_id, activate=True, yes=args.yes, root=root)
        if args.command == "deactivate":
            return update_activation(args.specialist_id, activate=False, yes=args.yes, root=root)
        if args.command == "doctor":
            return run_doctor(args, root)

        manifest = load_manifest(root)
        project = load_project(root)
        if args.command == "list":
            if args.source and args.source not in manifest["collections"]:
                raise BrokerError(f"Unknown source collection: {args.source}")
            return print_list(args, manifest, project)
        return print_show(args, manifest, project)
    except (BrokerError, profile_engine.ProfileError, OSError) as error:
        print(f"Specialist broker error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
