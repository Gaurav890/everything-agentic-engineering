# Handoff

Last updated: 2026-08-25

## Current goal

Maintain a minimal guided product studio whose generated projects preserve the
same design-critical guarantees as the reference starter.

## Completed

- Replaced flag-first onboarding with a guided, one-confirmation project flow.
- Added portfolio, product, and agentic-product experience manifests and
  genuinely different content architectures.
- Added a one-next-action router and profile-relevant downstream generation.
- Made web and mobile application profiles require the design-critical base.
- Added a real agent evidence/review gate and non-obscuring responsive direction
  controls.
- Split pristine creation validation from normal ongoing project verification.
- Made ongoing verification resolve current profiles and reject unknown
  specialists or unreviewed MCP authority state.
- Scoped generated tests to the selected archetype while retaining the full
  reference-lab evidence matrix.

## Blockers

- The draft pull request still requires human inspection and task approval;
  evaluator verdicts do not approve or merge it.

## Verification status

- 47 focused generator/router/design/MCP tests pass.
- The independent authority/profile suite passes 45 tests.
- Web model tests, typecheck, and production build pass.
- 21 Playwright interaction/accessibility checks pass; one intentional
  desktop skip covers a mobile-only overflow assertion.
- 18 macOS reference-lab visual candidates were generated successfully.
- A generated product project installs from the reviewed lockfile, builds,
  passes 15 selected-archetype browser checks with seven intentional irrelevant
  skips, and passes its complete downstream verification.
- Independent product-design and adversarial QA evaluations pass.
- Independent security/authority review passes at exact code head `b6e364f`.
- PR policy, repository verification, and web-quality checks pass.

## Exact next action

Use the repository collaboration workflow for the active work item and preserve
human authority over visual-baseline acceptance and release decisions.

## Relevant files

- `.agentic/experience.json`
- `scripts/project_generator.py`
- `scripts/next_action.py`
- `apps/web/app/product-lab.tsx`
- `apps/web/tests/`
- `docs/50-evals/evidence/T-043/`

Keep this concise enough to read in under two minutes.
