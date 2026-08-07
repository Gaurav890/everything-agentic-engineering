from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SecurityHookTests(unittest.TestCase):
    def call_hook(self, hook: str, payload: dict) -> str:
        result = subprocess.run(
            [str(ROOT / ".claude/hooks" / hook)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout

    def test_destructive_command_is_denied(self) -> None:
        output = self.call_hook(
            "pre-tool-security.sh",
            {"tool_name": "Bash", "tool_input": {"command": "git reset --hard HEAD~1"}},
        )
        decision = json.loads(output)
        self.assertEqual(
            decision["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_safe_command_is_not_denied(self) -> None:
        output = self.call_hook(
            "pre-tool-security.sh",
            {"tool_name": "Bash", "tool_input": {"command": "git status --short"}},
        )
        self.assertEqual(output, "")

    def test_secret_scanner_warns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.txt"
            path.write_text('api_key = "this-is-not-a-real-key-but-is-long"')
            output = self.call_hook(
                "post-edit-secret-scan.sh",
                {"tool_input": {"file_path": str(path)}},
            )
        warning = json.loads(output)
        self.assertIn("Potential hard-coded secret", warning["systemMessage"])

    def test_secret_scanner_supports_codex_apply_patch_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "codex-example.txt"
            path.write_text('token = "this-is-not-a-real-token-but-is-long"')
            output = self.call_hook(
                "post-edit-secret-scan.sh",
                {
                    "cwd": directory,
                    "tool_name": "apply_patch",
                    "tool_input": {
                        "command": "*** Begin Patch\n*** Update File: codex-example.txt\n*** End Patch"
                    },
                },
            )
        warning = json.loads(output)
        self.assertIn("codex-example.txt", warning["systemMessage"])


if __name__ == "__main__":
    unittest.main()
