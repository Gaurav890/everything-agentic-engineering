#!/usr/bin/env python3
"""Discoverable, registry-backed command router for the starter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / ".agentic" / "commands.json"


class RegistryError(ValueError):
    """Raised when the committed command registry is unsafe or inconsistent."""


def load_registry(root: Path = ROOT) -> dict[str, Any]:
    path = root / ".agentic" / "commands.json"
    try:
        registry = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RegistryError(f"Cannot read command registry {path}: {error}") from error
    validate_registry(registry, root)
    return registry


def validate_registry(registry: dict[str, Any], root: Path = ROOT) -> None:
    if registry.get("schema_version") != 1:
        raise RegistryError("Unsupported command-registry schema version")

    groups = registry.get("groups")
    commands = registry.get("commands")
    inventory = registry.get("shell_inventory")
    if not isinstance(groups, list) or not isinstance(commands, list) or not isinstance(inventory, list):
        raise RegistryError("Registry groups, commands, and shell_inventory must be lists")

    group_names = [item.get("name") for item in groups if isinstance(item, dict)]
    if len(group_names) != len(groups) or len(group_names) != len(set(group_names)):
        raise RegistryError("Registry group names must be present and unique")

    seen_paths: set[tuple[str, ...]] = set()
    for command in commands:
        if not isinstance(command, dict):
            raise RegistryError("Every command must be an object")
        path = command.get("path")
        target = command.get("target")
        if not isinstance(path, list) or not path or not all(isinstance(part, str) and part for part in path):
            raise RegistryError("Every command path must be a non-empty string list")
        path_key = tuple(path)
        if path_key in seen_paths:
            raise RegistryError(f"Duplicate command path: {' '.join(path)}")
        seen_paths.add(path_key)
        if len(path) > 1 and path[0] not in group_names:
            raise RegistryError(f"Unknown command group: {path[0]}")
        if not isinstance(target, str) or not target.startswith("scripts/") or ".." in Path(target).parts:
            raise RegistryError(f"Unsafe command target: {target!r}")
        target_path = root / target
        if not target_path.is_file():
            raise RegistryError(f"Command target does not exist: {target}")


def public_commands(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(registry["commands"], key=lambda item: tuple(item["path"]))


def print_top_help(registry: dict[str, Any], out: TextIO) -> None:
    out.write("Everything Agentic Engineering\n")
    out.write("One command surface for setup, delivery, verification, and releases.\n\n")
    out.write("Usage:\n")
    out.write("  ./agentic <group> <command> [arguments]\n")
    out.write("  ./agentic verify [quick|full]\n")
    out.write("  ./agentic commands [--json]\n")
    out.write("  ./agentic help [group|command]\n\n")
    out.write("Groups:\n")
    for group in registry["groups"]:
        out.write(f"  {group['name']:<12} {group['summary']}\n")
    out.write("\nStandalone commands:\n")
    for command in public_commands(registry):
        if len(command["path"]) == 1:
            out.write(f"  {command['path'][0]:<12} {command['summary']}\n")
    out.write("\nRun './agentic help <group>' or './agentic commands' to explore.\n")


def print_group_help(registry: dict[str, Any], group: str, out: TextIO) -> bool:
    group_record = next((item for item in registry["groups"] if item["name"] == group), None)
    commands = [item for item in public_commands(registry) if item["path"][0] == group]
    if group_record is None or not commands:
        return False
    out.write(f"{group}: {group_record['summary']}\n\n")
    out.write("Commands:\n")
    for command in commands:
        out.write(f"  {' '.join(command['path']):<24} {command['summary']}\n")
    out.write(f"\nRun './agentic help {group} <command>' for usage.\n")
    return True


def find_command(registry: dict[str, Any], parts: Sequence[str]) -> dict[str, Any] | None:
    candidates = sorted(public_commands(registry), key=lambda item: len(item["path"]), reverse=True)
    for command in candidates:
        path = command["path"]
        if list(parts[: len(path)]) == path:
            return command
    return None


def print_command_help(command: dict[str, Any], out: TextIO) -> None:
    out.write(f"{' '.join(command['path'])}: {command['summary']}\n\n")
    out.write(f"Usage: {command['usage']}\n")
    out.write(f"Impact: {command['impact'].replace('_', ' ')}\n")


def print_commands(registry: dict[str, Any], out: TextIO, as_json: bool) -> None:
    commands = [
        {
            "command": " ".join(item["path"]),
            "summary": item["summary"],
            "usage": item["usage"],
            "impact": item["impact"],
        }
        for item in public_commands(registry)
    ]
    if as_json:
        json.dump({"schema_version": 1, "commands": commands}, out, indent=2)
        out.write("\n")
        return
    for command in commands:
        out.write(f"{command['command']:<24} {command['summary']}\n")


def run_command(command: dict[str, Any], arguments: Sequence[str], root: Path = ROOT) -> int:
    target = (root / command["target"]).resolve()
    scripts_root = (root / "scripts").resolve()
    if scripts_root not in target.parents:
        raise RegistryError(f"Command target escapes scripts/: {command['target']}")
    completed = subprocess.run([str(target), *arguments], cwd=root, check=False)
    return completed.returncode


def main(
    argv: Sequence[str] | None = None,
    *,
    root: Path = ROOT,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        registry = load_registry(root)
    except RegistryError as error:
        err.write(f"Agentic command registry error: {error}\n")
        return 2

    if not arguments or arguments[0] in {"-h", "--help"}:
        print_top_help(registry, out)
        return 0

    if arguments[0] == "commands":
        if len(arguments) > 2 or (len(arguments) == 2 and arguments[1] != "--json"):
            err.write("Usage: ./agentic commands [--json]\n")
            return 2
        print_commands(registry, out, as_json=arguments[1:] == ["--json"])
        return 0

    if arguments[0] == "help":
        requested = arguments[1:]
        if not requested:
            print_top_help(registry, out)
            return 0
        command = find_command(registry, requested)
        if command and len(requested) >= len(command["path"]):
            print_command_help(command, out)
            return 0
        if len(requested) == 1 and print_group_help(registry, requested[0], out):
            return 0
        err.write(f"Unknown help topic: {' '.join(requested)}\n")
        return 2

    command = find_command(registry, arguments)
    if command is None:
        if len(arguments) == 1 and print_group_help(registry, arguments[0], out):
            return 0
        err.write(f"Unknown command: {' '.join(arguments)}\n")
        err.write("Run './agentic --help' to see supported commands.\n")
        return 2

    remaining = arguments[len(command["path"]) :]
    if remaining == ["--help"]:
        print_command_help(command, out)
        return 0
    try:
        return run_command(command, remaining, root)
    except (OSError, RegistryError) as error:
        err.write(f"Could not run {' '.join(command['path'])}: {error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
