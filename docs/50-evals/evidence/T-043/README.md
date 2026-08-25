# T-043 guided product studio evidence

Status: In review

## Product contract

- The public path is `./agentic setup create`.
- Five product decisions plus destination lead to one concise plan and one
  confirmation.
- Generated projects expose exactly one next action through `./agentic next`.
- Web and mobile application profiles cannot omit the design-critical base.
- Generated web projects expose and test only their selected archetype.
- Web/mobile projects carry the reviewed dependency lockfile; core projects do
  not receive irrelevant package state.

## Running-product evidence

- Portfolio, product, and agentic-product use complete, compatible identities
  and content architectures in the starter reference lab.
- Agentic review discloses evidence completeness and consequence, keeps approval
  locked until proof is ready, and supports approve, reject, cancel, and retry.
- The desktop direction lab occupies document flow; mobile uses a collapsed,
  focus-managed, escape-dismissible control.
- Playwright covers keyboard use, clipboard success/failure, agent review,
  occlusion, axe accessibility, mobile overflow, and reduced motion.
- `apps/web/tests/visual.spec.ts-snapshots/` contains the reference-lab
  three-archetype × three-direction × desktop/mobile candidates. Linux images
  remain subject to the existing human baseline-review workflow.

## Verification recorded before finalization

```text
python3 -m unittest tests.test_next_action tests.test_project_generator \
  tests.test_agentic_cli tests.test_design_engine
PASS — 38 tests

pnpm --filter @everything-agentic/web test
PASS — 4 tests

pnpm --filter @everything-agentic/web typecheck
PASS

pnpm --filter @everything-agentic/web build
PASS

pnpm --filter @everything-agentic/web test:e2e
PASS — 21 passed, 1 intentional skip

pnpm --filter @everything-agentic/web test:visual:update
PASS — 18 candidate captures

GitHub Web quality run 32819337421
PASS — Linux build, interaction/accessibility suite, 18 baseline candidates,
and artifact upload

Generated product project (fresh temporary destination):
pnpm install --offline --frozen-lockfile
PASS — 34 packages reused, 0 downloaded

pnpm build
PASS

pnpm test:e2e
PASS — 15 passed, 7 intentional irrelevant-archetype skips

./agentic verify full
PASS
```

## Independent evaluation

- The independent product-design critic certified the complete running
  experience after identity, evidence controls, responsive occlusion, content,
  and cross-direction differentiation were corrected.
- The independent adversarial QA evaluator passed the generator, validation,
  next-action, archetype scoping, reduced-motion, and downstream lifecycle
  contracts after all release blockers were resolved.
- The branch contains 18 Linux candidates generated from the final polished
  head. They remain subject to human inspection in the pull request before
  landing; committing candidates to the branch is not release approval.

## Authority boundary

No dependency, external skill, plugin, MCP, credential, backend, runtime, Git
repository, deployment, production surface, design direction, PR approval, or
merge is created or enabled by the guided flow.
