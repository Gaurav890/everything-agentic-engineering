"use client";

import {
  Activity,
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleAlert,
  Clock3,
  FileText,
  Filter,
  Gauge,
  Layers3,
  MoreHorizontal,
  Pause,
  Play,
  RotateCcw,
  Search,
  ShieldCheck,
  Sparkles,
  Square,
  Users,
  X,
} from "lucide-react";
import { useMemo, useState } from "react";
import { activity, runs, type Run, type RunStatus } from "@/lib/data";

type Scenario = "normal" | "loading" | "empty" | "error";
type FilterName = "all" | RunStatus;

const statusLabel: Record<RunStatus, string> = {
  active: "In motion",
  approval: "Needs approval",
  complete: "Complete",
  failed: "Needs recovery",
};

function LogoMark() {
  return (
    <div className="logoMark" aria-hidden="true">
      <span />
      <span />
      <span />
    </div>
  );
}

function StatusGlyph({ status }: { status: RunStatus }) {
  if (status === "approval") return <CircleAlert size={15} />;
  if (status === "complete") return <CheckCircle2 size={15} />;
  if (status === "failed") return <RotateCcw size={15} />;
  return <Activity size={15} />;
}

function Skeleton() {
  return (
    <main className="statePage" aria-live="polite" aria-busy="true">
      <div className="stateWord">SIGNALROOM</div>
      <div className="skeletonGrid">
        <div className="skeletonRail" />
        <div className="skeletonMain">
          <div className="skeletonLine short" />
          <div className="skeletonLine hero" />
          <div className="skeletonLine medium" />
          <div className="skeletonRows">
            <i />
            <i />
            <i />
          </div>
        </div>
        <div className="skeletonAside" />
      </div>
      <p>Reconstructing workspace state…</p>
    </main>
  );
}

function EmptyState({ onReset }: { onReset: () => void }) {
  return (
    <main className="statePage emptyState">
      <div className="stateWord">00 / QUIET</div>
      <div className="emptyOrb" aria-hidden="true">
        <span />
      </div>
      <p className="kicker">No runs match this view</p>
      <h1>The room is quiet.</h1>
      <p className="stateCopy">
        Nothing needs your attention. Start a run or return to the live workspace.
      </p>
      <button className="primaryButton" onClick={onReset}>
        Return to live workspace <ArrowUpRight size={16} />
      </button>
    </main>
  );
}

function ErrorState({ onReset }: { onReset: () => void }) {
  return (
    <main className="statePage errorState">
      <div className="stateWord">PARTIAL / 01</div>
      <div className="errorRule" />
      <p className="kicker">Workspace partially restored</p>
      <h1>One evidence stream went dark.</h1>
      <p className="stateCopy">
        The billing warehouse stopped responding after 2,104 of 2,418 rows. Completed
        work is preserved and no claims were published.
      </p>
      <div className="recoveryFacts">
        <span>
          <ShieldCheck size={17} /> No data written
        </span>
        <span>
          <CheckCircle2 size={17} /> 3 sources preserved
        </span>
        <span>
          <Clock3 size={17} /> Last checkpoint 10:42
        </span>
      </div>
      <div className="stateActions">
        <button className="primaryButton" onClick={onReset}>
          Retry from checkpoint <RotateCcw size={16} />
        </button>
        <button className="quietButton" onClick={onReset}>
          Open preserved workspace
        </button>
      </div>
    </main>
  );
}

function RunItem({
  run,
  active,
  onSelect,
}: {
  run: Run;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <button className={`runItem ${active ? "selected" : ""}`} onClick={onSelect}>
      <span className={`statusDot ${run.status}`} aria-hidden="true" />
      <span className="runItemCopy">
        <span className="runEyebrow">{run.eyebrow}</span>
        <strong>{run.title}</strong>
        <span className="runMeta">
          {run.id} <i /> {run.updated} ago
        </span>
      </span>
      <span className="runProgress" aria-label={`${run.progress}% complete`}>
        {run.progress}
      </span>
    </button>
  );
}

function ApprovalPanel({
  decided,
  onDecision,
}: {
  decided: "approved" | "denied" | null;
  onDecision: (decision: "approved" | "denied") => void;
}) {
  if (decided) {
    return (
      <section className={`decisionReceipt ${decided}`} aria-live="polite">
        {decided === "approved" ? <Check size={22} /> : <X size={22} />}
        <div>
          <p className="micro">Decision recorded</p>
          <h2>{decided === "approved" ? "Read-only access approved" : "Request denied"}</h2>
          <p>
            {decided === "approved"
              ? "Research can continue. Account identifiers remain masked in downstream artifacts."
              : "The run is paused at the evidence boundary and awaits redirection."}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="approvalPanel" aria-labelledby="approval-heading">
      <div className="approvalHeader">
        <span className="attentionIndex">01</span>
        <div>
          <p className="micro">Your attention</p>
          <h2 id="approval-heading">Approve a protected data read</h2>
        </div>
      </div>
      <p className="approvalLead">
        Research needs the enterprise billing cohort to test whether contract timing
        predicts early churn.
      </p>
      <dl className="approvalFacts">
        <div>
          <dt>Scope</dt>
          <dd>2,418 accounts · read only</dd>
        </div>
        <div>
          <dt>Protected field</dt>
          <dd>Account identifier</dd>
        </div>
        <div>
          <dt>Retention</dt>
          <dd>Removed after synthesis</dd>
        </div>
        <div>
          <dt>Reversible</dt>
          <dd>Yes · no external write</dd>
        </div>
      </dl>
      <div className="sourceProof">
        <ShieldCheck size={18} />
        <span>
          <strong>Policy gate passed</strong>
          Query is parameterized and sensitive columns are masked.
        </span>
      </div>
      <div className="approvalActions">
        <button className="approveButton" onClick={() => onDecision("approved")}>
          Approve read <ArrowUpRight size={16} />
        </button>
        <button className="denyButton" onClick={() => onDecision("denied")}>
          Deny
        </button>
      </div>
      <p className="shortcutHint">
        <kbd>A</kbd> approve <kbd>D</kbd> deny
      </p>
    </section>
  );
}

export default function Home() {
  const [selectedId, setSelectedId] = useState(runs[0].id);
  const [filter, setFilter] = useState<FilterName>("all");
  const [query, setQuery] = useState("");
  const [paused, setPaused] = useState(false);
  const [decision, setDecision] = useState<"approved" | "denied" | null>(null);
  const [scenario, setScenario] = useState<Scenario>("normal");

  const visibleRuns = useMemo(
    () =>
      runs.filter(
        (run) =>
          (filter === "all" || run.status === filter) &&
          `${run.title} ${run.eyebrow} ${run.id}`
            .toLowerCase()
            .includes(query.toLowerCase()),
      ),
    [filter, query],
  );
  const selected = runs.find((run) => run.id === selectedId) ?? runs[0];

  if (scenario === "loading") return <Skeleton />;
  if (scenario === "empty") return <EmptyState onReset={() => setScenario("normal")} />;
  if (scenario === "error") return <ErrorState onReset={() => setScenario("normal")} />;

  return (
    <main className="appShell">
      <a className="skipLink" href="#run-detail">
        Skip to selected run
      </a>

      <header className="topbar">
        <div className="brand">
          <LogoMark />
          <span>Signalroom</span>
          <i />
          <small>Agent operations</small>
        </div>
        <div className="topActions">
          <label className="searchBox">
            <Search size={15} />
            <span className="srOnly">Search runs</span>
            <input
              placeholder="Search runs"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <kbd>⌘ K</kbd>
          </label>
          <div className="scenarioControl" aria-label="Preview state">
            {(["normal", "loading", "empty", "error"] as Scenario[]).map((item) => (
              <button
                key={item}
                className={scenario === item ? "active" : ""}
                onClick={() => setScenario(item)}
              >
                {item}
              </button>
            ))}
          </div>
          <button className="iconButton" aria-label="More workspace options">
            <MoreHorizontal size={18} />
          </button>
          <div className="avatar" aria-label="Signed in as Gaurav">
            GK
          </div>
        </div>
      </header>

      <aside className="commandRail" aria-label="Workspace navigation">
        <nav>
          <button className="railButton active" aria-label="Runs">
            <Activity size={19} />
          </button>
          <button className="railButton" aria-label="Artifacts">
            <Layers3 size={19} />
          </button>
          <button className="railButton" aria-label="Team">
            <Users size={19} />
          </button>
          <button className="railButton" aria-label="Performance">
            <Gauge size={19} />
          </button>
        </nav>
        <div className="railBottom">
          <span className="liveMark">
            <i /> Live
          </span>
          <button className="railButton" aria-label="Workspace settings">
            <Sparkles size={19} />
          </button>
        </div>
      </aside>

      <aside className="runRail" aria-label="Agent runs">
        <div className="runRailHeader">
          <div>
            <p className="micro">Workspace</p>
            <h1>Northstar</h1>
          </div>
          <button className="iconButton light" aria-label="Filter options">
            <Filter size={16} />
          </button>
        </div>
        <div className="filterTabs" role="group" aria-label="Filter runs">
          {(["all", "approval", "active", "complete", "failed"] as FilterName[]).map(
            (item) => (
              <button
                key={item}
                onClick={() => setFilter(item)}
                className={filter === item ? "active" : ""}
              >
                {item === "all" ? "All" : item === "approval" ? "Attention" : item}
              </button>
            ),
          )}
        </div>
        <div className="runList">
          {visibleRuns.length ? (
            visibleRuns.map((run) => (
              <RunItem
                key={run.id}
                run={run}
                active={selected.id === run.id}
                onSelect={() => {
                  setSelectedId(run.id);
                  setDecision(null);
                }}
              />
            ))
          ) : (
            <div className="inlineEmpty">
              <span>00</span>
              <p>No runs in this state.</p>
              <button
                onClick={() => {
                  setFilter("all");
                  setQuery("");
                }}
              >
                Clear filter
              </button>
            </div>
          )}
        </div>
        <button className="newRunButton">
          <span>+</span> New run
          <kbd>N</kbd>
        </button>
      </aside>

      <section className="workspace" id="run-detail">
        <header className="runHeader">
          <div>
            <div className="runIdentity">
              <span className={`statusChip ${selected.status}`}>
                <StatusGlyph status={selected.status} />
                {statusLabel[selected.status]}
              </span>
              <span className="runId">{selected.id}</span>
              <span className="updated">Updated {selected.updated} ago</span>
            </div>
            <h2>{selected.title}</h2>
            <p>{selected.brief}</p>
          </div>
          <div className="runControls">
            <button
              className={`pauseButton ${paused ? "paused" : ""}`}
              onClick={() => setPaused((value) => !value)}
              aria-pressed={paused}
            >
              {paused ? <Play size={15} /> : <Pause size={15} />}
              {paused ? "Resume run" : "Pause run"}
            </button>
            <button className="iconButton light" aria-label="Stop run">
              <Square size={14} />
            </button>
          </div>
        </header>

        {paused && (
          <div className="pauseNotice" role="status">
            <Pause size={15} />
            Run paused at a safe checkpoint. Completed evidence remains available.
          </div>
        )}

        <section className="runRibbon" aria-label="Run progress">
          <div className="ribbonIntro">
            <p className="micro">Execution plan</p>
            <span>{selected.progress}%</span>
          </div>
          <div className="ribbonSteps">
            {selected.steps.map((step, index) => (
              <div className={`ribbonStep ${step.state}`} key={step.label}>
                <div className="stepTop">
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <i />
                  <small>{step.owner}</small>
                </div>
                <h3>{step.label}</h3>
                <p>{step.detail}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="activitySection">
          <div className="sectionHeading">
            <div>
              <p className="micro">Live evidence</p>
              <h2>What changed</h2>
            </div>
            <button className="textButton">
              View full trace <ArrowUpRight size={14} />
            </button>
          </div>
          <div className="activityTable">
            {activity.map((item) => (
              <article className={`activityRow ${item.tone}`} key={item.time}>
                <time>{item.time}</time>
                <span className="activityOwner">{item.owner}</span>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.detail}</p>
                </div>
                <button aria-label={`Open ${item.title}`}>
                  <ArrowUpRight size={15} />
                </button>
              </article>
            ))}
          </div>
        </section>

        <section className="artifactStrip">
          <div>
            <p className="micro">Durable work</p>
            <h2>Artifacts</h2>
          </div>
          <button className="artifact">
            <FileText size={18} />
            <span>
              <strong>Retention evidence map</strong>
              <small>Updated 4m ago · 18 sources</small>
            </span>
            <ArrowUpRight size={15} />
          </button>
          <button className="artifact">
            <FileText size={18} />
            <span>
              <strong>Board brief outline</strong>
              <small>Draft · 6 sections</small>
            </span>
            <ArrowUpRight size={15} />
          </button>
        </section>
      </section>

      <aside className="attentionRail">
        {selected.status === "approval" ? (
          <ApprovalPanel decided={decision} onDecision={setDecision} />
        ) : selected.status === "failed" ? (
          <section className="recoveryPanel">
            <span className="attentionIndex">01</span>
            <p className="micro">Recovery needed</p>
            <h2>Warehouse query expired</h2>
            <p>
              Completed work is preserved. Retry the final partition or redirect the
              analyst to the cached export.
            </p>
            <button className="approveButton">
              Retry checkpoint <RotateCcw size={16} />
            </button>
          </section>
        ) : (
          <section className="calmPanel">
            <CheckCircle2 size={28} />
            <p className="micro">No decision required</p>
            <h2>{selected.status === "complete" ? "Work is complete" : "Run is in motion"}</h2>
            <p>
              {selected.status === "complete"
                ? "All artifacts passed review and are ready for handoff."
                : "The next checkpoint will appear here if human judgment is required."}
            </p>
          </section>
        )}
        <section className="teamPanel">
          <div className="sectionHeading compact">
            <div>
              <p className="micro">Workstreams</p>
              <h2>{selected.agents} agents</h2>
            </div>
            <ChevronDown size={16} />
          </div>
          {selected.steps.slice(0, 3).map((step) => (
            <div className="agentRow" key={`${selected.id}-${step.owner}`}>
              <span className={`agentInitial ${step.state}`}>{step.owner[0]}</span>
              <span>
                <strong>{step.owner}</strong>
                <small>{step.state === "active" ? "Working now" : step.state}</small>
              </span>
              <i className={step.state} />
            </div>
          ))}
        </section>
      </aside>
    </main>
  );
}
