import assert from "node:assert/strict";
import {mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, symlinkSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import test from "node:test";
import ts from "typescript";

const source = readFileSync(new URL("../app/project-brief.server.ts", import.meta.url), "utf8");
const {outputText} = ts.transpileModule(source, {compilerOptions: {module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022}});
const {getProjectBrief, getProjectCandidates} = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`);
const captured = {schema_version: 1, name: "Sample", audience: "Readers", promise: "Read clearly.", first_outcome: null, design_preferences: null, assistant: "manual", design_mode: "custom", status: "captured", open_questions: []};

function fixture(run) {
  const root = mkdtempSync(join(tmpdir(), "project-brief-test-"));
  const cwd = process.cwd();
  mkdirSync(join(root, ".agentic"));
  mkdirSync(join(root, "apps/web"), {recursive: true});
  const write = (name, data) => writeFileSync(join(root, ".agentic", name), JSON.stringify(data));
  try {
    process.chdir(join(root, "apps/web"));
    run(write, root);
  } finally {
    process.chdir(cwd);
    rmSync(root, {recursive: true, force: true});
  }
}

test("public brief contains only product fields", () => fixture(write => {
  write("project-brief.json", {...captured, private_notes: "excluded", client_path: "/not-public"});
  assert.equal(getProjectBrief().name, "Sample");
  assert.equal("private_notes" in getProjectBrief(), false);
  assert.equal("client_path" in getProjectBrief(), false);
}));

test("ready requires human confirmation and a meaningful outcome", () => fixture(write => {
  for (const patch of [{status: "ready"}, {status: "ready", confirmed_by: "Reviewer", first_outcome: " "}, {assistant: ["manual"]}, {design_mode: ["custom"]}, {open_questions: null}]) {
    write("project-brief.json", {...captured, ...patch});
    assert.throws(getProjectBrief, /invalid/);
  }
  write("project-brief.json", {...captured, status: "ready", confirmed_by: "Reviewer", first_outcome: "Read a draft"});
  assert.equal(getProjectBrief().status, "ready");
}));

test("missing current brief and symlinked context fail closed", () => fixture((write, root) => {
  assert.equal(getProjectBrief(), null);
  write("generated-project.json", {onboarding_version: 1});
  assert.throws(getProjectBrief, /Missing project brief/);
  symlinkSync(join(root, ".agentic/generated-project.json"), join(root, ".agentic/project-brief.json"));
  assert.throws(getProjectBrief, /symlinks/);
}));

test("candidate views accept local previews without exposing sources", () => fixture(write => {
  const candidate = {id: "one", name: "One", thesis: "Content first", composition: "Reading", interaction: "Compare", preview_path: "/concepts/one", source_files: ["private-path"]};
  write("design-directions.json", {directions: []});
  assert.deepEqual(getProjectCandidates(), []);
  write("design-directions.json", {directions: [candidate]});
  assert.equal("source_files" in getProjectCandidates()[0], false);
  for (const preview_path of ["https://example.com", "//example.com", "/../secret", "javascript:alert(1)"]) {
    write("design-directions.json", {directions: [{...candidate, preview_path}]});
    assert.throws(getProjectCandidates, /safe local preview/);
  }
}));
