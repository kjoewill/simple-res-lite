import { test, expect } from '@playwright/test';

test.describe('Admin Page - Glider Management', () => {
  test.beforeEach(async ({ request }) => {
    const res = await request.post('http://localhost:8000/api/test/seed');
    expect(res.ok()).toBeTruthy();
  });

  test('can add and delete a glider', async ({ page }) => {
    await page.goto('/admin');

    // Confirm seeded gliders show up
    await expect(page.getByText('G1')).toBeVisible();
    await expect(page.getByText('G2')).toBeVisible();

    // Add a new glider
    const testGlider = 'Z-TestGlider';
    await page.getByPlaceholder('New glider name').fill(testGlider);
    await page.getByRole('button', { name: 'Add Glider' }).click();
    await expect(page.getByText(testGlider)).toBeVisible();

    // Delete the glider
    await page.getByRole('button', { name: 'Delete', exact: false }).locator(`xpath=..`).getByText(testGlider).click({ timeout: 2000 });

    // Confirm it's gone
    await expect(page.getByText(testGlider)).not.toBeVisible();
  });
});
