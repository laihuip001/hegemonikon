# DX-012: Playwright Route Mock の安全パターン

> **確信度**: [確信: 95%] (SOURCE: 3回の失敗→修正サイクルで実証)
> **導出**: Sprint 6 F6 実装 (2026-02-15)

## 信念

Playwright の `page.route()` で API をモックするとき、**パターン選択とタイミング**が安定性を決定する。

## 学び (3段階の失敗)

| # | やったこと | 壊れた理由 | 修正 |
|:--|:---------|:----------|:-----|
| 1 | `**/api/**` でインターセプト | Vite dev server のモジュールパス (`/src/api/client.ts`) にもマッチ → JS ロード失敗 | バックエンド URL 限定 (`http://127.0.0.1:9696/**`) |
| 2 | グローバル `beforeEach` で全テストに mock | 30/30 テスト失敗。ページ初期化への副作用 | 必要なテストのみに mock を適用 |
| 3 | `setupApiMock` → `page.goto` の順序 | ページロード中に mock が干渉し、DOM が `Loading...` で停止 | `page.goto` → `setupApiMock` の順序に変更 |

## 安全パターン

```typescript
// ✅ 正解: goto → mock → 操作
test('example', async ({ page }) => {
    await page.goto('/');              // 1. ページロード完了
    await page.waitForTimeout(500);    // 2. JS 初期化待ち
    await setupApiMock(page);          // 3. API mock 設定
    await page.keyboard.press('...');  // 4. 操作開始
});
```

```typescript
// ❌ NG: mock → goto
test('example', async ({ page }) => {
    await setupApiMock(page);          // mock が JS ロードを妨害する可能性
    await page.goto('/');
});
```

## 原則

1. **パターンは最小スコープ**: `**/api/**` ではなく `http://exact-host:port/**`
2. **タイミングは goto 後**: ページの JS ロードが完了してからモック設定
3. **スコープは最小**: グローバル `beforeEach` ではなく、必要なテストのみ

## 圏論的意味

Route mock = テスト空間における射の書き換え。
書き換えのスコープを誤ると、共変・反変の関係が壊れ、全体の図式が可換でなくなる。
