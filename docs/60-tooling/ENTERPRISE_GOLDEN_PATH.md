# Enterprise golden path

The enterprise archetype is a credible starting product, not a decorative
dashboard and not a production deployment.

## Start

```bash
./agentic setup create
```

Choose `enterprise-workflow`. After the five core setup decisions, answer only:

1. What business object is governed?
2. Is the product single-tenant or multi-tenant?
3. Does approval use a single reviewer or dual control?
4. What is the highest data-sensitivity level?

The generator shows the complete plan and asks once before writing. It installs
nothing, connects nothing, and enables no external authority.

## What works immediately

The generated web product includes one complete vertical slice:

```text
Create request
→ validate required evidence
→ submit for review
→ assign reviewer
→ approve / reject / request changes / cancel
→ append audit event
→ recover from empty, invalid, loading, and failure states
```

The interface includes tenant context, role switching, owner/assignment-scoped
reads, cross-tenant denial, self-approval prevention, evidence verification,
submission and resubmission, decision rationale, and an append-only local audit
trail. Audit attribution is constructed inside the service boundary. It can be
compared through all three approved design directions on desktop and mobile.

The approval choice changes executable policy:

- `single-review` permits an eligible same-tenant reviewer;
- `dual-control` requires the assigned reviewer to differ from the owner;
- `policy-gated` adds a recorded passed policy gate before approval.

## What is generated

- `.agentic/enterprise.json` — machine-readable workflow and authority contract;
- `docs/10-product/PRD.md` and `ACCEPTANCE_CRITERIA.md`;
- `docs/10-product/USER_JOURNEYS.md`;
- `docs/30-engineering/ARCHITECTURE.md`, `DATA_MODEL.md`, and `API_CONTRACTS.md`;
- `docs/30-engineering/SECURITY_MODEL.md`, `ROLE_MATRIX.md`, and `AUDIT_EVENTS.md`;
- an initial task graph tied to the generated acceptance contract;
- domain, API, persistence, and type package boundaries;
- Playwright interaction and visual-evidence contracts scoped to the selected
  enterprise archetype.

## Authority boundary

The supplied adapters are deliberately local:

| Concern | Generated state | Production replacement |
|---|---|---|
| Authentication | local demonstration actor | organization identity provider |
| Authorization | pure, tested domain policy | server-enforced policy using verified identity and tenant claims |
| Persistence | in-memory repository | transactional tenant-scoped database adapter |
| Notifications | disabled | idempotent queue/outbox adapter |
| Audit | local append-only events | durable immutable audit store and retention policy |

`production_ready` remains `false` until those boundaries are implemented,
threat-modelled, observed, and independently reviewed. The starter never calls
a demo selector “authentication,” and it never treats a browser-only rule as
production authorization.

## Build sequence

Run `./agentic next` and follow one action at a time:

1. restore dependencies;
2. compare the three directions in the running product;
3. approve or synthesize one direction;
4. compile tokens;
5. run full verification;
6. decompose the generated production-boundary tasks;
7. implement adapters behind the existing interfaces;
8. open a reviewed pull request with security, data, migration, and rollback
   evidence.

## Enterprise definition of done

A feature is not done because its happy path renders. It must show evidence for:

- tenant isolation and role authorization;
- allowed and denied state transitions;
- self-approval and cross-tenant rejection;
- idempotency, concurrency, retry, and rollback behavior;
- loading, empty, invalid, partial, failure, recovery, and success states;
- accessible keyboard and reduced-motion behavior;
- responsive running-product evidence;
- append-only audit consequences;
- production adapter status and unresolved risks;
- independent review separate from the builder.

This golden path is intentionally narrow. It proves the system can guide a
team from product intent to a credible, reviewable enterprise slice without
pretending that generic scaffolding is production software.
