from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from scripts.runtime_doctor import RuntimePolicyError, load_manifest, parse_version


ROOT = Path(__file__).resolve().parents[1]
DOCTOR = ROOT / "scripts/runtime-doctor.sh"
MANIFEST = ROOT / ".agentic/runtime-baselines.json"


class RuntimeCompatibilityTests(unittest.TestCase):
    def run_doctor(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(DOCTOR), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_manifest_is_valid_and_optional_capabilities_are_human_gated(self) -> None:
        manifest = load_manifest(MANIFEST)
        self.assertEqual(set(manifest["runtimes"]), {"claude", "codex"})
        for policy in manifest["runtimes"].values():
            for capability in policy["capabilities"]:
                if not capability["default_enabled"]:
                    self.assertTrue(capability["human_approval_required"])

    def test_stable_release_meets_equal_baseline_but_prerelease_does_not(self) -> None:
        stable = parse_version("codex-cli 0.148.0")
        prerelease = parse_version("codex-cli 0.148.0-alpha.4")
        required = parse_version("0.148.0")
        assert stable and prerelease and required
        self.assertTrue(stable.meets(required))
        self.assertFalse(prerelease.meets(required))

    def test_advisory_mode_warns_but_passes_for_old_versions(self) -> None:
        result = self.run_doctor(
            "--claude-version",
            "2.1.220",
            "--codex-version",
            "codex-cli 0.146.0-alpha.3.1",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WARN", result.stdout)
        self.assertIn("read-only", result.stdout)

    def test_strict_mode_rejects_old_versions(self) -> None:
        result = self.run_doctor(
            "--strict",
            "--claude-version",
            "2.1.238",
            "--codex-version",
            "0.147.0",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL", result.stdout)

    def test_strict_mode_accepts_recommended_versions(self) -> None:
        result = self.run_doctor(
            "--strict",
            "--claude-version",
            "2.1.239",
            "--codex-version",
            "codex-cli 0.148.0",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Runtime compatibility PASS", result.stdout)

    def test_json_output_is_stable_and_declares_no_mutation(self) -> None:
        result = self.run_doctor(
            "--json",
            "--claude-version",
            "2.1.239",
            "--codex-version",
            "0.148.0",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertFalse(report["mutation_performed"])
        self.assertEqual([item["id"] for item in report["runtimes"]], ["claude", "codex"])

    def test_runtime_baselines_record_hardening_without_expanding_authority(self) -> None:
        manifest = load_manifest(MANIFEST)
        claude = manifest["runtimes"]["claude"]
        self.assertEqual(claude["recommended_minimum"], "2.1.239")
        self.assertTrue(claude["source"].endswith("/v2.1.239"))

        capabilities = {item["id"]: item for item in claude["capabilities"]}
        self.assertEqual(
            capabilities["subagent-fork-and-background-behavior"]["minimum"],
            "2.1.232",
        )
        self.assertEqual(
            capabilities["synced-skill-and-marketplace-boundary-hardening"]["minimum"],
            "2.1.228",
        )
        self.assertEqual(
            capabilities[
                "powershell-repository-trust-and-linux-sandbox-hardening"
            ]["minimum"],
            "2.1.232",
        )
        self.assertEqual(
            capabilities["windows-device-path-and-credential-leak-hardening"][
                "minimum"
            ],
            "2.1.233",
        )
        self.assertEqual(
            capabilities["skill-argument-template-hardening"]["minimum"],
            "2.1.233",
        )
        self.assertEqual(
            capabilities["mcp-v2-subscription-reliability"]["minimum"],
            "2.1.233",
        )
        identity_forwarding = capabilities["apps-gateway-user-identity-forwarding"]
        self.assertEqual(identity_forwarding["minimum"], "2.1.233")
        self.assertFalse(identity_forwarding["default_enabled"])
        self.assertTrue(identity_forwarding["human_approval_required"])
        self.assertEqual(
            capabilities["windows-preapproval-path-and-marketplace-origin-hardening"]["minimum"],
            "2.1.234",
        )
        self.assertEqual(
            capabilities["permission-preview-and-grant-hardening"]["minimum"],
            "2.1.235",
        )
        self.assertEqual(
            capabilities["macos-wildcard-deny-and-managed-approval-hardening"]["minimum"],
            "2.1.236",
        )
        self.assertEqual(
            capabilities["mcp-helper-trust-and-credential-isolation"]["minimum"],
            "2.1.238",
        )
        self.assertEqual(
            capabilities["organization-policy-replay-and-plan-resume-hardening"]["minimum"],
            "2.1.239",
        )
        headers_helper = capabilities["marketplace-and-mcp-headers-helper"]
        self.assertFalse(headers_helper["default_enabled"])
        self.assertTrue(headers_helper["human_approval_required"])

        codex = manifest["runtimes"]["codex"]
        self.assertEqual(codex["recommended_minimum"], "0.148.0")
        self.assertTrue(codex["source"].endswith("/rust-v0.148.0"))
        codex_capabilities = {item["id"]: item for item in codex["capabilities"]}
        self.assertEqual(
            codex_capabilities["resumed-policy-and-instruction-state-hardening"]["minimum"],
            "0.148.0",
        )
        self.assertTrue(
            codex_capabilities["cross-platform-fail-closed-filesystem-sandbox"]["default_enabled"]
        )
        self.assertTrue(
            codex_capabilities["mcp-oauth-reauthentication-recovery"]["default_enabled"]
        )
        mcp_hooks = codex_capabilities["asynchronous-and-mcp-invoking-hooks"]
        self.assertFalse(mcp_hooks["default_enabled"])
        self.assertTrue(mcp_hooks["human_approval_required"])
        compatibility = (ROOT / "docs/60-tooling/COMPATIBILITY.md").read_text()
        self.assertIn("reverts", compatibility)
        self.assertIn("Bash input redirection", compatibility)
        self.assertIn("MCP `headersHelper`", compatibility)
        self.assertIn("makes the sandbox fail", compatibility)
        self.assertIn("closed for denied or unreadable paths", compatibility)
        self.assertFalse(capabilities["cross-session-messaging"]["default_enabled"])
        self.assertTrue(
            capabilities["cross-session-messaging"]["human_approval_required"]
        )
        for capability in capabilities.values():
            if capability["human_approval_required"]:
                self.assertFalse(capability["default_enabled"])

    def test_invalid_optional_capability_fails_closed(self) -> None:
        fixture = ROOT / ".cache/runtime-policy-invalid.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        policy = json.loads(MANIFEST.read_text())
        policy["runtimes"]["codex"]["capabilities"][0][
            "human_approval_required"
        ] = False
        fixture.write_text(json.dumps(policy))
        try:
            with self.assertRaises(RuntimePolicyError):
                load_manifest(fixture)
        finally:
            fixture.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
