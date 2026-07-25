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

PRESETS = {
    "core": ["core"],
    "web": ["web-next", "design-critical"],
    "web-research": ["web-next", "design-critical", "research-enabled"],
    "web-supabase": ["web-next", "design-critical", "backend-supabase"],
    "mobile": ["mobile-expo", "design-critical"],
    "mobile-research": ["mobile-expo", "design-critical", "research-enabled"],
    "full-stack": [
        "web-next",
        "mobile-expo",
        "design-critical",
        "research-enabled",
        "backend-supabase",
    ],
    "research": ["research-enabled"],
}


def prompt(question: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{question} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def prompt_choice(question: str, choices: tuple[str, ...], default: str) -> str:
    allowed = "/".join(choices)
    while True:
        answer = input(f"{question} [{allowed}] (default {default}): ").strip().lower()
        value = answer or default
        if value in choices:
            return value
        print(f"Choose one of: {', '.join(choices)}")


def interactive_answers() -> argparse.Namespace:
    print("Everything Agentic Engineering — project initializer")
    print("Choose only what this product needs.")
    print("The initializer previews first and never installs or deletes tools.")
    project_name = input("Project name: ").strip() or "my-agentic-project"
    surface = prompt_choice(
        "What are you building?",
        ("web", "mobile", "both", "core"),
        "web",
    )
    web = surface in {"web", "both"}
    mobile = surface in {"mobile", "both"}
    design = prompt("Is product design a primary competitive advantage?", default=True)
    research = prompt("Enable current-web research and crawling?", default=True)
    agentic = prompt("Does the product include AI agents or copilots?")
    backend = prompt_choice("Primary backend", ("none", "supabase", "convex"), "none")
    return argparse.Namespace(
        name=project_name,
        preset=None,
        web=web,
        mobile=mobile,
        design=design,
        research=research,
        agentic=agentic,
        backend=backend,
        dry_run=False,
        yes=False,
        list_presets=False,
    )


def selected_profiles(args: argparse.Namespace) -> list[str]:
    selectors_used = any((args.web, args.mobile, args.design, args.research, args.agentic))
    if args.preset:
        if selectors_used or args.backend != "none":
            raise profile_engine.ProfileError(
                "--preset cannot be combined with surface, design, research, agentic, or backend selectors"
            )
        return list(PRESETS[args.preset])

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


def print_presets() -> None:
    print("Available presets:")
    for preset, profiles in PRESETS.items():
        print(f"  {preset:16} {', '.join(profiles)}")


def print_capability_plan(result: dict) -> None:
    profiles = profile_engine.load_profiles()
    active_profiles = set(result["resolved_profiles"])
    active_resources = set(result["required_resources"])
    resources = result["resources"]

    print("\nActive profiles:")
    for profile_id in result["resolved_profiles"]:
        print(f"  + {profile_id}: {profiles[profile_id]['description']}")

    print("\nInactive profiles:")
    for profile_id in sorted(set(profiles) - active_profiles):
        print(f"  - {profile_id}: {profiles[profile_id]['description']}")

    print("\nActive capabilities:")
    for resource_id in result["required_resources"]:
        resource = resources[resource_id]
        print(f"  + {resource_id}: {resource['description']}")

    print("\nInactive capabilities (retained in the starter, not routed or required):")
    for resource_id in sorted(set(resources) - active_resources):
        resource = resources[resource_id]
        print(f"  - {resource_id}: {resource['description']}")

    external = [
        resource_id
        for resource_id in result["required_resources"]
        if resources[resource_id].get("kind") in {"external-skill", "mcp", "backend"}
    ]
    if external:
        print("\nExternal setup to review after selection:")
        for resource_id in external:
            print(f"  ! {resource_id}: {resources[resource_id]['description']}")


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
    print_capability_plan(result)
    print("\nSafety contract:")
    print("  - Writes only .agentic/project.json after confirmation.")
    print("  - Does not install, connect, enable, remove, or delete resources.")
    print("  - Inactive template files remain available but agents must not route to them.")

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
    print("Next: run ./scripts/profile-doctor.sh and review the external setup list.")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--name")
    value.add_argument("--preset", choices=tuple(PRESETS))
    value.add_argument("--list-presets", action="store_true")
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
            if args.list_presets:
                print_presets()
                return 0
            if not args.name:
                raise profile_engine.ProfileError("--name is required in non-interactive mode")
        return run(args)
    except (profile_engine.ProfileError, EOFError, KeyboardInterrupt) as exc:
        print(f"Initializer error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
