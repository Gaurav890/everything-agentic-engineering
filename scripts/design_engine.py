#!/usr/bin/env python3
"""Run the bounded design intake, comparison, and approval workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import project_brief
import project_handoff

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / ".agentic/design.json"
INTAKE_PATH = ROOT / ".agentic/design-intake.json"
CATALOG_PATH = ROOT / ".agentic/design-directions.json"
RESOURCES_PATH = ROOT / ".agentic/design-resources.json"
ASSETS_PATH = ROOT / ".agentic/design-assets.json"
CUSTOM_TEXT_FIELDS = (
    "composition",
    "interaction",
    "rationale",
    "axis",
    "signature",
    "asset_strategy",
    "asset_role",
    "asset_alternatives",
    "motion_rationale",
    "motion_interruption",
    "motion_performance_budget",
    "responsive_strategy",
    "reduced_motion",
)
STARTER_DEMO_SOURCES = {
    "apps/web/app/product-lab.tsx",
    "apps/web/app/portfolio-lab.tsx",
    "apps/web/app/enterprise-lab.tsx",
    "apps/web/app/project-studio.tsx",
}
RESOURCE_KINDS = {
    "human_operated_decision_aid",
    "human_operated_asset_generator",
    "optional_component_source",
}
RESOURCE_PHASES = {
    "design-intake",
    "design-directions",
    "component-translation",
    "implementation",
    "live-iteration",
}
RESOURCE_PLATFORMS = {"web", "mobile"}
RESOURCE_NEEDS = {"palette", "typography", "assets", "motion"}
TERMINAL_CONTROL_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f]")


class DesignError(ValueError):
    """Raised when design state violates the review contract."""


def load_object(path: Path) -> dict[str, Any]:
    if path.is_symlink() or path.parent.is_symlink():
        raise DesignError(f"Design data must not follow symlinks: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise DesignError(f"Cannot read valid design data from {path}: {error}") from error
    if not isinstance(value, dict):
        raise DesignError(f"Design data must be an object: {path}")
    return value


def load_resource_catalog(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the reviewed external-design resource contract fail closed."""
    location = path or RESOURCES_PATH
    payload = load_object(location)
    if payload.get("schema_version") != 1:
        raise DesignError("Unsupported design-resource catalog schema")
    policy = payload.get("policy")
    required_policy = {
        "automatic_browser_open": False,
        "automatic_browser_submission": False,
        "automatic_network_request": False,
        "automatic_external_execution": False,
        "automatic_external_copy": False,
        "automatic_authentication": False,
        "automatic_credential_access": False,
        "automatic_project_write": False,
        "automatic_install": False,
        "automatic_download": False,
        "external_sources_are_untrusted": True,
        "project_design_system_wins": True,
        "human_approval_before_canonical_tokens": True,
    }
    if (
        not isinstance(policy, dict)
        or set(policy) != set(required_policy)
        or any(type(policy[key]) is not bool or policy[key] is not expected for key, expected in required_policy.items())
    ):
        raise DesignError("Design-resource policy weakens a required safety boundary")
    resources = payload.get("resources")
    if not isinstance(resources, list) or not resources:
        raise DesignError("Design-resource catalog must contain reviewed resources")
    seen: set[str] = set()
    for resource in resources:
        if not isinstance(resource, dict):
            raise DesignError("Every design resource must be an object")
        expected_fields = {
            "id", "name", "kind", "phases", "platforms", "needs", "source",
            "trigger", "prerequisites", "bring_back", "return_to", "forbidden",
        }
        if set(resource) != expected_fields:
            raise DesignError("Design resource has missing or unknown fields")
        _reject_terminal_controls(resource, "design resource")
        resource_id = resource.get("id")
        if not isinstance(resource_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", resource_id):
            raise DesignError("Design resource ids must use lowercase kebab-case")
        if resource_id in seen:
            raise DesignError(f"Duplicate design resource: {resource_id}")
        seen.add(resource_id)
        if resource.get("kind") not in RESOURCE_KINDS:
            raise DesignError(f"Unsupported design-resource kind: {resource_id}")
        for field, allowed in (
            ("phases", RESOURCE_PHASES),
            ("platforms", RESOURCE_PLATFORMS),
            ("needs", RESOURCE_NEEDS),
        ):
            values = resource.get(field)
            if (not isinstance(values, list) or not values
                    or not all(isinstance(item, str) and item in allowed for item in values)
                    or len(values) != len(set(values))):
                raise DesignError(f"Invalid {field} for design resource: {resource_id}")
        source = resource.get("source")
        if not isinstance(source, dict) or set(source) != {
            "canonical_url", "repository_url", "reviewed_revision", "reviewed_at",
            "maintenance", "license",
        }:
            raise DesignError(f"Invalid source record for design resource: {resource_id}")
        for url_field in ("canonical_url", "repository_url"):
            url = source.get(url_field)
            if url is not None and (not isinstance(url, str) or not url.startswith("https://")):
                raise DesignError(f"Design-resource URLs must use HTTPS: {resource_id}")
        revision = source.get("reviewed_revision")
        if revision is not None and (not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision)):
            raise DesignError(f"Invalid reviewed revision for design resource: {resource_id}")
        if not isinstance(source.get("reviewed_at"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["reviewed_at"]):
            raise DesignError(f"Invalid reviewed date for design resource: {resource_id}")
        for field in ("maintenance", "license"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise DesignError(f"Design resource requires source {field}: {resource_id}")
        for field in ("name", "trigger"):
            if not isinstance(resource.get(field), str) or not resource[field].strip():
                raise DesignError(f"Design resource requires {field}: {resource_id}")
        for field in ("prerequisites", "bring_back", "return_to", "forbidden"):
            values = resource.get(field)
            if not isinstance(values, list) or not values or not all(isinstance(item, str) and item.strip() for item in values):
                raise DesignError(f"Design resource requires {field}: {resource_id}")
    return resources


def _reject_terminal_controls(value: Any, label: str) -> None:
    if isinstance(value, str) and TERMINAL_CONTROL_PATTERN.search(value):
        raise DesignError(f"{label} contains terminal control characters")
    if isinstance(value, list):
        for item in value:
            _reject_terminal_controls(item, label)
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_terminal_controls(key, label)
            _reject_terminal_controls(item, label)


def _meaningful_decision(value: Any) -> bool:
    """Reject empty and placeholder prose used to spoof a design gate."""
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    if normalized in {
        "none", "no", "n a", "na", "not applicable", "unknown", "undecided",
        "tbd", "todo", "placeholder", "later", "skip", "skipped",
    }:
        return False
    return bool(normalized)


def _dtcg_leaf_names(node: Any, path: tuple[str, ...] = ()) -> set[str]:
    if not isinstance(node, dict):
        return set()
    if "$value" in node:
        return {".".join(path)}
    names: set[str] = set()
    for key, child in node.items():
        if not key.startswith("$"):
            names.update(_dtcg_leaf_names(child, path + (key,)))
    return names


def _canonical_semantic_token_roles(root: Path) -> set[str]:
    token_root = root / "packages/design-tokens/tokens/semantic"
    paths = sorted(token_root.glob("*.json")) if token_root.is_dir() else []
    if not paths:
        raise DesignError("Canonical semantic token files are missing")
    roles: set[str] = set()
    for path in paths:
        roles.update(_dtcg_leaf_names(load_object(path)))
    if not roles:
        raise DesignError("Canonical semantic token catalog is empty")
    return roles


def _asset_dimensions(path: Path) -> tuple[int, int]:
    """Read intrinsic PNG dimensions or an SVG numeric viewport."""
    data = path.read_bytes()
    if path.suffix.lower() == ".png":
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            raise DesignError("Generated PNG has no valid IHDR dimensions")
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    header = data[:16384].decode("utf-8", errors="strict")
    svg = re.search(r"<svg\b([^>]*)>", header, re.IGNORECASE)
    if not svg:
        raise DesignError("Generated SVG has no root svg element")
    attributes = svg.group(1)
    view_box = re.search(r"\bviewBox\s*=\s*['\"]\s*[-+0-9.eE]+\s+[-+0-9.eE]+\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*['\"]", attributes)
    if view_box:
        width, height = float(view_box.group(1)), float(view_box.group(2))
    else:
        width_match = re.search(r"\bwidth\s*=\s*['\"]([0-9]+(?:\.[0-9]+)?)(?:px)?['\"]", attributes)
        height_match = re.search(r"\bheight\s*=\s*['\"]([0-9]+(?:\.[0-9]+)?)(?:px)?['\"]", attributes)
        if not width_match or not height_match:
            raise DesignError("Generated SVG requires numeric width/height or viewBox dimensions")
        width, height = float(width_match.group(1)), float(height_match.group(1))
    if not width.is_integer() or not height.is_integer() or width <= 0 or height <= 0:
        raise DesignError("Generated asset dimensions must be positive whole pixels")
    return int(width), int(height)


def load_asset_catalog(root: Path, path: Path | None = None) -> list[dict[str, Any]]:
    """Validate project-owned records for generated visual assets."""
    location = path or root / ".agentic/design-assets.json"
    payload = load_object(location)
    if set(payload) != {"schema_version", "assets"} or payload.get("schema_version") != 1:
        raise DesignError("Unsupported design-asset catalog schema")
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise DesignError("Design-asset catalog must contain an asset list")
    expected_fields = {
        "id", "source_id", "source_url", "source_revision", "created_at",
        "generator", "parameters", "file", "dimensions", "file_sha256", "token_roles", "placement",
        "responsive_behavior", "dark_mode_behavior", "semantics", "alt_text",
        "license_basis", "evidence",
    }
    seen: set[str] = set()
    for asset in assets:
        if not isinstance(asset, dict) or set(asset) != expected_fields:
            raise DesignError("Every design asset must match the reviewed asset schema")
        _reject_terminal_controls(asset, "design asset")
        identity = asset.get("id")
        if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identity):
            raise DesignError("Design asset ids must use lowercase kebab-case")
        if identity in seen:
            raise DesignError(f"Duplicate design asset: {identity}")
        seen.add(identity)
        if asset.get("source_id") != "haikei":
            raise DesignError(f"Unsupported generated-asset source: {identity}")
        if not isinstance(asset.get("source_url"), str) or not asset["source_url"].startswith("https://haikei.app/"):
            raise DesignError(f"Design asset requires the canonical Haikei source: {identity}")
        revision = asset.get("source_revision")
        if revision is not None and (not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision)):
            raise DesignError(f"Invalid generated-asset source revision: {identity}")
        if not isinstance(asset.get("created_at"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", asset["created_at"]):
            raise DesignError(f"Invalid generated-asset date: {identity}")
        for field in ("generator", "placement", "responsive_behavior", "dark_mode_behavior", "license_basis"):
            if not isinstance(asset.get(field), str) or not asset[field].strip():
                raise DesignError(f"Design asset requires {field}: {identity}")
        parameters = asset.get("parameters")
        if not isinstance(parameters, dict) or not parameters:
            raise DesignError(f"Design asset requires generator parameters: {identity}")
        if not all(isinstance(key, str) and key.strip() and type(value) in {str, int, float, bool}
                   for key, value in parameters.items()):
            raise DesignError(f"Design asset parameters must be scalar values: {identity}")
        if any(type(value) is float and not math.isfinite(value) for value in parameters.values()):
            raise DesignError(f"Design asset parameters must be finite: {identity}")
        relative = asset.get("file")
        if not isinstance(relative, str):
            raise DesignError(f"Design asset requires a project-local file: {identity}")
        relative_path = Path(relative)
        if (
            relative_path.is_absolute()
            or ".." in relative_path.parts
            or not relative.startswith(("apps/", "packages/", "docs/assets/"))
            or any((root / Path(*relative_path.parts[:index])).is_symlink()
                   for index in range(1, len(relative_path.parts) + 1))
        ):
            raise DesignError(f"Design asset file must stay in an approved project path: {identity}")
        target = root / relative_path
        if not target.is_file() or target.suffix.lower() not in {".svg", ".png"}:
            raise DesignError(f"Design asset file must be an existing SVG or PNG: {identity}")
        dimensions = asset.get("dimensions")
        if (
            not isinstance(dimensions, dict)
            or set(dimensions) != {"width", "height", "unit"}
            or type(dimensions.get("width")) is not int
            or type(dimensions.get("height")) is not int
            or dimensions["width"] <= 0
            or dimensions["height"] <= 0
            or dimensions.get("unit") != "px"
        ):
            raise DesignError(f"Design asset requires positive pixel dimensions: {identity}")
        if (dimensions["width"], dimensions["height"]) != _asset_dimensions(target):
            raise DesignError(f"Design asset dimensions do not match its file: {identity}")
        file_sha256 = asset.get("file_sha256")
        if not isinstance(file_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", file_sha256):
            raise DesignError(f"Design asset requires a SHA-256 file digest: {identity}")
        if hashlib.sha256(target.read_bytes()).hexdigest() != file_sha256:
            raise DesignError(f"Design asset file digest is stale: {identity}")
        token_roles = asset.get("token_roles")
        if not isinstance(token_roles, list) or not token_roles or not all(
            isinstance(role, str) and re.fullmatch(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*", role)
            for role in token_roles
        ):
            raise DesignError(f"Design asset requires semantic token roles: {identity}")
        unknown_roles = sorted(set(token_roles) - _canonical_semantic_token_roles(root))
        if unknown_roles:
            raise DesignError(f"Design asset uses unknown semantic token roles: {identity}: {', '.join(unknown_roles)}")
        if asset.get("semantics") not in {"decorative", "meaningful"}:
            raise DesignError(f"Design asset semantics must be decorative or meaningful: {identity}")
        alt_text = asset.get("alt_text")
        if asset["semantics"] == "meaningful" and (not isinstance(alt_text, str) or not alt_text.strip()):
            raise DesignError(f"Meaningful design asset requires alt text: {identity}")
        if asset["semantics"] == "decorative" and alt_text is not None:
            raise DesignError(f"Decorative design asset must use null alt text: {identity}")
        evidence = asset.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise DesignError(f"Design asset requires running-product evidence: {identity}")
        for record in evidence:
            if not isinstance(record, dict) or set(record) != {"file", "sha256"}:
                raise DesignError(f"Design asset evidence must contain file and sha256: {identity}")
            evidence_path = record.get("file")
            evidence_target = evidence_file(root, evidence_path)
            evidence_sha256 = record.get("sha256")
            if not isinstance(evidence_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", evidence_sha256):
                raise DesignError(f"Design asset evidence requires a SHA-256 digest: {identity}")
            if hashlib.sha256(evidence_target.read_bytes()).hexdigest() != evidence_sha256:
                raise DesignError(f"Design asset evidence digest is stale: {identity}")
    return assets


def _active_platforms(root: Path) -> list[str]:
    project = load_object(root / ".agentic/project.json")
    profiles = project.get("profiles")
    if not isinstance(profiles, list) or not all(isinstance(item, str) for item in profiles):
        raise DesignError("Project profiles must be a string list")
    platforms: list[str] = []
    if "web-next" in profiles:
        platforms.append("web")
    if "mobile-expo" in profiles:
        platforms.append("mobile")
    return platforms


def _text_has_meaningful_motion(value: Any) -> bool:
    return _meaningful_decision(value) and re.sub(r"[^a-z]+", " ", value.lower()).strip() != "no motion"


def _asset_route_is_relevant(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return any(term in value.lower() for term in (
        "svg", "generated", "abstract", "background", "texture", "pattern",
        "wave", "blob", "gradient", "geometric",
    ))


def _decision_is_open(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return True
    normalized = re.sub(r"[^a-z]+", " ", value.lower()).strip()
    return normalized in {"open", "undecided", "unknown", "not decided", "recommend for me"}


def _asset_contract_is_ready(direction: dict[str, Any] | None) -> bool:
    return bool(
        direction
        and _asset_route_is_relevant(direction.get("asset_strategy"))
        and _meaningful_decision(direction.get("asset_role"))
        and _meaningful_decision(direction.get("asset_alternatives"))
    )


def _design_resource_context(root: Path, explicit_phase: str | None, explicit_needs: list[str] | None) -> dict[str, Any]:
    intake = load_object(root / ".agentic/design-intake.json")
    state = load_object(root / ".agentic/design.json")
    catalog = load_catalog(root / ".agentic/design-directions.json")
    design_status = state.get("status")
    approval_valid = False
    try:
        validate_state(state, catalog, root)
        approval_valid = design_status == "approved"
    except DesignError:
        if design_status == "approved":
            design_status = "stale_approval"
    phase = explicit_phase
    if phase is None:
        if intake.get("status") != "complete":
            phase = "design-intake"
        elif not approval_valid:
            phase = "design-directions"
        else:
            phase = "implementation"
    needs = set(explicit_needs or [])
    answers = intake.get("answers") if isinstance(intake.get("answers"), dict) else {}
    selected = catalog.get(state.get("approved_direction")) if approval_valid else None
    candidates = list(catalog.values())
    palette_open = _decision_is_open(answers.get("color_intent"))
    typography_open = _decision_is_open(answers.get("typography"))
    relevant_directions = [selected] if selected else candidates
    asset_contract_ready = any(_asset_contract_is_ready(item) for item in relevant_directions if item)
    if not explicit_needs:
        if phase == "design-intake":
            if palette_open:
                needs.add("palette")
            if typography_open:
                needs.add("typography")
        if asset_contract_ready:
            needs.add("assets")
        if any(_text_has_meaningful_motion(item.get("motion")) and _meaningful_decision(item.get("motion_rationale"))
               and _meaningful_decision(item.get("motion_interruption"))
               and _meaningful_decision(item.get("motion_performance_budget"))
               and _meaningful_decision(item.get("reduced_motion"))
               for item in relevant_directions if item):
            needs.add("motion")
    motion_contract_ready = bool(selected and _text_has_meaningful_motion(selected.get("motion"))
                                 and _meaningful_decision(selected.get("motion_rationale"))
                                 and _meaningful_decision(selected.get("motion_interruption"))
                                 and _meaningful_decision(selected.get("motion_performance_budget"))
                                 and _meaningful_decision(selected.get("reduced_motion")))
    return {
        "phase": phase,
        "needs": sorted(needs),
        "platforms": _active_platforms(root),
        "design_status": design_status,
        "approved_direction": state.get("approved_direction") if approval_valid else None,
        "palette_open": palette_open,
        "typography_open": typography_open,
        "asset_contract_ready": asset_contract_ready,
        "motion_contract_ready": motion_contract_ready,
    }


def design_resource_plan(
    root: Path,
    *,
    phase: str | None = None,
    needs: list[str] | None = None,
    catalog_path: Path | None = None,
) -> dict[str, Any]:
    context = _design_resource_context(root, phase, needs)
    decisions: list[dict[str, Any]] = []
    for resource in load_resource_catalog(catalog_path or root / ".agentic/design-resources.json"):
        matching_needs = sorted(set(resource["needs"]).intersection(context["needs"]))
        state = "optional"
        reason = "Current project evidence does not justify this resource."
        if matching_needs:
            if not set(resource["platforms"]).intersection(context["platforms"]):
                state = "not_applicable"
                reason = "The active project platform is not supported by this resource."
            elif context["phase"] not in resource["phases"]:
                state = "deferred"
                reason = f"The need is present, but this resource belongs in {', '.join(resource['phases'])}."
            elif resource["id"] == "realtime-colors" and not any(
                (need == "palette" and context["palette_open"])
                or (need == "typography" and context["typography_open"])
                for need in matching_needs
            ):
                state = "deferred"
                reason = "Record palette or typography as unresolved in design intake before reopening exploration."
            elif resource["id"] == "haikei" and not context["asset_contract_ready"]:
                state = "deferred"
                reason = "First register a candidate with a product-specific generated-asset role and the alternatives considered."
            elif resource["id"] == "motion-primitives" and (
                context["design_status"] != "approved" or not context["motion_contract_ready"]
            ):
                state = "deferred"
                reason = "Approve a direction with purpose, interruption or reversal, performance budget, and reduced-motion behavior before selecting motion code."
            else:
                state = "recommended"
                reason = resource["trigger"]
        decisions.append({
            "id": resource["id"],
            "name": resource["name"],
            "state": state,
            "matching_needs": matching_needs,
            "reason": reason,
            "url": resource["source"]["canonical_url"],
            "source": resource["source"],
            "human_action_required": state in {"recommended", "deferred"},
            "prerequisites": resource["prerequisites"] if state in {"recommended", "deferred"} else [],
            "bring_back": resource["bring_back"] if state == "recommended" else [],
            "return_to": resource["return_to"] if state in {"recommended", "deferred"} else [],
            "forbidden": resource["forbidden"],
        })
    return {
        "schema_version": 1,
        "operation": "design-resource-plan",
        "context": context,
        "decisions": decisions,
        "mutation_performed": False,
        "browser_opened": False,
        "network_request_performed": False,
        "download_performed": False,
        "installation_performed": False,
    }


def load_catalog(path: Path | None = None) -> dict[str, dict[str, Any]]:
    location = path or CATALOG_PATH
    root = location.parent.parent
    payload = load_object(location)
    if payload.get("schema_version") not in {1, 2} or not isinstance(payload.get("directions"), list):
        raise DesignError("Unsupported design-direction catalog schema")
    custom = payload.get("schema_version") == 2 and payload.get("mode") != "reference"
    if (root / project_brief.BRIEF_PATH).exists():
        try:
            brief = project_brief.load(root)
        except project_brief.BriefError as error:
            raise DesignError(str(error)) from error
        if brief["design_mode"] != "reference":
            if payload.get("schema_version") != 2 or payload.get("mode") != brief["design_mode"]:
                raise DesignError("Custom project catalog must match the saved design mode")
            custom = True
    result: dict[str, dict[str, Any]] = {}
    for direction in payload["directions"]:
        if not isinstance(direction, dict):
            raise DesignError("Every design direction must be an object")
        direction_id = direction.get("id")
        if not isinstance(direction_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", direction_id):
            raise DesignError("Every design direction needs a kebab-case id")
        if direction_id in result:
            raise DesignError(f"Duplicate design direction: {direction_id}")
        for field in ("name", "thesis", "motion"):
            if not isinstance(direction.get(field), str) or not direction[field].strip():
                raise DesignError(f"Direction requires {field}")
        tokens = direction.get("tokens")
        if not isinstance(tokens, dict) or not tokens:
            raise DesignError(f"Design direction has no tokens: {direction_id}")
        for name, token in tokens.items():
            if not isinstance(name, str) or not isinstance(token, dict):
                raise DesignError(f"Invalid token in direction: {direction_id}")
            if "$type" not in token or "$value" not in token:
                raise DesignError(f"Direction token is not DTCG-compatible: {direction_id}.{name}")
            if not re.fullmatch(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*", name):
                raise DesignError("Token names must be lowercase semantic paths")
            token_to_css(token)
        if len({variable_name(name) for name in tokens}) != len(tokens):
            raise DesignError("Direction token names collide after CSS normalization")
        if custom:
            validate_custom_candidate(direction, root)
        result[direction_id] = direction
    if custom and len(result) > 1:
        axes = [re.sub(r"\s+", " ", value["axis"].strip().lower()) for value in result.values()]
        if len(axes) != len(set(axes)):
            raise DesignError("Custom candidates must diverge on distinct named axes")
    return result


def validate_state(state: dict[str, Any], catalog: dict[str, dict[str, Any]], root: Path | None = None) -> None:
    root = root or ROOT
    if state.get("schema_version") != 1:
        raise DesignError("Unsupported design-state schema")
    status = state.get("status")
    approved = state.get("approved_direction")
    if status == "needs_approval" and approved is not None:
        raise DesignError("Unapproved design state cannot name an approved direction")
    if status == "approved" and (not isinstance(approved, str) or approved not in catalog):
        raise DesignError("Approved design state must reference a catalog direction")
    if status not in ("needs_approval", "approved"):
        raise DesignError(f"Unsupported design status: {status}")
    if status == "approved":
        if not state.get("approved_by") or not state.get("approved_at"):
            raise DesignError("Approval requires a named reviewer and timestamp")
        evidence = state.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise DesignError("Approval has no reviewed evidence; re-review the direction")
        actual = approval_fingerprint(root, catalog[approved], evidence)
        if actual != state.get("fingerprint"):
            raise DesignError("Design approval is stale; review the changed brief, candidate, source, or evidence")


def evidence_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str):
        raise DesignError("Evidence paths must be strings")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not relative.startswith("docs/50-evals/"):
        raise DesignError("Evidence must be a project-local path under docs/50-evals/")
    target = root / path
    if any((root / Path(*path.parts[:index])).is_symlink() for index in range(1, len(path.parts) + 1)):
        raise DesignError("Evidence cannot follow symlinks")
    if not target.is_file() or target.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".md"}:
        raise DesignError("Reviewed evidence must be an existing screenshot or review document")
    return target


def approval_fingerprint(root: Path, direction: dict, evidence: list[str]) -> str:
    if (root / project_brief.BRIEF_PATH).exists():
        try:
            brief = project_brief.load(root)
        except project_brief.BriefError as error:
            raise DesignError(str(error)) from error
        if brief["status"] != "ready":
            raise DesignError("Confirm the product brief with its owner before design approval")
    intake = load_object(root / ".agentic/design-intake.json")
    if intake.get("status") != "complete" or not isinstance(intake.get("answers"), dict):
        raise DesignError("Complete the design intake before approval")
    if any(not isinstance(intake["answers"].get(field), str) or not intake["answers"][field].strip()
           for field, _, _ in INTAKE_FIELDS):
        raise DesignError("Complete the missing design intake answers before approval")
    files = {}
    for relative in evidence:
        target = evidence_file(root, relative)
        files[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    if not any(Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} for path in evidence):
        raise DesignError("Approval requires at least one reviewed screenshot")
    for relative in direction.get("source_files", []):
        target = candidate_source(root, relative)
        files[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    for relative in (".agentic/project-brief.json", ".agentic/experience.json", ".agentic/enterprise.json"):
        target = root / relative
        if target.is_symlink():
            raise DesignError("Design context must not follow symlinks")
        if target.is_file():
            files[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    return project_brief.digest({"direction": direction, "intake": intake, "files": files})


def candidate_source(root: Path, relative: str) -> Path:
    if not isinstance(relative, str):
        raise DesignError("Candidate source paths must be strings")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not relative.startswith(("apps/", "packages/")):
        raise DesignError("Candidate source must stay inside apps/ or packages/")
    if path == Path("packages/design-tokens/generated/direction.css"):
        raise DesignError("direction.css is approval output, not source; list preview code and canonical token inputs instead")
    if any((root / Path(*path.parts[:index])).is_symlink() for index in range(1, len(path.parts) + 1)):
        raise DesignError("Candidate source cannot follow symlinks")
    target = root / path
    if not target.is_file() or target.suffix not in {".tsx", ".ts", ".jsx", ".js", ".html", ".css", ".json", ".svg", ".png", ".jpg", ".webp", ".woff2"}:
        raise DesignError("Candidate source must reference existing preview code")
    approval_output = root / "packages/design-tokens/generated/direction.css"
    if approval_output.is_file() and target.samefile(approval_output):
        raise DesignError("Candidate source aliases approval output; list preview code and canonical token inputs instead")
    return target


def validate_custom_candidate(direction: dict, root: Path) -> None:
    preview = direction.get("preview_path")
    if not isinstance(preview, str) or not re.fullmatch(r"/(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+/?", preview):
        raise DesignError("A custom candidate needs a local preview_path, not a remote URL")
    for field in CUSTOM_TEXT_FIELDS:
        if not _meaningful_decision(direction.get(field)):
            raise DesignError(f"A custom candidate requires a meaningful {field}")
    states = direction.get("states")
    if (
        not isinstance(states, list)
        or len(states) < 3
        or not all(isinstance(state, str) and state.strip() for state in states)
        or len({state.strip().lower() for state in states}) != len(states)
    ):
        raise DesignError("A custom candidate requires at least three distinct realistic states")
    sources = direction.get("source_files")
    if not isinstance(sources, list) or not sources:
        raise DesignError("Candidate requires source_files for its actual local preview and dependencies")
    for relative in sources:
        candidate_source(root, relative)
    preview_source = direction.get("preview_source")
    if not isinstance(preview_source, str) or preview_source not in sources:
        raise DesignError("Candidate preview_source must name its actual UI entry in source_files")
    if preview_source in STARTER_DEMO_SOURCES:
        raise DesignError("A custom candidate cannot reuse a starter demo as its preview source")
    preview_file = candidate_source(root, preview_source)
    if preview_file.suffix not in {".tsx", ".jsx", ".html"}:
        raise DesignError("Candidate preview_source must be an actual UI surface")


def save_object(path: Path, payload: dict) -> None:
    if path.is_symlink() or path.parent.is_symlink():
        raise DesignError("Design output must not follow symlinks")
    path.write_text(json.dumps(payload, indent=2) + "\n")


def validate_project(root: Path) -> dict[str, Any]:
    catalog = load_catalog(root / ".agentic/design-directions.json")
    state = load_object(root / ".agentic/design.json")
    validate_state(state, catalog, root)
    load_resource_catalog(root / ".agentic/design-resources.json")
    load_asset_catalog(root)
    return state


def prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{label}{suffix}: ").strip()
    return answer or default


INTAKE_FIELDS = (
    ("product_type", "What are you designing", "discuss with the product owner"),
    ("audience", "Primary audience", "discuss with the product owner"),
    ("personality", "Desired character and styles to avoid", "open; propose and review"),
    ("color_intent", "Color temperature (warm / cool / neutral / open)", "open"),
    ("color_expression", "Color expression (restrained / balanced / expressive)", "balanced"),
    ("typography", "Typography (editorial / grotesk / humanist / technical / open)", "open"),
    ("density", "Density (compact / balanced / comfortable)", "balanced"),
    ("motion", "Motion (restrained / balanced / expressive)", "balanced"),
    ("advanced_canvas", "Advanced canvas (none / 2d / 3d / both)", "none"),
    ("required_modes", "Required modes (light / dark / system)", "system"),
    ("constraints", "Brand, accessibility, content, or platform constraints", "none recorded"),
)


def run_intake(args: argparse.Namespace) -> int:
    existing = load_object(INTAKE_PATH).get("answers", {}) if INTAKE_PATH.exists() else {}
    if not isinstance(existing, dict):
        raise DesignError("Existing intake answers must be an object")
    answers = {key: value for key, value in existing.items() if isinstance(value, str) and value.strip()}
    provided = args.answer or []
    for entry in provided:
        if "=" not in entry:
            raise DesignError("--answer values must use field=value")
        field, value = entry.split("=", 1)
        if field not in {item[0] for item in INTAKE_FIELDS} or not value.strip():
            raise DesignError(f"Unknown or empty intake answer: {field}")
        answers[field] = value.strip()
    if not args.non_interactive:
        print("Design intake — answer only what materially constrains the experience.")
        for field, question, default in INTAKE_FIELDS:
            if field not in answers:
                answers[field] = prompt(question, default)
    missing = [field for field, _, _ in INTAKE_FIELDS if field not in answers]
    if missing:
        raise DesignError("Missing non-interactive intake answers: " + ", ".join(missing))
    payload = {"schema_version": 1, "status": "complete", "answers": answers}
    if not args.yes:
        print(json.dumps(payload, indent=2))
        print("No change made. Re-run with --yes after reviewing the intake.")
        return 2
    save_object(INTAKE_PATH, payload)
    print("Design intake recorded. Create or revise product-specific candidates with your assistant.")
    print("Existing approval, if any, must be re-reviewed after intake changes.")
    return 0


def color_to_css(value: dict[str, Any]) -> str:
    components = value.get("components")
    if value.get("colorSpace") != "srgb" or not isinstance(components, list) or len(components) != 3:
        raise DesignError("Direction color values must use DTCG sRGB components")
    alpha = value.get("alpha", 1)
    if any(type(item) not in {int, float} or not math.isfinite(item) or not 0 <= item <= 1 for item in [*components, alpha]):
        raise DesignError("Color components and alpha must be finite numbers between zero and one")
    rgb = [round(component * 255) for component in components]
    return f"rgb({rgb[0]} {rgb[1]} {rgb[2]} / {alpha})"


def token_to_css(token: dict[str, Any]) -> str:
    token_type = token["$type"]
    value = token["$value"]
    if token_type == "color" and isinstance(value, dict):
        return color_to_css(value)
    if token_type in {"dimension", "duration"} and isinstance(value, dict):
        units = {"px", "rem"} if token_type == "dimension" else {"ms", "s"}
        if value.get("unit") not in units or type(value.get("value")) not in {int, float} or not math.isfinite(value["value"]) or value["value"] < 0:
            raise DesignError("Invalid dimension or duration")
        return f"{value['value']}{value['unit']}"
    if token_type == "fontFamily" and isinstance(value, list):
        if not value or any(not isinstance(item, str) or not re.fullmatch(r"[A-Za-z0-9 _-]+", item) for item in value):
            raise DesignError("Font families must be plain names, not CSS or URLs")
        return ", ".join(f'"{item}"' if " " in item else item for item in value)
    raise DesignError(f"Unsupported direction token type: {token_type}")


def variable_name(name: str) -> str:
    return "--eae-" + re.sub(r"[^a-z0-9-]+", "-", name.lower().replace(".", "-")).strip("-")


def render_direction_css(state: dict[str, Any] | None = None) -> str:
    catalog = load_catalog()
    state = load_object(STATE_PATH) if state is None else state
    validate_state(state, catalog)
    approved = state.get("approved_direction")
    if approved is None:
        return "/* No direction approved. Compare the live directions before token compilation. */\n"
    direction = catalog[approved]
    declarations = [
        f"  {variable_name(name)}: {token_to_css(token)};"
        for name, token in sorted(direction["tokens"].items())
    ]
    return (
        f"/* Approved direction: {approved} ({approved}). Fingerprint: {state['fingerprint']}. Generated; do not edit. */\n"
        ":root {\n" + "\n".join(declarations) + "\n}\n"
    )


def run_preview(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    intake = load_object(INTAKE_PATH)
    state = load_object(STATE_PATH)
    validate_state(state, catalog)
    payload = {
        "intake_status": intake.get("status"),
        "design_status": state.get("status"),
        "approved_direction": state.get("approved_direction"),
        "directions": [
            {
                "id": value["id"],
                "name": value["name"],
                "thesis": value["thesis"],
                "best_for": value.get("best_for", []),
                "motion": value["motion"],
                "preview_path": value.get("preview_path"),
            }
            for value in catalog.values()
        ],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Intake: {payload['intake_status']} | Direction: {payload['design_status']}")
        for direction in payload["directions"]:
            print(f"\n{direction['id']} — {direction['name']}")
            print(f"  {direction['thesis']}")
            print(f"  Motion: {direction['motion']}")
        print("\nNo candidates yet. Continue with ./agentic start." if not catalog else
              "\nInspect each candidate's local preview. You may reject all candidates or propose another.")
    return 0


def run_approve(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    if args.direction not in catalog:
        raise DesignError("Unknown direction; choose: " + ", ".join(catalog))
    if not args.yes:
        print(f"No change made. Re-run with --yes to approve {args.direction}.")
        return 2
    evidence = getattr(args, "evidence", None) or []
    if not evidence and sys.stdin.isatty():
        evidence = [prompt("Path to the reviewed screenshot under docs/50-evals/")]
    if not evidence:
        raise DesignError("Review the live candidate, then provide --evidence docs/50-evals/<screenshot>.png")
    fingerprint = approval_fingerprint(ROOT, catalog[args.direction], evidence)
    state = {
        "schema_version": 1,
        "status": "approved",
        "approved_direction": args.direction,
        "approved_by": args.approved_by,
        "approved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "fingerprint": fingerprint,
        "evidence": evidence,
    }
    save_object(STATE_PATH, state)
    print(f"Approved {catalog[args.direction]['name']}.")
    print("Next: ./agentic tokens build")
    return 0


def run_propose(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if path.is_absolute() or ".." in path.parts or any((ROOT / Path(*path.parts[:index])).is_symlink() for index in range(1, len(path.parts) + 1)) or not (ROOT / path).resolve().is_relative_to(ROOT.resolve()):
        raise DesignError("Candidate input must be a project-local JSON file")
    direction = load_object(ROOT / path)
    validate_custom_candidate(direction, ROOT)
    if not isinstance(direction.get("preview_path"), str) or not re.fullmatch(r"/(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+/?", direction["preview_path"]):
        raise DesignError("A candidate needs a local preview_path, not a remote URL")
    for field in CUSTOM_TEXT_FIELDS:
        if not _meaningful_decision(direction.get(field)):
            raise DesignError(f"A custom candidate requires a meaningful {field}")
    catalog = load_catalog()
    identity = direction.get("id")
    if not isinstance(identity, str):
        raise DesignError("Candidate id must be text")
    if identity in catalog:
        raise DesignError("Candidate id already exists; use a new revision id to preserve its history")
    proposed_axis = re.sub(r"\s+", " ", direction["axis"].strip().lower())
    existing_axes = {
        re.sub(r"\s+", " ", value["axis"].strip().lower())
        for value in catalog.values()
    }
    if proposed_axis in existing_axes:
        raise DesignError("Candidate axis already exists; propose a materially different design question")
    payload = load_object(CATALOG_PATH)
    payload["directions"].append(direction)
    # Validate all fields before any write using the same serializer as compilation.
    if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identity):
        raise DesignError("Candidate id must use lowercase kebab-case")
    for field in ("name", "thesis", "motion"):
        if not isinstance(direction.get(field), str) or not direction[field].strip():
            raise DesignError(f"Candidate requires {field}")
    sources = direction.get("source_files")
    if not isinstance(sources, list) or not sources:
        raise DesignError("Candidate requires source_files for its actual local preview")
    for relative in sources:
        candidate_source(ROOT, relative)
    tokens = direction.get("tokens")
    required = {"color.background.canvas", "color.background.surface", "color.text.primary",
                "color.text.secondary", "color.action.primary.default", "font.family.display",
                "radius.lg", "duration.normal"}
    if not isinstance(tokens, dict) or not required.issubset(tokens):
        raise DesignError("Candidate needs the semantic color, font, radius, and motion token contract")
    names = set()
    for name, token in tokens.items():
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*", name) or not isinstance(token, dict) or "$type" not in token or "$value" not in token:
            raise DesignError("Invalid candidate token")
        if variable_name(name) in names:
            raise DesignError("Candidate token names collide")
        names.add(variable_name(name))
        token_to_css(token)
    if not args.yes:
        print(json.dumps(direction, indent=2))
        print("No candidate registered. Re-run with --yes after reviewing this proposal.")
        return 2
    save_object(CATALOG_PATH, payload)
    print(f"Candidate {identity} registered, not approved. Preview: {direction['preview_path']}")
    return 0


def run_reset(args: argparse.Namespace) -> int:
    if not args.yes:
        print("No change made. Re-run with --yes to return to direction comparison.")
        return 2
    state = {
        "schema_version": 1,
        "status": "needs_approval",
        "approved_direction": None,
        "approved_by": None,
        "approved_at": None,
    }
    save_object(STATE_PATH, state)
    print("Direction approval reset. Existing source tokens were not changed.")
    return 0


def run_status(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    state = load_object(STATE_PATH)
    intake = load_object(INTAKE_PATH)
    validate_state(state, catalog)
    payload = {"intake": intake, "design": state}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Intake: {intake.get('status')}")
        print(f"Direction: {state.get('status')}")
        if state.get("approved_direction"):
            print(f"Approved: {state['approved_direction']}")
    return 0


def run_resources(args: argparse.Namespace) -> int:
    report = design_resource_plan(ROOT, phase=args.phase, needs=args.need)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    context = report["context"]
    print("Design resource plan (read only)")
    print(f"Phase: {context['phase']}")
    print(f"Platforms: {', '.join(context['platforms']) or 'none'}")
    print(f"Needs: {', '.join(context['needs']) or 'none identified'}")
    visible = [item for item in report["decisions"] if item["state"] != "optional" or args.all]
    if not visible:
        print("\nNo external design resource is justified by current evidence.")
    for item in visible:
        print(f"\n{item['state'].upper():<14} {item['name']}")
        print(f"Why: {item['reason']}")
        print(f"Reviewed: {item['source']['reviewed_at']}")
        print(f"Maintenance: {item['source']['maintenance']}")
        print(f"License/use boundary: {item['source']['license']}")
        if item["prerequisites"]:
            print("Before external use:")
            for prerequisite in item["prerequisites"]:
                print(f"  - {prerequisite}")
        print("Boundaries:")
        for boundary in item["forbidden"]:
            print(f"  - {boundary}")
        if item["state"] == "recommended":
            print(f"Open manually after reviewing the boundaries above: {item['url']}")
            print("Bring back:")
            for deliverable in item["bring_back"]:
                print(f"  - {deliverable}")
        if item["return_to"]:
            print("Return to:")
            for destination in item["return_to"]:
                print(f"  - {destination}")
    print("\nNothing was opened, submitted, downloaded, installed, or changed.")
    return 0


def run_check(_: argparse.Namespace) -> int:
    catalog = load_catalog()
    state = load_object(STATE_PATH)
    intake = load_object(INTAKE_PATH)
    load_resource_catalog()
    assets = load_asset_catalog(ROOT)
    validate_state(state, catalog)
    if intake.get("schema_version") != 1 or intake.get("status") not in {
        "not_started",
        "captured",
        "complete",
    }:
        raise DesignError("Invalid design-intake state")
    render_direction_css(state)
    print(f"Design workflow valid: {len(catalog)} directions, {len(assets)} generated assets, status={state['status']}")
    return 0


def run_sprint(args: argparse.Namespace) -> int:
    """Resume the saved brief directly into the live creative-direction sprint."""
    return project_handoff.run(args, ROOT)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    commands = value.add_subparsers(dest="command", required=True)
    sprint = commands.add_parser("sprint", help="Create live product-specific directions in the chosen client")
    sprint.add_argument("--assistant", choices=project_brief.CLIENTS)
    sprint.add_argument("--json", action="store_true")
    sprint.add_argument("--launch", action="store_true")
    sprint.add_argument("--yes", action="store_true")
    intake = commands.add_parser("intake", help="Record the short adaptive design intake")
    intake.add_argument("--answer", action="append")
    intake.add_argument("--non-interactive", action="store_true")
    intake.add_argument("--yes", action="store_true")
    preview = commands.add_parser("preview", help="Compare available directions")
    preview.add_argument("--json", action="store_true")
    approve = commands.add_parser("approve", help="Record explicit direction approval")
    approve.add_argument("direction")
    approve.add_argument("--approved-by", default="human reviewer")
    approve.add_argument("--yes", action="store_true")
    approve.add_argument("--evidence", action="append", help="Reviewed screenshot/report under docs/50-evals/")
    propose = commands.add_parser("propose", help="Register a project-owned direction without approving it")
    propose.add_argument("--file", required=True)
    propose.add_argument("--yes", action="store_true")
    reset = commands.add_parser("reset", help="Return to direction comparison")
    reset.add_argument("--yes", action="store_true")
    status = commands.add_parser("status", help="Show intake and approval state")
    status.add_argument("--json", action="store_true")
    resources = commands.add_parser("resources", help="Route reviewed palette, asset, and motion resources")
    resources.add_argument("--need", action="append", choices=sorted(RESOURCE_NEEDS))
    resources.add_argument("--phase", choices=sorted(RESOURCE_PHASES))
    resources.add_argument("--all", action="store_true", help="Include optional resources")
    resources.add_argument("--json", action="store_true")
    commands.add_parser("check", help="Validate the design workflow contract")
    return value


def main() -> int:
    try:
        args = parser().parse_args()
        return {
            "sprint": run_sprint,
            "intake": run_intake,
            "preview": run_preview,
            "approve": run_approve,
            "propose": run_propose,
            "reset": run_reset,
            "status": run_status,
            "resources": run_resources,
            "check": run_check,
        }[args.command](args)
    except (DesignError, OSError, EOFError, KeyboardInterrupt) as error:
        print(f"Design workflow error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
