import type {EnterpriseActor, TransitionResult, WorkflowAction, WorkflowRequest} from "@everything-agentic/types";
export declare const demoActors: EnterpriseActor[];
export declare const demoRequests: WorkflowRequest[];
export declare function transitionRequest(
  request: WorkflowRequest,
  actor: EnterpriseActor,
  action: WorkflowAction,
  options?: {reason?: string; now?: string; approvalModel?: "single-review" | "dual-control" | "policy-gated"},
): TransitionResult;
