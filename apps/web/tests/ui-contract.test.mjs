import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";

const component = readFileSync(new URL("../app/portfolio-lab.tsx", import.meta.url), "utf8");
const productComponent = readFileSync(new URL("../app/product-lab.tsx", import.meta.url), "utf8");
const page = readFileSync(new URL("../app/page.tsx", import.meta.url), "utf8");
const css = readFileSync(new URL("../app/globals.css", import.meta.url), "utf8");

test("renders three materially named directions", () => {
  for (const id of ["editorial-signal", "kinetic-index", "quiet-material"]) {
    assert.match(component, new RegExp(id));
    assert.match(css, new RegExp(`data-direction=\\"${id}\\"`));
  }
});

test("routes product and agentic-product to archetype-appropriate compositions", () => {
  assert.match(page, /archetype !== "portfolio"/);
  assert.match(productComponent, /Product outcome preview/);
  assert.match(productComponent, /Agent workflow demonstration/);
  assert.match(productComponent, /Candidate blocked until review/);
  assert.match(productComponent, /Approve next step/);
  assert.match(productComponent, /Reject &amp; revise/);
  assert.match(productComponent, /Cancel run/);
  assert.match(productComponent, /Nothing ships silently/);
  assert.match(productComponent, /data-archetype/);
});

test("keeps direction approval explicit", () => {
  assert.match(component, /\.\/agentic design approve/);
  assert.match(component, /aria-pressed/);
  assert.match(component, /Copy approval command/);
  assert.match(component, /Command copied/);
  assert.match(component, /Copy failed/);
  assert.match(component, /data-approved/);
  assert.match(productComponent, /\.\/agentic design approve/);
  assert.match(productComponent, /aria-pressed/);
  assert.match(css, /var\(--eae-color-background-canvas\)/);
});

test("includes keyboard, responsive, and reduced-motion contracts", () => {
  assert.match(component, /skip-link/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /@media \(max-width: 680px\)/);
  assert.match(css, /prefers-reduced-motion: reduce/);
});
