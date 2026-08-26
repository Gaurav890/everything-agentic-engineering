export type EnterpriseRole = "requester" | "reviewer" | "auditor" | "admin";
export type RequestStatus = "draft" | "in_review" | "changes_requested" | "approved" | "rejected" | "cancelled";
export type WorkflowAction = "submit" | "request_changes" | "approve" | "reject" | "cancel";
export type EvidenceState = "missing" | "partial" | "verified";

export type EnterpriseActor = {id: string; name: string; role: EnterpriseRole; tenantId: string};
export type RequestEvidence = {id: string; label: string; state: EvidenceState; source: string};
export type WorkflowRequest = {
  id: string;
  tenantId: string;
  title: string;
  businessObject: string;
  ownerId: string;
  ownerName: string;
  status: RequestStatus;
  risk: "low" | "medium" | "high";
  requestedScope: string;
  justification: string;
  createdAt: string;
  updatedAt: string;
  evidence: RequestEvidence[];
};
export type AuditEvent = {
  id: string;
  requestId: string;
  tenantId: string;
  actorId: string;
  actorName: string;
  action: string;
  fromStatus: RequestStatus | null;
  toStatus: RequestStatus;
  reason: string;
  occurredAt: string;
};
export type TransitionResult =
  | {ok: true; request: WorkflowRequest; event: AuditEvent}
  | {ok: false; code: "unauthorized" | "invalid_state" | "evidence_incomplete" | "reason_required"; message: string};
export type EnterpriseManifest = {
  schema_version: 1;
  enabled: boolean;
  business_object: {singular: string; plural: string};
  tenant_model: "single-tenant" | "multi-tenant";
  approval_model: "single-review" | "dual-control" | "policy-gated";
  data_sensitivity: "internal" | "confidential" | "restricted";
  roles: EnterpriseRole[];
  workflow_states: RequestStatus[];
  required_evidence: string[];
  audit_events: string[];
  adapters: {authentication: "local-demo"; persistence: "local-demo"; notifications: "disabled"; production_ready: false};
};
