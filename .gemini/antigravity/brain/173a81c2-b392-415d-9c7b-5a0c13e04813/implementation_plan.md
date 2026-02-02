# W9: /vet + Jules 直接統合

> **Goal**: /vet 実行時に Jules 既存レビュー結果を自動参照

---

## 背景

| 現状 | 目標 |
|:-----|:-----|
| /vet は手動4層監査 | Jules 結果を L5 として統合 |
| Jules 結果は Git ブランチに分散 | /vet 実行時に自動収集 |
| 59+ ブランチ存在 | `docs/reviews/` に集約 |

---

## Proposed Changes

### [MODIFY] [vet.md](file:///home/makaron8426/oikos/.agent/workflows/vet.md)

1. **L5: Jules Prior Art（新規追加）**

   ```markdown
   ## L5: Jules Prior Art (Synedrion Integration)

   > **Origin**: W9 直接統合 (2026-01-28)

   専門家レビュー結果を事前に確認:

   1. `git fetch origin` 実行
   2. `git branch -a | grep jules-review` で関連ブランチ確認
   3. `docs/reviews/*_review.md` から最新結果を読み込み
   4. 既知の発見事項を監査ベースラインに追加

   出力: Jules 事前発見リスト（重複回避）
   ```

2. **監査プロセスに Step 0.5 追加**

   ```
   [Step 0.5] Jules Prior Art 取得
     - git fetch origin
     - docs/reviews/ から既存レビュー検索
     - 関連する発見事項を L1-L4 参照に追加
   ```

---

## Verification Plan

### Manual Verification

1. `/vet` 実行時に L5 が表示されることを確認
2. Jules ブランチからのレビュー結果読み込み動作確認

---

*Plan created: 2026-01-28 19:02 JST*
