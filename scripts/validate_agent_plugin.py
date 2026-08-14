#!/usr/bin/env python3
"""Offline validation for the repository's Agent Plugins 1.0 portable core."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
MANIFEST_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
AUTHOR_FIELDS = {"name", "email", "url"}
NAME_PATTERN = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class PluginValidationError(ValueError):
    """Raised when the committed portable package violates the v1 contract."""


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise PluginValidationError(f"Cannot read valid JSON from {path}: {error}") from error
    if not isinstance(payload, dict):
        raise PluginValidationError(f"{path} must contain a JSON object")
    return payload


def validate_manifest(plugin_root: Path) -> dict[str, Any]:
    manifest_path = plugin_root / "plugin.json"
    if not manifest_path.is_file():
        raise PluginValidationError("Agent Plugins v1 requires root plugin.json")
    if not _inside(plugin_root, manifest_path.resolve()):
        raise PluginValidationError("plugin.json resolves outside the plugin root")

    manifest = _load_object(manifest_path)
    unknown = sorted(set(manifest) - MANIFEST_FIELDS)
    if unknown:
        raise PluginValidationError(
            "plugin.json uses non-portable top-level fields: " + ", ".join(unknown)
        )
    if manifest.get("$schema") != PLUGIN_SCHEMA:
        raise PluginValidationError("plugin.json must target Agent Plugins 1.0.0")
    name = manifest.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        raise PluginValidationError("plugin.json name violates Agent Plugins v1 constraints")

    string_fields = ("version", "description", "homepage", "repository", "license")
    for field in string_fields:
        if field in manifest and not isinstance(manifest[field], str):
            raise PluginValidationError(f"plugin.json {field} must be a string")
    if "version" in manifest and not SEMVER_PATTERN.fullmatch(manifest["version"]):
        raise PluginValidationError("repository policy requires a semantic plugin version")

    author = manifest.get("author")
    if author is not None:
        if not isinstance(author, dict) or set(author) - AUTHOR_FIELDS:
            raise PluginValidationError("plugin.json author uses unsupported fields")
        if not all(isinstance(value, str) for value in author.values()):
            raise PluginValidationError("plugin.json author values must be strings")

    keywords = manifest.get("keywords")
    if keywords is not None and (
        not isinstance(keywords, list) or not all(isinstance(item, str) for item in keywords)
    ):
        raise PluginValidationError("plugin.json keywords must be a string array")

    extensions = manifest.get("extensions")
    if extensions is not None:
        if not isinstance(extensions, dict):
            raise PluginValidationError("plugin.json extensions must be an object")
        for namespace, value in extensions.items():
            if not isinstance(namespace, str) or not isinstance(value, dict):
                raise PluginValidationError("every plugin extension must be a namespaced object")
    return manifest


def validate_skills(plugin_root: Path) -> list[str]:
    skills_path = plugin_root / "skills"
    if not skills_path.exists():
        return []
    if not skills_path.is_dir():
        raise PluginValidationError("skills must resolve to a directory")
    resolved_skills = skills_path.resolve()
    if not _inside(plugin_root, resolved_skills):
        raise PluginValidationError("skills resolves outside the plugin root")

    discovered: list[str] = []
    for child in sorted(skills_path.iterdir(), key=lambda item: item.name):
        skill_file = child / "SKILL.md"
        if not skill_file.exists():
            continue
        if not skill_file.is_file():
            raise PluginValidationError(f"{skill_file} does not resolve to a regular file")
        resolved_skill = skill_file.resolve()
        if not _inside(plugin_root, resolved_skill):
            raise PluginValidationError(f"{skill_file} resolves outside the plugin root")
        text = resolved_skill.read_text()
        frontmatter = FRONTMATTER_PATTERN.match(text)
        if not frontmatter:
            raise PluginValidationError(f"{skill_file} is missing YAML frontmatter")
        for field in ("name", "description"):
            if not re.search(rf"(?m)^{field}:\s*.+$", frontmatter.group(1)):
                raise PluginValidationError(f"{skill_file} is missing {field}")
        discovered.append(child.name)
    return discovered


def validate_mcp_boundary(plugin_root: Path) -> bool:
    """Fail closed against the reviewed portable MCP packaging decision."""

    mcp_path = plugin_root / "mcp.json"
    if not mcp_path.exists():
        return False
    compatibility_path = plugin_root / ".agentic/mcp-compatibility.json"
    if compatibility_path.is_file():
        compatibility = _load_object(compatibility_path)
        decision = compatibility.get("decision")
        if (
            isinstance(decision, dict)
            and decision.get("portable_packaging") == "blocked"
        ):
            raise PluginValidationError(
                "mcp.json must remain absent while portable MCP packaging is blocked"
            )
    if not mcp_path.is_file() or not _inside(plugin_root, mcp_path.resolve()):
        raise PluginValidationError("mcp.json must be a regular file inside the plugin root")
    payload = _load_object(mcp_path)
    if set(payload) != {"$schema", "mcpServers"}:
        raise PluginValidationError("mcp.json must contain only $schema and mcpServers")
    if payload.get("$schema") != MCP_SCHEMA:
        raise PluginValidationError("mcp.json must target Agent Plugins 1.0.0")
    if not isinstance(payload.get("mcpServers"), dict):
        raise PluginValidationError("mcp.json mcpServers must be an object")
    if payload["mcpServers"]:
        raise PluginValidationError(
            "portable MCP server entries require the separately reviewed MCP compatibility task"
        )
    return True


def validate_plugin(plugin_root: Path) -> dict[str, Any]:
    root = plugin_root.resolve()
    if not root.is_dir():
        raise PluginValidationError(f"Plugin root is not a directory: {root}")
    manifest = validate_manifest(root)
    skills = validate_skills(root)
    has_mcp = validate_mcp_boundary(root)
    return {
        "name": manifest["name"],
        "version": manifest.get("version"),
        "skills": skills,
        "mcp_manifest": has_mcp,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = validate_plugin(Path(args.plugin_root))
    except PluginValidationError as error:
        print(f"Agent Plugins validation failed: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"Agent Plugins 1.0 portable core valid: {report['name']} "
            f"({len(report['skills'])} skills; portable MCP: "
            f"{'present' if report['mcp_manifest'] else 'not packaged'})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
