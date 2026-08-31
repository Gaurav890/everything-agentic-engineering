# T-047 — Newcomer pilot implementation evidence

Status: deterministic implementation checks pass. Independent product/privacy
review and human approval remain separate. No participant result exists.

## Verified locally

- The committed policy keeps five anonymous P1–P5 sessions and the published
  launch thresholds fixed.
- Session creation previews before writing, requires `--yes`, and refuses to
  overwrite an existing packet.
- Templates cannot validate before consent, environment, outcomes, and a
  separate quality evaluator are recorded.
- Closed validation rejects unknown fields, direct-identifier fields, likely
  secrets, invalid timings, unknown session paths, incomplete privacy flags,
  and missing independent evaluation.
- One through four sessions return `INSUFFICIENT_EVIDENCE`; a complete sample
  can pass only when every gate passes.
- Repeated unresolved blockers fail the complete sample. Interventions remain
  visible and remove that session from the unassisted count.
- Generated core projects retain the same `./agentic pilot plan` command.
- Targeted tests, ten-stage full repository verification, and clean-checkout
  release smoke pass.

## Not claimed

The tests use synthetic scorecards. They do not establish that a newcomer can
use the starter, that generated designs are distinctive, or that any product is
production- or native-ready. No participant was recruited, observed, recorded,
or identified. No scorecard, report, testimonial, dependency, external service,
credential, deployment, approval, or merge was published or enabled.
