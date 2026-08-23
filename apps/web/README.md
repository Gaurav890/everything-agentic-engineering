# Web experience

This is a runnable Next.js product surface, not a blank scaffold. It opens as a
portfolio design lab with the same realistic content rendered through three
materially different directions.

```bash
pnpm install
./agentic design intake
pnpm dev
```

Compare the directions in the running app. After human review:

```bash
./agentic design approve editorial-signal --yes
./agentic tokens build
pnpm test
pnpm build
pnpm test:e2e
pnpm test:visual
```

The sample content is intentionally specific enough to expose weak hierarchy,
motion, responsiveness, and typography. Replace it with real approved content;
do not flatten the experience back into a generic hero and card grid.

Core motion uses platform primitives and has a reduced-motion path. Add a
specialist runtime only when the approved direction requires it:

- Motion for application choreography and gestures;
- GSAP for timeline or scroll choreography;
- Rive or canvas/SVG for authored 2D scenes;
- React Three Fiber for an approved, performance-budgeted 3D scene.

Advanced motion is never installed or activated automatically.

## Visual-quality gate

Playwright exercises every direction at 1440×960 and 390×844, checks direction
selection, keyboard focus, mobile overflow, reduced motion, and automated axe
findings, then compares six approved Linux screenshots.

Visual baselines are review artifacts, not snapshots to update until CI turns
green. For an intentional redesign:

1. approve the design-system or acceptance change;
2. run the `Web quality` workflow manually with
   `update_visual_baselines=true`;
3. download and inspect `web-visual-baselines-linux`;
4. commit only the approved images;
5. rerun normal comparison.

Local macOS screenshots are exploratory because browser rendering varies by
operating system. CI owns the canonical Ubuntu comparison environment.
