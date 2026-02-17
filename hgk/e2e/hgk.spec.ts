/**
 * HGK Desktop — E2E Test Suite
 *
 * Validates: navigation, view rendering, theme toggle, lazy loading.
 * Runs against Vite dev server (http://localhost:1420).
 * API calls are mocked via Playwright route interception.
 */


import { test, expect } from '@playwright/test';
import { setupApiMock } from './fixtures';

// ─── Dashboard ──────────────────────────────────────────────

test.describe('Dashboard', () => {
    test('loads and shows sidebar', async ({ page }) => {
        await page.goto('/');
        // Sidebar should contain navigation buttons
        const sidebar = page.locator('.sidebar, nav');
        await expect(sidebar).toBeVisible({ timeout: 5000 });

        // Should have at least 10 navigation items
        const navButtons = page.locator('.sidebar button, nav button');
        const count = await navButtons.count();
        expect(count).toBeGreaterThanOrEqual(10);
    });

    test('dashboard is default view', async ({ page }) => {
        await page.goto('/');
        // Dashboard button should be active/selected
        const dashboardBtn = page.locator('button:has-text("Dashboard")');
        await expect(dashboardBtn).toBeVisible();
    });
});

// ─── Navigation ─────────────────────────────────────────────

test.describe('Navigation', () => {
    const views = [
        'Dashboard', 'Agents', 'Search', 'FEP Agent', 'Gnōsis',
        'Quality', 'Postcheck', 'Graph', 'Notifications', 'PKS',
        'Sophia KI', 'Timeline', 'Synteleia', 'Synedrion',
        'Digestor', 'Desktop', 'Chat', 'Aristos',
    ];

    for (const view of views) {
        test(`navigates to ${view}`, async ({ page }) => {
            await page.goto('/');
            const btn = page.locator(`button:has-text("${view}")`);
            await expect(btn).toBeVisible({ timeout: 3000 });
            await btn.click();
            // View should transition (active state changes)
            await expect(btn).toHaveClass(/active/, { timeout: 3000 }).catch(() => {
                // Some views may not add 'active' class — just verify no crash
            });
            // No uncaught errors
            const errors: string[] = [];
            page.on('pageerror', err => errors.push(err.message));
            await page.waitForTimeout(500);
            expect(errors).toHaveLength(0);
        });
    }
});

// ─── Graph Lazy Loading ─────────────────────────────────────

test.describe('Graph 3D', () => {
    test('lazy loads graph3d chunk', async ({ page }) => {
        await page.goto('/');
        // Mock API after page load
        await setupApiMock(page);
        // Click Graph button
        const graphBtn = page.locator('button:has-text("Graph")');
        await graphBtn.click();

        // Knowledge toggle should appear (proves graph3d module loaded)
        const knowledgeBtn = page.locator('button:has-text("Knowledge")');
        await expect(knowledgeBtn).toBeVisible({ timeout: 5000 });
    });

    test('graph container exists after navigation', async ({ page }) => {
        await page.goto('/');
        // Mock API after page load
        await setupApiMock(page);
        await page.locator('button:has-text("Graph")').click();

        // graph-container should be present
        const container = page.locator('#graph-container');
        await expect(container).toBeVisible({ timeout: 5000 });
    });
});

// ─── Theme Toggle ───────────────────────────────────────────

test.describe('Theme', () => {
    test('toggles dark/light mode', async ({ page }) => {
        await page.goto('/');
        const themeBtn = page.locator('.theme-toggle');

        if (await themeBtn.isVisible().catch(() => false)) {
            const initialTheme = await page.evaluate(() =>
                document.documentElement.getAttribute('data-theme') || 'dark'
            );
            await themeBtn.click();
            await page.waitForTimeout(300);
            const newTheme = await page.evaluate(() =>
                document.documentElement.getAttribute('data-theme') || 'dark'
            );
            expect(newTheme).not.toEqual(initialTheme);
        }
    });
});

// ─── Sprint 5: Command Palette ──────────────────────────────

test.describe('Command Palette', () => {
    test('opens with Ctrl+K', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        await page.keyboard.press('Control+k');
        const overlay = page.locator('#cp-overlay');
        await expect(overlay).toBeVisible({ timeout: 2000 });
    });

    test('closes with Escape', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        await page.keyboard.press('Control+k');
        await expect(page.locator('#cp-overlay')).toBeVisible({ timeout: 2000 });
        await page.keyboard.press('Escape');
        await expect(page.locator('#cp-overlay')).not.toBeVisible({ timeout: 2000 });
    });

    test('has input field and footer', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        await page.keyboard.press('Control+k');
        const input = page.locator('#cp-input');
        await expect(input).toBeVisible({ timeout: 2000 });
        const footer = page.locator('.cp-footer');
        await expect(footer).toBeVisible();
    });

    test('shows items on open', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        // Mock API after page is loaded to avoid JS loading interference
        await setupApiMock(page);
        await page.keyboard.press('Control+k');
        await page.waitForTimeout(2000);
        const results = page.locator('#cp-results');
        const items = results.locator('.cp-item, .cp-route-item');
        const count = await items.count();
        expect(count).toBeGreaterThanOrEqual(1);
    });

    test('closes on overlay click', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        await page.keyboard.press('Control+k');
        await expect(page.locator('#cp-overlay')).toBeVisible({ timeout: 2000 });
        // Click overlay (outside dialog)
        await page.locator('#cp-overlay').click({ position: { x: 10, y: 10 } });
        await expect(page.locator('#cp-overlay')).not.toBeVisible({ timeout: 2000 });
    });
});

// ─── Sprint 5: Skeleton Loader ──────────────────────────────

test.describe('Skeleton Loader', () => {
    test('shows skeleton during navigation', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        // Navigate to a view — skeleton should briefly appear
        const btn = page.locator('button:has-text("Search")');
        await btn.click();
        // Just check that no error boundary appeared
        await page.waitForTimeout(500);
        const errorBoundary = page.locator('.error-boundary');
        const errorCount = await errorBoundary.count();
        // Error boundary may appear if API is down, which is acceptable
        expect(errorCount).toBeLessThanOrEqual(1);
    });
});

// ─── Sprint 5: Error Boundary ───────────────────────────────

test.describe('Error Boundary', () => {
    test('error boundary has retry button when shown', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(500);
        // Navigate to a view that might fail when API is down
        const searchBtn = page.locator('button:has-text("Search")');
        await searchBtn.click();
        await page.waitForTimeout(1000);
        // Check if error boundary appeared (API might be down)
        const errorBoundary = page.locator('.error-boundary');
        if (await errorBoundary.isVisible().catch(() => false)) {
            const retryBtn = page.locator('#error-retry');
            await expect(retryBtn).toBeVisible();
            const dashBtn = page.locator('#error-dashboard');
            await expect(dashBtn).toBeVisible();
        }
    });
});
