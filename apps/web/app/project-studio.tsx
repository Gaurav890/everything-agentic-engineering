import {CopyAction} from "./copy-action";
import type {ProjectBrief, ProjectCandidate, ProjectDesignStatus} from "./project-brief.server";
import styles from "./project-studio.module.css";

const handoff = "Use the project-onboarding and creative-direction-sprint skills. Read .agentic/project-brief.json and the project instructions. Resume from saved decisions, then build and register three materially different live product directions before implementation or token approval.";
const clients = {choose: "your coding assistant", manual: "your app or editor", claude: "Claude Code", codex: "Codex"};

export function ProjectStudio({brief, candidates, designStatus}: {brief: ProjectBrief; candidates: ProjectCandidate[]; designStatus: ProjectDesignStatus}) {
  const shapeComplete = brief.status === "ready";
  const directionComplete = designStatus === "approved";
  const stages = [
    {label: "Shape", detail: "Product and first outcome", status: shapeComplete ? "complete" : "active"},
    {label: "Direction", detail: "Working visual choices", status: directionComplete ? "complete" : shapeComplete || candidates.length ? "active" : "waiting"},
    {label: "Build", detail: "One useful product slice", status: directionComplete ? "active" : "waiting"},
    {label: "Proof", detail: "Running evidence and review", status: "waiting"},
  ];
  const next = !shapeComplete
    ? {eyebrow: "Shape the product", title: "Agree the first useful journey.", body: "Resume the saved brief, settle only the decisions that change the experience, and keep unknowns explicit."}
    : candidates.length === 0
      ? {eyebrow: "Find the direction", title: "Create live choices made for this product.", body: "Build materially different working answers. A palette swap, mood board, or renamed starter does not qualify."}
      : !directionComplete
        ? {eyebrow: "Choose deliberately", title: "Use, reject, or combine the live directions.", body: "Review the actual states below across desktop, mobile, keyboard, and reduced motion before approval."}
        : {eyebrow: "Build the first slice", title: "Turn the approved system into one useful result.", body: "Implement the accepted journey, verify the running behavior, and keep the evaluator separate from the builder."};
  return <div className={styles.studio}>
    <a className="skip-link" href="#project-main">Skip to your project</a>
    <header className={styles.header}>
      <span className={styles.wordmark}>{brief.name}<span> / project workspace</span></span>
      <a href="#continue">Continue building <span aria-hidden="true">↗</span></a>
    </header>
    <main id="project-main" tabIndex={-1}>
      <ol className={styles.progress} aria-label="Project progress">
        {stages.map((stage, index) => <li key={stage.label} data-status={stage.status} aria-current={stage.status === "active" ? "step" : undefined}>
          <span>{String(index + 1).padStart(2, "0")}</span><div><strong>{stage.label}</strong><small>{stage.detail}</small></div>
        </li>)}
      </ol>
      <section className={styles.hero} aria-labelledby="project-heading">
        <div>
          <p className={styles.eyebrow}>{next.eyebrow}</p>
          <h1 id="project-heading">Make <em>{brief.name}</em><br />worth remembering.</h1>
          <p className={styles.lead}>{next.title} {next.body}</p>
          <a className={styles.primary} href="#continue">Continue from here <span aria-hidden="true">↓</span></a>
          <p className={styles.note}>This is your setup workspace—not your finished product or an approved visual identity.</p>
        </div>
        <aside className={styles.brief} aria-labelledby="brief-heading">
          <div className={styles.sheetTop}><span>01 / Working brief</span><span>{brief.status === "ready" ? "Scope confirmed" : "Saved · needs review"}</span></div>
          <h2 id="brief-heading">What we’re here to make.</h2>
          <dl>
            {brief.idea ? <><dt>The idea</dt><dd>{brief.idea}</dd></> : null}
            <dt>The promise</dt><dd>{brief.promise}</dd>
            <dt>For</dt><dd>{brief.audience}</dd>
            <dt>First useful outcome</dt><dd>{brief.first_outcome || "Choose one useful journey together before implementation."}</dd>
            <dt>Design intent</dt><dd>{brief.design_preferences || "Still open. Explore palette, typography, layout, and motion together."}</dd>
          </dl>
          <p>{brief.design_mode === "existing-brand" ? "Start from your existing brand. Bring its guidelines and real product references." : "Custom direction. No preset shortlist and no assumed palette."}</p>
        </aside>
      </section>

      <section className={styles.continue} id="continue" aria-labelledby="continue-heading">
        <div><p className={styles.eyebrow}>One doorway</p><h2 id="continue-heading">Start once.<br />Resume anywhere.</h2>
          <p>The same command reads the saved state and prepares the right continuation. Specialist commands remain available as advanced controls.</p>
        </div>
        <div className={styles.instructions}>
          <div className={styles.command}><code>./agentic start</code><CopyAction text="./agentic start" label="Copy start command" destination="terminal" /></div>
          <p>Continue in {clients[brief.assistant]}. It asks only unresolved consequential questions and routes the current stage. No API key is collected here, and no client or design pack is installed automatically.</p>
          <details open={brief.assistant === "manual"}><summary>Already using an app or editor?</summary>
            <p>Open this generated project’s folder there. Copy this instruction into a new conversation:</p>
            <pre>{handoff}</pre><CopyAction text={handoff} label="Copy instruction" destination="assistant" />
          </details>
          <p className={styles.note}>Keep this preview running in its terminal. Use another terminal for the handoff, or stop the preview with Ctrl+C first.</p>
        </div>
      </section>

      <section className={styles.directions} aria-labelledby="directions-heading">
        <div className={styles.sectionHeading}><div><p className={styles.eyebrow}>Next, see it take shape</p><h2 id="directions-heading">Directions made for {brief.name}.</h2></div>
          <p>Compare working layouts and interactions. Mix ideas, request another direction, or reject them all. You choose what becomes the design system.</p>
        </div>
        {candidates.length ? <ul className={styles.candidates}>{candidates.map((candidate, index) => <li key={candidate.id}>
          <div className={styles.previewFrame}>
            <iframe src={candidate.preview_path} title={`${candidate.name} live design preview`} loading="lazy" sandbox="allow-forms allow-scripts" />
          </div>
          <span className={styles.eyebrow}>{String(index + 1).padStart(2, "0")} / {candidate.axis}</span>
          <h3>{candidate.name}</h3><p>{candidate.thesis}</p>
          <dl><dt>Signature idea</dt><dd>{candidate.signature}</dd><dt>Composition</dt><dd>{candidate.composition}</dd><dt>Interaction</dt><dd>{candidate.interaction}</dd></dl>
          <details><summary>Craft and resilience</summary><dl><dt>Assets</dt><dd>{candidate.asset_strategy}</dd><dt>Motion</dt><dd>{candidate.motion_rationale}</dd><dt>Responsive</dt><dd>{candidate.responsive_strategy}</dd><dt>Reduced motion</dt><dd>{candidate.reduced_motion}</dd><dt>States</dt><dd>{candidate.states.join(" · ")}</dd></dl></details>
          <a href={candidate.preview_path}>Use the working preview <span aria-hidden="true">↗</span></a>
        </li>)}</ul> : <div className={styles.empty}><span aria-hidden="true">↳</span><div><h3>Your product directions are ready to be made.</h3><p>Use the start command above. It will resume your saved outcome and route the design sprint to build working answers on different axes, then return here for comparison. The starter’s sample styles cannot qualify as your custom direction.</p></div></div>}
      </section>
    </main>
    <footer className={styles.footer}><span>{brief.name} / built around your decisions</span><span>Return through <code>./agentic start</code> · Inspect details with <code>./agentic journey</code></span></footer>
  </div>;
}
