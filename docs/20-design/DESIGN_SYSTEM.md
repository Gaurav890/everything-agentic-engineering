# Design system

Status: Draft

## Visual thesis

What should this product feel like, and why is that appropriate for the user and task?

## Design principles

1. Replace with product-specific principles.
2. Avoid generic slogans.

## Color

Define semantic roles, not just hex values.

| Token | Role | Light | Dark |
|---|---|---|---|
| background | Primary canvas | | |
| foreground | Primary text | | |
| accent | Primary action/emphasis | | |
| danger | Destructive/error | | |

## Typography

| Role | Family | Size/scale | Weight | Usage |
|---|---|---|---|---|
| Display | | | | |
| Heading | | | | |
| Body | | | | |
| Label | | | | |

## Spacing and layout

## Radius, border, elevation

## Iconography

## Motion

Respect `prefers-reduced-motion`.

## Interaction

## Responsive strategy

## Accessibility

## Required states

Every important flow must define:
- loading,
- empty,
- sparse,
- dense,
- invalid,
- error,
- disabled,
- success.

## Anti-patterns

List product-specific patterns to avoid.

Examples:
- gratuitous gradients,
- excessive glassmorphism,
- dashboard cards with no information hierarchy,
- meaningless animation,
- tiny low-contrast text,
- icon-only controls without accessible labels.

## Verification

Important UI must be inspected in the running application with Playwright or equivalent browser evidence.
