export type RunStatus = "active" | "approval" | "complete" | "failed";

export type Run = {
  id: string;
  eyebrow: string;
  title: string;
  brief: string;
  status: RunStatus;
  progress: number;
  updated: string;
  agents: number;
  steps: Array<{
    label: string;
    detail: string;
    state: "done" | "active" | "waiting" | "error";
    owner: string;
  }>;
};

export const runs: Run[] = [
  {
    id: "RUN-1842",
    eyebrow: "Strategy · Retention",
    title: "Find the inflection point in Q2 retention",
    brief:
      "Synthesize product telemetry, interviews, and support themes into a board-ready retention brief.",
    status: "approval",
    progress: 68,
    updated: "2m",
    agents: 4,
    steps: [
      {
        label: "Frame the question",
        detail: "Cohort boundary and causal-confidence rules locked.",
        state: "done",
        owner: "Planner",
      },
      {
        label: "Collect evidence",
        detail: "18 sources normalized; one billing export requires approval.",
        state: "active",
        owner: "Research",
      },
      {
        label: "Test hypotheses",
        detail: "Waiting on final enterprise cohort.",
        state: "waiting",
        owner: "Analyst",
      },
      {
        label: "Draft the brief",
        detail: "Structure ready; synthesis begins after evidence lock.",
        state: "waiting",
        owner: "Writer",
      },
    ],
  },
  {
    id: "RUN-1839",
    eyebrow: "Research · Market",
    title: "Map procurement objections by segment",
    brief:
      "Compare seven win/loss themes and produce intervention recommendations for sales enablement.",
    status: "active",
    progress: 42,
    updated: "6m",
    agents: 3,
    steps: [
      {
        label: "Normalize interviews",
        detail: "32 transcripts labeled against the agreed taxonomy.",
        state: "done",
        owner: "Research",
      },
      {
        label: "Cluster objections",
        detail: "Separating policy objections from integration friction.",
        state: "active",
        owner: "Analyst",
      },
      {
        label: "Review evidence",
        detail: "Reviewer begins when cluster confidence exceeds 0.8.",
        state: "waiting",
        owner: "Review",
      },
    ],
  },
  {
    id: "RUN-1827",
    eyebrow: "Launch · Messaging",
    title: "Prepare the enterprise launch narrative",
    brief:
      "Convert approved positioning into launch copy, internal enablement, and an evidence-backed FAQ.",
    status: "complete",
    progress: 100,
    updated: "1h",
    agents: 5,
    steps: [
      {
        label: "Collect approved claims",
        detail: "All product and legal claims linked to evidence.",
        state: "done",
        owner: "Research",
      },
      {
        label: "Draft narrative",
        detail: "Launch story approved by product marketing.",
        state: "done",
        owner: "Writer",
      },
      {
        label: "Adversarial review",
        detail: "Unsupported superlatives removed; FAQ expanded.",
        state: "done",
        owner: "Review",
      },
    ],
  },
  {
    id: "RUN-1814",
    eyebrow: "Support · Quality",
    title: "Trace escalation failures in onboarding",
    brief:
      "Identify where high-intent customers fall out of the onboarding support path.",
    status: "failed",
    progress: 31,
    updated: "3h",
    agents: 2,
    steps: [
      {
        label: "Load support export",
        detail: "Schema validated and sensitive columns removed.",
        state: "done",
        owner: "Research",
      },
      {
        label: "Join onboarding events",
        detail: "Warehouse query expired before the final partition.",
        state: "error",
        owner: "Analyst",
      },
      {
        label: "Map escalation gaps",
        detail: "Blocked until the failed join is retried.",
        state: "waiting",
        owner: "Analyst",
      },
    ],
  },
];

export const activity = [
  {
    time: "10:42:18",
    owner: "Research",
    title: "Billing cohort export requested",
    detail: "Read-only query · 2,418 rows · contains account identifiers",
    tone: "attention",
  },
  {
    time: "10:41:03",
    owner: "Research",
    title: "Support themes normalized",
    detail: "8 themes across 146 conversations · 94% source coverage",
    tone: "success",
  },
  {
    time: "10:38:44",
    owner: "Analyst",
    title: "Early churn hypothesis weakened",
    detail: "Activation latency explains 11%, below the 20% threshold",
    tone: "neutral",
  },
  {
    time: "10:34:12",
    owner: "Planner",
    title: "Causal-confidence rule added",
    detail: "Claims require two independent evidence classes",
    tone: "neutral",
  },
];
