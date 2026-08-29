# Installation

Use `./agentic --help` as the command index. The implementation scripts remain
available for compatibility, but the unified interface is the supported path
for new contributors and agents.

## Requirements

- Git
- Claude Code and/or Codex
- Python 3.11+ for project tooling and included guardrail hooks
- For the runnable web path: Node.js 20.9+ (22 LTS is tested) and the pnpm
  version declared in `package.json`
- Mobile currently supplies guidance and a placeholder; choose and verify a
  native runtime separately when implementing it

Claude Code 2.1.239+ and Codex 0.148.0+ are the recommended tested runtime
baselines. The read-only runtime doctor reports drift; it never installs or
upgrades either runtime.
The repository doctor reports an older or missing runtime without upgrading it
or enabling optional capabilities.

## 1. Clone/copy

```bash
git clone <your-repo>
cd <your-repo>
```

To create a clean downstream project instead of adapting the starter in place,
run the guided first-use path:

```bash
./agentic setup create
```

The guide captures only the inputs that change the result, shows one plan, and
asks once before writing. The destination must not exist. The generator copies
no Git history or secrets, enables no MCP server, and installs nothing. Continue
inside the generated directory and run `./agentic start`. See
[Downstream project generator](PROJECT_GENERATOR.md).

The handoff opens a brief-aware conversation after consent, or gives you the
instruction to paste in your existing editor/app. It installs no client and
reads no credentials. See [project onboarding](PROJECT_ONBOARDING.md).

When ready to inspect the generated web workspace or a design preview:

```bash
pnpm install --frozen-lockfile
pnpm dev
```

The brief captures your product intent. Custom and existing-brand modes start
with no preselected designs; your assistant creates product-specific previews.
The three bundled styles appear only in deliberately selected reference mode.
Complete the brief and design intake, inspect actual screenshots, and approve
the chosen direction before compiling overrides. Open the port printed by the
development server; use Ctrl+C to stop it, not Ctrl+Z to suspend it.

After token compilation, `./agentic next` guides the first feature, task
implementation, blockers, and human review. Follow
[Your first useful feature](FIRST_PROJECT.md); no paid service or API key is
needed for the supplied local examples.

`web-next` and `mobile-expo` always resolve the design-critical foundation.
There is no supported application-profile path that silently omits the token,
direction, audit, and independent-evaluation contracts.

The remaining sections are reference paths, **not a mandatory onboarding
checklist**. Skip secrets, external skills, MCPs, backends, and Obsidian unless
your selected project actually needs them.

## 2. Secrets

```bash
cp .env.example .env
```

Only when `research-enabled` is active, add:
- `PERPLEXITY_API_KEY`
- `FIRECRAWL_API_KEY`

Export them only into the shell that launches an approved MCP-enabled runtime.

Example:

```bash
set -a
source .env
set +a
```

## 3. Bootstrap

```bash
./agentic setup bootstrap
```

## 4. Install selected skills when routed

```bash
./agentic setup skills
```

Preview the exact profile-aware commands without installing anything:

```bash
./agentic setup skills --dry-run
```

The project-local skills require no Codex copy step. Codex discovers the same
catalog through `.agents/skills`.

This is an explicit external-install action. It reads the selected project
profiles and installs only their reviewed skill groups into the current user's
Claude Code and Codex skill directories:

- `web-next`: Vercel React and web-design guidance;
- `mobile-expo`: Vercel React Native guidance;
- `design-critical`: Emil Kowalski's ten-skill design-engineering collection.

The Emil installer is pinned to the reviewed commit in
`.agentic/external-skills.json`. A later upstream update requires a new source
review, manifest revision, and normal pull request rather than silently changing
the installed instructions.

Profile selection and `profile doctor` never install anything. The Emil suite
remains externally maintained and is routed one capability at a time through
`design-engineering-quality`. Anthropic `frontend-design` is supplementary and
is intentionally not part of the default install; the installer prints its
separate opt-in command.

## 5. Check MCPs only when routed

```bash
./agentic doctor mcp
```

Inside Claude Code, also use:

```text
/mcp
```

Project-scoped MCPs may require workspace trust/approval.

The Codex adapter intentionally does not translate `.mcp.json` into executable
project configuration. Read `CODEX.md` and configure only the MCP capabilities
required by the selected profile after reviewing their code, credentials, and
permissions.

## 6. Check the selected coding-agent runtime

For either adapter:

```bash
./agentic doctor runtime
```

Use `--strict` for a managed developer image or release validation and `--json`
for inventory tooling. The doctor is read-only.

For Codex:

```bash
./agentic doctor codex
```

Review project hooks with `/hooks` before trusting them.

For a compatible Agent Plugins 1.0 client, validate the portable skills-only
package before testing it:

```bash
./agentic doctor plugin
```

The doctor does not install or publish the plugin. Root `plugin.json` is the
portable manifest; `.codex-plugin/plugin.json` is a separate Codex-native
compatibility file. Project `.mcp.json` is not portable plugin configuration.

## 7. Open Obsidian

Open the `docs/` folder as a vault.

## 8. Choose profile

Read `PROFILES.md` and record the decision in:
- `ARCHITECTURE.md`
- an ADR when the choice is significant.

## 9. Build the PRD before large implementation

Use:
- `create-prd`
- `decompose-prd`
- `parallel-plan`
- `loop-engineering`
