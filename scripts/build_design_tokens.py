#!/usr/bin/env python3
"""Validate and generate CSS and TypeScript from the DTCG token source."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOKEN_ROOT = ROOT / "packages/design-tokens/tokens"
GENERATED_ROOT = ROOT / "packages/design-tokens/generated"
ALIAS = re.compile(r"^\{([^}]+)\}$")


class TokenError(Exception):
    pass


def load_tokens() -> dict[str, dict[str, Any]]:
    tokens: dict[str, dict[str, Any]] = {}

    def walk(node: Any, path: tuple[str, ...], inherited_type: str | None) -> None:
        if not isinstance(node, dict):
            return
        token_type = node.get("$type", inherited_type)
        if "$value" in node:
            name = ".".join(path)
            if name in tokens:
                raise TokenError(f"Duplicate token: {name}")
            tokens[name] = {"type": token_type, "value": node["$value"]}
            return
        for key, child in node.items():
            if not key.startswith("$"):
                walk(child, path + (key,), token_type)

    for path in sorted(TOKEN_ROOT.glob("*/*.json")):
        walk(json.loads(path.read_text()), (), None)
    return tokens


def resolve(name: str, tokens: dict[str, dict[str, Any]], stack: tuple[str, ...] = ()) -> Any:
    if name not in tokens:
        raise TokenError(f"Unknown token alias: {name}")
    if name in stack:
        raise TokenError("Circular token alias: " + " -> ".join(stack + (name,)))
    value = tokens[name]["value"]
    if isinstance(value, str):
        match = ALIAS.fullmatch(value)
        if match:
            return resolve(match.group(1), tokens, stack + (name,))
    return value


def css_value(value: Any, token_type: str | None) -> str:
    if token_type == "color" and isinstance(value, dict):
        components = value.get("components")
        if not isinstance(components, list) or len(components) != 3:
            raise TokenError(f"Unsupported color value: {value}")
        rgb = [round(float(component) * 255) for component in components]
        alpha = value.get("alpha", 1)
        return f"rgb({rgb[0]} {rgb[1]} {rgb[2]} / {alpha})"
    if token_type in {"dimension", "duration"} and isinstance(value, dict):
        return f"{value['value']}{value['unit']}"
    if token_type == "fontFamily" and isinstance(value, list):
        return ", ".join(f'"{item}"' if " " in item else item for item in value)
    if token_type == "cubicBezier" and isinstance(value, list):
        return "cubic-bezier(" + ", ".join(str(item) for item in value) + ")"
    if token_type == "shadow" and isinstance(value, dict):
        color = css_value(value["color"], "color")
        parts = [
            css_value(value["offsetX"], "dimension"),
            css_value(value["offsetY"], "dimension"),
            css_value(value["blur"], "dimension"),
            css_value(value["spread"], "dimension"),
            color,
        ]
        return " ".join(parts)
    if isinstance(value, (str, int, float)):
        return str(value)
    raise TokenError(f"Unsupported {token_type} value: {value}")


def variable_name(name: str) -> str:
    return "--eae-" + re.sub(r"[^a-z0-9-]+", "-", name.lower().replace(".", "-")).strip("-")


def generate(tokens: dict[str, dict[str, Any]]) -> tuple[str, str, str]:
    base: list[str] = []
    light: list[str] = []
    dark: list[str] = []
    resolved: dict[str, Any] = {}

    for name in sorted(tokens):
        value = resolve(name, tokens)
        resolved[name] = value
        declaration = f"  {variable_name(name)}: {css_value(value, tokens[name]['type'])};"
        if name.startswith("theme.light."):
            light.append(declaration.replace("--eae-theme-light-", "--eae-"))
        elif name.startswith("theme.dark."):
            dark.append(declaration.replace("--eae-theme-dark-", "--eae-"))
        else:
            base.append(declaration)

    css = (
        "/* Generated from DTCG sources. Do not edit directly. */\n"
        ":root {\n" + "\n".join(base + light) + "\n}\n\n"
        '[data-theme="dark"] {\n' + "\n".join(dark) + "\n}\n"
    )
    ts = (
        "// Generated from DTCG sources. Do not edit directly.\n"
        "export const tokens = "
        + json.dumps(resolved, indent=2, sort_keys=True)
        + " as const;\n\nexport type TokenName = keyof typeof tokens;\n"
    )
    light_theme = {
        name.removeprefix("theme.light."): value
        for name, value in resolved.items()
        if name.startswith("theme.light.")
    }
    dark_theme = {
        name.removeprefix("theme.dark."): value
        for name, value in resolved.items()
        if name.startswith("theme.dark.")
    }
    native = (
        "// Generated from DTCG sources. Do not edit directly.\n"
        "export const lightTheme = "
        + json.dumps(light_theme, indent=2, sort_keys=True)
        + " as const;\n\nexport const darkTheme = "
        + json.dumps(dark_theme, indent=2, sort_keys=True)
        + " as const;\n\nexport type NativeTheme = typeof lightTheme;\n"
    )
    return css, ts, native


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated output is stale")
    args = parser.parse_args()
    tokens = load_tokens()
    css, ts, native = generate(tokens)
    expected = {
        GENERATED_ROOT / "tokens.css": css,
        GENERATED_ROOT / "tokens.ts": ts,
        GENERATED_ROOT / "tokens.native.ts": native,
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in expected.items() if not path.exists() or path.read_text() != text]
        if stale:
            raise TokenError("Generated token output is stale: " + ", ".join(stale))
        print(f"Generated design-token outputs are current ({len(tokens)} tokens)")
        return 0
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    for path, text in expected.items():
        path.write_text(text)
    print(f"Generated CSS and TypeScript from {len(tokens)} tokens")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenError as exc:
        print(f"Token build error: {exc}")
        raise SystemExit(1)
