# Progress log

### 2026-08-27 — T-046

**Requirements:** FR-001, FR-003, FR-005, FR-006
**Acceptance:** AC-001, AC-004, AC-005, AC-006

Implemented product-owned onboarding context, consent-based native/manual
handoff, open-ended custom/existing-brand previews, and evidence-bound design
approval. The setup workspace shows saved intent and a clear continuation
without pretending to be the finished product. Custom generation no longer
assigns a default design personality as a user answer.

Local evidence includes 61 focused Python tests, nine web contract tests,
16 disposable-project browser cases, 25 reference browser passes and 24
unchanged visual comparisons. Independent product/security reviews found
blockers that were fixed and rechecked. Recovery reloads repaired context;
fixtures exercise empty, pending, failure and interactive preview states.
Clean-checkout release smoke passed from checkpoint `23495cc`, including guided
creation and the web, enterprise, mobile and core profiles.
See `docs/50-evals/evidence/T-046/` for scope and remaining checks.

No existing downstream project was overwritten. Native account sign-in,
unattended design generation, production readiness and newcomer outcomes
remain unclaimed. Human task approval and merge remain separate.

## 2026-08-27 — T-044 independent reviews passed

- Product-quality/adversarial QA and security/authority independently returned
  PASS for `b0a9843ca0f9b9bf6517c1fefb25b4d5d20eda27` after review corrections.
- Service-owned clocks reject caller-authored audit chronology. Stale refresh
  callbacks cannot restore previous actor data or overwrite newer outcomes.
- Generated browser assertions honor custom promises, business-object labels,
  and the selected approval model instead of assuming starter defaults.
- Full repository verification, 27 generator/next-action tests, 7 domain + 5
  API + 5 web model tests, source build, 25 browser cases (one expected skip),
  24 visual comparisons, and clean-checkout release smoke passed.
- Independent fresh policy-gated and single-review projects each built and
  passed 19 browser cases (seven expected skips) with custom copy and business
  objects. Offline locked restores reused 34 packages and downloaded none.
- Exact-head review evidence and production-adapter boundaries are recorded in
  `docs/50-evals/evidence/T-044/`. Current PR/merge state remains GitHub-owned.

## 2026-08-26 — T-044 independent-review remediation

- Independent product/QA and security reviewers blocked the first reviewed
  head on incomplete request submission, decorative approval-model selection,
  same-tenant over-broad reads, and caller-forgeable audit attribution.
- The service now scopes requester, reviewer, auditor, and administrator reads;
  rejects unknown roles; constructs trusted creation and evidence events; and
  resets caller-supplied evidence/policy state before persistence.
- The selected single-review, dual-control, or policy-gated model now changes
  executable reviewer and policy requirements.
- The running product now demonstrates evidence checks, submission, rejection,
  requested changes, resubmission, approval, cancellation, tenant/audit hiding,
  and safe recovery.
- Focused domain, API, generator, model, build, browser, accessibility, and
  existing visual-baseline checks pass. Exact-head clean-checkout verification
  and independent re-review remain pending before task finalization.

## 2026-08-24 — T-043 guided product studio

- Added progressive, archetype-aware downstream project creation and exactly
  one routed next action.
- Replaced portfolio leakage in product/agentic previews with complete fixtures
  and selected-archetype downstream scope.
- Added real evidence review, consequence, approve/reject/cancel, partial, and
  retry behavior to the agentic reference experience.
- Added responsive non-obscuring direction controls and the full reference-lab
  desktop/mobile visual matrix.
- Hardened generated-project validation for real post-install, Git, approved-
  design, task, JSON-array, and single-document automation workflows.
- Ongoing verification now resolves current profiles and fails closed on
  unknown/profile-incompatible specialists or unreviewed MCP configuration.
- Focused generator/design and 45 authority/profile tests, web build/typecheck,
  21 Playwright checks, full verification, release smoke, and all three PR
  checks pass. Independent design, adversarial QA, and security reviews pass.

Append-only verified history.

## Entry template

### YYYY-MM-DD — T-XXX

**Requirements:** FR-XXX  
**Acceptance:** AC-XXX  
**Outcome:** DONE | PARTIAL | BLOCKED

**Change**

**Evidence**

**Commit/PR**

**Remaining risk**

### 2026-07-25 — T-001

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Added the phase-based product-design router and local phase contracts; demoted
Anthropic frontend-design to optional supplementary intelligence; added the
product-specific design-system contract and DTCG-compatible token scaffold.

**Evidence**

- All project-local skills pass `quick_validate.py`.
- `./scripts/verify.sh full` passes.
- `git diff --check` passes.

**Commit/PR**

Merged through PR #2.

**Remaining risk**

The scaffold has no platform token build/export pipeline yet. External phase
skills remain optional installations and must be reviewed before use.

### 2026-07-25 — T-005

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Added a machine-readable project manifest, composable profiles, resource
provenance, deterministic resolution/conflict checks, drift reporting, and
non-destructive profile previews/selections.

**Evidence**

- Web-only and web+mobile resolution tested.
- Supabase/Convex conflict fails closed.
- Unknown profiles fail closed.
- Selection without confirmation is refused.
- Isolated confirmed selection changes only the manifest.
- `./scripts/verify.sh full` passes.

**Commit/PR**

Merged through PR #6.

**Remaining risk**

External installation and cleanup remain intentionally advisory. No package,
plugin, MCP, or user file is automatically added or removed.

### 2026-07-25 — T-006

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Added open-source governance files, guided non-destructive initialization,
profile-engine unit tests, CSS/TypeScript/React Native token generation,
security-hook tests, local-link validation, and machine-checkable evidence
bundles.

**Evidence**

- 16 unit and integration tests pass.
- 95 DTCG tokens and 45 aliases validate.
- Generated web and native outputs pass freshness checks.
- Full repository verification passes all ten stages.

**Commit/PR**

Merged through PR #7.

**Remaining risk**

Application-specific browser, accessibility, performance, and visual regression
checks activate only after a real showcase or product application exists.

### 2026-07-25 — T-007

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Built Signalroom, a distinctive agent-operations reference product using the
complete design router: brief, user needs, benchmark, UX strategy, interaction
model, design contract, token-driven implementation, responsive states,
browser interaction review, accessibility gate, evidence bundle, independent
critique, and post-critique fixes.

**Evidence**

- Production Next.js build passes.
- Lint, typecheck, model tests, and full repository verification pass.
- Approval and pause/resume behavior verified in the running product.
- Desktop, mobile, loading, empty, and error evidence captured.
- Evidence bundle passes machine validation.
- Playwright plus axe runs as a required GitHub Actions job.

**Commit/PR**

Merged through PR #8.

**Remaining risk**

The local macOS sandbox blocks a second headless Chromium process, so the
automated browser/axe suite is executed by GitHub Actions. Signalroom remains a
frontend reference, not a production backend.
### 2026-07-25 — T-008

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Added safe presets for common web, mobile, full-stack, research, and
harness-only starting points. Initializer previews now make active and inactive
profiles and capabilities explicit, including external setup that requires
separate review.

**Evidence**

- Eight initializer tests pass.
- Five profile-engine tests pass.
- Web-only preview explicitly keeps mobile capabilities inactive.
- Full repository verification passes all ten stages.

**Commit/PR**

Merged through PR #9.

**Remaining risk**

Inactive template inventory is deliberately retained so profile selection stays
reversible. Physical cleanup remains a separate explicit human decision.

### 2026-07-25 — T-009

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Added a read-only task planner and confirmation-gated task workspace launcher
with dependency, active-profile, specialist-routing, file-ownership,
verification, parallel-work, and stale-base gates.

**Evidence**

- Nine task-engine tests pass.
- Starting without `--yes` leaves task state unchanged.
- Incomplete dependencies and overlapping ownership fail closed.
- Independent active work recommends an isolated worktree.
- Full repository verification passes all ten stages.

**Commit/PR**

Merged through PR #10.

**Remaining risk**

The launcher prepares branches and worktrees only. GitHub Issue synchronization
and autonomous implementation remain intentionally out of scope.

### 2026-07-25 — T-010

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Prepared the first public preview as a human-gated release candidate: semantic
version and changelog, curated release notes, compatibility and limitation
statements, a release runbook, clean-checkout onboarding validation, a
review-first GitHub release workflow, README quick-start visual, a 60-second
demo script, and launch copy.

**Evidence**

- Release contract validation covers version, tag, changelog, notes, README,
  and compatibility.
- Clean-checkout smoke test exercises bootstrap, initializer preview, profile
  resolution, profile doctor, and tracked-file cleanliness.
- Full repository verification is required before packaging.
- Public publishing is disabled by default and refuses existing releases/tags.

**Commit/PR**

Merged through PR #11 and published as `v0.1.0` from commit `991c70c`.

**Remaining risk**

The demo recording, GitHub topics, social preview upload, final artifact review,
tag creation, public release, and announcements remain explicit maintainer
actions after this branch is merged.

### 2026-07-25 — T-011

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome AT FINAL VERIFICATION:** DONE ON TASK BRANCH

**Change**

Created a 1280×640 social-preview asset aligned with the Signalroom visual
language and prepared accurate repository description/topic metadata for the
public launch surface.

Applied the description and ten focused topics to the public repository and
uploaded the social preview through GitHub's repository settings.

**Evidence**

- Exact project name and launch tagline visually inspected.
- 1280×640 JPEG is 131 KB and suitable for GitHub social cards.
- The system path communicates durable context, product design, coordinated
  specialist agents, verification gates, and shipping.
- GitHub's social-preview menu exposes `Remove image`, confirming the upload.
- Full repository verification passes.

**Commit/PR**

Implementation commit `7a74be4` merged through PR #12. Follow-up PR #13 records
the final handoff state.

**Remaining risk**

GitHub caches social preview images; shared links may take time to refresh after
the settings upload.

### 2026-07-25 — T-012

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Replaced the single-video documentation approach with five focused README GIFs
embedded beside the capabilities they explain.

**Evidence**

- The project-profile GIF runs the real non-destructive initializer preview.
- The task-planning GIF runs the real planner against Signalroom task T-007.
- The approval GIF exercises pause, resume, and protected-read approval in the
  running Signalroom app.
- The UI-state GIF exercises normal, loading, empty, and error states.
- The verification GIF runs the full repository verification suite.
- Individual GIF sizes range from 122 KB to 542 KB.

**Commit/PR**

Branch: `feat/T-012-readme-demo-gifs`; commit and PR pending.

**Remaining risk**

GitHub may defer animation for users with reduced-motion preferences; the first
frame of every GIF remains meaningful and labeled.

### 2026-08-03 — T-015

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Added an adaptive product-design intake, durable brief and direction artifacts,
and an explicit human approval gate before design-system or canonical token
changes. Reworked color theming around stable semantic roles, added mode-aware
component resolution, theme parity and WCAG contrast validation, and generated
an inspectable light/dark token specimen.

**Evidence**

- The new `design-intake` skill passes project skill validation.
- Nine token tests cover generation, parity, light/dark resolution, contrast,
  invalid theme coupling, and invalid aliases.
- The token specimen was inspected at desktop and 390px mobile widths with no
  horizontal overflow.
- Full repository verification passes.

**Commit/PR**

Commit `2de0e01`; draft PR #16.

**Remaining risk**

Generated directions still require product-specific human taste and approval.
High-contrast mode is documented but not generated until a project activates
that requirement. External design and Figma tools remain optional inputs.

### 2026-08-04 — T-016

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Corrected version-sensitive Claude Code nesting guidance and documented the
credential-file masking and permission-analysis hardening introduced in Claude
Code 2.1.221. Kept the recommendation advisory and version-qualified: no
credentials, credential paths, sandbox settings, network rules, dependencies,
plugins, or MCP servers were added or enabled.

**Evidence**

- Official Claude Code releases and changelog confirm that 2.1.217 initially
  restricted nesting, 2.1.219 changed the default nesting depth to three, and
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` restores no nesting.
- The 2.1.221 release documents Linux/WSL credential masking, macOS deny
  fallback, and a zsh permission-check bypass fix.
- Existing Git and background-session policy already matches the upstream
  guidance, so no workflow behavior changed.
- Full repository verification passes all ten stages.

**Commit/PR**

Commit `acf9b83`; draft PR #17.

**Remaining risk**

Public documentation does not yet expose a complete stable schema for declaring
masked credential paths. A maintainer must review any future settings change;
macOS users should expect deny behavior instead of transparent masking.

### 2026-08-04 — T-017

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Reconciled T-011, T-012, T-013, and T-016 with their merged pull requests and
added a deterministic PR policy check that requires the task named in a
non-draft PR title to be `done` before final review or merge.

**Evidence**

- Merged PRs #12/#13, #14, #15, and #17 match the reconciled tasks.
- The new check accepts known `done` tasks.
- The new check rejects missing tasks and tasks that have not completed the
  documented `finish-task.sh` → `prepare-merge.sh` lifecycle.
- Draft PRs remain available for early collaboration without a false failure.
- Full repository verification passes throughout review and final branch-state
  preparation.

**Commit/PR**

Commit `dfe5aeb`; draft PR #18.

**Remaining risk**

The repository must keep the PR policy check required on `main`; otherwise the
script remains advisory. Emergency bypasses still depend on protected-branch
and ruleset administration.

### 2026-08-05 — T-018

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Recorded material agent-runtime security changes from Claude Code 2.1.222 and
Codex 0.146.1, then added narrow compatibility and threat-model guidance without
changing either runtime or any model, permission, hook, credential, sandbox,
network, or Remote Control setting.

**Evidence**

- Claude Code 2.1.222 first-party release notes document worktree/main-checkout
  isolation, background-task hook restriction, cross-session message
  classification, and Remote Control setting fixes.
- Codex 0.146.1 stable release notes and its first-party implementation PR
  document safer cyber-specialized model review defaults.
- The current Codex manual confirms that automatic review swaps the reviewer;
  it does not grant permissions or expand sandbox boundaries.
- Both findings were deduplicated against the learning ledger.
- Full repository verification passes.

**Commit/PR**

Commit `1745e31`; draft PR #19.

**Remaining risk**

Claude's release notes do not publish a CVE or affected-version floor. Codex's
behavior depends on model metadata and client support. Runtime upgrades and all
permission or automatic-review changes remain human decisions.
### 2026-08-07 — T-021

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Added a native Codex adapter that shares one canonical skill catalog with
Claude, uses trusted and authority-neutral project configuration, reuses the
reviewed safety scripts through Codex hooks, packages the catalog through a
skills-only plugin manifest, and documents safe multi-terminal worktree
operation.

**Evidence**

- Official skill validation passes for `codex-adapter`.
- Official plugin validation passes for the repository package.
- Six adapter tests cover shared skill discovery, authority-sensitive config,
  hook wiring, plugin scope, metadata, and runtime-independent doctor behavior.
- The secret scanner handles both Claude edit/write payloads and Codex
  `apply_patch` payloads.
- Default doctor passes and reports the installed 0.146.0 runtime; strict mode
  correctly rejects it as below the 0.147.0 plugin baseline.
- Full repository verification passes after restoring locked dependencies in
  the isolated worktree.
- PR #22 received human approval and merged before the final task-state commit.
- The final merge-readiness gate passed, and this narrow follow-up records
  T-021 as `done` on authoritative `main` without changing implementation.

**Commit/PR**

Implementation commit `40192a1`; merged PR #22; follow-up state reconciliation
requires human-reviewed merge.

**Remaining risk**

Codex-specific subagent role adapters and plugin marketplace publication are
not included. Runtime upgrades and all external capability or permission
changes remain human decisions.

### 2026-08-07 — T-022

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Activated GitHub `main` protection and delivered a native Codex role pack for
bounded product, architecture, research, design, security, QA, and integration
analysis. The roles remain read-only and do not replace worktree isolation for
parallel implementation.

**Evidence**

- Live GitHub protection requires `verify` and `policy`, an up-to-date branch,
  resolved conversations, linear history, and applies to administrators.
- Force pushes and branch deletion are disabled for `main`.
- Official Codex custom-agent documentation requires `name`, `description`,
  and `developer_instructions` and supports project-scoped `.codex/agents/`
  files and read-only sandbox overrides.
- The dependency-free validator accepts all seven reviewed role files and
  rejects unreviewed fields or writable sandboxes.
- Nine Codex adapter tests pass.
- Official skill and plugin validators pass.
- Full repository verification passes all ten stages.
- Human approval was recorded and the repository merge-readiness gate passed,
  moving T-022 from `review` to `done` on the feature branch.
- PR #24 passed the protected `verify` and `policy` checks and merged into
  authoritative `main` as `7906e62`.

**Commit/PR**

Merged through PR #24 as `7906e62`; implementation commit `c803398` and final
merge-preparation commit `5b80b57` remain visible in the PR history.

**Remaining risk**

Project roles inherit capabilities already approved for the parent session.
They add no external capability themselves. Independent approving reviews
remain at zero until another maintainer can participate without blocking work.

### 2026-08-07 — T-023

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** DONE

**Change**

Added a deterministic GitHub Issue ↔ task ↔ PR contract. New unfinished tasks
must record required issue references or a reviewed issue-free reason. The task
planner determines whether a PR should relate to or close each issue, the PR
policy validates the contract offline, and an optional live command reports
GitHub drift using read-only operations.

**Evidence**

- Twelve synchronization tests cover historical compatibility, required and
  issue-free tracking, title/body mismatches, exact multi-issue references,
  multi-task closure safety, reviewed fixtures, and read-only live status.
- Eleven task-launcher tests pass, including tracking-contract blocking and
  issue-closure guidance.
- `task-sync.sh validate-ledger` accepts all 22 ledger tasks.
- Post-merge status confirms issue #26 closed through the merged PR.
- GitHub workflow and issue-form YAML parse successfully.
- Local documentation links pass.
- `./scripts/verify.sh full` passes all ten stages, including Showcase lint,
  typecheck, and tests.

**Commit/PR**

Merged through PR #27 as `2dc1b63`; implementation commit `cfb25bb` and
merge-preparation commit `5604470` remain visible in the PR history.

**Remaining risk**

Live status depends on an authenticated GitHub CLI but is optional. Required CI
validation is offline. The automation deliberately cannot comment, label,
assign, close, approve, merge, or change repository/task state.

### 2026-08-07 — T-024

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome AT FINAL VERIFICATION:** DONE ON TASK BRANCH

**Change**

Added deterministic post-merge closeout. The command reads the live default
branch, merged PR, linked issues, volatile handoff sections, and local
branch/worktree state. It reports findings and optional cleanup commands but
cannot edit GitHub, durable state, branches, or worktrees.

**Evidence**

- The first live T-023 run verified PR #27, closed issue #26, and `done` on
  authoritative `main`, then detected all three stale volatile handoff claims.
- The same run identified the clean managed T-023 worktree and printed cleanup
  commands without executing them.
- Twelve closeout tests cover remote-main truth, merged PR ambiguity, issue
  closure, issue-free and historical tasks, missing CLI behavior, stale
  handoff detection, dirty/unmanaged worktree preservation, and read-only
  command safety.
- The offline handoff guard reports no transient task lifecycle claims.
- All 23 tasks pass the GitHub tracking contract.
- `./scripts/verify.sh full` passes all ten stages, including Showcase lint,
  typecheck, and tests.

**Commit/PR**

Implementation commit `22a9625`. Resolve the current lifecycle with
`task-closeout.sh T-024`; do not duplicate predicted PR state in this
historical record.

**Remaining risk**

Live closeout requires authenticated read access through `gh`. Cleanup commands
remain recommendations and require independent human target verification.

### 2026-08-09 — T-025

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** REVIEW

**Change**

Added one machine-readable runtime compatibility policy for Claude Code and
Codex, plus a dependency-free read-only doctor with advisory, strict,
runtime-specific, and JSON modes. Codex verification now reuses that canonical
policy. Optional runtime capabilities remain disabled and explicitly require
human approval.

**Evidence**

- The manifest records primary release sources and tested minimums: Claude Code
  2.1.225 and Codex 0.147.0.
- Seven runtime tests cover policy validation, stable versus prerelease
  comparison, advisory and strict behavior, JSON stability, and fail-closed
  optional-capability governance.
- Ten Codex adapter tests confirm the existing authority boundary and shared
  policy reuse.
- The doctor reports the inspected developer runtimes below recommendation
  without installing, upgrading, or enabling anything.
- Simulated strict checks reject older versions and accept the recommended
  stable versions.
- Full repository verification passes all ten stages, including 24-task
  tracking validation, security hooks, design tokens, Showcase lint,
  typecheck, and tests.
- Maintainer inspection completed before the final preparation gate wrote
  `done` on the task branch.

**Commit/PR**

Implementation commit `15f82d1`; PR #31; issue #30 owns the human discussion.

**Remaining risk**

The inspected developer runtimes remain below recommendation until a human
chooses to upgrade them. Self-hosted and cross-session Claude execution,
archive plugin sources, Codex portable plugin installation, MCP 2026-07-28,
and automatically reviewed approvals need separate threat models and are not
enabled by this change.

### 2026-08-09 — T-026

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Added one bounded PR finalizer around the existing task and verification
gates. After direct human approval it can prepare and commit only the task
ledger, push the current task branch, mark a draft ready, and wait for required
checks. Human-facing policy errors and collaboration docs now say what to do
without exposing manual `TASKS.jsonl` bookkeeping.

**Evidence**

- Six finalization tests cover dry-run no-mutation, clean-worktree enforcement,
  ledger-only staging, already-ready recovery, already-prepared idempotence,
  and absence of approval or merge commands.
- Twelve GitHub task-sync tests pass, including the plain-language recovery
  instruction for a prematurely ready PR.
- Shell syntax, Python compilation, task tracking, and local links pass.
- `./scripts/verify.sh full` passes all ten stages across 25 tracked tasks,
  design tokens, security hooks, runtime/Codex policy, Showcase lint,
  typecheck, and tests.

**Authority boundary**

Issue #32 owns the human discussion. The finalizer requires a direct human
approval for the named task. It cannot approve, merge, push the protected
branch, change permissions, stage unrelated files, deploy, or treat web and
issue content as authorization.

### 2026-08-09 — T-027

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Added one registry-backed `./agentic` interface for contributor workflows.
Twenty-three supported commands are grouped by purpose, while every shell file
is explicitly classified as public, internal, compatibility, or security hook.
Primary onboarding and collaboration documentation now teaches the unified
interface. Existing direct script paths remain compatible.

**Evidence**

- Eight command-interface tests cover complete shell inventory, unique public
  mappings, internal and hook isolation, grouped help, JSON discovery, exact
  argument forwarding, and executable entry-point behavior.
- Every one of the repository's 30 shell files is classified exactly once.
- The release smoke test exercises the unified interface in a disposable clean
  checkout while preserving existing compatibility paths.
- Full repository verification passes all ten stages across 26 tracked tasks,
  command registry checks, design tokens, security hooks, runtime/Codex policy,
  local documentation links, Showcase lint, typecheck, and tests.

**Authority boundary**

Issue #34 owns the human discussion. This phase does not delete or relocate
scripts, bypass security hooks, install external capabilities, widen runtime
authority, deploy, approve, or merge a pull request. Any later script removal
requires a separately reviewed, release-backed deprecation decision.

### 2026-08-10 — T-028

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Made the human-approved PR finalizer resumable across its real interruption
points. It now recognizes only the exact task-ledger `review` to `done`
transition it prepares, re-runs full verification before committing recovered
state, and safely resumes already-committed or already-ready checkpoints. It
also waits a bounded 55 seconds for GitHub to register checks before reporting
a clear retry instead of failing immediately on `no checks reported`.

**Evidence**

- Twelve finalization tests cover clean execution, dry-run behavior, staged and
  unstaged recovery, unrelated worktree and ledger rejection, delayed and
  missing check registration, ready-state recovery, idempotent prepared state,
  and absence of approval or merge commands.
- Twenty-four combined finalizer and task-policy tests pass.
- Full repository verification passes all ten stages across 27 tracked tasks,
  security hooks, runtime/Codex policy, design tokens, local links, Showcase
  lint, typecheck, and model tests.
- Locked worktree dependencies were restored offline with zero downloads.

**Authority boundary**

Issue #36 owns the human discussion. Recovery does not infer approval, accept
general dirty state, stage unrelated files, push `main`, approve, merge,
deploy, widen permissions, or turn check absence into success. The maintainer
still reviews first and performs the final squash merge separately.

### 2026-08-10 — T-029

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Reviewed all ten skills in Emil Kowalski's design-engineering repository and
integrated them as a profile-aware external craft layer. Added a local
`design-engineering-quality` router, exact phase/trigger metadata, a pinned
reviewed installer for Claude Code and Codex, non-mutating install preview,
purpose-first motion gates, and explicit-only controls for live variants,
library selection, and strict animation review. Anthropic `frontend-design`
remains secondary/opt-in and is no longer the starting implementation skill or
part of the default external install.

**Evidence**

- The manifest covers each upstream skill exactly once with source, license,
  reviewed commit, phase, trigger, and activation policy.
- Profile tests prove the collection is active for `design-critical` and absent
  from a web-only profile.
- Installer preview proves web guidance and the pinned Emil collection are
  selected while inactive mobile guidance is omitted.
- The new local skill passes the platform skill validator.
- Full repository verification passes all ten stages across 28 tracked tasks,
  28 shared local skills, profiles, tokens, security hooks, runtime/Codex
  policy, local links, Showcase lint, typecheck, and tests.

**Authority boundary**

Issue #38 owns the human discussion. Upstream code was inspected as untrusted
data and was not installed, executed, or copied into this repository during
implementation. Profile selection never installs skills. The explicit setup
command uses the reviewed commit, and future updates require a new review and
pull request. The project brief, approved design system, tokens, accessibility,
Playwright evidence, independent evaluator, and human merge remain authoritative.

### 2026-08-10 — T-030

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Added a deterministic specialist capability broker backed by 14 curated Agency
Agents contracts. Task planning now selects only capabilities justified by
task evidence and active profiles, preserves one accountable local owner,
declares required deliverables and independent evaluators, and records explicit
risk-review gates. Contributors can discover the full upstream roster while
optionally activating only a reviewed local contract.

**Evidence**

- Broker tests cover pinned provenance, MIT licensing, safe policy, security,
  payment, design, accessibility, i18n, no-match, explicit-routing, JSON,
  reversible activation, fail-closed doctor, and no external execution.
- Task-planner and command-registry tests verify operational routing through
  the unified `./agentic` interface.
- `specialist-router` passes the platform skill validator.
- Full repository verification passes all ten stages across 29 tracked tasks,
  29 shared local skills, profiles, tokens, security hooks, runtime/Codex
  policy, local links, Showcase lint, typecheck, and tests.

**Authority boundary**

Issue #40 owns the human discussion. The broker does not vendor, install, or
execute Agency Agents; select a model; add tools or credentials; widen network
or sandbox permissions; deploy; approve; or merge. Activation changes only the
project manifest. Prime Agent runtime integration remains a separate future
architecture and security decision.

### 2026-08-13 — T-034

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Added an additive Agent Plugins 1.0 portable, skills-only core through root
`plugin.json` and the existing contained `skills/` catalog. Kept
`.codex-plugin/plugin.json` as a separately validated Codex-native
compatibility surface. Added a read-only package doctor, closed-manifest and
path-containment validation, negative fixtures, version-parity checks, command
discovery, bootstrap integration, and a migration/security guide.

**Evidence**

- Seven portable-plugin tests cover the valid repository, closed manifest,
  package-version parity, Codex-native separation, project-MCP separation,
  escaping skill symlinks, and gated portable MCP entries.
- Eleven Codex adapter tests verify the native package remains valid and cannot
  drift from the portable package name or version.
- `./agentic doctor plugin --json` returns machine-readable inventory for 30
  contained skills and reports no packaged MCP configuration.
- `./agentic verify full` passes all ten verification stages, including command
  registry validation, design tokens, security hooks, runtime/Codex policy,
  local links, release checks, Showcase lint/typecheck, and tests.
- Locked dependencies were restored from the local pnpm cache with zero
  downloads before the application checks.

**Authority boundary**

This is packaging and validation only. It does not publish, install, enable,
execute, authenticate, add credentials, configure portable MCP servers, widen
runtime or sandbox authority, approve, or merge. Root `.mcp.json` remains a
project configuration, not a portable package. A separate compatibility review
is required before any portable MCP server entry is added. The GitHub connector
could not create a tracking issue, so the complete bounded issue-free reason is
recorded in the task and must be reproduced exactly in the PR.

### 2026-08-14 — T-035

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Added a machine-readable compatibility policy and read-only doctor for the
Perplexity, Firecrawl, and Playwright MCP servers across Agent Plugins 1.0,
Claude Code, and Codex. Portable packaging is fail-closed while the project
retains explicit client-specific configuration and routing.

**Evidence**

- Primary-source provenance records reviewed package versions and source blobs.
- Compatibility tests cover project configuration, environment references,
  isolated browser mode, client claims, portable-manifest absence, and JSON
  redaction.
- The required identity/access security review documents principals, trust
  boundaries, blocking findings, and verified controls.
- Full repository verification passes all ten stages, including 34 task
  records, compatibility and plugin negative fixtures, design tokens, security
  hooks, local links, evidence bundles, Showcase lint, typecheck, and tests.

**Authority boundary**

Issue #49 owns the decision. No package was installed or executed, no server was
started or contacted, no credential value was read, and no protocol, network,
sandbox, browser, deployment, production, approval, or merge authority was
enabled. A new human-approved task is required before portable packaging can be
reconsidered.

### 2026-08-14 — T-036

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Raised the machine-readable, read-only Claude Code advisory baseline from
2.1.225 to 2.1.232. Added explicit repository contracts for full-context
subagent forks, background execution, terminal states, synced-skill boundaries,
nested repository trust, shell input redirection, shared-socket and sandbox
hardening, and cross-session identity/authorization limits.

**Evidence**

- First-party release notes for v2.1.228, v2.1.229, v2.1.231, and v2.1.232 are
  recorded with dates, relevance, confidence, deduplication, and uncertainty.
- Runtime tests reject Claude Code 2.1.231 and accept 2.1.232 in strict mode.
- JSON reporting declares `mutation_performed: false`; all optional capabilities
  remain disabled and human-gated.
- An independent security evaluator passed the identity, authorization,
  multi-agent, context, failure, and mutation boundaries after four
  non-blocking corrections were applied.
- Full repository verification passes all ten stages across 35 tracked tasks,
  security hooks, runtime/Codex policy, design tokens, local links, evidence
  bundles, Showcase lint, typecheck, and tests.

**Authority boundary**

Issue #51 owns the baseline decision. This task does not install or upgrade a
runtime; change models, providers, permissions, credentials, network, sandbox,
or managed settings; enable self-hosted, cross-session, Remote Control, MCP,
plugin, marketplace, production, approval, or merge authority; or treat a
compatible version as authorization. Human review and merge remain separate.

### 2026-08-15 — T-037

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Added a confirmation-gated downstream project generator that materializes a
clean, profile-specific project in a new directory without pruning or mutating
the starter checkout. It rewrites project identity and provenance, resets
durable execution state, excludes inactive application surfaces and source
history, and keeps all external capability setup pending.

**Evidence**

- Twenty-two focused tests cover dry-run no-mutation behavior, web/mobile/core/
  research profile selection, destination containment, existing-destination
  preservation, empty MCP configuration, identity rewriting, and generated-
  project offline verification.
- Negative tests also require a Git-index copy source and reject sensitive file
  names, traversal in generator configuration, escaping leaf symlinks, and
  files reached through escaping symlinked parents before destination creation.
- A rollback identity-replacement test proves that failure cleanup preserves a
  different directory placed at the destination path instead of deleting it.
- Generated verification fails when automatic capability mutation is enabled
  or an external specialist is activated in the generated project manifest.
- The machine-readable generation plan reports selected and resolved profiles,
  included and excluded managed paths, pending external setup, source version
  and commit, dirty-state disclosure, and authority boundaries.
- Full repository verification passes all ten stages, including JSON/JSONL,
  command registry, shell/Python syntax, profiles, design tokens, security
  hooks, local links, evidence bundles, Showcase lint/typecheck, and tests.
- The T-037 security review covers path, copy, rollback, secret, symlink,
  profile, integration, and error boundaries.

**Authority boundary**

Issue #53 owns the change. Generation writes only a previously absent
destination outside the source checkout and rolls back only that exact new
directory on failure. It does not copy Git history or secret state; install or
enable dependencies, external skills, plugins, MCP servers, runtimes, or
backends; authenticate; widen network or sandbox authority; initialize Git;
deploy; modify production; approve; or merge.

### 2026-08-16 — T-038

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED

**Change**

Raised the read-only Claude Code advisory baseline from 2.1.232 to 2.1.233.
Recorded the Windows NT device-prefix credential boundary, literal
skill-argument substitution, MCP v2 subscription reliability, the reverted
Cygwin-symlink and Bash input-redirection permission changes, and the disabled
apps-gateway identity-forwarding surface.

**Evidence**

- The source ledger records the exact first-party release, date, authority,
  relevance, deduplication, confidence, and uncertainty.
- Eight targeted tests reject 2.1.232, accept 2.1.233, preserve read-only JSON
  output, and require identity forwarding to remain disabled and human-gated.
- An independent read-only security review found and resolved the reverted
  permission overclaim and missing identity/privacy gate, then returned PASS.
- Full repository verification passes all ten stages.

**Authority boundary**

Issue #55 owns human review. This task does not install or upgrade a runtime;
enable identity forwarding, MCP, plugins, self-hosted or cross-session work;
change models, providers, credentials, network, sandbox, or managed settings;
deploy; modify production; approve; or merge. Compatibility remains a
prerequisite, not authorization.

### 2026-08-19 — T-039

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED AND VERIFIED; INDEPENDENT REVIEW PENDING

**Change**

Replaced the placeholder web and UI surfaces with a runnable portfolio golden
path. Added a short adaptive intake, three live and materially different design
directions, explicit approval/reset state, DTCG-compatible direction token
compilation, semantic UI primitives, purposeful core motion, reduced-motion and
responsive contracts, generated root scripts, and streamlined onboarding.

**Evidence**

- Thirty-seven focused design-engine, token, generator, and command tests pass.
- Web UI contract tests verify all three direction IDs, explicit approval,
  semantic-token consumption, focus, responsive, and reduced-motion contracts.
- TypeScript and the Next.js production build pass.
- The running app was inspected at desktop and a 390 × 844 mobile viewport.
  All three directions changed composition and typography, not only color; the
  mobile page had no horizontal overflow.
- Generated `web`, `mobile`, and `core` profile tests pass with correct surface
  selection and reset design state.
- Full repository verification passes all ten stages.

**Authority boundary**

The connected issue integration returned 403, so the task and pull request carry
the review context. This task does not install or execute external skills,
enable MCP servers, use credentials, deploy, modify production, make advanced
2D/3D dependencies mandatory, approve its own direction, approve its own pull
request, or merge. A separate design critic and human reviewer remain required.

### 2026-08-19 — T-040

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED LOCALLY; LINUX BASELINE REVIEW PENDING

**Change**

Added a web-specific Playwright quality gate covering all three portfolio
directions at desktop and mobile sizes. The gate separates behavioral,
accessibility, responsive, reduced-motion, and screenshot evidence; generated
web projects retain it while non-web profiles omit it.

**Evidence so far**

- Eleven interaction/accessibility checks pass with one expected desktop skip
  for the mobile-only overflow contract.
- The axe scan found a real low-contrast step-index defect; the implementation
  was corrected and the suite then passed.
- The production build and fourteen focused downstream-generator tests pass.
- Live browser inspection confirmed every direction at desktop and 390 x 844,
  no mobile horizontal overflow, and no browser warnings or errors.
- The Linux workflow generates candidate baselines when none exist and then
  fails closed instead of treating generation as approval.
- The independent critic returned code-level PASS after the keyboard and flaky
  visual-test blockers were resolved; full repository verification passes.

**Remaining evidence**

Ubuntu CI must generate the six canonical baseline candidates. A human must
inspect and approve them before they are committed and compared by normal CI.
Final repository verification must be rerun after that evidence is committed
before the task can move to human approval.

**Authority boundary**

Issue #58 owns the review contract. This task does not silently update visual
baselines, approve its own evidence or pull request, deploy, modify production,
enable external capabilities, merge, or push `main`.

### 2026-08-23 — T-041

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED LOCALLY; INDEPENDENT REVIEW PENDING

**Change**

Added an offline, evidence-gated harness-evolution kernel. It validates
sanitized aggregate outcomes, protects the policy and regression exam with
fingerprints, compares bounded candidates with the incumbent across quality,
safety, cost, and latency, and keeps all promotion authority false.

**Evidence so far**

- Thirteen focused tests cover the valid comparison and fail-closed privacy,
  exam-integrity, path, coverage, evaluator, regression, safety, cost, and
  latency boundaries.
- Command and downstream-generator tests expose the same read-only
  `./agentic evolve` interface in generated projects.
- The committed policy, schemas, protected cases, and incumbent validate
  deterministically without network access or mutation.
- Full repository verification passes all ten stages, including the new
  evolution tests, generated-project checks, security hooks, design-token
  checks, documentation links, and project-defined lint/typecheck/tests.
- Independent security review remains pending before task finalization.

**Authority boundary**

Issue #60 owns review. The kernel does not collect production telemetry, retain
raw prompts or customer data, invoke remote models, train weights, execute
generated code, write candidates, weaken or mutate protected evals, install or
enable external capabilities, use credentials, change network or sandbox
authority, deploy, canary, promote, approve, or merge.

### 2026-08-24 — T-042

**Requirements:** FR-001
**Acceptance:** AC-001
**Outcome:** IMPLEMENTED LOCALLY; INDEPENDENT SECURITY REVIEW PASS

**Change**

Raised the read-only tested runtime floors to Claude Code 2.1.239 and Codex
0.148.0 based on first-party release evidence. The policy records cumulative
permission, filesystem, credential, marketplace, MCP trust, resumed-state, and
instruction-state hardening while keeping newly available helper and hook
surfaces disabled and human-gated.

**Evidence**

- Eight focused runtime compatibility tests pass.
- Strict simulation rejects Claude Code 2.1.238 and Codex 0.147.0, and accepts
  Claude Code 2.1.239 and Codex 0.148.0.
- JSON output parses with `mutation_performed: false`.
- Full repository verification passes all ten stages.
- The local Codex prerelease remains below the stable floor and produces an
  advisory warning; the repository does not upgrade it.

**Independent review**

- A separate read-only security reviewer inspected exact head `553c747` and
  returned `PASS` with no blocking security defect or authority expansion.
- The review is recorded under `docs/50-evals/evidence/T-042/`.
- Human task finalization and squash merge remain separate decisions.

**Authority boundary**

Issue #62 owns review. This task does not install, upgrade, or configure a
runtime; enable marketplace/MCP helpers, asynchronous or MCP-invoking hooks,
plugins, MCP servers, credentials, network, sandbox, provider, model,
production, approval, or merge authority; or change managed settings.

### 2026-08-26 — T-044

**Requirements:** FR-001, FR-002, FR-003, FR-004
**Acceptance:** AC-001, AC-002, AC-003, AC-004
**Outcome:** IMPLEMENTED LOCALLY; INDEPENDENT AND HUMAN REVIEW PENDING

**Change**

Added a conditional enterprise-workflow path to guided creation. It generates
a machine-readable enterprise contract and durable product, journey, role,
data, API, security, audit, design, and task artifacts. The running reference
slice covers tenant-scoped request creation, evidence review, approve/reject/
request-changes/cancel transitions, append-only audit consequences, and clear
local-versus-production adapter status across three design directions.

**Evidence so far**

- 27 focused generator/next-action tests pass.
- Domain, API, and web model suites pass, including tenant visibility and
  role-scoped creation.
- Source production build and full interaction/accessibility suite pass: 23
  passed, one intentional desktop skip.
- All 24 macOS reference visual comparisons pass for four archetypes, three
  directions, desktop, and mobile.
- A freshly generated enterprise project installs from the reviewed lockfile,
  advances to the live direction lab through `./agentic next`, passes full
  generated-project verification, builds, and passes 17 selected-archetype
  browser tests with seven intentional irrelevant-archetype skips.
- Ubuntu Web quality run `33014674724` passes the build and browser behavior
  gates and generated all 24 Linux candidates. The six enterprise candidates
  were builder-inspected without clipping, occlusion, or cross-direction
  contract drift. The project owner then explicitly approved T-044; only those
  six enterprise images became canonical Linux baselines.
- The public README was reduced from a reference-manual-sized first encounter
  to a concise onboarding path with real enterprise visual proof, archetype
  guidance, one-next-action usage, design-quality rules, enterprise boundaries,
  core commands, parallel-work guidance, safety defaults, and routed deep links.

**Review boundary**

This evidence includes explicit human visual approval but not merge authority.
The final updated head must pass its deterministic gates, independent product
and security review, and README review before task finalization. No production
service, credential, external
notification, deployment, approval, or merge authority was enabled.

### 2026-08-27 — T-045

**Requirements:** FR-001, FR-004, FR-005
**Acceptance:** AC-001, AC-004, AC-005

Added a task-aware first-project continuation path, generated first-feature
briefs, distinct repository/web/visual verification, and explicit readiness
guidance. New acceptance files are included in the web suite; visual candidates
remain separately generated and human-reviewed. The newcomer pilot is a
protocol, not evidence of participant success.

Verification recorded under `docs/50-evals/evidence/T-045/` includes 56 focused
tests, all ten repository stages, 25 source browser passes with one intentional
skip, 24 unchanged macOS visual comparisons, and clean-checkout release smoke.
A fresh custom enterprise example passed 21 browser cases with seven expected
skips, including an additional acceptance file. Its missing-baseline check
failed safely without creating or approving screenshots.

Independent product/QA and security reviews found and rechecked fixes for new
test discovery, malformed-state handling, changed-profile task routing,
feature-specific baseline paths, and post-merge guidance. No application UI or
approved design changed. Human approval, merge, deployment, public hosting,
production readiness, and real-user pilot results are not implied.
### 2026-08-30 — T-047

**Requirements:** FR-001, FR-004, FR-005, FR-006

**Acceptance:** AC-001, AC-004, AC-005, AC-006
**Outcome:** IMPLEMENTED LOCALLY; INDEPENDENT AND HUMAN REVIEW PENDING

Added a consent-based local newcomer-pilot command with anonymous P1–P5 session
packets, a closed scorecard schema and policy, strict privacy and completeness
validation, deterministic launch gates, repeated-blocker detection, and JSON/
Markdown aggregate reports. Fewer than five valid sessions cannot pass.

Targeted pilot, command-router, and generated-project tests pass. The ten-stage
full repository verification and clean-checkout release smoke pass after
restoring the reviewed locked dependencies. No participant data was collected and no newcomer success,
testimonial, production readiness, native readiness, publication, approval, or
merge is implied. Evidence and remaining review boundaries are recorded under
`docs/50-evals/evidence/T-047/`.
