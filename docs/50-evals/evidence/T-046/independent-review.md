# Independent review — T-046

Separate read-only product and security evaluators inspected the task diff and
disposable project. Neither edited files, granted human approval, or merged.

## Security

Scoped pass after re-review. Two blockers were fixed and probed: generated-output
leaf symlinks now fail before writes; custom catalog loading cannot bypass local
preview/source requirements. Output symlinks, project-local client executables,
unsafe preview links and unconfirmed ready briefs also fail closed. Only public
product fields reach the browser. An enum-coercion nit was subsequently fixed
and covered by a public-loader regression test.

## Product and usability

No unresolved blocker in the inspected scope. Generated README, vision, PRD,
acceptance, copy, architecture and first-feature drafts preserve actual intent
and distinguish it from implementation. Desktop/mobile screenshots show a
prominent continuation and explicit unfinished-workspace disclosure.

Findings fixed: primary-action focus contrast, ambiguous copy destination,
unconfirmed scope badge, metadata errors bypassing recovery, collapsed manual
instructions and inherited first-feature wording.

The product evaluator reviewed source and top-of-page screenshots. Lower
handoff, nonempty candidate and error recovery required subsequent live checks
by the implementation owner. Performance, screen-reader behavior, native sign-in
and newcomer outcomes were not independently measured. This review is not
human task approval or a claim of production readiness.

A final security recheck found no blocker in the added CI fixture: permissions
remain read-only, generation uses a new temporary path, native handoff is
JSON-only/manual, dependency restoration is offline and ignores lifecycle
scripts, and destructive-state simulation is gated and restored in `finally`.

A subsequent product follow-up inspected the lower handoff, focus, empty-catalog,
custom-preview and desktop/mobile recovery screenshots, the test definitions,
and both wording fixes. It found no visual or wording blocker and accepted the
stated evidence limits; it did not rerun the suites. A separate privacy follow-up
checked the inventory and disclosures against the implementation with no local
contract blocker. Its requested inventory/deletion precision is included below.

The final approval-source guard also received a separate recheck. It rejects
the generated approval stylesheet, including filesystem case and hardlink
aliases, while retaining ordinary preview/canonical-token inputs and all
source/evidence hashes. The alias finding was fixed and independently closed.

## Supporting contract evidence

The following inventory records implementation-owner evidence for the required
privacy, accessibility and finish-gate contracts; it does not expand the
independent review scope above.

### Privacy and consent

- Data: product name, audience, promise, first outcome, design preferences,
  design mode/status, assistant choice, open questions and a confirmation label.
  The handoff also resolves folder/executable paths for terminal-only display
  and execution; these paths are not added to the browser fields. Free text can
  contain personal information if supplied; it is not automatically redacted.
- Purpose/storage: resume the product conversation from local JSON and generated
  Markdown. The browser receives only the declared public product fields and
  safe candidate display fields; the allowlist excludes confirmation labels and
  executable paths, with explicit private-field regressions. No telemetry, account store or remote service
  is introduced. The workspace is not authenticated and must not be published
  with confidential content.
- Retention/deletion: local files remain user-owned with no automatic expiry.
  Manual edits/removal affect current copies only, not duplicated content in
  generated documents, Git history, backups or native-client sessions.
  Deletion/retention automation and real-data erasure
  were NOT RUN and are not claimed. The fixture suite uses synthetic content;
  the real downstream project was not modified.
- Consent: terminal launch requires explicit confirmation and terminal I/O.
  JSON/manual inspection never launches. A fixed prompt and explicit working
  directory are tested; no credential reading, shell interpolation or added
  permission flags. Native-client processing begins only after that handoff;
  its policies remain separate. Source/evidence fingerprints detect drift,
  but are not identity verification or a tamper-proof consent audit.
- Remediation: no supported blocker in this local-data contract. Review real
  data, authentication, retention and native-client policy before hosting or
  introducing production integrations.

### Accessibility and finish gate

- Automated scope: sixteen generated desktop/mobile Chromium cases, including
  axe on the workspace, reduced-motion emulation, horizontal overflow, skip
  navigation, CTA focus, clipboard states and recovery. Twenty-four source
  screenshot comparisons remain unchanged. These are not native-device tests.
- Manual scope: implementation-owner browser inspection of the brief, handoff,
  preview and recovery; independent screenshot/source inspection as stated
  above. Screen-reader, comprehensive zoom/high-contrast and real newcomer
  testing were NOT RUN.
- [WCAG 2.1.1 Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html):
  scripted Tab/Enter reaches the skip link, main and continuation link.
- [WCAG 2.4.7 Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html):
  corrected CTA outline and `keyboard-focus.png` show the focused action.
- [WCAG 4.1.3 Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html):
  clipboard pending/success/failure uses a polite status region. Actual spoken
  announcements still need assistive-technology testing. No conformance claim.
- Finish result: the workspace explains its incomplete status, reflects saved
  product intent, shows manual continuation without hiding it, and accepts a
  functioning non-preset preview. The example is synthetic, not an approved
  design or a finished financial product. No aesthetic approval is inferred.
- Remaining priorities: manual assistive-technology and native-client checks,
  then a real newcomer pilot before broader accessibility/self-service claims.
