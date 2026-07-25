# Release runbook

Releases are human-gated. No agent, scheduled workflow, research loop, or merge
to `main` may create a public tag or GitHub release without a maintainer
explicitly choosing to publish it.

## Release contract

Every release must have:

- a semantic version in the root `package.json`;
- a matching `v<version>` entry under `docs/releases/`;
- a curated changelog entry;
- current compatibility and known limitations;
- a clean-checkout onboarding smoke test;
- full repository verification;
- passing required GitHub checks on `main`;
- a reviewed release artifact and checksum;
- an explicit maintainer publish decision.

## Prepare a release candidate

1. Create or confirm a release task.
2. Branch from an up-to-date `main`.
3. Update the version, changelog, release notes, compatibility, README, and
   durable execution state.
4. Run:

   ```bash
   ./scripts/release-check.sh v0.1.0
   ./scripts/release-smoke-test.sh
   ./scripts/verify.sh full
   ```

5. Open a pull request and merge only after checks and review pass.

## Build without publishing

From GitHub Actions, open **Release** → **Run workflow**, enter the version, and
leave **Publish GitHub release** unchecked.

The workflow validates the clean checkout, runs the full suite, builds a
versioned source archive, generates a SHA-256 checksum, and uploads both as a
workflow artifact.

Inspect the downloaded archive before publishing.

## Publish

Publishing is a distinct decision after the release-candidate changes are on
`main`:

1. Confirm `main` is green and the candidate artifact was reviewed.
2. Run the **Release** workflow again with the exact version.
3. Check **Publish GitHub release**.
4. Confirm the generated GitHub release contains the curated notes, archive,
   and checksum.
5. Add the repository topics and social preview listed below if missing.
6. Publish launch announcements only after the release URL is live.

The workflow refuses to overwrite an existing tag or release.

## Repository launch metadata

Recommended GitHub topics:

```text
agentic-engineering
ai-agents
claude-code
codex
design-systems
developer-tools
mcp
multi-agent
product-design
software-engineering
```

Recommended repository description:

> A production-grade operating system for shipping software with AI coding
> agents: durable context, product design, skills, MCPs, task orchestration,
> security gates, evidence, and GitHub workflows.

Use `docs/assets/quickstart-flow.svg` as the basis for a 1280×640 social
preview. Uploading the preview in GitHub settings remains a maintainer action.

## After publishing

- Verify the public release and archive checksum.
- Test the README clone command in a new directory.
- Publish the approved launch copy.
- Watch issues and discussions for onboarding failures.
- Record factual feedback in the learning ledger.
- Fix critical release defects through a normal `fix/` branch and patch release.

Do not silently edit release claims after launch. Correct inaccuracies through
the changelog, documentation history, and a patch release when necessary.
