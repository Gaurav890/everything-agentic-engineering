from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import design_engine  # noqa: E402


class DesignEngineTests(unittest.TestCase):
    def test_catalog_has_three_dtcg_compatible_directions(self) -> None:
        catalog = design_engine.load_catalog()
        self.assertEqual(
            {"editorial-signal", "kinetic-index", "quiet-material"},
            set(catalog),
        )
        for direction in catalog.values():
            for token in direction["tokens"].values():
                self.assertIn("$type", token)
                self.assertIn("$value", token)

    def test_unapproved_state_emits_no_override(self) -> None:
        css = design_engine.render_direction_css(
            {
                "schema_version": 1,
                "status": "needs_approval",
                "approved_direction": None,
                "approved_by": None,
                "approved_at": None,
            }
        )
        self.assertIn("No direction approved", css)
        self.assertNotIn(":root", css)

    def test_approved_direction_compiles_semantic_overrides(self) -> None:
        css = design_engine.render_direction_css(
            {
                "schema_version": 1,
                "status": "approved",
                "approved_direction": "editorial-signal",
                "approved_by": "reviewer",
                "approved_at": "2026-08-19T00:00:00+00:00",
            }
        )
        self.assertIn("Approved direction: Editorial Signal", css)
        self.assertIn("--eae-color-background-canvas", css)
        self.assertIn("--eae-font-family-display", css)

    def test_invalid_approval_fails_closed(self) -> None:
        with self.assertRaises(design_engine.DesignError):
            design_engine.render_direction_css(
                {
                    "schema_version": 1,
                    "status": "approved",
                    "approved_direction": "missing",
                    "approved_by": "reviewer",
                    "approved_at": "2026-08-19T00:00:00+00:00",
                }
            )

    def test_noninteractive_intake_requires_every_answer(self) -> None:
        args = argparse.Namespace(
            answer=["product_type=portfolio"], non_interactive=True, yes=True
        )
        with self.assertRaisesRegex(design_engine.DesignError, "Missing non-interactive"):
            design_engine.run_intake(args)

    def test_first_run_captured_intake_is_a_valid_pre_approval_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "design.json"
            intake_path = root / "design-intake.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "status": "needs_approval",
                        "approved_direction": None,
                        "approved_by": None,
                        "approved_at": None,
                    }
                )
            )
            intake_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "status": "captured",
                        "answers": {
                            "product_type": "product",
                            "audience": "operators",
                            "personality": "precise",
                        },
                    }
                )
            )
            with (
                mock.patch.object(design_engine, "STATE_PATH", state_path),
                mock.patch.object(design_engine, "INTAKE_PATH", intake_path),
            ):
                self.assertEqual(0, design_engine.run_check(argparse.Namespace()))

    def test_approval_requires_confirmation_and_records_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state_path = Path(temporary) / "design.json"
            args = argparse.Namespace(
                direction="quiet-material", approved_by="Design owner", yes=False
            )
            with mock.patch.object(design_engine, "STATE_PATH", state_path):
                self.assertEqual(2, design_engine.run_approve(args))
                self.assertFalse(state_path.exists())
                args.yes = True
                self.assertEqual(0, design_engine.run_approve(args))
                state = json.loads(state_path.read_text())
            self.assertEqual("approved", state["status"])
            self.assertEqual("quiet-material", state["approved_direction"])
            self.assertEqual("Design owner", state["approved_by"])


if __name__ == "__main__":
    unittest.main()
