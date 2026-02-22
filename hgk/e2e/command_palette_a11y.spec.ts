import { test, expect } from '@playwright/test';
import { setupApiMock } from './fixtures';

test.describe('Command Palette A11y & UX', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await setupApiMock(page);
    });

    test('has correct ARIA roles', async ({ page }) => {
        await page.keyboard.press('Control+k');
        const dialog = page.locator('.cp-dialog');
        await expect(dialog).toHaveAttribute('role', 'dialog');
        await expect(dialog).toHaveAttribute('aria-modal', 'true');

        const input = page.locator('#cp-input');
        await expect(input).toHaveAttribute('role', 'combobox');
        await expect(input).toHaveAttribute('aria-expanded', 'true');
        await expect(input).toHaveAttribute('aria-controls', 'cp-results');

        const results = page.locator('#cp-results');
        await expect(results).toHaveAttribute('role', 'listbox');
    });

    test('manages focus and active descendant correctly', async ({ page }) => {
        await page.keyboard.press('Control+k');
        const input = page.locator('#cp-input');

        // Wait for results to populate
        const results = page.locator('#cp-results');
        await expect(results.locator('.cp-item').first()).toBeVisible();

        // Check initial state
        const activeItems = results.locator('.cp-item-active');
        // Verify only one item is active
        await expect(activeItems).toHaveCount(1);

        const firstItem = results.locator('.cp-item').first();
        await expect(firstItem).toHaveClass(/cp-item-active/);
        await expect(firstItem).toHaveAttribute('aria-selected', 'true');

        const firstItemId = await firstItem.getAttribute('id');
        await expect(input).toHaveAttribute('aria-activedescendant', firstItemId!);

        // Navigate down
        await page.keyboard.press('ArrowDown');
        const secondItem = results.locator('.cp-item').nth(1);

        await expect(secondItem).toHaveClass(/cp-item-active/);
        await expect(secondItem).toHaveAttribute('aria-selected', 'true');
        await expect(firstItem).not.toHaveClass(/cp-item-active/);
        await expect(firstItem).not.toHaveAttribute('aria-selected', 'true');

        const secondItemId = await secondItem.getAttribute('id');
        await expect(input).toHaveAttribute('aria-activedescendant', secondItemId!);
    });

    test('items have unique IDs', async ({ page }) => {
        await page.keyboard.press('Control+k');
        const results = page.locator('#cp-results');
        // Wait for at least one item
        await expect(results.locator('.cp-item').first()).toBeVisible();

        const items = page.locator('.cp-item');
        const count = await items.count();
        expect(count).toBeGreaterThan(0);

        const ids = new Set();
        for (let i = 0; i < count; i++) {
            const id = await items.nth(i).getAttribute('id');
            expect(id).not.toBeNull();
            expect(id).toMatch(/^cp-(wf|route|qa)-\d+$/);
            expect(ids.has(id)).toBeFalsy();
            ids.add(id);
        }
    });
});
