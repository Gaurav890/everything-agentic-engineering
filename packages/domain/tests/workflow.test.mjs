import assert from "node:assert/strict";
import test from "node:test";
import {demoActors, demoRequests, transitionRequest} from "../src/index.js";

const request = demoRequests[0];
const reviewer = demoActors.find((actor) => actor.role === "reviewer" && actor.tenantId === request.tenantId);

test("authorized approval creates an audit event without mutating input", () => {
  const result = transitionRequest(request, reviewer, "approve", {now: "2026-08-26T18:00:00Z"});
  assert.equal(result.ok, true);
  assert.equal(result.request.status, "approved");
  assert.equal(result.event.action, "request.approved");
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

test("submission requires complete evidence and request ownership", () => {
  const requester = demoActors.find((actor) => actor.id === request.ownerId);
  const partial = {...request, status: "draft", evidence: request.evidence.map((item, index) => index === 0 ? {...item, state: "partial"} : item)};
  const complete = {...request, status: "draft"};
  const otherRequester = {...requester, id: "actor-requester-2"};

  assert.equal(transitionRequest(partial, requester, "submit").code, "evidence_incomplete");
  assert.equal(transitionRequest(complete, otherRequester, "submit").code, "unauthorized");
  assert.equal(transitionRequest(complete, requester, "submit").request.status, "in_review");
});

test("approval models enforce assignment and policy gates", () => {
  const backup = demoActors.find((actor) => actor.id === "actor-reviewer-backup");
  const selfReviewer = {...reviewer, id: request.ownerId};
  assert.equal(transitionRequest(request, backup, "approve", {approvalModel: "dual-control"}).code, "unauthorized");
  assert.equal(transitionRequest(request, backup, "approve", {approvalModel: "single-review"}).ok, true);
  assert.equal(transitionRequest(request, selfReviewer, "approve", {approvalModel: "single-review"}).code, "unauthorized");
  assert.equal(transitionRequest({...request, policyState: "pending"}, reviewer, "approve", {approvalModel: "policy-gated"}).code, "policy_required");
  assert.equal(transitionRequest(request, reviewer, "approve", {approvalModel: "policy-gated"}).ok, true);
});

test("request changes, rejection, cancellation, and resubmission record consequences", () => {
  const requester = demoActors.find((actor) => actor.id === request.ownerId);
  const changes = transitionRequest(request, reviewer, "request_changes", {reason: "Narrow the scope.", now: "2026-08-26T18:01:00Z"});
  assert.equal(changes.request.status, "changes_requested");
  assert.equal(changes.event.reason, "Narrow the scope.");
  assert.equal(transitionRequest(changes.request, requester, "submit").request.status, "in_review");
  assert.equal(transitionRequest(request, reviewer, "reject", {reason: "Risk exceeds policy."}).request.status, "rejected");
  assert.equal(transitionRequest({...request, status: "draft"}, requester, "cancel").request.status, "cancelled");
  assert.equal(transitionRequest({...request, status: "draft"}, demoActors.find((actor) => actor.role === "admin"), "cancel").request.status, "cancelled");
});
