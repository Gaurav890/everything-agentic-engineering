import type {EnterpriseRepository} from "@everything-agentic/database";
import type {EnterpriseActor, TransitionResult, WorkflowAction, WorkflowRequest} from "@everything-agentic/types";
export type EnterpriseService = {
  list(actor: EnterpriseActor): WorkflowRequest[];
  create(actor: EnterpriseActor, request: WorkflowRequest): TransitionResult;
  verifyEvidence(actor: EnterpriseActor, requestId: string): TransitionResult;
  transition(actor: EnterpriseActor, requestId: string, action: WorkflowAction, reason?: string): TransitionResult;
};
export declare function createEnterpriseService(
  repository: EnterpriseRepository,
  options?: {approvalModel?: "single-review" | "dual-control" | "policy-gated"; clock?: () => string},
): EnterpriseService;
