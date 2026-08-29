# Current state

Last updated: 2026-08-27

## Product

Product-design work is routed through explicit discovery, strategy, interaction,
system, implementation, audit, critique, polish, and delivery phases.

Design-critical work first uses an adaptive intake for the active project
profiles. It records brand authority, experience intent, color constraints,
typography, composition, motion, accessibility, and references, then presents
comparable directions. Canonical design-system and token changes require an
explicitly approved direction or synthesis.

Signalroom under `apps/showcase` is the reference AI-native product. It
demonstrates agent runs, protected approvals, interruption, recovery, durable
artifacts, required UI states, and responsive supervision.

The guided project studio materializes a portfolio, product, agentic-product,
enterprise-workflow, mobile, or core project after capturing its audience,
outcome, design approach, optional preferences, and preferred coding client.
Enterprise workflows ask four additional domain decisions only when selected.
New projects persist `.agentic/project-brief.json` and their own product
drafts; web reference metadata remains in `.agentic/experience.json`.
`./agentic start` continues the saved brief; `next` exposes one action at a time.
Web and mobile application profiles always resolve the design-critical
foundation.

## First-project continuation

Generated projects include their own vision, PRD, acceptance draft, copy,
architecture, README, and first-feature context. Native client launch requires
terminal confirmation; a manual app/editor instruction needs no installation
or credential collection. Existing projects are not migrated automatically.

Custom/existing-brand web projects show an honest setup workspace, not a
finished product. Their catalog starts empty and supports arbitrary local
preview routes. Bundled examples require an explicit reference choice.
Approval binds completed intake, confirmed scope, screenshot evidence, selected
candidate, and listed sources. Fingerprints detect drift, not design quality.
`next` follows current profiles, prerequisites, approved design, dependencies,
workstreams, blockers, and review instead of stopping at setup verification.
It does not install tools, alter task state, or infer approval or merge.

`verify full` checks repository contracts and available package checks;
`verify web` additionally requires tools and runs build, interaction, and
automated accessibility tests; `verify visual` compares existing screenshots
without updating them. New acceptance files join the web suite, while
`@visual` selects screenshot-only tests. Missing evidence remains explicit.

The newcomer pilot protocol exists, but no real participant outcomes have been
measured. Public-demo hosting, production adapters, and launch promotion remain
separate work. Implementation and review evidence is under
`docs/50-evals/evidence/T-046/`.

## Web

Substantial frontend work uses the project design system as authority and
requires running-product evidence plus independent evaluation.

`apps/web` is a buildable Next.js reference lab with distinct portfolio,
product, agentic-product, and enterprise-workflow architectures, accessible direction controls,
responsive composition, purposeful core motion, and a reduced-motion path.
The agentic example includes a working evidence-completeness gate, consequence
disclosure, approval lock, approve/reject/cancel paths, and recovery language.
The direction lab is non-obscuring on desktop and collapses to a focus-managed,
escape-dismissible mobile control.

The enterprise archetype runs a tenant-scoped request/evidence/decision/audit
journey over explicit API, pure domain-policy, repository, and shared-type
boundaries. Cross-tenant visibility, invalid roles, self-approval, incomplete
evidence, missing rationale, and invalid transitions fail closed. Creation and
evidence audit attribution and all mutation timestamps are service-owned.
Pending refresh work is cancelled when the acting identity or workflow state
changes. Generated browser tests honor the selected promise, business object,
and approval model. Its identity,
persistence, notifications, and audit adapters are explicitly local and
`production_ready` remains false.
`packages/ui` contains behavior primitives rather than a visual theme. Advanced
2D, 3D, timeline, or gesture runtimes remain opt-in escalation tiers after an
approved direction and performance budget.

The starter reference lab has Playwright interaction/accessibility coverage and
a complete four-archetype × three-direction × desktop/mobile visual matrix.
Generated projects exclude reference baselines. Reference mode tests the chosen
archetype; custom/existing-brand mode tests the workspace and local candidate
links. Actual product behavior needs feature-specific tests. Linux candidate
generation remains separate from human visual approval.

When `design-critical` is active, Emil Kowalski's reviewed ten-skill external
collection is available as a profile-aware design-engineering craft layer.
`design-engineering-quality` routes `emil-design-eng` as the first external
design implementation skill or one exact specialist; Anthropic
`frontend-design` remains secondary and opt-in. The router never invokes the
collection wholesale or replaces product discovery,
approved directions, tokens, accessibility, Playwright, or the final evaluator.

## Mobile

The same phase routing applies while preserving native platform conventions.
The current native application directory is a placeholder, not a runnable Expo
app. Responsive browser evidence does not certify native behavior.

## Backend

## Data

Canonical DTCG-compatible design-token source files exist under
`packages/design-tokens/tokens/`. A dependency-free build generates CSS,
TypeScript, React Native theme outputs, and an inspectable token specimen.
Component tokens consume stable semantic roles; light and dark themes override
those roles. The build fails on theme parity drift, direct component-to-theme
aliases, missing aliases, and required WCAG contrast failures.

Candidate direction packs use DTCG `$type`/`$value` structures in
`.agentic/design-directions.json`. `./agentic design` records intake and explicit
approval; token generation emits `direction.css` only for the approved pack.

## Harness evolution

The repository now has an offline, proposal-only harness-evolution kernel.
`./agentic evolve` validates a closed authority and privacy policy, sanitized
aggregate outcome signals, protected regression cases, and last-known-good
incumbent evidence. It compares a bounded candidate on quality, protected
regressions, safety, aggregate cost, and p95 latency while checking exact
policy/eval fingerprints, complete case coverage, allowed changed paths, and
builder/evaluator separation.

A passing result authorizes only a human-reviewed proposal. The committed
policy forbids candidate writing, protected-eval mutation, automatic promotion,
deployment, approval, and merge. The starter fixture is synthetic and does not
claim product performance; downstream production signal collection and
domain-owned evals require a separate privacy and data architecture.

## Integrations

Project capabilities are selected in `.agentic/project.json` and resolved
through non-destructive profile tooling. The doctor reports drift; it does not
install or remove resources.

`.agentic/external-skills.json` records the Emil collection's complete
ten-skill inventory, source URLs, reviewed commit, MIT license, triggers,
phases, activation gates, and pinned install command. External installation is
an explicit `./agentic setup skills` action for active profiles and targets both
Claude Code and Codex globally. It has a non-mutating `--dry-run` preview.

The guided initializer offers safe presets or manual selection and previews
active profiles, inactive profiles, required capabilities, retained inactive
capabilities, and external setup. It writes only the profile manifest after
explicit confirmation. Unselected mobile, web, research, backend, or
design-critical capabilities are not routed or treated as project requirements.

The downstream project generator materializes a clean, profile-specific project
in a previously absent directory outside the starter checkout. It copies only
reviewed tracked assets, removes inactive application surfaces, rewrites project
identity and provenance, resets execution history, and leaves external setup
pending. It does not prune the starter, copy Git or secret state, install
dependencies or capabilities, enable MCP servers, initialize Git, or expand
runtime authority. Generated projects have a dedicated offline verification
mode through the same `./agentic verify full` interface. That mode resolves the
current project profiles, validates the surfaces those profiles require, and
fails closed on unknown or profile-incompatible specialist activation. MCP
configuration must remain empty or exactly match the reviewed compatibility
policy; arbitrary servers, commands, packages, and credential shapes cannot
receive a passing verification result.

Generated web projects receive runnable root scripts, their selected content
architecture, product-specific experience/brief state, unapproved direction
state, and a one-path README. Creation validation rejects copied transient or
authority state; ongoing validation allows normal Git, dependencies, task
history, approved design state, and reviewed capability configuration while
keeping current profile and authority checks deterministic. After
`pnpm install`, package lint, typecheck, and UI contract tests are active.

Contributor workflows are exposed through one registry-backed `./agentic`
interface. `.agentic/commands.json` classifies all 36 shell files as public,
internal, compatibility, or security-hook surfaces. The 29 supported public
workflows are grouped by setup, profile, task, pull request, workspace, doctor,
specialist agents, design, tokens, harness evolution, release, and
verification. Existing direct script paths remain compatible; no script or
hook has been deleted or relocated.

Task-ledger work can be inspected with `./agentic task plan` and prepared with
`./agentic task start`. The launcher checks dependency completion, active-profile
compatibility, specialist routing, exclusive file ownership, verification
gates, and base-branch freshness. Planning is read-only and workspace creation
requires explicit confirmation.

Reviewed external specialist expertise is operational through
`.agentic/external-agents.json`, `specialist-router`, and `./agentic agents`.
The broker exposes the complete upstream source roster, routes 14 curated
contracts from task evidence and active profiles, keeps one accountable local
owner, and specifies required artifacts plus independent evaluators. Optional
activation changes only `.agentic/project.json`; it never installs or executes
upstream agents or expands runtime authority.

New unfinished tasks also carry an explicit GitHub tracking contract: required
issue references or a reviewed issue-free reason. The task planner reports
whether a PR should relate to or close each issue. Required PR policy validation
is deterministic and offline; optional live status uses read-only GitHub
commands and cannot edit issues, tasks, pull requests, or repository state.

Post-merge closeout is resolved live rather than predicted in committed prose.
`./agentic task closeout` reads the default branch and GitHub state, verifies the
merged task/PR/issue contract, detects stale volatile handoff claims, and
reports safe local worktree/branch cleanup commands without executing them.

PR finalization is a separate, human-approved gate. A direct task approval can
invoke `./agentic pr finalize`, which validates the branch, open PR, task and
issue contract; reuses full verification; stages and commits only the task
ledger; pushes the task branch; marks a draft ready; waits a bounded interval
for check registration; and watches the checks. The same command can recover
from its exact uncommitted or staged `review` to `done` ledger transition and
from already-committed or already-ready checkpoints. Every recovery remains
fail-closed against unrelated files or ledger edits. It never approves,
merges, pushes `main`, or treats external content as approval. Humans do not
manually edit `TASKS.jsonl` to clear policy failures.

Codex is supported through a native repository adapter. `AGENTS.md` carries the
cross-runtime contract; `.agents/skills` exposes the canonical
`.claude/skills` catalog without copied instructions; trusted project
configuration bounds context and concurrency; Codex hooks reuse the reviewed
destructive-command and secret-scan scripts. The adapter intentionally does not
select models/providers, add credentials or MCP execution, enable network
access, widen sandboxes, or bypass approvals.

Root `plugin.json` and fixed-location `skills/` provide an additive Agent
Plugins 1.0 portable, skills-only core. `.codex-plugin/plugin.json` remains a
separate Codex-native compatibility manifest. The offline plugin doctor checks
the closed manifest, semantic version, immediate skill discovery, and path
containment. Project `.mcp.json` is not copied into portable `mcp.json` because
its client-specific environment references are not a portable credential
contract.

Portable MCP compatibility is now machine-readable in
`.agentic/mcp-compatibility.json`. Perplexity, Firecrawl, and Playwright remain
reviewed client-specific capabilities, while root `mcp.json` is absent and
fail-closed. `./agentic doctor mcp` validates the server provenance,
environment-reference boundary, isolated Playwright mode, client matrix, and
blocked portable decision without reading secret values or starting servers.

Seven project-scoped Codex custom agents cover read-only product planning,
architecture, research, design critique, security review, adversarial QA, and
integration review. They add context specialization without adding runtime
authority. Parallel implementation remains isolated by task branch and
worktree.

Claude Code and Codex compatibility is defined in
`.agentic/runtime-baselines.json` and reported by `runtime-doctor.sh` in
advisory, strict, or JSON form. The doctor is read-only and keeps version
availability separate from optional capability approval. Claude Code 2.1.239
is the recommended tested baseline. It includes the documented permission,
Windows and macOS filesystem, marketplace-origin, MCP helper trust, credential
isolation, organization-policy, and resumed-plan hardening through that
release. Codex 0.148.0 is the recommended tested baseline for consistent
instruction and approval state, fail-closed filesystem denials, and MCP OAuth
recovery. The full-context fork and background-spawn defaults remain bounded by
the repository contract:
in-session specialists are read-only, writers use isolated branches/worktrees,
and delegated work requires observed evidence. Claude self-hosted and
cross-session execution, Remote
Control, archive and dynamic marketplace sources, marketplace or MCP
`headersHelper` commands, Codex portable plugin installation, MCP 2026-07-28
opt-in, asynchronous or MCP-invoking hooks, apps-gateway identity forwarding,
and automatically reviewed approvals are not enabled by the committed policy.

GitHub `main` protection requires the `verify` and `policy` checks, an up-to-date
branch, linear history, and resolved review conversations. It applies to
administrators and blocks force pushes and branch deletion. The solo-maintainer
configuration currently requires zero approving reviews; increase this when a
second maintainer can provide independent approval.

The repository identifies as `v0.1.0` and contains a human-gated release
workflow, curated release notes, a clean-checkout onboarding smoke test,
compatibility and limitation statements, a 60-second demo script, and
channel-specific launch copy. Running the workflow without its publish option
only builds a reviewable archive and checksum.

The public `v0.1.0` release is published from reviewed commit `991c70c` with a
verified source archive and checksum. A 1280×640 launch card is maintained at
`docs/assets/social-preview-v0.1.0.jpg`.

The README demonstrates the system with five focused GIFs captured from actual
initializer, task-planning, running-product interaction, UI-state, and full
verification flows.

## Security

## Verification

The full suite validates local skills, external design-skill provenance and
routing, profiles, initialization, token
generation, security hooks, local documentation links, collaboration policy,
evidence bundles when present, and project-defined checks. Signalroom also has
production builds, model tests, Playwright interaction tests, and axe
accessibility checks; browser tests run as a dedicated GitHub Actions gate.

Codex verification additionally validates shared skill discovery, project
configuration authority boundaries, hook wiring, separate native and portable
plugin metadata, portable path containment, default and strict runtime-doctor
behavior, and Codex `apply_patch` secret scanning.

The web browser gate verifies direction selection, keyboard entry, automated
axe findings, mobile horizontal overflow, reduced-motion behavior, and visual
comparisons in a fixed Linux environment. Local browser inspection remains
exploratory evidence rather than the canonical screenshot environment.

Runtime compatibility verification validates the machine-readable policy,
stable-versus-prerelease comparison, advisory and strict outcomes, JSON output,
and Codex doctor reuse without requiring either runtime in portable CI.

## Known incomplete work

- Signalroom is a static reference experience, not a connected agent runtime.
- Optional external design skills are not bundled or installed by profile
  selection; the explicit setup command installs only active, reviewed groups.
- Existing-copy initialization intentionally does not delete inactive template
  inventory. New products can instead use the downstream generator, which
  omits inactive application surfaces without mutating the starter checkout.
- The reviewed screen recording still requires a maintainer to capture it.
- Social platforms may cache older repository preview metadata after updates.
- Write-capable Codex specialist roles are intentionally not committed;
  parallel writers use separate task branches and worktrees.
- Portable and Codex-native plugin marketplace publication and installation
  policy remain explicit release actions.
- Portable MCP packaging is intentionally blocked until portable credentials,
  deterministic execution, target-protocol negotiation, clean-client trust and
  rollback behavior, and independent security review all have evidence.
- The developer machine inspected for T-025 reports Claude Code 2.1.220 and a
  Codex 0.146.0 prerelease build, both below the recommended baselines. The
  repository reports this drift but does not upgrade developer tooling.
- New or intentionally changed web visual baselines require human inspection
  before their Linux candidates can be committed as comparison evidence.

Only factual present-tense truth belongs here.
