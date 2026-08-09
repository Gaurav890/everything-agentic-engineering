#!/usr/bin/env python3
"""Report agent runtime compatibility without installing or enabling anything."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / ".agentic/runtime-baselines.json"
VERSION_PATTERN = re.compile(
    r"(?<!\d)(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?P<suffix>[-+][0-9A-Za-z.-]+)?"
)


class RuntimePolicyError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedVersion:
    core: tuple[int, int, int]
    text: str
    prerelease: bool

    def meets(self, required: "ParsedVersion") -> bool:
        if self.core != required.core:
            return self.core > required.core
        if self.prerelease and not required.prerelease:
            return False
        return True


def parse_version(text: str) -> ParsedVersion | None:
    match = VERSION_PATTERN.search(text)
    if not match:
        return None
    suffix = match.group("suffix") or ""
    return ParsedVersion(
        core=tuple(int(match.group(name)) for name in ("major", "minor", "patch")),
        text=match.group(0),
        prerelease=suffix.startswith("-"),
    )


def load_manifest(path: Path) -> dict:
    try:
        manifest = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimePolicyError(f"cannot read runtime policy: {exc}") from exc

    if manifest.get("schema_version") != 1:
        raise RuntimePolicyError("runtime policy schema_version must be 1")
    runtimes = manifest.get("runtimes")
    if not isinstance(runtimes, dict) or not runtimes:
        raise RuntimePolicyError("runtime policy must define runtimes")

    for runtime_id, policy in runtimes.items():
        if not isinstance(policy, dict):
            raise RuntimePolicyError(f"{runtime_id}: policy must be an object")
        for required_key in ("command", "recommended_minimum", "source", "capabilities"):
            if required_key not in policy:
                raise RuntimePolicyError(f"{runtime_id}: missing {required_key}")
        if parse_version(str(policy["recommended_minimum"])) is None:
            raise RuntimePolicyError(f"{runtime_id}: invalid recommended_minimum")
        if not str(policy["source"]).startswith("https://"):
            raise RuntimePolicyError(f"{runtime_id}: source must be HTTPS")
        capabilities = policy["capabilities"]
        if not isinstance(capabilities, list):
            raise RuntimePolicyError(f"{runtime_id}: capabilities must be a list")
        ids: set[str] = set()
        for capability in capabilities:
            capability_id = capability.get("id") if isinstance(capability, dict) else None
            if not capability_id or capability_id in ids:
                raise RuntimePolicyError(f"{runtime_id}: capability IDs must be unique")
            ids.add(capability_id)
            if parse_version(str(capability.get("minimum", ""))) is None:
                raise RuntimePolicyError(
                    f"{runtime_id}/{capability_id}: invalid minimum"
                )
            if capability.get("default_enabled") not in (True, False):
                raise RuntimePolicyError(
                    f"{runtime_id}/{capability_id}: default_enabled must be boolean"
                )
            if capability.get("default_enabled") is False and capability.get(
                "human_approval_required"
            ) is not True:
                raise RuntimePolicyError(
                    f"{runtime_id}/{capability_id}: optional capabilities require human approval"
                )
    return manifest


def detect_version(command: str) -> tuple[bool, str, ParsedVersion | None]:
    resolved = shutil.which(command)
    if not resolved:
        return False, "", None
    completed = subprocess.run(
        [resolved, "--version"],
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )
    output = (completed.stdout or completed.stderr).strip()
    return True, output, parse_version(output)


def evaluate_runtime(
    runtime_id: str,
    policy: dict,
    override: str | None,
    strict: bool,
) -> dict:
    required = parse_version(policy["recommended_minimum"])
    assert required is not None

    if override is None:
        installed, raw, detected = detect_version(policy["command"])
    else:
        installed, raw, detected = True, override, parse_version(override)

    if not installed:
        status = "fail" if strict else "warn"
        message = f"{runtime_id} is not installed"
    elif detected is None:
        status = "fail" if strict else "warn"
        message = f"{runtime_id} version could not be parsed"
    elif detected.meets(required):
        status = "pass"
        message = (
            f"{runtime_id} {detected.text} meets the "
            f"{required.text} recommended baseline"
        )
    else:
        status = "fail" if strict else "warn"
        message = (
            f"{runtime_id} {detected.text} is below the "
            f"{required.text} recommended baseline"
        )

    return {
        "id": runtime_id,
        "command": policy["command"],
        "installed": installed,
        "detected_version": detected.text if detected else None,
        "recommended_minimum": required.text,
        "status": status,
        "message": message,
        "source": policy["source"],
        "capabilities": policy["capabilities"],
        "raw_version_output": raw or None,
    }


def build_report(args: argparse.Namespace) -> dict:
    manifest = load_manifest(args.manifest)
    runtime_ids = list(manifest["runtimes"])
    if args.runtime != "all":
        if args.runtime not in manifest["runtimes"]:
            raise RuntimePolicyError(f"unknown runtime: {args.runtime}")
        runtime_ids = [args.runtime]

    overrides = {"claude": args.claude_version, "codex": args.codex_version}
    results = [
        evaluate_runtime(
            runtime_id,
            manifest["runtimes"][runtime_id],
            overrides.get(runtime_id),
            args.strict,
        )
        for runtime_id in runtime_ids
    ]
    return {
        "schema_version": 1,
        "strict": args.strict,
        "ok": all(result["status"] != "fail" for result in results),
        "policy_path": str(args.manifest),
        "runtimes": results,
        "mutation_performed": False,
    }


def print_human(report: dict) -> None:
    for runtime in report["runtimes"]:
        print(f"{runtime['status'].upper():4}  {runtime['message']}")
        for capability in runtime["capabilities"]:
            if not capability["default_enabled"]:
                print(
                    "      OPTIONAL "
                    f"{capability['id']} (human approval required; not enabled)"
                )
    mode = "strict" if report["strict"] else "advisory"
    verdict = "PASS" if report["ok"] else "FAIL"
    print(f"\nRuntime compatibility {verdict} ({mode}; read-only).")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Claude Code and Codex runtime compatibility without mutation."
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--runtime", choices=("all", "claude", "codex"), default="all")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--claude-version", help="Explicit version output for testing")
    parser.add_argument("--codex-version", help="Explicit version output for testing")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report(args)
    except RuntimePolicyError as exc:
        if args.json:
            print(json.dumps({"schema_version": 1, "ok": False, "error": str(exc)}))
        else:
            print(f"FAIL  {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
