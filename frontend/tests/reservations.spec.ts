import { test, expect } from '@playwright/test';

test.describe('Reservation App', () => {
  test('displays seeded reservations for 2025-07-01 after selecting date', async ({ page }) => {
    // Step 1: Seed backend
    const res = await page.request.post('http://localhost:8000/api/test/seed');
    console.log(await res.text()); // For manual debug
    expect(res.ok()).toBeTruthy();

    // Step 2: Launch frontend
    await page.goto('/');

    // Step 3: Change date to 2025-07-01
    const dateInput = page.getByLabel('Select Date');
    await dateInput.fill('2025-07-01');
    await dateInput.dispatchEvent('change');

    // Step 4: Wait for header to confirm date change
    await expect(page.getByText('Reservations for 2025-07-01')).toBeVisible();

    // Step 5: Wait for the reservation grid to appear (adjust selector if needed)
    await page.waitForSelector('table');
    await page.waitForTimeout(100);

    // Step 6: Optional screenshot for visual debug
    await page.screenshot({ path: 'debug.png', fullPage: true });

    // Step 7: Confirm known reservation entries are visible
    await expect(page.getByText('G1-08:00')).toBeVisible();
    await expect(page.getByText('Alice')).toBeVisible();
    await expect(page.getByText('G2-09:00')).toBeVisible();
    await expect(page.getByText('Bob')).toBeVisible();
    await expect(page.getByText('G3-10:00')).toBeVisible();
    await expect(page.getByText('Charlie')).toBeVisible();
  });
});
