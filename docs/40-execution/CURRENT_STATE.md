# Current state

Last updated: 2026-07-25

## Product

Product-design work is routed through explicit discovery, strategy, interaction,
system, implementation, audit, critique, polish, and delivery phases.

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
TypeScript, and React Native theme outputs.

## Integrations

Project capabilities are selected in `.agentic/project.json` and resolved
through non-destructive profile tooling. The doctor reports drift; it does not
install or remove resources.

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

Only factual present-tense truth belongs here.
