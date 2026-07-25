#!/usr/bin/env python3
"""Validate a task evidence bundle against the repository contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(bundle: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = bundle / "evidence.json"
    if not manifest_path.exists():
        return [f"Missing {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as exc:
        return [f"Invalid {manifest_path}: {exc}"]

    for field in ("task_id", "acceptance_ids", "commands", "artifacts", "verdict"):
        if not manifest.get(field):
            errors.append(f"Missing or empty field: {field}")
    if manifest.get("builder") and manifest.get("evaluator"):
        if manifest["builder"] == manifest["evaluator"]:
            errors.append("Builder and evaluator must be different for independent review")
    for relative in manifest.get("artifacts", []):
        artifact = bundle / relative
        if not artifact.is_file():
            errors.append(f"Missing artifact: {artifact}")
    if manifest.get("ui_change"):
        states = set(manifest.get("states", []))
        viewports = set(manifest.get("viewports", []))
        for state in {"normal", "loading", "empty", "error"} - states:
            errors.append(f"UI evidence missing state: {state}")
        for viewport in {"mobile", "desktop"} - viewports:
            errors.append(f"UI evidence missing viewport: {viewport}")
        if not manifest.get("evaluator"):
            errors.append("UI evidence requires an independent evaluator")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundles", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for bundle in args.bundles:
        errors = validate(bundle)
        if errors:
            failed = True
            print(f"{bundle}: FAIL")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{bundle}: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
