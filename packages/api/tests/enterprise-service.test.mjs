import assert from "node:assert/strict";
import test from "node:test";
import {createLocalEnterpriseRepository} from "@everything-agentic/database";
import {demoActors, demoRequests} from "@everything-agentic/domain";
import {createEnterpriseService} from "../src/index.js";

function draftFor(actor) {
  const now = "2026-08-26T19:00:00Z";
  return {
    id: "REQ-3001", tenantId: actor.tenantId, title: "Finance reporting access",
    businessObject: "access request", ownerId: actor.id, ownerName: actor.name,
    assignedReviewerId: "actor-reviewer", policyState: "pending",
    status: "draft", risk: "medium", requestedScope: "Read only for fourteen days",
    justification: "Complete the approved close review.", createdAt: now, updatedAt: now,
    evidence: [
      {id: "REQ-3001-E1", label: "Business justification", state: "verified", source: "Request form"},
      {id: "REQ-3001-E2", label: "Manager attestation", state: "missing", source: "People directory"},
      {id: "REQ-3001-E3", label: "Scope and expiry", state: "partial", source: "Policy check"},
    ],
  };
}

test("request creation is validated and constructs trusted audit attribution", () => {
  const repository = createLocalEnterpriseRepository(demoRequests);
  const trustedTime = "2026-08-26T19:05:00Z";
  const service = createEnterpriseService(repository, {clock: () => trustedTime});
  const requester = demoActors.find((actor) => actor.role === "requester");
  const reviewer = demoActors.find((actor) => actor.role === "reviewer" && actor.tenantId === requester.tenantId);
  const request = draftFor(requester);

  assert.equal(service.create(reviewer, request).code, "unauthorized");
  assert.equal(service.create(requester, {...request, title: ""}).code, "invalid_input");
  const result = service.create(requester, {...request, ownerName: "Forged Admin", status: "approved"}, {now: "1900-01-01T00:00:00Z", actorName: "Forged Admin"});
  assert.equal(result.ok, true);
  assert.equal(result.request.status, "draft");
  assert.equal(result.request.evidence.every((item) => item.state === "missing"), true);
  assert.equal(result.request.ownerName, requester.name);
  assert.equal(result.event.actorId, requester.id);
  assert.equal(result.event.actorName, requester.name);
  assert.equal(result.event.fromStatus, null);
  assert.equal(result.event.toStatus, "draft");
  assert.equal(result.event.occurredAt, trustedTime);
  assert.equal(result.request.createdAt, trustedTime);
  assert.equal(result.request.updatedAt, trustedTime);
  assert.equal(service.list(requester).some((item) => item.id === request.id), true);
  assert.equal(repository.listAudit(requester.tenantId, request.id)[0].action, "request.created");
});

test("tenant, role, owner, and reviewer visibility fail closed", () => {
  const repository = createLocalEnterpriseRepository(demoRequests);
  const service = createEnterpriseService(repository);
  const requester = demoActors.find((actor) => actor.id === "actor-requester");
  const reviewer = demoActors.find((actor) => actor.id === "actor-reviewer");
  const backup = demoActors.find((actor) => actor.id === "actor-reviewer-backup");
  const auditor = demoActors.find((actor) => actor.id === "actor-auditor");
  const unknown = {id: "actor-unknown", name: "Unknown", role: "unknown", tenantId: requester.tenantId};
  const otherRequester = {id: "actor-requester-2", name: "Other", role: "requester", tenantId: requester.tenantId};
  const outsider = demoActors.find((actor) => actor.id === "actor-other-tenant");

  assert.equal(service.list(requester).length, 3);
  assert.equal(service.list(reviewer).length, 3);
  assert.deepEqual(service.list(backup), []);
  assert.equal(service.list(auditor).length, 3);
  assert.deepEqual(service.list(unknown), []);
  assert.deepEqual(service.list(otherRequester), []);
  assert.deepEqual(service.list(outsider), []);
  assert.equal(service.transition(outsider, "REQ-2048", "approve").code, "unauthorized");
});

test("created drafts complete evidence, submit, return for changes, resubmit, and approve", () => {
  const repository = createLocalEnterpriseRepository(demoRequests);
  const service = createEnterpriseService(repository, {approvalModel: "dual-control"});
  const requester = demoActors.find((actor) => actor.id === "actor-requester");
  const reviewer = demoActors.find((actor) => actor.id === "actor-reviewer");
  const request = draftFor(requester);

  assert.equal(service.create(requester, request).ok, true);
  assert.equal(service.transition(requester, request.id, "submit").code, "evidence_incomplete");
  assert.equal(service.verifyEvidence(reviewer, request.id).code, "unauthorized");
  assert.equal(service.verifyEvidence(requester, request.id).ok, true);
  assert.equal(service.transition(requester, request.id, "submit").ok, true);
  assert.equal(service.transition(reviewer, request.id, "request_changes").code, "reason_required");
  assert.equal(service.transition(reviewer, request.id, "request_changes", "Narrow the requested scope.").ok, true);
  assert.equal(service.transition(requester, request.id, "submit").ok, true);
  assert.equal(service.transition(reviewer, request.id, "approve").ok, true);
  assert.deepEqual(
    repository.listAudit(requester.tenantId, request.id).map((event) => event.action),
    ["request.created", "request.evidence_verified", "request.submitted", "request.changes_requested", "request.submitted", "request.approved"],
  );
});

test("all mutations use the service-owned clock and ignore caller timestamps", () => {
  const repository = createLocalEnterpriseRepository([]);
  const times = ["2026-08-26T19:00:00Z", "2026-08-26T19:01:00Z", "2026-08-26T19:02:00Z"];
  let tick = 0;
  const service = createEnterpriseService(repository, {clock: () => times[tick++]});
  const requester = demoActors.find((actor) => actor.id === "actor-requester");
  const forgedTime = "1900-01-01T00:00:00Z";
  const request = {...draftFor(requester), createdAt: forgedTime, updatedAt: forgedTime};

  const created = service.create(requester, request, {now: forgedTime});
  const verified = service.verifyEvidence(requester, request.id, {now: forgedTime});
  const submitted = service.transition(requester, request.id, "submit", "", {now: forgedTime});

  for (const [index, result] of [created, verified, submitted].entries()) {
    assert.equal(result.ok, true);
    assert.equal(result.event.occurredAt, times[index]);
    assert.equal(result.request.updatedAt, times[index]);
    assert.equal(result.request.createdAt, times[0]);
    assert.equal(result.event.id.endsWith(times[index]), true);
  }
  assert.deepEqual(repository.listAudit(requester.tenantId, request.id).map((event) => event.occurredAt), times);
});

test("approval models enforce distinct executable policies", () => {
  const reviewer = demoActors.find((actor) => actor.id === "actor-reviewer");
  const backup = demoActors.find((actor) => actor.id === "actor-reviewer-backup");

  const dualRepository = createLocalEnterpriseRepository(demoRequests);
  const dual = createEnterpriseService(dualRepository, {approvalModel: "dual-control"});
  assert.equal(dual.transition(backup, "REQ-2048", "approve").code, "unauthorized");
  assert.equal(dual.transition(reviewer, "REQ-2048", "approve").ok, true);

  const singleRepository = createLocalEnterpriseRepository(demoRequests);
  const single = createEnterpriseService(singleRepository, {approvalModel: "single-review"});
  assert.equal(single.transition(backup, "REQ-2048", "approve").ok, true);

  const gatedSeed = demoRequests.map((request) => request.id === "REQ-2048" ? {...request, policyState: "pending"} : request);
  const gatedRepository = createLocalEnterpriseRepository(gatedSeed);
  const gated = createEnterpriseService(gatedRepository, {approvalModel: "policy-gated"});
  assert.equal(gated.transition(reviewer, "REQ-2048", "approve").code, "policy_required");
});
