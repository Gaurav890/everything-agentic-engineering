import {existsSync, lstatSync, readFileSync} from "node:fs";
import {execFileSync} from "node:child_process";
import {resolve} from "node:path";

export type ProjectBrief = {
  name: string;
  idea: string | null;
  audience: string;
  promise: string;
  first_outcome: string | null;
  design_preferences: string | null;
  design_mode: "custom" | "existing-brand" | "reference";
  assistant: "choose" | "claude" | "codex" | "manual";
  status: "captured" | "ready";
};

export type ProjectCandidate = {
  id: string;
  name: string;
  thesis: string;
  axis: string;
  composition: string;
  interaction: string;
  signature: string;
  asset_strategy: string;
  motion_rationale: string;
  responsive_strategy: string;
  reduced_motion: string;
  states: string[];
  preview_path: string;
};

export type ProjectDesignStatus = "needs_approval" | "approved";

export type ProjectStudioStage = {
  id: "product" | "direction" | "build" | "proof";
  label: "Shape" | "Direction" | "Build" | "Proof";
  status: "complete" | "active" | "waiting";
};

export type ProjectStudioContext = {
  client: "choose" | "claude" | "codex" | "manual";
  prompt: string;
  research_enabled: boolean;
  mutation_performed: false;
  studio: {
    stages: ProjectStudioStage[];
    next: {title: string; action: string};
  };
};

function projectRoot(): string {
  return resolve(process.cwd(), "../..");
}

function readProjectFile(filename: string): unknown {
  const directory = resolve(projectRoot(), ".agentic");
  const file = resolve(directory, filename);
  if (lstatSync(directory).isSymbolicLink() || (existsSync(file) && lstatSync(file).isSymbolicLink())) {
    throw new Error("Project context must not follow symlinks.");
  }
  return existsSync(file) ? JSON.parse(readFileSync(file, "utf8")) : null;
}

export function getProjectStudioContext(): ProjectStudioContext {
  const root = projectRoot();
  const script = resolve(root, "scripts/project_handoff.py");
  if (!existsSync(script) || lstatSync(script).isSymbolicLink()) {
    throw new Error("The Project Studio handoff is missing or unsafe.");
  }
  let parsed: unknown;
  try {
    const output = execFileSync("python3", [script, "--json"], {
      cwd: root,
      encoding: "utf8",
      timeout: 5_000,
      maxBuffer: 512 * 1024,
      stdio: ["ignore", "pipe", "pipe"],
    });
    parsed = JSON.parse(output);
  } catch {
    throw new Error("The Project Studio could not read the current journey. Run ./agentic start in the terminal for guidance.");
  }
  const data = parsed as Record<string, unknown>;
  const studio = data?.studio as Record<string, unknown> | undefined;
  const stages = studio?.stages;
  const next = studio?.next as Record<string, unknown> | undefined;
  const expected = [
    ["product", "Shape"],
    ["direction", "Direction"],
    ["build", "Build"],
    ["proof", "Proof"],
  ];
  if (
    data?.mutation_performed !== false ||
    typeof data?.prompt !== "string" || !data.prompt.trim() || data.prompt.length > 100_000 ||
    typeof data?.research_enabled !== "boolean" ||
    !["choose", "claude", "codex", "manual"].includes(String(data?.client)) ||
    !Array.isArray(stages) || stages.length !== expected.length ||
    !stages.every((value, index) => {
      const stage = value as Record<string, unknown>;
      return stage.id === expected[index][0] && stage.label === expected[index][1] &&
        ["complete", "active", "waiting"].includes(String(stage.status));
    }) ||
    typeof next?.title !== "string" || !next.title.trim() ||
    typeof next?.action !== "string" || !next.action.trim()
  ) {
    throw new Error("The Project Studio journey is invalid. Run ./agentic start in the terminal for guidance.");
  }
  return data as ProjectStudioContext;
}

export function getProjectBrief(): ProjectBrief | null {
  const data = readProjectFile("project-brief.json") as Record<string, unknown> | null;
  if (!data) {
    const generated = readProjectFile("generated-project.json") as {onboarding_version?: number} | null;
    if (generated?.onboarding_version === 1) throw new Error("Missing project brief. Restore .agentic/project-brief.json before continuing.");
    return null;
  }
  if (
    data.schema_version !== 1 ||
    !["name", "audience", "promise"].every(key => typeof data[key] === "string" && String(data[key]).trim()) ||
    !["idea", "first_outcome", "design_preferences"].every(key => data[key] == null || typeof data[key] === "string") ||
    !["design_mode", "assistant", "status"].every(key => typeof data[key] === "string") ||
    !["custom", "existing-brand", "reference"].includes(String(data.design_mode)) ||
    !["choose", "claude", "codex", "manual"].includes(String(data.assistant)) ||
    !["captured", "ready"].includes(String(data.status)) ||
    !Array.isArray(data.open_questions) ||
    !data.open_questions.every(question => typeof question === "string" && question.trim()) ||
    (data.status === "ready" && !["first_outcome", "confirmed_by"].every(key => typeof data[key] === "string" && String(data[key]).trim()))
  ) throw new Error("The project brief is invalid. Run ./agentic start for guidance.");
  // Only public product intent goes to the page, not client paths or credentials.
  return Object.fromEntries([
    "name", "idea", "audience", "promise", "first_outcome", "design_preferences",
    "design_mode", "assistant", "status",
  ].map(key => [key, data[key]])) as ProjectBrief;
}

export function getProjectCandidates(): ProjectCandidate[] {
  const data = readProjectFile("design-directions.json") as {directions?: unknown[]} | null;
  if (!data || !Array.isArray(data.directions)) throw new Error("Invalid design catalog.");
  return data.directions.map(value => {
    const candidate = value as Record<string, unknown>;
    const keys = [
      "id", "name", "thesis", "axis", "composition", "interaction", "signature",
      "asset_strategy", "motion_rationale", "responsive_strategy", "reduced_motion", "preview_path",
    ];
    if (!candidate || !keys.every(key => typeof candidate[key] === "string") ||
      !Array.isArray(candidate.states) || candidate.states.length < 3 ||
      !candidate.states.every(state => typeof state === "string" && state.trim()) ||
      !/^\/(?:[a-zA-Z0-9_-]+\/)*[a-zA-Z0-9_-]+\/?$/.test(String(candidate.preview_path))) {
      throw new Error("A project candidate needs a safe local preview and its design rationale.");
    }
    return {...Object.fromEntries(keys.map(key => [key, candidate[key]])), states: candidate.states} as ProjectCandidate;
  });
}

export function getProjectDesignStatus(): ProjectDesignStatus {
  const data = readProjectFile("design.json") as Record<string, unknown> | null;
  if (!data || !["needs_approval", "approved"].includes(String(data.status))) {
    throw new Error("The project design state is invalid. Run ./agentic design check.");
  }
  return data.status as ProjectDesignStatus;
}
