# Handoff

Last updated: 2026-08-14

## Current goal

Review the evidence-backed Claude Code 2.1.232 advisory baseline and its
subagent, context, permission, and sandbox boundaries before human finalization.

## Completed

- The machine-readable Claude Code recommended minimum and primary source now
  point to v2.1.232.
- Compatibility guidance covers the v2.1.228 synced-skill hardening, v2.1.229
  sandbox and Git safety changes, v2.1.231 MCP OAuth fix, and v2.1.232 defaults
  plus cumulative security fixes.
- The repository contract explicitly bounds full-context forks and background
  spawns with least context, read-only in-session specialists, isolated writers,
  timeout/retry budgets, terminal states, fail-closed interruption, and
  independent evidence.
- Cross-session names remain convenience identifiers, not identity or
  authorization. Optional cross-session, self-hosted, MCP, marketplace, Remote
  Control, sandbox-setting, approval, and merge authority remains human-gated.
- The independent security review passed with all non-blocking corrections
  applied. Accessibility was not applicable because no UI changed.

## Blockers

- None.

## Unresolved decisions

- Runtime installation or upgrade remains a developer/enterprise-managed
  decision outside this task.
- Optional authority-expanding Claude Code capabilities require separate tasks,
  threat models, rollback plans, and human approval.
- Release notes do not publish CVEs or a complete affected-version floor; do
  not infer universal exploitability for earlier versions.

## Verification status

- Runtime tests reject Claude Code 2.1.231 and accept 2.1.232 in strict mode.
- Advisory and JSON reports remain read-only and declare no mutation.
- The T-036 evidence bundle and independent security review validate.
- Full repository verification passes all ten stages.

## Exact next action

For any task that reaches human review, follow the bounded finalization contract
in `docs/70-collaboration/GITHUB_WORKFLOW.md`. Direct human approval authorizes
only ledger finalization for that task; squash merge remains a separate human
action.

## Relevant files

- `.agentic/runtime-baselines.json`
- `CLAUDE.md`
- `AGENTS.md`
- `docs/30-engineering/SECURITY_MODEL.md`
- `docs/60-tooling/COMPATIBILITY.md`
- `docs/60-tooling/LEARNING_LEDGER.md`
- `docs/50-evals/evidence/T-036/security-review.md`
- `tests/test_runtime_compatibility.py`

Keep this concise enough to read in under two minutes.
