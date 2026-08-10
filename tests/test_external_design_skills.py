from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".agentic" / "external-skills.json"
ROUTER = ROOT / ".claude" / "skills" / "design-engineering-quality" / "SKILL.md"

EXPECTED_EMIL_SKILLS = {
    "emil-design-eng",
    "animate",
    "review-animations",
    "improve-animations",
    "find-animation-opportunities",
    "animation-vocabulary",
    "apple-design",
    "prototype",
    "pick-ui-library",
    "ask-sonner",
}


class ExternalDesignSkillsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.collection = cls.manifest["collections"]["emilkowalski-design-engineering"]
        cls.skills = cls.collection["skills"]

    def test_reviewed_collection_has_exact_upstream_inventory(self) -> None:
        names = [skill["name"] for skill in self.skills]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), EXPECTED_EMIL_SKILLS)

    def test_provenance_install_and_license_are_explicit(self) -> None:
        self.assertEqual(self.collection["source_repository"], "https://github.com/emilkowalski/skills")
        self.assertRegex(self.collection["reviewed_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(self.collection["license"], "MIT")
        self.assertEqual(self.collection["install_command"], "npx skills@latest add emilkowalski/skills")
        self.assertIn(self.collection["reviewed_commit"], self.collection["reviewed_install_command"])
        self.assertEqual(self.collection["profiles"], ["design-critical"])
        self.assertEqual(
            self.collection["default_external_design_implementation_skill"],
            "emil-design-eng",
        )
        self.assertEqual(self.collection["anthropic_frontend_design_policy"], "secondary_opt_in")

    def test_external_suite_is_never_automatic_or_vendored(self) -> None:
        policy = self.manifest["policy"]
        self.assertFalse(policy["automatic_install"])
        self.assertFalse(policy["vendor_source"])
        self.assertFalse(policy["invoke_all_by_default"])
        self.assertTrue(policy["project_design_system_wins"])

    def test_each_skill_has_complete_routing_metadata(self) -> None:
        allowed_activations = {"routed_when_installed", "explicit_only", "conditional"}
        for skill in self.skills:
            with self.subTest(skill=skill["name"]):
                self.assertTrue(skill["source_url"].startswith("https://github.com/emilkowalski/skills/tree/main/skills/"))
                self.assertTrue(skill["phases"])
                self.assertIn(skill["activation"], allowed_activations)
                self.assertTrue(skill["trigger"].strip())

    def test_high_authority_actions_require_explicit_invocation(self) -> None:
        activation = {skill["name"]: skill["activation"] for skill in self.skills}
        self.assertEqual(activation["prototype"], "explicit_only")
        self.assertEqual(activation["pick-ui-library"], "explicit_only")
        self.assertEqual(activation["review-animations"], "explicit_only")

    def test_local_router_covers_every_skill_and_preserves_authority(self) -> None:
        text = ROUTER.read_text()
        for name in EXPECTED_EMIL_SKILLS:
            self.assertIn(f"`{name}`", text)
        self.assertIn("project contract wins", text)
        self.assertIn("do not animate", text)
        self.assertIn("independent final critic", text)

    def test_profile_aware_installer_has_a_non_mutating_preview(self) -> None:
        result = subprocess.run(
            [str(ROOT / "scripts" / "install-skills.sh"), "--dry-run"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("emilkowalski/skills", result.stdout)
        self.assertIn(self.collection["reviewed_commit"], result.stdout)
        self.assertIn("react-best-practices", result.stdout)
        self.assertNotIn("react-native-guidelines", result.stdout)
        self.assertIn("No external skills were installed", result.stdout)


if __name__ == "__main__":
    unittest.main()
