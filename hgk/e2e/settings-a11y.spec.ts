import { test, expect } from '@playwright/test';

test.describe('Settings Accessibility', () => {
    test('renders with proper ARIA attributes and labels', async ({ page }) => {
        await page.goto('/');

        // 1. Navigate to Settings
        // Click the System group icon (Ω) in the rail
        const systemGroupBtn = page.locator('.rail-btn[data-group="system"]');
        await expect(systemGroupBtn).toBeVisible();
        await systemGroupBtn.click();

        // Click the Settings tab
        const settingsTab = page.locator('button:has-text("Settings")');
        await expect(settingsTab).toBeVisible();
        await settingsTab.click();

        // 2. Verify Accessibility Improvements

        // Label associations
        await expect(page.locator('label[for="set-theme"]')).toBeVisible();
        await expect(page.locator('label[for="set-theme"]')).toHaveText('カラーモード');

        await expect(page.locator('label[for="set-polling"]')).toBeVisible();
        await expect(page.locator('label[for="set-polling"]')).toHaveText('Dashboard 更新間隔');

        await expect(page.locator('label[for="set-notif"]')).toBeVisible();
        await expect(page.locator('label[for="set-notif"]')).toHaveText('デフォルト表示');

        await expect(page.locator('label[for="set-api"]')).toBeVisible();
        await expect(page.locator('label[for="set-api"]')).toHaveText('ベース URL');

        // Input attributes
        const pollingInput = page.locator('input#set-polling');
        await expect(pollingInput).toHaveAttribute('aria-label', 'Polling interval');

        // Toast notification attributes
        const toast = page.locator('#set-toast');
        await expect(toast).toHaveAttribute('role', 'status');
        await expect(toast).toHaveAttribute('aria-live', 'polite');
    });
});
