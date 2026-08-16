# T-037 downstream-generator security review

Reviewed: 2026-08-15
Evaluator: security-reviewer
Review mode: independent, read-only review after implementation

## Scope

Review the downstream project generator against destination and source path
containment, Git-index copy boundaries, secret and transient-state exclusion,
symlink behavior, profile filtering, integration authority, rollback identity,
failure paths, and generated-project verification.

The review did not install dependencies or external capabilities, enable MCP
servers, initialize a downstream Git repository, authenticate, deploy, modify
production, approve, or merge.

## Findings and corrections

No blocking findings remain.

The evaluator initially found five blocking boundary gaps. All were corrected
and re-reviewed:

1. Git enumeration failure now fails closed instead of falling back to a
   filesystem walk that could include untracked or ignored content.
2. Every source entry is containment-checked before destination creation and
   immediately before copy, including files reached through symlinked parents.
3. Environment variants, credential/key names, browser authentication, HAR,
   Python cache, TypeScript build metadata, logs, and generated token output are
   excluded even if present in the Git index.
4. Failure rollback records the created destination device/inode and refuses
   deletion when another directory replaces that path.
5. Generated-project verification now rejects automatic install/removal
   permission, activated external specialists, and non-empty MCP configuration.

## Verified controls

- The destination must be previously absent, outside the checkout, and beneath
  an existing parent directory.
- The starter path must be the root of a valid Git checkout; only indexed paths
  under the reviewed source roots are candidates.
- Relative generator configuration paths cannot contain parent traversal.
- Copied symlinks must have relative targets, remain inside the generated
  project, and cannot be ancestors of later outputs.
- The source checkout is not pruned or mutated.
- The generated project starts without Git history, secrets, dependencies,
  caches, build artifacts, historical evidence, source tasks, active MCP
  servers, automatic capability mutation, or activated specialists.
- Rollback is scoped to the exact directory identity created by the invocation.
- Profile-specific web, mobile, backend, research, and design surfaces are
  selected or omitted by deterministic configuration.

## Evidence

- Twenty-two focused generator and command-routing tests pass.
- Negative tests cover no-Git fallback, traversal, escaping leaf and parent
  symlinks, destination replacement, sensitive/transient filenames, automatic
  capability policy mutation, external specialist activation, and MCP state.
- Python compilation, shell syntax, machine-readable dry-run, generated-project
  offline verification, and `git diff --check` pass.
- Full repository verification passes all ten stages.

## Residual risks

- A dirty source checkout is disclosed but permitted. Generation copies current
  tracked working-tree content rather than immutable Git blobs.
- A hard process termination can leave a partial destination for manual review;
  ordinary handled failures use identity-checked rollback.
- Filename filtering cannot prove that an ordinary tracked file contains no
  secret; the contract assumes reviewed tracked source plus repository secret
  controls.
- A same-user process can race source content between final validation and
  copy. Fully eliminating that requires descriptor-pinned or immutable-blob
  copying.
- Generated verification proves structural policy, not cryptographic
  provenance. Release archives are intentionally unsupported without a future
  reviewed archive manifest.

These risks are non-blocking for a local, human-confirmed generator and are
disclosed in the plan or documentation where relevant.

## Verification verdict

**PASS.** T-037 can proceed to human review. External setup, Git initialization,
deployment, production changes, approval, and merge remain separate decisions.
