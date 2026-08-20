import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("../app/portfolio-lab.tsx", import.meta.url), "utf8");
const css = readFileSync(new URL("../app/globals.css", import.meta.url), "utf8");

test("renders three materially named directions", () => {
  for (const id of ["editorial-signal", "kinetic-index", "quiet-material"]) {
    assert.match(component, new RegExp(id));
    assert.match(css, new RegExp(`data-direction=\\"${id}\\"`));
  }
});

test("keeps direction approval explicit", () => {
  assert.match(component, /\.\/agentic design approve/);
  assert.match(component, /aria-pressed/);
  assert.match(component, /Approve this direction/);
  assert.match(component, /data-approved/);
  assert.match(css, /var\(--eae-color-background-canvas\)/);
});

test("includes keyboard, responsive, and reduced-motion contracts", () => {
  assert.match(component, /skip-link/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /@media \(max-width: 680px\)/);
  assert.match(css, /prefers-reduced-motion: reduce/);
});
