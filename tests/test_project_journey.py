from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import project_journey


class ProjectJourneyTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".agentic").mkdir()
        (self.root / ".agentic/generated-project.json").write_text("{}")
        self.brief = {
            "schema_version": 1,
            "name": "Afford",
            "audience": "households",
            "promise": "Make a confident purchase decision",
            "first_outcome": None,
            "design_preferences": None,
            "design_mode": "custom",
            "research_enabled": True,
            "assistant": "manual",
            "status": "captured",
            "confirmed_by": None,
            "open_questions": ["Confirm one journey"],
        }
        (self.root / ".agentic/project-brief.json").write_text(json.dumps(self.brief))
        (self.root / ".agentic/design.json").write_text(json.dumps({"status": "needs_approval"}))
        (self.root / "docs/10-product").mkdir(parents=True)
        (self.root / "docs/10-product/RESEARCH.md").write_text("# Research\n\nStatus: Not started\n")
        (self.root / "docs/40-execution").mkdir(parents=True)
        (self.root / "docs/40-execution/TASKS.jsonl").write_text("")
        self.profiles = mock.patch.object(
            project_journey.next_action,
            "active_profiles",
            return_value=["web-next", "design-critical", "research-enabled"],
        )
        self.action = mock.patch.object(
            project_journey.next_action,
            "next_action",
            return_value=("Create live directions", "./agentic design sprint"),
        )
        self.profiles.start()
        self.action.start()
        self.addCleanup(mock.patch.stopall)

    def test_research_to_review_journey_is_read_only(self) -> None:
        tracked = [
            self.root / ".agentic/project-brief.json",
            self.root / ".agentic/design.json",
            self.root / "docs/10-product/RESEARCH.md",
            self.root / "docs/40-execution/TASKS.jsonl",
        ]
        before = {path: path.read_bytes() for path in tracked}
        result = project_journey.build(self.root)
        stages = {stage["id"]: stage["status"] for stage in result["stages"]}
        self.assertEqual("selected", stages["research"])
        self.assertEqual("active", stages["product"])
        self.assertEqual("waiting", stages["design"])
        self.assertEqual("waiting", stages["build"])
        self.assertFalse(result["mutation_performed"])
        self.assertEqual("./agentic design sprint", result["next"]["action"])
        self.assertEqual(before, {path: path.read_bytes() for path in tracked})
        rendered = project_journey.render(result)
        self.assertIn("PROJECT JOURNEY — Afford", rendered)
        self.assertIn("[SELECTED] RESEARCH", rendered)
        self.assertIn("NEXT", rendered)

    def test_completed_research_and_review_task_are_reported_without_certifying_quality(self) -> None:
        (self.root / "docs/10-product/RESEARCH.md").write_text("# Research\n\nStatus: Complete\n")
        self.brief.update(status="ready", first_outcome="Compare two purchase dates", confirmed_by="Owner")
        (self.root / ".agentic/project-brief.json").write_text(json.dumps(self.brief))
        (self.root / ".agentic/design.json").write_text(json.dumps({"status": "approved"}))
        task = {"id": "T-101", "status": "review"}
        (self.root / "docs/40-execution/TASKS.jsonl").write_text(json.dumps(task) + "\n")
        result = project_journey.build(self.root)
        stages = {stage["id"]: stage["status"] for stage in result["stages"]}
        self.assertEqual("complete", stages["research"])
        self.assertEqual("complete", stages["product"])
        self.assertEqual("complete", stages["design"])
        self.assertEqual("active", stages["verify"])
        self.assertEqual("active", stages["review"])
        review = next(stage for stage in result["stages"] if stage["id"] == "review")
        self.assertIn("human approval", review["detail"])

    def test_no_research_path_is_explicitly_skipped(self) -> None:
        self.brief["research_enabled"] = False
        (self.root / ".agentic/project-brief.json").write_text(json.dumps(self.brief))
        with mock.patch.object(
            project_journey.next_action,
            "active_profiles",
            return_value=["web-next", "design-critical"],
        ):
            result = project_journey.build(self.root)
        research = next(stage for stage in result["stages"] if stage["id"] == "research")
        self.assertEqual("skipped", research["status"])

    def test_source_checkout_routes_to_creation(self) -> None:
        (self.root / ".agentic/generated-project.json").unlink()
        with mock.patch.object(
            project_journey.next_action,
            "next_action",
            return_value=("Create a project", "./agentic setup create"),
        ):
            result = project_journey.build(self.root)
        self.assertEqual("decision", result["stages"][0]["status"])
        self.assertEqual("./agentic setup create", result["next"]["action"])


if __name__ == "__main__":
    unittest.main()
