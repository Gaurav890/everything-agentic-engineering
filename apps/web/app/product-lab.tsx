"use client";

import {Button} from "@everything-agentic/ui";
import {useEffect, useRef, useState} from "react";

import type {ExperienceManifest} from "./experience-types";

const directions = [
  {
    id: "editorial-signal",
    number: "01",
    name: "Editorial Signal",
    palette: ["#f4efe3", "#181411", "#c7220f"],
  },
  {
    id: "kinetic-index",
    number: "02",
    name: "Kinetic Index",
    palette: ["#090a09", "#efffe3", "#adff29"],
  },
  {
    id: "quiet-material",
    number: "03",
    name: "Quiet Material",
    palette: ["#e5eddc", "#142228", "#155257"],
  },
] as const;

type DirectionId = (typeof directions)[number]["id"];
type CopyStatus = "idle" | "copied" | "error";
type AgentDecision = "pending" | "approved" | "rejected" | "cancelled";
type EvidenceState = "partial" | "loading" | "ready";

const characterDirection = {
  precise: "editorial-signal",
  bold: "kinetic-index",
  warm: "quiet-material",
  experimental: "kinetic-index",
} as const satisfies Record<ExperienceManifest["visual_character"], DirectionId>;

function AgentStage() {
  const [reviewOpen, setReviewOpen] = useState(false);
  const [decision, setDecision] = useState<AgentDecision>("pending");
  const [evidenceState, setEvidenceState] = useState<EvidenceState>("partial");

  function runFinalCheck() {
    setEvidenceState("loading");
    window.setTimeout(() => setEvidenceState("ready"), 450);
  }

  function decide(next: AgentDecision) {
    setDecision(next);
    setReviewOpen(false);
  }

  const decisionLabel = {
    pending: "Candidate blocked until review",
    approved: "Candidate approved for the next controlled step",
    rejected: "Candidate rejected and returned for revision",
    cancelled: "Run cancelled; no downstream action taken",
  }[decision];

  return (
    <div className="agent-stage" id="agent-review" aria-label="Agent workflow demonstration">
      <div className="stage-topline">
        <span>Demonstration · launch decision</span>
        <span className="stage-live"><i /> Human gate active</span>
      </div>
      <div className="agent-objective">
        <span>Objective</span>
        <strong>Prepare the launch decision with verified evidence.</strong>
      </div>
      <ol className="agent-steps">
        <li data-state="done"><i>01</i><span>Research signal</span><strong>12 sources reconciled</strong></li>
        <li data-state="done"><i>02</i><span>Build candidate</span><strong>Contract checks passed</strong></li>
        <li data-state={decision === "pending" ? "waiting" : "done"}>
          <i>03</i><span>Decision gate</span><strong>{decisionLabel}</strong>
        </li>
      </ol>

      {reviewOpen ? (
        <section className="evidence-review" aria-labelledby="evidence-title">
          <div className="evidence-heading">
            <div>
              <span>Review gate</span>
              <h3 id="evidence-title">Evidence before consequence</h3>
            </div>
            <button type="button" className="text-control" onClick={() => setReviewOpen(false)}>
              Close
            </button>
          </div>
          <ul className="evidence-list">
            <li data-state="verified"><span>Source reconciliation</span><strong>12 / 12 traceable</strong></li>
            <li data-state="verified"><span>Contract checks</span><strong>7 / 7 passed</strong></li>
            <li data-state={evidenceState}>
              <span>Visual comparison</span>
              <strong>
                {evidenceState === "ready"
                  ? "Reviewed"
                  : evidenceState === "loading"
                    ? "Checking…"
                    : "Needs review"}
              </strong>
            </li>
          </ul>
          {evidenceState !== "ready" ? (
            <button
              type="button"
              className="verify-control"
              disabled={evidenceState === "loading"}
              onClick={runFinalCheck}
            >
              {evidenceState === "loading" ? "Verifying final evidence…" : "Verify final evidence"}
            </button>
          ) : null}
          <p className="consequence">
            <strong>Consequence:</strong> approval advances only this candidate. Rejection returns it for
            revision. Cancellation stops the run. Failed or unavailable checks keep approval locked and
            expose retry.
          </p>
          <div className="decision-controls">
            <button type="button" onClick={() => decide("rejected")}>Reject &amp; revise</button>
            <button type="button" onClick={() => decide("cancelled")}>Cancel run</button>
            <button
              type="button"
              className="decision-primary"
              disabled={evidenceState !== "ready"}
              onClick={() => decide("approved")}
            >
              Approve next step
            </button>
          </div>
        </section>
      ) : (
        <div className="agent-control">
          <span role="status" aria-live="polite">{decisionLabel}. Nothing ships silently.</span>
          <button type="button" aria-expanded="false" onClick={() => setReviewOpen(true)}>
            {decision === "pending" ? "Review evidence" : "Review again"} <b aria-hidden="true">↗</b>
          </button>
        </div>
      )}
    </div>
  );
}

function ProductStage({agentic}: {agentic: boolean}) {
  if (agentic) {
    return <AgentStage />;
  }

  return (
    <div className="product-stage" aria-label="Product outcome preview">
      <div className="stage-topline">
        <span>Workspace · This week</span>
        <span className="stage-live"><i /> In sync</span>
      </div>
      <div className="signal-orbit" aria-hidden="true">
        <span className="orbit orbit-one" />
        <span className="orbit orbit-two" />
        <span className="orbit-core">01</span>
      </div>
      <div className="outcome-line">
        <span>Signal</span>
        <strong>One clear priority replaced nine competing requests.</strong>
      </div>
      <div className="outcome-line">
        <span>Decision</span>
        <strong>Owner, evidence, and next move are visible.</strong>
      </div>
    </div>
  );
}

export function ProductLab({
  experience,
  approvedDirection,
}: {
  experience: ExperienceManifest;
  approvedDirection: string | null;
}) {
  const approved = directions.some((item) => item.id === approvedDirection)
    ? (approvedDirection as DirectionId)
    : null;
  const [active, setActive] = useState<DirectionId>(
    approved ?? characterDirection[experience.visual_character],
  );
  const [copyStatus, setCopyStatus] = useState<CopyStatus>("idle");
  const [dockOpen, setDockOpen] = useState(false);
  const dockTrigger = useRef<HTMLButtonElement>(null);
  const firstDirection = useRef<HTMLButtonElement>(null);
  const agentic = experience.archetype === "agentic-product";
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
      className="experience product-experience"
      data-archetype={experience.archetype}
      data-character={experience.visual_character}
      data-direction={active}
      data-approved={active === approved ? "true" : "false"}
    >
      <a className="skip-link" href="#product-proof">Skip to product proof</a>

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
          <span>Direction</span><strong>{directions.find((item) => item.id === active)?.name}</strong>
          <b aria-hidden="true">{dockOpen ? "×" : "+"}</b>
        </button>
        <div className="direction-dock-panel" id="direction-dock-panel">
          <div className="dock-intro">
            <span className="dock-kicker">Direction lab</span>
            <strong>Same promise. Three systems.</strong>
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
                  if (window.matchMedia("(max-width: 720px)").matches) {
                    setDockOpen(false);
                    window.setTimeout(() => dockTrigger.current?.focus(), 0);
                  }
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

      <div className="product-shell">
        <header className="product-header">
          <a className="product-wordmark" href="#top" aria-label={`${experience.name}, home`}>
            <i aria-hidden="true" />
            {experience.name}
          </a>
          <p>{agentic ? "Controlled autonomy" : "One clear system"}</p>
          <nav aria-label="Primary navigation">
            <a href="#product-proof">Why it works</a>
            <a href="#product-method">Method</a>
            <a className="header-action" href={agentic ? "#agent-review" : "#product-start"}>{agentic ? "See the gate" : "Start focused"} ↗</a>
          </nav>
        </header>

        <section className="product-hero" id="top" aria-labelledby="product-title">
          <div className="product-hero-copy">
            <p className="eyebrow">For {experience.audience}</p>
            <h1 id="product-title">{experience.promise}</h1>
            <p className="product-deck">
              {agentic
                ? "Delegate consequential work without losing visibility, control, or the evidence behind every decision."
                : "Replace scattered updates and soft consensus with a shared view of what matters, why it matters, and what happens next."}
            </p>
            <div className="hero-actions">
              <a href={agentic ? "#agent-review" : "#product-proof"}>{agentic ? "Inspect the control gate" : "See the system"} <span aria-hidden="true">↘</span></a>
              <small>Designed to earn trust before asking for commitment.</small>
            </div>
          </div>
          <ProductStage agentic={agentic} />
        </section>

        <section className="proof-band" id="product-proof" aria-label="Product principles">
          <p><span>01</span><strong>One shared truth</strong><small>Decisions stay attached to their evidence.</small></p>
          <p><span>02</span><strong>Visible progress</strong><small>State is legible before status meetings.</small></p>
          <p><span>03</span><strong>Human control</strong><small>Important actions remain reviewable and reversible.</small></p>
        </section>

        <section className="product-method" id="product-method" aria-labelledby="method-title">
          <div className="method-intro">
            <p className="eyebrow">The operating rhythm</p>
            <h2 id="method-title">Less ceremony.<br /><span>More certainty.</span></h2>
          </div>
          <ol className="method-list">
            <li><span>01</span><div><strong>See the real constraint.</strong><p>Turn noise into a precise decision before work multiplies.</p></div></li>
            <li><span>02</span><div><strong>Move with evidence.</strong><p>Keep outcomes, owners, and proof in the same visible system.</p></div></li>
            <li><span>03</span><div><strong>Finish with confidence.</strong><p>Test the whole experience, not just the happy path or the source code.</p></div></li>
          </ol>
        </section>

        <section className="product-close" id="product-start">
          <p className="eyebrow">{experience.name} · {experience.visual_character} starting character</p>
          <h2>{agentic ? "Autonomy people can trust." : "Clarity people can feel."}</h2>
          <div className="activation-contract">
            <strong>Connect the real activation path.</strong>
            <span>This starter will not invent a fake signup, email address, or conversion action.</span>
          </div>
          <small>Product-owner review is required before release.</small>
        </section>
      </div>
    </main>
  );
}
