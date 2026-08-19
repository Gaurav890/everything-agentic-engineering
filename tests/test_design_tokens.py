from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_design_tokens


class DesignTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tokens = build_design_tokens.load_tokens()
        build_design_tokens.validate(cls.tokens)

    def test_token_source_is_nontrivial(self) -> None:
        self.assertGreaterEqual(len(self.tokens), 90)

    def test_alias_resolution(self) -> None:
        value = build_design_tokens.resolve("theme.light.color.text.primary", self.tokens)
        self.assertEqual(value["colorSpace"], "srgb")

    def test_css_and_typescript_are_generated(self) -> None:
        css, typescript, native, preview, direction = build_design_tokens.generate(self.tokens)
        self.assertIn(":root {", css)
        self.assertIn('[data-theme="dark"]', css)
        self.assertIn("--eae-color-text-primary", css)
        self.assertIn(
            "--eae-button-primary-background-default: var(--eae-color-action-primary-default)",
            css,
        )
        self.assertIn("export const tokens", typescript)
        self.assertIn("export type TokenName", typescript)
        self.assertIn("export const lightTheme", native)
        self.assertIn("export const darkTheme", native)
        self.assertIn("Design token specimen", preview)
        self.assertIn("Required contrast pairs", preview)
        self.assertIn("No direction approved", direction)

    def test_component_tokens_resolve_per_mode(self) -> None:
        light = build_design_tokens.resolve(
            "button.primary.background.default", self.tokens, mode="light"
        )
        dark = build_design_tokens.resolve(
            "button.primary.background.default", self.tokens, mode="dark"
        )
        self.assertNotEqual(light["components"], dark["components"])

    def test_theme_key_and_type_parity(self) -> None:
        build_design_tokens.validate_theme_parity(self.tokens)
        invalid = copy.deepcopy(self.tokens)
        del invalid["theme.dark.color.focus.ring"]
        with self.assertRaises(build_design_tokens.TokenError):
            build_design_tokens.validate_theme_parity(invalid)

    def test_required_contrast_pairs_pass(self) -> None:
        results = build_design_tokens.contrast_results(self.tokens)
        self.assertTrue(results)
        self.assertTrue(all(ratio >= minimum for _, _, _, ratio, minimum in results))

    def test_low_contrast_fails(self) -> None:
        invalid = copy.deepcopy(self.tokens)
        invalid["theme.light.color.text.primary"]["value"] = "{color.neutral.0}"
        with self.assertRaises(build_design_tokens.TokenError):
            build_design_tokens.validate_contrast(invalid)

    def test_component_cannot_reference_specific_theme(self) -> None:
        invalid = copy.deepcopy(self.tokens)
        invalid["button.primary.background.default"]["value"] = (
            "{theme.light.color.action.primary.default}"
        )
        with self.assertRaises(build_design_tokens.TokenError):
            build_design_tokens.validate_component_aliases(invalid)

    def test_unknown_alias_fails(self) -> None:
        with self.assertRaises(build_design_tokens.TokenError):
            build_design_tokens.resolve("missing.token", self.tokens)


if __name__ == "__main__":
    unittest.main()
