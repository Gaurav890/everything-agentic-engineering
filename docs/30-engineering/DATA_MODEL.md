# Data model

## Entities

### EnterpriseRequest

`id`, `tenant_id`, `owner_id`, `title`, `scope`, `justification`, `risk`,
`status`, `evidence[]`, `assigned_reviewer_id`, `policy_state`, timestamps, and
concurrency version.

### EvidenceItem

`kind`, `source`, `state`, `verified_at`, and non-secret provenance reference.

### AuditEvent

Immutable `id`, `tenant_id`, `request_id`, `actor_id`, `action`, `from_state`,
`to_state`, `reason_code`, rationale where permitted, correlation ID, and time.

## Relationships

One request belongs to one tenant and owner, has many evidence items and audit
events, and may have an eligible reviewer distinct from its owner.

## Ownership

All reads and writes are tenant scoped. Production actor and tenant identity
come from verified server-side claims, not request payloads.

## Retention

Request and audit retention is organization policy. Audit events are append-only
and require a separately reviewed deletion/legal-hold process.

## Sensitive fields

Justification, scope, evidence provenance, actor identity, and rationale may be
sensitive. Do not log their raw values. The reference fixture is synthetic.

## Indexes/performance

Production adapters should index tenant/status/update time, tenant/owner, and
tenant/request audit order. Measure queue and audit-list access patterns before
adding speculative indexes.

## Migration notes

Use versioned, backward-compatible migrations; define backfill, rollback,
idempotency, and audit-integrity checks before replacing the local adapter.
