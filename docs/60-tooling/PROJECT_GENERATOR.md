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
./agentic setup create \
  --name "My Product" \
  --destination ../my-product \
  --preset web-supabase \
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
- mutation and authority boundaries.

Dry-run performs no writes.

## Copy contract

The generator copies a reviewed core from tracked source files and applies
profile-specific path rules:

| Selection | Included surface |
|---|---|
| `web-next` | runnable portfolio direction lab, UI behavior primitives, web owner/rules, shared app packages |
| `mobile-expo` | `apps/mobile`, mobile owner/rules, shared app packages |
| backend profile | API/database/shared packages and backend owner/rules |
| `design-critical` | intake/approval state, three DTCG-compatible directions, design command, and token package |
| `research-enabled` | Research owner/rules and credential placeholders |

Signalroom, historical evidence, launch assets, release artifacts, source
tasks, source progress, and generated token build output are not downstream
project state. They are excluded.

The generated project receives:

- a project-specific README;
- selected `.agentic/project.json` profiles;
- `.agentic/generated-project.json` provenance and path decisions;
- project-specific package and plugin identities;
- runnable root web scripts when `web-next` is active;
- reset design intake and direction state when `design-critical` is active;
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

Generated-project mode validates identity, provenance, selected/excluded
surfaces, empty MCP configuration, empty task state, JSON, symlink containment,
disabled automatic installation/removal, empty specialist activation, shell
syntax, Python syntax, command discovery, and profile resolution. When
dependencies are not installed, verification reports package checks as pending.
After `pnpm install`, the same command runs lint, typecheck, and UI contract
tests for the runnable web surface.

## After generation

1. Read the generated `README.md`, then run `pnpm install` for a web project.
2. Run `./agentic design intake` and compare the live directions with `pnpm dev`.
3. Record human direction approval before canonical implementation.
4. Complete `docs/00-vision/NORTH_STAR.md`, then create the first PRD and task graph.
5. Run `./agentic profile doctor` and review missing external setup.
6. Run `./agentic setup skills --dry-run` only if a selected profile requires
   reviewed external skills.
7. Review MCP and backend setup separately before enabling anything.
8. Initialize a new Git repository only when ready to own that project.
