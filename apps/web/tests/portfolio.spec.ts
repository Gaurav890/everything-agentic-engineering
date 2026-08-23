import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const directions = [
  { id: "editorial-signal", name: "Editorial Signal" },
  { id: "kinetic-index", name: "Kinetic Index" },
  { id: "quiet-material", name: "Quiet Material" },
] as const;

async function chooseDirection(page: Page, name: string, id: string) {
  const control = page.getByRole("button", { name: new RegExp(name) });
  await control.click();
  await expect(control).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", id);
}

test("direction comparison stays explicit and keyboard reachable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Designing systems people can feel." })).toBeVisible();

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to selected work" })).toBeFocused();

  for (const direction of directions) {
    await chooseDirection(page, direction.name, direction.id);
    await expect(page.locator(".approval code")).toHaveText(
      `./agentic design approve ${direction.id} --yes`,
    );
  }
});

test("direction controls support Enter and Space selection", async ({ page }) => {
  await page.goto("/");

  const kinetic = page.getByRole("button", { name: /Kinetic Index/ });
  await kinetic.focus();
  await expect(kinetic).toBeFocused();
  await kinetic.press("Enter");
  await expect(kinetic).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", "kinetic-index");

  const quiet = page.getByRole("button", { name: /Quiet Material/ });
  await quiet.focus();
  await expect(quiet).toBeFocused();
  await quiet.press("Space");
  await expect(quiet).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", "quiet-material");
});

test("approval command exposes clipboard success and failure states", async ({ page }) => {
  await page.goto("/");
  await chooseDirection(page, "Kinetic Index", "kinetic-index");

  await page.evaluate(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async (value: string) => sessionStorage.setItem("approval-command", value),
      },
    });
  });
  await page.getByRole("button", { name: "Copy approval command" }).click();
  await expect(page.getByRole("button", { name: "Command copied" })).toBeVisible();
  await expect(page.getByRole("status")).toHaveText("Approval command copied to the clipboard.");
  await expect.poll(() => page.evaluate(() => sessionStorage.getItem("approval-command"))).toBe(
    "./agentic design approve kinetic-index --yes",
  );

  await chooseDirection(page, "Quiet Material", "quiet-material");
  await page.evaluate(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: async () => Promise.reject(new Error("Clipboard unavailable")) },
    });
  });
  await page.getByRole("button", { name: "Copy approval command" }).click();
  await expect(page.getByRole("button", { name: "Copy failed — try again" })).toBeVisible();
  await expect(page.getByRole("status")).toHaveText(
    "The approval command could not be copied. Try again.",
  );
});

test("every direction has no automatically detectable accessibility violations", async ({ page }) => {
  await page.goto("/");

  for (const direction of directions) {
    await chooseDirection(page, direction.name, direction.id);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations, `${direction.name} accessibility violations`).toEqual([]);
  }
});

test("mobile composition does not overflow horizontally", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "mobile", "The overflow contract is mobile-specific.");
  await page.goto("/");

  for (const direction of directions) {
    await chooseDirection(page, direction.name, direction.id);
    const geometry = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      content: document.documentElement.scrollWidth,
    }));
    expect(geometry.content, `${direction.name} horizontal overflow`).toBeLessThanOrEqual(
      geometry.viewport,
    );
  }
});

test("reduced motion collapses every decorative animation", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await expect.poll(() => page.evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches)).toBe(true);

  for (const direction of directions) {
    await chooseDirection(page, direction.name, direction.id);
    const motion = await page.evaluate(() =>
      Array.from(
        document.querySelectorAll<HTMLElement>(
          ".availability i, .artifact-one, .artifact-three, .gesture",
        ),
      ).map((element) => {
        const style = getComputedStyle(element);
        const durations = style.animationDuration.split(",").map((duration) =>
          duration.trim().endsWith("ms")
            ? Number.parseFloat(duration)
            : Number.parseFloat(duration) * 1000,
        );
        return {
          selector: element.className || element.tagName,
          names: style.animationName,
          durations,
          iterations: style.animationIterationCount.split(",").map((value) => value.trim()),
        };
      }),
    );

    expect(motion.length, `${direction.name} animated elements`).toBeGreaterThan(0);
    for (const item of motion) {
      for (const duration of item.durations) {
        expect(duration, `${direction.name} ${item.selector} duration`).toBeLessThanOrEqual(0.01);
      }
      expect(item.iterations, `${direction.name} ${item.selector} iterations`).toEqual(["1"]);
    }
  }
});
