import { test, expect } from '@playwright/test';

test.describe('Search View UX', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        // Navigate to Search view
        const searchBtn = page.locator('button:has-text("Search")');
        await searchBtn.click();
        await expect(searchBtn).toHaveClass(/active/);
    });

    test('search input has accessible label', async ({ page }) => {
        const input = page.locator('#symploke-search-input');
        await expect(input).toBeVisible();
        await expect(input).toHaveAttribute('aria-label', '検索キーワード');
    });

    test('search button has accessible label', async ({ page }) => {
        const btn = page.locator('#symploke-search-btn');
        await expect(btn).toBeVisible();
        await expect(btn).toHaveAttribute('aria-label', '検索実行');
    });

    test('source chips use aria-pressed', async ({ page }) => {
        const chips = page.locator('.search-source-chip');
        await expect(chips.first()).toBeVisible();
        const count = await chips.count();
        expect(count).toBeGreaterThan(0);

        // Check first chip
        const firstChip = chips.first();
        await expect(firstChip).toHaveAttribute('aria-pressed');
    });

    test('toggling source chip updates aria-pressed', async ({ page }) => {
        const chip = page.locator('.search-source-chip').first();

        // Initial state should be pressed (active by default)
        await expect(chip).toHaveAttribute('aria-pressed', 'true');

        // Click to toggle off
        await chip.click();
        await expect(chip).toHaveAttribute('aria-pressed', 'false');

        // Click to toggle on
        await chip.click();
        await expect(chip).toHaveAttribute('aria-pressed', 'true');
    });

    test('results container is live', async ({ page }) => {
        const results = page.locator('#symploke-search-results');
        await expect(results).toHaveAttribute('aria-live', 'polite');
    });
});
