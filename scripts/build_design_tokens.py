#!/usr/bin/env python3
"""Validate and generate CSS and TypeScript from the DTCG token source."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

import design_engine

ROOT = Path(__file__).resolve().parents[1]
TOKEN_ROOT = ROOT / "packages/design-tokens/tokens"
GENERATED_ROOT = ROOT / "packages/design-tokens/generated"
ALIAS = re.compile(r"^\{([^}]+)\}$")


class TokenError(Exception):
    pass


def load_tokens() -> dict[str, dict[str, Any]]:
    tokens: dict[str, dict[str, Any]] = {}

    def walk(
        node: Any,
        path: tuple[str, ...],
        inherited_type: str | None,
        layer: str,
    ) -> None:
        if not isinstance(node, dict):
            return
        token_type = node.get("$type", inherited_type)
        if "$value" in node:
            name = ".".join(path)
            if name in tokens:
                raise TokenError(f"Duplicate token: {name}")
            tokens[name] = {
                "type": token_type,
                "value": node["$value"],
                "layer": layer,
            }
            return
        for key, child in node.items():
            if not key.startswith("$"):
                walk(child, path + (key,), token_type, layer)

    for path in sorted(TOKEN_ROOT.glob("*/*.json")):
        walk(json.loads(path.read_text()), (), None, path.parent.name)
    return tokens


def resolve(
    name: str,
    tokens: dict[str, dict[str, Any]],
    stack: tuple[str, ...] = (),
    mode: str | None = None,
) -> Any:
    lookup = name
    if mode and not name.startswith("theme."):
        override = f"theme.{mode}.{name}"
        if override in tokens:
            lookup = override
    if lookup not in tokens:
        raise TokenError(f"Unknown token alias: {lookup}")
    if lookup in stack:
        raise TokenError("Circular token alias: " + " -> ".join(stack + (lookup,)))
    value = tokens[lookup]["value"]
    if isinstance(value, str):
        match = ALIAS.fullmatch(value)
        if match:
            return resolve(match.group(1), tokens, stack + (lookup,), mode)
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


def css_token_value(name: str, tokens: dict[str, dict[str, Any]]) -> str:
    value = tokens[name]["value"]
    if isinstance(value, str):
        match = ALIAS.fullmatch(value)
        if match:
            return f"var({variable_name(match.group(1))})"
    return css_value(resolve(name, tokens), tokens[name]["type"])


def theme_tokens(tokens: dict[str, dict[str, Any]], mode: str) -> dict[str, dict[str, Any]]:
    prefix = f"theme.{mode}."
    return {
        name.removeprefix(prefix): token
        for name, token in tokens.items()
        if name.startswith(prefix)
    }


def validate_theme_parity(tokens: dict[str, dict[str, Any]]) -> None:
    light = theme_tokens(tokens, "light")
    dark = theme_tokens(tokens, "dark")
    missing_dark = sorted(set(light) - set(dark))
    missing_light = sorted(set(dark) - set(light))
    if missing_dark or missing_light:
        raise TokenError(
            "Theme semantic parity failed; "
            f"missing in dark={missing_dark}, missing in light={missing_light}"
        )
    mismatched_types = sorted(
        name for name in light if light[name]["type"] != dark[name]["type"]
    )
    if mismatched_types:
        raise TokenError("Theme token type mismatch: " + ", ".join(mismatched_types))


def validate_component_aliases(tokens: dict[str, dict[str, Any]]) -> None:
    invalid: list[str] = []
    for name, token in tokens.items():
        value = token["value"]
        match = ALIAS.fullmatch(value) if isinstance(value, str) else None
        if token["layer"] == "component" and match and match.group(1).startswith("theme."):
            invalid.append(name)
    if invalid:
        raise TokenError(
            "Component tokens must reference mode-independent roles: " + ", ".join(invalid)
        )


def relative_luminance(value: Any) -> float:
    if not isinstance(value, dict) or value.get("colorSpace") != "srgb":
        raise TokenError("Contrast validation currently requires sRGB color tokens")
    components = value.get("components")
    if not isinstance(components, list) or len(components) != 3:
        raise TokenError(f"Unsupported color value for contrast: {value}")

    def linearize(component: float) -> float:
        return component / 12.92 if component <= 0.04045 else ((component + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(float(component)) for component in components)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: Any, second: Any) -> float:
    high, low = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


CONTRAST_PAIRS = (
    ("color.text.primary", "color.background.canvas", 4.5, "normal text"),
    ("color.text.secondary", "color.background.canvas", 4.5, "secondary text"),
    ("color.action.primary.default", "color.background.canvas", 3.0, "primary control"),
    ("color.action.primary.foreground", "color.action.primary.default", 4.5, "button label"),
    ("color.focus.ring", "color.background.canvas", 3.0, "focus indicator"),
)


def contrast_results(tokens: dict[str, dict[str, Any]]) -> list[tuple[str, str, str, float, float]]:
    results: list[tuple[str, str, str, float, float]] = []
    for mode in ("light", "dark"):
        for foreground, background, minimum, purpose in CONTRAST_PAIRS:
            ratio = contrast_ratio(
                resolve(foreground, tokens, mode=mode),
                resolve(background, tokens, mode=mode),
            )
            results.append((mode, purpose, f"{foreground} / {background}", ratio, minimum))
    return results


def validate_contrast(tokens: dict[str, dict[str, Any]]) -> None:
    failures = [
        f"{mode} {purpose} {pair}: {ratio:.2f}:1 < {minimum:.1f}:1"
        for mode, purpose, pair, ratio, minimum in contrast_results(tokens)
        if ratio < minimum
    ]
    if failures:
        raise TokenError("Contrast validation failed: " + "; ".join(failures))


def validate(tokens: dict[str, dict[str, Any]]) -> None:
    validate_theme_parity(tokens)
    validate_component_aliases(tokens)
    validate_contrast(tokens)


def generate_preview(tokens: dict[str, dict[str, Any]]) -> str:
    roles = sorted(
        name
        for name, token in theme_tokens(tokens, "light").items()
        if token["type"] == "color"
    )
    sections: list[str] = []
    for mode in ("light", "dark"):
        swatches = "".join(
            '<li><span class="swatch" style="background:var('
            + html.escape(variable_name(role))
            + ')"></span><code>'
            + html.escape(role)
            + "</code></li>"
            for role in roles
        )
        rows = "".join(
            "<tr><td>"
            + html.escape(purpose)
            + "</td><td><code>"
            + html.escape(pair)
            + f"</code></td><td>{ratio:.2f}:1</td><td>{minimum:.1f}:1</td></tr>"
            for result_mode, purpose, pair, ratio, minimum in contrast_results(tokens)
            if result_mode == mode
        )
        sections.append(
            f'<section class="theme" data-theme="{mode}"><header><div><p class="eyebrow">Mode</p>'
            f"<h2>{mode.title()}</h2></div><button>Primary action</button></header>"
            f'<ul class="swatches">{swatches}</ul><h3>Required contrast pairs</h3>'
            f"<table><thead><tr><th>Purpose</th><th>Pair</th><th>Actual</th><th>Minimum</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></section>"
        )
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Design token specimen</title>
  <link rel="stylesheet" href="tokens.css">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; background: #e8e8ec; color: #111; }
    main { width: min(1180px, calc(100% - 32px)); margin: 40px auto; }
    h1 { margin: 0 0 8px; font-size: clamp(2rem, 5vw, 4rem); letter-spacing: -.05em; }
    .intro { max-width: 68ch; margin: 0 0 32px; color: #4e4e59; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 460px), 1fr)); gap: 20px; }
    .theme { padding: 24px; border: 1px solid var(--eae-color-border-default); border-radius: var(--eae-radius-lg); background: var(--eae-color-background-canvas); color: var(--eae-color-text-primary); box-shadow: var(--eae-shadow-low); }
    header { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    h2, h3 { margin: 0; } h3 { margin-top: 28px; font-size: 1rem; }
    .eyebrow { margin: 0 0 4px; color: var(--eae-color-text-secondary); font-size: .75rem; text-transform: uppercase; letter-spacing: .12em; }
    button { border: 0; border-radius: var(--eae-button-primary-radius); padding: 10px 14px; color: var(--eae-button-primary-foreground); background: var(--eae-button-primary-background-default); transition: background var(--eae-button-primary-transition); }
    button:hover { background: var(--eae-button-primary-background-hover); }
    button:focus-visible { outline: 3px solid var(--eae-button-primary-focusring); outline-offset: 3px; }
    .swatches { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; padding: 0; margin: 24px 0 0; list-style: none; }
    .swatches li { display: grid; grid-template-columns: 36px 1fr; align-items: center; gap: 10px; min-width: 0; }
    .swatch { width: 36px; height: 36px; border: 1px solid var(--eae-color-border-default); border-radius: var(--eae-radius-sm); }
    code { overflow-wrap: anywhere; font-size: .72rem; }
    table { width: 100%; margin-top: 10px; border-collapse: collapse; font-size: .78rem; }
    th, td { padding: 9px 6px; border-bottom: 1px solid var(--eae-color-border-default); text-align: left; vertical-align: top; }
    @media (max-width: 580px) { main { margin: 24px auto; } .theme { padding: 18px; } header { align-items: flex-start; flex-direction: column; } }
  </style>
</head>
<body><main><h1>Design token specimen</h1><p class="intro">Generated evidence for semantic roles, modes, component aliases, and required WCAG contrast pairs. Review this with realistic product screens before approving a direction.</p><div class="grid">""" + "".join(sections) + """</div></main></body></html>
"""


def generate(tokens: dict[str, dict[str, Any]]) -> tuple[str, str, str, str, str]:
    base: list[str] = []
    light: list[str] = []
    dark: list[str] = []
    resolved: dict[str, Any] = {}

    for name in sorted(tokens):
        value = resolve(name, tokens)
        resolved[name] = value
        declaration = f"  {variable_name(name)}: {css_token_value(name, tokens)};"
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
    light_theme: dict[str, Any] = {
        name.removeprefix("theme.light."): value
        for name, value in resolved.items()
        if name.startswith("theme.light.")
    }
    dark_theme: dict[str, Any] = {
        name.removeprefix("theme.dark."): value
        for name, value in resolved.items()
        if name.startswith("theme.dark.")
    }
    for name, token in tokens.items():
        if token["layer"] in {"semantic", "component"}:
            light_theme[name] = resolve(name, tokens, mode="light")
            dark_theme[name] = resolve(name, tokens, mode="dark")
    native = (
        "// Generated from DTCG sources. Do not edit directly.\n"
        "export const lightTheme = "
        + json.dumps(light_theme, indent=2, sort_keys=True)
        + " as const;\n\nexport const darkTheme = "
        + json.dumps(dark_theme, indent=2, sort_keys=True)
        + " as const;\n\nexport type NativeTheme = typeof lightTheme;\n"
    )
    return css, ts, native, generate_preview(tokens), design_engine.render_direction_css()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated output is stale")
    args = parser.parse_args()
    tokens = load_tokens()
    validate(tokens)
    css, ts, native, preview, direction = generate(tokens)
    expected = {
        GENERATED_ROOT / "tokens.css": css,
        GENERATED_ROOT / "tokens.ts": ts,
        GENERATED_ROOT / "tokens.native.ts": native,
        GENERATED_ROOT / "tokens.preview.html": preview,
        GENERATED_ROOT / "direction.css": direction,
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in expected.items() if not path.exists() or path.read_text() != text]
        if stale:
            raise TokenError("Generated token output is stale: " + ", ".join(stale))
        print(f"Generated design-token outputs and evidence are current ({len(tokens)} tokens)")
        return 0
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    for path, text in expected.items():
        path.write_text(text)
    print(f"Generated CSS, TypeScript, native themes, and preview from {len(tokens)} tokens")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenError as exc:
        print(f"Token build error: {exc}")
        raise SystemExit(1)
