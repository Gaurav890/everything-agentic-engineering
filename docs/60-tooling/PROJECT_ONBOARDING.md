# From your idea to your first useful feature

Create a project, enter its folder, then run **`./agentic start`**. That is the
normal next step. You do not need to know the skill names or write a giant
prompt. `./agentic next` helps you resume later.

## What happens

1. Creation captures your product, audience, desired outcome, design approach,
   optional preferences, and preferred coding client. Unknown answers can wait.
2. Your new README, vision, PRD, acceptance draft, copy, and engineering context
   describe **your project**. Drafts are not fabricated research or built features.
3. `start` prepares a specific instruction for the installed client you chose.
   It displays the folder and asks before launching. In an editor or desktop
   app, open that same folder and paste the supplied instruction instead.
4. The assistant reads the saved brief and asks only unresolved questions. You
   agree one useful journey, then compare real product-specific previews.
5. Approve the scope and design separately. Approved design decisions become
   tokens; implementation follows the ordinary test, review, and PR workflow.

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

`./agentic start --json` is read-only. `--assistant claude`, `--assistant codex`,
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

There is no maximum of three candidates. Two or three *in a review round* can
make comparison manageable; request another, combine ideas, or reject all.
Palette is only part of a direction. Compare layout, hierarchy, typography,
copy, density, interaction, focus, recovery, and purposeful motion. Advanced
2D/3D is conditional on the product need, performance, and reduced-motion plan.

Installed design skills are used at the appropriate phase. Missing skills are
reported as missing, not claimed as executed. References and component sources
remain inputs to the project design system, never automatic aesthetic authority.

## Candidate contract (for the implementation assistant)

First build a real local preview route. Keep experimental styling scoped to
that preview. Save a project-local JSON proposal with these fields:

- `id`: unique lowercase kebab-case, including a new revision ID for changes;
- `name`, `thesis`, `composition`, `interaction`, `rationale`, `motion`: meaningful text;
- `preview_path`: local route such as `/concepts/purchase-path`, not a URL;
- `source_files`: existing project-relative preview code **and every shared
  dependency/asset affecting its appearance**, under `apps/` or `packages/`;
- `tokens`: flat semantic paths mapped to DTCG `$type` / `$value` objects.

Required semantic paths are `color.background.canvas`,
`color.background.surface`, `color.text.primary`, `color.text.secondary`,
`color.action.primary.default`, `font.family.display`, `radius.lg`, and
`duration.normal`. Additional overrides are supported. Supported values are
DTCG sRGB color objects (0–1 components/alpha), font-family arrays, dimensions
in px/rem, and durations in ms/s. References and other types belong in the
canonical token package, not this small preview override format.

Register the proposal with `./agentic design propose --file <local.json>` to
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
