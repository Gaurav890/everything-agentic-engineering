# Handoff

Last updated: 2026-08-15

## Current goal

Review the safe downstream project generator before human finalization.

## Completed

- `./agentic setup create` previews or materializes a new project outside the
  starter checkout using presets or manual profile selection.
- Generation uses reviewed tracked files plus explicit profile path rules; it
  excludes Git state, secrets, dependencies, caches, build output, Signalroom,
  source evidence, launch assets, release artifacts, and source execution state.
- Project identity, profile manifest, provenance, README, package/plugin
  metadata, environment placeholders, and durable execution ledgers are reset.
- Generated `.mcp.json` is empty. Dependency, skill, plugin, MCP, runtime,
  backend, authentication, deployment, approval, and merge work remains a
  separate reviewed decision.
- Failure rollback removes only the previously absent destination created by
  that exact invocation; existing destinations and paths inside the starter are
  rejected before writing.
- Rollback records the created directory identity and refuses deletion if the
  destination path is replaced during generation.
- Generation requires a valid Git checkout and resolves every planned source
  entry before destination creation and immediately before copy. Escaping
  parent or leaf symlinks, absolute link targets, and symlinked output ancestors
  fail closed.

## Blockers

- None.

## Unresolved decisions

- The generator intentionally does not initialize Git or install project
  dependencies; the project owner performs those steps after inspecting the
  generated project.
- Profile catalogs and on-demand local skills remain available in generated
  projects, while inactive application surfaces and their owners/rules are
  omitted.

## Verification status

- Twenty-two focused generator and command-routing tests pass.
- Web, mobile, core, and research generation paths validate offline.
- Dry-run, destination containment, existing-destination preservation, profile
  selection, empty MCP state, and generated-project verification are covered.
- Generated verification rejects automatic install/removal permission changes
  and non-empty specialist activation.
- Full repository verification passes all ten stages.

## Exact next action

For work that reaches human review, use the bounded finalization contract in
`docs/70-collaboration/GITHUB_WORKFLOW.md`. Human approval authorizes only the
linked task-ledger transition; squash merge remains a separate human action.

## Relevant files

- `.agentic/generator.json`
- `.agentic/commands.json`
- `scripts/project_generator.py`
- `scripts/verify_generated_project.py`
- `scripts/create-project.sh`
- `tests/test_project_generator.py`
- `docs/60-tooling/PROJECT_GENERATOR.md`
- `docs/50-evals/evidence/T-037/security-review.md`
- `CLAUDE.md`
- `AGENTS.md`

Keep this concise enough to read in under two minutes.
