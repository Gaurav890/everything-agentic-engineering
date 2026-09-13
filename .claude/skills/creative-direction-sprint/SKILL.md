---
name: creative-direction-sprint
description: Turn a confirmed product outcome into three materially different, live, product-specific design directions before production implementation. Use by default for a fresh custom or existing-brand design-critical project, and when an approved visual system needs an explicit redesign.
---

# Creative direction sprint

This is the default bridge between product intent and implementation. Its output
is not a mood board, a palette menu, or prose. Its output is a small set of real,
working product previews that make a consequential design choice visible.

## Start condition

Read `.agentic/project-brief.json`, `docs/20-design/DESIGN_BRIEF.md`, the first
feature brief, active profiles, existing tokens, and any product-owned references.
Ask only questions whose answers would change the experience. Never repeat saved
answers. If the brief is not ready, settle one useful journey before designing.

For an existing brand, inventory its real assets, type licenses, variables,
components, and constraints. For a new product, do not ask the user to art-direct
raw token values. Ask for examples they love or dislike, desired feeling, density,
motion appetite, available imagery, and any non-negotiable brand constraint. When
they delegate a choice, make and explain a recommendation.

## Diverge before converging

Build three candidates by default. Use two only when the design space is narrow;
use up to five only when each additional candidate tests a real question.

Before code, name one primary axis for every candidate. Valid axes include
information architecture, interaction model, composition, density, visual voice,
content pacing, spatial model, or motion language. Palette, radius, shadows, and
copy alone are not valid axes.

Each candidate must:

- use the same realistic, product-specific content and first useful journey;
- work as an independently shippable answer, not a partial mood board;
- contain the important default, loading, empty, error, success, and recovery
  states relevant to that journey;
- have one signature visual or interaction idea that belongs to this product;
- state its asset strategy: owned assets, generated/commissioned assets,
  illustration, data visualization, photography, 2D canvas, 3D, or intentionally
  none;
- state why motion helps, which interactions move, and how reduced motion behaves;
- work at a narrow mobile viewport and a wide desktop viewport;
- preserve keyboard access, visible focus, contrast, and content clarity.

Do not add 2D, 3D, shaders, parallax, or continuous motion as status decoration.
Use them only when they explain the product, make manipulation clearer, or create
a deliberate brand moment within a measured performance budget.

When a candidate needs an original abstract asset, run
`./agentic design resources --need assets`. Haikei may be recommended for a
human-operated SVG/PNG exploration only when the candidate already names the
asset's product-specific role. Use candidate token colors, record the generator,
parameters, source, date, and license basis, then optimize and review the actual
project-local asset. A generic blob, wave, or gradient is not signature craft.

## Build in isolation

Create candidates under a clearly isolated preview surface, such as
`apps/web/app/design-candidates/<candidate-id>/`. Do not rewrite the production
route or canonical tokens during divergence. Candidate code may share safe
product primitives, but each direction must remain inspectable and removable.

When the reviewed external design-engineering pack is installed, use `prototype`
as the divergence workflow and `emil-design-eng` as the craft pass. These are
accelerators, not hidden prerequisites. If they are absent, follow this contract
directly and report the missing capability; do not silently lower the bar. Keep
the general frontend-design skill secondary and opt-in.

## Register and show the work

For each candidate, create a project-local JSON proposal containing:

- `id`, `name`, `thesis`, and `axis`;
- `composition`, `interaction`, and `signature`;
- `asset_strategy`, `asset_role`, `asset_alternatives`, `motion`,
  `motion_rationale`, `motion_interruption`, `motion_performance_budget`, and
  `reduced_motion`;
- `responsive_strategy`, `states`, and `rationale`;
- `preview_path`, actual `source_files`, and DTCG-compatible semantic tokens.

Register it with `./agentic design propose --file <path> --yes`. Registration is
not approval. Run the product locally and show the live comparison board. Capture
desktop and mobile evidence only after the UI is stable.

## Human decision

Invite the reviewer to choose, combine, revise, or reject all candidates. Record
what wins and what is explicitly rejected. Only the selected or synthesized
direction may move into the canonical design system and token compiler.

## Finish gate

The sprint is incomplete when candidates are theme swaps, content is generic,
interactions are dead, the signature idea is absent, or only source code was
reviewed. Return the axes explored, live preview paths, evidence, tradeoffs,
recommended direction, and the exact human decision still required.
