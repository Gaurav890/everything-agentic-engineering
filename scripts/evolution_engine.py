#!/usr/bin/env python3
"""Offline, deterministic comparison for evidence-gated harness candidates."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
EVOLUTION_ROOT = ROOT / ".agentic" / "evolution"
POLICY_PATH = EVOLUTION_ROOT / "policy.json"
SCHEMA_ROOT = EVOLUTION_ROOT / "schemas"


class EvolutionError(ValueError):
    """Raised when evolution evidence violates the fail-closed contract."""


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise EvolutionError(f"Cannot read valid {label} from {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvolutionError(f"{label} must be a JSON object: {path}")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    found = set(value)
    if found != expected:
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        raise EvolutionError(f"{label} keys are not closed; missing={missing}, extra={extra}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise EvolutionError(f"{label} must be a non-empty POSIX repository path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        raise EvolutionError(f"{label} must stay inside the repository: {value!r}")
    return value


def policy_file(value: str, label: str) -> Path:
    relative = repository_path(value, label)
    target = (ROOT / relative).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError as error:
        raise EvolutionError(f"{label} escapes the repository: {value!r}") from error
    return target


def load_policy() -> dict[str, Any]:
    policy = load_object(POLICY_PATH, "evolution policy")
    exact_keys(
        policy,
        {
            "schema_version",
            "mode",
            "protected_eval_set",
            "incumbent_results",
            "minimum_evidence",
            "thresholds",
            "allowed_change_surfaces",
            "protected_paths",
            "data_policy",
            "authority",
        },
        "Evolution policy",
    )
    if policy["schema_version"] != 1 or policy["mode"] != "offline_proposal_only":
        raise EvolutionError("Evolution policy must use schema 1 in offline_proposal_only mode")
    policy_file(policy["protected_eval_set"], "protected_eval_set")
    policy_file(policy["incumbent_results"], "incumbent_results")

    minimum = policy["minimum_evidence"]
    if not isinstance(minimum, dict):
        raise EvolutionError("minimum_evidence must be an object")
    exact_keys(
        minimum,
        {"evaluated_cases", "human_calibration_required_for_learned_judges"},
        "minimum_evidence",
    )
    if not isinstance(minimum["evaluated_cases"], int) or minimum["evaluated_cases"] < 1:
        raise EvolutionError("minimum_evidence.evaluated_cases must be a positive integer")
    if minimum["human_calibration_required_for_learned_judges"] is not True:
        raise EvolutionError("Learned judges must remain human-calibrated")

    thresholds = policy["thresholds"]
    threshold_keys = {
        "minimum_weighted_quality_gain",
        "quality_regression_tolerance",
        "maximum_protected_regressions",
        "maximum_safety_failures",
        "maximum_cost_ratio",
        "maximum_p95_latency_ratio",
    }
    if not isinstance(thresholds, dict):
        raise EvolutionError("thresholds must be an object")
    exact_keys(thresholds, threshold_keys, "thresholds")
    for key in threshold_keys:
        if not isinstance(thresholds[key], (int, float)) or isinstance(thresholds[key], bool):
            raise EvolutionError(f"thresholds.{key} must be numeric")
    if thresholds["minimum_weighted_quality_gain"] <= 0:
        raise EvolutionError("The quality gate must require a positive gain")
    if thresholds["quality_regression_tolerance"] < 0:
        raise EvolutionError("Regression tolerance cannot be negative")
    if thresholds["maximum_protected_regressions"] != 0:
        raise EvolutionError("Protected regressions must remain zero")
    if thresholds["maximum_safety_failures"] != 0:
        raise EvolutionError("Safety failures must remain zero")
    if thresholds["maximum_cost_ratio"] < 1 or thresholds["maximum_p95_latency_ratio"] < 1:
        raise EvolutionError("Cost and latency ratios cannot require impossible negative growth")

    surfaces = policy["allowed_change_surfaces"]
    if not isinstance(surfaces, list) or not surfaces:
        raise EvolutionError("allowed_change_surfaces must be a non-empty list")
    surface_ids: set[str] = set()
    for surface in surfaces:
        if not isinstance(surface, dict):
            raise EvolutionError("Every allowed change surface must be an object")
        exact_keys(surface, {"id", "risk", "patterns", "required_reviews"}, "change surface")
        if not isinstance(surface["id"], str) or surface["id"] in surface_ids:
            raise EvolutionError("Change surface ids must be unique strings")
        surface_ids.add(surface["id"])
        if surface["risk"] not in {"low", "medium"}:
            raise EvolutionError("Only low- and medium-risk surfaces may enter this loop")
        for key in ("patterns", "required_reviews"):
            if not isinstance(surface[key], list) or not surface[key] or not all(
                isinstance(item, str) and item for item in surface[key]
            ):
                raise EvolutionError(f"change surface {key} must be a non-empty string list")
        for pattern in surface["patterns"]:
            repository_path(pattern.replace("*", "x"), "change-surface pattern")

    protected = policy["protected_paths"]
    if not isinstance(protected, list) or not protected:
        raise EvolutionError("protected_paths must be a non-empty list")
    for pattern in protected:
        repository_path(pattern.replace("*", "x"), "protected-path pattern")

    data_policy = policy["data_policy"]
    if not isinstance(data_policy, dict):
        raise EvolutionError("data_policy must be an object")
    exact_keys(
        data_policy,
        {"storage", "forbidden_record_fields", "required_privacy_flags"},
        "data_policy",
    )
    if data_policy["storage"] != "sanitized_aggregates_only":
        raise EvolutionError("Evolution data storage must remain sanitized_aggregates_only")
    forbidden = data_policy["forbidden_record_fields"]
    if not isinstance(forbidden, list) or not forbidden or len(forbidden) != len(set(forbidden)):
        raise EvolutionError("forbidden_record_fields must be a unique non-empty list")
    required_flags = {
        "redacted": True,
        "contains_personal_data": False,
        "contains_secrets": False,
        "retention_class": "aggregate_only",
    }
    if data_policy["required_privacy_flags"] != required_flags:
        raise EvolutionError("Evolution privacy flags cannot be weakened")

    authority = policy["authority"]
    if not isinstance(authority, dict):
        raise EvolutionError("authority must be an object")
    exact_keys(
        authority,
        {"propose", "compare", "write_candidate", "modify_eval_set", "promote", "deploy", "approve", "merge", "human_review_required"},
        "authority",
    )
    if authority["propose"] is not True or authority["compare"] is not True:
        raise EvolutionError("The offline loop must retain propose and compare capability")
    for key in ("write_candidate", "modify_eval_set", "promote", "deploy", "approve", "merge"):
        if authority[key] is not False:
            raise EvolutionError(f"Evolution authority must keep {key}=false")
    if authority["human_review_required"] is not True:
        raise EvolutionError("Human review must remain required")
    return policy


def validate_schema_documents() -> None:
    for name in ("outcome-signal.schema.json", "evaluation-result.schema.json"):
        schema = load_object(SCHEMA_ROOT / name, "evolution schema")
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise EvolutionError(f"{name} must declare JSON Schema 2020-12")
        if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
            raise EvolutionError(f"{name} must be a closed object schema")


def load_eval_set(policy: dict[str, Any]) -> tuple[list[dict[str, Any]], Path]:
    path = policy_file(policy["protected_eval_set"], "protected_eval_set")
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text().splitlines()
    except OSError as error:
        raise EvolutionError(f"Cannot read protected eval set: {error}") from error
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise EvolutionError(f"Invalid eval JSONL at line {line_number}: {error}") from error
        if not isinstance(record, dict):
            raise EvolutionError(f"Eval case {line_number} must be an object")
        exact_keys(record, {"case_id", "category", "protected", "weight", "minimum_quality"}, f"eval case {line_number}")
        if not isinstance(record["case_id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,127}", record["case_id"]):
            raise EvolutionError(f"Invalid case_id at eval line {line_number}")
        if not isinstance(record["category"], str) or not record["category"]:
            raise EvolutionError(f"Invalid category at eval line {line_number}")
        if record["protected"] is not True:
            raise EvolutionError("The committed starter eval set must remain fully protected")
        if not isinstance(record["weight"], (int, float)) or isinstance(record["weight"], bool) or record["weight"] <= 0:
            raise EvolutionError(f"Invalid weight at eval line {line_number}")
        if not isinstance(record["minimum_quality"], (int, float)) or isinstance(record["minimum_quality"], bool) or not 0 <= record["minimum_quality"] <= 1:
            raise EvolutionError(f"Invalid minimum_quality at eval line {line_number}")
        records.append(record)
    ids = [record["case_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise EvolutionError("Protected eval case ids must be unique")
    if len(records) < policy["minimum_evidence"]["evaluated_cases"]:
        raise EvolutionError("Protected eval set has insufficient cases")
    return records, path


def recursive_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from recursive_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from recursive_keys(child)


def validate_signal(signal: dict[str, Any], policy: dict[str, Any]) -> None:
    exact_keys(
        signal,
        {"schema_version", "signal_id", "observed_at", "source_type", "outcome", "metrics", "labels", "provenance", "privacy"},
        "outcome signal",
    )
    if signal["schema_version"] != 1:
        raise EvolutionError("Outcome signal must use schema version 1")
    if not isinstance(signal["signal_id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._:-]{2,127}", signal["signal_id"]):
        raise EvolutionError("Outcome signal_id is invalid")
    if not isinstance(signal["observed_at"], str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        signal["observed_at"],
    ):
        raise EvolutionError("observed_at must be an ISO-8601 timestamp with timezone")
    if signal["source_type"] not in {"pull_request", "verification", "review", "generated_project", "human_feedback"}:
        raise EvolutionError("Unsupported outcome source_type")
    if signal["outcome"] not in {"success", "partial", "failure", "reverted", "escalated"}:
        raise EvolutionError("Unsupported outcome")
    forbidden = set(policy["data_policy"]["forbidden_record_fields"])
    exposed = sorted(forbidden.intersection(recursive_keys(signal)))
    if exposed:
        raise EvolutionError("Outcome signal contains forbidden raw or identifying fields: " + ", ".join(exposed))

    metrics = signal["metrics"]
    if not isinstance(metrics, dict):
        raise EvolutionError("Outcome metrics must be an object")
    exact_keys(metrics, {"quality_score", "safety_pass", "cost_units", "latency_ms"}, "outcome metrics")
    quality = metrics["quality_score"]
    if not isinstance(quality, (int, float)) or isinstance(quality, bool) or not 0 <= quality <= 1:
        raise EvolutionError("Outcome quality_score must be between 0 and 1")
    if not isinstance(metrics["safety_pass"], bool):
        raise EvolutionError("Outcome safety_pass must be boolean")
    for key in ("cost_units", "latency_ms"):
        if not isinstance(metrics[key], (int, float)) or isinstance(metrics[key], bool) or metrics[key] < 0:
            raise EvolutionError(f"Outcome {key} must be a non-negative number")
    labels = signal["labels"]
    if not isinstance(labels, list) or len(labels) != len(set(labels)) or not all(
        isinstance(item, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", item) for item in labels
    ):
        raise EvolutionError("Outcome labels must be unique kebab-case strings")
    provenance = signal["provenance"]
    if not isinstance(provenance, dict):
        raise EvolutionError("Outcome provenance must be an object")
    exact_keys(provenance, {"source_ref", "authority"}, "outcome provenance")
    if not isinstance(provenance["source_ref"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._:#/-]{1,127}", provenance["source_ref"]):
        raise EvolutionError("Outcome source_ref must be a bounded opaque reference")
    if provenance["authority"] not in {"human", "deterministic_test", "repository_check", "calibrated_judge"}:
        raise EvolutionError("Unsupported outcome authority")
    if signal["privacy"] != policy["data_policy"]["required_privacy_flags"]:
        raise EvolutionError("Outcome signal privacy flags do not satisfy policy")


def path_matches(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def validate_candidate_paths(paths: list[str], policy: dict[str, Any]) -> list[str]:
    normalized = [repository_path(path, "candidate changed path") for path in paths]
    if len(normalized) != len(set(normalized)):
        raise EvolutionError("Candidate changed_paths must be unique")
    protected = policy["protected_paths"]
    surfaces = policy["allowed_change_surfaces"]
    selected: set[str] = set()
    for path in normalized:
        if path_matches(path, protected):
            raise EvolutionError(f"Candidate attempts to change protected path: {path}")
        matches = [surface for surface in surfaces if path_matches(path, surface["patterns"])]
        if not matches:
            raise EvolutionError(f"Candidate path is outside allowed evolution surfaces: {path}")
        selected.update(surface["id"] for surface in matches)
    return sorted(selected)


def load_result(
    path: Path,
    *,
    label: str,
    policy: dict[str, Any],
    eval_cases: list[dict[str, Any]],
    policy_sha256: str,
    eval_set_sha256: str,
    candidate: bool,
) -> tuple[dict[str, Any], list[str]]:
    result = load_object(path, label)
    exact_keys(
        result,
        {"schema_version", "harness_id", "policy_sha256", "eval_set_sha256", "builder_role", "evaluator_role", "changed_paths", "cases"},
        label,
    )
    if result["schema_version"] != 1:
        raise EvolutionError(f"{label} must use schema version 1")
    if not isinstance(result["harness_id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,127}", result["harness_id"]):
        raise EvolutionError(f"{label} harness_id is invalid")
    if result["policy_sha256"] != policy_sha256:
        raise EvolutionError(f"{label} was evaluated against a different policy digest")
    if result["eval_set_sha256"] != eval_set_sha256:
        raise EvolutionError(f"{label} was evaluated against a different eval-set digest")
    if not isinstance(result["builder_role"], str) or not result["builder_role"]:
        raise EvolutionError(f"{label} builder_role is required")
    if not isinstance(result["evaluator_role"], str) or not result["evaluator_role"]:
        raise EvolutionError(f"{label} evaluator_role is required")
    if result["builder_role"] == result["evaluator_role"]:
        raise EvolutionError(f"{label} builder and evaluator must remain separate")
    paths = result["changed_paths"]
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        raise EvolutionError(f"{label} changed_paths must be a string list")
    if candidate:
        surfaces = validate_candidate_paths(paths, policy)
        if not paths:
            raise EvolutionError("Candidate must declare at least one changed path")
    else:
        if paths:
            raise EvolutionError("Incumbent changed_paths must be empty")
        surfaces = []

    cases = result["cases"]
    if not isinstance(cases, list):
        raise EvolutionError(f"{label} cases must be a list")
    expected_ids = {case["case_id"] for case in eval_cases}
    found_ids: set[str] = set()
    for index, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            raise EvolutionError(f"{label} case {index} must be an object")
        exact_keys(case, {"case_id", "quality_score", "safety_pass", "cost_units", "latency_ms"}, f"{label} case {index}")
        case_id = case["case_id"]
        if case_id not in expected_ids or case_id in found_ids:
            raise EvolutionError(f"{label} has an unknown or duplicate case_id: {case_id!r}")
        found_ids.add(case_id)
        quality = case["quality_score"]
        if not isinstance(quality, (int, float)) or isinstance(quality, bool) or not 0 <= quality <= 1:
            raise EvolutionError(f"{label} quality_score must be between 0 and 1")
        if not isinstance(case["safety_pass"], bool):
            raise EvolutionError(f"{label} safety_pass must be boolean")
        for key in ("cost_units", "latency_ms"):
            if not isinstance(case[key], (int, float)) or isinstance(case[key], bool) or case[key] < 0:
                raise EvolutionError(f"{label} {key} must be a non-negative number")
    if found_ids != expected_ids:
        missing = sorted(expected_ids - found_ids)
        raise EvolutionError(f"{label} is missing protected eval cases: {missing}")
    return result, surfaces


def weighted_quality(result: dict[str, Any], eval_cases: list[dict[str, Any]]) -> float:
    weights = {case["case_id"]: case["weight"] for case in eval_cases}
    numerator = sum(case["quality_score"] * weights[case["case_id"]] for case in result["cases"])
    return numerator / sum(weights.values())


def ratio(candidate: float, incumbent: float) -> float:
    if incumbent == 0:
        return 1.0 if candidate == 0 else math.inf
    return candidate / incumbent


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def compare(candidate_path: Path, incumbent_path: Path | None = None) -> dict[str, Any]:
    policy = load_policy()
    validate_schema_documents()
    eval_cases, eval_path = load_eval_set(policy)
    policy_sha256 = digest(POLICY_PATH)
    eval_set_sha256 = digest(eval_path)
    incumbent_path = incumbent_path or policy_file(policy["incumbent_results"], "incumbent_results")
    incumbent, _ = load_result(
        incumbent_path,
        label="incumbent results",
        policy=policy,
        eval_cases=eval_cases,
        policy_sha256=policy_sha256,
        eval_set_sha256=eval_set_sha256,
        candidate=False,
    )
    candidate, surfaces = load_result(
        candidate_path,
        label="candidate results",
        policy=policy,
        eval_cases=eval_cases,
        policy_sha256=policy_sha256,
        eval_set_sha256=eval_set_sha256,
        candidate=True,
    )

    incumbent_by_id = {case["case_id"]: case for case in incumbent["cases"]}
    candidate_by_id = {case["case_id"]: case for case in candidate["cases"]}
    threshold = policy["thresholds"]
    protected_regressions = []
    for case in eval_cases:
        case_id = case["case_id"]
        incumbent_score = incumbent_by_id[case_id]["quality_score"]
        candidate_score = candidate_by_id[case_id]["quality_score"]
        if candidate_score < case["minimum_quality"] or candidate_score + threshold["quality_regression_tolerance"] < incumbent_score:
            protected_regressions.append(case_id)
    safety_failures = sorted(
        case_id for case_id, value in candidate_by_id.items() if value["safety_pass"] is not True
    )
    incumbent_quality = weighted_quality(incumbent, eval_cases)
    candidate_quality = weighted_quality(candidate, eval_cases)
    gain = candidate_quality - incumbent_quality
    cost_ratio = ratio(
        sum(case["cost_units"] for case in candidate["cases"]),
        sum(case["cost_units"] for case in incumbent["cases"]),
    )
    latency_ratio = ratio(
        p95([case["latency_ms"] for case in candidate["cases"]]),
        p95([case["latency_ms"] for case in incumbent["cases"]]),
    )
    gates = {
        "evidence_coverage": len(candidate["cases"]) >= policy["minimum_evidence"]["evaluated_cases"],
        "weighted_quality_gain": gain >= threshold["minimum_weighted_quality_gain"],
        "protected_regressions": len(protected_regressions) <= threshold["maximum_protected_regressions"],
        "safety_failures": len(safety_failures) <= threshold["maximum_safety_failures"],
        "cost_budget": cost_ratio <= threshold["maximum_cost_ratio"],
        "p95_latency_budget": latency_ratio <= threshold["maximum_p95_latency_ratio"],
        "allowed_change_surface": bool(surfaces),
        "independent_evaluator": candidate["builder_role"] != candidate["evaluator_role"],
    }
    verdict = "PASS" if all(gates.values()) else "FAIL"
    required_reviews = sorted(
        {
            review
            for surface in policy["allowed_change_surfaces"]
            if surface["id"] in surfaces
            for review in surface["required_reviews"]
        }
    )
    return {
        "schema_version": 1,
        "mode": policy["mode"],
        "policy_sha256": policy_sha256,
        "eval_set_sha256": eval_set_sha256,
        "incumbent": incumbent["harness_id"],
        "candidate": candidate["harness_id"],
        "selected_surfaces": surfaces,
        "required_reviews": required_reviews,
        "metrics": {
            "incumbent_weighted_quality": round(incumbent_quality, 6),
            "candidate_weighted_quality": round(candidate_quality, 6),
            "weighted_quality_gain": round(gain, 6),
            "cost_ratio": round(cost_ratio, 6) if math.isfinite(cost_ratio) else "infinity",
            "p95_latency_ratio": round(latency_ratio, 6) if math.isfinite(latency_ratio) else "infinity",
            "protected_regressions": protected_regressions,
            "safety_failures": safety_failures,
        },
        "gates": gates,
        "verdict": verdict,
        "promotion": {
            "authorized": False,
            "human_review_required": True,
            "next_action": "open_reviewed_pull_request" if verdict == "PASS" else "reject_or_revise_candidate",
        },
        "mutation_performed": False,
    }


def status_payload() -> dict[str, Any]:
    policy = load_policy()
    validate_schema_documents()
    eval_cases, eval_path = load_eval_set(policy)
    policy_sha256 = digest(POLICY_PATH)
    eval_set_sha256 = digest(eval_path)
    incumbent_path = policy_file(policy["incumbent_results"], "incumbent_results")
    incumbent, _ = load_result(
        incumbent_path,
        label="incumbent results",
        policy=policy,
        eval_cases=eval_cases,
        policy_sha256=policy_sha256,
        eval_set_sha256=eval_set_sha256,
        candidate=False,
    )
    return {
        "schema_version": 1,
        "status": "PASS",
        "mode": policy["mode"],
        "policy_sha256": policy_sha256,
        "eval_set_sha256": eval_set_sha256,
        "protected_cases": len(eval_cases),
        "incumbent": incumbent["harness_id"],
        "allowed_surfaces": [surface["id"] for surface in policy["allowed_change_surfaces"]],
        "authority": policy["authority"],
        "mutation_performed": False,
    }


def print_status(payload: dict[str, Any]) -> None:
    print(f"Harness evolution {payload['status']} ({payload['mode']})")
    print(f"  Incumbent:       {payload['incumbent']}")
    print(f"  Protected cases: {payload['protected_cases']}")
    print(f"  Policy digest:   {payload['policy_sha256']}")
    print(f"  Eval digest:     {payload['eval_set_sha256']}")
    print("  Promotion:       forbidden; independent human review required")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status", help="Report policy, eval, and incumbent state")
    status.add_argument("--json", action="store_true")
    validate = sub.add_parser("validate", help="Validate the committed offline evolution contract")
    validate.add_argument("--json", action="store_true")
    signal = sub.add_parser("signal", help="Validate a sanitized aggregate outcome signal")
    signal_sub = signal.add_subparsers(dest="signal_command", required=True)
    signal_validate = signal_sub.add_parser("validate")
    signal_validate.add_argument("path")
    signal_validate.add_argument("--json", action="store_true")
    comparison = sub.add_parser("compare", help="Compare candidate results with the protected incumbent")
    comparison.add_argument("--candidate", required=True)
    comparison.add_argument("--incumbent")
    comparison.add_argument("--json", action="store_true")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command in {"status", "validate"}:
            payload = status_payload()
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print_status(payload)
            return 0
        if args.command == "signal" and args.signal_command == "validate":
            policy = load_policy()
            validate_schema_documents()
            signal = load_object(Path(args.path), "outcome signal")
            validate_signal(signal, policy)
            payload = {"schema_version": 1, "status": "PASS", "signal_id": signal["signal_id"], "mutation_performed": False}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(f"Sanitized outcome signal valid: {signal['signal_id']}")
            return 0
        if args.command == "compare":
            report = compare(
                Path(args.candidate),
                Path(args.incumbent) if args.incumbent else None,
            )
            if args.json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(f"Harness candidate verdict: {report['verdict']}")
                print(f"  Quality gain: {report['metrics']['weighted_quality_gain']}")
                print(f"  Cost ratio:   {report['metrics']['cost_ratio']}")
                print(f"  p95 ratio:    {report['metrics']['p95_latency_ratio']}")
                failed = [name for name, passed in report["gates"].items() if not passed]
                print("  Failed gates: " + (", ".join(failed) if failed else "none"))
                print("  Reviews:      " + ", ".join(report["required_reviews"]))
                print("  Promotion: forbidden; independent human review required")
            return 0 if report["verdict"] == "PASS" else 1
        raise EvolutionError("Unsupported evolution command")
    except EvolutionError as error:
        print(f"Harness evolution stopped safely: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
