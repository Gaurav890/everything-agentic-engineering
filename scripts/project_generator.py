#!/usr/bin/env python3
"""Materialize a clean, profile-specific project in a new directory."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import init_project  # noqa: E402
import profile_engine  # noqa: E402

CONFIG_PATH = Path(".agentic/generator.json")
GENERATED_PATH = Path(".agentic/generated-project.json")
PROJECT_PATH = Path(".agentic/project.json")

TRANSIENT_NAMES = {
    ".DS_Store",
    ".env",
    ".git",
    ".next",
    ".pnpm-store",
    ".turbo",
    ".cache",
    ".expo",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "playwright-report",
    "test-results",
    ".auth",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "tmp",
    "venv",
}

SENSITIVE_NAMES = {
    ".git-credentials",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "id_ed25519",
    "id_rsa",
}
SENSITIVE_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}
TRANSIENT_SUFFIXES = {".har", ".log", ".pyc", ".pyo", ".tsbuildinfo"}

MANDATORY_GENERATOR_FILES = {
    Path(".agentic/generator.json"),
    Path("scripts/create-project.sh"),
    Path("scripts/project_generator.py"),
    Path("scripts/verify_generated_project.py"),
}

GENERATED_WRITE_PATHS = {
    PROJECT_PATH,
    GENERATED_PATH,
    Path("package.json"),
    Path("plugin.json"),
    Path(".codex-plugin/plugin.json"),
    Path(".mcp.json"),
    Path(".env.example"),
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path("docs/40-execution/TASKS.jsonl"),
    Path("docs/40-execution/CURRENT_STATE.md"),
    Path("docs/40-execution/PROGRESS.md"),
    Path("docs/40-execution/HANDOFF.md"),
    Path("docs/40-execution/BLOCKERS.md"),
    Path("docs/40-execution/RISKS.md"),
}


class GenerationError(ValueError):
    """Raised when generation would violate the copy-only safety contract."""


@dataclass(frozen=True)
class GenerationPlan:
    source_root: Path
    destination: Path
    project_name: str
    slug: str
    selected_profiles: tuple[str, ...]
    resolved_profiles: tuple[str, ...]
    files: tuple[Path, ...]
    included_managed_paths: tuple[str, ...]
    excluded_managed_paths: tuple[str, ...]
    always_excluded: tuple[str, ...]
    external_setup: tuple[str, ...]
    source_version: str
    source_commit: str
    source_dirty: bool

    def public_report(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "operation": "create_downstream_project",
            "project": {"name": self.project_name, "slug": self.slug},
            "destination": str(self.destination),
            "selected_profiles": list(self.selected_profiles),
            "resolved_profiles": list(self.resolved_profiles),
            "copy": {
                "tracked_file_count": len(self.files),
                "included_managed_paths": list(self.included_managed_paths),
                "excluded_managed_paths": list(self.excluded_managed_paths),
                "always_excluded": list(self.always_excluded),
            },
            "external_setup_to_review": list(self.external_setup),
            "source": {
                "name": "everything-agentic-engineering",
                "version": self.source_version,
                "commit": self.source_commit,
                "working_tree_dirty": self.source_dirty,
            },
            "safety": {
                "source_mutation": False,
                "destination_must_not_exist": True,
                "copies_git_history": False,
                "copies_secrets": False,
                "installs_external_capabilities": False,
                "enables_mcp_servers": False,
                "initializes_git": False,
            },
        }


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise GenerationError(f"Cannot read valid {label} from {path}: {error}") from error
    if not isinstance(payload, dict):
        raise GenerationError(f"{label} must be a JSON object: {path}")
    return payload


def load_config(source_root: Path) -> dict[str, Any]:
    config = load_object(source_root / CONFIG_PATH, "generator configuration")
    if config.get("schema_version") != 1:
        raise GenerationError("Unsupported generator configuration schema")
    for field in ("source_roots", "always_excluded"):
        value = config.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise GenerationError(f"generator.json {field} must be a non-empty string list")
        for item in value:
            validate_relative_config_path(item, f"generator.json {field}")
    profile_paths = config.get("profile_paths")
    if not isinstance(profile_paths, dict):
        raise GenerationError("generator.json profile_paths must be an object")
    for path, profiles in profile_paths.items():
        if not isinstance(path, str) or not path or not isinstance(profiles, list) or not profiles:
            raise GenerationError("Every profile path needs a path and at least one profile")
        validate_relative_config_path(path, "generator.json profile_paths")
        if not all(isinstance(profile, str) and profile for profile in profiles):
            raise GenerationError(f"Invalid profile list for {path}")
    return config


def validate_relative_config_path(value: str, label: str) -> None:
    path = Path(value)
    if path.is_absolute() or path == Path(".") or ".." in path.parts:
        raise GenerationError(f"{label} paths must be contained relative paths: {value}")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", slug):
        raise GenerationError(
            "Project name must produce a 1-63 character lowercase kebab-case slug"
        )
    return slug


def is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True


def resolve_destination(raw: str, source_root: Path, cwd: Path | None = None) -> Path:
    base = Path.cwd() if cwd is None else cwd
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = base / candidate
    candidate = candidate.resolve(strict=False)
    source = source_root.resolve()
    if candidate == source or is_within(candidate, source):
        raise GenerationError(
            "Destination must be outside the starter checkout; use a sibling or separate directory"
        )
    if candidate.exists():
        raise GenerationError(f"Destination already exists; choose a new path: {candidate}")
    if not candidate.parent.is_dir():
        raise GenerationError(f"Destination parent does not exist: {candidate.parent}")
    return candidate


def path_is_under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix + "/")


def git_source_state(source_root: Path) -> tuple[str, bool, list[Path]]:
    try:
        top_level = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        if Path(top_level).resolve() != source_root.resolve():
            raise GenerationError("The starter path must be the root of its Git checkout")
        commit = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(source_root), "status", "--porcelain"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        tracked = subprocess.run(
            ["git", "-C", str(source_root), "ls-files", "-z"],
            capture_output=True,
            check=True,
        ).stdout.split(b"\0")
    except (OSError, subprocess.CalledProcessError) as error:
        raise GenerationError(
            "A valid Git checkout is required so generation can copy only tracked files"
        ) from error
    paths = [Path(item.decode()) for item in tracked if item]
    return commit, bool(status.strip()), paths


def candidate_files(
    source_root: Path,
    source_roots: list[str],
    tracked: list[Path],
) -> list[Path]:
    roots = tuple(Path(value) for value in source_roots)
    values = {
        path
        for path in tracked
        if any(path == root or root in path.parents for root in roots)
    }
    # These files are needed only while validating an uncommitted generator
    # implementation. After merge they are ordinary tracked inputs.
    values.update(
        path for path in MANDATORY_GENERATOR_FILES if (source_root / path).is_file()
    )
    return sorted(values, key=lambda path: path.as_posix())


def path_allowed(path: Path, config: dict[str, Any], active_profiles: set[str]) -> bool:
    value = path.as_posix()
    if any(part in TRANSIENT_NAMES for part in path.parts):
        return False
    if any(part.startswith(".env") for part in path.parts):
        return False
    if any(part in SENSITIVE_NAMES for part in path.parts):
        return False
    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        return False
    if path.suffix.lower() in TRANSIENT_SUFFIXES:
        return False
    if value == ".vscode/settings.json":
        return False
    if any(path_is_under(value, prefix) for prefix in config["always_excluded"]):
        return False
    for prefix, required_profiles in config["profile_paths"].items():
        if path_is_under(value, prefix) and not active_profiles.intersection(required_profiles):
            return False
    return True


def source_version(source_root: Path) -> str:
    package = load_object(source_root / "package.json", "source package metadata")
    version = package.get("version")
    if not isinstance(version, str) or not version:
        raise GenerationError("Source package.json has no version")
    return version


def build_plan(
    *,
    name: str,
    destination: str,
    selected_profiles: list[str],
    source_root: Path = ROOT,
    cwd: Path | None = None,
) -> GenerationPlan:
    if not name.strip():
        raise GenerationError("Project name is required")
    slug = slugify(name)
    target = resolve_destination(destination, source_root, cwd)
    config = load_config(source_root)
    resolution = profile_engine.resolve(selected_profiles)
    if resolution["conflicts"]:
        raise GenerationError("Conflicting profiles: " + ", ".join(resolution["conflicts"]))
    active = set(resolution["resolved_profiles"])
    commit, dirty, tracked = git_source_state(source_root)
    candidates = candidate_files(source_root, config["source_roots"], tracked)
    files = tuple(path for path in candidates if path_allowed(path, config, active))
    managed = config["profile_paths"]
    included_managed = tuple(
        sorted(path for path, profiles in managed.items() if active.intersection(profiles))
    )
    excluded_managed = tuple(
        sorted(path for path, profiles in managed.items() if not active.intersection(profiles))
    )
    resources = resolution["resources"]
    external = tuple(
        resource_id
        for resource_id in resolution["required_resources"]
        if resources[resource_id].get("kind") in {"external-skill", "mcp", "backend"}
    )
    return GenerationPlan(
        source_root=source_root.resolve(),
        destination=target,
        project_name=name.strip(),
        slug=slug,
        selected_profiles=tuple(selected_profiles),
        resolved_profiles=tuple(resolution["resolved_profiles"]),
        files=files,
        included_managed_paths=included_managed,
        excluded_managed_paths=excluded_managed,
        always_excluded=tuple(config["always_excluded"]),
        external_setup=external,
        source_version=source_version(source_root),
        source_commit=commit,
        source_dirty=dirty,
    )


def copy_entry(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_symlink():
        destination.symlink_to(os.readlink(source), target_is_directory=source.is_dir())
        return
    shutil.copy2(source, destination)


def validate_source_entry(plan: GenerationPlan, relative: Path) -> None:
    if relative.is_absolute() or ".." in relative.parts:
        raise GenerationError(f"Planned source path is not contained: {relative}")
    source = plan.source_root / relative
    try:
        resolved = source.resolve(strict=True)
    except OSError as error:
        raise GenerationError(f"Planned source path is invalid: {relative}") from error
    if not is_within(resolved, plan.source_root):
        raise GenerationError(f"Planned source path escapes the starter: {relative}")
    if not source.is_file() and not source.is_symlink():
        raise GenerationError(f"Planned source entry is not a file: {relative}")
    if not source.is_symlink():
        return

    raw_target = Path(os.readlink(source))
    if raw_target.is_absolute():
        raise GenerationError(f"Planned source symlink uses an absolute target: {relative}")
    destination_target = (plan.destination / relative).parent / raw_target
    if not is_within(destination_target.resolve(strict=False), plan.destination):
        raise GenerationError(f"Generated symlink would escape the project: {relative}")
    descendants = (*plan.files, *GENERATED_WRITE_PATHS)
    if any(relative in path.parents for path in descendants if path != relative):
        raise GenerationError(f"Planned source symlink is an output ancestor: {relative}")


def validate_planned_sources(plan: GenerationPlan) -> None:
    """Reject missing or escaping source entries before creating the destination."""
    for relative in plan.files:
        validate_source_entry(plan, relative)


def directory_identity(path: Path) -> tuple[int, int]:
    details = path.lstat()
    if stat.S_ISLNK(details.st_mode) or not stat.S_ISDIR(details.st_mode):
        raise GenerationError(f"Generated destination is no longer a real directory: {path}")
    return details.st_dev, details.st_ino


def rollback_created_destination(path: Path, expected: tuple[int, int]) -> None:
    try:
        current = directory_identity(path)
    except (FileNotFoundError, GenerationError) as error:
        raise GenerationError(
            "Generation failed and the created destination identity changed; rollback refused"
        ) from error
    if current != expected:
        raise GenerationError(
            "Generation failed and the created destination identity changed; rollback refused"
        )
    shutil.rmtree(path)


def require_destination_identity(path: Path, expected: tuple[int, int]) -> None:
    if directory_identity(path) != expected:
        raise GenerationError("Generated destination identity changed during generation")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def generated_project_manifest(plan: GenerationPlan) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project": {"name": plan.project_name},
        "profiles": list(plan.selected_profiles),
        "specialists": [],
        "policy": {
            "allow_automatic_install": False,
            "allow_automatic_removal": False,
        },
    }


def generated_metadata(plan: GenerationPlan) -> dict[str, Any]:
    report = plan.public_report()
    return {
        "schema_version": 1,
        "project": report["project"],
        "selected_profiles": report["selected_profiles"],
        "resolved_profiles": report["resolved_profiles"],
        "included_managed_paths": report["copy"]["included_managed_paths"],
        "excluded_managed_paths": report["copy"]["excluded_managed_paths"],
        "expected_external_setup": report["external_setup_to_review"],
        "source": report["source"],
        "safety": report["safety"],
    }


def generated_package(plan: GenerationPlan) -> dict[str, Any]:
    source = load_object(plan.source_root / "package.json", "source package metadata")
    return {
        "name": plan.slug,
        "version": "0.1.0",
        "private": True,
        "packageManager": source.get("packageManager", "pnpm@9.15.9"),
        "scripts": {},
    }


def generated_portable_plugin(plan: GenerationPlan) -> dict[str, Any]:
    return {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": plan.slug,
        "version": "0.1.0",
        "description": f"Durable product and engineering workflows for {plan.project_name}.",
        "license": "MIT",
        "keywords": ["agentic-engineering", "agent-skills", "software-development"],
    }


def generated_native_plugin(plan: GenerationPlan) -> dict[str, Any]:
    return {
        "name": plan.slug,
        "version": "0.1.0",
        "description": f"Project-local engineering workflows for {plan.project_name}.",
        "license": "MIT",
        "keywords": ["agentic-engineering", "product-development", "worktrees"],
        "skills": "./skills/",
        "interface": {
            "displayName": plan.project_name,
            "shortDescription": "Ship software with durable engineering workflows.",
            "longDescription": "An evidence-gated system for product discovery, implementation, verification, security, and collaboration.",
            "developerName": "Project maintainers",
            "category": "Productivity",
            "capabilities": [],
            "defaultPrompt": "Read AGENTS.md, inspect the active project profiles, and prepare the next evidence-gated task.",
        },
    }


def generated_env_example(plan: GenerationPlan) -> str:
    active = set(plan.resolved_profiles)
    lines = ["# Never commit real values."]
    if "research-enabled" in active:
        lines.extend(
            [
                "PERPLEXITY_API_KEY=",
                "PERPLEXITY_TIMEOUT_MS=600000",
                "FIRECRAWL_API_KEY=",
            ]
        )
    if "web-next" in active:
        lines.append("NEXT_PUBLIC_APP_URL=http://localhost:3000")
    if "backend-supabase" in active:
        lines.extend(["SUPABASE_URL=", "SUPABASE_ANON_KEY=", "SUPABASE_SERVICE_ROLE_KEY="])
    if "backend-convex" in active:
        lines.append("CONVEX_DEPLOYMENT=")
    if len(lines) == 1:
        lines.append("# Add project-specific variables only when a reviewed integration requires them.")
    return "\n".join(lines) + "\n"


def generated_readme(plan: GenerationPlan) -> str:
    profiles = "\n".join(f"- `{profile}`" for profile in plan.resolved_profiles)
    external = (
        "\n".join(f"- `{resource}`" for resource in plan.external_setup)
        if plan.external_setup
        else "- None selected."
    )
    return f"""# {plan.project_name}

This project was materialized from Everything Agentic Engineering using a
profile-specific, non-destructive generation plan.

## Active profiles

{profiles}

## Start here

1. Read `CLAUDE.md` and `AGENTS.md`.
2. Complete `docs/00-vision/NORTH_STAR.md`.
3. Build the initial PRD in `docs/10-product/PRD.md`.
4. Run `./agentic profile resolve` and review the selected capabilities.
5. Run `./agentic setup bootstrap`.
6. Run `./agentic verify full`.

## External setup requiring separate review

{external}

The generator did not install dependencies, external skills, plugins, MCP
servers, runtimes, or backends. It did not initialize Git or copy credentials.
Use `./agentic profile doctor` and the tooling guides under `docs/60-tooling/`
before enabling any external capability.

## Durable project memory

- Product intent: `docs/00-vision/`
- Requirements: `docs/10-product/`
- Architecture and security: `docs/30-engineering/`
- Task state and handoffs: `docs/40-execution/`
- Evaluation: `docs/50-evals/`
- Tooling and profiles: `docs/60-tooling/`
- Collaboration: `docs/70-collaboration/`
"""


def reset_durable_state(plan: GenerationPlan) -> None:
    execution = plan.destination / "docs/40-execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "TASKS.jsonl").write_text("")
    (execution / "CURRENT_STATE.md").write_text(
        f"# Current state\n\nProject: {plan.project_name}\n\n"
        "The project has been generated, but product discovery and implementation have not started.\n\n"
        "Only factual present-tense truth belongs here.\n"
    )
    (execution / "PROGRESS.md").write_text(
        "# Progress log\n\nNo verified project work has been recorded yet.\n"
    )
    (execution / "HANDOFF.md").write_text(
        "# Handoff\n\n"
        "## Current goal\n\nComplete the north star and initial product discovery.\n\n"
        "## Blockers\n\nNone recorded.\n\n"
        "## Exact next action\n\nFill in `docs/00-vision/NORTH_STAR.md`, then create the initial PRD.\n"
    )
    (execution / "BLOCKERS.md").write_text("# Blockers\n\nNone recorded.\n")
    (execution / "RISKS.md").write_text("# Risks\n\nNo project-specific risks recorded yet.\n")


def write_generated_files(plan: GenerationPlan) -> None:
    write_json(plan.destination / PROJECT_PATH, generated_project_manifest(plan))
    write_json(plan.destination / GENERATED_PATH, generated_metadata(plan))
    write_json(plan.destination / "package.json", generated_package(plan))
    write_json(plan.destination / "plugin.json", generated_portable_plugin(plan))
    write_json(plan.destination / ".codex-plugin/plugin.json", generated_native_plugin(plan))
    write_json(plan.destination / ".mcp.json", {"mcpServers": {}})
    (plan.destination / ".env.example").write_text(generated_env_example(plan))
    (plan.destination / "README.md").write_text(generated_readme(plan))
    (plan.destination / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n\nNo released project changes yet.\n"
    )
    reset_durable_state(plan)


def validate_symlinks(root: Path) -> None:
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(directory)
        for name in [*dirnames, *filenames]:
            path = current / name
            if not path.is_symlink():
                continue
            resolved = path.resolve(strict=False)
            if not is_within(resolved, root):
                raise GenerationError(f"Generated symlink escapes the project: {path.relative_to(root)}")


def validate_generated_project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    metadata = load_object(root / GENERATED_PATH, "generated-project metadata")
    project = load_object(root / PROJECT_PATH, "project manifest")
    package = load_object(root / "package.json", "package metadata")
    mcp = load_object(root / ".mcp.json", "MCP configuration")
    if metadata.get("schema_version") != 1:
        raise GenerationError("Unsupported generated-project metadata schema")
    selected = metadata.get("selected_profiles")
    resolved = metadata.get("resolved_profiles")
    if not isinstance(selected, list) or not isinstance(resolved, list):
        raise GenerationError("Generated profile metadata must be arrays")
    if project.get("profiles") != selected:
        raise GenerationError("Generated project profiles do not match provenance")
    if project.get("specialists") != []:
        raise GenerationError("Generated projects must not activate external specialists")
    expected_policy = {
        "allow_automatic_install": False,
        "allow_automatic_removal": False,
    }
    if project.get("policy") != expected_policy:
        raise GenerationError(
            "Generated projects must keep automatic capability installation and removal disabled"
        )
    if project.get("project", {}).get("name") != metadata.get("project", {}).get("name"):
        raise GenerationError("Generated project identity does not match provenance")
    if package.get("name") != metadata.get("project", {}).get("slug"):
        raise GenerationError("Generated package slug does not match provenance")
    if mcp != {"mcpServers": {}}:
        raise GenerationError("Generated projects must not enable MCP servers")
    for path in (".git", ".env", "node_modules", "apps/showcase", "docs/80-showcase"):
        if (root / path).exists():
            raise GenerationError(f"Generated project contains prohibited path: {path}")
    for path in metadata.get("included_managed_paths", []):
        if not (root / path).exists():
            raise GenerationError(f"Expected selected path is missing: {path}")
    for path in metadata.get("excluded_managed_paths", []):
        if (root / path).exists():
            raise GenerationError(f"Inactive profile path is present: {path}")
    tasks = root / "docs/40-execution/TASKS.jsonl"
    if not tasks.is_file() or tasks.read_text() != "":
        raise GenerationError("Generated task ledger must start empty")
    if not (root / "README.md").is_file() or metadata["project"]["name"] not in (
        root / "README.md"
    ).read_text():
        raise GenerationError("Generated README does not contain the project identity")
    for path in root.rglob("*.json"):
        load_object(path, "JSON document")
    validate_symlinks(root)
    return {
        "status": "PASS",
        "project": metadata["project"],
        "profiles": resolved,
        "external_setup_pending": metadata.get("expected_external_setup", []),
        "mutation_performed": False,
    }


def materialize(plan: GenerationPlan) -> dict[str, Any]:
    validate_planned_sources(plan)
    try:
        plan.destination.mkdir(mode=0o755)
    except FileExistsError as error:
        raise GenerationError(f"Destination appeared during generation: {plan.destination}") from error
    created_identity = directory_identity(plan.destination)
    try:
        for relative in plan.files:
            require_destination_identity(plan.destination, created_identity)
            source = plan.source_root / relative
            validate_source_entry(plan, relative)
            copy_entry(source, plan.destination / relative)
        require_destination_identity(plan.destination, created_identity)
        write_generated_files(plan)
        require_destination_identity(plan.destination, created_identity)
        return validate_generated_project(plan.destination)
    except Exception as error:
        try:
            rollback_created_destination(plan.destination, created_identity)
        except GenerationError as rollback_error:
            raise rollback_error from error
        raise


def print_plan(plan: GenerationPlan) -> None:
    report = plan.public_report()
    print("Downstream project generation plan")
    print(f"  Project:     {plan.project_name} ({plan.slug})")
    print(f"  Destination: {plan.destination}")
    print(f"  Source:      {plan.source_version} @ {plan.source_commit[:12]}")
    if plan.source_dirty:
        print("  Warning:     source working tree has local changes")
    print("\nResolved profiles:")
    for profile in plan.resolved_profiles:
        print(f"  + {profile}")
    print("\nProfile-managed paths included:")
    for path in plan.included_managed_paths:
        print(f"  + {path}")
    print("\nProfile-managed paths excluded:")
    for path in plan.excluded_managed_paths:
        print(f"  - {path}")
    print(f"\nTracked files to copy: {report['copy']['tracked_file_count']}")
    print("External setup to review separately:")
    if plan.external_setup:
        for resource in plan.external_setup:
            print(f"  ! {resource}")
    else:
        print("  - none")
    print("\nSafety contract:")
    print("  - The source checkout is not modified or pruned.")
    print("  - The destination must not already exist and must be outside the source.")
    print("  - Git history, secrets, dependencies, caches, builds, and historical evidence are excluded.")
    print("  - No dependency, external skill, plugin, MCP server, runtime, or backend is installed or enabled.")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--name", required=True)
    value.add_argument("--destination", required=True)
    value.add_argument("--preset", choices=tuple(init_project.PRESETS))
    value.add_argument("--web", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--mobile", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--design", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--research", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--agentic", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--backend", default="none")
    value.add_argument("--json", action="store_true")
    confirmation = value.add_mutually_exclusive_group()
    confirmation.add_argument("--dry-run", action="store_true")
    confirmation.add_argument("--yes", action="store_true")
    return value


def run(args: argparse.Namespace) -> int:
    if args.backend not in {"none", "supabase", "convex"}:
        raise GenerationError("backend must be none, supabase, or convex")
    selected = init_project.selected_profiles(args)
    plan = build_plan(
        name=args.name,
        destination=args.destination,
        selected_profiles=selected,
    )
    if args.json:
        print(json.dumps(plan.public_report(), indent=2))
    else:
        print_plan(plan)
    if args.dry_run:
        if not args.json:
            print("\nDry run complete; no files changed.")
        return 0
    if not args.yes:
        if not args.json:
            print("\nNo project created. Re-run with --yes after reviewing this plan.")
        return 2
    report = materialize(plan)
    if args.json:
        print(json.dumps({"created": str(plan.destination), "verification": report}, indent=2))
    else:
        print(f"\nCreated {plan.project_name} at {plan.destination}")
        print("Generated-project verification: PASS")
        print(f"Next: cd {plan.destination} && ./agentic setup bootstrap")
    return 0


def main() -> int:
    try:
        return run(parser().parse_args())
    except (GenerationError, profile_engine.ProfileError, OSError) as error:
        print(f"Project generator error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
