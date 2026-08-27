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
import agent_broker  # noqa: E402
import mcp_compatibility  # noqa: E402
import profile_engine  # noqa: E402

CONFIG_PATH = Path(".agentic/generator.json")
GENERATED_PATH = Path(".agentic/generated-project.json")
PROJECT_PATH = Path(".agentic/project.json")
EXPERIENCE_PATH = Path(".agentic/experience.json")
ENTERPRISE_PATH = Path(".agentic/enterprise.json")

WEB_ARCHETYPES = ("product", "agentic-product", "portfolio", "enterprise-workflow")
VISUAL_CHARACTERS = ("precise", "bold", "warm", "experimental")
TENANT_MODELS = ("single-tenant", "multi-tenant")
APPROVAL_MODELS = ("single-review", "dual-control", "policy-gated")
DATA_SENSITIVITY_LEVELS = ("internal", "confidential", "restricted")

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
    Path(".agentic/enterprise.json"),
    Path(".agentic/generator.json"),
    Path("apps/web/app/experience-types.ts"),
    Path("apps/web/app/enterprise-lab.tsx"),
    Path("apps/web/app/product-lab.tsx"),
    Path("packages/api/package.json"),
    Path("packages/api/src/index.d.ts"),
    Path("packages/api/src/index.js"),
    Path("packages/api/tests/enterprise-service.test.mjs"),
    Path("packages/database/package.json"),
    Path("packages/database/src/index.d.ts"),
    Path("packages/database/src/index.js"),
    Path("packages/domain/package.json"),
    Path("packages/domain/src/index.d.ts"),
    Path("packages/domain/src/index.js"),
    Path("packages/domain/tests/workflow.test.mjs"),
    Path("packages/types/package.json"),
    Path("packages/types/src/index.d.ts"),
    Path("scripts/create-project.sh"),
    Path("scripts/next-action.sh"),
    Path("scripts/next_action.py"),
    Path("scripts/project_generator.py"),
    Path("scripts/verify_generated_project.py"),
}

GENERATED_WRITE_PATHS = {
    PROJECT_PATH,
    GENERATED_PATH,
    Path(".agentic/design.json"),
    Path(".agentic/design-intake.json"),
    EXPERIENCE_PATH,
    ENTERPRISE_PATH,
    Path("package.json"),
    Path("plugin.json"),
    Path(".codex-plugin/plugin.json"),
    Path(".mcp.json"),
    Path(".env.example"),
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path("docs/20-design/DESIGN_BRIEF.md"),
    Path("docs/10-product/PRD.md"),
    Path("docs/10-product/ACCEPTANCE_CRITERIA.md"),
    Path("docs/10-product/USER_JOURNEYS.md"),
    Path("docs/30-engineering/ROLE_MATRIX.md"),
    Path("docs/30-engineering/DATA_MODEL.md"),
    Path("docs/30-engineering/API_CONTRACTS.md"),
    Path("docs/30-engineering/SECURITY_MODEL.md"),
    Path("docs/30-engineering/AUDIT_EVENTS.md"),
    Path("docs/40-execution/INITIAL_TASK_GRAPH.md"),
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
    archetype: str | None
    audience: str | None
    promise: str | None
    visual_character: str | None
    business_object: str | None
    tenant_model: str | None
    approval_model: str | None
    data_sensitivity: str | None

    def public_report(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "operation": "create_downstream_project",
            "project": {"name": self.project_name, "slug": self.slug},
            "experience": {
                "archetype": self.archetype,
                "audience": self.audience,
                "promise": self.promise,
                "visual_character": self.visual_character,
            },
            "enterprise": {
                "enabled": self.archetype == "enterprise-workflow",
                "business_object": self.business_object,
                "tenant_model": self.tenant_model,
                "approval_model": self.approval_model,
                "data_sensitivity": self.data_sensitivity,
            },
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


def clean_text(value: str | None, label: str, *, maximum: int = 180) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    if not cleaned:
        raise GenerationError(f"{label} cannot be empty")
    if len(cleaned) > maximum:
        raise GenerationError(f"{label} must be {maximum} characters or fewer")
    return cleaned


def experience_defaults(name: str, archetype: str) -> tuple[str, str]:
    if archetype == "portfolio":
        return (
            "ambitious teams looking for a distinctive creative partner",
            f"{name} turns complex product challenges into experiences people remember.",
        )
    if archetype == "agentic-product":
        return (
            "teams delegating consequential work to software agents",
            f"{name} makes autonomous work visible, interruptible, and trustworthy.",
        )
    if archetype == "enterprise-workflow":
        return (
            "operations and security teams making consequential decisions",
            f"{name} moves every request from evidence to accountable decision.",
        )
    return (
        "teams replacing fragmented work with one clear system",
        f"{name} turns a complicated workflow into calm, measurable momentum.",
    )


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
    archetype: str | None = None,
    audience: str | None = None,
    promise: str | None = None,
    visual_character: str | None = None,
    business_object: str | None = None,
    tenant_model: str | None = None,
    approval_model: str | None = None,
    data_sensitivity: str | None = None,
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
    has_web = "web-next" in active
    if archetype is not None and archetype not in WEB_ARCHETYPES:
        raise GenerationError("archetype must be product, agentic-product, portfolio, or enterprise-workflow")
    if visual_character is not None and visual_character not in VISUAL_CHARACTERS:
        raise GenerationError(
            "visual character must be precise, bold, warm, or experimental"
        )
    if not has_web and any((archetype, audience, promise, visual_character)):
        raise GenerationError("Web experience options require an active web profile")
    resolved_archetype = archetype or ("product" if has_web else None)
    if resolved_archetype:
        default_audience, default_promise = experience_defaults(name.strip(), resolved_archetype)
        resolved_audience = clean_text(audience, "audience", maximum=120) or default_audience
        resolved_promise = clean_text(promise, "product promise", maximum=120) or default_promise
        resolved_character = visual_character or "precise"
    else:
        resolved_audience = None
        resolved_promise = None
        resolved_character = None
    enterprise_enabled = resolved_archetype == "enterprise-workflow"
    if not enterprise_enabled and any((business_object, tenant_model, approval_model, data_sensitivity)):
        raise GenerationError("Enterprise options require the enterprise-workflow archetype")
    if enterprise_enabled:
        resolved_business_object = clean_text(
            business_object or "access request", "business object", maximum=80
        )
        resolved_tenant_model = tenant_model or "multi-tenant"
        resolved_approval_model = approval_model or "dual-control"
        resolved_data_sensitivity = data_sensitivity or "confidential"
        if resolved_tenant_model not in TENANT_MODELS:
            raise GenerationError("tenant model must be single-tenant or multi-tenant")
        if resolved_approval_model not in APPROVAL_MODELS:
            raise GenerationError(
                "approval model must be single-review, dual-control, or policy-gated"
            )
        if resolved_data_sensitivity not in DATA_SENSITIVITY_LEVELS:
            raise GenerationError(
                "data sensitivity must be internal, confidential, or restricted"
            )
    else:
        resolved_business_object = None
        resolved_tenant_model = None
        resolved_approval_model = None
        resolved_data_sensitivity = None
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
        archetype=resolved_archetype,
        audience=resolved_audience,
        promise=resolved_promise,
        visual_character=resolved_character,
        business_object=resolved_business_object,
        tenant_model=resolved_tenant_model,
        approval_model=resolved_approval_model,
        data_sensitivity=resolved_data_sensitivity,
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
        "experience": report["experience"],
        "enterprise": report["enterprise"],
        "selected_profiles": report["selected_profiles"],
        "resolved_profiles": report["resolved_profiles"],
        "included_managed_paths": report["copy"]["included_managed_paths"],
        "excluded_managed_paths": report["copy"]["excluded_managed_paths"],
        "expected_external_setup": report["external_setup_to_review"],
        "source": report["source"],
        "safety": report["safety"],
    }


def generated_experience(plan: GenerationPlan) -> dict[str, Any]:
    if plan.archetype is None or plan.audience is None or plan.promise is None:
        raise GenerationError("Web experience metadata is incomplete")
    return {
        "schema_version": 1,
        "name": plan.project_name,
        "archetype": plan.archetype,
        "audience": plan.audience,
        "promise": plan.promise,
        "visual_character": plan.visual_character,
        "content_status": "starter_copy_requires_review",
        "preview_all_archetypes": False,
    }


def business_object_plural(value: str) -> str:
    return value if value.endswith("s") else f"{value}s"


def generated_enterprise(plan: GenerationPlan) -> dict[str, Any]:
    enabled = plan.archetype == "enterprise-workflow"
    singular = plan.business_object or "workflow request"
    return {
        "schema_version": 1,
        "enabled": enabled,
        "business_object": {
            "singular": singular,
            "plural": business_object_plural(singular),
        },
        "tenant_model": plan.tenant_model or "single-tenant",
        "approval_model": plan.approval_model or "single-review",
        "data_sensitivity": plan.data_sensitivity or "internal",
        "roles": ["requester", "reviewer", "auditor", "admin"],
        "workflow_states": [
            "draft",
            "in_review",
            "changes_requested",
            "approved",
            "rejected",
            "cancelled",
        ],
        "required_evidence": [
            "business justification",
            "manager attestation",
            "scope and expiry",
        ],
        "audit_events": [
            "request.created",
            "request.evidence_verified",
            "request.submitted",
            "request.changes_requested",
            "request.approved",
            "request.rejected",
            "request.cancelled",
        ],
        "adapters": {
            "authentication": "local-demo",
            "persistence": "local-demo",
            "notifications": "disabled",
            "production_ready": False,
        },
    }


def generated_enterprise_artifacts(plan: GenerationPlan) -> dict[Path, str]:
    if plan.archetype != "enterprise-workflow" or not all(
        (plan.business_object, plan.tenant_model, plan.approval_model, plan.data_sensitivity)
    ):
        return {}
    object_name = plan.business_object
    plural = business_object_plural(object_name)
    marker = "Generated from `.agentic/enterprise.json`; review before production."
    return {
        Path("docs/10-product/PRD.md"): f"""# Product requirements document

Status: Captured — product-owner review required

{marker}

## Problem

{plan.audience} need to move each {object_name} from evidence to an accountable
decision without losing ownership, tenant context, rationale, or recovery.

## Desired outcome

{plan.promise}

## Primary journey

Create {object_name} → validate evidence → submit → authorized review → approve,
reject, request changes, or cancel → append audit event → communicate outcome.

## Functional requirements

- **FR-001** — A requester can create, edit, submit, and cancel their own {plural}.
- **FR-002** — An authorized reviewer can review evidence and make a reasoned decision.
- **FR-003** — Every transition is tenant-scoped, attributable, and append-only audited.
- **FR-004** — Unauthorized, incomplete, invalid, partial, and failed states recover safely.

## Non-functional requirements

- **NFR-001** — Authorization fails closed at the domain/service boundary.
- **NFR-002** — Keyboard, screen-reader, responsive, reduced-motion, and performance contracts pass.
- **NFR-003** — Local adapters remain visibly non-production until replaced and reviewed.

## Non-goals

Production identity, persistence, notifications, credentials, deployment, and
customer data are not configured by generation.
""",
        Path("docs/10-product/ACCEPTANCE_CRITERIA.md"): f"""# Acceptance criteria

{marker}

- **AC-001** — A synthetic {object_name} can traverse the reviewed workflow and record an audit event.
- **AC-002** — A cross-tenant, read-only, self-approving, or otherwise unauthorized actor is denied.
- **AC-003** — Approval remains disabled until all required evidence is verified.
- **AC-004** — Reject and request-changes decisions require a rationale.
- **AC-005** — Loading, empty, dense, invalid, partial, error, disabled, unauthorized, and success states are inspectable.
- **AC-006** — The experience passes responsive, keyboard, accessibility, reduced-motion, interaction, and visual checks.
- **AC-007** — Replacing local adapters does not change the canonical workflow or UI contract.
""",
        Path("docs/10-product/USER_JOURNEYS.md"): f"""# User journeys

{marker}

## Requester

Create {object_name} → understand missing evidence → submit → respond to requested
changes → see the final decision and its rationale.

## Reviewer

Open assigned queue → inspect scope and provenance → verify every requirement →
approve, reject, or request changes → see the recorded consequence.

## Auditor

Inspect tenant-scoped history and evidence without receiving mutation authority.

## Administrator

Cancel an unsafe in-flight request and inspect policy configuration; approval
authority remains governed by the selected `{plan.approval_model}` model.
""",
        Path("docs/30-engineering/ROLE_MATRIX.md"): f"""# Role matrix

{marker}

| Capability | Requester | Reviewer | Auditor | Admin |
|---|---:|---:|---:|---:|
| Create own {object_name} | Yes | No | No | No |
| Submit or cancel own request | Yes | No | No | Cancel only |
| Inspect tenant-scoped evidence | Own | {"Any same-tenant request" if plan.approval_model == "single-review" else "Assigned"} | Read only | Read only |
| Request changes / reject | No | Yes | No | No |
| Approve complete evidence | No | Yes | No | No |
| Inspect audit trail | Own | Assigned | Yes | Yes |

Every capability also requires a matching tenant boundary. Under `single-review`,
any eligible same-tenant reviewer can decide; `dual-control` requires the assigned
reviewer to be distinct from the owner; `policy-gated` additionally requires the
recorded policy gate to pass. The selected `{plan.approval_model}` behavior is
enforced by the service and domain policy rather than displayed as metadata only.
""",
        Path("docs/30-engineering/DATA_MODEL.md"): f"""# Data model

{marker}

## `{object_name.replace(' ', '_')}`

`id`, `tenant_id`, `owner_id`, `assigned_reviewer_id`, `policy_state`, `status`,
`risk`, `requested_scope`, `justification`, `created_at`, `updated_at`.

## `request_evidence`

`id`, `request_id`, `tenant_id`, `label`, `state`, `source`, `verified_at`.

## `audit_event`

`id`, `request_id`, `tenant_id`, `actor_id`, `action`, `from_status`,
`to_status`, `reason`, `occurred_at`.

Tenant model: `{plan.tenant_model}`. Data sensitivity: `{plan.data_sensitivity}`.
Audit events are append-only; updates and deletes are not part of the contract.
""",
        Path("docs/30-engineering/API_CONTRACTS.md"): f"""# API contracts

{marker}

- `GET /{plural.replace(' ', '-')}` — tenant-scoped list authorized for the current actor.
- `POST /{plural.replace(' ', '-')}` — create a draft owned by the current requester.
- `POST /{plural.replace(' ', '-')}/:id/evidence-checks` — run the bounded local check and append a trusted service-authored evidence event.
- `GET /{plural.replace(' ', '-')}/:id` — request, evidence, allowed transitions, and audit summary.
- `POST /{plural.replace(' ', '-')}/:id/transitions` — action plus rationale; server re-authorizes and appends one audit event atomically.

The generated application uses a local in-memory adapter behind this interface.
Do not expose it as a production API. Production routes must derive identity and
tenant from reviewed server-side authentication, never client input.
All mutation timestamps come from a trusted service-owned clock configured at
construction; callers cannot override chronology in mutation input.
""",
        Path("docs/30-engineering/SECURITY_MODEL.md"): f"""# Security model

{marker}

## Trust boundaries

- Identity and tenant claims must come from reviewed server-side authentication.
- Domain transitions fail closed for role, tenant, ownership, evidence, reason, and state.
- Reads fail closed and are scoped to requester ownership, reviewer eligibility,
  or auditor/administrator tenant visibility.
- Creation and evidence audit attribution is constructed inside the trusted
  service boundary; callers cannot author actor or transition metadata.
- All mutation timestamps come from the service-owned clock, never caller input.
- `{plan.approval_model}` approval never permits silent self-approval and is
  executable: reviewer eligibility and policy-gate state change the outcome.
- `{plan.data_sensitivity}` fields must not enter logs, analytics, prompts, or client-visible errors without review.
- Audit writes must commit atomically with the state transition.

## Generated adapter boundary

Authentication and persistence are `local-demo`; notifications are disabled;
production readiness is false. Generation creates no credentials, database,
identity provider, external service, or deployment.
""",
        Path("docs/30-engineering/AUDIT_EVENTS.md"): f"""# Audit events

{marker}

Canonical events: `request.created`, `request.evidence_verified`, `request.submitted`,
`request.changes_requested`, `request.approved`, `request.rejected`, and
`request.cancelled`.

Every event requires event ID, request ID, tenant ID, actor ID, action, prior
state, next state, rationale, and timestamp. Events are immutable, ordered, and
must not contain secrets or full sensitive payloads.
""",
        Path("docs/40-execution/INITIAL_TASK_GRAPH.md"): f"""# Initial task graph

{marker}

1. **DISC-001** — Product owner reviews PRD, journeys, roles, and non-goals.
2. **DES-001** — Compare the three running directions; approve one explicitly.
3. **SEC-001** — Choose production identity, tenant, data-retention, and audit controls.
4. **BE-001** — Replace local repository/API adapters behind existing interfaces.
5. **FE-001** — Replace synthetic content while preserving workflow and state coverage.
6. **QA-001** — Run domain, integration, accessibility, responsive, visual, and security gates.

Do not copy these into `TASKS.jsonl` blindly. Decompose approved work into owned,
dependency-aware tasks after product and architecture review.
""",
    }


def generated_package(plan: GenerationPlan) -> dict[str, Any]:
    source = load_object(plan.source_root / "package.json", "source package metadata")
    active = set(plan.resolved_profiles)
    scripts: dict[str, str] = {}
    if "web-next" in active:
        scripts.update(
            {
                "dev": "pnpm --filter @everything-agentic/web dev",
                "build": "pnpm --filter @everything-agentic/web build",
                "lint": "pnpm --filter @everything-agentic/web lint",
                "typecheck": "pnpm --filter @everything-agentic/web typecheck",
                "test": "pnpm --filter @everything-agentic/domain test && pnpm --filter @everything-agentic/api test && pnpm --filter @everything-agentic/web test",
                "test:e2e": "pnpm --dir apps/web build && pnpm --dir apps/web test:e2e",
                "test:visual": "pnpm --dir apps/web build && pnpm --dir apps/web test:visual",
                "test:visual:update": "pnpm --dir apps/web build && pnpm --dir apps/web test:visual:update",
            }
        )
    if "design-critical" in active:
        scripts["tokens:build"] = "./agentic tokens build"
    return {
        "name": plan.slug,
        "version": "0.1.0",
        "private": True,
        "packageManager": source.get("packageManager", "pnpm@9.15.9"),
        "scripts": scripts,
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
        lines.extend(
            [
                "NEXT_PUBLIC_APP_URL=http://localhost:3000",
            ]
        )
    if "backend-supabase" in active:
        lines.extend(["SUPABASE_URL=", "SUPABASE_ANON_KEY=", "SUPABASE_SERVICE_ROLE_KEY="])
    if "backend-convex" in active:
        lines.append("CONVEX_DEPLOYMENT=")
    if len(lines) == 1:
        lines.append("# Add project-specific variables only when a reviewed integration requires them.")
    return "\n".join(lines) + "\n"


def generated_first_feature(plan: GenerationPlan) -> str:
    examples = {
        "portfolio": "Help a visitor find a relevant case study and understand its outcome using your real work.",
        "product": "Make one primary product action useful, with a clear result and a recoverable empty or error state.",
        "agentic-product": "Let a person inspect an action's evidence and consequence before approving it, then recover from a failed attempt.",
        "enterprise-workflow": f"Help a reviewer find the right {plan.business_object} in the queue without weakening tenant, role, evidence, or audit boundaries.",
    }
    return f"""# First feature brief — {plan.project_name}

## Starting intent

- Audience: {plan.audience}
- Promise: {plan.promise}
- Experience: `{plan.archetype}`

This is a planning aid, not approval to implement an invented requirement.
Revisit these inputs if your product intent has changed since generation.

## One possible first outcome

{examples[plan.archetype]}

Choose this example or replace it with a more useful outcome. Replace synthetic
copy with content you own or have permission to use. Preserve the approved
design system; request an explicit redesign if it no longer serves the intent.

## Agree before building

Ask your coding assistant to help define one requirement, acceptance criteria,
happy path, failure/recovery states, file ownership, and a bounded task. Review
that scope before implementation. Keep production identity, persistence,
credentials, external services, and deployment as separate reviewed decisions.

## Prove the result

Run `./agentic verify web` for repository, build, interaction, and automated
accessibility checks. Add tests for the new behavior: the supplied reference
tests cannot prove a feature you have just invented. Use separately reviewed
screenshots with `./agentic verify visual`, and obtain an independent critique.
Neither a passing command nor this brief grants human approval or merge authority.

See [the first-project guide](../60-tooling/FIRST_PROJECT.md) for version control,
review, visual candidates, and continuation. Run `./agentic next` to resume.
"""


def generated_readme(plan: GenerationPlan) -> str:
    profiles = "\n".join(f"- `{profile}`" for profile in plan.resolved_profiles)
    external = (
        "\n".join(f"- `{resource}`" for resource in plan.external_setup)
        if plan.external_setup
        else "- None selected."
    )
    active = set(plan.resolved_profiles)
    if "web-next" in active:
        enterprise = ""
        if plan.archetype == "enterprise-workflow":
            enterprise = f"""

Your enterprise boundary is also captured:

- Business object: `{plan.business_object}`
- Tenant model: `{plan.tenant_model}`
- Approval model: `{plan.approval_model}`
- Data sensitivity: `{plan.data_sensitivity}`

The running application uses local synthetic data and replaceable adapters.
Review the generated product, role, data, API, security, audit, and task-graph
documents before selecting production identity or persistence."""
        start = f"""Your first experience brief is already captured:

- Archetype: `{plan.archetype}`
- Audience: {plan.audience}
- Promise: {plan.promise}
- Visual character: `{plan.visual_character}`
{enterprise}

Run exactly this next:

```bash
pnpm install --frozen-lockfile
```

Then run `./agentic next`. It will reveal one next action at a time as you
compare directions, approve the strongest system, compile tokens, plan your
first useful feature, and continue through implementation and review.

Read [your first-feature brief](docs/10-product/FIRST_FEATURE.md) once the design
is approved. The [first-project guide](docs/60-tooling/FIRST_PROJECT.md) explains
version control, verification scopes, visual evidence, and the review handoff.
The supplied direction lab is a starting reference, not a finished product."""
    else:
        start = """Run exactly this next:

```bash
./agentic next
```

The router exposes one project-appropriate action at a time."""
    return f"""# {plan.project_name}

This project was materialized from Everything Agentic Engineering using a
profile-specific, non-destructive generation plan.

## Active profiles

{profiles}

## Start here

{start}

Web setup requires Python 3.11+, Node.js 20.9+ (22 LTS is the tested baseline),
and the pnpm version in `package.json`. Local examples need no paid service or
API key. The mobile profile is guidance and a placeholder, not a runnable native
application; see the [readiness guide](docs/60-tooling/FIRST_PROJECT.md).

For web projects, the default is intentionally design-critical and
archetype-aware. The live direction lab is the starting point; a generic blank
page is not. Core motion and reduced-motion behavior are built in. Add advanced
2D, 3D, timeline, or gesture runtimes only when the approved direction and
performance budget justify them.

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
    if plan.archetype == "enterprise-workflow":
        current = (
            f"# Current state\n\nProject: {plan.project_name}\n\n"
            "A synthetic enterprise workflow, machine-readable boundary, and generated review artifacts are present. "
            "Production identity, persistence, notifications, credentials, and deployment are not configured.\n\n"
            "Only factual present-tense truth belongs here.\n"
        )
        handoff = (
            "# Handoff\n\n## Current goal\n\nReview the enterprise product and design contracts in the running local experience.\n\n"
            "## Blockers\n\nProduction adapters require explicit architecture and security decisions.\n\n"
            "## Exact next action\n\nRun `./agentic next` and follow the single revealed step.\n"
        )
    elif "web-next" in set(plan.resolved_profiles):
        current = (
            f"# Current state\n\nProject: {plan.project_name}\n\n"
            "The local direction lab and starting brief are present. No project-specific feature, "
            "design approval, production integration, or deployment has been completed.\n"
        )
        handoff = (
            "# Handoff\n\n## Current goal\n\nCompare the running directions, then choose the first useful feature.\n\n"
            "## Exact next action\n\nRun `./agentic next` and follow its single revealed step.\n"
        )
    else:
        current = (
            f"# Current state\n\nProject: {plan.project_name}\n\n"
            "The project has been generated, but product discovery and implementation have not started.\n\n"
            "Only factual present-tense truth belongs here.\n"
        )
        handoff = (
            "# Handoff\n\n"
            "## Current goal\n\nComplete the north star and initial product discovery.\n\n"
            "## Blockers\n\nNone recorded.\n\n"
            "## Exact next action\n\nFill in `docs/00-vision/NORTH_STAR.md`, then create the initial PRD.\n"
        )
    (execution / "CURRENT_STATE.md").write_text(current)
    (execution / "PROGRESS.md").write_text(
        "# Progress log\n\nNo verified project work has been recorded yet.\n"
    )
    (execution / "HANDOFF.md").write_text(handoff)
    (execution / "BLOCKERS.md").write_text("# Blockers\n\nNone recorded.\n")
    (execution / "RISKS.md").write_text("# Risks\n\nNo project-specific risks recorded yet.\n")


def reset_design_state(plan: GenerationPlan) -> None:
    if "design-critical" not in set(plan.resolved_profiles):
        return
    write_json(
        plan.destination / ".agentic/design.json",
        {
            "schema_version": 1,
            "status": "needs_approval",
            "approved_direction": None,
            "approved_by": None,
            "approved_at": None,
        },
    )
    write_json(
        plan.destination / ".agentic/design-intake.json",
        {
            "schema_version": 1,
            "status": "captured" if plan.archetype else "not_started",
            "answers": {
                "product_type": plan.archetype,
                "audience": plan.audience,
                "personality": plan.visual_character,
                "color_intent": None,
                "color_expression": None,
                "typography": None,
                "density": None,
                "motion": None,
                "advanced_canvas": None,
                "required_modes": None,
                "constraints": None,
            },
        },
    )


def generated_design_brief(plan: GenerationPlan) -> str:
    if plan.archetype is None:
        return (plan.source_root / "docs/20-design/DESIGN_BRIEF.md").read_text()
    return f"""# Design brief

Status: Captured — direction approval pending

## Product intent

- Product: {plan.project_name}
- Archetype: `{plan.archetype}`
- Audience: {plan.audience}
- Product promise: {plan.promise}
- Desired character: `{plan.visual_character}`
{f"- Enterprise workflow: `{plan.business_object}` · `{plan.tenant_model}` · `{plan.approval_model}` · `{plan.data_sensitivity}`" if plan.archetype == "enterprise-workflow" else ""}

These are first-run inputs, not permission to invent facts. Replace starter copy
with verified product content before release.

## Direction contract

The running direction lab must compare materially different systems using this
same product promise and audience. References are ingredients, components are
structural donors, tokens encode approved decisions, and this project's design
system wins every conflict.

Canonical design-system and token changes still require explicit human approval
through `./agentic design approve <direction-id> --yes`.
"""


def write_generated_files(plan: GenerationPlan) -> None:
    write_json(plan.destination / PROJECT_PATH, generated_project_manifest(plan))
    write_json(plan.destination / GENERATED_PATH, generated_metadata(plan))
    write_json(plan.destination / "package.json", generated_package(plan))
    write_json(plan.destination / "plugin.json", generated_portable_plugin(plan))
    write_json(plan.destination / ".codex-plugin/plugin.json", generated_native_plugin(plan))
    write_json(plan.destination / ".mcp.json", {"mcpServers": {}})
    (plan.destination / ".env.example").write_text(generated_env_example(plan))
    (plan.destination / "README.md").write_text(generated_readme(plan))
    if "web-next" in set(plan.resolved_profiles):
        write_json(plan.destination / EXPERIENCE_PATH, generated_experience(plan))
        write_json(plan.destination / ENTERPRISE_PATH, generated_enterprise(plan))
        (plan.destination / "docs/10-product/FIRST_FEATURE.md").write_text(
            generated_first_feature(plan)
        )
        (plan.destination / "docs/20-design/DESIGN_BRIEF.md").write_text(
            generated_design_brief(plan)
        )
        for relative, content in generated_enterprise_artifacts(plan).items():
            destination = plan.destination / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content)
    (plan.destination / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n\nNo released project changes yet.\n"
    )
    reset_durable_state(plan)
    reset_design_state(plan)


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


def resolve_generated_profiles(root: Path, selected: list[str]) -> dict[str, Any]:
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
        profile_engine.PROJECT_PATH = root / PROJECT_PATH
        profile_engine.RESOURCES_PATH = root / ".agentic" / "resources.json"
        profile_engine.MCP_PATH = root / ".mcp.json"
        result = profile_engine.resolve(selected)
    except profile_engine.ProfileError as error:
        raise GenerationError(f"Current project profiles are invalid: {error}") from error
    finally:
        profile_engine.ROOT = original_root
        profile_engine.CONFIG_DIR = original_config
        profile_engine.PROFILES_DIR = original_profiles
        profile_engine.PROJECT_PATH = original_project
        profile_engine.RESOURCES_PATH = original_resources
        profile_engine.MCP_PATH = original_mcp
    if result["conflicts"]:
        raise GenerationError(
            "Current project profiles conflict: " + ", ".join(result["conflicts"])
        )
    return result


def validate_generated_project(root: Path, *, pristine: bool = False) -> dict[str, Any]:
    root = root.resolve()
    metadata = load_object(root / GENERATED_PATH, "generated-project metadata")
    project = load_object(root / PROJECT_PATH, "project manifest")
    package = load_object(root / "package.json", "package metadata")
    mcp = load_object(root / ".mcp.json", "MCP configuration")
    if metadata.get("schema_version") != 1:
        raise GenerationError("Unsupported generated-project metadata schema")
    selected = metadata.get("selected_profiles")
    resolved = metadata.get("resolved_profiles")
    if (
        not isinstance(selected, list)
        or not selected
        or not all(isinstance(item, str) and item for item in selected)
        or not isinstance(resolved, list)
        or not resolved
        or not all(isinstance(item, str) and item for item in resolved)
    ):
        raise GenerationError("Generated profile metadata must contain non-empty string arrays")
    current_selected = project.get("profiles")
    if (
        not isinstance(current_selected, list)
        or not current_selected
        or not all(isinstance(item, str) and item for item in current_selected)
    ):
        raise GenerationError("Project profiles must remain a non-empty string array")
    current_resolution = resolve_generated_profiles(root, current_selected)
    current_resolved = current_resolution["resolved_profiles"]
    if pristine and current_selected != selected:
        raise GenerationError("Generated project profiles do not match provenance")
    if pristine and current_resolved != resolved:
        raise GenerationError("Generated resolved profiles do not match provenance")
    specialists = project.get("specialists")
    if not isinstance(specialists, list) or not all(
        isinstance(item, str) and item for item in specialists
    ):
        raise GenerationError("Project specialists must remain a string array")
    if len(specialists) != len(set(specialists)):
        raise GenerationError("Project specialists must not contain duplicates")
    if pristine and specialists:
        raise GenerationError("Generated projects must not activate external specialists")
    try:
        specialist_catalog = agent_broker.specialist_index(agent_broker.load_manifest(root))
    except agent_broker.BrokerError as error:
        raise GenerationError(f"Specialist catalog validation failed: {error}") from error
    unknown_specialists = sorted(set(specialists).difference(specialist_catalog))
    if unknown_specialists:
        raise GenerationError(
            "Unknown activated specialist: " + ", ".join(unknown_specialists)
        )
    for specialist_id in specialists:
        required_profiles = set(specialist_catalog[specialist_id]["profiles_any_of"])
        if not required_profiles.intersection(current_resolved):
            raise GenerationError(
                f"Activated specialist {specialist_id} does not match the current profiles"
            )
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
    if "web-next" in current_resolved:
        required_scripts = {
            "dev",
            "build",
            "lint",
            "typecheck",
            "test",
            "test:e2e",
            "test:visual",
            "test:visual:update",
        }
        if not required_scripts.issubset(set(package.get("scripts", {}))):
            raise GenerationError("Generated web project is missing runnable root scripts")
        web_package = load_object(root / "apps/web/package.json", "web package metadata")
        if web_package.get("name") != "@everything-agentic/web":
            raise GenerationError("Generated web package identity is invalid")
        if not (root / "pnpm-lock.yaml").is_file():
            raise GenerationError("Generated web project is missing the reviewed dependency lockfile")
        if not (root / ".github/workflows/web-quality.yml").is_file():
            raise GenerationError("Generated web project is missing its visual-quality workflow")
        experience = load_object(root / EXPERIENCE_PATH, "experience manifest")
        if experience.get("schema_version") != 1:
            raise GenerationError("Unsupported experience-manifest schema")
        if pristine and experience.get("name") != metadata["project"]["name"]:
            raise GenerationError("Experience identity does not match generated project")
        if not isinstance(experience.get("name"), str) or not experience["name"].strip():
            raise GenerationError("Web experience is missing its product name")
        if experience.get("archetype") not in WEB_ARCHETYPES:
            raise GenerationError("Generated web experience has an invalid archetype")
        if experience.get("visual_character") not in VISUAL_CHARACTERS:
            raise GenerationError("Generated web experience has an invalid visual character")
        for field in ("audience", "promise"):
            if not isinstance(experience.get(field), str) or not experience[field].strip():
                raise GenerationError(f"Generated web experience is missing {field}")
        enterprise = load_object(root / ENTERPRISE_PATH, "enterprise manifest")
        if enterprise.get("schema_version") != 1 or not isinstance(
            enterprise.get("enabled"), bool
        ):
            raise GenerationError("Unsupported enterprise-manifest schema")
        enterprise_expected = experience.get("archetype") == "enterprise-workflow"
        if enterprise.get("enabled") is not enterprise_expected:
            raise GenerationError(
                "Enterprise manifest enablement must match the experience archetype"
            )
        if enterprise.get("tenant_model") not in TENANT_MODELS:
            raise GenerationError("Generated enterprise manifest has an invalid tenant model")
        if enterprise.get("approval_model") not in APPROVAL_MODELS:
            raise GenerationError("Generated enterprise manifest has an invalid approval model")
        if enterprise.get("data_sensitivity") not in DATA_SENSITIVITY_LEVELS:
            raise GenerationError(
                "Generated enterprise manifest has an invalid data-sensitivity level"
            )
        required_roles = {"requester", "reviewer", "auditor", "admin"}
        if set(enterprise.get("roles", [])) != required_roles:
            raise GenerationError("Generated enterprise manifest has an invalid role contract")
        adapters = enterprise.get("adapters")
        if adapters != {
            "authentication": "local-demo",
            "persistence": "local-demo",
            "notifications": "disabled",
            "production_ready": False,
        }:
            raise GenerationError("Generated enterprise adapters must remain explicitly local")
        if enterprise_expected:
            business_object = enterprise.get("business_object")
            if not isinstance(business_object, dict) or not all(
                isinstance(business_object.get(field), str)
                and business_object[field].strip()
                for field in ("singular", "plural")
            ):
                raise GenerationError("Generated enterprise business object is incomplete")
            required_artifacts = (
                "docs/10-product/PRD.md",
                "docs/10-product/ACCEPTANCE_CRITERIA.md",
                "docs/10-product/USER_JOURNEYS.md",
                "docs/30-engineering/ROLE_MATRIX.md",
                "docs/30-engineering/DATA_MODEL.md",
                "docs/30-engineering/API_CONTRACTS.md",
                "docs/30-engineering/SECURITY_MODEL.md",
                "docs/30-engineering/AUDIT_EVENTS.md",
                "docs/40-execution/INITIAL_TASK_GRAPH.md",
            )
            for relative in required_artifacts:
                artifact = root / relative
                if not artifact.is_file() or "Generated from `.agentic/enterprise.json`" not in artifact.read_text():
                    raise GenerationError(
                        f"Generated enterprise project is missing its contract: {relative}"
                    )
        env_text = (root / ".env.example").read_text()
        if "Mara Voss" in env_text or "NEXT_PUBLIC_PORTFOLIO_" in env_text:
            raise GenerationError("Generated web environment contains starter portfolio identity")
    elif (root / ".github/workflows/web-quality.yml").exists():
        raise GenerationError("Inactive web project contains its visual-quality workflow")
    elif (root / EXPERIENCE_PATH).exists():
        raise GenerationError("Non-web generated project contains a web experience manifest")
    elif (root / ENTERPRISE_PATH).exists():
        raise GenerationError("Non-web generated project contains an enterprise manifest")
    if "mobile-expo" in current_resolved and not (root / "pnpm-lock.yaml").is_file():
        raise GenerationError("Generated mobile project is missing the reviewed dependency lockfile")
    if "design-critical" in current_resolved:
        design_state = load_object(root / ".agentic/design.json", "design state")
        intake_state = load_object(root / ".agentic/design-intake.json", "design intake")
        if design_state.get("schema_version") != 1:
            raise GenerationError("Unsupported design-state schema")
        direction_ids = {
            item.get("id")
            for item in load_object(
                root / ".agentic/design-directions.json", "design-direction catalog"
            ).get("directions", [])
            if isinstance(item, dict)
        }
        design_status = design_state.get("status")
        approved_direction = design_state.get("approved_direction")
        if pristine and (design_status != "needs_approval" or approved_direction is not None):
            raise GenerationError("Generated design direction must begin unapproved")
        if not pristine:
            if design_status == "needs_approval" and approved_direction is not None:
                raise GenerationError("Unapproved design state cannot name a direction")
            if design_status == "approved" and approved_direction not in direction_ids:
                raise GenerationError("Approved design state must name a catalog direction")
            if design_status not in {"needs_approval", "approved"}:
                raise GenerationError("Unsupported ongoing design status")
        expected_intake = "captured" if "web-next" in current_resolved else "not_started"
        if pristine and intake_state.get("status") != expected_intake:
            raise GenerationError(
                f"Generated design intake must begin {expected_intake.replace('_', ' ')}"
            )
        if not pristine and intake_state.get("status") not in {
            "not_started",
            "captured",
            "complete",
        }:
            raise GenerationError("Unsupported ongoing design-intake status")
    if pristine and mcp != {"mcpServers": {}}:
        raise GenerationError("Generated projects must not enable MCP servers")
    if not isinstance(mcp.get("mcpServers"), dict):
        raise GenerationError("MCP configuration must contain a server object")
    try:
        mcp_compatibility.validate(root, allow_disabled=True)
    except mcp_compatibility.MCPCompatibilityError as error:
        raise GenerationError(f"MCP compatibility validation failed: {error}") from error
    prohibited = ["apps/showcase", "docs/80-showcase"]
    if pristine:
        prohibited.extend([".git", ".env", "node_modules"])
    for path in prohibited:
        if (root / path).exists():
            raise GenerationError(f"Generated project contains prohibited path: {path}")
    if pristine:
        for path in metadata.get("included_managed_paths", []):
            if not (root / path).exists():
                raise GenerationError(f"Expected selected path is missing: {path}")
        for path in metadata.get("excluded_managed_paths", []):
            if (root / path).exists():
                raise GenerationError(f"Inactive profile path is present: {path}")
    tasks = root / "docs/40-execution/TASKS.jsonl"
    if not tasks.is_file():
        raise GenerationError("Generated project is missing its task ledger")
    if pristine and tasks.read_text() != "":
        raise GenerationError("Generated task ledger must start empty")
    if not (root / "README.md").is_file() or metadata["project"]["name"] not in (
        root / "README.md"
    ).read_text():
        raise GenerationError("Generated README does not contain the project identity")
    for path in root.rglob("*.json"):
        if any(part in TRANSIENT_NAMES for part in path.relative_to(root).parts):
            continue
        try:
            json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise GenerationError(f"Invalid JSON document at {path}: {error}") from error
    validate_symlinks(root)
    return {
        "status": "PASS",
        "project": metadata["project"],
        "profiles": current_resolved,
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
        return validate_generated_project(plan.destination, pristine=True)
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
    if plan.archetype:
        print("\nExperience brief:")
        print(f"  Archetype:   {plan.archetype}")
        print(f"  Audience:    {plan.audience}")
        print(f"  Promise:     {plan.promise}")
        print(f"  Character:   {plan.visual_character}")
    if plan.archetype == "enterprise-workflow":
        print("\nEnterprise boundary:")
        print(f"  Object:      {plan.business_object}")
        print(f"  Tenancy:     {plan.tenant_model}")
        print(f"  Approval:    {plan.approval_model}")
        print(f"  Sensitivity: {plan.data_sensitivity}")
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


def prompt_text(question: str, default: str, *, maximum: int = 180) -> str:
    while True:
        answer = input(f"{question}\n  [{default}]\n> ").strip() or default
        try:
            return clean_text(answer, question, maximum=maximum) or default
        except GenerationError as error:
            print(error)


def prompt_choice(question: str, choices: tuple[str, ...], default: str) -> str:
    print(question)
    for index, choice in enumerate(choices, start=1):
        marker = " (recommended)" if choice == default else ""
        print(f"  {index}. {choice}{marker}")
    while True:
        answer = input("> ").strip().lower()
        if not answer:
            return default
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1]
        if answer in choices:
            return answer
        print(f"Choose 1-{len(choices)} or type: {', '.join(choices)}")


def prompt_confirm(question: str) -> bool:
    return input(f"{question} [y/N] ").strip().lower() in {"y", "yes"}


def interactive_answers() -> argparse.Namespace:
    print("\nCreate something unmistakable.")
    print("Five product decisions shape the first running experience; enterprise boundaries appear only when relevant.\n")
    name = prompt_text("1/5  What is the project called?", "My Product", maximum=80)
    slug = slugify(name)
    destination = prompt_text(
        "2/5  Where should the new project live?",
        str(ROOT.parent / slug),
        maximum=500,
    )
    kind = prompt_choice(
        "3/5  What should people experience first?",
        ("product", "agentic-product", "enterprise-workflow", "portfolio", "mobile", "core"),
        "product",
    )
    web = kind in WEB_ARCHETYPES
    mobile = kind == "mobile"
    if web:
        default_audience, default_promise = experience_defaults(name, kind)
        audience = prompt_text("4/5  Who is this for?", default_audience, maximum=120)
        promise = prompt_text(
            "5/5  What should it help them achieve?",
            default_promise,
            maximum=120,
        )
        character = prompt_choice(
            "Choose the starting character; the live lab will still compare three systems.",
            VISUAL_CHARACTERS,
            "precise",
        )
        if kind == "enterprise-workflow":
            print("\nFour enterprise boundaries keep the generated workflow credible.")
            business_object = prompt_text(
                "6/9  What is the core business object?",
                "access request",
                maximum=80,
            )
            tenant_model = prompt_choice(
                "7/9  How is organizational data separated?",
                TENANT_MODELS,
                "multi-tenant",
            )
            approval_model = prompt_choice(
                "8/9  What decision control is required?",
                APPROVAL_MODELS,
                "dual-control",
            )
            data_sensitivity = prompt_choice(
                "9/9  What is the highest data sensitivity in this workflow?",
                DATA_SENSITIVITY_LEVELS,
                "confidential",
            )
        else:
            business_object = None
            tenant_model = None
            approval_model = None
            data_sensitivity = None
    else:
        audience = None
        promise = None
        character = None
        business_object = None
        tenant_model = None
        approval_model = None
        data_sensitivity = None
    return argparse.Namespace(
        name=name,
        destination=destination,
        preset=None,
        web=web,
        mobile=mobile,
        design=web or mobile,
        research=False,
        agentic=kind == "agentic-product",
        backend="none",
        archetype=kind if web else None,
        audience=audience,
        promise=promise,
        visual_character=character,
        business_object=business_object,
        tenant_model=tenant_model,
        approval_model=approval_model,
        data_sensitivity=data_sensitivity,
        json=False,
        dry_run=False,
        yes=False,
        interactive=True,
    )


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
    value.add_argument("--archetype", choices=WEB_ARCHETYPES)
    value.add_argument("--audience")
    value.add_argument("--promise")
    value.add_argument("--visual-character", choices=VISUAL_CHARACTERS)
    value.add_argument("--business-object")
    value.add_argument("--tenant-model", choices=TENANT_MODELS)
    value.add_argument("--approval-model", choices=APPROVAL_MODELS)
    value.add_argument("--data-sensitivity", choices=DATA_SENSITIVITY_LEVELS)
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
        archetype=args.archetype,
        audience=args.audience,
        promise=args.promise,
        visual_character=args.visual_character,
        business_object=args.business_object,
        tenant_model=args.tenant_model,
        approval_model=args.approval_model,
        data_sensitivity=args.data_sensitivity,
    )
    if not args.json:
        print_plan(plan)
    if args.dry_run:
        if args.json:
            print(json.dumps(plan.public_report(), indent=2))
        else:
            print("\nDry run complete; no files changed.")
        return 0
    if getattr(args, "interactive", False):
        print("\nOne confirmation creates the new directory. Nothing is installed or enabled.")
        if not prompt_confirm("Create this project?"):
            print("No project created.")
            return 0
        args.yes = True
    if not args.yes:
        if not args.json:
            print("\nNo project created. Re-run with --yes after reviewing this plan.")
        return 2
    report = materialize(plan)
    if args.json:
        print(
            json.dumps(
                {
                    "plan": plan.public_report(),
                    "created": str(plan.destination),
                    "verification": report,
                },
                indent=2,
            )
        )
    else:
        print(f"\nCreated {plan.project_name} at {plan.destination}")
        print("Generated-project verification: PASS")
        print(f"\nNext: cd {plan.destination} && ./agentic next")
    return 0


def main() -> int:
    try:
        args = interactive_answers() if len(sys.argv) == 1 else parser().parse_args()
        return run(args)
    except (GenerationError, profile_engine.ProfileError, OSError, EOFError, KeyboardInterrupt) as error:
        print(f"Project generator error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
