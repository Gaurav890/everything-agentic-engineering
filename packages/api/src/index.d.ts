import type {EnterpriseRepository} from "@everything-agentic/database";
import type {AuditEvent, EnterpriseActor, TransitionResult, WorkflowAction, WorkflowRequest} from "@everything-agentic/types";
export type EnterpriseService = {
  list(actor: EnterpriseActor): WorkflowRequest[];
  create(actor: EnterpriseActor, request: WorkflowRequest, event: AuditEvent): TransitionResult;
  transition(actor: EnterpriseActor, requestId: string, action: WorkflowAction, reason?: string): TransitionResult;
};
export declare function createEnterpriseService(repository: EnterpriseRepository): EnterpriseService;
