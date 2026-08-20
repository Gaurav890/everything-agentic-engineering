# Portfolio golden path

This is the opinionated first vertical slice for web projects. Its purpose is to
make a high-quality, product-specific experience easier than a generic first
draft.

## Create and run

```bash
./agentic setup create \
  --name "My Portfolio" \
  --destination ../my-portfolio \
  --preset web \
  --dry-run

# After reviewing the copy plan:
./agentic setup create \
  --name "My Portfolio" \
  --destination ../my-portfolio \
  --preset web \
  --yes

cd ../my-portfolio
pnpm install
./agentic design intake
pnpm dev
```

The intake asks for the product and audience, personality, palette temperature
and expression, typography, density, motion, required modes, advanced-canvas
need, and hard constraints. It records facts; it does not choose an aesthetic.

## Compare before approving

The running app renders one realistic portfolio through:

| Direction | Character | Primary risk |
|---|---|---|
| `editorial-signal` | authored, typographic, case-study led | poor long-title wrapping or an unlicensed display face |
| `kinetic-index` | high-contrast, motion-led, experimental | performance, distraction, or weak reduced-motion hierarchy |
| `quiet-material` | warm, tactile, calm | becoming tasteful but anonymous |

These are not final themes. They are coherent systems that make tradeoffs
visible. The design owner may select one, request revisions, or define an
explicit synthesis.

```bash
./agentic design preview
./agentic design approve kinetic-index --approved-by "Design owner" --yes
./agentic tokens build
```

Approval compiles the chosen DTCG-compatible direction overrides. Components
continue to consume semantic variables; redesign does not require repainting
every screen.

```bash
./agentic design reset --yes
./agentic tokens build
```

Reset returns to comparison and removes compiled overrides. It does not delete
content, rewrite product flows, or pretend tokens can repair interaction design.

## Prove the running result

After dependencies and the Chromium test browser are installed:

```bash
pnpm --filter @everything-agentic/web install:browsers
pnpm test:web:e2e
pnpm test:web:visual
```

The gate covers all three directions at desktop and mobile sizes. It also checks
keyboard entry, explicit selection, automated accessibility findings, mobile
overflow, and reduced-motion behavior. Screenshot assertions run with motion
disabled in a fixed Ubuntu environment so comparisons remain reproducible.

Normal pull requests compare approved baselines and never rewrite them. If a
new project or intentional redesign needs baselines, CI uploads
`web-visual-baselines-linux` candidates. A human reviews those images before
committing them; generation alone is not approval. Failed comparisons upload
actual, expected, diff, trace, and report evidence where available.

This follows Playwright's official
[visual-comparison](https://playwright.dev/docs/test-snapshots) and
[CI](https://playwright.dev/docs/ci) guidance while keeping the repository's
separate-review contract authoritative.

## Motion escalation ladder

Start at the lowest tier that communicates the approved experience:

1. CSS/platform transitions for focus, hover, reveal, and simple continuity.
2. Motion for layout choreography, gesture, and application state transitions.
3. GSAP for a justified timeline, SVG, or scroll-led sequence.
4. Rive, SVG, canvas, or a comparable authored runtime for purposeful 2D.
5. React Three Fiber for a real spatial concept with device and fallback budgets.

Every tier needs a purpose, interruption behavior, reduced-motion result,
performance budget, and independent review. A 3D scene is not evidence of good
design by itself.

## Completion gate

Frontend completion requires:

- approved direction and rationale;
- canonical tokens generated and current;
- real content or clearly marked replacement content;
- keyboard and visible-focus inspection;
- representative desktop and mobile evidence;
- loading, empty, error, dense, and important overlay states when applicable;
- reduced-motion and performance checks;
- responsive, accessibility, token, and system audits;
- a separate critic who did not build the interface;
- Playwright evidence from the running product;
- approved Linux baselines for every shipped direction and target viewport;
- no unreviewed `--update-snapshots` output committed as a shortcut.

The builder may fix critic findings. The builder may not certify its own visual
quality from source inspection.
