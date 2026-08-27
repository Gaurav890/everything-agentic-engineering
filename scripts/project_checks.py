"""Shared read-only profile and web prerequisite checks."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import profile_engine


class ProjectCheckError(ValueError):
    pass


def load_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise ProjectCheckError(f"Cannot read valid project state from {path}: {error}") from error
    if not isinstance(value, dict):
        raise ProjectCheckError(f"Project state must be an object: {path}")
    return value


def active_profiles(root: Path) -> set[str]:
    selected = load_object(root / ".agentic/project.json").get("profiles")
    if not isinstance(selected, list) or not selected or not all(
        isinstance(item, str) and item for item in selected
    ):
        raise ProjectCheckError("project.json profiles must be a non-empty string array")
    catalog = {}
    for path in sorted((root / ".agentic/profiles").glob("*.json")):
        profile = load_object(path)
        name = profile.get("id")
        if not isinstance(name, str) or not name or name in catalog:
            raise ProjectCheckError(f"Invalid or duplicate profile id: {path}")
        for key in ("requires", "conflicts"):
            values = profile.get(key, [])
            if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
                raise ProjectCheckError(f"Invalid {key} in {path}")
        catalog[name] = profile
    try:
        resolved = profile_engine.expand_profiles(selected, catalog)
        conflicts = profile_engine.validate_conflicts(resolved, catalog)
    except profile_engine.ProfileError as error:
        raise ProjectCheckError(str(error)) from error
    if conflicts:
        raise ProjectCheckError("Conflicting profiles: " + ", ".join(conflicts))
    return set(resolved)


def web_prerequisite(root: Path) -> tuple[str, str] | None:
    node = shutil.which("node")
    if node is None:
        return "Node.js is required for this web project", "Install Node.js 22 LTS, then run ./agentic next again."
    try:
        result = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        result = None
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)\s*", result.stdout) if result and result.returncode == 0 else None
    if not match or tuple(map(int, match.groups())) < (20, 9, 0):
        return "The web runtime needs Node.js 20.9 or newer", "Use the tested Node.js 22 LTS baseline, then run ./agentic next again."
    if shutil.which("pnpm") is None:
        manager = load_object(root / "package.json").get("packageManager", "pnpm")
        return "The project package manager is missing", f"Install the package manager declared in package.json ({manager}), then run ./agentic next again."
    if not (root / "node_modules/.pnpm").is_dir() or not (root / "node_modules/.modules.yaml").is_file():
        return "Install the selected project's local dependencies", "pnpm install --frozen-lockfile"
    return None
