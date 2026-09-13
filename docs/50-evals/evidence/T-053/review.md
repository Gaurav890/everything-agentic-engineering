# T-053 visual-resource routing evidence

Reviewed: 2026-09-13
Issue: #85
Review mode: independent read-only design and security reviews after implementation

## Outcome

**PASS.** The project now routes three visual-craft resources only when current
design evidence justifies them:

| Resource | Eligible use | Durable return |
|---|---|---|
| Realtime Colors | Palette or typography remains unresolved during intake or direction work | Design brief, candidate semantic roles, screenshots, contrast and font-license evidence |
| Haikei | A direction records a product-specific generated-asset role and alternatives considered | Project-local asset, closed provenance record, token mapping, accessibility and running-product evidence |
| Motion Primitives | Web direction is approved and records purpose, interruption, performance and reduced-motion behavior | Reviewed component revision, token mapping, interaction, accessibility and performance evidence |

No resource is installed, copied, downloaded, opened, authenticated, submitted
to, or executed automatically. External content remains untrusted, and the
project design system and human approval remain authoritative.

## Source provenance

- Motion Primitives official documentation and repository were reviewed at
  revision `40f59b61e567712aa8329c7dc8c2ced763054c34`; upstream labels the
  project beta and publishes it under MIT.
- Haikei's official product, generator, pricing and terms pages were reviewed;
  no official source repository is claimed.
- Realtime Colors' official hosted product and contrast documentation were
  reviewed with its published repository at revision
  `4be24a05ba126f38d6946e8f0ba811c454cd209a`. The repository says its source is
  no longer current. Color choices remain user decisions; font licensing must
  be verified independently and the published website source is not copied.

## Contract integrity

- The safety policy is a closed exact-value schema and fails closed if an
  automatic-action boundary is weakened or an unknown field appears.
- Terminal control characters are rejected recursively before catalog values
  can reach terminal output.
- Generated assets remain inside approved project paths and may not traverse
  symlinks.
- Their recorded pixel dimensions must match the PNG IHDR or SVG viewport.
- Asset files and structured evidence records are bound to current SHA-256
  digests, and token roles must resolve to the canonical semantic DTCG catalog.
- Empty and placeholder decisions such as `n/a`, `TBD`, `none`, or
  `placeholder` cannot unlock asset or motion routes.
- Generated design-critical projects receive the same catalogs, validation,
  handoff and no-mutation contract. Profiles without design-critical scope do
  not receive or silently activate this state.

## Verification

- `72` focused design, generator and handoff tests pass.
- `./agentic design check` passes with three directions and zero generated
  assets in the starter.
- Full repository verification passes all ten stages as part of
  `./agentic verify web`.
- The production web build passes.
- `25` interaction and automated-accessibility browser checks pass; `11`
  non-applicable cases are skipped.
- `24` reviewed visual comparisons pass without updating baselines.
- `git diff --check` passes.

## Independent reviews

The design reviewer initially blocked the change because asset/evidence
identity, dimensions and semantic token roles were not fully enforced, and
placeholder prose could unlock routes. Those findings were corrected and the
re-review passed with no remaining design blocker.

The security reviewer initially found fail-open policy and untrusted-output
handling gaps. The final re-review passed: the policy is closed, terminal
controls are rejected, project paths and symlinks are constrained, external
actions remain manual, and no new execution authority exists.

The integration reviewer exercised current web, reference-web, mobile, and core
profiles, verified profile-authoritative propagation and exclusion, confirmed
the human and JSON output contracts are read-only, and passed the final
cross-layer review after adding the width/height-only SVG regression.

## Residual limits

Digests prove identity and freshness, not aesthetic or semantic quality. A
person must still inspect every exported SVG/PNG and copied motion component,
review the exact dependency/source revision, exercise the running interface,
verify assistive-technology and reduced-motion behavior, and approve the design.
This task does not certify a future palette, asset, animation, or product as
high quality merely because its record validates.
