from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "capability_adapters"))

import agency_agents  # noqa: E402


class AgencyAgentsPlannerTests(unittest.TestCase):
    def run_main(self, arguments: list[str]) -> tuple[int, str, str]:
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            result = agency_agents.main(["--root", str(ROOT), *arguments])
        return result, output.getvalue(), errors.getvalue()

    def test_manifest_matches_shared_contract_and_provenance(self) -> None:
        manifest = json.loads((ROOT / ".agentic/capabilities/agency-agents.json").read_text())
        self.assertEqual({
            "schema_version", "id", "kind", "display_name", "status", "summary",
            "source", "recommend_when", "authority", "setup", "rollback", "risks",
        }, set(manifest))
        self.assertEqual({
            "profiles_any_of", "task_terms_any_of", "task_owners_any_of", "file_patterns_any_of",
        }, set(manifest["recommend_when"]))
        self.assertEqual("optional", manifest["status"])
        self.assertEqual([], manifest["recommend_when"]["profiles_any_of"])
        self.assertEqual([], manifest["recommend_when"]["task_owners_any_of"])
        self.assertEqual("none", manifest["authority"]["default"])
        self.assertFalse(manifest["setup"]["automatic"])
        self.assertEqual("plan_only", manifest["setup"]["mode"])
        self.assertEqual(agency_agents.EXPECTED_REPOSITORY, manifest["source"]["repository"])
        self.assertEqual(agency_agents.EXPECTED_COMMIT, manifest["source"]["reviewed_commit"])
        self.assertEqual("MIT", manifest["source"]["license"])

    def test_doctor_validates_allowlist_without_mutation(self) -> None:
        watched = [ROOT / ".agentic/external-agents.json", ROOT / ".agentic/project.json"]
        before = {path: path.read_bytes() for path in watched}
        result, output, errors = self.run_main(["doctor", "--json"])
        self.assertEqual(0, result, errors)
        payload = json.loads(output)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(14, payload["eligible_agent_count"])
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["network_used"])
        self.assertFalse(payload["external_code_executed"])
        self.assertEqual(before, {path: path.read_bytes() for path in watched})

    def test_plan_is_selective_pinned_diff_first_and_project_local(self) -> None:
        result, output, errors = self.run_main([
            "plan", "--agent", "multi-agent-systems", "--agent", "evidence-collector", "--json",
        ])
        self.assertEqual(0, result, errors)
        payload = json.loads(output)
        self.assertEqual("plan_only", payload["mode"])
        self.assertEqual(["multi-agent-systems", "evidence-collector"], payload["selected_agent_ids"])
        self.assertEqual(agency_agents.EXPECTED_COMMIT, payload["provenance"]["reviewed_commit"])
        self.assertEqual("untrusted_data", payload["provenance"]["upstream_content_trust"])
        self.assertTrue(payload["backup"]["required_before_future_write"])
        self.assertFalse(payload["backup"]["performed"])
        for item in payload["items"]:
            self.assertIn(agency_agents.EXPECTED_COMMIT, item["source_url"])
            self.assertTrue(item["proposed_destination"].startswith(".agentic/"))
            self.assertEqual("inactive_review_staging", item["destination_state"])
            self.assertTrue(item["checksum"]["verification_required"])
            self.assertIsNone(item["checksum"]["expected"])
            self.assertTrue(item["conversion_required"])
            self.assertFalse(item["activation_planned"])
        for field in (
            "mutation_performed", "network_used", "download_performed", "external_code_executed",
            "conversion_performed", "activation_performed", "authority_changed",
        ):
            self.assertFalse(payload[field])

    def test_unknown_and_wildcard_agents_fail_closed(self) -> None:
        for agent_id, expected in (
            ("not-reviewed", "not in the reviewed local allowlist"),
            ("*", "wildcards are forbidden"),
            ("engineering-*", "wildcards are forbidden"),
        ):
            with self.subTest(agent_id=agent_id):
                result, _, errors = self.run_main(["plan", "--agent", agent_id, "--json"])
                self.assertEqual(2, result)
                self.assertIn(expected, errors)

    def test_bulk_global_auto_update_and_mutating_flags_are_rejected(self) -> None:
        for flag in (
            "--all", "--bulk", "--division", "--global", "--user-global", "--auto-update",
            "--fetch", "--download", "--install", "--execute", "--activate",
        ):
            with self.subTest(flag=flag):
                result, _, errors = self.run_main([
                    "plan", "--agent", "multi-agent-systems", flag, "--json",
                ])
                self.assertEqual(2, result)
                self.assertIn("is forbidden", errors)

    def test_destination_must_be_project_local_and_narrow(self) -> None:
        for destination in ("~/.claude/agents", "/tmp/agency-agents", "docs/vendor"):
            with self.subTest(destination=destination):
                result, _, errors = self.run_main([
                    "plan", "--agent", "multi-agent-systems",
                    "--destination", destination, "--json",
                ])
                self.assertEqual(2, result)
                self.assertIn("destination", errors)

    def test_adapter_has_no_download_execution_or_write_surface(self) -> None:
        source = (ROOT / "scripts/capability_adapters/agency_agents.py").read_text()
        for forbidden in (
            "import subprocess", "import urllib", "import requests", "import http",
            ".write_text(", ".write_bytes(", "git clone", "curl ",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
