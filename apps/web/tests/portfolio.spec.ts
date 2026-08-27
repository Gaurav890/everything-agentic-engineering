import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { previewExperiences } from "../app/experience-types";

const experience = JSON.parse(
  readFileSync(resolve(process.cwd(), "../../.agentic/experience.json"), "utf8"),
) as { archetype: string; promise: string; preview_all_archetypes?: boolean };

const enterprise = JSON.parse(
  readFileSync(resolve(process.cwd(), "../../.agentic/enterprise.json"), "utf8"),
) as { business_object: {singular: string}; approval_model: string };

const directions = [
  { id: "editorial-signal", name: "Editorial Signal" },
  { id: "kinetic-index", name: "Kinetic Index" },
  { id: "quiet-material", name: "Quiet Material" },
] as const;

const productArchetypes = experience.preview_all_archetypes
  ? (["product", "agentic-product", "enterprise-workflow"] as const)
  : experience.archetype === "portfolio"
    ? ([] as const)
    : ([experience.archetype] as const);

async function chooseDirection(page: Page, name: string, id: string) {
  const control = page.locator(".direction-option").filter({ hasText: name });
  if (!(await control.isVisible())) {
    await page.locator(".direction-trigger").click();
  }
  await control.click();
  await expect(control).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", id);
}

test("direction comparison stays explicit and keyboard reachable", async ({ page }) => {
  await page.goto("/");
  if (experience.archetype === "portfolio") {
    await expect(page.getByRole("heading", { name: "Designing systems people can feel." })).toBeVisible();
  } else {
    await expect(page.getByRole("heading", { name: experience.promise })).toBeVisible();
  }

  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", {
      name: experience.archetype === "portfolio" ? "Skip to selected work" : "Skip to product proof",
    }),
  ).toBeFocused();

  for (const direction of directions) {
    await chooseDirection(page, direction.name, direction.id);
    await expect(page.locator(".approval code")).toHaveText(
      `./agentic design approve ${direction.id} --yes`,
    );
  }
});

test("direction controls support Enter and Space selection", async ({ page }) => {
  await page.goto("/");

  const kinetic = page.locator(".direction-option").filter({ hasText: "Kinetic Index" });
  if (!(await kinetic.isVisible())) {
    await page.locator(".direction-trigger").click();
    await expect(page.locator(".direction-option").first()).toBeFocused();
  }
  await kinetic.focus();
  await expect(kinetic).toBeFocused();
  await kinetic.press("Enter");
  await expect(kinetic).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("main.experience")).toHaveAttribute("data-direction", "kinetic-index");

  const quiet = page.locator(".direction-option").filter({ hasText: "Quiet Material" });
  if (!(await quiet.isVisible())) {
    const trigger = page.locator(".direction-trigger");
    await expect(trigger).toBeFocused();
    await trigger.press("Enter");
    await expect(page.locator(".direction-option").first()).toBeFocused();
  }
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
  if (!(await page.getByRole("button", { name: "Copy approval command" }).isVisible())) {
    await page.locator(".direction-trigger").click();
  }
  await page.getByRole("button", { name: "Copy approval command" }).click();
  await expect(page.getByRole("button", { name: "Command copied" })).toBeVisible();
  await expect(page.locator(".copy-status")).toHaveText("Approval command copied to the clipboard.");
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
  if (!(await page.getByRole("button", { name: "Copy approval command" }).isVisible())) {
    await page.locator(".direction-trigger").click();
  }
  await page.getByRole("button", { name: "Copy approval command" }).click();
  await expect(page.getByRole("button", { name: "Copy failed — try again" })).toBeVisible();
  await expect(page.locator(".copy-status")).toHaveText(
    "The approval command could not be copied. Try again.",
  );
});

test("agent review gate exposes evidence, consequence, and recovery controls", async ({ page }) => {
  test.skip(
    experience.archetype !== "agentic-product" && !experience.preview_all_archetypes,
    "Only agentic products need the agent review gate.",
  );
  await page.goto("/?archetype=agentic-product");
  await page.getByRole("button", { name: "Review evidence" }).click();
  await expect(page.getByRole("heading", { name: "Evidence before consequence" })).toBeVisible();
  const approve = page.getByRole("button", { name: "Approve next step" });
  await expect(approve).toBeDisabled();
  await expect(page.getByText(/Failed or unavailable checks keep approval locked/)).toBeVisible();

  await page.getByRole("button", { name: "Verify final evidence" }).click();
  await expect(page.getByRole("button", { name: "Verifying final evidence…" })).toBeDisabled();
  await expect(page.getByText("Reviewed", { exact: true })).toBeVisible();
  await expect(approve).toBeEnabled();
  await approve.click();
  await expect(page.locator(".agent-control [role=status]")).toContainText("Candidate approved");

  await page.getByRole("button", { name: "Review again" }).click();
  await page.getByRole("button", { name: "Reject & revise" }).click();
  await expect(page.locator(".agent-control [role=status]")).toContainText("returned for revision");
});

test("direction lab is non-obscuring on desktop and collapsed on mobile", async ({ page }, testInfo) => {
  await page.goto(
    experience.preview_all_archetypes ? "/?archetype=agentic-product" : "/",
  );
  if (testInfo.project.name === "mobile") {
    const trigger = page.locator(".direction-trigger");
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(page.locator(".direction-option").first()).not.toBeVisible();
    const overlaps = await page.evaluate(() => {
      const triggerRect = document.querySelector(".direction-trigger")!.getBoundingClientRect();
      const titleRect = document.querySelector("#product-title")!.getBoundingClientRect();
      const intersects = (a: DOMRect, b: DOMRect) =>
        a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
      return intersects(triggerRect, titleRect);
    });
    expect(overlaps).toBe(false);
    await trigger.click();
    await expect(page.locator(".direction-option").first()).toBeFocused();
    await page.locator(".direction-option").nth(1).click();
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
    await expect(trigger).toBeFocused();
    await trigger.click();
    await expect(page.locator(".direction-option").first()).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(trigger).toBeFocused();
  } else {
    const geometry = await page.evaluate(() => {
      const dock = document.querySelector(".direction-dock")!.getBoundingClientRect();
      const shell = document.querySelector(".product-shell")!.getBoundingClientRect();
      return { dockBottom: dock.bottom, shellTop: shell.top };
    });
    expect(geometry.dockBottom).toBeLessThanOrEqual(geometry.shellTop + 1);
  }
});

test("every direction has no automatically detectable accessibility violations", async ({ page }) => {
  await page.goto("/");

  for (const direction of directions) {
    await chooseDirection(page, direction.name, direction.id);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations, `${direction.name} accessibility violations`).toEqual([]);
  }
});

test("product and agentic-product use their own experience architecture", async ({ page }) => {
  test.skip(!experience.preview_all_archetypes, "The reference lab owns cross-archetype coverage.");
  await page.goto("/?archetype=product");
  await expect(page.locator("main.experience")).toHaveAttribute("data-archetype", "product");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    experience.archetype === "product"
      ? experience.promise
      : "Turn competing signals into one decision everyone can act on.",
  );
  if (experience.archetype !== "product") {
    await expect(page.getByText("Northstar", { exact: true })).toBeVisible();
  }
  await expect(page.getByLabel("Product outcome preview")).toBeVisible();
  await expect(page.getByText("One shared truth")).toBeVisible();

  await page.goto("/?archetype=agentic-product");
  await expect(page.locator("main.experience")).toHaveAttribute(
    "data-archetype",
    "agentic-product",
  );
  await expect(page.getByLabel("Agent workflow demonstration")).toBeVisible();
  await expect(page.getByText("Candidate blocked until review", { exact: true })).toBeVisible();
  await expect(page.getByText("Nothing ships silently.")).toBeVisible();
});

test("enterprise workflow enforces evidence, role, tenant, consequence, and recovery", async ({ page }) => {
  test.skip(
    experience.archetype !== "enterprise-workflow" && !experience.preview_all_archetypes,
    "Only the enterprise workflow needs enterprise transition coverage.",
  );
  await page.goto("/?archetype=enterprise-workflow");
  await expect(page.locator("main.experience")).toHaveAttribute("data-archetype", "enterprise-workflow");
  await expect(page.getByRole("heading", {name: experience.archetype === "enterprise-workflow" ? experience.promise : previewExperiences["enterprise-workflow"].promise, exact: true})).toBeVisible();
  await expect(page.getByText("Request queue", {exact: true})).toBeVisible();

  await page.getByRole("button", {name: "Test failure"}).click();
  await expect(page.locator(".enterprise-state[role=alert]")).toContainText("No local decision was lost");
  await page.getByRole("button", {name: "Retry safely"}).click();
  await expect(page.getByText("Production analytics access")).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-auditor");
  await page.getByRole("button", {name: "Approve request"}).click();
  await expect(page.getByRole("status").filter({hasText: "not authorized"})).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-other-tenant");
  await expect(page.getByText("Production analytics access")).toHaveCount(0);
  await expect(page.getByText("No requests are exposed across the tenant boundary.")).toBeVisible();
  await expect(page.locator(".audit-section li")).toHaveCount(0);

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-reviewer");
  await page.getByLabel("Decision rationale").fill("The requested scope exceeds the reviewed need.");
  await page.getByRole("button", {name: "Reject"}).click();
  await expect(page.getByRole("status").filter({hasText: "Rejected recorded"})).toBeVisible();
  await expect(page.locator(".audit-section li strong").filter({hasText: /^rejected$/})).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-requester");
  await page.getByRole("button", {name: `New ${enterprise.business_object.singular}`, exact: true}).click();
  await page.getByRole("button", {name: "Create draft"}).click();
  await expect(page.getByText("Give reviewers a precise title.")).toBeVisible();
  await page.getByLabel("Request title").fill("Finance reporting access");
  await page.getByLabel("Requested scope").fill("Read-only for fourteen days");
  await page.getByLabel("Business justification").fill("Complete the approved close review.");
  await page.getByRole("button", {name: "Create draft"}).click();
  await expect(page.getByText("Draft created locally", {exact: false})).toBeVisible();
  await expect(page.getByRole("button", {name: "Submit for review"})).toBeDisabled();
  await page.getByRole("button", {name: "Run local evidence checks"}).click();
  await expect(page.getByText("Local evidence checks passed", {exact: false})).toBeVisible();
  await page.getByRole("button", {name: "Submit for review"}).click();
  await expect(page.getByRole("status").filter({hasText: "In review recorded"})).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-reviewer-backup");
  if (enterprise.approval_model === "single-review") {
    await expect(page.getByRole("button", {name: /Finance reporting access/})).toBeVisible();
  } else {
    await expect(page.getByText("Finance reporting access")).toHaveCount(0);
  }

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-reviewer");
  await page.getByRole("button", {name: /Finance reporting access/}).click();
  await page.getByLabel("Decision rationale").fill("Confirm the expiry owner before approval.");
  await page.getByRole("button", {name: "Request changes"}).click();
  await expect(page.getByRole("status").filter({hasText: "Changes requested recorded"})).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-requester");
  await page.getByRole("button", {name: /Finance reporting access/}).click();
  await page.getByRole("button", {name: "Run local evidence checks"}).click();
  await page.getByRole("button", {name: "Submit for review"}).click();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-reviewer");
  await page.getByRole("button", {name: /Finance reporting access/}).click();
  await page.getByRole("button", {name: "Approve request"}).click();
  await expect(page.getByRole("status").filter({hasText: "Approved recorded"})).toBeVisible();
  await expect(page.locator(".audit-section li strong").filter({hasText: /^approved$/})).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-requester");
  await page.getByRole("button", {name: /Vendor security exception/}).click();
  await page.getByRole("button", {name: "Cancel"}).click();
  await expect(page.getByRole("status").filter({hasText: "Cancelled recorded"})).toBeVisible();

  await page.getByRole("combobox", {name: "Filter requests"}).selectOption("empty");
  await expect(page.getByText("No requests match this view.")).toBeVisible();
  await page.getByRole("button", {name: "Show all requests"}).click();
  await expect(page.locator(".request-list strong").filter({hasText: "Finance reporting access"})).toBeVisible();
});

test("enterprise refresh cannot restore a previous actor or overwrite a new decision", async ({ page }) => {
  test.skip(
    experience.archetype !== "enterprise-workflow" && !experience.preview_all_archetypes,
    "Only the enterprise workflow needs refresh isolation coverage.",
  );
  await page.goto("/?archetype=enterprise-workflow");
  await expect(page.getByRole("combobox", {name: "Acting as"})).toBeVisible();
  await page.clock.install();
  await page.clock.pauseAt(new Date());

  await page.getByRole("button", {name: "Refresh", exact: true}).click();
  await expect(page.getByRole("button", {name: "Refreshing…"})).toBeDisabled();
  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-other-tenant");
  await page.clock.runFor(500);
  await expect(page.getByText("Production analytics access")).toHaveCount(0);
  await expect(page.locator(".audit-section li")).toHaveCount(0);
  await expect(page.getByText("No requests are exposed across the tenant boundary.")).toBeVisible();

  await page.getByRole("combobox", {name: "Acting as"}).selectOption("actor-requester");
  await page.getByRole("button", {name: "Refresh", exact: true}).click();
  await page.getByRole("button", {name: `New ${enterprise.business_object.singular}`, exact: true}).click();
  await page.clock.runFor(1);
  await page.getByLabel("Request title").fill("Refresh isolation request");
  await page.getByLabel("Requested scope").fill("Read only for one day");
  await page.getByLabel("Business justification").fill("Verify the approved refresh boundary.");
  await page.getByRole("button", {name: "Create draft"}).click();
  await page.clock.runFor(500);
  await expect(page.getByText("Draft created locally", {exact: false})).toBeVisible();

  await page.getByRole("button", {name: "Refresh", exact: true}).click();
  await page.getByRole("button", {name: "Run local evidence checks"}).click();
  await page.getByRole("button", {name: "Submit for review"}).click();
  await page.clock.runFor(500);
  await expect(page.getByRole("status").filter({hasText: "In review recorded"})).toBeVisible();
  await expect(page.getByRole("heading", {name: "Refresh isolation request"})).toBeVisible();
  await expect(page.locator(".audit-section li strong").filter({hasText: /^submitted$/})).toBeVisible();
});

test("product archetypes remain accessible through every direction", async ({ page }) => {
  for (const archetype of productArchetypes) {
    await page.goto(`/?archetype=${archetype}`);
    for (const direction of directions) {
      await chooseDirection(page, direction.name, direction.id);
      const results = await new AxeBuilder({ page }).analyze();
      expect(
        results.violations,
        `${archetype} / ${direction.name} accessibility violations`,
      ).toEqual([]);
    }
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


  for (const archetype of productArchetypes) {
    await page.goto(`/?archetype=${archetype}`);
    for (const direction of directions) {
      await chooseDirection(page, direction.name, direction.id);
      const geometry = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        content: document.documentElement.scrollWidth,
      }));
      expect(
        geometry.content,
        `${archetype} / ${direction.name} horizontal overflow`,
      ).toBeLessThanOrEqual(geometry.viewport);
    }
  }
});

test("selected product motion collapses under reduced motion", async ({ page }) => {
  test.skip(
    experience.archetype === "portfolio" && !experience.preview_all_archetypes,
    "A portfolio project uses the portfolio motion contract.",
  );
  await page.emulateMedia({ reducedMotion: "reduce" });
  const productArchetype = experience.preview_all_archetypes
    ? "agentic-product"
    : experience.archetype;
  await page.goto(`/?archetype=${productArchetype}`);
  const motion = await page.evaluate(() => {
    const elements = document.querySelectorAll<HTMLElement>(".stage-live i, .orbit-one");
    return Array.from(elements, (element) => getComputedStyle(element).animationDuration);
  });
  expect(motion.length).toBeGreaterThan(0);
  for (const duration of motion) {
    expect(duration).not.toBe("missing");
    expect(Number.parseFloat(duration)).toBeLessThanOrEqual(0.01);
  }
});

test("reduced motion collapses every decorative animation", async ({ page }) => {
  test.skip(
    experience.archetype !== "portfolio" && !experience.preview_all_archetypes,
    "A product project uses the selected-product motion contract.",
  );
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
