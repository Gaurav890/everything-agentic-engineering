# Design decisions

## DD-001 — Example

**Date**

**Decision**

**Context**

**Alternatives**

**Why**

**Evidence**

**Revisit trigger**

## DD-002 — Adaptive intake before canonical design changes

**Date**

2026-08-03

**Decision**

Route design-critical work through an adaptive intake and two or three coherent
directions when appropriate. A human must approve one direction or an explicit
synthesis before the design-system contract or canonical token values change.
Stable semantic roles remain mode-independent; light and dark themes override
those roles, and components consume the semantic roles rather than a named
theme.

**Context**

Generic starter values are useful for proving the pipeline but are not a valid
art direction. Asking every project the same questionnaire also creates noise:
a web-only project should not answer mobile questions, an inherited brand needs
asset fidelity, and a redesign needs migration evidence rather than a blank
canvas. Redesign should be easy where tokens can safely express the change, but
token changes must not pretend to solve information architecture or interaction
problems.

**Alternatives**

- Let the frontend builder choose a palette and update tokens immediately.
- Require one exhaustive questionnaire for every project and platform.
- Bind component tokens directly to `theme.light` or `theme.dark` values.

**Why**

The approved flow separates user intent from implementation, keeps human taste
and brand authority explicit, and makes theme changes predictable without
forcing components to know the active mode. Automated parity, contrast, and
preview evidence catch system failures before a direction is adopted.

**Evidence**

- `design-intake` routes greenfield, existing-brand, redesign, and restrained
  baseline work differently.
- The token validator rejects theme drift, direct component-to-theme aliases,
  missing aliases, and required contrast failures.
- The generated specimen was inspected at desktop and 390px mobile widths.

**Revisit trigger**

Revisit when high-contrast mode becomes an active profile, the project adopts a
visual design authority such as Figma Variables, or product research shows that
the current intake creates avoidable friction.
