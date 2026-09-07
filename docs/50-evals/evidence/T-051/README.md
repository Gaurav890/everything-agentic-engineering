# T-051 — Guided Project Studio evidence

Status: implementation and independent review pass. Human task review, merge,
and real-newcomer outcome measurement remain separate.

## What was proved

- `./agentic start` is the single public create-or-resume doorway in both the
  starter and every generated profile. `setup create`, `next`, `journey`, and
  specialist commands remain available as progressive-disclosure controls.
- The guided interview asks for the idea, audience, promise, and first useful
  result before destination and implementation-route mechanics. The suggested
  route remains editable.
- The generated Project Studio shows Shape → Direction → Build → Proof while
  deriving its current stage, exact next decision, and manual handoff from the
  canonical six-stage journey. Research, token compilation, implementation,
  verification, and review states do not rely on UI-local guesses.
- The copied handoff is research-aware and current. It does not collect a key,
  install or activate a client/plugin/MCP, contact a provider, launch a client,
  approve scope or design, deploy, or merge.
- Every progress step exposes complete/active/waiting state visually and to
  assistive technology. Post-design token compilation remains Direction;
  implemented work awaiting evidence or review remains Proof.
- Generator inputs reject terminal control characters before any plan is
  displayed. Server-side Studio inspection requires a canonical project-
  contained, non-symlinked script and uses pinned executables, a closed
  environment, ignored stdin, and bounded execution.

## Running-product evidence

A fresh research-enabled web product, `Decision Lens`, was generated from
implementation commit `9114f3f`.
Its locked dependencies were restored offline with zero downloads, then
`./agentic verify web` passed:

- production build;
- generated-project lint, typecheck, and unit checks;
- the research-aware canonical handoff;
- normal and empty Studio states;
- clipboard loading, success, and manual error fallback;
- keyboard focus and skip navigation;
- accessible progress-state names;
- desktop and mobile responsive/overflow checks;
- reduced-motion behavior; and
- automated accessibility checks.

Ten applicable Project Studio browser cases passed across desktop and mobile.
Twenty-six unrelated archetype cases were intentionally skipped by profile.
The source Studio was also manually inspected at desktop and 390px width with
no horizontal overflow. These checks do not claim assistive-technology user
testing or real-newcomer success.

## Deterministic verification

- 95 focused generator, handoff, journey, next-action, and command-router tests
  pass.
- 11 web unit tests pass, including adversarial ancestor-symlink rejection and
  proof that unrelated parent environment values do not reach Studio inspection.
- A real mobile-review regression proves that Proof takes precedence over
  still-active native design planning once the canonical next action is review.
- Clean-checkout release smoke passes through the public `./agentic start`
  doorway.
- The complete ten-stage repository verification passes.

## Boundary

This task improves the self-serve journey and its evidence, not the quality of
an unseen future product. A real five-person newcomer pilot and human review
remain required before claiming that unfamiliar users succeed unaided. No
credential, external capability, model/provider integration, production
service, deployment, approval, or merge authority was added.
