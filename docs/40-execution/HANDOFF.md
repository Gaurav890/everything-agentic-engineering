# Handoff

Last updated: 2026-08-10

## Current goal

Keep external design-engineering craft precise, profile-aware, reviewable, and
subordinate to the product's approved experience contract.

## Completed

- The full Emil Kowalski ten-skill inventory is recorded with provenance,
  reviewed revision, license, phase, trigger, and invocation policy.
- `design-engineering-quality` routes the broad craft pass or one exact
  specialist without replacing upstream product/design work. `emil-design-eng`
  is the first external design implementation skill; Anthropic
  `frontend-design` is secondary and opt-in.
- Motion requires purpose, interruption, performance, accessibility, and
  reduced-motion behavior; no motion is an acceptable result.
- The `design-critical` profile activates the external collection while web-only
  and mobile-only concerns remain independently selectable.
- External setup is explicit, pinned, targets Claude Code and Codex, and has a
  non-mutating preview.

## Blockers

- None.

## Unresolved decisions

- Future upstream revisions require a new source review before the pinned
  manifest may advance.
- The collection remains optional; projects can use the local fallback contracts
  when external installation is undesirable.
- Human approval remains necessary for design-direction changes, live variant
  selection, new UI dependencies, and final merge.

## Verification status

- External-skill manifest and profile tests pass.
- The local skill passes the platform validator.
- Full repository verification passes all ten stages across 28 tracked tasks
  and 28 shared local skills.

## Exact next action

Preview selected external capabilities with `./agentic setup skills --dry-run`.
Install only after reviewing the pinned plan, then let `product-design-router`
select the minimum capability for each real product task.

## Relevant files

- `.agentic/external-skills.json`
- `.agentic/profiles/design-critical.json`
- `.claude/skills/design-engineering-quality/SKILL.md`
- `.claude/skills/product-design-router/SKILL.md`
- `docs/60-tooling/PRODUCT_DESIGN_RESOURCES.md`
- `scripts/install-skills.sh`

Keep this concise enough to read in under two minutes.
