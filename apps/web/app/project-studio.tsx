import {CopyAction} from "./copy-action";
import type {ProjectBrief, ProjectCandidate, ProjectStudioContext} from "./project-brief.server";
import styles from "./project-studio.module.css";

const clients = {choose: "your coding assistant", manual: "your app or editor", claude: "Claude Code", codex: "Codex"};
const details = {
  product: "Product evidence and first outcome",
  direction: "Working visual choices",
  build: "One useful product slice",
  proof: "Running evidence and review",
};
const stageCopy = {
  product: {eyebrow: "Shape the product", body: "Settle only the decisions that change the experience and keep unknowns explicit."},
  direction: {eyebrow: "Find the direction", body: "Build materially different working answers; a palette swap, mood board, or renamed starter does not qualify."},
  build: {eyebrow: "Build the first slice", body: "Turn the accepted journey and design system into one useful result."},
  proof: {eyebrow: "Prove the experience", body: "Verify running behavior and keep the evaluator separate from the builder."},
};

const directionCopy = {
  product: {
    eyebrow: "First, make the brief credible",
    title: "Design follows product evidence.",
    body: "Finish the current product step first. The Studio will then route you into working directions made for this product—not generic starter themes.",
  },
  direction: {
    eyebrow: "Next, see it take shape",
    title: "Compare working product directions.",
    body: "Compare real layouts and interactions. Mix ideas, request another direction, or reject them all. You choose what becomes the design system.",
  },
  build: {
    eyebrow: "Direction accepted",
    title: "Build from approved decisions.",
    body: "The chosen direction now constrains the design system and first useful product slice. Sample styles cannot replace those decisions.",
  },
  proof: {
    eyebrow: "The product is running",
    title: "Prove the experience before shipping.",
    body: "Inspect the real product across states, viewports, keyboard use, accessibility, and reduced motion. Independent evidence decides whether it is ready.",
  },
};

export function ProjectStudio({brief, candidates, context}: {brief: ProjectBrief; candidates: ProjectCandidate[]; context: ProjectStudioContext}) {
  const activeStage = context.studio.stages.find(stage => stage.status === "active") ?? context.studio.stages.at(-1)!;
  const next = {...stageCopy[activeStage.id], title: context.studio.next.title};
  const directions = directionCopy[activeStage.id];
  return <div className={styles.studio}>
    <a className="skip-link" href="#project-main">Skip to your project</a>
    <header className={styles.header}>
      <span className={styles.wordmark}>{brief.name}<span> / project workspace</span></span>
      <a href="#continue">Continue building <span aria-hidden="true">↗</span></a>
    </header>
    <main id="project-main" tabIndex={-1}>
      <ol className={styles.progress} aria-label="Project progress">
        {context.studio.stages.map((stage, index) => <li key={stage.label} data-status={stage.status} aria-current={stage.status === "active" ? "step" : undefined}>
          <span>{String(index + 1).padStart(2, "0")}</span><div><strong>{stage.label}</strong><small>{details[stage.id]}</small></div>
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
          <p>Continue in {clients[context.client]}. It asks only unresolved consequential questions and routes the current stage. No API key is collected here, and no client or design pack is installed automatically.</p>
          <details open={context.client === "manual"}><summary>Already using an app or editor?</summary>
            <p>Open this generated project’s folder there. Copy this instruction into a new conversation:</p>
            <pre>{context.prompt}</pre><CopyAction text={context.prompt} label="Copy instruction" destination="assistant" />
          </details>
          <p className={styles.note}>Keep this preview running in its terminal. Use another terminal for the handoff, or stop the preview with Ctrl+C first.</p>
        </div>
      </section>

      <section className={styles.directions} aria-labelledby="directions-heading">
        <div className={styles.sectionHeading}><div><p className={styles.eyebrow}>{directions.eyebrow}</p><h2 id="directions-heading">{directions.title}</h2></div>
          <p>{directions.body}</p>
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
        </li>)}</ul> : <div className={styles.empty}><span aria-hidden="true">↳</span><div><h3>{context.studio.next.title}</h3><p>Use the start command above. It will follow the current saved stage, then return here when there are working directions to compare. The starter’s sample styles cannot qualify as your custom direction.</p></div></div>}
      </section>
    </main>
    <footer className={styles.footer}><span>{brief.name} / built around your decisions</span><span>Return through <code>./agentic start</code> · Inspect details with <code>./agentic journey</code></span></footer>
  </div>;
}
