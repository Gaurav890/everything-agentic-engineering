from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import project_generator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/project_generator.py"


class ProjectGeneratorTests(unittest.TestCase):
    def run_generator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_is_non_mutating_and_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "planned-project"
            result = self.run_generator(
                "--name",
                "Planned Project",
                "--destination",
                str(destination),
                "--preset",
                "web-supabase",
                "--dry-run",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(destination.exists())
            report = json.loads(result.stdout)
            self.assertEqual("create_downstream_project", report["operation"])
            self.assertIn("apps/web", report["copy"]["included_managed_paths"])
            self.assertIn("apps/mobile", report["copy"]["excluded_managed_paths"])
            self.assertFalse(report["safety"]["source_mutation"])
            self.assertFalse(report["safety"]["enables_mcp_servers"])

    def test_web_project_is_materialized_and_verifies_offline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "example-web"
            result = self.run_generator(
                "--name",
                "Example Web",
                "--destination",
                str(destination),
                "--preset",
                "web",
                "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((destination / "apps/web").is_dir())
            self.assertFalse((destination / "apps/mobile").exists())
            self.assertFalse((destination / "apps/showcase").exists())
            self.assertTrue((destination / "packages/design-tokens").is_dir())
            self.assertTrue((destination / "apps/web/package.json").is_file())
            self.assertTrue((destination / "apps/web/app/portfolio-lab.tsx").is_file())
            self.assertTrue((destination / ".github/workflows/web-quality.yml").is_file())
            self.assertFalse((destination / ".git").exists())
            self.assertFalse((destination / "docs/50-evals/evidence").exists())
            self.assertEqual(
                {"mcpServers": {}},
                json.loads((destination / ".mcp.json").read_text()),
            )
            manifest = json.loads((destination / ".agentic/project.json").read_text())
            self.assertEqual("Example Web", manifest["project"]["name"])
            self.assertEqual(["web-next", "design-critical"], manifest["profiles"])
            package = json.loads((destination / "package.json").read_text())
            self.assertEqual(
                "pnpm --filter @everything-agentic/web dev",
                package["scripts"]["dev"],
            )
            self.assertEqual(
                "pnpm --dir apps/web build && pnpm --dir apps/web test:visual",
                package["scripts"]["test:visual"],
            )
            design = json.loads((destination / ".agentic/design.json").read_text())
            self.assertEqual("needs_approval", design["status"])
            self.assertIsNone(design["approved_direction"])
            intake = json.loads((destination / ".agentic/design-intake.json").read_text())
            self.assertEqual("not_started", intake["status"])
            self.assertEqual("", (destination / "docs/40-execution/TASKS.jsonl").read_text())
            verification = subprocess.run(
                [str(destination / "agentic"), "verify", "full"],
                cwd=destination,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(verification.returncode, 0, verification.stderr)
            self.assertIn("Generated project verification complete", verification.stdout)

    def test_mobile_project_excludes_web_and_showcase(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "mobile-product"
            result = self.run_generator(
                "--name",
                "Mobile Product",
                "--destination",
                str(destination),
                "--preset",
                "mobile",
                "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((destination / "apps/mobile").is_dir())
            self.assertFalse((destination / "apps/web").exists())
            self.assertFalse((destination / "apps/showcase").exists())
            self.assertFalse((destination / ".github/workflows/web-quality.yml").exists())
            self.assertTrue((destination / ".claude/agents/mobile.md").is_file())
            self.assertFalse((destination / ".claude/agents/frontend.md").exists())

    def test_core_project_excludes_optional_surfaces_and_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "core-project"
            result = self.run_generator(
                "--name",
                "Core Project",
                "--destination",
                str(destination),
                "--preset",
                "core",
                "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((destination / "apps").exists())
            self.assertFalse((destination / ".github/workflows/web-quality.yml").exists())
            self.assertFalse((destination / "packages/design-tokens").exists())
            self.assertFalse((destination / ".agentic/design.json").exists())
            self.assertFalse((destination / ".agentic/design-intake.json").exists())
            self.assertFalse((destination / ".agentic/design-directions.json").exists())
            self.assertTrue((destination / ".agentic/evolution/policy.json").is_file())
            self.assertTrue((destination / ".agentic/evolution/incumbent.json").is_file())
            evolution = subprocess.run(
                [str(destination / "agentic"), "evolve", "validate", "--json"],
                cwd=destination,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, evolution.returncode, evolution.stderr)
            self.assertFalse(json.loads(evolution.stdout)["mutation_performed"])
            self.assertFalse((destination / ".claude/agents/frontend.md").exists())
            self.assertFalse((destination / ".claude/agents/mobile.md").exists())
            self.assertFalse((destination / ".claude/agents/backend.md").exists())
            self.assertFalse((destination / ".claude/agents/researcher.md").exists())
            env_text = (destination / ".env.example").read_text()
            self.assertNotIn("PERPLEXITY", env_text)
            self.assertNotIn("SUPABASE", env_text)

    def test_research_project_lists_credentials_but_does_not_enable_servers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "research-project"
            result = self.run_generator(
                "--name",
                "Research Project",
                "--destination",
                str(destination),
                "--preset",
                "research",
                "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            env_text = (destination / ".env.example").read_text()
            self.assertIn("PERPLEXITY_API_KEY", env_text)
            self.assertIn("FIRECRAWL_API_KEY", env_text)
            self.assertEqual(
                {"mcpServers": {}},
                json.loads((destination / ".mcp.json").read_text()),
            )
            metadata = json.loads(
                (destination / ".agentic/generated-project.json").read_text()
            )
            self.assertIn("perplexity-mcp", metadata["expected_external_setup"])
            self.assertIn("firecrawl-mcp", metadata["expected_external_setup"])

    def test_generated_verification_rejects_capability_activation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "policy-project"
            result = self.run_generator(
                "--name",
                "Policy Project",
                "--destination",
                str(destination),
                "--preset",
                "core",
                "--yes",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest_path = destination / ".agentic/project.json"
            manifest = json.loads(manifest_path.read_text())

            manifest["policy"]["allow_automatic_install"] = True
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            with self.assertRaisesRegex(
                project_generator.GenerationError,
                "automatic capability installation and removal disabled",
            ):
                project_generator.validate_generated_project(destination)

            manifest["policy"]["allow_automatic_install"] = False
            manifest["specialists"] = ["unreviewed-specialist"]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            with self.assertRaisesRegex(
                project_generator.GenerationError, "must not activate external specialists"
            ):
                project_generator.validate_generated_project(destination)

    def test_existing_destination_is_preserved_and_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "existing"
            destination.mkdir()
            marker = destination / "keep.txt"
            marker.write_text("user owned\n")
            result = self.run_generator(
                "--name",
                "Existing",
                "--destination",
                str(destination),
                "--preset",
                "core",
                "--yes",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)
            self.assertEqual("user owned\n", marker.read_text())

    def test_destination_inside_source_fails_before_writing(self) -> None:
        destination = ROOT / ".forbidden-generator-target"
        self.assertFalse(destination.exists())
        result = self.run_generator(
            "--name",
            "Unsafe",
            "--destination",
            str(destination),
            "--preset",
            "core",
            "--dry-run",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the starter checkout", result.stderr)
        self.assertFalse(destination.exists())

    def test_sensitive_file_names_are_excluded(self) -> None:
        config = project_generator.load_config(ROOT)
        for value in (
            ".env.production",
            "apps/web/.env.local",
            ".npmrc",
            "credentials/private.key",
            "apps/web/playwright/.auth/state.json",
            "apps/web/trace.har",
            "apps/web/cache.tsbuildinfo",
            "scripts/__pycache__/helper.pyc",
            ".vscode/settings.json",
        ):
            with self.subTest(value=value):
                self.assertFalse(
                    project_generator.path_allowed(Path(value), config, {"core"})
                )

    def test_escaping_source_symlink_is_rejected_before_destination_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "generated"
            source.mkdir()
            (root / "outside").mkdir()
            os.symlink(root / "outside", source / "escape")

            base = project_generator.build_plan(
                name="Safe Base",
                destination=str(destination),
                selected_profiles=["core"],
            )
            plan = replace(
                base,
                source_root=source.resolve(),
                files=(Path("escape"),),
            )

            with self.assertRaisesRegex(
                project_generator.GenerationError, "path escapes the starter"
            ):
                project_generator.materialize(plan)
            self.assertFalse(destination.exists())

    def test_rollback_refuses_to_delete_a_replacement_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "generated"
            moved_original = root / "original-created-directory"
            base = project_generator.build_plan(
                name="Rollback Identity",
                destination=str(destination),
                selected_profiles=["core"],
            )
            plan = replace(base, files=(Path("LICENSE"),))

            def replace_destination(_: Path, __: Path) -> None:
                destination.rename(moved_original)
                destination.mkdir()
                (destination / "keep.txt").write_text("replacement\n")
                raise project_generator.GenerationError("forced copy failure")

            with mock.patch.object(
                project_generator, "copy_entry", side_effect=replace_destination
            ):
                with self.assertRaisesRegex(
                    project_generator.GenerationError, "rollback refused"
                ):
                    project_generator.materialize(plan)

            self.assertEqual("replacement\n", (destination / "keep.txt").read_text())
            self.assertTrue(moved_original.is_dir())

    def test_symlinked_parent_is_rejected_before_destination_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "generated"
            outside = root / "outside"
            source.mkdir()
            outside.mkdir()
            (outside / "payload.txt").write_text("outside\n")
            os.symlink(outside, source / "nested")

            base = project_generator.build_plan(
                name="Safe Base",
                destination=str(destination),
                selected_profiles=["core"],
            )
            plan = replace(
                base,
                source_root=source.resolve(),
                files=(Path("nested/payload.txt"),),
            )
            with self.assertRaisesRegex(
                project_generator.GenerationError, "path escapes the starter"
            ):
                project_generator.materialize(plan)
            self.assertFalse(destination.exists())

    def test_git_checkout_is_required_instead_of_filesystem_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "generated"
            (source / ".agentic").mkdir(parents=True)
            (source / ".agentic/generator.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source_roots": ["docs"],
                        "always_excluded": [],
                        "profile_paths": {},
                    }
                )
            )
            (source / "package.json").write_text(
                json.dumps({"name": "fixture", "version": "0.1.0"})
            )
            with self.assertRaisesRegex(
                project_generator.GenerationError, "valid Git checkout is required"
            ):
                project_generator.build_plan(
                    name="Archive Copy",
                    destination=str(destination),
                    selected_profiles=["core"],
                    source_root=source,
                )
            self.assertFalse(destination.exists())

    def test_generator_configuration_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            (source / ".agentic").mkdir()
            (source / ".agentic/generator.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source_roots": ["../outside"],
                        "always_excluded": [],
                        "profile_paths": {},
                    }
                )
            )
            with self.assertRaisesRegex(
                project_generator.GenerationError, "contained relative paths"
            ):
                project_generator.load_config(source)


if __name__ == "__main__":
    unittest.main()
