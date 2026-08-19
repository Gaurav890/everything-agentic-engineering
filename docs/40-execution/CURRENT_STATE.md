# Current state

Last updated: 2026-08-19

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

The web profile now materializes a runnable portfolio golden path instead of a
placeholder surface. A short local intake records product-specific palette,
typography, density, motion, mode, and advanced-canvas constraints. The running
app compares Editorial Signal, Kinetic Index, and Quiet Material using the same
realistic content; none becomes canonical until human approval is recorded.

## Web

Substantial frontend work uses the project design system as authority and
requires running-product evidence plus independent evaluation.

`apps/web` is a buildable Next.js experience with accessible direction controls,
responsive composition, purposeful core motion, and a reduced-motion path.
`packages/ui` contains behavior primitives rather than a visual theme. Advanced
2D, 3D, timeline, or gesture runtimes remain opt-in escalation tiers after an
approved direction and performance budget.

When `design-critical` is active, Emil Kowalski's reviewed ten-skill external
collection is available as a profile-aware design-engineering craft layer.
`design-engineering-quality` routes `emil-design-eng` as the first external
design implementation skill or one exact specialist; Anthropic
`frontend-design` remains secondary and opt-in. The router never invokes the
collection wholesale or replaces product discovery,
approved directions, tokens, accessibility, Playwright, or the final evaluator.

## Mobile

The same phase routing applies while preserving native platform conventions.

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
mode through the same `./agentic verify full` interface.

Generated web projects receive runnable root scripts, the live portfolio
direction lab, reset intake/approval state, project identity environment
placeholders, and a one-path README. Offline verification validates structure;
after `pnpm install`, package lint, typecheck, and UI contract tests are active.

Contributor workflows are exposed through one registry-backed `./agentic`
interface. `.agentic/commands.json` classifies all 35 shell files as public,
internal, compatibility, or security-hook surfaces. The 28 supported public
workflows are grouped by setup, profile, task, pull request, workspace, doctor,
specialist agents, design, tokens, release, and verification. Existing direct script paths remain
compatible; no script or hook has been deleted or relocated.

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
availability separate from optional capability approval. Claude Code 2.1.233
is the recommended tested baseline, adding Windows NT device-prefix validation,
literal skill-argument substitution, and MCP v2 subscription reliability while
explicitly excluding the reverted Cygwin-symlink and Bash input-redirection
permission changes from the tested guarantee. The full-context fork and
background-spawn defaults remain bounded by the repository contract:
in-session specialists are read-only, writers use isolated branches/worktrees,
and delegated work requires observed evidence. Claude self-hosted and
cross-session execution, Remote
Control, archive and dynamic marketplace sources, Codex portable plugin
installation, MCP 2026-07-28 opt-in, apps-gateway identity forwarding, and
automatically reviewed approvals are not enabled by the committed policy.

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

Only factual present-tense truth belongs here.
