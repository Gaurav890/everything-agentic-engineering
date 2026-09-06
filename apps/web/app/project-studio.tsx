import {CopyAction} from "./copy-action";
import type {ProjectBrief, ProjectCandidate} from "./project-brief.server";
import styles from "./project-studio.module.css";

const handoff = "Use the project-onboarding and creative-direction-sprint skills. Read .agentic/project-brief.json and the project instructions. Resume from saved decisions, then build and register three materially different live product directions before implementation or token approval.";
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
          <p className={styles.lead}>The foundation is ready. Next, turn the first useful experience into live directions you can see, use, reject, and combine.</p>
          <a className={styles.primary} href="#continue">Create live directions <span aria-hidden="true">↓</span></a>
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
        <div><p className={styles.eyebrow}>Your next step</p><h2 id="continue-heading">One sprint.<br />Real choices.</h2>
          <p>Use the terminal inside this project. The sprint resumes your brief and requires working product previews—not a mood board or renamed demo.</p>
        </div>
        <div className={styles.instructions}>
          <div className={styles.command}><code>./agentic design sprint</code><CopyAction text="./agentic design sprint" label="Copy sprint command" destination="terminal" /></div>
          <p>Continue in {clients[brief.assistant]}. It asks only unresolved consequential questions, then creates three distinct live candidates by default. No API key is collected here, and no client or design pack is installed automatically.</p>
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
            <iframe src={candidate.preview_path} title={`${candidate.name} live design preview`} loading="lazy" sandbox="allow-forms allow-scripts" tabIndex={-1} />
          </div>
          <span className={styles.eyebrow}>{String(index + 1).padStart(2, "0")} / {candidate.axis}</span>
          <h3>{candidate.name}</h3><p>{candidate.thesis}</p>
          <dl><dt>Signature idea</dt><dd>{candidate.signature}</dd><dt>Composition</dt><dd>{candidate.composition}</dd><dt>Interaction</dt><dd>{candidate.interaction}</dd></dl>
          <details><summary>Craft and resilience</summary><dl><dt>Assets</dt><dd>{candidate.asset_strategy}</dd><dt>Motion</dt><dd>{candidate.motion_rationale}</dd><dt>Responsive</dt><dd>{candidate.responsive_strategy}</dd><dt>Reduced motion</dt><dd>{candidate.reduced_motion}</dd><dt>States</dt><dd>{candidate.states.join(" · ")}</dd></dl></details>
          <a href={candidate.preview_path}>Use the working preview <span aria-hidden="true">↗</span></a>
        </li>)}</ul> : <div className={styles.empty}><span aria-hidden="true">↳</span><div><h3>Your product directions are ready to be made.</h3><p>Run the sprint above. It will use your saved outcome to build three working answers on different design axes, then return here for comparison. The starter’s sample styles cannot qualify as your custom direction.</p></div></div>}
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
