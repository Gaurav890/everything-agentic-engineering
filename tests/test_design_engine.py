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
sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_fixture import prepare, write


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
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = prepare(root)
            with mock.patch.object(design_engine, "ROOT", root):
                css = design_engine.render_direction_css(state)
        self.assertIn("Approved direction: editorial-signal", css)
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
            root = Path(temporary)
            prepare(root)
            state_path = Path(temporary) / "design.json"
            args = argparse.Namespace(
                direction="quiet-material", approved_by="Design owner", yes=False,
                evidence=["docs/50-evals/fixture.png"],
            )
            with mock.patch.object(design_engine, "STATE_PATH", state_path), mock.patch.object(design_engine, "ROOT", root):
                self.assertEqual(2, design_engine.run_approve(args))
                self.assertFalse(state_path.exists())
                args.yes = True
                self.assertEqual(0, design_engine.run_approve(args))
                state = json.loads(state_path.read_text())
            self.assertEqual("approved", state["status"])
            self.assertEqual("quiet-material", state["approved_direction"])
            self.assertEqual("Design owner", state["approved_by"])

    def test_custom_catalog_can_be_empty_or_have_more_than_three_directions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prepare(root, approved=False)
            path = root / ".agentic/design-directions.json"
            write(root, str(path.relative_to(root)), {"schema_version": 2, "mode": "custom", "directions": []})
            self.assertEqual({}, design_engine.load_catalog(path))
            source = root / "apps/web/app/concepts/page.tsx"
            source.parent.mkdir(parents=True)
            source.write_text("export default function Preview() { return null; }")
            candidate = dict(design_engine.load_catalog()["quiet-material"])
            candidate.update(composition="Timeline", interaction="Compare two purchase dates", rationale="Expose tradeoffs", preview_path="/concepts", source_files=["apps/web/app/concepts/page.tsx"])
            candidates = [{**candidate, "id": f"purchase-path-{n}"} for n in range(4)]
            write(root, str(path.relative_to(root)), {"schema_version": 2, "mode": "custom", "directions": candidates})
            self.assertEqual(4, len(design_engine.load_catalog(path)))
            args = argparse.Namespace(file="candidate.json", yes=True)
            write(root, args.file, {**candidate, "id": "fifth-option"})
            with mock.patch.object(design_engine, "ROOT", root), mock.patch.object(design_engine, "CATALOG_PATH", path):
                self.assertEqual(0, design_engine.run_propose(args))
            self.assertEqual(5, len(design_engine.load_catalog(path)))

    def test_approval_is_invalidated_by_evidence_intake_and_candidate_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for change in ("evidence", "intake", "candidate"):
                state = prepare(root)
                catalog = design_engine.load_catalog(root / ".agentic/design-directions.json")
                if change == "evidence":
                    (root / "docs/50-evals/fixture.png").write_bytes(b"changed")
                elif change == "intake":
                    intake = json.loads((root / ".agentic/design-intake.json").read_text())
                    intake["answers"]["color_intent"] = "warm"
                    write(root, ".agentic/design-intake.json", intake)
                else:
                    catalog[state["approved_direction"]]["thesis"] += " revised"
                with self.assertRaisesRegex(design_engine.DesignError, "stale"):
                    design_engine.validate_state(state, catalog, root)

    def test_custom_candidates_cannot_bypass_local_source_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = dict(design_engine.load_catalog()["quiet-material"])
            path = root / ".agentic/design-directions.json"
            for preview in ("https://example.com", "/../escape", "/preview"):
                candidate["preview_path"] = preview
                write(root, ".agentic/design-directions.json", {"schema_version": 2, "mode": "custom", "directions": [candidate]})
                with self.assertRaises(design_engine.DesignError):
                    design_engine.load_catalog(path)

    def test_approval_output_cannot_be_its_own_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "packages/design-tokens/generated/direction.css"
            output.parent.mkdir(parents=True)
            output.write_text("/* No direction approved. */")
            for relative in ("packages/design-tokens/generated/direction.css",
                             "packages/design-tokens/generated/./direction.css"):
                with self.subTest(relative=relative), self.assertRaisesRegex(design_engine.DesignError, "approval output"):
                    design_engine.candidate_source(root, relative)

    def test_unsafe_token_values_and_output_symlinks_are_rejected(self):
        for token in ({"$type": "fontFamily", "$value": ["x; url(remote)"]},
                      {"$type": "duration", "$value": {"value": float("nan"), "unit": "ms"}},
                      {"$type": "color", "$value": {"colorSpace": "srgb", "components": [1, 0, 9]}}):
            with self.assertRaises(design_engine.DesignError):
                design_engine.token_to_css(token)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "state.json"
            outside = Path(temporary) / "safe.json"
            outside.write_text("preserve")
            path.symlink_to(outside)
            with self.assertRaises(design_engine.DesignError):
                design_engine.save_object(path, {"status": "approved"})
            self.assertEqual("preserve", outside.read_text())


if __name__ == "__main__":
    unittest.main()
