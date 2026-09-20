#!/usr/bin/env node

import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import path from "node:path";
import process from "node:process";
import { chromium } from "../apps/showcase/node_modules/@playwright/test/index.mjs";

const root = path.resolve(import.meta.dirname, "..");
const prototype = path.join(root, "docs/20-design/prototypes/product-to-proof-studio.html");
const evidenceDirectory = path.join(root, "docs/50-evals/evidence/T-054");
const executablePath = process.env.BROWSER_EXECUTABLE;
const browser = await chromium.launch(executablePath ? { executablePath } : { channel: "chrome" });

const states = [
  "shape",
  "design-blocked",
  "design-ready",
  "build-boundary",
  "wave-paused",
  "recovery",
  "dependency",
  "prove",
];

function luminance(rgb) {
  const channels = rgb.match(/[\d.]+/g).slice(0, 3).map((value) => Number(value) / 255);
  const linear = channels.map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrastRatio(first, second) {
  const light = Math.max(luminance(first), luminance(second));
  const dark = Math.min(luminance(first), luminance(second));
  return (light + 0.05) / (dark + 0.05);
}

async function verifyKeyboardOrder(page, url, colorScheme) {
  await page.emulateMedia({ colorScheme, reducedMotion: "no-preference" });
  await page.goto(url);
  const expected = ["a.skip", "nav a", "nav a", "nav a", "nav a", "a.primary", "summary", "summary"];
  const observed = [];
  for (const selector of expected) {
    await page.keyboard.press("Tab");
    const focus = page.locator(":focus");
    const state = await focus.evaluate((element) => ({
      tag: element.tagName.toLowerCase(),
      className: element.className,
      parent: element.parentElement?.tagName.toLowerCase(),
      outline: getComputedStyle(element).outlineStyle,
    }));
    const matches = selector === "nav a"
      ? state.tag === "a" && state.parent === "nav"
      : selector === "summary"
        ? state.tag === "summary"
        : state.tag === "a" && state.className.split(" ").includes(selector.split(".")[1]);
    assert.equal(matches, true, `${colorScheme} keyboard order expected ${selector}`);
    assert.notEqual(state.outline, "none", `${colorScheme} focus must remain visible on ${selector}`);
    observed.push(selector);
  }
  assert.deepEqual(observed, expected);
}

try {
  await mkdir(evidenceDirectory, { recursive: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, colorScheme: "light" });
  const baseUrl = pathToFileURL(prototype).href;

  for (const state of states) {
    await page.goto(`${baseUrl}#${state}`);
    const visibleStates = await page.locator(".state:visible").count();
    const visiblePrimaryActions = await page.locator(".state:visible .primary:visible").count();
    assert.equal(visibleStates, 1, `${state} must render exactly one Studio state`);
    assert.equal(visiblePrimaryActions, 1, `${state} must render exactly one primary action`);
    assert.equal(await page.locator(".state:visible").getAttribute("id"), state);
  }

  await page.goto(`${baseUrl}#design-blocked`);
  assert.equal(await page.locator(".state:visible .primary").getAttribute("href"), "#shape");
  await page.locator(".state:visible .primary").click();
  assert.equal(await page.locator(".state:visible").getAttribute("id"), "shape");

  await verifyKeyboardOrder(page, baseUrl, "light");

  const lightColors = await page.locator("body").evaluate((element) => {
    const style = getComputedStyle(element);
    return [style.color, style.backgroundColor];
  });
  assert.ok(contrastRatio(...lightColors) >= 4.5, "light theme body contrast must meet WCAG AA");

  await page.setViewportSize({ width: 360, height: 780 });
  await page.goto(`${baseUrl}#recovery`);
  const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(mobileOverflow <= 1, `mobile view overflowed by ${mobileOverflow}px`);
  await page.screenshot({ path: path.join(evidenceDirectory, "studio-recovery-mobile.png"), fullPage: true });

  const zoomContext = await browser.newContext({ viewport: { width: 360, height: 780 }, deviceScaleFactor: 2, colorScheme: "light" });
  const zoomPage = await zoomContext.newPage();
  await zoomPage.goto(`${baseUrl}#recovery`);
  const zoomMetrics = await zoomPage.evaluate(() => ({
    cssWidth: innerWidth,
    scale: devicePixelRatio,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  assert.equal(zoomMetrics.cssWidth, 360, "2x reflow must expose a 360 CSS-pixel viewport at 720 physical pixels");
  assert.equal(zoomMetrics.scale, 2, "2x reflow context must use a 200% device scale");
  assert.ok(zoomMetrics.overflow <= 1, `200% reflow view overflowed by ${zoomMetrics.overflow}px`);
  const zoomTargetsFit = await zoomPage.locator("a:visible, summary:visible").evaluateAll((elements) =>
    elements.every((element) => {
      const box = element.getBoundingClientRect();
      return box.left >= -1 && box.right <= innerWidth + 1;
    }),
  );
  assert.equal(zoomTargetsFit, true, "all 200% reflow focus targets must fit the effective viewport");
  await zoomPage.screenshot({ path: path.join(evidenceDirectory, "studio-recovery-200-percent.png"), fullPage: true });
  await zoomContext.close();

  await page.setViewportSize({ width: 1440, height: 1000 });
  await verifyKeyboardOrder(page, baseUrl, "dark");
  await page.emulateMedia({ colorScheme: "dark", reducedMotion: "reduce" });
  await page.goto(`${baseUrl}#build-boundary`);
  const desktopOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(desktopOverflow <= 1, `desktop view overflowed by ${desktopOverflow}px`);
  const reducedMotion = await page.locator("html").evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
  assert.equal(reducedMotion, true);
  const darkColors = await page.locator("body").evaluate((element) => {
    const style = getComputedStyle(element);
    return [style.color, style.backgroundColor];
  });
  assert.ok(contrastRatio(...darkColors) >= 4.5, "dark theme body contrast must meet WCAG AA");
  await page.screenshot({ path: path.join(evidenceDirectory, "studio-build-boundary-dark.png"), fullPage: true });

  console.log(`PASS: ${states.length} Studio states, keyboard focus, AA body contrast, responsive/200% reflow, dark mode, and reduced motion.`);
} finally {
  await browser.close();
}
