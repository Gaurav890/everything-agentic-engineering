# Signalroom design contract

## Visual thesis

**Editorial operations desk.** Signalroom should feel like an exacting newsroom
and a calm control room: dense enough for professional supervision, restrained
enough that one consequential decision dominates.

Personality: exact, composed, candid, tactile, quietly urgent.

The interface must not resemble a generic purple AI dashboard, Anthropic,
Vercel, Linear, shadcn defaults, or a chat application.

## Composition

- A narrow black command rail anchors identity and global controls.
- A warm off-white work surface carries plans and evidence like annotated paper.
- A dark graphite inspector elevates the pending human decision.
- Rules, alignment, and typography establish hierarchy before containers.
- Corners stay mostly square; small radii indicate interactive affordance.

## Typography

- Display and headings: `Instrument Serif` when available, with Georgia fallback.
- Operational text: `Inter`/system sans.
- Identifiers and evidence metadata: system monospace.
- Large numerals are used only when they communicate real progress or priority.

## Color

- ink: near-black, not blue-black;
- paper: warm ivory;
- signal: safety orange for attention and active control;
- success: restrained green;
- danger: direct red;
- muted information: cool gray.

Color encodes state and attention; it does not decorate surfaces.

## Signature behavior

The **run ribbon** is a horizontal, labeled sequence of consequential phases.
The active phase carries an orange edge and expands into its workstream. It
makes agent progress tangible without imitating a chat transcript.

## Motion

120–220ms transitions communicate selection, expansion, approval, and pause.
Continuous animation is limited to a small live-status indicator and respects
reduced motion.

## Accessibility

- WCAG AA contrast target;
- complete keyboard navigation;
- visible focus;
- 44px mobile targets;
- status never communicated by color alone;
- controls use explicit labels and live feedback.

## Component sourcing

No third-party visual component is copied. Lucide may supply neutral icons.
Repository design tokens supply primitives and semantic intent; showcase-local
CSS translates them into this product-specific language.
