from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evolution_engine  # noqa: E402


class EvolutionEngineTests(unittest.TestCase):
    def incumbent(self) -> dict:
        return json.loads((ROOT / ".agentic/evolution/incumbent.json").read_text())

    def passing_candidate(self) -> dict:
        candidate = copy.deepcopy(self.incumbent())
        candidate["harness_id"] = "candidate-v1"
        candidate["builder_role"] = "orchestrator"
        candidate["evaluator_role"] = "qa-evaluator"
        candidate["changed_paths"] = ["CLAUDE.md"]
        for case in candidate["cases"]:
            case["quality_score"] = min(1.0, case["quality_score"] + 0.07)
            case["cost_units"] = round(case["cost_units"] * 1.05, 4)
            case["latency_ms"] = round(case["latency_ms"] * 1.05, 4)
        return candidate

    def write(self, directory: str, name: str, payload: dict) -> Path:
        path = Path(directory) / name
        path.write_text(json.dumps(payload, indent=2) + "\n")
        return path

    def test_committed_contract_is_valid_and_non_mutating(self) -> None:
        status = evolution_engine.status_payload()
        self.assertEqual("PASS", status["status"])
        self.assertEqual("offline_proposal_only", status["mode"])
        self.assertEqual(5, status["protected_cases"])
        self.assertFalse(status["authority"]["promote"])
        self.assertFalse(status["authority"]["merge"])
        self.assertFalse(status["mutation_performed"])

    def test_candidate_passes_all_gates_but_is_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            report = evolution_engine.compare(
                self.write(temporary, "candidate.json", self.passing_candidate())
            )
        self.assertEqual("PASS", report["verdict"])
        self.assertTrue(all(report["gates"].values()))
        self.assertFalse(report["promotion"]["authorized"])
        self.assertTrue(report["promotion"]["human_review_required"])
        self.assertFalse(report["mutation_performed"])
        self.assertEqual(["qa-evaluator", "security"], report["required_reviews"])

    def test_protected_quality_regression_fails(self) -> None:
        candidate = self.passing_candidate()
        candidate["cases"][0]["quality_score"] = 0.8
        with tempfile.TemporaryDirectory() as temporary:
            report = evolution_engine.compare(self.write(temporary, "candidate.json", candidate))
        self.assertEqual("FAIL", report["verdict"])
        self.assertFalse(report["gates"]["protected_regressions"])
        self.assertIn("traceability", report["metrics"]["protected_regressions"])

    def test_safety_failure_fails_even_with_quality_gain(self) -> None:
        candidate = self.passing_candidate()
        candidate["cases"][1]["safety_pass"] = False
        with tempfile.TemporaryDirectory() as temporary:
            report = evolution_engine.compare(self.write(temporary, "candidate.json", candidate))
        self.assertEqual("FAIL", report["verdict"])
        self.assertFalse(report["gates"]["safety_failures"])
        self.assertEqual(["unsafe-authority-expansion"], report["metrics"]["safety_failures"])

    def test_cost_and_latency_blowup_fail(self) -> None:
        candidate = self.passing_candidate()
        for case in candidate["cases"]:
            case["cost_units"] *= 2
            case["latency_ms"] *= 2
        with tempfile.TemporaryDirectory() as temporary:
            report = evolution_engine.compare(self.write(temporary, "candidate.json", candidate))
        self.assertEqual("FAIL", report["verdict"])
        self.assertFalse(report["gates"]["cost_budget"])
        self.assertFalse(report["gates"]["p95_latency_budget"])

    def test_candidate_cannot_modify_its_policy_or_exam(self) -> None:
        candidate = self.passing_candidate()
        candidate["changed_paths"] = [".agentic/evolution/policy.json"]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(temporary, "candidate.json", candidate)
            with self.assertRaisesRegex(evolution_engine.EvolutionError, "protected path"):
                evolution_engine.compare(path)

    def test_candidate_cannot_modify_unapproved_surface(self) -> None:
        candidate = self.passing_candidate()
        candidate["changed_paths"] = ["scripts/new-tool.py"]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(temporary, "candidate.json", candidate)
            with self.assertRaisesRegex(evolution_engine.EvolutionError, "outside allowed"):
                evolution_engine.compare(path)

    def test_stale_policy_or_eval_digest_fails_closed(self) -> None:
        candidate = self.passing_candidate()
        candidate["policy_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(temporary, "candidate.json", candidate)
            with self.assertRaisesRegex(evolution_engine.EvolutionError, "different policy digest"):
                evolution_engine.compare(path)

    def test_missing_protected_case_fails_closed(self) -> None:
        candidate = self.passing_candidate()
        candidate["cases"].pop()
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(temporary, "candidate.json", candidate)
            with self.assertRaisesRegex(evolution_engine.EvolutionError, "missing protected eval"):
                evolution_engine.compare(path)

    def test_builder_and_evaluator_must_differ(self) -> None:
        candidate = self.passing_candidate()
        candidate["evaluator_role"] = candidate["builder_role"]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(temporary, "candidate.json", candidate)
            with self.assertRaisesRegex(evolution_engine.EvolutionError, "must remain separate"):
                evolution_engine.compare(path)

    def test_sanitized_signal_is_accepted(self) -> None:
        policy = evolution_engine.load_policy()
        signal = {
            "schema_version": 1,
            "signal_id": "pr:60:verification",
            "observed_at": "2026-08-23T23:30:00Z",
            "source_type": "verification",
            "outcome": "success",
            "metrics": {
                "quality_score": 0.91,
                "safety_pass": True,
                "cost_units": 12,
                "latency_ms": 920,
            },
            "labels": ["full-verification", "human-reviewed"],
            "provenance": {"source_ref": "pr:#60", "authority": "repository_check"},
            "privacy": {
                "redacted": True,
                "contains_personal_data": False,
                "contains_secrets": False,
                "retention_class": "aggregate_only",
            },
        }
        evolution_engine.validate_signal(signal, policy)

    def test_raw_or_identifying_signal_fields_are_rejected(self) -> None:
        policy = evolution_engine.load_policy()
        signal = {
            "schema_version": 1,
            "signal_id": "pr:60:failure",
            "observed_at": "2026-08-23T23:30:00Z",
            "source_type": "review",
            "outcome": "failure",
            "metrics": {
                "quality_score": 0.2,
                "safety_pass": False,
                "cost_units": 10,
                "latency_ms": 900,
                "prompt": "raw content must never be retained",
            },
            "labels": ["unsafe"],
            "provenance": {"source_ref": "pr:#60", "authority": "human"},
            "privacy": {
                "redacted": True,
                "contains_personal_data": False,
                "contains_secrets": False,
                "retention_class": "aggregate_only",
            },
        }
        with self.assertRaisesRegex(evolution_engine.EvolutionError, "forbidden raw"):
            evolution_engine.validate_signal(signal, policy)

    def test_cli_emits_machine_readable_pass_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(temporary, "candidate.json", self.passing_candidate())
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/evolution_engine.py"), "compare", "--candidate", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual("PASS", report["verdict"])
        self.assertFalse(report["promotion"]["authorized"])
        self.assertFalse(report["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
