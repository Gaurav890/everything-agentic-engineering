import assert from "node:assert/strict";
import test from "node:test";
import {createLocalEnterpriseRepository} from "@everything-agentic/database";
import {demoActors, demoRequests} from "@everything-agentic/domain";
import {createEnterpriseService} from "../src/index.js";

function draftFor(actor) {
  const now = "2026-08-26T19:00:00Z";
  const request = {
    id: "REQ-3001", tenantId: actor.tenantId, title: "Finance reporting access",
    businessObject: "access request", ownerId: actor.id, ownerName: actor.name,
    status: "draft", risk: "medium", requestedScope: "Read only for fourteen days",
    justification: "Complete the approved close review.", createdAt: now, updatedAt: now,
    evidence: [],
  };
  const event = {
    id: "AUD-REQ-3001-created", requestId: request.id, tenantId: request.tenantId,
    actorId: actor.id, actorName: actor.name, action: "request.created",
    fromStatus: null, toStatus: "draft", reason: "Created from reviewed input.", occurredAt: now,
  };
  return {request, event};
}

test("request creation is role and tenant scoped and persists its audit event", () => {
  const repository = createLocalEnterpriseRepository(demoRequests);
  const service = createEnterpriseService(repository);
  const requester = demoActors.find((actor) => actor.role === "requester");
  const reviewer = demoActors.find((actor) => actor.role === "reviewer" && actor.tenantId === requester.tenantId);
  const {request, event} = draftFor(requester);

  assert.equal(service.create(reviewer, request, event).code, "unauthorized");
  assert.equal(service.create(requester, request, event).ok, true);
  assert.equal(service.list(requester).some((item) => item.id === request.id), true);
  assert.equal(repository.listAudit(requester.tenantId, request.id)[0].action, "request.created");
});

test("tenant visibility fails closed before a transition is attempted", () => {
  const repository = createLocalEnterpriseRepository(demoRequests);
  const service = createEnterpriseService(repository);
  const outsider = demoActors.find((actor) => actor.id === "actor-other-tenant");
  assert.deepEqual(service.list(outsider), []);
  assert.equal(service.transition(outsider, "REQ-2048", "approve").code, "unauthorized");
});
