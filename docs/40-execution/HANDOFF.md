# Handoff

Last updated: 2026-08-19

## Current goal

Finish the human-reviewed Linux baseline loop for the web quality gate.

## Completed

- Replaced placeholder web/UI surfaces with a runnable Next.js portfolio.
- Added a short adaptive design intake and explicit approval/reset state.
- Added three materially different live directions using identical content.
- Compiled an approved DTCG-compatible direction into semantic CSS overrides.
- Added responsive, focus, reduced-motion, UI contract, generator, and command
  checks.
- Put the web golden path first in the README and generated project README.
- Added Playwright coverage for every direction at desktop and mobile sizes,
  including keyboard, selection, axe, overflow, and reduced-motion contracts.
- Added a fail-closed Linux visual workflow with reviewable candidate and
  failure artifacts.
- Fixed the low-contrast step indexes exposed by the new axe scan.

## Blockers

- No code or local verification blocker.
- Linux baseline candidates must be generated in CI and inspected by a human;
  automatic generation is not visual approval.

## Unresolved decisions

- The sample portfolio content must be replaced by each downstream project.
- Advanced Motion, GSAP, Rive/canvas, or React Three Fiber remains opt-in and
  should be selected only after the approved direction establishes user value,
  device budget, reduced-motion behavior, and fallback.
- Mobile still needs its own executable golden path in a later task; web work
  was deliberately completed first.

## Verification status

- Web unit tests, project-generator tests, the production build, and the new
  Playwright interaction/accessibility suite pass locally.
- The live desktop and 390 x 844 mobile experience was inspected across all
  three directions with no horizontal overflow or browser errors.
- The independent critic returned code-level PASS after keyboard, flaky-test,
  clipboard-state, and reduced-motion findings were resolved.
- Full repository verification must be rerun after the final T-040 evidence
  and state updates.

## Exact next action

Open the draft pull request so Ubuntu CI can produce the six Linux baseline
candidates. Inspect those images, commit only approved baselines, rerun normal
comparison, and then request direct human task approval. Landing remains a
separate human action.

## Relevant files

- `apps/web/`
- `packages/ui/`
- `.agentic/design-directions.json`
- `scripts/design_engine.py`
- `.github/workflows/web-quality.yml`
- `apps/web/playwright.config.ts`
- `apps/web/tests/portfolio.spec.ts`
- `apps/web/tests/visual.spec.ts`
- `docs/60-tooling/PORTFOLIO_GOLDEN_PATH.md`
- `tests/test_design_engine.py`
- `tests/test_project_generator.py`

Keep this concise enough to read in under two minutes.
