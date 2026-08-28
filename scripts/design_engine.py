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

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / ".agentic/design.json"
INTAKE_PATH = ROOT / ".agentic/design-intake.json"
CATALOG_PATH = ROOT / ".agentic/design-directions.json"


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
    if not target.is_file() or target.suffix not in {".tsx", ".ts", ".jsx", ".js", ".css", ".json", ".svg", ".png", ".jpg", ".webp", ".woff2"}:
        raise DesignError("Candidate source must reference existing preview code")
    return target


def validate_custom_candidate(direction: dict, root: Path) -> None:
    preview = direction.get("preview_path")
    if not isinstance(preview, str) or not re.fullmatch(r"/(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+/?", preview):
        raise DesignError("A custom candidate needs a local preview_path, not a remote URL")
    for field in ("composition", "interaction", "rationale"):
        if not isinstance(direction.get(field), str) or not direction[field].strip():
            raise DesignError(f"A custom candidate requires {field}")
    sources = direction.get("source_files")
    if not isinstance(sources, list) or not sources:
        raise DesignError("Candidate requires source_files for its actual local preview and dependencies")
    for relative in sources:
        candidate_source(root, relative)


def save_object(path: Path, payload: dict) -> None:
    if path.is_symlink() or path.parent.is_symlink():
        raise DesignError("Design output must not follow symlinks")
    path.write_text(json.dumps(payload, indent=2) + "\n")


def validate_project(root: Path) -> dict[str, Any]:
    catalog = load_catalog(root / ".agentic/design-directions.json")
    state = load_object(root / ".agentic/design.json")
    validate_state(state, catalog, root)
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
    for field in ("composition", "interaction", "rationale"):
        if not isinstance(direction.get(field), str) or not direction[field].strip():
            raise DesignError(f"A custom candidate requires {field}")
    catalog = load_catalog()
    identity = direction.get("id")
    if not isinstance(identity, str):
        raise DesignError("Candidate id must be text")
    if identity in catalog:
        raise DesignError("Candidate id already exists; use a new revision id to preserve its history")
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


def run_check(_: argparse.Namespace) -> int:
    catalog = load_catalog()
    state = load_object(STATE_PATH)
    intake = load_object(INTAKE_PATH)
    validate_state(state, catalog)
    if intake.get("schema_version") != 1 or intake.get("status") not in {
        "not_started",
        "captured",
        "complete",
    }:
        raise DesignError("Invalid design-intake state")
    render_direction_css(state)
    print(f"Design workflow valid: {len(catalog)} directions, status={state['status']}")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    commands = value.add_subparsers(dest="command", required=True)
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
    commands.add_parser("check", help="Validate the design workflow contract")
    return value


def main() -> int:
    try:
        args = parser().parse_args()
        return {
            "intake": run_intake,
            "preview": run_preview,
            "approve": run_approve,
            "propose": run_propose,
            "reset": run_reset,
            "status": run_status,
            "check": run_check,
        }[args.command](args)
    except (DesignError, OSError, EOFError, KeyboardInterrupt) as error:
        print(f"Design workflow error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
