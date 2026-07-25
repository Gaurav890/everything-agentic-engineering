from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/init_project.py"


class InitializerTests(unittest.TestCase):
    def run_init(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_resolves_web_design_and_research(self) -> None:
        result = self.run_init(
            "--name",
            "example",
            "--web",
            "--design",
            "--research",
            "--dry-run",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"web-next"', result.stdout)
        self.assertIn('"design-critical"', result.stdout)
        self.assertIn('"research-enabled"', result.stdout)
        self.assertIn("no files changed", result.stdout.lower())

    def test_agentic_product_activates_design_contract(self) -> None:
        result = self.run_init("--name", "agent", "--agentic", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"design-critical"', result.stdout)

    def test_invalid_backend_fails(self) -> None:
        result = self.run_init("--name", "bad", "--backend", "both", "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("backend must be", result.stderr)

    def test_write_requires_confirmation(self) -> None:
        result = self.run_init("--name", "example", "--web")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--yes", result.stdout)


if __name__ == "__main__":
    unittest.main()
