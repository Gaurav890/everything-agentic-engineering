from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
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
    def prepare_resource_root(
        self,
        root: Path,
        *,
        approved: bool = False,
        profiles: list[str] | None = None,
    ) -> None:
        prepare(root, approved=approved)
        write(root, ".agentic/project.json", {
            "schema_version": 1,
            "project": {"name": "resource-test"},
            "profiles": profiles or ["web-next", "design-critical"],
            "specialists": [],
            "policy": {"allow_automatic_install": False, "allow_automatic_removal": False},
        })
        write(
            root,
            ".agentic/design-resources.json",
            json.loads(design_engine.RESOURCES_PATH.read_text()),
        )
        write(
            root,
            ".agentic/design-assets.json",
            {"schema_version": 1, "assets": []},
        )

    def test_design_resource_catalog_has_reviewed_bounded_routes(self) -> None:
        resources = design_engine.load_resource_catalog()
        self.assertEqual(
            {"realtime-colors", "haikei", "motion-primitives"},
            {item["id"] for item in resources},
        )
        motion = next(item for item in resources if item["id"] == "motion-primitives")
        self.assertEqual(["web"], motion["platforms"])
        self.assertIn("beta", motion["source"]["maintenance"].lower())
        for resource in resources:
            self.assertTrue(resource["source"]["canonical_url"].startswith("https://"))
            self.assertTrue(resource["forbidden"])

    def test_resource_plan_routes_open_palette_and_type_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root)
            intake = json.loads((root / ".agentic/design-intake.json").read_text())
            intake.update(status="not_started")
            intake["answers"]["color_intent"] = None
            intake["answers"]["typography"] = None
            write(root, ".agentic/design-intake.json", intake)
            report = design_engine.design_resource_plan(root)
        decisions = {item["id"]: item for item in report["decisions"]}
        self.assertEqual("recommended", decisions["realtime-colors"]["state"])
        self.assertEqual("optional", decisions["haikei"]["state"])
        self.assertEqual("optional", decisions["motion-primitives"]["state"])
        self.assertFalse(report["mutation_performed"])
        self.assertFalse(report["browser_opened"])
        self.assertFalse(report["download_performed"])
        self.assertFalse(report["installation_performed"])

    def test_resource_plan_requires_candidate_evidence_for_assets_and_approval_for_motion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root)
            without_evidence = design_engine.design_resource_plan(
                root,
                phase="design-directions",
                needs=["assets", "motion"],
            )
            catalog = json.loads((root / ".agentic/design-directions.json").read_text())
            catalog["directions"][0].update(
                asset_strategy="A generated geometric SVG derived from approved candidate colors",
                asset_role="Visualize the relationship between evidence and a human decision",
                asset_alternatives="Considered CSS geometry and a data chart; neither carries the narrative role",
            )
            write(root, ".agentic/design-directions.json", catalog)
            with_evidence = design_engine.design_resource_plan(
                root,
                phase="design-directions",
                needs=["assets", "motion"],
            )
        without = {item["id"]: item for item in without_evidence["decisions"]}
        with_contract = {item["id"]: item for item in with_evidence["decisions"]}
        self.assertEqual("deferred", without["haikei"]["state"])
        self.assertEqual("recommended", with_contract["haikei"]["state"])
        self.assertEqual("deferred", with_contract["motion-primitives"]["state"])

    def test_resource_plan_makes_no_recommendation_without_a_current_need(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root)
            report = design_engine.design_resource_plan(root)
        self.assertEqual([], report["context"]["needs"])
        self.assertFalse(any(
            item["state"] == "recommended" for item in report["decisions"]
        ))

    def test_resource_plan_allows_approved_web_motion_and_rejects_mobile_route(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root, approved=True)
            catalog = json.loads((root / ".agentic/design-directions.json").read_text())
            catalog["directions"][0].update(
                motion_rationale="The transition preserves object continuity after selection.",
                motion_interruption="A new selection reverses the transition immediately without queuing.",
                motion_performance_budget="Transform and opacity only, completing within 180ms.",
                reduced_motion="Update the selected state instantly with the same persistent label.",
            )
            write(root, ".agentic/design-directions.json", catalog)
            state = json.loads((root / ".agentic/design.json").read_text())
            state["fingerprint"] = design_engine.approval_fingerprint(
                root,
                catalog["directions"][0],
                state["evidence"],
            )
            write(root, ".agentic/design.json", state)
            web = design_engine.design_resource_plan(root, needs=["motion"])
            project = json.loads((root / ".agentic/project.json").read_text())
            project["profiles"] = ["mobile-expo", "design-critical"]
            write(root, ".agentic/project.json", project)
            mobile = design_engine.design_resource_plan(root, needs=["motion"])
        web_decision = next(item for item in web["decisions"] if item["id"] == "motion-primitives")
        mobile_decision = next(item for item in mobile["decisions"] if item["id"] == "motion-primitives")
        self.assertEqual("recommended", web_decision["state"])
        self.assertEqual("not_applicable", mobile_decision["state"])

    def test_resource_catalog_rejects_weakened_automatic_install_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = json.loads(design_engine.RESOURCES_PATH.read_text())
            payload["policy"]["automatic_install"] = True
            path = root / "design-resources.json"
            write(root, "design-resources.json", payload)
            with self.assertRaisesRegex(design_engine.DesignError, "safety boundary"):
                design_engine.load_resource_catalog(path)

    def test_resource_catalog_rejects_unknown_policy_and_terminal_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = json.loads(design_engine.RESOURCES_PATH.read_text())
            payload["policy"]["automatic_network_override"] = True
            write(root, "unknown.json", payload)
            with self.assertRaisesRegex(design_engine.DesignError, "safety boundary"):
                design_engine.load_resource_catalog(root / "unknown.json")
            payload = json.loads(design_engine.RESOURCES_PATH.read_text())
            payload["resources"][0]["name"] = "Palette\u001b]8;;https://evil.invalid\u0007spoof"
            write(root, "control.json", payload)
            with self.assertRaisesRegex(design_engine.DesignError, "terminal control"):
                design_engine.load_resource_catalog(root / "control.json")

    def test_human_resource_output_places_safety_and_return_contract_before_url(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root)
            intake = json.loads((root / ".agentic/design-intake.json").read_text())
            intake["answers"]["color_intent"] = "open"
            write(root, ".agentic/design-intake.json", intake)
            args = argparse.Namespace(phase="design-intake", need=["palette"], all=False, json=False)
            with mock.patch.object(design_engine, "ROOT", root), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(0, design_engine.run_resources(args))
            rendered = output.getvalue()
        self.assertIn("Use only non-confidential inputs", rendered)
        self.assertIn("License/use boundary", rendered)
        self.assertIn("Return to:", rendered)
        self.assertLess(rendered.index("Before external use:"), rendered.index("Open manually after"))

    def test_design_asset_catalog_validates_a_complete_haikei_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root)
            asset = root / "apps/web/public/decision-field.svg"
            asset.parent.mkdir(parents=True)
            asset.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1600 900\"></svg>")
            evidence = root / "docs/50-evals/fixture.png"
            record = {
                "id": "decision-field",
                "source_id": "haikei",
                "source_url": "https://haikei.app/generators/",
                "source_revision": None,
                "created_at": "2026-09-13",
                "generator": "layered-waves",
                "parameters": {"waves": 4, "direction": "up"},
                "file": "apps/web/public/decision-field.svg",
                "dimensions": {"width": 1600, "height": 900, "unit": "px"},
                "file_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
                "token_roles": ["color.background.canvas", "color.action.primary.default"],
                "placement": "Behind the evidence-to-decision transition only",
                "responsive_behavior": "Crop the quiet edge while preserving the decision focal point",
                "dark_mode_behavior": "Use the approved dark semantic roles",
                "semantics": "decorative",
                "alt_text": None,
                "license_basis": "Generated under the reviewed Haikei professional-use terms",
                "evidence": [{
                    "file": "docs/50-evals/fixture.png",
                    "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                }],
            }
            write(root, ".agentic/design-assets.json", {"schema_version": 1, "assets": [record]})
            self.assertEqual([record], design_engine.load_asset_catalog(root))

            invalid_cases = {
                "missing-dimensions": lambda item: item.pop("dimensions"),
                "unknown-token": lambda item: item.update(token_roles=["color.fake.role"]),
                "stale-file": lambda item: item.update(file_sha256="0" * 64),
                "stale-evidence": lambda item: item.update(evidence=[{
                    "file": "docs/50-evals/fixture.png", "sha256": "0" * 64,
                }]),
            }
            for label, mutate in invalid_cases.items():
                with self.subTest(label=label):
                    changed = json.loads(json.dumps(record))
                    mutate(changed)
                    write(root, ".agentic/design-assets.json", {"schema_version": 1, "assets": [changed]})
                    with self.assertRaises(design_engine.DesignError):
                        design_engine.load_asset_catalog(root)

    def test_svg_dimensions_use_distinct_width_and_height_without_viewbox(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "asset.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"></svg>')
            self.assertEqual((1600, 900), design_engine._asset_dimensions(path))

    def test_motion_route_defers_when_interruption_or_performance_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root, approved=True)
            for missing in ("motion_interruption", "motion_performance_budget"):
                catalog = json.loads((root / ".agentic/design-directions.json").read_text())
                catalog["directions"][0].update(
                    motion_rationale="The transition preserves object continuity after selection.",
                    motion_interruption="A new selection reverses immediately.",
                    motion_performance_budget="Transform and opacity only within 180ms.",
                    reduced_motion="Update the selected state instantly.",
                )
                catalog["directions"][0].pop(missing)
                write(root, ".agentic/design-directions.json", catalog)
                state = json.loads((root / ".agentic/design.json").read_text())
                state["fingerprint"] = design_engine.approval_fingerprint(
                    root, catalog["directions"][0], state["evidence"]
                )
                write(root, ".agentic/design.json", state)
                decision = next(item for item in design_engine.design_resource_plan(
                    root, needs=["motion"]
                )["decisions"] if item["id"] == "motion-primitives")
                self.assertEqual("deferred", decision["state"], missing)

    def test_resource_routes_reject_placeholder_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare_resource_root(root, approved=True)
            catalog = json.loads((root / ".agentic/design-directions.json").read_text())
            direction = catalog["directions"][0]
            direction.update(
                asset_strategy="Generated SVG background for the decision surface",
                asset_role="n/a",
                asset_alternatives="placeholder",
                motion="Crossfade the selected consequence",
                motion_rationale="TBD",
                motion_interruption="none",
                motion_performance_budget="n/a",
                reduced_motion="later",
            )
            write(root, ".agentic/design-directions.json", catalog)
            state = json.loads((root / ".agentic/design.json").read_text())
            state["fingerprint"] = design_engine.approval_fingerprint(root, direction, state["evidence"])
            write(root, ".agentic/design.json", state)
            decisions = {item["id"]: item for item in design_engine.design_resource_plan(
                root, needs=["assets", "motion"]
            )["decisions"]}
            self.assertEqual("deferred", decisions["haikei"]["state"])
            self.assertEqual("deferred", decisions["motion-primitives"]["state"])

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
            candidate.update(
                composition="Timeline", interaction="Compare two purchase dates",
                rationale="Expose tradeoffs", axis="temporal comparison",
                signature="A budget horizon that bends around the selected purchase date",
                asset_strategy="Purpose-built data visualization; no stock imagery",
                asset_role="Make the timing consequence visible as the primary product graphic",
                asset_alternatives="Considered stock imagery and a plain table; both hide the timing relationship",
                motion_rationale="The horizon transition explains the changed date and affordability",
                motion_interruption="A new date reverses the active transition without queuing",
                motion_performance_budget="Transform and opacity only within 180ms",
                responsive_strategy="The horizon becomes a vertically stepped plan on narrow screens",
                reduced_motion="The selected horizon updates instantly with persistent labels",
                states=["ready", "over budget", "safe plan"], preview_path="/concepts",
                preview_source="apps/web/app/concepts/page.tsx",
                source_files=["apps/web/app/concepts/page.tsx"],
            )
            candidates = [{**candidate, "id": f"purchase-path-{n}", "axis": f"design axis {n}"} for n in range(4)]
            write(root, str(path.relative_to(root)), {"schema_version": 2, "mode": "custom", "directions": candidates})
            self.assertEqual(4, len(design_engine.load_catalog(path)))
            args = argparse.Namespace(file="candidate.json", yes=True)
            write(root, args.file, {**candidate, "id": "fifth-option", "axis": "decision confidence"})
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

    def test_custom_candidates_require_distinct_axes_and_cannot_reuse_demo_surface(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "apps/web/app/concepts/page.tsx"
            source.parent.mkdir(parents=True)
            source.write_text("export default function Preview() { return null; }")
            base = dict(design_engine.load_catalog()["quiet-material"])
            base.update(
                composition="A decision horizon", interaction="Select a date",
                rationale="Make the tradeoff visible", axis="time horizon",
                signature="A horizon that bends around the target",
                asset_strategy="Product-owned data visualization",
                asset_role="Make the target-date consequence visible",
                asset_alternatives="Considered a plain table and stock imagery; neither communicates the change",
                motion_rationale="Motion links the changed input to its consequence",
                motion_interruption="A new selection reverses the transition without queuing",
                motion_performance_budget="Transform and opacity only within 180ms",
                responsive_strategy="The horizon stacks on narrow screens",
                reduced_motion="Values update without interpolation",
                states=["ready", "unsafe", "safe"], preview_path="/concepts",
                preview_source="apps/web/app/concepts/page.tsx",
                source_files=["apps/web/app/concepts/page.tsx"],
            )
            path = root / ".agentic/design-directions.json"
            write(root, str(path.relative_to(root)), {
                "schema_version": 2, "mode": "custom",
                "directions": [{**base, "id": "one"}, {**base, "id": "two"}],
            })
            with self.assertRaisesRegex(design_engine.DesignError, "distinct named axes"):
                design_engine.load_catalog(path)
            demo = root / "apps/web/app/product-lab.tsx"
            demo.write_text("export default function Demo() { return null; }")
            base.update(preview_source="apps/web/app/product-lab.tsx", source_files=["apps/web/app/product-lab.tsx"])
            with self.assertRaisesRegex(design_engine.DesignError, "starter demo"):
                design_engine.validate_custom_candidate(base, root)

    def test_approval_output_cannot_be_its_own_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "packages/design-tokens/generated/direction.css"
            output.parent.mkdir(parents=True)
            output.write_text("/* No direction approved. */")
            alias = output.with_name("approval-copy.css")
            os.link(output, alias)
            sources = ["packages/design-tokens/generated/direction.css",
                       "packages/design-tokens/generated/./direction.css",
                       str(alias.relative_to(root))]
            case_alias = output.with_name("Direction.css")
            if case_alias.is_file():
                sources.append(str(case_alias.relative_to(root)))
            for relative in sources:
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
