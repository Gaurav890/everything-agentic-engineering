# Downstream project generator

The project generator turns this reusable starter into a clean downstream
project without pruning the source checkout.

## Choose between `init` and `create`

Use `setup init` when maintaining this repository or an existing copy and only
changing its active profile manifest:

```bash
./agentic setup init --name my-product --preset web-supabase --dry-run
```

Use `setup create` when starting a new product in a separate directory:

```bash
./agentic setup create
```

This is the default human flow. It progressively asks for the project name,
destination, first experience, audience, promise, and visual character only
when those answers affect the selected surface. Enterprise workflows then ask
only four additional decisions: the governed business object, tenant model,
approval model, and data sensitivity. It shows the complete plan and asks once
before writing.

Use explicit flags for automation or repeatable scaffolding:

```bash
./agentic setup create \
  --name "My Product" \
  --destination ../my-product \
  --preset web-supabase \
  --archetype product \
  --audience "operations teams replacing fragmented handoffs" \
  --promise "Turn a complicated workflow into calm, measurable momentum." \
  --visual-character precise \
  --dry-run
```

Review the plan, then repeat it with explicit confirmation:

```bash
./agentic setup create \
  --name "My Product" \
  --destination ../my-product \
  --preset web-supabase \
  --yes
```

Use `--json` with `--dry-run` for a machine-readable review artifact.

## What the plan shows

Every plan reports:

- project name and generated slug;
- exact destination;
- selected and dependency-expanded profiles;
- profile-managed paths included and excluded;
- tracked file count;
- external setup that remains pending;
- source version, commit, and dirty-state disclosure;
- web archetype, audience, promise, and starting visual character when active;
- enterprise workflow contract when that archetype is selected;
- mutation and authority boundaries.

Dry-run performs no writes.

## Copy contract

The generator copies a reviewed core from tracked source files and applies
profile-specific path rules:

| Selection | Included surface |
|---|---|
| `web-next` | runnable archetype-aware direction lab, design-critical foundation, UI behavior primitives, web owner/rules, shared app packages |
| `mobile-expo` | `apps/mobile` placeholder (not a runnable native app), design-critical foundation, mobile owner/rules, shared app packages |
| backend profile | API/database/shared packages and backend owner/rules |
| `design-critical` | intake/approval state, three DTCG-compatible directions, design command, and token package |
| `research-enabled` | Research owner/rules and credential placeholders |

Signalroom, historical evidence, launch assets, release artifacts, source
tasks, source progress, and generated token build output are not downstream
project state. They are excluded.

The generated project receives:

- a project-specific README;
- a web first-feature brief with the chosen audience, promise, and an editable
  outcome example; it does not invent approved requirements;
- a machine-readable `.agentic/experience.json` for web identity, audience,
  promise, archetype, and starting visual character;
- a machine-readable `.agentic/enterprise.json` for workflow state, roles,
  evidence, tenancy, approval policy, audit events, and adapter boundaries;
- selected `.agentic/project.json` profiles;
- `.agentic/generated-project.json` provenance and path decisions;
- project-specific package and plugin identities;
- runnable root web scripts when `web-next` is active;
- the reviewed workspace lockfile for web/mobile dependency restoration;
- captured first-run design intent and an unapproved direction state when a web
  experience is active;
- an empty task ledger;
- reset current-state, progress, handoff, risk, and blocker files;
- an empty `.mcp.json` so no server is enabled implicitly;
- only the environment-variable placeholders relevant to selected profiles.

## Safety contract

The generator fails closed unless:

- the destination is outside the starter checkout;
- the destination does not already exist;
- the destination parent already exists;
- the starter is a valid Git checkout so the copy set can come from the Git
  index rather than a filesystem walk;
- profile dependencies and conflicts resolve successfully.

It never:

- modifies or deletes the starter checkout;
- overlays an existing directory;
- copies `.git`, `.env`, dependencies, caches, builds, browser state, or
  historical evidence; environment variants and common credential/key file
  names are excluded even if they were accidentally tracked;
- initializes Git;
- installs dependencies, skills, plugins, runtimes, MCP servers, or backends;
- authenticates, enables network access, deploys, modifies production,
  approves, or merges.

If copying or validation fails, rollback removes only the new directory created
by that exact invocation. The generator records the directory identity when it
creates the destination and refuses rollback if another process replaces that
path. The same identity is rechecked throughout copy and before validation.

Every planned source entry is resolved before destination creation and again
immediately before copy. Parent symlinks must remain inside the starter;
copied symlinks must be relative, remain inside the generated project, and may
not be ancestors of later output. Generated symlinks are checked again after
copy.

## Generated-project verification

The generated project uses the same public verification command:

```bash
cd ../my-product
./agentic verify full
```

Creation-time validation proves the new directory contains only its selected
surfaces, no copied Git/secrets/dependencies, no enabled MCP or specialist, and
an empty task/design state. Ongoing verification deliberately allows normal
Git, dependency, environment, task, approved-direction, and reviewed capability
state. It resolves the profiles currently selected in `.agentic/project.json`
rather than treating creation provenance as current configuration. Newly active
profiles must have their required surfaces, inactive surfaces are rejected, and
profile conflicts fail closed. Activated specialists must match the reviewed
local catalog and current profiles. MCP remains either fully disabled or an
exact match for the reviewed compatibility policy; unknown servers, commands,
packages, and credential shapes fail verification. These checks preserve
manifest shape, safe automatic-install policy, JSON, symlink containment, shell
syntax, Python syntax, command discovery, and profile resolution. When
dependencies are not installed, verification reports package checks as pending.
After `pnpm install --frozen-lockfile`, the same command runs lint, typecheck,
and unit/contract tests for the runnable web surface. It does not build the
application or run browser/visual checks. Use `./agentic verify web` for the
build and interaction/automated accessibility path, then `./agentic verify
visual` for comparison against separately reviewed screenshots. Missing
browser tools or baselines stop with instructions; nothing is auto-installed
or accepted. See [the verification scopes](FIRST_PROJECT.md#build-prove-review-repeat).

Generated web tests and visual baselines are archetype-scoped. Portfolio or
agentic fixtures are never imposed on a product that selected a different
architecture.

## After generation

Run:

```bash
./agentic next
```

It exposes exactly one project-appropriate action at a time. For a generated
web project the path is dependency installation → live direction comparison →
human approval → token compilation → first-feature planning → implementation →
evidence → human review. It reads current profiles and task state; it does not
keep repeating a verification command after setup. Multiple workstreams can be
selected with `./agentic next --task <TASK-ID>`. Mobile and core projects do not
receive web-only instructions. Follow [the first-project guide](FIRST_PROJECT.md).

External skills, MCPs, backend credentials, Git initialization, deployment, and
production authority remain separate, explicit decisions.

## Web archetypes

| Archetype | First composition |
|---|---|
| `product` | product promise, outcome surface, proof principles, operating rhythm |
| `agentic-product` | objective, visible execution, tool/decision states, human approval |
| `enterprise-workflow` | tenant-scoped request queue, evidence review, dual control, decision rationale, append-only audit trail |
| `portfolio` | personal identity, selected work, evidence, working philosophy |

These are content architectures, not themes. Each one can be compared through
the same three coherent direction systems and compiled into the canonical
semantic token layer after human approval.

For the full enterprise contract, generated artifacts, production boundary,
and acceptance evidence, read
[`ENTERPRISE_GOLDEN_PATH.md`](ENTERPRISE_GOLDEN_PATH.md).
