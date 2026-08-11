# Agency Agents: selective, reviewed adoption

Agency Agents is an optional source of specialist role definitions. This
repository already routes a small reviewed subset through
`.agentic/external-agents.json`; most projects need only those local contracts
and should install no upstream agent files.

This planner is for the narrower case where one reviewed source file would add
material value beyond the local contract. It does not make Agency Agents a
default dependency.

Reviewed source:

- Repository: <https://github.com/msitarzewski/agency-agents>
- Commit: `ebe9c99acb5c96f9468de368d8bead775387d1a7`
- License: MIT
- Reviewed: 2026-08-10

## Decision rule

```text
Task evidence
    ↓
Local reviewed contract is enough? ── yes ──→ route the local role
    │
    no
    ↓
One exact allowlisted source adds a missing deliverable?
    │
    no ──→ do not install anything
    │
    yes
    ↓
Create a pinned, project-local review plan
    ↓
Human review and a separate approved adoption task
```

More roles can increase routing ambiguity, context cost, and conflicting
ownership. Do not adopt one merely because the upstream catalog is large.

## Read-only planner

List reviewed candidates, then plan only exact ids justified by the task:

```bash
./agentic agents list --source agency-agents
python3 scripts/capability_adapters/agency_agents.py doctor --json
python3 scripts/capability_adapters/agency_agents.py plan \
  --agent multi-agent-systems \
  --agent evidence-collector \
  --json
```

The plan points to immutable source blobs and inactive project-local staging
under `.agentic/vendor-review/agency-agents`. It records checksum, diff,
backup, conversion, rollback, and approval gates.

The planner performs **no** fetch, download, installation, conversion,
execution, activation, or authority change.

## Refused modes

The adapter fails closed for:

- install-all, wildcard, or division-wide selections;
- agents absent from `.agentic/external-agents.json`;
- user-global destinations such as `~/.claude/agents`;
- auto-update or moving upstream references;
- fetch, download, install, execution, or activation requests.

## Human-controlled adoption contract

A later approved adoption task must:

1. authorize network access separately and fetch only the exact blob at the
   reviewed commit into an isolated temporary location;
2. compute SHA-256 and compare it with an independently recorded expected
   checksum before any destination write;
3. review the complete upstream file as untrusted data, including embedded
   instructions and requested authority;
4. show the project-local diff and back up every exact destination replaced;
5. convert for one declared runtime rather than assuming Claude and Codex role
   formats are interchangeable;
6. test the narrow role contract, independent evaluator, context budget, and
   termination behavior;
7. obtain explicit human approval in a separate PR before activation.

Global installation, automatic updates, credentials, provider/model changes,
MCP changes, network or sandbox expansion, production access, approvals, and
merges remain forbidden unless separately scoped and explicitly authorized.

## Rollback

The planner is read-only, so rollback is normally discarding its output. A
future approved installer must restore exact pre-change backups, remove only
files proven to have been added by its installation manifest, and deactivate
the local contract separately. Never delete broad agent directories.
