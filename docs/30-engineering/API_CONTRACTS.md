# API contracts

The reference enterprise service is an in-process contract so the journey can
run without credentials or external services. A production transport must
preserve these semantics server-side.

## Enterprise request service

### List requests

**Authorization:** authenticated actor; tenant scope applied before return.

**Response:** requests visible to the actor's verified tenant and role.

### Create request

**Authorization:** requester or authorized administrator in the same tenant.

**Request:** title, scope, justification, risk, tenant, evidence.

**Response:** submitted request plus `created` and `submitted` audit events.

**Errors:** invalid input, wrong tenant, missing evidence, duplicate idempotency
key, persistence conflict.

### Decide request

**Authorization:** eligible reviewer in the same tenant; self-approval denied;
auditor read-only; dual-control policy enforced.

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
