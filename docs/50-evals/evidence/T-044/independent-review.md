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

## Re-review status

Pending at the next committed exact head. These corrections are builder evidence
only until the independent product/QA and security reviewers return PASS.
