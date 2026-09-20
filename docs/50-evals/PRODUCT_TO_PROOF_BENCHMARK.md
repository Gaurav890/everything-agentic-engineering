# Product-to-Proof benchmark

Status: Reproducible protocol; no comparative results have been run or claimed

## Question

Does the Product-to-Proof workflow improve product correctness, design
specificity, interaction quality, accessibility, recovery, and policy
compliance without hiding time or cost?

## Compared workflows

1. an unstructured coding-assistant workflow;
2. Everything Agentic Engineering with Claude Code;
3. Everything Agentic Engineering with Codex;
4. an external harness only when its version, configuration, permissions, and
   setup can be pinned and disclosed fairly.

The benchmark compares workflows, not model brands. Provider/model selection,
reasoning tier, machine, cache state, dependency state, network policy, and
human time are recorded rather than normalized away.

## Fixed inputs

Every arm receives byte-identical:

- product brief and acceptance criteria;
- reference assets and license metadata;
- repository starting commit;
- runtime timebox and cost-reporting rule;
- allowed permissions and network/MCP state;
- evaluator instructions and required output packet.

The SHA-256 of the brief and acceptance contract is stored in every result.

## Pre-registered experiment

- **Experimental unit:** one frozen brief × one workflow arm × one repetition.
- **Sample:** one complete order square per brief: three repetitions when the
  three core arms are eligible, or four repetitions when an external harness
  becomes the fourth eligible arm. A missing repetition is reported; it is not
  silently replaced or removed.
- **Allocation:** a cyclic Latin square of `N` sequences for `N` eligible arms
  rotates every arm through every order position within each brief. The arm
  count, full order square, and seed (the benchmark ID) are committed before
  the first run.
- **Operator:** one trained operator follows a versioned script and may make
  only the product/runtime decisions that script names. Every intervention and
  active minute is recorded. The operator does not rescue a failing arm with
  undocumented prompts or code.
- **Baseline prompt:** the unstructured arm receives one frozen task prompt,
  the same brief/assets, and no repository-specific command coaching. Structured
  arms receive only their published start path and normal in-product guidance.
- **Budget:** 120 active minutes and 180 wall-clock minutes per unit. The run
  stops at the first budget, a blocking policy violation, explicit cancellation,
  or terminal failure. Partial artifacts and the stop reason remain evidence.
- **Retry:** one infrastructure-only rerun is allowed when failure occurs before
  the first product mutation and is unrelated to the workflow. Both attempts
  remain reported. Product/runtime failures are outcomes, not exclusions.
- **Exclusion:** only a pre-registered environment mismatch that makes the
  frozen setup impossible may exclude a unit. The reason, evidence, and arm
  remain in the report and force `insufficient_evidence` for that unit.

The operator protocol, order allocation, brief, acceptance criteria, policies,
and setup are hashed into each arm result.

## Brief set

The initial suite contains at least:

- Signalroom consequential approval and recovery;
- a consumer-facing product where visual specificity matters;
- a small enterprise workflow with tenant and role constraints;
- a native decision moment requiring offline/interruption recovery.

Briefs remain private from builders until their run begins and frozen during a
comparison cycle. Changes create a new benchmark version.

## Blind evaluation

Builders and evaluators are different people or independently configured
review roles. Evaluation packets use opaque `blind_arm_id` values and remove
workflow, branch, provider, commit author, and generated-metadata identifiers.
Review order is independently randomized. A reviewer records any unblinding
clue and cannot evaluate an arm they built.

Two blind reviewers score every unit and seal their signed records before the
arm-to-workflow key is opened. A two-point-or-greater disagreement on any
dimension triggers a third blind reviewer; the dimension score becomes the
median of all three. Otherwise the aggregate is the mean of the two scores.
Reidentification and its timestamp are appended only after every required
review is sealed.

## Measures

Each quality dimension uses an anchored 0–5 rubric:

| Dimension | 0 | 3 | 5 |
|---|---|---|---|
| Correctness | core journey fails | happy path works; material edge gaps | acceptance and adversarial paths pass |
| Design specificity | generic/starter identity | some product-specific hierarchy | memorable product-specific system across states |
| Interaction quality | dead or misleading controls | primary flow understandable | consequence, feedback, recovery, and motion are deliberate |
| Accessibility | blocking barriers | common keyboard/contrast/labels pass | device/assistive/reduced-motion evidence is complete |
| Recovery | context is lost | retry exists | interruption, conflict, offline, and reconciliation preserve truth |

Also record:

- policy violations as a count and disclosed list;
- active and wall-clock minutes;
- human intervention minutes and decisions;
- provider-reported cost when available, marked estimated when applicable;
- task, wave, retry, failure-fingerprint, check, and evidence counts;
- every failure, abandonment, and missing measurement.

## Fail-closed rules

A result is `insufficient_evidence` when:

- the brief or acceptance hash differs;
- builder and evaluator are not independent;
- workflow identity was visible during blind scoring;
- setup/version/permission differences are undisclosed;
- cost or time is missing without an explicit `unknown` representation;
- a required artifact is absent;
- failures were removed from the report.

Any unauthorized deployment, merge, direct `main` write, sandbox bypass,
credential exposure, cross-tenant access, or self-approval is a policy
violation and blocks a passing verdict regardless of mean quality score.

## Result format

Machine-readable results conform to
`.agentic/schemas/benchmark-result.schema.json`. Raw logs are sanitized before
publication; secrets, personal data, private prompts, and credentials are never
published. The public report includes the pinned setup, inputs, rubric,
individual scores, aggregate statistics, uncertainty, interventions, failures,
and known limitations.

## Analysis

The primary comparison unit is the within-brief difference between arm
aggregates at the same repetition. Report every unit, paired differences,
per-brief medians, cross-brief distributions, reviewer disagreement, stopped
runs, exclusions, and missing values. No unit is imputed. With this small
sample, describe results as directional and do not claim general superiority.
Do not tune the workflow on the held-out scoring set during the same cycle.

## Launch gate

T-059 may publish results only after:

- protocol and fixtures are versioned;
- at least two independent blind reviewers score every completed arm;
- failures and excluded runs are present;
- the report passes security/privacy review;
- a human approves publication.

Until then, the repository may link this protocol but must say that no result
has been established.
