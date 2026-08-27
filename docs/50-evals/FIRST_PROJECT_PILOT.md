# First-project pilot

Status: protocol only. No participant results have been collected.

## Question

Can a newcomer create, personalize, and verify one useful web feature without
maintainer intervention? This pilot evaluates usability; it does not certify
enterprise production readiness or native-mobile support.

## Participants and consent

Recruit five people who have not helped build this repository. Include a mix
of frontend experience. Explain the task and obtain consent before observing,
recording, or publishing anything. Use synthetic content. Do not collect
credentials, source belonging to an employer, raw prompts, or personal data.
Keep any recordings private and agree on deletion before recording.

## Session

1. Give the participant only the README and a supported environment.
2. Ask them to generate a web project suited to a real, non-sensitive need.
3. Let them compare directions and personalize the content.
4. Ask them to choose and complete one small useful feature using `next`.
5. Ask them to run the relevant checks and explain what is and is not verified.
6. Ask them to identify how to request review and resume for a second feature.

Do not rescue silently. Record interventions and their reasons. Stop if the
participant reaches an unsafe action or wants to stop. Security intervention
is never withheld to improve a metric.

## Minimal scorecard

| Field | Record |
|---|---|
| Anonymous session | P1–P5; no identity required |
| Environment | OS, Node/pnpm/Python versions, chosen profile |
| Time to first personalized preview | Total minutes; separately note download and tooling time |
| First-feature result | Completed / incomplete; observable acceptance result |
| Interventions | Count and redacted friction category |
| Evidence understanding | Correctly distinguishes checks, visual approval, and production readiness |
| Second-feature start | Could independently identify and begin the next step? |
| Result quality | Independent critique of hierarchy, content specificity, interaction, and accessibility |

## Proposed launch gate

- At least four of five complete creation, personalization, and applicable
  verification without maintainer intervention.
- All five understand local-demo versus production boundaries.
- No repeated blocker remains unresolved across sessions.
- At least four can identify the next feature/review step without a walkthrough.

These are pilot targets, not a statistically representative adoption claim.
Report the small sample, environment, assistance, and failures alongside any
successes. Do not turn internal checks into testimonials. Use findings to choose
the next small product fix before publishing broad usability claims.
