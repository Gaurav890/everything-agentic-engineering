# Test matrix

| AC ID | Scenario | Layer | Method | Evidence | Status |
|---|---|---|---|---|---|
| AC-001 | Guided creation selects only relevant profiles and one next action | Generator / smoke | Unit + clean downstream project | `evidence/T-044/README.md` | Pass |
| AC-002 | Enterprise allowed and denied request transitions | Domain / API / E2E | Node tests + Playwright | `evidence/T-044/README.md` | Pass; independent review pending |
| AC-003 | Generated enterprise artifacts share one intake contract | Generator | Unit + generated-project full verify | `evidence/T-044/README.md` | Pass |
| AC-004 | Four archetypes × three directions × desktop/mobile | E2E / visual | Axe + Playwright screenshots | `apps/web/tests/visual.spec.ts-snapshots/` | macOS pass; Linux human review pending |
