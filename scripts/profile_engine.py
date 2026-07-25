#!/usr/bin/env python3
"""Resolve project profiles without installing or deleting resources."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / ".agentic"
PROJECT_PATH = CONFIG_DIR / "project.json"
RESOURCES_PATH = CONFIG_DIR / "resources.json"
PROFILES_DIR = CONFIG_DIR / "profiles"
MCP_PATH = ROOT / ".mcp.json"


class ProfileError(Exception):
    pass


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise ProfileError(f"Missing configuration: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ProfileError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def load_profiles() -> dict[str, dict]:
    profiles: dict[str, dict] = {}
    for path in sorted(PROFILES_DIR.glob("*.json")):
        profile = load_json(path)
        profile_id = profile.get("id")
        if not profile_id:
            raise ProfileError(f"Profile has no id: {path.relative_to(ROOT)}")
        if profile_id in profiles:
            raise ProfileError(f"Duplicate profile id: {profile_id}")
        profiles[profile_id] = profile
    return profiles


def expand_profiles(selected: list[str], profiles: dict[str, dict]) -> list[str]:
    resolved: list[str] = []
    visiting: set[str] = set()

    def visit(profile_id: str) -> None:
        if profile_id not in profiles:
            raise ProfileError(f"Unknown profile: {profile_id}")
        if profile_id in visiting:
            raise ProfileError(f"Circular profile dependency at: {profile_id}")
        if profile_id in resolved:
            return
        visiting.add(profile_id)
        for dependency in profiles[profile_id].get("requires", []):
            visit(dependency)
        visiting.remove(profile_id)
        resolved.append(profile_id)

    for profile_id in selected:
        visit(profile_id)
    return resolved


def validate_conflicts(resolved: list[str], profiles: dict[str, dict]) -> list[str]:
    active = set(resolved)
    conflicts: set[str] = set()
    for profile_id in resolved:
        for other in profiles[profile_id].get("conflicts", []):
            if other in active:
                conflicts.add(" ↔ ".join(sorted((profile_id, other))))
    return sorted(conflicts)


def resolve(selected: list[str]) -> dict:
    profiles = load_profiles()
    resources = load_json(RESOURCES_PATH).get("resources", {})
    resolved_profiles = expand_profiles(selected, profiles)
    conflicts = validate_conflicts(resolved_profiles, profiles)
    required_resources: list[str] = []
    owners: dict[str, list[str]] = {}
    for profile_id in resolved_profiles:
        for resource_id in profiles[profile_id].get("resources", []):
            if resource_id not in resources:
                raise ProfileError(f"Profile {profile_id} references unknown resource: {resource_id}")
            owners.setdefault(resource_id, []).append(profile_id)
            if resource_id not in required_resources:
                required_resources.append(resource_id)
    return {
        "selected_profiles": selected,
        "resolved_profiles": resolved_profiles,
        "required_resources": required_resources,
        "resource_owners": owners,
        "conflicts": conflicts,
        "resources": resources,
    }


def load_mcp_servers() -> set[str]:
    if not MCP_PATH.exists():
        return set()
    return set(load_json(MCP_PATH).get("mcpServers", {}))


def detect_resource(resource: dict, mcp_servers: set[str]) -> str:
    checks = resource.get("detect", [])
    if not checks:
        return "external"
    results: list[bool] = []
    for check in checks:
        check_type = check.get("type")
        value = check.get("value", "")
        if check_type == "path":
            results.append((ROOT / value).exists())
        elif check_type == "mcp":
            results.append(value in mcp_servers)
        else:
            raise ProfileError(f"Unsupported detection type: {check_type}")
    return "present" if all(results) else "missing"


def current_profiles() -> list[str]:
    project = load_json(PROJECT_PATH)
    selected = project.get("profiles", [])
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        raise ProfileError("project.json profiles must be an array of strings")
    return selected


def print_resolution(result: dict) -> None:
    print("Selected profiles:")
    for profile_id in result["selected_profiles"]:
        print(f"  - {profile_id}")
    print("Resolved profiles:")
    for profile_id in result["resolved_profiles"]:
        print(f"  - {profile_id}")
    print("Required resources:")
    for resource_id in result["required_resources"]:
        owners = ", ".join(result["resource_owners"][resource_id])
        print(f"  - {resource_id} ({owners})")
    if result["conflicts"]:
        print("Conflicts:")
        for conflict in result["conflicts"]:
            print(f"  - {conflict}")


def command_resolve(_: argparse.Namespace) -> int:
    result = resolve(current_profiles())
    print_resolution(result)
    return 1 if result["conflicts"] else 0


def command_doctor(_: argparse.Namespace) -> int:
    result = resolve(current_profiles())
    mcp_servers = load_mcp_servers()
    active = set(result["required_resources"])
    missing: list[str] = []
    external: list[str] = []

    print_resolution(result)
    print("Resource status:")
    for resource_id in result["required_resources"]:
        status = detect_resource(result["resources"][resource_id], mcp_servers)
        print(f"  - {resource_id}: {status}")
        if status == "missing":
            missing.append(resource_id)
        elif status == "external":
            external.append(resource_id)

    inactive_present: list[str] = []
    for resource_id, resource in result["resources"].items():
        if resource_id in active or resource.get("catalog_only_when_inactive"):
            continue
        if detect_resource(resource, mcp_servers) == "present":
            inactive_present.append(resource_id)

    if inactive_present:
        print("Present but inactive (review before cleanup):")
        for resource_id in inactive_present:
            print(f"  - {resource_id}")
    if external:
        print("External resources require separate trusted installation/connection:")
        for resource_id in external:
            print(f"  - {resource_id}")
    if result["conflicts"] or missing:
        print("Doctor result: attention required")
        return 1
    print("Doctor result: profile configuration is coherent")
    return 0


def parse_profile_list(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ProfileError("At least one profile is required")
    return values


def command_preview(args: argparse.Namespace) -> int:
    before = resolve(current_profiles())
    after = resolve(parse_profile_list(args.profiles))
    before_resources = set(before["required_resources"])
    after_resources = set(after["required_resources"])

    print("Profile change preview (no files or dependencies will be modified)")
    print("Profiles to enable:")
    for item in sorted(set(after["resolved_profiles"]) - set(before["resolved_profiles"])):
        print(f"  + {item}")
    print("Profiles to disable:")
    for item in sorted(set(before["resolved_profiles"]) - set(after["resolved_profiles"])):
        print(f"  - {item}")
    print("Resources to activate:")
    for item in sorted(after_resources - before_resources):
        print(f"  + {item}")
    print("Resources to deactivate:")
    for item in sorted(before_resources - after_resources):
        print(f"  - {item}")
    if after["conflicts"]:
        print("Conflicts:")
        for conflict in after["conflicts"]:
            print(f"  ! {conflict}")
        return 1
    return 0


def command_select(args: argparse.Namespace) -> int:
    selected = parse_profile_list(args.profiles)
    result = resolve(selected)
    if result["conflicts"]:
        raise ProfileError("Cannot select conflicting profiles: " + ", ".join(result["conflicts"]))
    if not args.yes:
        print("Refusing to update project.json without --yes. Run preview first.")
        return 2
    project = load_json(PROJECT_PATH)
    project["profiles"] = selected
    temporary_path = PROJECT_PATH.with_suffix(".json.tmp")
    temporary_path.write_text(json.dumps(project, indent=2) + "\n")
    temporary_path.replace(PROJECT_PATH)
    print("Updated .agentic/project.json only.")
    print("No packages, plugins, MCPs, or files were installed, removed, or deleted.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("resolve").set_defaults(func=command_resolve)
    subparsers.add_parser("doctor").set_defaults(func=command_doctor)
    preview = subparsers.add_parser("preview")
    preview.add_argument("--profiles", required=True, help="Comma-separated profile ids")
    preview.set_defaults(func=command_preview)
    select = subparsers.add_parser("select")
    select.add_argument("--profiles", required=True, help="Comma-separated profile ids")
    select.add_argument("--yes", action="store_true", help="Confirm manifest-only update")
    select.set_defaults(func=command_select)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except ProfileError as exc:
        print(f"Profile error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
