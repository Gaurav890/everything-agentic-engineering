import {CopyAction} from "./copy-action";
import type {ProjectBrief, ProjectCandidate} from "./project-brief.server";
import styles from "./project-studio.module.css";

const handoff = "Use the project-onboarding skill. Read .agentic/project-brief.json and the project instructions. Resume from the current brief, tasks, and evidence; do not repeat settled questions or assume a preset is the final design.";
const clients = {choose: "your coding assistant", manual: "your app or editor", claude: "Claude Code", codex: "Codex"};

export function ProjectStudio({brief, candidates}: {brief: ProjectBrief; candidates: ProjectCandidate[]}) {
  return <div className={styles.studio}>
    <a className="skip-link" href="#project-main">Skip to your project</a>
    <header className={styles.header}>
      <span className={styles.wordmark}>{brief.name}<span> / project workspace</span></span>
      <a href="#continue">Continue building <span aria-hidden="true">↗</span></a>
    </header>
    <main id="project-main" tabIndex={-1}>
      <section className={styles.hero} aria-labelledby="project-heading">
        <div>
          <p className={styles.eyebrow}>Your idea. Your direction.</p>
          <h1 id="project-heading">Let’s make<br /><em>{brief.name}</em><br />your own.</h1>
          <p className={styles.lead}>The foundation is ready. Next, shape the first useful experience with {clients[brief.assistant]}.</p>
          <a className={styles.primary} href="#continue">Continue from your brief <span aria-hidden="true">↓</span></a>
          <p className={styles.note}>This is your setup workspace—not your finished product or an approved visual identity.</p>
        </div>
        <aside className={styles.brief} aria-labelledby="brief-heading">
          <div className={styles.sheetTop}><span>01 / Working brief</span><span>{brief.status === "ready" ? "Scope confirmed" : "Saved · needs review"}</span></div>
          <h2 id="brief-heading">What we’re here to make.</h2>
          <dl>
            <dt>The promise</dt><dd>{brief.promise}</dd>
            <dt>For</dt><dd>{brief.audience}</dd>
            <dt>First useful outcome</dt><dd>{brief.first_outcome || "Choose one useful journey together before implementation."}</dd>
            <dt>Design intent</dt><dd>{brief.design_preferences || "Still open. Explore palette, typography, layout, and motion together."}</dd>
          </dl>
          <p>{brief.design_mode === "existing-brand" ? "Start from your existing brand. Bring its guidelines and real product references." : "Custom direction. No preset shortlist and no assumed palette."}</p>
        </aside>
      </section>

      <section className={styles.continue} id="continue" aria-labelledby="continue-heading">
        <div><p className={styles.eyebrow}>Your next step</p><h2 id="continue-heading">One conversation.<br />A clear way forward.</h2>
          <p>Use the terminal inside this project. The handoff shows what will happen and asks before starting an installed client.</p>
        </div>
        <div className={styles.instructions}>
          <div className={styles.command}><code>./agentic start</code><CopyAction text="./agentic start" label="Copy command" destination="terminal" /></div>
          <p>Continue in {clients[brief.assistant]}. Sign in through the client’s own flow if needed. No API key is collected here, and no client is installed automatically.</p>
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
          <span className={styles.eyebrow}>{String(index + 1).padStart(2, "0")} / Proposed preview</span>
          <h3>{candidate.name}</h3><p>{candidate.thesis}</p>
          <dl><dt>Composition</dt><dd>{candidate.composition}</dd><dt>Interaction</dt><dd>{candidate.interaction}</dd></dl>
          <a href={candidate.preview_path}>Open working preview <span aria-hidden="true">↗</span></a>
        </li>)}</ul> : <div className={styles.empty}><span aria-hidden="true">↳</span><div><h3>No product-specific previews yet.</h3><p>Your assistant will use the brief to explore real screens and interactions. This page does not pretend that those designs already exist.</p></div></div>}
      </section>
      <ol className={styles.journey} aria-label="The path to your first feature">
        <li><span>01</span><h3>Shape</h3><p>Confirm the user, content, and one useful outcome.</p></li>
        <li><span>02</span><h3>See & choose</h3><p>Try real previews. Approve the direction and its tokens.</p></li>
        <li><span>03</span><h3>Build & review</h3><p>Implement the agreed slice, test it, and review evidence.</p></li>
      </ol>
    </main>
    <footer className={styles.footer}><span>{brief.name} / built around your decisions</span><span>Need your next step later? <code>./agentic next</code></span></footer>
  </div>;
}
