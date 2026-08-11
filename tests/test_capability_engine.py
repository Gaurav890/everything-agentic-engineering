from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import capability_engine  # noqa: E402


SHA = "1" * 40


class CapabilityEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / ".agentic" / "capabilities").mkdir(parents=True)
        (self.root / ".agentic" / "profiles").mkdir(parents=True)
        (self.root / "docs" / "40-execution").mkdir(parents=True)
        (self.root / "scripts" / "capability_adapters").mkdir(parents=True)
        self.write_json(
            ".agentic/project.json",
            {"schema_version": 1, "project": {"name": "test"}, "profiles": ["web"], "policy": {}},
        )
        self.write_json(
            ".agentic/profiles/core.json",
            {"id": "core", "description": "core", "requires": [], "resources": [], "conflicts": []},
        )
        self.write_json(
            ".agentic/profiles/web.json",
            {"id": "web", "description": "web", "requires": ["core"], "resources": [], "conflicts": []},
        )
        (self.root / "docs/40-execution/TASKS.jsonl").write_text(
            json.dumps(
                {
                    "id": "T-900",
                    "title": "Coordinate a persistent multi-agent runtime",
                    "goal": "Support bounded long-running sessions",
                    "owner": "orchestrator",
                    "files_owned": ["docs/30-engineering/ARCHITECTURE.md"],
                    "verification": ["kill-switch behavior"],
                }
            )
            + "\n"
        )
        (self.root / "CLAUDE.md").write_text("# test\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_json(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n")

    def manifest(
        self,
        capability_id: str,
        *,
        status: str = "optional",
        kind: str = "runtime",
        terms: list[str] | None = None,
        detect: list[dict] | None = None,
        adapter: str | None = None,
    ) -> dict:
        if adapter is None and status != "built_in":
            adapter = f"scripts/capability_adapters/{capability_id.replace('-', '_')}.py"
            adapter_path = self.root / adapter
            adapter_path.write_text("raise SystemExit('adapter must not execute during routing')\n")
        return {
            "schema_version": 1,
            "id": capability_id,
            "kind": kind,
            "display_name": capability_id.replace("-", " ").title(),
            "status": status,
            "summary": "Test capability contract.",
            "source": {
                "repository": "https://example.com/source",
                "reviewed_commit": SHA,
                "license": "MIT",
                "reviewed_at": "2026-08-10",
            },
            "recommend_when": {
                "profiles_any_of": ["core"] if status == "built_in" else [],
                "task_terms_any_of": terms or [],
                "task_owners_any_of": [],
                "file_patterns_any_of": [],
            },
            "authority": {
                "default": "none",
                "possible": ["local planning"],
                "forbidden": ["automatic installation", "production mutation"],
            },
            "setup": {
                "automatic": False,
                "mode": "plan_only",
                "adapter": adapter,
                "detect": detect or [{"type": "path", "value": f"vendor/{capability_id}"}],
            },
            "rollback": ["Remove the separately approved local integration."],
            "risks": ["External execution may inherit user permissions."],
        }

    def add_manifest(self, manifest: dict) -> None:
        self.write_json(f".agentic/capabilities/{manifest['id']}.json", manifest)

    def test_matching_missing_capability_is_explained_without_mutation(self) -> None:
        self.add_manifest(self.manifest("prime-runtime", terms=["long-running", "multi-agent"] ))
        report = capability_engine.build_report("T-900", self.root)
        decision = report["capabilities"][0]
        self.assertEqual("missing", decision["state"])
        self.assertFalse(decision["present"])
        self.assertIn("task evidence: long-running, multi-agent", decision["rationale"])
        self.assertFalse(report["mutation_performed"])
        self.assertFalse((self.root / "vendor/prime-runtime").exists())

    def test_present_matching_capability_is_recommended(self) -> None:
        (self.root / "vendor/prime-runtime").mkdir(parents=True)
        self.add_manifest(self.manifest("prime-runtime", terms=["long-running"]))
        decision = capability_engine.build_report("T-900", self.root)["capabilities"][0]
        self.assertEqual("recommended", decision["state"])
        self.assertTrue(decision["present"])

    def test_unmatched_capability_remains_optional_even_when_present(self) -> None:
        (self.root / "vendor/design-suite").mkdir(parents=True)
        self.add_manifest(self.manifest("design-suite", terms=["visual polish"]))
        decision = capability_engine.build_report("T-900", self.root)["capabilities"][0]
        self.assertEqual("optional", decision["state"])

    def test_blocked_contract_wins_over_matching_evidence(self) -> None:
        self.add_manifest(self.manifest("unsafe-runtime", status="blocked", terms=["long-running"]))
        decision = capability_engine.build_report("T-900", self.root)["capabilities"][0]
        self.assertEqual("blocked", decision["state"])

    def test_built_in_missing_is_doctor_failure(self) -> None:
        self.add_manifest(
            self.manifest(
                "core-harness",
                status="built_in",
                kind="built_in",
                detect=[{"type": "path", "value": "missing-core-file"}],
                adapter=None,
            )
        )
        stdout = io.StringIO()
        original = sys.stdout
        try:
            sys.stdout = stdout
            result = capability_engine.main(["doctor", "--json"], root=self.root)
        finally:
            sys.stdout = original
        self.assertEqual(1, result)
        decision = json.loads(stdout.getvalue())["capabilities"][0]
        self.assertEqual("missing", decision["state"])
        self.assertIn("Restore the committed repository files", decision["safe_next_action"])

    def test_manifest_fails_closed_on_automatic_setup(self) -> None:
        manifest = self.manifest("prime-runtime")
        manifest["setup"]["automatic"] = True
        self.add_manifest(manifest)
        with self.assertRaisesRegex(capability_engine.CapabilityError, "automatic must be false"):
            capability_engine.load_manifests(self.root)

    def test_router_never_executes_plan_adapter(self) -> None:
        sentinel = self.root / "adapter-executed"
        manifest = self.manifest("prime-runtime", terms=["long-running"])
        adapter = self.root / manifest["setup"]["adapter"]
        adapter.write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).touch()\n")
        self.add_manifest(manifest)
        capability_engine.build_report("T-900", self.root)
        self.assertFalse(sentinel.exists())

    def test_json_cli_output_declares_no_mutation(self) -> None:
        self.add_manifest(
            self.manifest(
                "core-harness",
                status="built_in",
                kind="built_in",
                detect=[{"type": "path", "value": "CLAUDE.md"}],
                adapter=None,
            )
        )
        stdout = io.StringIO()
        original = sys.stdout
        try:
            sys.stdout = stdout
            result = capability_engine.main(["list", "--json"], root=self.root)
        finally:
            sys.stdout = original
        self.assertEqual(0, result)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["mutation_performed"])
        self.assertEqual("built_in", payload["capabilities"][0]["state"])


if __name__ == "__main__":
    unittest.main()
