# Visual QA

## Automated visual-regression contract

The Showcase uses Playwright screenshot assertions for the normal, loading,
empty, and error states at its desktop and mobile project sizes.

The web reference lab uses the same approved-Linux-baseline contract for
portfolio, product, agentic-product, and enterprise-workflow across Editorial
Signal, Kinetic Index, and Quiet Material at desktop and mobile sizes. Its
interaction suite separately verifies keyboard entry, direction selection,
axe results, horizontal overflow, and reduced-motion behavior.

Approved baselines live beside the visual test:

```text
apps/showcase/tests/visual.spec.ts-snapshots/
apps/web/tests/visual.spec.ts-snapshots/
```

Browser rendering varies by operating system. The committed baselines are
generated on the same Ubuntu GitHub Actions environment that performs the
required comparison. Local macOS snapshots are useful for exploration but must
not replace the Linux baseline by accident.

Normal pull requests compare against the committed baseline and fail when more
than 0.1% of pixels exceed Playwright's perceptual threshold. On failure, CI
uploads the actual, expected, and diff images for review.

When web baselines are absent, CI generates and uploads candidates, then fails
closed until reviewed Linux images are committed. This makes first-run setup
obvious without turning automatic generation into visual approval.

An intentional redesign uses this process:

1. Confirm the design-system and acceptance changes are approved.
2. Run the relevant `Showcase` or `Web quality` workflow manually with
   `update_visual_baselines=true`.
3. Download and inspect the Linux baseline-candidate artifact.
4. Replace only the snapshots that represent approved changes.
5. Commit the reviewed baselines on the task branch.
6. Run the normal comparison again before merge.

Baseline generation is never approval. A separate reviewer must inspect
intentional visual changes.

## Page/state template

### Route/state

**Viewport**

**Evidence**

**Hierarchy**

**Typography**

**Spacing**

**Interaction**

**Accessibility**

**Issues**

**Verdict**
