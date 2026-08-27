const terminalStates = new Set(["approved", "rejected", "cancelled"]);
const transitions = {
  submit: {from: new Set(["draft", "changes_requested"]), to: "in_review", roles: new Set(["requester"])},
  request_changes: {from: new Set(["in_review"]), to: "changes_requested", roles: new Set(["reviewer"])},
  approve: {from: new Set(["in_review"]), to: "approved", roles: new Set(["reviewer"])},
  reject: {from: new Set(["in_review"]), to: "rejected", roles: new Set(["reviewer"])},
  cancel: {from: new Set(["draft", "in_review", "changes_requested"]), to: "cancelled", roles: new Set(["requester", "admin"])},
};

export const demoActors = [
  {id: "actor-requester", name: "Maya Chen", role: "requester", tenantId: "tenant-northstar"},
  {id: "actor-reviewer", name: "Jon Bell", role: "reviewer", tenantId: "tenant-northstar"},
  {id: "actor-reviewer-backup", name: "Priya Shah", role: "reviewer", tenantId: "tenant-northstar"},
  {id: "actor-auditor", name: "Leila Noor", role: "auditor", tenantId: "tenant-northstar"},
  {id: "actor-admin", name: "Sam Ortiz", role: "admin", tenantId: "tenant-northstar"},
  {id: "actor-other-tenant", name: "Ari West", role: "reviewer", tenantId: "tenant-elsewhere"},
];

export const demoRequests = [
  {
    id: "REQ-2048", tenantId: "tenant-northstar", title: "Production analytics access",
    businessObject: "access request", ownerId: "actor-requester", ownerName: "Maya Chen",
    assignedReviewerId: "actor-reviewer", policyState: "passed",
    status: "in_review", risk: "high", requestedScope: "Read-only analytics for 30 days",
    justification: "Validate the renewal cohort before the Q4 planning review.",
    createdAt: "2026-08-24T09:30:00Z", updatedAt: "2026-08-26T16:20:00Z",
    evidence: [
      {id: "E-1", label: "Business justification", state: "verified", source: "Request form"},
      {id: "E-2", label: "Manager attestation", state: "verified", source: "People directory"},
      {id: "E-3", label: "Scope and expiry", state: "verified", source: "Policy check"},
    ],
  },
  {
    id: "REQ-2047", tenantId: "tenant-northstar", title: "Vendor security exception",
    businessObject: "access request", ownerId: "actor-requester", ownerName: "Maya Chen",
    assignedReviewerId: "actor-reviewer", policyState: "pending",
    status: "changes_requested", risk: "medium", requestedScope: "Temporary exception for staging webhook",
    justification: "Unblock the controlled partner validation window.",
    createdAt: "2026-08-23T14:10:00Z", updatedAt: "2026-08-25T11:45:00Z",
    evidence: [
      {id: "E-4", label: "Business justification", state: "verified", source: "Request form"},
      {id: "E-5", label: "Manager attestation", state: "partial", source: "People directory"},
      {id: "E-6", label: "Scope and expiry", state: "verified", source: "Policy check"},
    ],
  },
  {
    id: "REQ-2046", tenantId: "tenant-northstar", title: "Customer export permission",
    businessObject: "access request", ownerId: "actor-requester", ownerName: "Maya Chen",
    assignedReviewerId: "actor-reviewer", policyState: "passed",
    status: "approved", risk: "low", requestedScope: "One-time redacted export",
    justification: "Complete the approved customer portability request.",
    createdAt: "2026-08-22T08:00:00Z", updatedAt: "2026-08-22T12:35:00Z",
    evidence: [
      {id: "E-7", label: "Business justification", state: "verified", source: "Request form"},
      {id: "E-8", label: "Manager attestation", state: "verified", source: "People directory"},
      {id: "E-9", label: "Scope and expiry", state: "verified", source: "Policy check"},
    ],
  },
];

function denial(code, message) { return {ok: false, code, message}; }

export function transitionRequest(request, actor, action, options = {}) {
  const approvalModel = options.approvalModel ?? "dual-control";
  const policy = transitions[action];
  if (!policy || terminalStates.has(request.status) || !policy.from.has(request.status)) {
    return denial("invalid_state", `The ${action} action is not available from ${request.status}.`);
  }
  if (actor.tenantId !== request.tenantId || !policy.roles.has(actor.role)) {
    return denial("unauthorized", "This actor is not authorized for this tenant and transition.");
  }
  if (actor.role === "requester" && actor.id !== request.ownerId) {
    return denial("unauthorized", "Only the request owner can submit or cancel this request.");
  }
  if (
    new Set(["request_changes", "approve", "reject"]).has(action)
    && approvalModel !== "single-review"
    && actor.id !== request.assignedReviewerId
  ) {
    return denial("unauthorized", "Only the assigned reviewer can decide this request under the selected approval model.");
  }
  if (action === "approve" && actor.id === request.ownerId) {
    return denial("unauthorized", "Request owners cannot approve their own request.");
  }
  if ((action === "submit" || action === "approve") && request.evidence.some((item) => item.state !== "verified")) {
    return denial("evidence_incomplete", "Every required evidence item must be verified before submission or approval.");
  }
  if (action === "approve" && approvalModel === "policy-gated" && request.policyState !== "passed") {
    return denial("policy_required", "The policy gate must pass before this request can be approved.");
  }
  if ((action === "request_changes" || action === "reject") && !options.reason?.trim()) {
    return denial("reason_required", "A review reason is required for this decision.");
  }
  const occurredAt = options.now ?? new Date().toISOString();
  const updated = {...request, status: policy.to, updatedAt: occurredAt};
  const event = {
    id: `AUD-${request.id}-${action}-${occurredAt}`, requestId: request.id, tenantId: request.tenantId,
    actorId: actor.id, actorName: actor.name,
    action: `request.${{
      submit: "submitted",
      request_changes: "changes_requested",
      approve: "approved",
      reject: "rejected",
      cancel: "cancelled",
    }[action]}`,
    fromStatus: request.status, toStatus: policy.to,
    reason: options.reason?.trim() || "Transition completed through the reviewed workflow.", occurredAt,
  };
  return {ok: true, request: updated, event};
}
