#!/usr/bin/env python3
"""Guide project setup and write only the approved profile manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import profile_engine  # noqa: E402


def prompt(question: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def interactive_answers() -> argparse.Namespace:
    print("Everything Agentic Engineering — project initializer")
    print("This selects profiles only. It never installs or deletes tools.")
    project_name = input("Project name: ").strip() or "my-agentic-project"
    web = prompt("Build a web application?", default=True)
    mobile = prompt("Build a native Expo/React Native application?")
    design = prompt("Is product design a primary competitive advantage?", default=True)
    research = prompt("Enable current-web research and crawling?", default=True)
    agentic = prompt("Does the product include AI agents or copilots?")
    backend = input("Backend [none/supabase/convex] (default none): ").strip().lower() or "none"
    return argparse.Namespace(
        name=project_name,
        web=web,
        mobile=mobile,
        design=design,
        research=research,
        agentic=agentic,
        backend=backend,
        dry_run=False,
        yes=False,
    )


def selected_profiles(args: argparse.Namespace) -> list[str]:
    selected: list[str] = []
    if args.web:
        selected.append("web-next")
    if args.mobile:
        selected.append("mobile-expo")
    if args.design or args.agentic:
        selected.append("design-critical")
    if args.research:
        selected.append("research-enabled")
    if args.backend != "none":
        selected.append(f"backend-{args.backend}")
    if not selected:
        selected.append("core")
    return selected


def build_manifest(name: str, profiles: list[str]) -> dict:
    current = profile_engine.load_json(profile_engine.PROJECT_PATH)
    current["project"] = {"name": name}
    current["profiles"] = profiles
    current.setdefault(
        "policy",
        {"allow_automatic_install": False, "allow_automatic_removal": False},
    )
    current["policy"]["allow_automatic_install"] = False
    current["policy"]["allow_automatic_removal"] = False
    return current


def run(args: argparse.Namespace) -> int:
    if args.backend not in {"none", "supabase", "convex"}:
        raise profile_engine.ProfileError("backend must be none, supabase, or convex")
    profiles = selected_profiles(args)
    result = profile_engine.resolve(profiles)
    if result["conflicts"]:
        raise profile_engine.ProfileError("Conflicting profiles: " + ", ".join(result["conflicts"]))

    manifest = build_manifest(args.name, profiles)
    print("\nProposed project configuration:")
    print(json.dumps(manifest, indent=2))
    print("\nResolved capabilities:")
    for profile_id in result["resolved_profiles"]:
        print(f"  - {profile_id}")
    print("\nThis will not install, enable, remove, or delete any resource.")

    if args.dry_run:
        print("Dry run complete; no files changed.")
        return 0
    if not args.yes:
        print("No change made. Re-run with --yes after reviewing the proposal.")
        return 2

    temporary = profile_engine.PROJECT_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n")
    temporary.replace(profile_engine.PROJECT_PATH)
    print("Updated .agentic/project.json.")
    print("Next: run ./scripts/profile-doctor.sh and review external requirements.")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--name")
    value.add_argument("--web", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--mobile", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--design", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--research", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--agentic", action=argparse.BooleanOptionalAction, default=False)
    value.add_argument("--backend", default="none")
    value.add_argument("--dry-run", action="store_true")
    value.add_argument("--yes", action="store_true")
    return value


def main() -> int:
    try:
        if len(sys.argv) == 1:
            args = interactive_answers()
            print("\nReview the proposal before confirming.")
            args.yes = prompt("Write this profile manifest?")
        else:
            args = parser().parse_args()
            if not args.name:
                raise profile_engine.ProfileError("--name is required in non-interactive mode")
        return run(args)
    except (profile_engine.ProfileError, EOFError, KeyboardInterrupt) as exc:
        print(f"Initializer error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
