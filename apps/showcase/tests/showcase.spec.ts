import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import path from "node:path";

const evidence = path.resolve(__dirname, "../../../docs/50-evals/evidence/T-007");

test("normal experience supports approval and interruption", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Find the inflection point in Q2 retention" })).toBeVisible();

  if (testInfo.project.name === "desktop") {
    await page.screenshot({ path: path.join(evidence, "desktop.jpg"), fullPage: true, type: "jpeg", quality: 90 });
  } else {
    await page.screenshot({ path: path.join(evidence, "mobile.jpg"), fullPage: true, type: "jpeg", quality: 90 });
  }

  await page.getByRole("button", { name: "Pause run" }).click();
  await expect(page.getByText("Run paused at a safe checkpoint. Completed evidence remains available.")).toBeVisible();
  await page.getByRole("button", { name: "Resume run" }).click();

  await page.getByRole("button", { name: "Approve read" }).click();
  await expect(page.getByText("Decision recorded")).toBeVisible();
  await expect(page.getByText("Read-only access approved")).toBeVisible();

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test("desktop captures loading, empty, and error states", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "State evidence is captured once on desktop.");
  await page.goto("/");

  await page.getByRole("button", { name: "loading" }).click();
  await expect(page.getByText("Reconstructing workspace state…")).toBeVisible();
  await page.screenshot({ path: path.join(evidence, "loading.jpg"), fullPage: true, type: "jpeg", quality: 90 });

  await page.goto("/");
  await page.getByRole("button", { name: "empty" }).click();
  await expect(page.getByRole("heading", { name: "The room is quiet." })).toBeVisible();
  await page.screenshot({ path: path.join(evidence, "empty.jpg"), fullPage: true, type: "jpeg", quality: 90 });

  await page.goto("/");
  await page.getByRole("button", { name: "error" }).click();
  await expect(page.getByRole("heading", { name: "One evidence stream went dark." })).toBeVisible();
  await page.screenshot({ path: path.join(evidence, "error.jpg"), fullPage: true, type: "jpeg", quality: 90 });
});
