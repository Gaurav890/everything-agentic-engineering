# API contracts

The reference enterprise service is an in-process contract so the journey can
run without credentials or external services. A production transport must
preserve these semantics server-side.

## Enterprise request service

### List requests

**Authorization:** authenticated actor; tenant, role, requester ownership, and
reviewer assignment/eligibility are applied before return. Unknown roles receive
no records.

**Response:** requests visible to the actor's verified tenant and role.

### Create request

**Authorization:** requester or authorized administrator in the same tenant.

**Request:** title, scope, justification, risk, tenant, assigned reviewer, and
initial evidence requirements. Caller-authored audit identity or transition
metadata is not accepted.

**Response:** validated draft whose evidence and policy state are reset to
unverified, plus one service-authored `created` audit event.

**Errors:** invalid input, wrong tenant, missing evidence, duplicate idempotency
key, invalid evidence, unsafe reviewer assignment, persistence conflict.

### Verify evidence

**Authorization:** request owner or authorized administrator in the same tenant.

**Behavior:** the local demonstration runs deterministic synthetic checks,
updates evidence and policy-gate state, and appends one service-authored
`evidence_verified` event. A production adapter must replace this with reviewed
provenance and must not trust browser assertions.

### Submit request

**Authorization:** request owner in the same tenant.

**Behavior:** complete evidence moves a draft or returned request to review and
appends one attributable `submitted` event. Missing or partial evidence fails
closed.

### Decide request

**Authorization:** eligible reviewer in the same tenant; self-approval denied;
auditor read-only. `single-review` permits an eligible same-tenant reviewer;
`dual-control` requires the assigned reviewer distinct from the owner;
`policy-gated` additionally requires a passed policy gate.

**Request:** request ID, action, actor, optional rationale. Rejection and
requested changes require rationale.

**Response:** updated request and one attributable audit event.

**Errors:** forbidden role, cross-tenant access, self-approval, invalid state,
missing/partial evidence, missing rationale, concurrency conflict.

**Idempotency:** production transport requires a caller-provided idempotency key
for write actions and must not append duplicate audit events.

**Observability:** record correlation ID, tenant-safe request ID, action,
outcome, policy reason code, duration, and audit event ID without sensitive
request content.

## Endpoint/event template

### Name

**Purpose**

**Authentication**

**Authorization**

**Request**

**Response**

**Errors**

**Idempotency**

**Rate limits**

**Observability**
