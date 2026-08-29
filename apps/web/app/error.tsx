"use client";

import styles from "./project-studio.module.css";

export default function ProjectError() {
  return <div className={styles.studio}>
    <main className={styles.hero}>
      <div>
        <p className={styles.eyebrow}>Your project is still here</p>
        <h1>Let’s get<br />back on track.</h1>
        <p className={styles.lead}>The workspace could not load. No files were reset or replaced.</p>
        <p>Ask your assistant to check the terminal error and your project brief and design catalog in <code>.agentic/</code>. Preserve your answers; don’t create a new project over this folder.</p>
        <button type="button" onClick={() => window.location.reload()}>Reload after fixing</button>
      </div>
    </main>
  </div>;
}
