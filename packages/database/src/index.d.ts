import type {AuditEvent, WorkflowRequest} from "@everything-agentic/types";
export type EnterpriseRepository = {
  listRequests(tenantId: string): WorkflowRequest[];
  getRequest(tenantId: string, requestId: string): WorkflowRequest | null;
  saveRequest(request: WorkflowRequest, event: AuditEvent): void;
  listAudit(tenantId: string, requestId: string): AuditEvent[];
};
export declare function createLocalEnterpriseRepository(seed: WorkflowRequest[]): EnterpriseRepository;
