# First-project pilot

Status: runnable protocol. No participant results have been collected.

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

This repository's scorecard does not accept recordings, transcripts, raw
prompts, participant identity, employer or repository details, credentials,
secrets, or personal data. If a separate research program records a session,
keep that material outside this pilot bundle under its own consent, retention,
access, and deletion policy. Only the closed anonymous scorecard may enter the
aggregate evaluator.

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

## Run the pilot

First inspect the contract:

```bash
./agentic pilot plan
```

Create one private local packet per anonymous participant. Use only `P1`
through `P5`; do not replace those identifiers with names or handles.

```bash
./agentic pilot create P1 --output /private/local/pilot --yes
```

Give the participant only the public README. The observer uses `SESSION.md` and
records closed categories in `scorecard.json`. The template intentionally does
not validate until consent, environment, results, and an independent quality
review are complete.

```bash
./agentic pilot validate /private/local/pilot/P1/scorecard.json
```

After all five sessions, evaluate the directory. Without `--output` the command
prints JSON and writes nothing.

```bash
./agentic pilot summarize /private/local/pilot
./agentic pilot summarize /private/local/pilot \
  --output /private/local/pilot/report.json --yes
```

The second form writes a JSON report and a Markdown companion. It refuses to
overwrite either file. Keep session packets private; publish only a separately
reviewed aggregate report, and never convert participant outcomes into
testimonials without explicit permission.

## Minimal scorecard

| Field | Record |
|---|---|
| Anonymous session | P1–P5; identity is prohibited from the scorecard |
| Environment | OS, Node/pnpm/Python versions, chosen profile |
| Time to first personalized preview | Product-flow minutes; download and tooling time is separate |
| First-feature result | Completed / incomplete; observable acceptance result |
| Interventions | Closed stage and redacted friction code; no free-text transcript |
| Evidence understanding | Correctly distinguishes checks, visual approval, and production readiness |
| Second-feature start | Could independently identify and begin the next step? |
| Result quality | Separate evaluator scores hierarchy, content specificity, interaction, and accessibility from 1–5 |

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

The evaluator returns `INSUFFICIENT_EVIDENCE` until all five valid P1–P5
scorecards exist. A complete sample returns `FAIL` when any launch gate misses;
there is no partial-pass label. Quality scores are reported but are not used to
manufacture a usability pass. Distinctive-output benchmarking remains a
separate evaluation.
