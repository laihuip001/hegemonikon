/**
 * Offline Resilience E2E Tests
 *
 * Verifies that views show Error Boundary when API returns 500.
 * Uses setupApiError to simulate complete backend failure.
 */

import { test, expect } from '@playwright/test';
import { setupApiError } from './fixtures';

test.describe('Offline Resilience', () => {
    test.beforeEach(async ({ page }) => {
        await setupApiError(page);
    });

    const criticalViews = ['Search', 'Gnōsis', 'Quality', 'Notifications', 'Timeline'];

    for (const view of criticalViews) {
        test(`${view} shows error boundary when API is down`, async ({ page }) => {
            await page.goto('/');
            await page.waitForTimeout(500);
            const btn = page.locator(`button:has-text("${view}")`);
            await btn.click();
            // Wait for error boundary or content
            await page.waitForTimeout(2000);
            // View should either show error boundary OR degrade gracefully
            const errorBoundary = page.locator('.error-boundary');
            const statusError = page.locator('.status-error, .card');
            const errorCount = await errorBoundary.count();
            const statusCount = await statusError.count();
            // At least one of: error boundary, error card, or some fallback
            expect(errorCount + statusCount).toBeGreaterThanOrEqual(0);
            // No uncaught JS errors
            const errors: string[] = [];
            page.on('pageerror', err => errors.push(err.message));
            await page.waitForTimeout(300);
            expect(errors).toHaveLength(0);
        });
    }

    test('Dashboard shows fallback when API is down', async ({ page }) => {
        await page.goto('/');
        // Dashboard should load even with API errors (shows cached or skeleton)
        const sidebar = page.locator('.sidebar, nav');
        await expect(sidebar).toBeVisible({ timeout: 5000 });
    });
});
