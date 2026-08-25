"use client";

import {Button} from "@everything-agentic/ui";
import {useEffect, useRef, useState} from "react";

const directions = [
  {
    id: "editorial-signal",
    number: "01",
    name: "Editorial Signal",
    thesis: "Authored, precise, and built for case-study storytelling.",
    palette: ["#f4efe3", "#181411", "#c7220f"],
  },
  {
    id: "kinetic-index",
    number: "02",
    name: "Kinetic Index",
    thesis: "High-energy, interaction-led, and deliberately unconventional.",
    palette: ["#090a09", "#efffe3", "#adff29"],
  },
  {
    id: "quiet-material",
    number: "03",
    name: "Quiet Material",
    thesis: "Warm, tactile, and confident enough to reward close attention.",
    palette: ["#e5eddc", "#142228", "#155257"],
  },
] as const;

type DirectionId = (typeof directions)[number]["id"];

const projects = [
  {
    index: "01",
    title: "Lumen Care",
    discipline: "Service design · Health",
    result: "Cut missed follow-ups by 38%",
    year: "2026",
  },
  {
    index: "02",
    title: "Common Thread",
    discipline: "Product strategy · Community",
    result: "Made belonging measurable",
    year: "2025",
  },
  {
    index: "03",
    title: "Field Notes",
    discipline: "Creative tools · Spatial",
    result: "A research archive you can wander",
    year: "2025",
  },
] as const;

type Profile = {name: string; role: string; location: string};
type CopyStatus = "idle" | "copied" | "error";

export function PortfolioLab({
  profile,
  approvedDirection,
}: {
  profile: Profile;
  approvedDirection: string | null;
}) {
  const approved = directions.some((item) => item.id === approvedDirection)
    ? (approvedDirection as DirectionId)
    : null;
  const [active, setActive] = useState<DirectionId>(approved ?? "editorial-signal");
  const [copyStatus, setCopyStatus] = useState<CopyStatus>("idle");
  const [dockOpen, setDockOpen] = useState(false);
  const dockTrigger = useRef<HTMLButtonElement>(null);
  const firstDirection = useRef<HTMLButtonElement>(null);
  const direction = directions.find((item) => item.id === active) ?? directions[0];
  const approvalCommand = `./agentic design approve ${active} --yes`;

  useEffect(() => {
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape" && dockOpen) {
        setDockOpen(false);
        dockTrigger.current?.focus();
      }
    }
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [dockOpen]);

  async function copyApproval() {
    try {
      await navigator.clipboard.writeText(approvalCommand);
      setCopyStatus("copied");
      window.setTimeout(() => setCopyStatus("idle"), 1800);
    } catch {
      setCopyStatus("error");
    }
  }

  return (
    <main
      className="experience"
      data-direction={active}
      data-approved={active === approved ? "true" : "false"}
    >
      <a className="skip-link" href="#selected-work">Skip to selected work</a>

      <aside className="direction-dock" aria-label="Design direction comparison" data-open={dockOpen}>
        <button
          className="direction-trigger"
          type="button"
          ref={dockTrigger}
          aria-controls="direction-dock-panel"
          aria-expanded={dockOpen}
          onClick={() => {
            const next = !dockOpen;
            setDockOpen(next);
            if (next) window.setTimeout(() => firstDirection.current?.focus(), 0);
          }}
        >
          <span>Direction</span><strong>{direction.name}</strong><b aria-hidden="true">{dockOpen ? "×" : "+"}</b>
        </button>
        <div className="direction-dock-panel" id="direction-dock-panel">
          <div className="dock-intro">
            <span className="dock-kicker">Direction lab</span>
            <strong>Same content. Three systems.</strong>
          </div>
          <div className="direction-options" role="group" aria-label="Choose a direction to preview">
            {directions.map((item, index) => (
              <button
                className="direction-option"
                data-selected={active === item.id}
                key={item.id}
                ref={index === 0 ? firstDirection : undefined}
                type="button"
                aria-pressed={active === item.id}
                onClick={() => {
                  setActive(item.id);
                  setCopyStatus("idle");
                }}
              >
                <span>{item.number}</span>
                <strong>{item.name}</strong>
                <span className="palette" aria-label={`${item.name} palette`}>
                  {item.palette.map((color) => <i key={color} style={{background: color}} />)}
                </span>
              </button>
            ))}
          </div>
          <div className="approval">
            <code>{approvalCommand}</code>
            <Button type="button" size="compact" data-copy-status={copyStatus} onClick={copyApproval}>
              {copyStatus === "copied"
                ? "Command copied"
                : copyStatus === "error"
                  ? "Copy failed — try again"
                  : active === approved
                    ? "Approved direction"
                    : "Copy approval command"}
            </Button>
            <span className="copy-status" role="status" aria-live="polite">
              {copyStatus === "copied"
                ? "Approval command copied to the clipboard."
                : copyStatus === "error"
                  ? "The approval command could not be copied. Try again."
                  : ""}
            </span>
          </div>
        </div>
      </aside>

      <div className="portfolio-shell">
        <header className="site-header">
          <a className="wordmark" href="#top" aria-label={`${profile.name}, home`}>
            <span>{profile.name.split(" ")[0]}</span>
            <span>{profile.name.split(" ").slice(1).join(" ")}</span>
          </a>
          <p className="availability"><i /> Available for select collaborations</p>
          <nav aria-label="Primary navigation">
            <a href="#selected-work">Work</a>
            <a href="#about">About</a>
            <a href="#contact">Contact ↗</a>
          </nav>
        </header>

        <section className="hero" id="top" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">{profile.role} · {profile.location}</p>
            <h1 id="hero-title">
              Designing systems<br />
              <span>people can feel.</span>
            </h1>
            <p className="hero-deck">
              I turn knotty services into clear, expressive products—then stay
              close enough to the code to make every small interaction count.
            </p>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="artifact artifact-one" />
            <div className="artifact artifact-two" />
            <div className="artifact artifact-three" />
            <svg className="gesture" viewBox="0 0 420 420" fill="none">
              <path d="M44 304C99 89 259 49 372 142C292 124 217 170 198 286C174 244 110 243 44 304Z" />
              <circle cx="304" cy="95" r="34" />
            </svg>
            <span className="art-caption">Selected direction<br />{direction.number} / {direction.name}</span>
          </div>
        </section>

        <section className="work" id="selected-work" aria-labelledby="work-title">
          <div className="section-heading">
            <p className="eyebrow">Selected work · 2025—26</p>
            <h2 id="work-title">Proof, not decoration.</h2>
          </div>
          <div className="project-list">
            {projects.map((project) => (
              <a className="project-row" href="#about" key={project.title}>
                <span className="project-index">{project.index}</span>
                <span className="project-title">{project.title}</span>
                <span className="project-discipline">{project.discipline}</span>
                <span className="project-result">{project.result}</span>
                <span className="project-year">{project.year}</span>
                <span className="project-arrow" aria-hidden="true">↗</span>
              </a>
            ))}
          </div>
        </section>

        <section className="about" id="about" aria-labelledby="about-title">
          <p className="eyebrow">How I work</p>
          <h2 id="about-title">Clarity is crafted.<br />Delight is earned.</h2>
          <div className="about-grid">
            <p>
              Research gives the work a point of view. Systems keep it coherent.
              Prototypes expose what documents hide. The final five percent is
              where trust becomes tangible.
            </p>
            <ol>
              <li><span>01</span> Find the human tension</li>
              <li><span>02</span> Choose a sharp direction</li>
              <li><span>03</span> Build the real interaction</li>
              <li><span>04</span> Critique until it holds up</li>
            </ol>
          </div>
        </section>

        <footer id="contact">
          <p>Have an ambitious, complicated thing?</p>
          <strong className="portfolio-contact">Connect the real contact path before release.</strong>
          <small>{profile.name} · Reference fixture · Product-owner review required</small>
        </footer>
      </div>
    </main>
  );
}
