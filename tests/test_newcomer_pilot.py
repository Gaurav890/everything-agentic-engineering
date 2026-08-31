from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "newcomer_pilot",
    ROOT / "scripts" / "newcomer-pilot.py",
)
assert SPEC and SPEC.loader
newcomer_pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(newcomer_pilot)


class NewcomerPilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = newcomer_pilot.load_policy()

    def scorecard(self, session_id: str, *, interventions: list[dict] | None = None) -> dict:
        value = newcomer_pilot.template_scorecard(session_id, self.policy)
        value["consent"] = {
            "participant_consented": True,
            "observer_explained_data_boundary": True,
        }
        value["environment"] = {
            "operating_system": "macos",
            "experience_level": "working_frontend_knowledge",
            "profile": "web-next",
            "node_version": "22.12.0",
            "pnpm_version": "9.15.9",
            "python_version": "3.12.4",
        }
        value["timings"] = {
            "download_and_tooling_minutes": 3,
            "product_flow_minutes": 34,
            "time_to_personalized_preview_minutes": 8,
        }
        value["outcomes"] = {
            "creation_completed": True,
            "personalization_completed": True,
            "feature_completed": True,
            "applicable_verification_completed": True,
            "evidence_boundaries_understood": True,
            "next_step_identified": True,
        }
        value["interventions"] = interventions or []
        value["quality"] = {
            "independent_evaluator": True,
            "hierarchy": 4,
            "content_specificity": 4,
            "interaction": 4,
            "accessibility": 4,
        }
        return value

    def test_policy_and_schema_are_closed(self) -> None:
        schema = json.loads((ROOT / ".agentic" / "pilot" / "scorecard.schema.json").read_text())
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(5, self.policy["required_sessions"])
        self.assertEqual(4, self.policy["thresholds"]["minimum_unassisted_completions"])

    def test_template_intentionally_fails_until_consent_and_evidence_exist(self) -> None:
        with self.assertRaisesRegex(newcomer_pilot.PilotError, "consent"):
            newcomer_pilot.validate_scorecard(
                newcomer_pilot.template_scorecard("P1", self.policy),
                self.policy,
            )

    def test_valid_scorecard_passes(self) -> None:
        value = self.scorecard("P1")
        self.assertIs(value, newcomer_pilot.validate_scorecard(value, self.policy))

    def test_unknown_and_sensitive_fields_fail_closed(self) -> None:
        unknown = self.scorecard("P1")
        unknown["participant_name"] = "redacted"
        with self.assertRaisesRegex(newcomer_pilot.PilotError, "keys are closed"):
            newcomer_pilot.validate_scorecard(unknown, self.policy)

        direct_identifier = self.scorecard("P1")
        direct_identifier["environment"]["email"] = "person@example.com"
        with self.assertRaisesRegex(newcomer_pilot.PilotError, "identifier or secret|Forbidden"):
            newcomer_pilot.validate_scorecard(direct_identifier, self.policy)

        secret = self.scorecard("P1")
        secret["environment"]["node_version"] = "sk-abcdefghijklmnopqrstuvwxyz123456"
        with self.assertRaisesRegex(newcomer_pilot.PilotError, "identifier or secret"):
            newcomer_pilot.validate_scorecard(secret, self.policy)

    def test_invalid_time_and_missing_independent_evaluator_fail(self) -> None:
        invalid_time = self.scorecard("P1")
        invalid_time["timings"]["product_flow_minutes"] = -1
        with self.assertRaisesRegex(newcomer_pilot.PilotError, "0 to 480"):
            newcomer_pilot.validate_scorecard(invalid_time, self.policy)

        no_evaluator = self.scorecard("P1")
        no_evaluator["quality"]["independent_evaluator"] = False
        with self.assertRaisesRegex(newcomer_pilot.PilotError, "separate evaluator"):
            newcomer_pilot.validate_scorecard(no_evaluator, self.policy)

    def test_create_requires_confirmation_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "pilot"
            self.assertEqual(
                0,
                newcomer_pilot.main(["create", "P1", "--output", str(target)]),
            )
            self.assertFalse(target.exists())
            self.assertEqual(
                0,
                newcomer_pilot.main(["create", "P1", "--output", str(target), "--yes"]),
            )
            self.assertTrue((target / "P1" / "scorecard.json").is_file())
            instructions = (target / "P1" / "SESSION.md").read_text()
            self.assertNotIn(str(target), instructions)
            self.assertIn("<pilot-root>/P1/scorecard.json", instructions)
            self.assertEqual(
                2,
                newcomer_pilot.main(["create", "P1", "--output", str(target), "--yes"]),
            )

    def test_incomplete_sample_is_never_a_pass(self) -> None:
        report = newcomer_pilot.build_report([self.scorecard("P1")], self.policy)
        self.assertEqual("INSUFFICIENT_EVIDENCE", report["verdict"])
        self.assertEqual(1, report["sample_size"])

    def test_five_unassisted_sessions_pass_the_launch_gate(self) -> None:
        scorecards = [self.scorecard(f"P{index}") for index in range(1, 6)]
        report = newcomer_pilot.build_report(scorecards, self.policy)
        self.assertEqual("PASS", report["verdict"])
        self.assertTrue(all(item["passed"] for item in report["gate_results"]))
        self.assertEqual(34.0, report["metrics"]["median_product_flow_minutes"])

    def test_repeated_unresolved_blocker_fails_complete_sample(self) -> None:
        scorecards = [self.scorecard(f"P{index}") for index in range(1, 6)]
        blocker = {
            "stage": "creation",
            "code": "unclear_instruction",
            "safety_required": False,
            "resolved": False,
        }
        scorecards[0]["blockers"] = [dict(blocker)]
        scorecards[1]["blockers"] = [dict(blocker)]
        report = newcomer_pilot.build_report(scorecards, self.policy)
        self.assertEqual("FAIL", report["verdict"])
        self.assertEqual(["creation:unclear_instruction"], report["repeated_unresolved_blockers"])

    def test_any_intervention_removes_unassisted_status_but_is_reported(self) -> None:
        intervention = {
            "stage": "handoff",
            "code": "navigation_confusion",
            "safety_required": False,
        }
        scorecards = [self.scorecard(f"P{index}") for index in range(1, 6)]
        scorecards[0]["interventions"] = [intervention]
        report = newcomer_pilot.build_report(scorecards, self.policy)
        self.assertEqual("PASS", report["verdict"])
        self.assertEqual(4, report["metrics"]["unassisted_completions"])
        self.assertEqual(1, report["friction_counts"]["handoff:navigation_confusion"])

    def test_directory_summary_validates_session_directory_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            session = root / "P1"
            session.mkdir()
            wrong = self.scorecard("P2")
            (session / "scorecard.json").write_text(json.dumps(wrong))
            with self.assertRaisesRegex(newcomer_pilot.PilotError, "does not match"):
                newcomer_pilot.collect_scorecards(root, self.policy)

    def test_directory_summary_rejects_unknown_session_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            session = root / "P6"
            session.mkdir()
            (session / "scorecard.json").write_text(json.dumps(self.scorecard("P1")))
            with self.assertRaisesRegex(newcomer_pilot.PilotError, "Unexpected scorecard path"):
                newcomer_pilot.collect_scorecards(root, self.policy)


if __name__ == "__main__":
    unittest.main()
