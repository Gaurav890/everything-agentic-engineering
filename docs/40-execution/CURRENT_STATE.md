# Current state

Last updated: 2026-08-03

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

## Web

Substantial frontend work uses the project design system as authority and
requires running-product evidence plus independent evaluation.

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

## Integrations

Project capabilities are selected in `.agentic/project.json` and resolved
through non-destructive profile tooling. The doctor reports drift; it does not
install or remove resources.

The guided initializer offers safe presets or manual selection and previews
active profiles, inactive profiles, required capabilities, retained inactive
capabilities, and external setup. It writes only the profile manifest after
explicit confirmation. Unselected mobile, web, research, backend, or
design-critical capabilities are not routed or treated as project requirements.

Task-ledger work can be inspected with `task-plan.sh` and prepared with
`task-start.sh`. The launcher checks dependency completion, active-profile
compatibility, specialist routing, exclusive file ownership, verification
gates, and base-branch freshness. Planning is read-only and workspace creation
requires explicit confirmation.

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

The full suite validates local skills, profiles, initialization, token
generation, security hooks, local documentation links, collaboration policy,
evidence bundles when present, and project-defined checks. Signalroom also has
production builds, model tests, Playwright interaction tests, and axe
accessibility checks; browser tests run as a dedicated GitHub Actions gate.

## Known incomplete work

- Signalroom is a static reference experience, not a connected agent runtime.
- Optional external design skills are not bundled or auto-installed.
- The initializer intentionally does not delete inactive template inventory;
  cleanup remains a separate explicit decision.
- The reviewed screen recording still requires a maintainer to capture it.
- Social platforms may cache older repository preview metadata after updates.

Only factual present-tense truth belongs here.
