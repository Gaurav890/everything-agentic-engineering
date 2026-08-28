import {readFileSync, writeFileSync} from "node:fs";
import {resolve} from "node:path";
import {expect, test} from "@playwright/test";

test.skip(process.env.ONBOARDING_TEST_PROJECT !== "1", "Disposable onboarding fixture only");
test.describe.configure({mode: "serial"});

test("empty custom catalog explains how to create a direction", async ({page}, testInfo) => {
  const path = resolve(process.cwd(), "../../.agentic/design-directions.json");
  const original = readFileSync(path, "utf8");
  try {
    writeFileSync(path, JSON.stringify({...JSON.parse(original), directions: []}));
    await page.goto("/");
    const empty = page.getByRole("heading", {name: "No product-specific previews yet."});
    await expect(empty).toBeVisible();
    await empty.scrollIntoViewIfNeeded();
    await page.screenshot({path: testInfo.outputPath("empty-catalog.png")});
  } finally {
    writeFileSync(path, original);
  }
});

test("custom preview changes its explanation when the timing changes", async ({page}) => {
  await page.goto("/");
  await page.getByRole("link", {name: "Open working preview"}).click();
  await expect(page.getByRole("radio", {name: "Later", exact: true})).toBeChecked();
  await page.getByRole("radio", {name: "Sooner", exact: true}).check();
  await expect(page.getByRole("status")).toContainText("flexibility you would give up");
});

test("invalid brief recovers after repair without losing answers", async ({page}, testInfo) => {
  const path = resolve(process.cwd(), "../../.agentic/project-brief.json");
  const original = readFileSync(path, "utf8");
  const name = JSON.parse(original).name;
  try {
    writeFileSync(path, "{invalid");
    await page.goto("/");
    await expect(page.getByRole("heading", {name: "Let’s get back on track."})).toBeVisible();
    await page.screenshot({path: testInfo.outputPath("context-recovery.png")});
    writeFileSync(path, original);
    await page.getByRole("button", {name: "Reload after fixing"}).click();
    await expect(page.getByRole("heading", {level: 1})).toContainText(name);
    await expect(page.locator("aside")).toContainText(JSON.parse(original).promise);
  } finally {
    writeFileSync(path, original);
  }
});
