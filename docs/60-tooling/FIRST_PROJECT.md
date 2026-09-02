# Your first useful feature

The web path is runnable locally. Start with one useful change, prove it works,
and repeat. The initial design lab is a reference, not your finished product.

## Start and resume

From the starter, run `./agentic setup create`, then copy its final continuation
command. That one command enters the generated directory and runs `./agentic
start`. It prepares a brief-aware conversation in your chosen installed terminal
client, or an instruction for your editor/app. Native sign-in stays in that
client; no keys are collected here. Use `./agentic next` later to resume. See
[the complete handoff](PROJECT_ONBOARDING.md).

Web prerequisites are Python 3.11+, Node.js 20.9+ (22 LTS is the tested baseline),
and the pnpm version declared in `package.json`. No paid service or API key is
needed for the supplied local examples. Dependency and browser downloads remain
explicit actions. Review them before running them.

The guide reads current profiles and task state, not the old creation choices.
It never installs, edits tasks, approves a direction, starts a branch, or merges.
If several workstreams are active, use `./agentic next --task T-101` to select
one. Substitute the actual task ID; the guide prints the available choices.

## Make it yours

Custom projects begin with no proposed directions. The assistant uses your
saved product brief to confirm one outcome, discuss palette/type/motion intent,
and build real previews. Existing-brand mode preserves your brand; reference
mode explicitly opts into the three examples. Record evidence-backed approval before
compiling canonical tokens. A new feature should preserve that approved system
unless you explicitly request a redesign.

Your scope and first journey are established before design approval. After
tokens are compiled, `next` helps move into a bounded implementation task. Your
project-specific starting brief is in `docs/10-product/FIRST_FEATURE.md`.
Choose one outcome: for example, helping someone find a relevant case study or
filtering a decision queue. Define the useful behavior and its failure/recovery
states. Do not begin by selecting another tool or adding arbitrary animation.

The planning request produces a requirement, acceptance criteria, ownership,
verification plan, and one bounded task. Review that scope before implementation.
An empty ledger is normal: it means you have not chosen the first feature yet.

## Version control

Generation deliberately does not initialize Git. Before committed feature work,
ask your coding assistant to:

1. Check whether this directory has its own repository; a parent repository
   must not be mistaken for this project's history.
2. Propose a local `main` initialization only if needed, inspect ignore rules,
   and show the exact source files to stage. Exclude credentials, dependencies,
   caches, and generated evidence containing sensitive data.
3. Create a reviewed source-only checkpoint. Do not stage all files blindly.
4. Ask where the project belongs before creating or attaching a GitHub remote.
   Do not push to the starter's repository or another guessed destination.
5. Commit the accepted task plan, then preview `./agentic task start <TASK-ID>`.
   Its output requests explicit confirmation before creating the workspace.

Local development does not require a remote. When collaboration moves to
GitHub, follow the issue/PR policy and record the correct tracking contract.

## Build, prove, review, repeat

`next` distinguishes planning, dependencies, implementation, blockers, review,
and post-merge closeout. It does not mistake a branch's `done` record for a
verified merge. Closeout checks live truth separately.

| Command | What it proves | What it does not prove |
|---|---|---|
| `./agentic verify full` | Repository contracts plus available lint, type, and unit checks; the generated-project scope is smaller than the starter's maintenance suite | A running application, visual fidelity, or production readiness; missing package checks are explicitly reported |
| `./agentic verify web` | Requires local dependencies and Chromium; runs repository checks, a production web build, interaction tests, and automated accessibility checks | Visual comparison, manual accessibility, security certification, or human approval |
| `./agentic verify visual` | Builds the web app and compares existing screenshots on the current platform | Baseline creation or approval, interaction coverage, or subjective design quality |

If Chromium is missing, the command explains the explicit download step:
`pnpm --dir apps/web install:browsers`. It never performs the download itself.
Tests launch their own local server; close any server already using port 3012.

Put new feature acceptance tests in `apps/web/tests/**/*.spec.ts`; `verify web`
discovers them, not just the supplied reference suite. Mark screenshot-only
tests with `{ tag: "@visual" }` so `verify visual` runs them separately. Do not
tag interaction or authorization tests as visual to skip them. The shared
test configuration refuses baseline updates by default.

Record actual command results and scope in the draft PR. A skipped, missing,
failed, or timed-out check is not passing evidence. Use `./agentic task finish
<TASK-ID>` only after the relevant application and independent checks are
recorded; this command itself runs repository verification, not the browser suite.

The reviewer can request changes or say `T-101 approved` for the actual task.
The finalizer then prepares the reviewed branch; the human merge is separate.
Nobody needs to edit the ledger to satisfy PR policy. After merge, close out the
task. Closeout is read-only: review its instructions and local changes, then
return to the updated default branch before running `next` for another useful
change. On the old task branch, `next` intentionally still points to closeout.
Never discard or overwrite uncommitted work to switch branches.

## Visual evidence

New projects do not inherit screenshots approved for the starter. A missing
baseline makes visual verification stop with instructions; it never writes a
replacement and calls that a pass. Comparisons also reject changed screenshots.

For a new project or deliberate redesign, generate candidates explicitly:

```bash
pnpm --dir apps/web build
pnpm --dir apps/web test:visual:update
```

Inspect every candidate at desktop and mobile sizes. A separate human approves
the intended images before they are committed as expectations. Candidate
generation is not approval. Use the existing Web quality workflow's explicit
candidate run for Linux images; do not rename macOS images as Linux baselines.
Then run `./agentic verify visual` in the matching environment. Neither command
certifies that the design is good; the independent critic still examines it.

## Mobile readiness

`mobile` currently supplies selected guidance, contracts, and token outputs;
`apps/mobile` is a placeholder. It is not a runnable Expo application, and
responsive web tests do not prove native behavior. Define the product intent,
then explicitly approve a separate native implementation and device-testing
task. Do not install a native stack or claim platform parity automatically.

## Where to get help

For local setup, share the failing command, tool versions, operating system,
and a redacted error in a repository issue. Do not share `.env`, access tokens,
customer data, browser storage, or unredacted traces.

Maintainers can validate this journey with the
[first-project pilot](../50-evals/FIRST_PROJECT_PILOT.md). Run `./agentic pilot
plan` to create anonymous P1–P5 packets and evaluate the closed scorecards.
Fewer than five valid sessions returns `INSUFFICIENT_EVIDENCE`; its targets are
not claims of measured newcomer success.
