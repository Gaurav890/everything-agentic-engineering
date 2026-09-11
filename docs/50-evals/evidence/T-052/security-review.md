# T-052 runtime-baseline security review

Reviewed: 2026-09-10
Evaluator: security-reviewer
Review mode: independent, read-only review after implementation
Reviewed head: `202190e9512f0d27fa1ef77eea5f1db4d79aa50e`

## Scope

Review the Claude Code 2.1.259 and Codex 0.153.0 tested-baseline change against
the reconciled issue #74 contract, first-party release evidence, runtime
authority boundaries, optional capability gates, strict/advisory/JSON behavior,
tests, and durable guidance. The review did not edit files, push, comment,
approve, finalize, or merge.

## Findings and corrections

No blocking security defect or accidental authority expansion remains.

The initial review found two issues that were corrected before this verdict:

1. Issue #74's original body still named older floors even though later owner
   addenda had revised the proposal. The issue now contains one current scope
   and acceptance contract.
2. Optional-capability output implied that the doctor had inspected runtime
   configuration. It now says the capability is not enabled by repository
   policy and that runtime configuration was not inspected.

The branch also explicitly excludes the Bash argument-level `Read()` deny
expansion introduced in 2.1.259 and reverted in 2.1.260.

## Verified boundaries

- Runtime floors and source URLs match the reviewed official releases.
- Strict mode rejects Claude Code 2.1.258 and Codex 0.152.1 and accepts the
  exact 2.1.259 and 0.153.0 floors.
- Advisory and JSON modes remain read-only; JSON declares
  `mutation_performed: false`.
- Managed MCP servers, remote plugin marketplaces, experimental context
  management, automatic reviews, and every other optional surface remain
  disabled by repository policy and human-gated.
- No runtime, dependency, hook, MCP, plugin, credential, network, sandbox,
  provider, model, data, deployment, production, approval, or merge
  configuration changed.
- Claude Code 2.1.265–2.1.267 and Codex 0.154.0 are observed but deferred to a
  separate stabilization and evidence cycle.

## Evidence

- Eight focused runtime compatibility tests pass.
- Strict below-floor simulation exits 1; exact-floor simulation exits 0.
- JSON parses with `ok: true` and `mutation_performed: false`.
- Full repository verification passes all ten stages.
- GitHub `verify` and `policy` checks pass on the implementation branch.
- `git diff --check` is clean.

## Residual uncertainty

Minimum-version comparison does not certify later versions or inspect actual
user/managed runtime configuration. Upstream release notes do not publish CVEs,
complete affected-version ranges, or exploit prerequisites. The repository
states both limitations and makes no broader claim.

## Verdict

**PASS.** No blocking or material non-blocking security finding remains. Human
task finalization and squash merge remain separate decisions.
