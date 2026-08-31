#!/usr/bin/env python3
"""Create and evaluate anonymous, local newcomer-pilot scorecards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".agentic" / "pilot" / "policy.json"
PROTOCOL_PATH = ROOT / "docs" / "50-evals" / "FIRST_PROJECT_PILOT.md"


class PilotError(ValueError):
    """Raised when pilot evidence violates the closed local contract."""


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise PilotError(f"Cannot read valid {label} from {path}: {error}") from error
    if not isinstance(value, dict):
        raise PilotError(f"{label} must be a JSON object: {path}")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    found = set(value)
    if found != expected:
        raise PilotError(
            f"{label} keys are closed; missing={sorted(expected - found)}, "
            f"extra={sorted(found - expected)}"
        )


def recursive_items(value: Any) -> Iterable[tuple[str | None, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from recursive_items(child)
    elif isinstance(value, list):
        for child in value:
            yield None, child
            yield from recursive_items(child)


def load_policy() -> dict[str, Any]:
    policy = load_object(POLICY_PATH, "pilot policy")
    exact_keys(
        policy,
        {"schema_version", "mode", "required_sessions", "allowed_session_ids", "thresholds", "privacy", "enums"},
        "Pilot policy",
    )
    if policy["schema_version"] != 1 or policy["mode"] != "consent_local_only":
        raise PilotError("Pilot policy must use schema 1 in consent_local_only mode")
    if policy["required_sessions"] != 5:
        raise PilotError("The first launch pilot requires exactly five sessions")
    if policy["allowed_session_ids"] != ["P1", "P2", "P3", "P4", "P5"]:
        raise PilotError("Anonymous session identifiers must remain P1 through P5")

    exact_keys(
        policy["thresholds"],
        {
            "minimum_unassisted_completions",
            "minimum_boundary_understanding",
            "minimum_independent_next_steps",
            "maximum_repeated_unresolved_blockers",
        },
        "Pilot thresholds",
    )
    if policy["thresholds"] != {
        "minimum_unassisted_completions": 4,
        "minimum_boundary_understanding": 5,
        "minimum_independent_next_steps": 4,
        "maximum_repeated_unresolved_blockers": 0,
    }:
        raise PilotError("Pilot launch thresholds cannot be weakened")

    exact_keys(policy["privacy"], {"forbidden_field_names", "required_flags"}, "Pilot privacy policy")
    forbidden = policy["privacy"]["forbidden_field_names"]
    if not isinstance(forbidden, list) or not forbidden or len(forbidden) != len(set(forbidden)):
        raise PilotError("forbidden_field_names must be a unique non-empty list")
    required_flags = {
        "redacted": True,
        "contains_personal_data": False,
        "contains_secrets": False,
        "contains_raw_prompts": False,
        "recording_collected": False,
        "retention_class": "aggregate_only",
    }
    if policy["privacy"]["required_flags"] != required_flags:
        raise PilotError("Pilot privacy flags cannot be weakened")

    exact_keys(
        policy["enums"],
        {"operating_system", "experience_level", "profile", "stage", "friction_code"},
        "Pilot enums",
    )
    expected_enums = {
        "operating_system": ["macos", "linux", "windows-wsl", "other"],
        "experience_level": ["new_to_frontend", "working_frontend_knowledge", "experienced_frontend"],
        "profile": ["web-next", "portfolio", "product", "agentic-product", "enterprise-workflow"],
        "stage": ["prerequisites", "creation", "personalization", "design", "handoff", "implementation", "verification", "review", "continuation", "safety"],
        "friction_code": ["missing_prerequisite", "unclear_instruction", "unexpected_output", "command_failure", "navigation_confusion", "concept_confusion", "unsafe_action", "other_redacted"],
    }
    if policy["enums"] != expected_enums:
        raise PilotError("Pilot enum values cannot be expanded without review")
    for name, values in policy["enums"].items():
        if not isinstance(values, list) or not values or not all(isinstance(item, str) and item for item in values):
            raise PilotError(f"Pilot enum {name} must be a non-empty string list")
        if len(values) != len(set(values)):
            raise PilotError(f"Pilot enum {name} contains duplicates")
    return policy


def enum_value(value: Any, allowed: list[str], label: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise PilotError(f"{label} must be one of: {', '.join(allowed)}")
    return value


def boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise PilotError(f"{label} must be true or false")
    return value


def bounded_number(value: Any, label: str, minimum: float, maximum: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise PilotError(f"{label} must be a number from {minimum:g} to {maximum:g}")
    return float(value)


def validate_friction(value: Any, policy: dict[str, Any], label: str, *, blocker: bool) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PilotError(f"{label} must be an object")
    expected = {"stage", "code", "safety_required", "resolved"} if blocker else {"stage", "code", "safety_required"}
    exact_keys(value, expected, label)
    enum_value(value["stage"], policy["enums"]["stage"], f"{label}.stage")
    enum_value(value["code"], policy["enums"]["friction_code"], f"{label}.code")
    boolean(value["safety_required"], f"{label}.safety_required")
    if blocker:
        boolean(value["resolved"], f"{label}.resolved")
    return value


def reject_sensitive_content(scorecard: dict[str, Any], policy: dict[str, Any]) -> None:
    forbidden = {item.lower() for item in policy["privacy"]["forbidden_field_names"]}
    sensitive_patterns = [
        re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})\b"),
        re.compile(r"\b(?:api[_-]?key|access[_-]?token|password)\s*[:=]", re.IGNORECASE),
    ]
    for key, child in recursive_items(scorecard):
        if key is not None and key.lower() in forbidden:
            raise PilotError(f"Forbidden pilot field: {key}")
        if isinstance(child, str) and any(pattern.search(child) for pattern in sensitive_patterns):
            raise PilotError("Scorecard contains a possible identifier or secret; redact it before validation")


def validate_scorecard(scorecard: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    exact_keys(
        scorecard,
        {"schema_version", "session_id", "consent", "environment", "timings", "outcomes", "interventions", "blockers", "quality", "privacy"},
        "Scorecard",
    )
    reject_sensitive_content(scorecard, policy)
    if scorecard["schema_version"] != 1:
        raise PilotError("Scorecard must use schema version 1")
    enum_value(scorecard["session_id"], policy["allowed_session_ids"], "session_id")

    consent = scorecard["consent"]
    if not isinstance(consent, dict):
        raise PilotError("consent must be an object")
    exact_keys(consent, {"participant_consented", "observer_explained_data_boundary"}, "consent")
    if consent != {"participant_consented": True, "observer_explained_data_boundary": True}:
        raise PilotError("Participant consent and the data boundary must be confirmed before recording a scorecard")

    environment = scorecard["environment"]
    if not isinstance(environment, dict):
        raise PilotError("environment must be an object")
    exact_keys(
        environment,
        {"operating_system", "experience_level", "profile", "node_version", "pnpm_version", "python_version"},
        "environment",
    )
    for key in ("operating_system", "experience_level", "profile"):
        enum_value(environment[key], policy["enums"][key], f"environment.{key}")
    for key in ("node_version", "pnpm_version", "python_version"):
        if not isinstance(environment[key], str) or not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", environment[key]):
            raise PilotError(f"environment.{key} must be a numeric version such as 22.12.0")

    timings = scorecard["timings"]
    if not isinstance(timings, dict):
        raise PilotError("timings must be an object")
    exact_keys(
        timings,
        {"download_and_tooling_minutes", "product_flow_minutes", "time_to_personalized_preview_minutes"},
        "timings",
    )
    for key, value in timings.items():
        bounded_number(value, f"timings.{key}", 0, 480)

    outcomes = scorecard["outcomes"]
    if not isinstance(outcomes, dict):
        raise PilotError("outcomes must be an object")
    outcome_keys = {
        "creation_completed",
        "personalization_completed",
        "feature_completed",
        "applicable_verification_completed",
        "evidence_boundaries_understood",
        "next_step_identified",
    }
    exact_keys(outcomes, outcome_keys, "outcomes")
    for key, value in outcomes.items():
        boolean(value, f"outcomes.{key}")

    for field, blocker in (("interventions", False), ("blockers", True)):
        values = scorecard[field]
        if not isinstance(values, list) or len(values) > 100:
            raise PilotError(f"{field} must be an array with at most 100 entries")
        for index, value in enumerate(values):
            validate_friction(value, policy, f"{field}[{index}]", blocker=blocker)

    quality = scorecard["quality"]
    if not isinstance(quality, dict):
        raise PilotError("quality must be an object")
    exact_keys(
        quality,
        {"independent_evaluator", "hierarchy", "content_specificity", "interaction", "accessibility"},
        "quality",
    )
    if quality["independent_evaluator"] is not True:
        raise PilotError("A separate evaluator must score result quality")
    for key in ("hierarchy", "content_specificity", "interaction", "accessibility"):
        value = quality[key]
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
            raise PilotError(f"quality.{key} must be an integer from 1 to 5")

    privacy = scorecard["privacy"]
    if not isinstance(privacy, dict):
        raise PilotError("privacy must be an object")
    exact_keys(privacy, set(policy["privacy"]["required_flags"]), "privacy")
    if privacy != policy["privacy"]["required_flags"]:
        raise PilotError("Scorecard privacy flags do not satisfy the aggregate-only policy")
    return scorecard


def template_scorecard(session_id: str, policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "session_id": session_id,
        "consent": {
            "participant_consented": False,
            "observer_explained_data_boundary": False,
        },
        "environment": {
            "operating_system": "other",
            "experience_level": "working_frontend_knowledge",
            "profile": "web-next",
            "node_version": "0.0.0",
            "pnpm_version": "0.0.0",
            "python_version": "0.0.0",
        },
        "timings": {
            "download_and_tooling_minutes": 0,
            "product_flow_minutes": 0,
            "time_to_personalized_preview_minutes": 0,
        },
        "outcomes": {
            "creation_completed": False,
            "personalization_completed": False,
            "feature_completed": False,
            "applicable_verification_completed": False,
            "evidence_boundaries_understood": False,
            "next_step_identified": False,
        },
        "interventions": [],
        "blockers": [],
        "quality": {
            "independent_evaluator": False,
            "hierarchy": 1,
            "content_specificity": 1,
            "interaction": 1,
            "accessibility": 1,
        },
        "privacy": dict(policy["privacy"]["required_flags"]),
    }


def session_instructions(session_id: str, scorecard_path: Path) -> str:
    return f"""# Newcomer pilot {session_id}

This is an anonymous usability session. Give the participant only the public
README. Do not collect their identity, employer, repository, raw prompts,
transcript, recording, credentials, secrets, or personal data.

1. Explain the data boundary and obtain consent.
2. Run the six steps in `docs/50-evals/FIRST_PROJECT_PILOT.md` without silent rescue.
3. Record only closed categories in `{scorecard_path.name}`.
4. A separate evaluator scores the resulting experience from 1–5.
5. Validate with:

   `./agentic pilot validate <pilot-root>/{session_id}/{scorecard_path.name}`

Safety interventions are always allowed and must be recorded. The scorecard
template intentionally fails validation until consent, environment, outcomes,
and independent quality evidence are complete.
"""


def is_unassisted_completion(scorecard: dict[str, Any]) -> bool:
    outcomes = scorecard["outcomes"]
    required = (
        "creation_completed",
        "personalization_completed",
        "feature_completed",
        "applicable_verification_completed",
    )
    return all(outcomes[key] for key in required) and not scorecard["interventions"]


def build_report(scorecards: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    ordered = sorted(scorecards, key=lambda item: item["session_id"])
    session_ids = [item["session_id"] for item in ordered]
    if len(session_ids) != len(set(session_ids)):
        raise PilotError("Each anonymous session id may appear only once")

    friction = Counter(
        f"{item['stage']}:{item['code']}"
        for scorecard in ordered
        for item in scorecard["interventions"]
    )
    unresolved = Counter(
        f"{item['stage']}:{item['code']}"
        for scorecard in ordered
        for item in scorecard["blockers"]
        if not item["resolved"]
    )
    repeated_unresolved = sorted(code for code, count in unresolved.items() if count >= 2)

    unassisted = sum(is_unassisted_completion(item) for item in ordered)
    boundaries = sum(item["outcomes"]["evidence_boundaries_understood"] for item in ordered)
    next_steps = sum(item["outcomes"]["next_step_identified"] for item in ordered)
    thresholds = policy["thresholds"]
    gates = [
        {
            "id": "unassisted_completion",
            "passed": unassisted >= thresholds["minimum_unassisted_completions"],
            "actual": unassisted,
            "required": thresholds["minimum_unassisted_completions"],
        },
        {
            "id": "evidence_boundary_understanding",
            "passed": boundaries >= thresholds["minimum_boundary_understanding"],
            "actual": boundaries,
            "required": thresholds["minimum_boundary_understanding"],
        },
        {
            "id": "independent_next_step",
            "passed": next_steps >= thresholds["minimum_independent_next_steps"],
            "actual": next_steps,
            "required": thresholds["minimum_independent_next_steps"],
        },
        {
            "id": "repeated_unresolved_blockers",
            "passed": len(repeated_unresolved) <= thresholds["maximum_repeated_unresolved_blockers"],
            "actual": len(repeated_unresolved),
            "required": thresholds["maximum_repeated_unresolved_blockers"],
        },
    ]

    sample_complete = len(ordered) == policy["required_sessions"] and session_ids == policy["allowed_session_ids"]
    verdict = "INSUFFICIENT_EVIDENCE"
    if sample_complete:
        verdict = "PASS" if all(gate["passed"] for gate in gates) else "FAIL"

    quality_keys = ("hierarchy", "content_specificity", "interaction", "accessibility")
    quality_averages = {
        key: round(sum(item["quality"][key] for item in ordered) / len(ordered), 2)
        for key in quality_keys
    } if ordered else {key: None for key in quality_keys}

    return {
        "schema_version": 1,
        "verdict": verdict,
        "sample_size": len(ordered),
        "required_sample_size": policy["required_sessions"],
        "session_ids": session_ids,
        "metrics": {
            "unassisted_completions": unassisted,
            "evidence_boundary_understanding": boundaries,
            "independent_next_steps": next_steps,
            "intervention_count": sum(len(item["interventions"]) for item in ordered),
            "median_product_flow_minutes": median([item["timings"]["product_flow_minutes"] for item in ordered]),
            "median_time_to_personalized_preview_minutes": median(
                [item["timings"]["time_to_personalized_preview_minutes"] for item in ordered]
            ),
        },
        "gate_results": gates,
        "friction_counts": dict(sorted(friction.items())),
        "repeated_unresolved_blockers": repeated_unresolved,
        "environments": [item["environment"] for item in ordered],
        "quality_averages": quality_averages,
        "privacy": dict(policy["privacy"]["required_flags"]),
        "uncertainty": "Five consented sessions are a directional usability pilot, not a statistically representative adoption claim or production certification.",
    }


def median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return round(ordered[middle], 2)
    return round((ordered[middle - 1] + ordered[middle]) / 2, 2)


def markdown_report(report: dict[str, Any]) -> str:
    gate_lines = "\n".join(
        f"- {'PASS' if gate['passed'] else 'FAIL'} — `{gate['id']}`: {gate['actual']} (required {gate['required']})"
        for gate in report["gate_results"]
    )
    blocker_lines = "\n".join(f"- `{item}`" for item in report["repeated_unresolved_blockers"]) or "- None"
    friction_lines = "\n".join(
        f"- `{key}`: {value}" for key, value in report["friction_counts"].items()
    ) or "- None recorded"
    return f"""# Newcomer pilot report

**Verdict:** `{report['verdict']}`
**Sample:** {report['sample_size']} / {report['required_sample_size']} anonymous sessions

## Gates

{gate_lines}

## Timing and intervention summary

- Median product-flow time: {report['metrics']['median_product_flow_minutes']} minutes
- Median time to personalized preview: {report['metrics']['median_time_to_personalized_preview_minutes']} minutes
- Total interventions: {report['metrics']['intervention_count']}

## Repeated unresolved blockers

{blocker_lines}

## Friction categories

{friction_lines}

## Independent quality averages

- Hierarchy: {report['quality_averages']['hierarchy']} / 5
- Content specificity: {report['quality_averages']['content_specificity']} / 5
- Interaction: {report['quality_averages']['interaction']} / 5
- Accessibility: {report['quality_averages']['accessibility']} / 5

## Limits

{report['uncertainty']}

The report contains closed anonymous categories and aggregate-only privacy flags.
It is not a testimonial, raw research archive, accessibility certification, or
production-readiness approval.
"""


def collect_scorecards(directory: Path, policy: dict[str, Any]) -> list[dict[str, Any]]:
    if not directory.is_dir() or directory.is_symlink():
        raise PilotError(f"Pilot input must be a real directory: {directory}")
    paths = sorted(directory.glob("**/scorecard.json"))
    scorecards: list[dict[str, Any]] = []
    for path in paths:
        relative = path.relative_to(directory)
        if (
            len(relative.parts) != 2
            or relative.parts[0] not in policy["allowed_session_ids"]
            or path.is_symlink()
            or path.parent.is_symlink()
        ):
            raise PilotError(f"Unexpected scorecard path; use only P1-P5/scorecard.json: {path}")
        scorecard = validate_scorecard(load_object(path, "pilot scorecard"), policy)
        if scorecard["session_id"] != path.parent.name:
            raise PilotError(f"Session id does not match its directory: {path}")
        scorecards.append(scorecard)
    return scorecards


def command_plan(policy: dict[str, Any]) -> int:
    print("Newcomer pilot: consented, local, anonymous, five-session evaluation")
    print(f"Protocol: {PROTOCOL_PATH.relative_to(ROOT)}")
    print("1. ./agentic pilot create P1 --output <private-local-directory> --yes")
    print("2. Complete and validate each P1-P5 scorecard")
    print("3. ./agentic pilot summarize <private-local-directory>")
    print("The pilot never recruits, records, uploads, publishes, approves, or merges.")
    return 0


def command_create(args: argparse.Namespace, policy: dict[str, Any]) -> int:
    session_id = enum_value(args.session_id, policy["allowed_session_ids"], "session_id")
    output = Path(args.output).expanduser().resolve()
    target = output / session_id
    if target.exists() or target.is_symlink():
        raise PilotError(f"Refusing to overwrite existing pilot session: {target}")
    print(f"Will create anonymous pilot session {session_id} at {target}")
    if not args.yes:
        print("No files written. Re-run with --yes after reviewing the destination.")
        return 0
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise PilotError(f"Pilot output cannot be a symlink: {output}")
    target.mkdir()
    scorecard_path = target / "scorecard.json"
    scorecard_path.write_text(json.dumps(template_scorecard(session_id, policy), indent=2) + "\n")
    (target / "SESSION.md").write_text(session_instructions(session_id, scorecard_path))
    print(f"Created {target}")
    print(f"Next: edit {scorecard_path}, then run ./agentic pilot validate {scorecard_path}")
    return 0


def command_validate(args: argparse.Namespace, policy: dict[str, Any]) -> int:
    path = Path(args.scorecard).expanduser().resolve()
    validate_scorecard(load_object(path, "pilot scorecard"), policy)
    print(f"PASS: valid anonymous scorecard {path.name}")
    return 0


def command_summarize(args: argparse.Namespace, policy: dict[str, Any]) -> int:
    directory = Path(args.directory).expanduser().resolve()
    scorecards = collect_scorecards(directory, policy)
    report = build_report(scorecards, policy)
    if not args.output:
        print(json.dumps(report, indent=2))
        return 0 if report["verdict"] == "PASS" else 1

    output = Path(args.output).expanduser().resolve()
    markdown = output.with_suffix(".md")
    if output.exists() or output.is_symlink() or markdown.exists() or markdown.is_symlink():
        raise PilotError("Refusing to overwrite an existing pilot report")
    print(f"Will write {output} and {markdown}")
    if not args.yes:
        print("No files written. Re-run with --yes after reviewing the destinations.")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    markdown.write_text(markdown_report(report))
    print(f"{report['verdict']}: wrote aggregate pilot report for {report['sample_size']} sessions")
    return 0 if report["verdict"] == "PASS" else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Run the local anonymous newcomer pilot")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Show the pilot sequence without writing files")

    create = commands.add_parser("create", help="Create one anonymous session packet")
    create.add_argument("session_id", help="P1 through P5")
    create.add_argument("--output", required=True, help="Private local directory for pilot evidence")
    create.add_argument("--yes", action="store_true", help="Confirm creation of the new session directory")

    validate = commands.add_parser("validate", help="Validate one completed scorecard")
    validate.add_argument("scorecard", help="Path to a completed scorecard.json")

    summarize = commands.add_parser("summarize", help="Evaluate available P1-P5 scorecards")
    summarize.add_argument("directory", help="Directory containing P1-P5 session directories")
    summarize.add_argument("--output", help="Optional new JSON report path; a Markdown companion is also written")
    summarize.add_argument("--yes", action="store_true", help="Confirm writing report files")
    return root


def main(argv: list[str] | None = None) -> int:
    try:
        policy = load_policy()
        args = parser().parse_args(argv)
        if args.command == "plan":
            return command_plan(policy)
        if args.command == "create":
            return command_create(args, policy)
        if args.command == "validate":
            return command_validate(args, policy)
        if args.command == "summarize":
            return command_summarize(args, policy)
        raise PilotError(f"Unknown command: {args.command}")
    except PilotError as error:
        print(f"Newcomer pilot error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
