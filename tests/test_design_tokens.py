from __future__ import annotations

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

    def test_token_source_is_nontrivial(self) -> None:
        self.assertGreaterEqual(len(self.tokens), 90)

    def test_alias_resolution(self) -> None:
        value = build_design_tokens.resolve("theme.light.color.text.primary", self.tokens)
        self.assertEqual(value["colorSpace"], "srgb")

    def test_css_and_typescript_are_generated(self) -> None:
        css, typescript, native = build_design_tokens.generate(self.tokens)
        self.assertIn(":root {", css)
        self.assertIn('[data-theme="dark"]', css)
        self.assertIn("--eae-color-text-primary", css)
        self.assertIn("export const tokens", typescript)
        self.assertIn("export type TokenName", typescript)
        self.assertIn("export const lightTheme", native)
        self.assertIn("export const darkTheme", native)

    def test_unknown_alias_fails(self) -> None:
        with self.assertRaises(build_design_tokens.TokenError):
            build_design_tokens.resolve("missing.token", self.tokens)


if __name__ == "__main__":
    unittest.main()
