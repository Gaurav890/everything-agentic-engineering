# T-046 — Personalized onboarding evidence

Status: Local implementation and clean-checkout release smoke checks pass.
No product or human approval implied.

## Actual test story

A disposable Afford-style project was generated for households comparing two
purchase dates. Its promise, audience, first outcome and design preferences
appeared in its own documents and workspace. The existing project was untouched.

The initial catalog was empty. A synthetic Purchase Path preview was then
registered at a real local route without approval. This proves custom candidate
routing, not correctness or visual approval of a financial product.

## Completed checks

- 60 focused Python tests: generation, handoff consent, malformed data,
  source/output symlinks, arbitrary candidates, approval fingerprints and drift.
- Nine web contract tests, including real public-data loader validation.
- Generated production build.
- Sixteen generated desktop/mobile browser tests: saved brief, manual handoff,
  clipboard success/pending/failure, focus, overflow, axe, empty catalog, real
  candidate interaction and damaged-brief recovery after repair.
- Full repository verification, 25 reference browser checks (11 intentional
  non-applicable skips), and 24 unchanged macOS visual comparisons.
- New onboarding skill validation.
- `./agentic release smoke` from committed checkpoint `23495cc`: clean-checkout
  guided creation and web, enterprise, mobile and core generation passed.
  This does not install product dependencies or claim native application readiness.

Pending copy is loading evidence; the empty catalog and clipboard fallback are
empty/error evidence. Screenshots show the actual workspace, not an approved
product baseline. Lower-section, custom-preview, keyboard, pending-copy, empty
catalog and damaged-brief recovery captures are included. The retry test found
a stale server-response problem; recovery now explicitly reloads current
context and preserves answers. Desktop and mobile recovery tests pass.

## Reproduction

The fresh-project step in `.github/workflows/web-quality.yml` creates a new
temporary project, copies `tests/fixtures/onboarding/` into that disposable
project only, registers the preview, installs from the existing offline locked
cache without lifecycle scripts, builds and runs the sixteen browser cases.
The fixture test deliberately damages/restores only its temporary copy, with
single-worker execution and `finally` restoration. No fixture is an approved
visual baseline or financial model.

## Limits

Native launch uses mocked argv/cwd/consent tests; no sign-in or live assistant
session ran. Browser checks do not certify screen-reader/native-device behavior.
No newcomer study or measured self-service success is claimed. Source-list
completeness and screenshot authenticity require review; fingerprints do not
certify taste. Existing-project migration remains separate. No external skill
installation, credential collection, service enablement, deployment, task
approval, or merge occurred.
