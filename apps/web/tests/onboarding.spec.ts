import AxeBuilder from "@axe-core/playwright";
import {expect, test} from "@playwright/test";
import {getProjectBrief, getProjectCandidates} from "../app/project-brief.server";

const brief = getProjectBrief();
test.skip(!brief || brief.design_mode === "reference", "Generated custom/existing-brand workspace only");

test("shows the saved project and one executable continuation", async ({page}) => {
  await page.goto("/");
  await expect(page).toHaveTitle(`${brief!.name} — Project workspace`);
  await expect(page.getByRole("heading", {level: 1})).toContainText(brief!.name);
  await expect(page.locator("aside")).toContainText(brief!.promise);
  await expect(page.locator("aside")).toContainText(brief!.audience);
  await expect(page.getByText("./agentic start", {exact: true})).toBeVisible();
  await expect(page.getByText("No product-specific previews yet.")).toHaveCount(getProjectCandidates().length ? 0 : 1);
  await expect(page.getByRole("button", {name: "Editorial Signal"})).toHaveCount(0);
  await expect(page.getByText("No API key is collected here", {exact: false})).toBeVisible();
});

test("copy succeeds or explains the manual fallback without launching anything", async ({page}) => {
  await page.goto("/");
  await page.evaluate(() => Object.defineProperty(navigator, "clipboard", {configurable: true, value: {writeText: async (value: string) => sessionStorage.setItem("copied", value)}}));
  await page.getByRole("button", {name: "Copy command", exact: true}).click();
  expect(await page.evaluate(() => sessionStorage.getItem("copied"))).toBe("./agentic start");
  await expect(page.getByRole("status").first()).toContainText("Copied");
  if (!(await page.locator("details").getAttribute("open")) && !(await page.locator("pre").isVisible())) {
    await page.getByText("Already using an app or editor?").click();
  }
  await page.evaluate(() => Object.defineProperty(navigator, "clipboard", {configurable: true, value: {writeText: async () => { throw new Error("unavailable"); }}}));
  await page.getByRole("button", {name: "Copy instruction"}).click();
  await expect(page.getByRole("status").last()).toContainText("Select and copy");
  await expect(page.locator("pre")).toContainText("project-onboarding");
});

test("copy shows a pending state and prevents duplicate actions", async ({page}, testInfo) => {
  await page.goto("/");
  await page.evaluate(() => Object.defineProperty(navigator, "clipboard", {configurable: true, value: {writeText: () => new Promise<void>(() => {})}}));
  await page.getByRole("button", {name: "Copy command", exact: true}).click();
  await expect(page.getByRole("button", {name: "Copying…", exact: true})).toBeDisabled();
  await expect(page.getByRole("status").first()).toHaveText("Copying…");
  await page.screenshot({path: testInfo.outputPath("copy-pending.png")});
});

test("workspace supports keyboard, narrow screens, and automated accessibility", async ({page}, testInfo) => {
  await page.emulateMedia({reducedMotion: "reduce"});
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", {name: "Skip to your project"})).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("main")).toBeFocused();
  await page.keyboard.press("Tab");
  const primary = page.getByRole("link", {name: "Continue from your brief"});
  await expect(primary).toBeFocused();
  await expect(primary).toHaveCSS("outline-width", "3px");
  await expect.poll(() => primary.evaluate(node => getComputedStyle(node).outlineColor !== getComputedStyle(node).color)).toBe(true);
  await page.screenshot({path: testInfo.outputPath("keyboard-focus.png")});
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  const results = await new AxeBuilder({page}).analyze();
  expect(results.violations).toEqual([]);
});

test("every registered candidate links to a real local preview", async ({page}) => {
  await page.goto("/");
  for (const candidate of getProjectCandidates()) {
    // Read href directly to keep the assertion valid for arbitrary project-owned routes.
    await expect(page.locator(`a[href="${candidate.preview_path}"]`)).toBeVisible();
    const response = await page.request.get(candidate.preview_path);
    expect(response.ok()).toBe(true);
  }
});
