import {transitionRequest} from "@everything-agentic/domain";

export function createEnterpriseService(repository) {
  return {
    list(actor) { return repository.listRequests(actor.tenantId); },
    create(actor, request, event) {
      if (!new Set(["requester", "admin"]).has(actor.role) || actor.tenantId !== request.tenantId) {
        return {ok: false, code: "unauthorized", message: "This actor cannot create a request in this tenant."};
      }
      if (actor.role === "requester" && actor.id !== request.ownerId) {
        return {ok: false, code: "unauthorized", message: "A requester can create only their own request."};
      }
      if (request.status !== "draft" || event.action !== "request.created") {
        return {ok: false, code: "invalid_state", message: "A new request must begin as a draft with a creation event."};
      }
      repository.saveRequest(request, event);
      return {ok: true, request, event};
    },
    transition(actor, requestId, action, reason = "") {
      const request = repository.getRequest(actor.tenantId, requestId);
      if (!request) {
        return {ok: false, code: "unauthorized", message: "The request is unavailable in this tenant."};
      }
      const result = transitionRequest(request, actor, action, {reason});
      if (result.ok) repository.saveRequest(result.request, result.event);
      return result;
    },
  };
}
