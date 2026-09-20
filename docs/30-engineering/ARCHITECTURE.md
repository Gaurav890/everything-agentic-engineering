# Architecture

Status: Active reference architecture

## System context

The Product-to-Proof Studio is the local control surface over durable project
contracts. The starter generates profile-scoped projects. The enterprise
reference path uses web and, after T-058, native presentations over explicit
API, domain-policy, repository, and shared-type boundaries. Included data and
identity adapters are local demonstrations.

The control plane and execution engine are not yet implemented. Their accepted
contract is ADR-001 plus `.agentic/product-to-proof.json` and the schemas under
`.agentic/schemas/`.

## Components

| Component | Owns | Must not own |
|---|---|---|
| `apps/web` | interaction, responsive states, accessible evidence | production authorization or durable audit guarantees |
| `packages/api` | use-case orchestration and stable service boundary | UI state or provider-specific persistence |
| `packages/domain` | pure workflow transition and authorization policy | network, credentials, framework, or storage |
| `packages/database` | repository interface and local demo adapter | business transition policy |
| `packages/types` | shared contracts | runtime side effects |
| future Studio control plane (T-055) | read models, allow-listed actions, loopback session | arbitrary shell or provider authority |
| future run engine (T-056) | DAG, waves, journal, reconciliation, adapter lifecycle | approval, deployment, direct `main` writes, merge |

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

```text
task ledger → immutable plan → isolated wave → append-only events
→ reconcile observed state → integration evidence → human continue or stop
```

## Trust boundaries

- user-controlled form and rationale input;
- verified actor identity and tenant claims;
- tenant-scoped repository access;
- external identity, notification, and audit providers;
- agent/runtime tools and generated-project authority.
- loopback browser origin/session and validated project root;
- provider process, inherited environment, hooks, plugins, MCPs, and network;
- run journal versus observed Git/worktree/process/check/PR state.

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

- [ADR-001: Product-to-Proof Studio and supervised-run contracts](ADR/001-product-to-proof-studio-contract.md)
