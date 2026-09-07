# From your idea to your first useful feature

Run **`./agentic start`** in the starter to create a project, then run the same
command in the generated folder whenever you resume. Research, custom design,
reference, enterprise, mobile, and core routes remain different internally,
but users do not need to select internal profiles or remember a different first
command. `./agentic journey` explains the detailed path; `./agentic next`
returns the current low-level action for advanced use.

## What happens

1. Creation captures the product idea, audience, and desired outcome before it
   recommends an editable plain-language path. It then asks whether current
   research should shape the first pass and how design should begin. Unknown
   answers can wait; “recommend for me” is valid.
2. When research is selected, the project creates a source-ledger contract and
   routes current evidence before scope/design. Perplexity is preferred when
   configured; primary-source/manual research is the explicit fallback.
3. Your new README, vision, PRD, acceptance draft, copy, and engineering context
   describe **your project**. Drafts are not fabricated research or built features.
4. The creation receipt previews the remaining journey and confirms that
   nothing was installed or launched and no API key was collected.
5. The printed `start` command prepares a specific, profile-aware instruction
   and asks which existing coding client or manual editor should continue.
   It displays the folder and asks before launching. In an editor or desktop
   app, open that same folder and paste the supplied instruction instead.
6. The assistant reads the saved brief and asks only unresolved consequential
   questions. You agree one useful journey. A custom design-critical web
   project then compares three materially different live directions by default;
   reference, mobile, and core profiles follow their narrower contracts.
7. Approve the scope and design separately. Approved design decisions become
   tokens; implementation follows the ordinary test, review, and PR workflow.

Run `./agentic journey` to see all six stages and their current status. Run
`./agentic next` when you want only the exact next action. Neither command
changes project state.

## Current research is an explicit product decision

Choosing Perplexity-first research activates the existing `research-enabled`
profile and generates `docs/10-product/RESEARCH.md`. It does not configure the
project's empty `.mcp.json`, install a server, start a network request, or ask
for a credential. Configure Perplexity through the selected client's reviewed
MCP path and keep `PERPLEXITY_API_KEY` in environment or user scope.

If Perplexity is unavailable, use official/first-party sources manually and
record the fallback. Firecrawl is for authorized extraction from known sites;
Playwright is for interaction and behavior. The coding assistant records human-
readable sources in `docs/10-product/RESEARCH.md` and may set the validated
`.agentic/research.json` state to `complete` only after recording the route,
source URLs, synthesis, changed/no-change decision, product changes,
uncertainties, and SHA-256 bindings to the ledger and before/after brief. The
brief records the ledger digest. Do not edit status text in Markdown to advance
the workflow. Research is evidence, not scope or design approval.

The initial custom-project page is a workspace showing your brief and handoff,
not a claim that your product is finished. The next session must build real
previews and then the accepted first feature. This is not an unattended site
generator or a guarantee of exceptional design without critique and iteration.

## Use the account you already have

Choose Claude Code, Codex, or a manual editor/app handoff. Native sign-in stays
inside that client's own interface. The starter does not read login tokens,
accept passwords, provide its own subscription login, or require an API key.
Clients and accounts must already be available, or you install/sign in through
their official setup separately. An unsupported client can use the manual
instruction, but may need its own skill-discovery configuration.

Reference: [Claude Code authentication](https://code.claude.com/docs/en/authentication)
and [Codex authentication](https://developers.openai.com/codex/auth/).
Their usage/billing is separate from any future model-powered feature inside
your product. Never place development-assistant credentials in product code.

`./agentic design sprint --json` is read-only. `--assistant claude`, `--assistant codex`,
or `--assistant manual` overrides the saved choice for that handoff. A native
session requires terminal input/output and confirmation; it receives a fixed
instruction with the project as its working folder. User answers are read as
project data, never interpolated into a shell command. No bypass-permission,
model, sandbox, network, or provider flags are added.

## Your design is not a preset

| Starting approach | What it means |
|---|---|
| Custom (default) | Start with an empty candidate catalog; create directions from this product's content and interactions. |
| Existing brand | Interpret your supplied brand and product references, then propose compatible previews. |
| Reference | Deliberately start with the bundled example lab. Its sample content and three styles are references, not your product's requirements. |

There is no maximum of three candidates. Three is the default first review;
use two when the space is narrow and up to five only when every additional
candidate tests a real question. Request another, combine ideas, or reject all.
Palette is only part of a direction. Compare layout, hierarchy, typography,
copy, density, interaction, focus, recovery, and purposeful motion. Advanced
2D/3D is conditional on the product need, performance, and reduced-motion plan.

Installed design skills are used at the appropriate phase. For a fresh custom
or existing-brand sprint, the reviewed `prototype` skill is routed when present;
the local `creative-direction-sprint` contract remains the fallback. Missing skills are
reported as missing, not claimed as executed. References and component sources
remain inputs to the project design system, never automatic aesthetic authority.

## Candidate contract (for the implementation assistant)

First build a real local preview route. Keep experimental styling scoped to
that preview. Save a project-local JSON proposal with these fields:

- `id`: unique lowercase kebab-case, including a new revision ID for changes;
- `name`, `thesis`, and `axis`: the direction and the primary experiential
  question it explores;
- `composition`, `interaction`, `signature`, `rationale`, and `motion`: meaningful text;
- `asset_strategy`, `motion_rationale`, `responsive_strategy`, and
  `reduced_motion`: explicit craft and resilience decisions;
- `states`: at least three distinct realistic states for the first journey;
- `preview_path`: local route such as `/concepts/purchase-path`, not a URL;
- `preview_source`: the actual UI entry included in `source_files`;
- `source_files`: existing project-relative preview code **and every shared
  dependency/asset affecting its appearance**, under `apps/` or `packages/`;
- `tokens`: flat semantic paths mapped to DTCG `$type` / `$value` objects.

Do not list `packages/design-tokens/generated/direction.css` as a source: it is
the output of approval and includes that approval's fingerprint. Listing it
would make a build invalidate itself. List preview code and canonical token
inputs instead; `./agentic tokens build --check` separately checks derived output.

Required semantic paths are `color.background.canvas`,
`color.background.surface`, `color.text.primary`, `color.text.secondary`,
`color.action.primary.default`, `font.family.display`, `radius.lg`, and
`duration.normal`. Additional overrides are supported. Supported values are
DTCG sRGB color objects (0–1 components/alpha), font-family arrays, dimensions
in px/rem, and durations in ms/s. References and other types belong in the
canonical token package, not this small preview override format.

The actual UI entry cannot be one of the starter demo surfaces, and candidates
in the same catalog cannot reuse the same named axis. Register the proposal with
`./agentic design propose --file <local.json>` to
inspect it, then repeat with `--yes`. Registration never approves it. Do not
merely rename an example or supply a screenshot without a functioning preview.

Complete the intake and confirm the product brief before approval. Capture
screenshots and notes from the exact preview under `docs/50-evals/`, including
responsive, keyboard, contrast, and reduced-motion checks. After direct human
approval, run `design approve <id> --approved-by <reviewer> --evidence <path>
--yes`; repeat `--evidence` for additional screenshots/review notes. The terminal
asks for a screenshot path when it was omitted. It does not capture or judge
screenshots on the human's behalf.

Approval fingerprints bind the selected candidate, completed intake, project
context, **listed** source files, and submitted evidence. Listing all relevant
source dependencies is a review responsibility, not automatic dependency
analysis. Changes invalidate that approval; they do not silently bless a new
palette. `./agentic tokens build` compiles approved overrides. Use
`./agentic design reset --yes` to return to unapproved experimentation, then
re-review. Resetting is not approval or an accepted visual baseline.

The fingerprint detects drift, not screenshot authenticity, accessibility,
subjective quality, or production readiness. Separate tests and independent
review still apply to the actual feature.

## What is retained, and what becomes yours

The brief and product documents become project-owned, editable truth. Later
sessions update them deliberately and preserve your edits; creation is never
rerun over an existing project. Starter operating agreements, license,
provenance, workflow guides, and security policies remain reusable foundation.
Research catalogs remain references, not claims about your product.

Keep the brief suitable for display: its name, audience, promise, outcome and
design preferences appear in the local workspace and generated documents. Do
not put secrets, customer records, or confidential research into those fields.
This workspace has no authentication; keep it local and do not publish it with
private content. No telemetry or automatic retention/deletion service is added.
Your files remain until you change them; copies in version control, backups or
your chosen client's session have separate retention. Removing a current file
does not erase those copies or duplicate text in the generated documents.
Review content before sharing or committing it.

Existing generated projects are **not migrated automatically**. In particular,
their source, tokens, and approvals must not be overwritten. Review their
current product work, then deliberately adopt the brief/handoff/candidate
contract on a separate branch. Older approvals without evidence require review.

For mobile/core, the same saved-brief conversation applies, but the repository
still does not promise a runnable native application. Agree its implementation
and device-testing scope explicitly. For enterprise, generated contracts and
local adapters remain reference scaffolding until reviewed for the real domain.
