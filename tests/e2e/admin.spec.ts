import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { randomUUID } from 'node:crypto';

async function signIn(page: import('@playwright/test').Page) {
  const email = process.env.E2E_OWNER_EMAIL;
  const password = process.env.E2E_OWNER_PASSWORD;
  if (!email || !password) throw new Error('Owner acceptance tests require the isolated make e2e runner with E2E_OWNER_EMAIL and E2E_OWNER_PASSWORD.');
  await page.goto('/admin/login');
  await page.getByLabel('Email address', { exact: true }).fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Welcome back, Gagandeep.' })).toBeVisible();
}
const origin = () => process.env.E2E_ORIGIN || 'http://localhost:3000';
async function saveDraft(page: import('@playwright/test').Page) {
  await Promise.all([page.waitForResponse(response => response.url().endsWith('/api/v1/admin/draft') && response.request().method() === 'PUT' && response.status() === 200), page.getByRole('button', { name: 'Save draft', exact: true }).click()]);
  await expect(page.getByRole('button', { name: 'Save draft', exact: true })).toBeDisabled();
}

test('owner saves a private draft, previews mobile, publishes and restores history', async ({ page }) => {
  await signIn(page);
  const original = await (await page.request.get('/api/v1/site')).json();
  const marker = `An unpublished introduction ${randomUUID()}.`;
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  await page.getByRole('textbox', { name: 'Introduction', exact: true }).fill(marker);
  await page.getByRole('link', { name: 'Projects', exact: true }).click();
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  await expect(page.getByRole('textbox', { name: 'Introduction', exact: true })).toHaveValue(marker);
  await saveDraft(page);
  const saved = await (await page.request.get('/api/v1/site')).json();
  expect(saved.content.profile.intro).toBe(original.content.profile.intro);
  await page.getByRole('link', { name: 'Preview', exact: true }).click();
  await expect(page.frameLocator('iframe').getByText(marker, { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Mobile', exact: true }).click();
  await expect(page.locator('.admin-preview-canvas')).toHaveCSS('width', '375px');
  await expect(page.frameLocator('iframe').getByText(marker, { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Publish', exact: true }).click();
  await expect(page.getByRole('dialog')).toContainText('profile');
  await page.getByRole('button', { name: 'Publish saved draft', exact: true }).click();
  await expect(page.getByText(/Release \d+ was published\./)).toBeVisible();
  const published = await (await page.request.get('/api/v1/site')).json();
  expect(published.content.profile.intro).toBe(marker);
  await page.getByRole('link', { name: 'History', exact: true }).click();
  const oldRelease = page.locator('.admin-history-list article').filter({ has: page.getByRole('heading', { name: `Release ${original.release.revision}`, exact: true }) });
  await oldRelease.getByRole('button', { name: 'Restore to draft', exact: true }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Restore to draft', exact: true }).click();
  await expect(page.getByText(/restored to draft revision/)).toBeVisible();
  expect((await (await page.request.get('/api/v1/site')).json()).content.profile.intro).toBe(marker);
  await page.getByRole('button', { name: 'Publish', exact: true }).click();
  await page.getByRole('button', { name: 'Publish saved draft', exact: true }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  expect((await (await page.request.get('/api/v1/site')).json()).content.profile.intro).toBe(original.content.profile.intro);
});

test('stale editor keeps local text and explicitly reloads the server draft', async ({ page }) => {
  await signIn(page);
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  const localText = `Local edit to keep ${randomUUID()}.`;
  await page.getByRole('textbox', { name: 'Introduction', exact: true }).fill(localText);
  const session = await (await page.request.get('/api/v1/admin/auth/session')).json();
  const draft = await (await page.request.get('/api/v1/admin/draft')).json();
  const serverText = `A saved change from another tab ${randomUUID()}.`;
  const body = structuredClone(draft.content); body.profile.intro = serverText;
  const result = await page.request.put('/api/v1/admin/draft', { data: body, headers: { Origin: origin(), 'X-CSRF-Token': session.csrf_token, 'If-Match': `"draft-${draft.revision}"` } });
  expect(result.status()).toBe(200);
  await page.getByRole('button', { name: 'Save draft', exact: true }).click();
  await expect(page.getByText('This draft changed on the server.')).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Introduction', exact: true })).toHaveValue(localText);
  await page.getByRole('button', { name: 'Reload latest draft', exact: true }).click();
  await page.getByRole('button', { name: 'Discard local edits and reload', exact: true }).click();
  await expect(page.getByRole('textbox', { name: 'Introduction', exact: true })).toHaveValue(serverText);
  await page.getByRole('textbox', { name: 'Introduction', exact: true }).fill(draft.content.profile.intro);
  await saveDraft(page);
});

test('owner reads, archives, restores and deletes a persisted contact message', async ({ page, request }) => {
  const subject = `Owner inbox acceptance ${randomUUID()}`;
  const received = await request.post('/api/v1/contact', { data: { name: 'Local acceptance visitor', email: 'inbox-check@example.com', subject, message: 'A plain-text contact message used by isolated acceptance tests.' }, headers: { Origin: origin(), 'Idempotency-Key': randomUUID() } });
  expect(received.status()).toBe(201);
  await signIn(page);
  await page.getByRole('link', { name: 'Inbox', exact: true }).click();
  await page.getByRole('link').filter({ hasText: subject }).click();
  await expect(page.getByRole('heading', { name: subject, exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Reply in email app ↗' })).toHaveAttribute('href', /^mailto:/);
  await page.getByRole('button', { name: 'Archive', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Restore to inbox', exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('button', { name: 'Restore to inbox', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Restore to inbox', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Archive', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Delete message', exact: true }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Delete message', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Your inbox', exact: true })).toBeVisible();
  await expect(page.getByRole('link').filter({ hasText: subject })).toHaveCount(0);
});

test('owner uploads and crops a portrait draft; admin fits mobile and has accessible controls', async ({ page }) => {
  await signIn(page);
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  const accessibility = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(accessibility.violations).toEqual([]);
  await page.locator('fieldset').filter({ has: page.locator('legend', { hasText: /^Portrait$/ }) }).getByRole('button', { name: 'Choose image', exact: true }).click();
  const png = await page.evaluate(async () => { const canvas = document.createElement('canvas'); canvas.width = 600; canvas.height = 400; const context = canvas.getContext('2d')!; context.fillStyle = '#e4ebe4'; context.fillRect(0, 0, 600, 400); context.fillStyle = '#153e3b'; context.fillRect(100, 100, 200, 300); return canvas.toDataURL('image/png').split(',')[1]; });
  await page.getByRole('dialog').locator('input[type=file]').setInputFiles({ name: 'acceptance-portrait.png', mimeType: 'image/png', buffer: Buffer.from(png, 'base64') });
  await expect(page.getByRole('heading', { name: 'Frame your portrait' })).toBeVisible();
  await page.getByLabel('Horizontal focus (%)', { exact: true }).focus();
  await page.keyboard.press('ArrowRight');
  await page.getByRole('button', { name: 'Apply portrait crop', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Frame your portrait' })).toHaveCount(0);
  await page.getByRole('textbox', { name: 'Alternative text', exact: true }).fill('Geometric artwork used for the isolated upload test.');
  await saveDraft(page);
  const draft = await (await page.request.get('/api/v1/admin/draft')).json();
  expect(draft.content.profile.portrait.alt).toBe('Geometric artwork used for the isolated upload test.');
  const library = await (await page.request.get('/api/v1/admin/media?kind=image&limit=30')).json();
  const derived = library.items.find((asset: { id: string }) => asset.id === draft.content.profile.portrait.asset_id);
  expect(derived.parent_asset_id).toBeTruthy();
  expect(derived.source_width / derived.source_height).toBe(0.8);
  const publicMedia = await page.request.get(`/api/v1/media/${draft.content.profile.portrait.asset_id}/card`);
  expect(publicMedia.status()).toBe(404);
  await page.setViewportSize({ width: 320, height: 900 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.getByRole('button', { name: 'Open studio navigation', exact: true }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button', { name: 'Open studio navigation', exact: true })).toBeFocused();
  await page.screenshot({ path: 'docs/screenshots/admin-profile-320.png', fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({ path: 'docs/screenshots/admin-profile-1440.png', fullPage: true });
  await page.getByRole('button', { name: 'Remove from draft', exact: true }).click();
  await saveDraft(page);
});
