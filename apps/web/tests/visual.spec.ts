import { expect, test, type Page } from "@playwright/test";

const directions = [
  { id: "editorial-signal", name: "Editorial Signal" },
  { id: "kinetic-index", name: "Kinetic Index" },
  { id: "quiet-material", name: "Quiet Material" },
] as const;

async function prepareDirection(page: Page, name: string, id: string) {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const control = page.getByRole("button", { name: new RegExp(name) });
  await control.click();
  await expect(control).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", id);
  await page.evaluate(() => document.fonts.ready);
}

for (const direction of directions) {
  test(`${direction.name} matches the approved visual baseline`, async ({ page }) => {
    await prepareDirection(page, direction.name, direction.id);
    await expect(page).toHaveScreenshot(`portfolio-${direction.id}.png`, {
      fullPage: true,
    });
  });
}
