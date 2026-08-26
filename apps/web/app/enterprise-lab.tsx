"use client";

import {createEnterpriseService} from "@everything-agentic/api";
import {createLocalEnterpriseRepository} from "@everything-agentic/database";
import {demoActors, demoRequests} from "@everything-agentic/domain";
import type {
  AuditEvent,
  EnterpriseActor,
  EnterpriseManifest,
  RequestStatus,
  WorkflowAction,
  WorkflowRequest,
} from "@everything-agentic/types";
import {useEffect, useMemo, useRef, useState} from "react";

import type {ExperienceManifest} from "./experience-types";

const directions = [
  {id: "editorial-signal", number: "01", name: "Editorial Signal", palette: ["#f4efe3", "#181411", "#c7220f"]},
  {id: "kinetic-index", number: "02", name: "Kinetic Index", palette: ["#090a09", "#efffe3", "#adff29"]},
  {id: "quiet-material", number: "03", name: "Quiet Material", palette: ["#e5eddc", "#142228", "#155257"]},
] as const;

type DirectionId = (typeof directions)[number]["id"];
type LoadState = "ready" | "loading" | "error";
type Filter = "all" | RequestStatus | "empty";

const characterDirection = {
  precise: "editorial-signal",
  bold: "kinetic-index",
  warm: "quiet-material",
  experimental: "kinetic-index",
} as const satisfies Record<ExperienceManifest["visual_character"], DirectionId>;

const statusLabel: Record<RequestStatus, string> = {
  draft: "Draft",
  in_review: "In review",
  changes_requested: "Changes requested",
  approved: "Approved",
  rejected: "Rejected",
  cancelled: "Cancelled",
};

const initialAudit: AuditEvent[] = [
  {
    id: "AUD-SEED-2", requestId: "REQ-2048", tenantId: "tenant-northstar",
    actorId: "policy-engine", actorName: "Policy engine", action: "request.submitted",
    fromStatus: "draft", toStatus: "in_review", reason: "Three evidence requirements verified.",
    occurredAt: "2026-08-26T16:20:00Z",
  },
  {
    id: "AUD-SEED-1", requestId: "REQ-2048", tenantId: "tenant-northstar",
    actorId: "actor-requester", actorName: "Maya Chen", action: "request.created",
    fromStatus: null, toStatus: "draft", reason: "Created from the reviewed request form.",
    occurredAt: "2026-08-24T09:30:00Z",
  },
];

function shortTime(value: string) {
  return new Intl.DateTimeFormat("en", {month: "short", day: "numeric", hour: "numeric", minute: "2-digit", timeZone: "UTC"}).format(new Date(value));
}

function DirectionDock({active, approved, onChange}: {active: DirectionId; approved: string | null; onChange: (id: DirectionId) => void}) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState<"idle" | "copied" | "error">("idle");
  const trigger = useRef<HTMLButtonElement>(null);
  const first = useRef<HTMLButtonElement>(null);
  const command = `./agentic design approve ${active} --yes`;

  useEffect(() => {
    function onEscape(event: KeyboardEvent) {
      if (event.key === "Escape" && open) {
        setOpen(false);
        trigger.current?.focus();
      }
    }
    window.addEventListener("keydown", onEscape);
    return () => window.removeEventListener("keydown", onEscape);
  }, [open]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(command);
      setCopied("copied");
      window.setTimeout(() => setCopied("idle"), 1600);
    } catch {
      setCopied("error");
    }
  }

  return (
    <aside className="direction-dock" aria-label="Design direction comparison" data-open={open}>
      <button
        className="direction-trigger" type="button" ref={trigger}
        aria-controls="enterprise-direction-panel" aria-expanded={open}
        onClick={() => {
          const next = !open;
          setOpen(next);
          if (next) window.setTimeout(() => first.current?.focus(), 0);
        }}
      >
        <span>Direction</span><strong>{directions.find((item) => item.id === active)?.name}</strong><b aria-hidden="true">{open ? "×" : "+"}</b>
      </button>
      <div className="direction-dock-panel" id="enterprise-direction-panel">
        <div className="dock-intro"><span className="dock-kicker">Enterprise lab</span><strong>Same workflow. Three systems.</strong></div>
        <div className="direction-options" role="group" aria-label="Choose a direction to preview">
          {directions.map((item, index) => (
            <button
              key={item.id} ref={index === 0 ? first : undefined} type="button"
              className="direction-option" data-selected={active === item.id} aria-pressed={active === item.id}
              onClick={() => {
                onChange(item.id);
                setCopied("idle");
                if (window.matchMedia("(max-width: 680px)").matches) {
                  setOpen(false);
                  window.setTimeout(() => trigger.current?.focus(), 0);
                }
              }}
            >
              <span>{item.number}</span><strong>{item.name}</strong>
              <span className="palette" aria-label={`${item.name} palette`}>
                {item.palette.map((color) => <i key={color} style={{background: color}} />)}
              </span>
            </button>
          ))}
        </div>
        <div className="approval">
          <code>{command}</code>
          <button type="button" className="eae-button" data-size="compact" onClick={copy}>
            {copied === "copied" ? "Command copied" : copied === "error" ? "Copy failed — try again" : active === approved ? "Approved direction" : "Copy approval command"}
          </button>
          <span className="copy-status" role="status" aria-live="polite">
            {copied === "copied" ? "Approval command copied to the clipboard." : copied === "error" ? "The approval command could not be copied. Try again." : ""}
          </span>
        </div>
      </div>
    </aside>
  );
}

function CreateRequest({open, onClose, onCreate, objectName, actor}: {open: boolean; onClose: () => void; onCreate: (request: WorkflowRequest, event: AuditEvent) => void; objectName: string; actor: EnterpriseActor}) {
  const titleRef = useRef<HTMLInputElement>(null);
  const [title, setTitle] = useState("");
  const [scope, setScope] = useState("");
  const [justification, setJustification] = useState("");
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    window.setTimeout(() => titleRef.current?.focus(), 0);
    function keepFocus(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = Array.from(document.querySelectorAll<HTMLElement>(".enterprise-modal button, .enterprise-modal input, .enterprise-modal textarea"));
      const first = controls[0];
      const last = controls.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
    window.addEventListener("keydown", keepFocus);
    return () => { window.removeEventListener("keydown", keepFocus); previous?.focus(); };
  }, [open, onClose]);
  if (!open) return null;
  const invalid = !title.trim() || !scope.trim() || !justification.trim();

  function submit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitted(true);
    if (invalid) return;
    const now = new Date().toISOString();
    const id = `REQ-${Math.floor(3000 + Math.random() * 6000)}`;
    const request: WorkflowRequest = {
      id, tenantId: "tenant-northstar", title: title.trim(), businessObject: objectName,
      ownerId: actor.id, ownerName: actor.name, status: "draft", risk: "medium",
      requestedScope: scope.trim(), justification: justification.trim(), createdAt: now, updatedAt: now,
      evidence: [
        {id: `${id}-E1`, label: "Business justification", state: "verified", source: "Request form"},
        {id: `${id}-E2`, label: "Manager attestation", state: "missing", source: "People directory"},
        {id: `${id}-E3`, label: "Scope and expiry", state: "partial", source: "Policy check"},
      ],
    };
    onCreate(request, {
      id: `AUD-${id}-created`, requestId: id, tenantId: request.tenantId,
      actorId: request.ownerId, actorName: request.ownerName, action: "request.created",
      fromStatus: null, toStatus: "draft", reason: "Created from the reviewed request form.", occurredAt: now,
    });
    setTitle(""); setScope(""); setJustification(""); setSubmitted(false); onClose();
  }

  return (
    <div className="enterprise-modal-layer" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <section className="enterprise-modal" role="dialog" aria-modal="true" aria-labelledby="new-request-title">
        <div className="enterprise-modal-heading">
          <div><span>New {objectName}</span><h2 id="new-request-title">Make the decision reviewable.</h2></div>
          <button type="button" onClick={onClose} aria-label="Close request form">×</button>
        </div>
        <form onSubmit={submit} noValidate>
          <label>Request title<input ref={titleRef} value={title} onChange={(event) => setTitle(event.target.value)} aria-invalid={submitted && !title.trim()} />{submitted && !title.trim() ? <small>Give reviewers a precise title.</small> : null}</label>
          <label>Requested scope<input value={scope} onChange={(event) => setScope(event.target.value)} aria-invalid={submitted && !scope.trim()} />{submitted && !scope.trim() ? <small>State what access or exception is requested.</small> : null}</label>
          <label>Business justification<textarea value={justification} onChange={(event) => setJustification(event.target.value)} aria-invalid={submitted && !justification.trim()} />{submitted && !justification.trim() ? <small>Explain the business consequence.</small> : null}</label>
          <p><strong>Demo boundary:</strong> this creates local synthetic data only. No notification, production write, or credential use occurs.</p>
          <div><button type="button" onClick={onClose}>Cancel</button><button type="submit" className="enterprise-primary">Create draft</button></div>
        </form>
      </section>
    </div>
  );
}

export function EnterpriseLab({experience, enterprise, approvedDirection}: {experience: ExperienceManifest; enterprise: EnterpriseManifest; approvedDirection: string | null}) {
  const approved = directions.some((item) => item.id === approvedDirection) ? approvedDirection : null;
  const [active, setActive] = useState<DirectionId>((approved as DirectionId | null) ?? characterDirection[experience.visual_character]);
  const repository = useMemo(() => createLocalEnterpriseRepository(demoRequests), []);
  const service = useMemo(() => createEnterpriseService(repository), [repository]);
  const [actorId, setActorId] = useState("actor-reviewer");
  const actor = demoActors.find((item) => item.id === actorId) as EnterpriseActor;
  const canCreate = actor.role === "requester" || actor.role === "admin";
  const [requests, setRequests] = useState<WorkflowRequest[]>(() => service.list(demoActors[1] as EnterpriseActor));
  const [selectedId, setSelectedId] = useState("REQ-2048");
  const [audit, setAudit] = useState<AuditEvent[]>(initialAudit);
  const [filter, setFilter] = useState<Filter>("all");
  const [loadState, setLoadState] = useState<LoadState>("ready");
  const [notice, setNotice] = useState("Three evidence checks are ready for a human decision.");
  const [reason, setReason] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const allRequests = requests;
  const selected = allRequests.find((request) => request.id === selectedId) ?? allRequests[0];
  const visible = filter === "empty" ? [] : filter === "all" ? allRequests : allRequests.filter((request) => request.status === filter);

  function refresh() {
    setLoadState("loading");
    window.setTimeout(() => {
      setRequests(service.list(actor));
      setLoadState("ready");
      setNotice(actor.tenantId === "tenant-northstar" ? "The tenant-scoped queue is current." : "No requests are exposed across the tenant boundary.");
    }, 420);
  }

  function changeActor(nextId: string) {
    const next = demoActors.find((item) => item.id === nextId) as EnterpriseActor;
    const nextRequests = service.list(next);
    setActorId(nextId);
    setRequests(nextRequests);
    setSelectedId(nextRequests[0]?.id ?? "");
    setNotice(nextRequests.length > 0
      ? "Actor changed. Tenant visibility and permissions were re-evaluated."
      : "No requests are exposed across the tenant boundary.");
  }

  function applyAction(action: WorkflowAction) {
    if (!selected) return;
    const result = service.transition(actor, selected.id, action, reason);
    if (!result.ok) {
      setNotice(result.message);
      return;
    }
    setRequests((current) => current.map((item) => item.id === result.request.id ? result.request : item));
    setAudit((current) => [result.event, ...current]);
    setReason("");
    setNotice(`${statusLabel[result.request.status]} recorded. The audit trail now shows who changed what and why.`);
  }

  function addRequest(request: WorkflowRequest, event: AuditEvent) {
    const result = service.create(actor, request, event);
    if (!result.ok) {
      setNotice(result.message);
      return;
    }
    setRequests(service.list(actor));
    setAudit((current) => [event, ...current]);
    setSelectedId(request.id);
    setFilter("all");
    setNotice("Draft created locally. Evidence remains incomplete, so approval is unavailable.");
  }

  return (
    <main className="experience enterprise-experience" data-archetype="enterprise-workflow" data-direction={active} data-character={experience.visual_character} data-approved={active === approved ? "true" : "false"}>
      <a className="skip-link" href="#product-proof">Skip to product proof</a>
      <DirectionDock active={active} approved={approved} onChange={setActive} />
      <div className="product-shell enterprise-shell">
        <header className="enterprise-topbar">
          <a href="#enterprise-main" className="enterprise-brand" aria-label={`${experience.name}, workspace`}><i aria-hidden="true" /><span>{experience.name}</span><small>Decision operations</small></a>
          <div className="enterprise-context"><span className="stage-live"><i /> Local demonstration</span><strong>Northstar Systems</strong></div>
          <div className="enterprise-actor">
            <label htmlFor="actor-select">Acting as</label>
            <select id="actor-select" value={actorId} onChange={(event) => changeActor(event.target.value)}>
              {demoActors.map((item) => <option key={item.id} value={item.id}>{item.name} · {item.role}{item.tenantId !== "tenant-northstar" ? " · other tenant" : ""}</option>)}
            </select>
          </div>
        </header>

        <div className="enterprise-frame">
          <nav className="enterprise-rail" aria-label="Workspace">
            <a href="#enterprise-main" aria-current="page"><span>01</span>Decisions</a>
            <a href="#audit-trail"><span>02</span>Audit</a>
            <a href="#enterprise-contract"><span>03</span>Controls</a>
            <p><small>Tenant boundary</small><strong>{enterprise.tenant_model}</strong><span>{enterprise.data_sensitivity} data</span></p>
          </nav>

          <section className="enterprise-main" id="enterprise-main" aria-labelledby="product-title">
            <div className="enterprise-heading">
              <div><p className="eyebrow">Decision queue · {enterprise.business_object.plural}</p><h1 id="product-title">{experience.promise}</h1><p>{experience.audience}. Every consequential transition is scoped, reviewable, and attributable.</p></div>
              <button
                type="button" className="enterprise-primary"
                onClick={() => setCreateOpen(true)}
                disabled={!canCreate}
                title={!canCreate ? "Switch to a requester or administrator to create a request." : undefined}
              >New {enterprise.business_object.singular} <span aria-hidden="true">＋</span></button>
            </div>

            <div className="enterprise-metrics" aria-label="Queue summary">
              <article><span>Awaiting decision</span><strong>{allRequests.filter((item) => item.status === "in_review").length.toString().padStart(2, "0")}</strong><small>Evidence-ready requests</small></article>
              <article><span>Needs changes</span><strong>{allRequests.filter((item) => item.status === "changes_requested").length.toString().padStart(2, "0")}</strong><small>Returned with rationale</small></article>
              <article><span>Control coverage</span><strong>100%</strong><small>{enterprise.approval_model.replace("-", " ")}</small></article>
            </div>

            <section className="enterprise-workspace" id="product-proof" aria-label="Enterprise request workflow">
              <div className="enterprise-queue">
                <div className="queue-toolbar">
                  <div><span>Request queue</span><strong>{visible.length} visible</strong></div>
                  <label><span className="sr-only">Filter requests</span><select value={filter} onChange={(event) => setFilter(event.target.value as Filter)}><option value="all">All states</option><option value="in_review">In review</option><option value="changes_requested">Needs changes</option><option value="approved">Approved</option><option value="empty">Empty state</option></select></label>
                  <button type="button" onClick={refresh} disabled={loadState === "loading"}>{loadState === "loading" ? "Refreshing…" : "Refresh"}</button>
                  <button type="button" onClick={() => setLoadState("error")}>Test failure</button>
                </div>
                {loadState === "error" ? (
                  <div className="enterprise-state" role="alert"><span>Connection interrupted</span><strong>The queue could not be refreshed.</strong><p>No local decision was lost and no action was retried automatically.</p><button type="button" onClick={refresh}>Retry safely</button></div>
                ) : loadState === "loading" ? (
                  <div className="enterprise-state" role="status"><span>Loading tenant-scoped requests</span><strong>Confirming policy and evidence state…</strong></div>
                ) : visible.length === 0 ? (
                  <div className="enterprise-state"><span>Queue clear</span><strong>No requests match this view.</strong><p>Change the filter or create a synthetic draft.</p><button type="button" onClick={() => setFilter("all")}>Show all requests</button></div>
                ) : (
                  <div className="request-list" aria-label="Requests">
                    {visible.map((request) => (
                      <button key={request.id} type="button" data-selected={request.id === selected?.id} onClick={() => setSelectedId(request.id)}>
                        <span className="request-risk" data-risk={request.risk}>{request.risk}</span>
                        <span><strong>{request.title}</strong><small>{request.id} · {request.ownerName}</small></span>
                        <span className="request-status" data-status={request.status}>{statusLabel[request.status]}</span>
                        <time dateTime={request.updatedAt}>{shortTime(request.updatedAt)}</time>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <aside className="enterprise-detail" aria-live="polite">
                {selected ? <>
                  <div className="detail-heading"><div><span>{selected.id} · {selected.risk} risk</span><h2>{selected.title}</h2></div><span className="request-status" data-status={selected.status}>{statusLabel[selected.status]}</span></div>
                  <dl><div><dt>Owner</dt><dd>{selected.ownerName}</dd></div><div><dt>Scope</dt><dd>{selected.requestedScope}</dd></div><div><dt>Justification</dt><dd>{selected.justification}</dd></div></dl>
                  <div className="evidence-panel"><div><span>Required evidence</span><strong>{selected.evidence.filter((item) => item.state === "verified").length} / {selected.evidence.length} verified</strong></div><ul>{selected.evidence.map((item) => <li key={item.id} data-state={item.state}><i aria-hidden="true" /><span><strong>{item.label}</strong><small>{item.source}</small></span><b>{item.state}</b></li>)}</ul></div>
                  <label className="decision-reason">Decision rationale<textarea value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Required for rejection or requested changes" /></label>
                  <div className="enterprise-actions">
                    <button type="button" onClick={() => applyAction("request_changes")}>Request changes</button>
                    <button type="button" onClick={() => applyAction("reject")}>Reject</button>
                    <button type="button" onClick={() => applyAction("cancel")}>Cancel</button>
                    <button type="button" className="enterprise-primary" onClick={() => applyAction("approve")} disabled={selected.status !== "in_review" || selected.evidence.some((item) => item.state !== "verified")}>Approve request</button>
                  </div>
                  <p className="enterprise-notice" role="status">{notice}</p>
                </> : <div className="enterprise-state" role="status"><span>Tenant boundary enforced</span><strong>{notice}</strong><p>Select a permitted request to inspect its evidence and allowed transitions.</p></div>}
              </aside>
            </section>

            <section className="audit-section" id="audit-trail" aria-labelledby="audit-title">
              <div><p className="eyebrow">Append-only evidence</p><h2 id="audit-title">The decision leaves a trail.</h2><p>Local demo events mirror the contract a production adapter must persist. They do not represent a production audit store.</p></div>
              <ol>{audit.filter((event) => !selected || event.requestId === selected.id).map((event) => <li key={event.id}><i aria-hidden="true" /><div><strong>{event.action.replace("request.", "").replace("_", " ")}</strong><span>{event.actorName} · {event.reason}</span></div><time dateTime={event.occurredAt}>{shortTime(event.occurredAt)}</time></li>)}</ol>
            </section>

            <section className="enterprise-contract" id="enterprise-contract" aria-label="Enterprise adapter boundary">
              <div><span>Auth</span><strong>{enterprise.adapters.authentication}</strong><small>Replace before production</small></div>
              <div><span>Persistence</span><strong>{enterprise.adapters.persistence}</strong><small>Repository interface ready</small></div>
              <div><span>Notifications</span><strong>{enterprise.adapters.notifications}</strong><small>No silent side effects</small></div>
              <p><strong>Production-ready?</strong> No. The contract is credible; the local adapters are intentionally bounded.</p>
            </section>
          </section>
        </div>
      </div>
      <CreateRequest open={createOpen} onClose={() => setCreateOpen(false)} onCreate={addRequest} objectName={enterprise.business_object.singular} actor={actor} />
    </main>
  );
}
