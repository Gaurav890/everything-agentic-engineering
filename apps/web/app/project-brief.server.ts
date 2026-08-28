import {existsSync, lstatSync, readFileSync} from "node:fs";
import {resolve} from "node:path";

export type ProjectBrief = {
  name: string;
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
  composition: string;
  interaction: string;
  preview_path: string;
};

function readProjectFile(filename: string): unknown {
  const directory = resolve(process.cwd(), "../../.agentic");
  const file = resolve(directory, filename);
  if (lstatSync(directory).isSymbolicLink() || (existsSync(file) && lstatSync(file).isSymbolicLink())) {
    throw new Error("Project context must not follow symlinks.");
  }
  return existsSync(file) ? JSON.parse(readFileSync(file, "utf8")) : null;
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
    !["first_outcome", "design_preferences"].every(key => data[key] == null || typeof data[key] === "string") ||
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
    "name", "audience", "promise", "first_outcome", "design_preferences",
    "design_mode", "assistant", "status",
  ].map(key => [key, data[key]])) as ProjectBrief;
}

export function getProjectCandidates(): ProjectCandidate[] {
  const data = readProjectFile("design-directions.json") as {directions?: unknown[]} | null;
  if (!data || !Array.isArray(data.directions)) throw new Error("Invalid design catalog.");
  return data.directions.map(value => {
    const candidate = value as Record<string, unknown>;
    const keys = ["id", "name", "thesis", "composition", "interaction", "preview_path"];
    if (!candidate || !keys.every(key => typeof candidate[key] === "string") ||
      !/^\/(?:[a-zA-Z0-9_-]+\/)*[a-zA-Z0-9_-]+\/?$/.test(String(candidate.preview_path))) {
      throw new Error("A project candidate needs a safe local preview and its design rationale.");
    }
    return Object.fromEntries(keys.map(key => [key, candidate[key]])) as ProjectCandidate;
  });
}
