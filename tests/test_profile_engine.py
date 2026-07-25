from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import profile_engine


class ProfileEngineTests(unittest.TestCase):
    def test_dependencies_are_expanded_once(self) -> None:
        result = profile_engine.resolve(["web-next", "design-critical"])
        self.assertEqual(result["resolved_profiles"][0], "core")
        self.assertEqual(result["resolved_profiles"].count("core"), 1)
        self.assertIn("playwright-mcp", result["required_resources"])

    def test_shared_resource_has_multiple_owners(self) -> None:
        result = profile_engine.resolve(["web-next", "design-critical", "research-enabled"])
        self.assertEqual(
            result["resource_owners"]["playwright-mcp"],
            ["web-next", "design-critical", "research-enabled"],
        )

    def test_conflicting_backends_are_reported(self) -> None:
        result = profile_engine.resolve(["backend-supabase", "backend-convex"])
        self.assertEqual(result["conflicts"], ["backend-convex ↔ backend-supabase"])

    def test_unknown_profile_fails_closed(self) -> None:
        with self.assertRaisesRegex(profile_engine.ProfileError, "Unknown profile"):
            profile_engine.resolve(["does-not-exist"])

    def test_empty_profile_list_is_rejected(self) -> None:
        with self.assertRaisesRegex(profile_engine.ProfileError, "At least one"):
            profile_engine.parse_profile_list(" , ")


if __name__ == "__main__":
    unittest.main()
