import assert from "node:assert/strict";
import test from "node:test";
import {demoActors, demoRequests, transitionRequest} from "../src/index.js";

const request = demoRequests[0];
const reviewer = demoActors.find((actor) => actor.role === "reviewer" && actor.tenantId === request.tenantId);

test("authorized approval creates an audit event without mutating input", () => {
  const result = transitionRequest(request, reviewer, "approve", {now: "2026-08-26T18:00:00Z"});
  assert.equal(result.ok, true);
  assert.equal(result.request.status, "approved");
  assert.equal(result.event.action, "request.approve");
  assert.equal(request.status, "in_review");
});

test("cross-tenant and read-only actors fail closed", () => {
  const crossTenant = demoActors.find((actor) => actor.id === "actor-other-tenant");
  const auditor = demoActors.find((actor) => actor.role === "auditor");
  assert.equal(transitionRequest(request, crossTenant, "approve").code, "unauthorized");
  assert.equal(transitionRequest(request, auditor, "approve").code, "unauthorized");
});

test("incomplete evidence blocks approval", () => {
  const incomplete = {...request, evidence: request.evidence.map((item, index) => index === 0 ? {...item, state: "partial"} : item)};
  assert.equal(transitionRequest(incomplete, reviewer, "approve").code, "evidence_incomplete");
});

test("review reasons and terminal states are enforced", () => {
  assert.equal(transitionRequest(request, reviewer, "reject").code, "reason_required");
  assert.equal(transitionRequest({...request, status: "approved"}, reviewer, "approve").code, "invalid_state");
});
