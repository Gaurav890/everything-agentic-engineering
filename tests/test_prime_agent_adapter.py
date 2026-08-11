#!/usr/bin/env python3
"""Tests for the disabled-by-default Prime Agent planning adapter."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts/capability_adapters/prime_agent.py"
MANIFEST = ROOT / ".agentic/capabilities/prime-agent.json"
PIN = "71ca6cfd1a2f7205ca0ec1baa65d10d0ed88f6e8"


def run_adapter(*args: str, env: dict[str, str] | None = None) -> dict:
    completed = subprocess.run([sys.executable, str(ADAPTER), *args], cwd=ROOT, text=True, capture_output=True, check=True, env=env)
    return json.loads(completed.stdout)


class PrimeAgentAdapterTests(unittest.TestCase):
    def test_manifest_matches_optional_plan_only_contract(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(set(manifest), {"schema_version", "id", "kind", "display_name", "status", "summary", "source", "recommend_when", "authority", "setup", "rollback", "risks"})
        self.assertEqual(set(manifest["recommend_when"]), {"profiles_any_of", "task_terms_any_of", "task_owners_any_of", "file_patterns_any_of"})
        self.assertEqual(manifest["source"]["reviewed_commit"], PIN)
        self.assertEqual(manifest["source"]["license"], "MIT")
        self.assertEqual(manifest["status"], "optional")
        self.assertEqual(manifest["recommend_when"]["profiles_any_of"], [])
        self.assertEqual(manifest["recommend_when"]["task_owners_any_of"], [])
        self.assertEqual(manifest["authority"]["default"], "none")
        self.assertFalse(manifest["setup"]["automatic"])
        self.assertEqual(manifest["setup"]["mode"], "plan_only")
        self.assertEqual(manifest["setup"]["detect"], [{"type": "command", "value": "prime-agent"}])

    def test_doctor_does_not_execute_detected_binary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            marker = temporary / "executed"
            binary = temporary / "prime-agent"
            binary.write_text("#!/bin/sh\nprintf executed > \"$PRIME_AGENT_TEST_MARKER\"\n")
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
            env = os.environ.copy()
            env["PATH"] = str(temporary)
            env["PRIME_AGENT_TEST_MARKER"] = str(marker)
            report = run_adapter("doctor", "--json", env=env)
            self.assertTrue(report["binary_detected"])
            self.assertFalse(report["binary_executed"])
            self.assertFalse(report["version_probe_performed"])
            self.assertFalse(report["mutation_performed"])
            self.assertFalse(marker.exists())

    def test_missing_doctor_is_read_only(self) -> None:
        env = os.environ.copy()
        env["PATH"] = ""
        report = run_adapter("doctor", "--json", env=env)
        self.assertEqual(report["status"], "not_detected")
        self.assertFalse(report["binary_detected"])
        self.assertFalse(report["mutation_performed"])

    def test_plan_is_bounded_inert_and_human_gated(self) -> None:
        report = run_adapter("plan", "--json")
        self.assertEqual(report["mode"], "plan_only")
        self.assertFalse(report["automatic"])
        self.assertFalse(report["security_boundary"]["is_security_sandbox"])
        self.assertEqual(report["source"]["reviewed_commit"], PIN)
        self.assertEqual(report["commands"], [])
        self.assertFalse(report["mutation_performed"])
        self.assertLessEqual(report["budgets"]["max_session_minutes"], 60)
        self.assertLessEqual(report["budgets"]["max_parallel_subagents"], 3)
        self.assertLessEqual(report["budgets"]["max_scheduled_runs_without_review"], 1)
        self.assertFalse(report["kill_switch"]["automatic_destructive_cleanup"])
        self.assertTrue(report["rollback"])
        self.assertTrue(all(not item["execute"] for item in report["instructions"]))
        forbidden = {"download", "installation", "login", "schedule creation", "provider or model configuration", "credential access or modification", "MCP registration", "network or sandbox change", "production or deployment change", "approval or merge"}
        self.assertTrue(forbidden.issubset(set(report["explicitly_not_performed"])))


if __name__ == "__main__":
    unittest.main()
