# T-045 — First-project success evidence

Date: 2026-08-27
Implementation: `31df6f4b1118ee372554d6de77556c3e0e22de18`

Browser and visual execution used `2b68d27393c8327019aa405e0105a728fbc229c1`;
the final follow-up only suppresses interpreter bytecode caching during
read-only inspection and adds its real-command regression. It changes no
rendering or test selection. Independent review covered both deltas.

## What changed

The read-only guide continues from approved tokens into feature planning,
dependency-aware work, blockers, human review, and post-merge guidance. Current
profiles control routing. Generated web projects receive a personalized first
feature brief; multiple workstreams can be selected explicitly.

Verification now distinguishes repository checks, running-web checks, and
visual comparisons. New acceptance-test files participate in the web suite;
`@visual` tests run separately. Missing tools or screenshots cannot become
passing evidence. No application UI, visual token, or approved screenshot changed.

## Executed checks

These are recorded tool-console results, not fabricated user-study results.

| Check | Observed result |
|---|---|
| Focused continuation, verification, generator, and command tests | 56 passed: 16 + 9 + 23 + 8 |
| `./agentic verify full` | All ten repository stages, package lint/types/unit tests passed |
| `./agentic verify web` at `2b68d27` | Repository checks and production build passed; 25 browser cases passed, one intentional viewport skip |
| `./agentic verify visual` | Production build and 24 macOS comparisons passed; no baselines updated |
| `./agentic release smoke` on the implementation commit | Fresh checkout plus guided/web/mobile/core/enterprise generation and offline contract validation passed |
| Generated enterprise `./agentic verify web` with an extra acceptance file | 21 browser cases passed, seven irrelevant-archetype/viewport skips; includes two executions of the new file |
| Generated enterprise `./agentic verify visual` without baselines | Correctly blocked before build/test with explicit review instructions; no baseline created |
| `git diff --check` | Passed |

The browser runs use the existing locally installed Chromium and desktop/mobile
web viewports. They do not prove native mobile behavior. The initial sandboxed
attempt could not launch Chromium because macOS denied its process port; the
same local checks passed after permission to run outside that sandbox. No
repository security gate was weakened.

Local execution used Node.js 25.2.1, Python 3.9.6, and pnpm 9.15.9. The documented
supported setup recommends Python 3.11+ and the tested CI Node.js 22 baseline;
local success on another version does not expand that support promise. Live
Linux CI status must be checked on the PR rather than inferred from this report.

## Fresh-project reproduction

Generate a separate web project named `Northline Review`, archetype
`enterprise-workflow`, audience `operations reviewers`, promise
`Resolve a request with confidence.`, business object `access request`,
multi-tenant, dual-control, confidential. Do not approve its design or initialize
Git merely for this check.

1. Confirm `next` requests local dependencies.
2. Restore the reviewed lockfile. This run reused 34 packages from the source
   checkout's local package cache, with scripts disabled and zero downloads.
   An initial attempt against a different empty cache stopped in offline mode;
   no network fallback occurred.
3. Confirm `next` now asks to compare live directions, not to mark a task done.
4. Add a temporary `apps/web/tests/first-feature.spec.ts` acceptance fixture:

   ```ts
   import { expect, test } from "@playwright/test";

   test("new acceptance files join the web verification suite", async ({ page }) => {
     await page.goto("/");
     await expect(page.locator("h1")).toHaveText("Resolve a request with confidence.");
   });
   ```

5. Run `./agentic verify web`. The new file is discovered in both viewports.
6. Run `./agentic verify visual`. It must refuse to invent missing baselines.

This fixture proves extensible test discovery against the generated custom
promise. It is not evidence that a newcomer invented or delivered a new feature.

## Acceptance and limitations

- AC-001: selected-surface generation, personalized brief, clean-checkout smoke.
- AC-004: inherited browser/visual regression, independent evaluation, unchanged
  human approval boundary; no new visual design approval claimed.
- AC-005: lifecycle and malformed-state regressions, feature-test discovery,
  scoped evidence, and the newcomer pilot protocol.

Real newcomer success remains unmeasured. Manual assistive-technology testing,
production security certification, native app implementation, production
adapters, deployment, public demo hosting, and launch promotion are outside this
change. The pilot protocol is a future launch gate, not completed research.
