import { test, expect } from '@playwright/test';

test.describe('Settings Accessibility', () => {
  test('settings view has accessible labels and roles', async ({ page }) => {
    // 1. Navigate to Settings
    await page.goto('/');

    // Click the System (Ω) group button
    const systemGroupBtn = page.locator('button[data-group="system"]');
    await expect(systemGroupBtn).toBeVisible();
    await systemGroupBtn.click();

    // Click the Settings route button (use tab-btn to be specific)
    const settingsBtn = page.locator('button.tab-btn[data-route="settings"]');
    await expect(settingsBtn).toBeVisible();
    await settingsBtn.click();

    // 2. Verify 'for' attributes on labels
    // Theme
    const themeLabel = page.locator('label:has-text("カラーモード")');
    await expect(themeLabel).toBeVisible();
    await expect(themeLabel).toHaveAttribute('for', 'set-theme');

    // Polling
    const pollingLabel = page.locator('label:has-text("Dashboard 更新間隔")');
    await expect(pollingLabel).toBeVisible();
    await expect(pollingLabel).toHaveAttribute('for', 'set-polling');

    // Notifications
    const notifLabel = page.locator('label:has-text("デフォルト表示")');
    await expect(notifLabel).toBeVisible();
    await expect(notifLabel).toHaveAttribute('for', 'set-notif');

    // API
    const apiLabel = page.locator('label:has-text("ベース URL")');
    await expect(apiLabel).toBeVisible();
    await expect(apiLabel).toHaveAttribute('for', 'set-api');

    // 3. Verify Toast accessibility roles
    const toast = page.locator('#set-toast');
    // Toast is hidden by default but present in DOM
    await expect(toast).toHaveAttribute('role', 'status');
    await expect(toast).toHaveAttribute('aria-live', 'polite');

    // 4. Verify Range input label
    const rangeInput = page.locator('#set-polling');
    await expect(rangeInput).toBeVisible();
    await expect(rangeInput).toHaveAttribute('aria-label', /Polling interval/);
  });
});
