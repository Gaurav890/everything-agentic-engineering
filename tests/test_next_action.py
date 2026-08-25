from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import next_action  # noqa: E402


class NextActionTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def test_source_checkout_routes_to_guided_create(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(
                ("Create your first project", "./agentic setup create"),
                next_action.next_action(Path(temporary)),
            )

    def test_web_project_reveals_one_step_at_a_time(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_json(
                root / ".agentic/generated-project.json",
                {"resolved_profiles": ["web-next", "design-critical"]},
            )
            self.assertEqual("pnpm install", next_action.next_action(root)[1])

            (root / "node_modules").mkdir()
            self.assertEqual("pnpm install", next_action.next_action(root)[1])
            (root / "node_modules/.pnpm").mkdir()
            (root / "node_modules/.modules.yaml").write_text("layoutVersion: 5\n")
            self.write_json(root / ".agentic/design.json", {"status": "needs_approval"})
            self.assertEqual("pnpm dev", next_action.next_action(root)[1])

            self.write_json(
                root / ".agentic/design.json",
                {"status": "approved", "approved_direction": "editorial-signal"},
            )
            self.assertEqual("./agentic tokens build", next_action.next_action(root)[1])

            (root / "packages/design-tokens/generated").mkdir(parents=True)
            (root / "packages/design-tokens/generated/direction.css").write_text(
                "/* Approved direction: Kinetic Index (kinetic-index). */\n"
            )
            self.assertEqual("./agentic tokens build", next_action.next_action(root)[1])
            (root / "packages/design-tokens/generated/direction.css").write_text(
                "/* Approved direction: Editorial Signal (editorial-signal). */\n"
            )
            self.assertEqual("./agentic verify full", next_action.next_action(root)[1])

    def test_malformed_profile_metadata_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for value in (None, "web-next", {"web-next": True}, ["web-next", 7]):
                self.write_json(
                    root / ".agentic/generated-project.json",
                    {"resolved_profiles": value},
                )
                with self.assertRaisesRegex(
                    next_action.NextActionError,
                    "resolved_profiles must be a string array",
                ):
                    next_action.next_action(root)

    def test_mobile_project_does_not_route_web_setup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_json(
                root / ".agentic/generated-project.json",
                {"resolved_profiles": ["mobile-expo", "design-critical"]},
            )
            title, action = next_action.next_action(root)
            self.assertIn("mobile", title.lower())
            self.assertEqual("Open docs/00-vision/NORTH_STAR.md", action)


if __name__ == "__main__":
    unittest.main()
