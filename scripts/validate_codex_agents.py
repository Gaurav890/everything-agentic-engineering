#!/usr/bin/env python3
"""Validate the repository's restricted, authority-neutral Codex role files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


EXPECTED_ROLES = {
    "architect",
    "design_critic",
    "integration_reviewer",
    "product_planner",
    "qa_evaluator",
    "researcher",
    "security_reviewer",
}
ALLOWED_FIELDS = {
    "name",
    "description",
    "developer_instructions",
    "sandbox_mode",
}
REQUIRED_FIELDS = {"name", "description", "developer_instructions"}
ASSIGNMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


class AgentValidationError(ValueError):
    """Raised when a project Codex agent leaves the reviewed schema."""


def load_restricted_toml(path: Path) -> dict[str, str]:
    """Parse the flat string-only TOML subset allowed for committed roles."""

    lines = path.read_text().splitlines()
    values: dict[str, str] = {}
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line or line.startswith("#"):
            continue

        match = ASSIGNMENT.fullmatch(line)
        if not match:
            raise AgentValidationError(f"{path}: unsupported TOML syntax: {line}")

        key, raw_value = match.groups()
        if key in values:
            raise AgentValidationError(f"{path}: duplicate field: {key}")

        if raw_value == '"""':
            block: list[str] = []
            while index < len(lines) and lines[index].strip() != '"""':
                block.append(lines[index])
                index += 1
            if index >= len(lines):
                raise AgentValidationError(f"{path}: unterminated multiline string")
            index += 1
            value = "\n".join(block)
        else:
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                raise AgentValidationError(
                    f"{path}: field {key} must be a TOML basic string"
                ) from exc
            if not isinstance(value, str):
                raise AgentValidationError(f"{path}: field {key} must be a string")

        values[key] = value

    return values


def validate_role_directory(role_dir: Path) -> dict[str, Path]:
    roles: dict[str, Path] = {}

    for path in sorted(role_dir.glob("*.toml")):
        role = load_restricted_toml(path)
        unknown = sorted(set(role).difference(ALLOWED_FIELDS))
        if unknown:
            raise AgentValidationError(
                f"{path}: unreviewed configuration fields: {', '.join(unknown)}"
            )

        missing = sorted(REQUIRED_FIELDS.difference(role))
        if missing:
            raise AgentValidationError(
                f"{path}: missing required fields: {', '.join(missing)}"
            )
        for key in REQUIRED_FIELDS:
            if not role[key].strip():
                raise AgentValidationError(f"{path}: empty required field: {key}")

        if role["name"] != path.stem:
            raise AgentValidationError(f"{path}: name must match the filename")
        if role.get("sandbox_mode") != "read-only":
            raise AgentValidationError(f"{path}: sandbox_mode must be read-only")
        if role["name"] in roles:
            raise AgentValidationError(f"duplicate Codex role: {role['name']}")
        roles[role["name"]] = path

    missing_roles = sorted(EXPECTED_ROLES.difference(roles))
    unexpected_roles = sorted(set(roles).difference(EXPECTED_ROLES))
    if missing_roles:
        raise AgentValidationError("missing Codex roles: " + ", ".join(missing_roles))
    if unexpected_roles:
        raise AgentValidationError(
            "unexpected Codex roles require review: " + ", ".join(unexpected_roles)
        )

    return roles


def main() -> int:
    role_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".codex/agents")
    try:
        roles = validate_role_directory(role_dir)
    except AgentValidationError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    print(f"PASS  validated {len(roles)} read-only Codex specialist roles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
