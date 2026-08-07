# Progress log

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
**Outcome:** REVIEW

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
**Outcome:** REVIEW

**Change**

Activated GitHub `main` protection and began a native Codex role pack for
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

**Commit/PR**

Implementation commit `c803398`; draft PR #24.

**Remaining risk**

Project roles inherit capabilities already approved for the parent session.
They add no external capability themselves. Independent approving reviews
remain at zero until another maintainer can participate without blocking work.
