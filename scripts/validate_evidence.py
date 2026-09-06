#!/usr/bin/env python3
"""Validate a task evidence bundle against the repository contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VERDICT_STATUSES = {
    "PASS",
    "PASS_WITH_RISKS",
    "PASS_WITH_REVIEW_PENDING",
    "PASS_WITH_PORTABLE_PACKAGING_BLOCKED",
    "FAIL",
    "BLOCKED",
    "NEEDS_HUMAN",
    "INSUFFICIENT_EVIDENCE",
}
PLACEHOLDER_COMMAND_MARKERS = (
    "not executed",
    "not run",
    "did not run",
    "not applicable",
    "skipped",
    "n/a",
)


def verdict_status(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    status, separator, detail = value.strip().partition(" — ")
    if status not in VERDICT_STATUSES:
        return None
    if separator and not detail.strip():
        return None
    return status


def symlink_component(base: Path, target: Path) -> Path | None:
    try:
        relative = target.relative_to(base)
    except ValueError:
        return target
    current = base
    if current.is_symlink():
        return current
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return current
    return None


def artifact_error(bundle: Path, relative: object) -> str | None:
    if not isinstance(relative, str) or not relative.strip():
        return "Artifact paths must be non-empty strings"
    path = Path(relative)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return f"Artifact path must stay relative to the bundle: {relative}"
    candidate = bundle / path
    current = bundle
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            return f"Artifact cannot follow symlinks: {relative}"
    try:
        resolved_bundle = bundle.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
    except OSError:
        return f"Missing artifact: {candidate}"
    if not resolved_candidate.is_relative_to(resolved_bundle):
        return f"Artifact escapes bundle: {relative}"
    if not candidate.is_file():
        return f"Missing regular artifact: {candidate}"
    return None


def validate(
    bundle: Path,
    *,
    evidence_root: Path | None = None,
    trusted_root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    evidence_root = evidence_root or bundle.parent
    trusted_root = trusted_root or evidence_root
    manifest_path = bundle / "evidence.json"
    unsafe = (
        symlink_component(trusted_root, evidence_root)
        or symlink_component(evidence_root, bundle)
        or symlink_component(bundle, manifest_path)
    )
    if unsafe:
        return [f"Evidence path cannot follow symlinks: {unsafe}"]
    try:
        resolved_root = evidence_root.resolve(strict=True)
        resolved_bundle = bundle.resolve(strict=True)
    except OSError as exc:
        return [f"Invalid evidence path: {exc}"]
    if not resolved_bundle.is_relative_to(resolved_root) or resolved_bundle.parent != resolved_root:
        return [f"Evidence bundle must be a direct child of {evidence_root}: {bundle}"]
    if not manifest_path.exists():
        return [f"Missing {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Invalid {manifest_path}: {exc}"]
    if not isinstance(manifest, dict):
        return ["Evidence manifest must be a JSON object"]

    task_id = manifest.get("task_id")
    if not isinstance(task_id, str) or not re.fullmatch(r"T-\d{3,}", task_id):
        errors.append("task_id must use the T-000 format")
    for field in ("acceptance_ids", "commands", "artifacts"):
        value = manifest.get(field)
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            errors.append(f"{field} must be a non-empty array of strings")
    commands = manifest.get("commands", [])
    if isinstance(commands, list):
        for command in commands:
            if isinstance(command, str):
                normalized = " ".join(command.strip().lower().split())
                if any(marker in normalized for marker in PLACEHOLDER_COMMAND_MARKERS):
                    errors.append(f"Command evidence cannot contain a placeholder claim: {command}")
    builder = manifest.get("builder")
    evaluator = manifest.get("evaluator")
    if not isinstance(builder, str) or not builder.strip():
        errors.append("Evidence requires a non-empty builder identity")
    if not isinstance(evaluator, str) or not evaluator.strip():
        errors.append("Evidence requires a non-empty evaluator identity")
    if (
        isinstance(builder, str)
        and isinstance(evaluator, str)
        and builder.strip() == evaluator.strip()
    ):
        errors.append("Builder and evaluator must be different for independent review")
    if not isinstance(manifest.get("ui_change"), bool):
        errors.append("ui_change must be a boolean")
    if verdict_status(manifest.get("verdict")) is None:
        errors.append("verdict must use the documented verdict vocabulary")
    artifacts = manifest.get("artifacts", [])
    if isinstance(artifacts, list):
        for relative in artifacts:
            error = artifact_error(bundle, relative)
            if error:
                errors.append(error)
    if manifest.get("ui_change") is True:
        states_value = manifest.get("states")
        viewports_value = manifest.get("viewports")
        if not isinstance(states_value, list) or not all(
            isinstance(item, str) for item in states_value
        ):
            errors.append("UI evidence states must be an array of strings")
            states_value = []
        if not isinstance(viewports_value, list) or not all(
            isinstance(item, str) for item in viewports_value
        ):
            errors.append("UI evidence viewports must be an array of strings")
            viewports_value = []
        states = set(states_value)
        viewports = set(viewports_value)
        for state in {"normal", "loading", "empty", "error"} - states:
            errors.append(f"UI evidence missing state: {state}")
        for viewport in {"mobile", "desktop"} - viewports:
            errors.append(f"UI evidence missing viewport: {viewport}")
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
