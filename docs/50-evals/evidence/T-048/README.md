# T-048 — Self-serve handoff evidence

Status: implementation and deterministic checks pass. Independent product
review, human task approval, and real newcomer measurement remain separate.

## Observed gap

A fresh project generated and verified correctly, but the terminal ended with a
destination path and a second command. A newcomer still had to reconstruct the
directory change, infer what `start` would do, and decide whether credentials or
installation were expected.

## Verified locally

- Human output now presents one shell-safe continuation command. A destination
  containing spaces generated `cd '<absolute path>' && ./agentic start` and the
  printed command ran successfully.
- The creation receipt previews the remaining journey: saved brief, first useful
  journey, product-specific design previews, approved implementation, and
  running-product verification.
- The receipt states that nothing else was installed or launched, no API key is
  collected, native sign-in stays in the selected client, and native launch
  still asks for confirmation.
- Mutating JSON output carries equivalent structured continuation metadata,
  including explicit `automatic_launch: false` and `collects_api_keys: false`.
- All 26 project-generator tests pass, including paths with spaces and generated
  README assertions.
- Ten-stage full repository verification passes after restoring the unchanged
  locked local dependencies.
- A fresh web project passed generated-project verification, the exact printed
  manual continuation, and its downstream `./agentic verify full` check.

## Not claimed

No client, account, dependency, external capability, product feature, design,
service, deployment, approval, or merge is installed, created, or authorized by
this change. Automated checks do not establish measured newcomer success; the
P1–P5 pilot remains the authority for that claim.
