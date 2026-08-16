# T-038 runtime-baseline security review

Reviewed: 2026-08-16
Evaluator: security-reviewer
Review mode: independent, read-only review after implementation

## Scope

Review the Claude Code 2.1.233 advisory-baseline change against the exact
first-party release note, runtime authority boundaries, regression handling,
tests, and mutation controls. The review did not edit files, install or upgrade
a runtime, enable an integration, use credentials, or change external state.

## Findings and corrections

The first review found two blocking overclaims and one scope issue:

1. The documentation treated the 2.1.232 Cygwin-symlink and Bash
   input-redirection permission changes as cumulative even though 2.1.233
   explicitly reverted them.
2. The opt-in apps-gateway user-identity-forwarding surface was not represented
   as a disabled, human-gated privacy and proxy-trust decision.
3. An unrelated prerelease observation lacked recorded evidence and was removed.

The implementation now excludes the reverted checks from the 2.1.233 guarantee,
narrows the older hardening capability, tests the regression wording, and keeps
identity forwarding disabled pending privacy, proxy, retention, audit, access,
disclosure, rollback, and human review.

## Verified boundaries

- Version and source provenance match the official v2.1.233 release.
- Windows NT device-prefix and literal skill-argument fixes are
  version-qualified without granting new authority.
- MCP v2 subscription handling is classified as reliability, not server
  compatibility or permission to connect.
- Every optional capability remains disabled and human-gated.
- Advisory and JSON reporting remain read-only and declare no mutation.
- Installation, upgrades, credentials, network/sandbox expansion, MCP/plugin
  enablement, deployment, production changes, approval, and merge stay outside
  the task contract.

## Evidence

- Eight targeted runtime tests pass.
- Strict simulation rejects 2.1.232 and accepts 2.1.233.
- JSON output reports `ok: true` and `mutation_performed: false`.
- `git diff --check` passes.
- Added-line attribution and unrelated-source scans are clean.

## Residual uncertainty

The upstream release does not publish a CVE, full affected-version range, or
exploit prerequisites for the NTLM issue. The MCP note proves a client fix, not
universal server compatibility.

## Verdict

**PASS.** No blocking or material non-blocking findings remain. Human review,
task finalization, and squash merge remain separate decisions.
