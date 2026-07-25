import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";

const source = readFileSync(new URL("../lib/data.ts", import.meta.url), "utf8");

test("showcase contains all required run states", () => {
  for (const state of ["active", "approval", "complete", "failed"]) {
    assert.match(source, new RegExp(`status: "${state}"`));
  }
});

test("agent steps include recovery and waiting states", () => {
  assert.match(source, /state: "error"/);
  assert.match(source, /state: "waiting"/);
});
