# Architecture

Status: Active reference architecture

## System context

The starter generates profile-scoped projects. The enterprise reference path
uses a web presentation layer over explicit API, domain-policy, repository, and
shared-type boundaries. The included adapters are local demonstrations.

## Components

| Component | Owns | Must not own |
|---|---|---|
| `apps/web` | interaction, responsive states, accessible evidence | production authorization or durable audit guarantees |
| `packages/api` | use-case orchestration and stable service boundary | UI state or provider-specific persistence |
| `packages/domain` | pure workflow transition and authorization policy | network, credentials, framework, or storage |
| `packages/database` | repository interface and local demo adapter | business transition policy |
| `packages/types` | shared contracts | runtime side effects |

## Module boundaries

## Data ownership

The repository owns requests and audit events. Every record carries tenant
identity. The domain policy owns allowed transitions and required evidence.
Verified identity/tenant claims belong to the production authentication
adapter, never to browser selectors.

## Primary flows

```text
UI intent → API use case → load tenant-scoped request → domain transition
→ atomic request/audit persistence → response → visible consequence
```

## Trust boundaries

- user-controlled form and rationale input;
- verified actor identity and tenant claims;
- tenant-scoped repository access;
- external identity, notification, and audit providers;
- agent/runtime tools and generated-project authority.

## Failure modes

Invalid role, tenant, owner, evidence, state, or rationale fails before
persistence. Production adapters must make request mutation and audit append
atomic, define idempotency, and surface safe recovery without duplicate effects.

## Timeouts and retries

## Idempotency

## Observability

## Deployment

## Migration and rollback

Local adapters require no migration. Each production adapter needs a separate
ADR covering schema evolution, backfill, compatibility, rollback, retention,
and observability before activation.

## Known debt

The reference slice intentionally has no production identity, database,
notification, immutable audit, or deployment integration.

## Related ADRs
