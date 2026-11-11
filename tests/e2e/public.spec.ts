import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { randomUUID } from "node:crypto";
test("React server rendering retains content, metadata and document security", async ({ request }) => {
  const response = await request.get('/');
  expect(response.status()).toBe(200);
  const html = await response.text();
  expect(html).toContain('Gagandeep');
  expect(html).toContain('Weather App');
  expect(html).toContain('rel="canonical"');
  expect(html).toContain('application/ld+json');
  expect(html).not.toContain('/_next/');
  const headers = response.headers();
  const nonce = headers['content-security-policy'].match(/'nonce-([^']+)'/)?.[1];
  expect(nonce).toBeTruthy();
  expect(html).toContain(`nonce="${nonce}"`);
  expect(headers['cache-control']).toBe('no-store');
  expect(headers['x-frame-options']).toBe('DENY');
  const preview = await request.get('/admin/preview/frame');
  expect(preview.headers()['x-frame-options']).toBe('SAMEORIGIN');
  expect(preview.headers()['x-robots-tag']).toContain('noindex');
  const missing = await request.get('/unwritten-chapter');
  expect(missing.status()).toBe(404);
});

test("published portfolio exposes supported projects and hides private phone", async ({
  page,
  request,
}) => {
  const site = await request.get("/api/v1/site");
  expect(site.ok()).toBeTruthy();
  const data = await site.json();
  expect(data.content.profile.full_name).toBe("Gagandeep Kaur");
  expect(data.content.profile.phone_e164).toBeUndefined();
  expect(data.content.profile.resume_asset_id).toBeUndefined();
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Gagandeep Kaur/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "GK portrait placeholder. Portrait coming soon." }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Weather App", exact: true })
    .first()
    .click();
  await expect(page).toHaveURL(/\/projects\/weather-app$/);
  await expect(
    page.getByRole("link", { name: /Visit live project/ }),
  ).toHaveAttribute("href", "https://gagandeepkaurrr.github.io/weatherApp/");
  await expect(
    page.getByRole("heading", { name: "What I built" }),
  ).toBeVisible();
  await page.goto("/projects/previous-portfolio");
  await expect(
    page.getByRole("link", { name: /Visit previous portfolio/ }),
  ).toHaveAttribute("href", "https://portfolio-gagandeep.vercel.app/");
});
test("contact form validates and saves a real message", async ({ page }) => {
  await page.goto("/#contact");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByText("Please enter your name.")).toBeVisible();
  await page
    .getByLabel("Name", { exact: false })
    .fill("Portfolio browser verification");
  await page
    .getByLabel("Email", { exact: false })
    .fill("browser-test@example.com");
  await page
    .getByLabel("Message", { exact: false })
    .fill(
      `Local acceptance check ${randomUUID()}. This message can be deleted.`,
    );
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Message received." }),
  ).toBeVisible();
});
test("contact retry preserves receipt and rejects changed payload", async ({
  request,
}) => {
  const origin = process.env.E2E_ORIGIN || "http://localhost:3000";
  const headers = { Origin: origin, "Idempotency-Key": randomUUID() };
  const data = {
    name: "Retry verification",
    email: "retry@example.com",
    message: "A local verification of receipt deduplication.",
  };
  const first = await request.post("/api/v1/contact", { data, headers });
  expect(first.status()).toBe(201);
  const second = await request.post("/api/v1/contact", { data, headers });
  expect(second.status()).toBe(200);
  expect(await second.json()).toEqual(await first.json());
  expect(
    (
      await request.post("/api/v1/contact", {
        data: { ...data, message: "Different request with the same identity." },
        headers,
      })
    ).status(),
  ).toBe(409);
});
test("private routes and unknown projects are protected", async ({
  page,
  request,
}) => {
  for (const path of [
    "/admin/draft",
    "/admin/preview",
    "/admin/releases",
    "/admin/contact",
  ])
    expect((await request.get(`/api/v1${path}`)).status()).toBe(401);
  const response = await page.goto("/projects/does-not-exist");
  expect(response?.status()).toBe(404);
  await expect(
    page.getByRole("heading", { name: /This chapter/ }),
  ).toBeVisible();
  await page.goto("/admin");
  await expect(page.getByLabel("Password", { exact: true })).toBeVisible();
});
for (const width of [320, 360, 768, 1440])
  test(`home fits ${width}px and remains accessible`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBeTruthy();
    if (width === 360) {
      await page.getByRole("button", { name: /Menu/ }).click();
      await expect(
        page.getByRole("navigation", { name: "Main navigation" }),
      ).toBeVisible();
      await page.keyboard.press("Escape");
      await expect(page.getByRole("button", { name: /Menu/ })).toBeFocused();
    }
    if (width === 1440) {
      const a11y = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze();
      expect(a11y.violations).toEqual([]);
    }
    await page.screenshot({
      path: `docs/screenshots/home-${width}.png`,
      fullPage: true,
    });
  });
test("privacy, résumé and sitemap are usable", async ({ page, request }) => {
  await page.goto("/privacy");
  await expect(
    page.getByRole("heading", { name: "Privacy, in plain language." }),
  ).toBeVisible();
  const site = await (await request.get("/api/v1/site")).json();
  if (site.content.profile.resume_available) {
    const pdf = await request.get("/api/v1/resume");
    expect(pdf.status()).toBe(200);
    expect(pdf.headers()["content-type"]).toContain("application/pdf");
    expect((await pdf.body()).subarray(0, 5).toString()).toBe("%PDF-");
  }
  const map = await request.get("/sitemap.xml");
  expect(map.status()).toBe(200);
  const xml = await map.text();
  expect(xml).toContain("/projects/weather-app");
  expect(xml).not.toContain("/admin");
});
