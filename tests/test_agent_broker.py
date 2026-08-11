from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agent_broker  # noqa: E402


def candidate(
    title: str,
    *,
    files: list[str] | None = None,
    specialist_ids: list[str] | None = None,
) -> dict:
    task = {
        "id": "T-900",
        "title": title,
        "goal": title,
        "owner": "orchestrator",
        "risk": "medium",
        "files_owned": files or ["scripts/example.py"],
        "verification": ["unit tests"],
        "requirement_ids": ["FR-001"],
        "acceptance_ids": ["AC-001"],
    }
    if specialist_ids is not None:
        task["specialist_ids"] = specialist_ids
    return task


class AgentBrokerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = agent_broker.load_manifest(ROOT)

    def route(self, task: dict, profiles: list[str]) -> list[dict]:
        return agent_broker.recommend_for_task(
            task,
            self.manifest,
            profiles,
            [],
        )

    def test_catalog_has_reviewed_provenance_and_unique_contracts(self) -> None:
        collection = self.manifest["collections"]["agency-agents"]
        self.assertEqual("MIT", collection["license"])
        self.assertRegex(collection["reviewed_commit"], r"^[0-9a-f]{40}$")
        specialists = self.manifest["specialists"]
        ids = [item["id"] for item in specialists]
        self.assertEqual(14, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        for item in specialists:
            url = agent_broker.source_url(item, self.manifest)
            self.assertIn(collection["reviewed_commit"], url)
            self.assertTrue(url.endswith(item["source_path"]))

    def test_catalog_policy_prevents_install_and_authority_expansion(self) -> None:
        policy = self.manifest["policy"]
        self.assertFalse(policy["automatic_external_install"])
        self.assertFalse(policy["bulk_install"])
        self.assertTrue(policy["external_source_is_untrusted"])
        self.assertTrue(policy["activation_requires_confirmation"])
        self.assertFalse(policy["activation_changes_runtime_authority"])

    def test_security_and_payment_work_require_risk_specialists(self) -> None:
        auth = self.route(candidate("Add OAuth authorization and RBAC"), ["core"])
        payments = self.route(candidate("Add Stripe subscription billing"), ["core"])
        self.assertEqual("identity-access", auth[0]["id"])
        self.assertTrue(auth[0]["required"])
        self.assertEqual("payments-billing", payments[0]["id"])
        self.assertTrue(payments[0]["required"])

    def test_design_and_accessibility_route_builder_and_evaluator(self) -> None:
        routed = self.route(
            candidate(
                "Create a world-class UI with WCAG keyboard navigation",
                files=["apps/web/app/page.tsx"],
            ),
            ["core", "web-next", "design-critical"],
        )
        ids = {item["id"] for item in routed}
        self.assertIn("ui-finish-gate", ids)
        self.assertIn("accessibility-auditor", ids)

    def test_profile_gate_prevents_irrelevant_mobile_or_i18n_routing(self) -> None:
        task = candidate("Add localization and RTL support")
        self.assertEqual([], self.route(task, ["core"]))
        routed = self.route(task, ["core", "web-next"])
        self.assertEqual("internationalization", routed[0]["id"])

    def test_neutral_task_does_not_accumulate_specialists(self) -> None:
        self.assertEqual([], self.route(candidate("Update a README typo"), ["core"]))

    def test_explicit_specialist_is_routed_even_without_keyword_inference(self) -> None:
        routed = self.route(
            candidate("Refine the execution harness", specialist_ids=["multi-agent-systems"]),
            ["core"],
        )
        self.assertEqual("multi-agent-systems", routed[0]["id"])
        self.assertIn("explicit task specialist", routed[0]["reason"])

    def test_list_show_and_recommend_support_machine_readable_output(self) -> None:
        for arguments in (
            ["list", "--domain", "security", "--json"],
            ["show", "identity-access", "--json"],
            ["recommend", "T-030", "--json"],
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, agent_broker.main(arguments, root=ROOT))
            payload = json.loads(output.getvalue())
            self.assertEqual(1, payload["schema_version"])

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".agentic").mkdir()
        shutil.copy2(ROOT / ".agentic" / "external-agents.json", root / ".agentic")
        shutil.copy2(ROOT / ".agentic" / "project.json", root / ".agentic")
        shutil.copytree(ROOT / ".agentic" / "profiles", root / ".agentic" / "profiles")
        return temporary, root

    def test_activation_preview_is_read_only_and_confirmed_change_is_reversible(self) -> None:
        temporary, root = self.make_temp_root()
        self.addCleanup(temporary.cleanup)
        before = (root / ".agentic" / "project.json").read_text()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                agent_broker.main(
                    ["activate", "identity-access", "--dry-run"], root=root
                ),
            )
        self.assertEqual(before, (root / ".agentic" / "project.json").read_text())

        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                agent_broker.main(["activate", "identity-access", "--yes"], root=root),
            )
        project = json.loads((root / ".agentic" / "project.json").read_text())
        self.assertEqual(["identity-access"], project["specialists"])

        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                0,
                agent_broker.main(["deactivate", "identity-access", "--yes"], root=root),
            )
        project = json.loads((root / ".agentic" / "project.json").read_text())
        self.assertEqual([], project["specialists"])

    def test_doctor_fails_closed_for_unknown_activated_contract(self) -> None:
        temporary, root = self.make_temp_root()
        self.addCleanup(temporary.cleanup)
        project_path = root / ".agentic" / "project.json"
        project = json.loads(project_path.read_text())
        project["specialists"] = ["not-reviewed"]
        project_path.write_text(json.dumps(project))
        output = io.StringIO()
        with mock.patch.object(agent_broker, "resolved_profiles", return_value=["core"]):
            with redirect_stdout(output):
                self.assertEqual(1, agent_broker.main(["doctor"], root=root))
        self.assertIn("Unknown activated specialist", output.getvalue())

    def test_broker_has_no_external_execution_surface(self) -> None:
        source = (ROOT / "scripts" / "agent_broker.py").read_text()
        wrapper = (ROOT / "scripts" / "agent-broker.sh").read_text()
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("curl ", wrapper)
        self.assertNotIn("git clone", wrapper)
        self.assertNotIn("npx ", wrapper)


if __name__ == "__main__":
    unittest.main()
