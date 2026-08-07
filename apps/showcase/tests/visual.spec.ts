import { expect, test, type Page } from "@playwright/test";

type Scenario = "normal" | "loading" | "empty" | "error";

const scenarios: Scenario[] = ["normal", "loading", "empty", "error"];

async function selectScenario(page: Page, scenario: Scenario) {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");

  if (scenario === "normal") {
    await expect(
      page.getByRole("heading", { name: "Find the inflection point in Q2 retention" }),
    ).toBeVisible();
    return;
  }

  const scenarioButton = page
    .locator(".scenarioControl button")
    .filter({ hasText: scenario });

  await scenarioButton.evaluate((button: HTMLButtonElement) => button.click());

  const expectedCopy = {
    loading: "Reconstructing workspace state…",
    empty: "The room is quiet.",
    error: "One evidence stream went dark.",
  }[scenario];

  await expect(page.getByText(expectedCopy, { exact: true })).toBeVisible();
}

for (const scenario of scenarios) {
  test(`${scenario} state matches the approved visual baseline`, async ({ page }) => {
    await selectScenario(page, scenario);

    await expect(page).toHaveScreenshot(`signalroom-${scenario}.png`, {
      fullPage: true,
    });
  });
}
