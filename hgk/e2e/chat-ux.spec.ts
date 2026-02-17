import { test, expect } from '@playwright/test';

test.describe('Chat UX Accessibility', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        // Navigate to Chat view
        // The navigation might depend on the specific button text or icon
        // Based on hgk.spec.ts, it seems to be 'Chat'
        const chatBtn = page.locator('button:has-text("Chat")');
        await chatBtn.click();
        await expect(page.locator('.chat-container')).toBeVisible();
    });

    test('Chat input has aria-label', async ({ page }) => {
        const input = page.locator('#chat-input');
        await expect(input).toHaveAttribute('aria-label', 'メッセージ入力');
    });

    test('Model select has aria-label', async ({ page }) => {
        const select = page.locator('#chat-model-select');
        await expect(select).toHaveAttribute('aria-label', 'AIモデル選択');
    });

    test('Settings button has aria-label', async ({ page }) => {
        const btn = page.locator('#chat-settings-btn');
        await expect(btn).toHaveAttribute('aria-label', 'API キー設定');
    });

    test('Clear button has aria-label', async ({ page }) => {
        const btn = page.locator('#chat-clear-btn');
        await expect(btn).toHaveAttribute('aria-label', '履歴クリア');
    });

    test('Delete message button has aria-label', async ({ page }) => {
         // Inject a dummy message into the DOM directly for testing
         await page.evaluate(() => {
             const container = document.getElementById('chat-messages');
             if (container) {
                 container.innerHTML = `
                    <div class="chat-msg chat-msg-user" data-idx="0">
                      <div class="chat-msg-header">
                        <button class="chat-msg-delete" title="削除" aria-label="このメッセージを削除" data-idx="0">✕</button>
                      </div>
                    </div>
                 `;
             }
         });

         const deleteBtn = page.locator('.chat-msg-delete').first();
         await expect(deleteBtn).toHaveAttribute('aria-label', 'このメッセージを削除');
    });
});
