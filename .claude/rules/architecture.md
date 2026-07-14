# Architecture rules

- Prefer explicit module boundaries and typed contracts.
- Keep domain logic independent of UI frameworks where practical.
- Document external boundaries, trust boundaries, data ownership, and failure modes.
- One default backend per product profile unless an ADR justifies more.
- Add an ADR for irreversible or expensive-to-reverse choices.
- Keep API contract changes synchronized with tests and docs.
- Avoid premature microservices.
