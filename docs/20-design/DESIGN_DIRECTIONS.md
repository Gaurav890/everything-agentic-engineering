# Design directions

Status: Needs approval

Use for substantial design-critical work. Compare coherent systems in realistic
product states; do not present accent-color swaps as different directions.

## Evaluation criteria

- Product and user fit
- Differentiation without imitation
- Interaction clarity
- Accessibility and contrast
- Responsive/platform suitability
- Maintainability and token coherence
- Implementation cost and risk

## Direction A — Editorial Signal

### Thesis

An authored editorial portfolio where typography, pacing, and decisive red
accents make case-study storytelling feel considered rather than templated.

### System

Warm paper canvas, ink foreground, muted clay surface, and signal-red action.
Use a serif display voice, compact editorial labels, sharp geometry, restrained
reveals, typographic wipes, and directional hover cues.

### Evidence and tradeoffs

Live in `apps/web` as `editorial-signal` with the same hero, selected work,
process, contact, desktop, and mobile content used by every direction. The final
display face must be licensed or deliberately system-based, and long titles need
editorial wrapping evidence.

## Direction B — Kinetic Index

### Thesis

A high-contrast, motion-led portfolio that behaves like a live creative index
rather than a polite template.

### System

Black, soft-white, and electric-lime; an assertive grotesk display; large scale
shifts; grid structure; ambient geometry; and higher-energy project transitions.

### Evidence and tradeoffs

Live in `apps/web` as `kinetic-index`. This direction carries the highest
performance, distraction, and content-fit risk. Reduced motion must preserve its
hierarchy without continuous animation.

## Direction C — Quiet Material

### Thesis

A warm, tactile portfolio with calm hierarchy and small material details that
reward close attention.

### System

Moss canvas, deep blue-green ink, layered surfaces, a humanist display voice,
generous pacing, and low-amplitude spatial continuity.

### Evidence and tradeoffs

Live in `apps/web` as `quiet-material`. Its risk is becoming tasteful but
anonymous, so project imagery, writing, and one signature interaction must carry
specificity.

## Reference rule

Borrow principles such as pacing, hierarchy, density, or interaction structure.
Do not copy brand marks, assets, copy, layouts, or another product's wholesale
visual identity. Components are structural donors only.

## Required evidence for every direction

- Same realistic content and important states
- Desktop and mobile inspection
- Keyboard and visible-focus behavior
- Reduced-motion behavior
- Contrast and token validation
- Performance and implementation risk

## Decision

- Selected direction or synthesis:
- Why:
- Requested revisions:
- Approver:
- Date:
- Decision ID:

Do not update canonical design tokens until this decision is approved.

Machine state lives in `.agentic/design.json`. Use `./agentic design preview`
to compare and `./agentic design approve <direction-id> --yes` only after the
named human approver makes the decision. `./agentic design reset --yes` returns
the project to comparison without silently rewriting source tokens.
