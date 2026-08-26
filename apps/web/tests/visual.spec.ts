import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const experience = JSON.parse(
  readFileSync(resolve(process.cwd(), "../../.agentic/experience.json"), "utf8"),
) as { archetype: "portfolio" | "product" | "agentic-product"; preview_all_archetypes?: boolean };

const directions = [
  { id: "editorial-signal", name: "Editorial Signal" },
  { id: "kinetic-index", name: "Kinetic Index" },
  { id: "quiet-material", name: "Quiet Material" },
] as const;

const archetypes = experience.preview_all_archetypes
  ? (["portfolio", "product", "agentic-product"] as const)
  : ([experience.archetype] as const);

async function prepareDirection(page: Page, archetype: string, name: string, id: string) {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(`/?archetype=${archetype}`);
  const control = page.locator(".direction-option").filter({ hasText: name });
  if (!(await control.isVisible())) {
    await page.locator(".direction-trigger").click();
  }
  await control.click();
  await expect(control).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", id);
  await page.evaluate(() => document.fonts.ready);
}

for (const archetype of archetypes) {
  for (const direction of directions) {
    test(`${archetype} / ${direction.name} matches the visual baseline`, async ({ page }) => {
      await prepareDirection(page, archetype, direction.name, direction.id);
      await expect(page).toHaveScreenshot(`${archetype}-${direction.id}.png`, {
        fullPage: true,
      });
    });
  }
}
