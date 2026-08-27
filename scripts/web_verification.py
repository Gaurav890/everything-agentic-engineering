"""Run explicit web or visual checks without installing or accepting baselines."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from project_checks import ProjectCheckError, active_profiles, web_prerequisite

ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str], root: Path) -> None:
    print("CHECK: " + " ".join(command), flush=True)
    try:
        result = subprocess.run(command, cwd=root, check=False, timeout=900)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProjectCheckError(f"Check could not complete: {error}") from error
    if result.returncode:
        raise ProjectCheckError(f"Check failed ({result.returncode}): {' '.join(command)}")


def verify(mode: str, root: Path = ROOT) -> None:
    if mode not in {"web", "visual"}:
        raise ProjectCheckError("Expected web or visual verification")
    if "web-next" not in active_profiles(root):
        raise ProjectCheckError("No active web profile. Native/mobile readiness is not proved by web checks.")
    prerequisite = web_prerequisite(root)
    if prerequisite:
        raise ProjectCheckError(" — ".join(prerequisite))
    browser_check = subprocess.run(
        ["node", "-e", "const {chromium}=require('@playwright/test');process.exit(require('node:fs').existsSync(chromium.executablePath())?0:1)"],
        cwd=root / "apps/web", capture_output=True, text=True, check=False, timeout=15,
    )
    if browser_check.returncode:
        raise ProjectCheckError(
            "The local Chromium test browser is unavailable. After reviewing the download, run "
            "pnpm --dir apps/web install:browsers, then retry. Nothing was installed."
        )
    if mode == "visual":
        baselines = root / "apps/web/tests"
        if not any(path.parent.name.endswith("-snapshots") for path in baselines.rglob(f"*-{sys.platform}.png")):
            raise ProjectCheckError(
                f"No {sys.platform} visual baselines are present. Follow docs/60-tooling/FIRST_PROJECT.md "
                "for candidate generation and separate human review. No baseline was created or approved."
            )
    else:
        run_command(["bash", "scripts/verify.sh", "full"], root)
    run_command(["pnpm", "--dir", "apps/web", "build"], root)
    selector = "--grep-invert" if mode == "web" else "--grep"
    run_command([
        "pnpm", "--dir", "apps/web", "exec", "playwright", "test", selector, "@visual",
        "--update-snapshots=none",
    ], root)
    if mode == "web":
        print("PASS: repository checks, web build, interaction and automated accessibility checks.")
        print("NOT RUN: visual comparison. Run ./agentic verify visual after baseline review.")
    else:
        print("PASS: web build and visual comparisons. Baselines were not updated.")
    print("Human design review, assistive-technology testing, security review, and production readiness are not certified by this command.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("web", "visual"))
    args = parser.parse_args()
    try:
        verify(args.mode)
    except (ProjectCheckError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Verification blocked: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
