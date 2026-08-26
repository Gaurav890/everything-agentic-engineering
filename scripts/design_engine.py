#!/usr/bin/env python3
"""Run the bounded design intake, comparison, and approval workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / ".agentic/design.json"
INTAKE_PATH = ROOT / ".agentic/design-intake.json"
CATALOG_PATH = ROOT / ".agentic/design-directions.json"


class DesignError(ValueError):
    """Raised when design state violates the review contract."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise DesignError(f"Cannot read valid design data from {path}: {error}") from error
    if not isinstance(value, dict):
        raise DesignError(f"Design data must be an object: {path}")
    return value


def load_catalog() -> dict[str, dict[str, Any]]:
    payload = load_object(CATALOG_PATH)
    if payload.get("schema_version") != 1 or not isinstance(payload.get("directions"), list):
        raise DesignError("Unsupported design-direction catalog schema")
    result: dict[str, dict[str, Any]] = {}
    for direction in payload["directions"]:
        if not isinstance(direction, dict):
            raise DesignError("Every design direction must be an object")
        direction_id = direction.get("id")
        if not isinstance(direction_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", direction_id):
            raise DesignError("Every design direction needs a kebab-case id")
        if direction_id in result:
            raise DesignError(f"Duplicate design direction: {direction_id}")
        tokens = direction.get("tokens")
        if not isinstance(tokens, dict) or not tokens:
            raise DesignError(f"Design direction has no tokens: {direction_id}")
        for name, token in tokens.items():
            if not isinstance(name, str) or not isinstance(token, dict):
                raise DesignError(f"Invalid token in direction: {direction_id}")
            if "$type" not in token or "$value" not in token:
                raise DesignError(f"Direction token is not DTCG-compatible: {direction_id}.{name}")
        result[direction_id] = direction
    if len(result) < 3:
        raise DesignError("At least three comparable design directions are required")
    return result


def validate_state(state: dict[str, Any], catalog: dict[str, dict[str, Any]]) -> None:
    if state.get("schema_version") != 1:
        raise DesignError("Unsupported design-state schema")
    status = state.get("status")
    approved = state.get("approved_direction")
    if status == "needs_approval" and approved is not None:
        raise DesignError("Unapproved design state cannot name an approved direction")
    if status == "approved" and approved not in catalog:
        raise DesignError("Approved design state must reference a catalog direction")
    if status not in {"needs_approval", "approved"}:
        raise DesignError(f"Unsupported design status: {status}")


def prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{label}{suffix}: ").strip()
    return answer or default


INTAKE_FIELDS = (
    ("product_type", "What are you designing", "portfolio"),
    ("audience", "Primary audience", "hiring managers and design leaders"),
    ("personality", "Personality (editorial / kinetic / quiet / custom)", "editorial"),
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
    answers: dict[str, str] = {}
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
    INTAKE_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print("Design intake recorded. Next: ./agentic design preview")
    return 0


def color_to_css(value: dict[str, Any]) -> str:
    components = value.get("components")
    if value.get("colorSpace") != "srgb" or not isinstance(components, list) or len(components) != 3:
        raise DesignError("Direction color values must use DTCG sRGB components")
    rgb = [round(float(component) * 255) for component in components]
    return f"rgb({rgb[0]} {rgb[1]} {rgb[2]} / {value.get('alpha', 1)})"


def token_to_css(token: dict[str, Any]) -> str:
    token_type = token["$type"]
    value = token["$value"]
    if token_type == "color" and isinstance(value, dict):
        return color_to_css(value)
    if token_type in {"dimension", "duration"} and isinstance(value, dict):
        return f"{value['value']}{value['unit']}"
    if token_type == "fontFamily" and isinstance(value, list):
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
        f"/* Approved direction: {direction['name']} ({approved}). Generated; do not edit. */\n"
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
                "best_for": value["best_for"],
                "motion": value["motion"],
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
        print("\nRun the web app to compare the same content live, then approve one direction.")
    return 0


def run_approve(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    if args.direction not in catalog:
        raise DesignError("Unknown direction; choose: " + ", ".join(catalog))
    if not args.yes:
        print(f"No change made. Re-run with --yes to approve {args.direction}.")
        return 2
    state = {
        "schema_version": 1,
        "status": "approved",
        "approved_direction": args.direction,
        "approved_by": args.approved_by,
        "approved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    print(f"Approved {catalog[args.direction]['name']}.")
    print("Next: ./agentic tokens build")
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
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
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
            "reset": run_reset,
            "status": run_status,
            "check": run_check,
        }[args.command](args)
    except (DesignError, EOFError, KeyboardInterrupt) as error:
        print(f"Design workflow error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
