#!/usr/bin/env python3
"""Return one project-appropriate next action without mutating the workspace."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class NextActionError(ValueError):
    """Raised when durable project state cannot be interpreted safely."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise NextActionError(f"Cannot read valid project state from {path}: {error}") from error
    if not isinstance(value, dict):
        raise NextActionError(f"Project state must be a JSON object: {path}")
    return value


def next_action(root: Path = ROOT) -> tuple[str, str]:
    generated_path = root / ".agentic/generated-project.json"
    if not generated_path.is_file():
        return "Create your first project", "./agentic setup create"

    generated = load_object(generated_path)
    raw_profiles = generated.get("resolved_profiles")
    if not isinstance(raw_profiles, list) or not all(
        isinstance(profile, str) and profile for profile in raw_profiles
    ):
        raise NextActionError("resolved_profiles must be a string array")
    profiles = set(raw_profiles)
    if "web-next" in profiles:
        pnpm_store = root / "node_modules/.pnpm"
        pnpm_manifest = root / "node_modules/.modules.yaml"
        if not pnpm_store.is_dir() or not pnpm_manifest.is_file():
            return "Install the selected project's local dependencies", "pnpm install"
        design_path = root / ".agentic/design.json"
        design = load_object(design_path) if design_path.is_file() else {}
        if design.get("status") != "approved":
            return (
                "Open the live direction lab and compare the complete experience",
                "pnpm dev",
            )
        direction_path = root / "packages/design-tokens/generated/direction.css"
        approved_direction = design.get("approved_direction")
        compiled = direction_path.read_text() if direction_path.is_file() else ""
        if (
            not isinstance(approved_direction, str)
            or not approved_direction
            or f"({approved_direction})" not in compiled
        ):
            return (
                "Compile the approved direction into the canonical token outputs",
                "./agentic tokens build",
            )
        return "Prove the approved experience before review", "./agentic verify full"

    if "mobile-expo" in profiles:
        return (
            "Complete the mobile product intent before selecting implementation capabilities",
            "Open docs/00-vision/NORTH_STAR.md",
        )
    return (
        "Define the product outcome before creating the first requirement",
        "Open docs/00-vision/NORTH_STAR.md",
    )


def main() -> int:
    try:
        title, command = next_action()
    except NextActionError as error:
        print(f"Next-action error: {error}", file=sys.stderr)
        return 1
    print("NEXT")
    print(title)
    print(f"\n  {command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
