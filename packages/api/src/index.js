import {transitionRequest} from "@everything-agentic/domain";

const readableRoles = new Set(["requester", "reviewer", "auditor", "admin"]);
const creatorRoles = new Set(["requester", "admin"]);

function denial(code, message) { return {ok: false, code, message}; }

function visibleTo(actor, request, approvalModel) {
  if (!readableRoles.has(actor.role) || actor.tenantId !== request.tenantId) return false;
  if (actor.role === "requester") return actor.id === request.ownerId;
  if (actor.role === "reviewer") return approvalModel === "single-review" || actor.id === request.assignedReviewerId;
  return true;
}

function validRequestInput(request) {
  const evidenceIds = Array.isArray(request?.evidence) ? request.evidence.map((item) => item?.id) : [];
  return request
    && typeof request.id === "string" && request.id.trim()
    && typeof request.tenantId === "string" && request.tenantId.trim()
    && typeof request.ownerId === "string" && request.ownerId.trim()
    && typeof request.title === "string" && request.title.trim()
    && typeof request.businessObject === "string" && request.businessObject.trim()
    && typeof request.requestedScope === "string" && request.requestedScope.trim()
    && typeof request.justification === "string" && request.justification.trim()
    && new Set(["low", "medium", "high"]).has(request.risk)
    && typeof request.assignedReviewerId === "string" && request.assignedReviewerId.trim()
    && Array.isArray(request.evidence) && request.evidence.length > 0
    && request.evidence.every((item) =>
      item
      && typeof item.id === "string" && item.id.trim()
      && typeof item.label === "string" && item.label.trim()
      && typeof item.source === "string" && item.source.trim()
      && new Set(["missing", "partial", "verified"]).has(item.state)
    )
    && new Set(evidenceIds).size === evidenceIds.length;
}

export function createEnterpriseService(repository, options = {}) {
  const approvalModel = options.approvalModel ?? "dual-control";
  const clock = options.clock ?? (() => new Date().toISOString());
  return {
    list(actor) {
      if (!readableRoles.has(actor?.role) || typeof actor?.tenantId !== "string") return [];
      return repository.listRequests(actor.tenantId).filter((request) => visibleTo(actor, request, approvalModel));
    },
    create(actor, request) {
      if (!creatorRoles.has(actor?.role) || actor.tenantId !== request?.tenantId) {
        return denial("unauthorized", "This actor cannot create a request in this tenant.");
      }
      if (actor.role === "requester" && actor.id !== request.ownerId) {
        return denial("unauthorized", "A requester can create only their own request.");
      }
      if (!validRequestInput(request)) {
        return denial("invalid_input", "Title, scope, justification, reviewer assignment, and evidence are required.");
      }
      if (approvalModel !== "single-review" && request.assignedReviewerId === request.ownerId) {
        return denial("invalid_input", "The assigned reviewer must be distinct from the request owner.");
      }
      if (repository.getRequest(actor.tenantId, request.id)) {
        return denial("invalid_state", "A request with this identifier already exists.");
      }
      const occurredAt = clock();
      const trustedRequest = {
        ...request,
        ownerName: actor.role === "requester" ? actor.name : request.ownerName,
        status: "draft",
        evidence: request.evidence.map((item) => ({...item, state: "missing"})),
        policyState: "pending",
        createdAt: occurredAt,
        updatedAt: occurredAt,
      };
      const event = {
        id: `AUD-${trustedRequest.id}-created-${occurredAt}`,
        requestId: trustedRequest.id,
        tenantId: trustedRequest.tenantId,
        actorId: actor.id,
        actorName: actor.name,
        action: "request.created",
        fromStatus: null,
        toStatus: "draft",
        reason: "Created from validated request input.",
        occurredAt,
      };
      repository.saveRequest(trustedRequest, event);
      return {ok: true, request: trustedRequest, event};
    },
    verifyEvidence(actor, requestId) {
      const request = repository.getRequest(actor?.tenantId, requestId);
      if (!request || !creatorRoles.has(actor?.role)) {
        return denial("unauthorized", "This actor cannot run evidence checks for this request.");
      }
      if (actor.role === "requester" && actor.id !== request.ownerId) {
        return denial("unauthorized", "Only the request owner can run evidence checks for this request.");
      }
      if (!new Set(["draft", "changes_requested"]).has(request.status)) {
        return denial("invalid_state", `Evidence checks are not available from ${request.status}.`);
      }
      const occurredAt = clock();
      const updated = {
        ...request,
        evidence: request.evidence.map((item) => ({...item, state: "verified"})),
        policyState: "passed",
        updatedAt: occurredAt,
      };
      const event = {
        id: `AUD-${request.id}-evidence-${occurredAt}`,
        requestId: request.id,
        tenantId: request.tenantId,
        actorId: "local-policy-engine",
        actorName: "Local policy engine",
        action: "request.evidence_verified",
        fromStatus: request.status,
        toStatus: request.status,
        reason: "Synthetic local checks verified every configured evidence requirement.",
        occurredAt,
      };
      repository.saveRequest(updated, event);
      return {ok: true, request: updated, event};
    },
    transition(actor, requestId, action, reason = "") {
      const request = repository.getRequest(actor.tenantId, requestId);
      if (!request) {
        return {ok: false, code: "unauthorized", message: "The request is unavailable in this tenant."};
      }
      const result = transitionRequest(request, actor, action, {reason, approvalModel, now: clock()});
      if (result.ok) repository.saveRequest(result.request, result.event);
      return result;
    },
  };
}
