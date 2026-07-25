# Handoff

Last updated: 2026-07-25

## Current goal

Land T-001 through review without merging directly to `main`.

## Completed

- Phase-based product-design routing and contracts.
- Product-specific design-system authority rules.
- DTCG-compatible primitive, semantic, component, theme, layout, density,
  motion, and agent-state token scaffold.
- Skill and repository verification.

## In progress

- Final branch commit and pull-request preparation.

## Blockers

- `gh` is not installed; PR creation may require GitHub API tooling or manual URL.

## Unresolved decisions

- Select a build/export tool only when a target web/mobile profile needs it.
- Choose external design-phase skills per active project; do not bulk-install.

## Verification status

All local skills validate. Full repository verification and diff checks pass.

## Exact next action

Review the committed diff, push `feat/T-001-product-design-engine`, and open a
PR titled `feat(T-001): add phase-based product design engine`.

## Relevant files

- `.claude/skills/product-design-router/SKILL.md`
- `.claude/skills/design-system/SKILL.md`
- `.claude/skills/design-tokens/SKILL.md`
- `docs/20-design/DESIGN_SYSTEM.md`
- `docs/60-tooling/SKILLS.md`
- `packages/design-tokens/`

Keep this concise enough to read in under two minutes.
