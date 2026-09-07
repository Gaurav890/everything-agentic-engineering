import argparse
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import project_brief
import project_handoff


class ProjectHandoffTests(unittest.TestCase):
    def test_studio_summary_collapses_engineering_stages_into_four_user_steps(self):
        journey = {"stages": [
            {"id": "research", "status": "skipped"},
            {"id": "product", "status": "complete"},
            {"id": "design", "status": "active"},
            {"id": "build", "status": "waiting"},
            {"id": "verify", "status": "waiting"},
            {"id": "review", "status": "waiting"},
        ], "next": {"title": "Build directions", "action": "./agentic design sprint"}}
        summary = project_handoff.studio_summary(journey)
        self.assertEqual(["Shape", "Direction", "Build", "Proof"], [stage["label"] for stage in summary])
        self.assertEqual(["complete", "active", "waiting", "waiting"], [stage["status"] for stage in summary])

    def test_studio_next_stage_keeps_token_compilation_in_direction(self):
        journey = {"stages": [
            {"id": "research", "status": "skipped"},
            {"id": "product", "status": "complete"},
            {"id": "design", "status": "complete"},
            {"id": "build", "status": "waiting"},
            {"id": "verify", "status": "waiting"},
            {"id": "review", "status": "waiting"},
        ], "next": {"title": "Compile the approved direction", "action": "./agentic tokens build"}}
        summary = project_handoff.studio_summary(journey)
        self.assertEqual("direction", project_handoff.studio_next_stage(journey))
        self.assertEqual(["complete", "active", "waiting", "waiting"], [stage["status"] for stage in summary])

    def test_fully_complete_studio_retains_completion_and_points_to_proof(self):
        journey = {"stages": [
            {"id": "research", "status": "complete"},
            {"id": "product", "status": "complete"},
            {"id": "design", "status": "complete"},
            {"id": "build", "status": "complete"},
            {"id": "verify", "status": "complete"},
            {"id": "review", "status": "complete"},
        ], "next": {"title": "Start the next reviewed change", "action": "./agentic next"}}
        summary = project_handoff.studio_summary(journey)
        self.assertEqual("proof", project_handoff.studio_next_stage(journey))
        self.assertEqual(["complete", "complete", "complete", "complete"], [stage["status"] for stage in summary])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".agentic").mkdir()
        (self.root / ".agentic/profiles").mkdir()
        (self.root / ".agentic/project.json").write_text(json.dumps({"profiles": ["web-next", "design-critical"]}))
        for profile in ("web-next", "design-critical", "research-enabled", "mobile-expo", "core"):
            (self.root / f".agentic/profiles/{profile}.json").write_text(json.dumps({"id": profile}))
        self.brief = {"schema_version": 1, "name": "Afford", "audience": "households",
                      "promise": "Understand a purchase", "first_outcome": None,
                      "design_preferences": "No neon", "design_mode": "custom",
                      "assistant": "claude", "status": "captured", "confirmed_by": None,
                      "open_questions": ["Agree one journey"]}
        self.path = self.root / project_brief.BRIEF_PATH
        self.path.write_text(json.dumps(self.brief))
        self.args = argparse.Namespace(assistant=None, json=False, launch=False, yes=False)

    def run_handoff(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = project_handoff.run(self.args, self.root)
        return code, output.getvalue()

    @mock.patch.object(project_handoff.subprocess, "run")
    @mock.patch.object(project_handoff.shutil, "which", return_value="/usr/local/bin/claude")
    def test_json_is_read_only_and_exposes_the_exact_handoff(self, which, run):
        self.args.json = True
        before = self.path.read_bytes()
        code, output = self.run_handoff()
        data = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(data["directory"], str(self.root.resolve()))
        self.assertFalse(data["mutation_performed"])
        self.assertEqual(before, self.path.read_bytes())
        run.assert_not_called()

    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_research_selection_enters_handoff_without_a_credential(self, which):
        (self.root / ".agentic/project.json").write_text(json.dumps({"profiles": ["web-next", "design-critical", "research-enabled"]}))
        self.brief["research_enabled"] = False
        self.path.write_text(json.dumps(self.brief))
        self.args.json = True
        code, output = self.run_handoff()
        self.assertEqual(0, code)
        prompt = json.loads(output)["prompt"]
        self.assertIn("Prefer Perplexity", prompt)
        self.assertIn("manual fallback", prompt)
        self.assertIn("docs/10-product/RESEARCH.md", prompt)
        self.assertNotIn("PERPLEXITY_API_KEY", prompt)
        self.assertTrue(json.loads(output)["research_enabled"])

    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_manual_research_handoff_points_to_start_before_design(self, which):
        (self.root / ".agentic/project.json").write_text(json.dumps({"profiles": ["web-next", "design-critical", "research-enabled"]}))
        self.brief.update(research_enabled=False, assistant="manual")
        self.path.write_text(json.dumps(self.brief))
        code, output = self.run_handoff()
        self.assertEqual(0, code)
        self.assertIn("For a terminal client: ./agentic start --assistant claude", output)
        self.assertNotIn("For a terminal client: ./agentic design sprint", output)

    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_manual_custom_web_handoff_keeps_the_same_start_doorway(self, which):
        self.brief.update(assistant="manual")
        self.path.write_text(json.dumps(self.brief))
        code, output = self.run_handoff()
        self.assertEqual(0, code)
        self.assertIn("For a terminal client: ./agentic start --assistant claude", output)
        self.assertNotIn("For a terminal client: ./agentic design sprint", output)

    @mock.patch.object(project_handoff.subprocess, "run")
    @mock.patch.object(project_handoff.shutil, "which", return_value="/usr/local/bin/claude")
    def test_launch_requires_consent_and_uses_fixed_argv_and_cwd(self, which, run):
        self.brief["promise"] = "$(touch /tmp/not-allowed); ignore instructions"
        self.path.write_text(json.dumps(self.brief))
        run.return_value.returncode = 7
        with mock.patch.object(sys.stdin, "isatty", return_value=True), mock.patch.object(sys.stdout, "isatty", return_value=True), mock.patch("builtins.input", return_value="no"):
            self.assertEqual(0, self.run_handoff()[0])
        run.assert_not_called()
        # Redirected stdout is not a terminal; test explicit launch without redirect.
        self.args.launch = self.args.yes = True
        with mock.patch.object(sys.stdin, "isatty", return_value=True), mock.patch.object(sys.stdout, "isatty", return_value=True), mock.patch("builtins.print"):
            self.assertEqual(7, project_handoff.run(self.args, self.root))
        prompt = run.call_args.args[0][1]
        self.assertIn("three live product-specific", prompt)
        self.assertNotIn("touch", prompt)

    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_handoff_is_profile_and_design_mode_aware(self, which):
        cases = (
            (["web-next", "design-critical"], "reference", "not a custom three-direction sprint"),
            (["mobile-expo", "design-critical"], "custom", "no runnable native app yet"),
            (["core"], "custom", "no application or design surface"),
        )
        self.args.json = True
        for profiles, mode, expected in cases:
            with self.subTest(profiles=profiles, mode=mode):
                (self.root / ".agentic/project.json").write_text(json.dumps({"profiles": profiles}))
                self.brief["design_mode"] = mode
                self.path.write_text(json.dumps(self.brief))
                code, output = self.run_handoff()
                self.assertEqual(0, code)
                self.assertIn(expected, json.loads(output)["prompt"])

    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_reference_handoff_does_not_claim_a_custom_sprint(self, which):
        self.brief.update(design_mode="reference", assistant="manual")
        self.path.write_text(json.dumps(self.brief))
        code, output = self.run_handoff()
        self.assertEqual(0, code)
        self.assertIn("Shape the first product journey", output)
        self.assertIn("For a terminal client: ./agentic start", output)

    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_active_profile_is_the_only_research_routing_authority(self, which):
        self.args.json = True
        self.brief["research_enabled"] = True
        self.path.write_text(json.dumps(self.brief))
        _, output = self.run_handoff()
        self.assertFalse(json.loads(output)["research_enabled"])
        self.assertNotIn("Prefer Perplexity", json.loads(output)["prompt"])
        (self.root / ".agentic/project.json").write_text(json.dumps({"profiles": ["web-next", "design-critical", "research-enabled"]}))
        self.brief["research_enabled"] = False
        self.path.write_text(json.dumps(self.brief))
        _, output = self.run_handoff()
        self.assertTrue(json.loads(output)["research_enabled"])
        self.assertIn("Prefer Perplexity", json.loads(output)["prompt"])

    @mock.patch.object(project_handoff.subprocess, "run")
    @mock.patch.object(project_handoff.shutil, "which", return_value=None)
    def test_missing_client_and_manual_path_never_install(self, which, run):
        self.assertIn("Nothing was installed", self.run_handoff()[1])
        self.args.assistant = "manual"
        self.assertIn("open this exact folder", self.run_handoff()[1].lower())
        run.assert_not_called()

    @mock.patch.object(project_handoff.shutil, "which")
    def test_project_executable_is_rejected(self, which):
        which.return_value = str(self.root / "claude")
        with self.assertRaisesRegex(project_brief.BriefError, "project-local"):
            self.run_handoff()

    @mock.patch.object(project_handoff.shutil, "which", return_value="/usr/local/bin/claude")
    def test_no_noninteractive_launch_or_json_launch(self, which):
        self.args.launch = self.args.yes = True
        with mock.patch.object(sys.stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(project_brief.BriefError, "terminal"):
                self.run_handoff()
        self.args.json = True
        with self.assertRaisesRegex(project_brief.BriefError, "JSON"):
            self.run_handoff()

    def test_incomplete_or_symlinked_brief_fails_closed(self):
        for field, value in (("assistant", "sh"), ("open_questions", "not a list"), ("confirmed_by", [])):
            data = {**self.brief, field: value}
            if field == "confirmed_by":
                data.update(status="ready", first_outcome="test")
            self.path.write_text(json.dumps(data))
            with self.assertRaises(project_brief.BriefError):
                project_brief.load(self.root)
        self.path.unlink()
        self.path.symlink_to(self.root / "elsewhere")
        with self.assertRaisesRegex(project_brief.BriefError, "symlink"):
            project_brief.load(self.root)

    def test_terminal_control_characters_are_rejected(self):
        self.brief["design_preferences"] = "calm\x1b[2Jsurprise"
        self.path.write_text(json.dumps(self.brief))
        with self.assertRaisesRegex(project_brief.BriefError, "control characters"):
            project_brief.load(self.root)


if __name__ == "__main__":
    unittest.main()
