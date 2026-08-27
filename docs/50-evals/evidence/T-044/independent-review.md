# T-044 independent review

Initial review: 2026-08-26
Initial reviewed head: `23afb1506435a3b37a9be936adbcc09c595b9bf4`

## Initial product-quality and adversarial QA verdict

**BLOCKED.** The reviewer found that a newly created draft could not complete
the advertised evidence → submit → decision journey, the selected approval
model did not affect executable behavior, and the claimed decision/state test
matrix exceeded the implemented coverage.

## Initial security and authority verdict

**BLOCKED.** The reviewer reproduced same-tenant over-broad reads for unknown,
requester, and reviewer actors, plus caller-forgeable creation audit identity
and transition metadata.

## Corrective implementation prepared for re-review

- Request reads now fail closed by tenant and known role, then scope requesters
  to owned records, reviewers to eligible records, and auditors/admins to their
  tenant. Audit UI state is filtered through the same visible-request set.
- Creation now validates input, resets evidence and policy state, constructs
  actor attribution and transition metadata inside the service, and rejects
  unsafe reviewer assignment or duplicate identity.
- Local evidence verification is a separate service action with a trusted
  policy-engine event; submission requires complete evidence.
- All service mutations use a clock configured once at service construction;
  per-call timestamp overrides and request-supplied chronology are ignored.
- Pending refresh callbacks are cancelled on actor changes and successful
  mutations, preventing stale identity views and overwritten outcome messages.
- Generated browser assertions read the configured promise, business-object
  label, and approval model instead of assuming the starter's default copy or
  reviewer policy.
- `single-review`, `dual-control`, and `policy-gated` now enforce distinct
  reviewer/assignment/gate rules while every model rejects self-approval.
- The UI and browser suite now cover creation, evidence checks, submission,
  rejection, requested changes, resubmission, approval, cancellation,
  assignment hiding, cross-tenant request/audit hiding, failure, and recovery.
- Domain/API tests cover unknown roles, owner/reviewer visibility, forged audit
  input, invalid creation, evidence enforcement, all configured approval models,
  decision rationale, terminal states, cancellation, and resubmission.

## Additional review findings resolved

- Security re-review of `52352e8` identified caller-controlled audit time. The
  service-owned clock and forged-timestamp regression close that gap.
- Linux run `33034011132` showed a refresh callback replacing the successful
  draft notice. The same stale callback could restore a previous actor's view.
  Cancellation and deterministic desktop/mobile timing tests close both paths.
- Product re-review of `493daba` generated a valid custom product promise and
  exposed a test that assumed default copy. The final assertions use the
  configured promise, business-object label, and approval model.

## Final independent verdicts

Review date: 2026-08-27

Exact reviewed implementation: `b0a9843ca0f9b9bf6517c1fefb25b4d5d20eda27`

**Product-quality / adversarial QA: PASS.** A separate read-only evaluator
verified the complete lifecycle and the refresh isolation correction, then
generated two fresh projects with different custom promises and a
`policy exception` business object. Both `policy-gated` and `single-review`
projects built successfully and passed 19 desktop/mobile browser cases, with
seven intentionally irrelevant-archetype skips each. Each restored locked
dependencies offline with scripts disabled, 34 reused packages and zero
downloads. The assertions honor all selected product choices.

**Security / authority: PASS.** A separate read-only evaluator verified the
factory-owned clock, forged-input regressions, tenant/role/ownership/assignment
restrictions, audit attribution, evidence reset, and approval policies.
Independent API tests (5), domain tests (7), and generator/next-action tests
(27) passed. The evaluator confirmed the final test-only delta preserves the
security verdict; refresh callbacks cannot restore a previous actor's records.

Neither evaluator edited the implementation, approved the GitHub PR, or merged.
Later review-record and task-finalization commits do not change the reviewed
implementation; any further behavior change requires appropriate re-review.

## Residual boundaries

- This is a bounded local demonstration, not production readiness.
- Verified identity, transactional tenant storage, durable audit integrity,
  production evidence checks, idempotency, and clock operation require separate
  adapter implementation and review.
- New downstream projects require their own human visual-baseline approval.
- Dynamic lifecycle states have interaction/accessibility coverage; not every
  state has a separate visual snapshot.
- Live required checks and merge status are resolved from PR #67, not inferred
  from these historical review verdicts.
