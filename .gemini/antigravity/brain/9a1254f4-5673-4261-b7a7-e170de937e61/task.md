# Task: タスク自動分類機構（I2）の設計と実装

> **起点**: wishlist_organized.md の I2
> **目標**: タスク・TODO・アイデアを投げたら自動的に優先順位・緊急度を分類する機構

## 📋 チェックリスト

### Phase 1: 設計 (PLANNING)

- [ ] 既存関連実装の調査
  - [ ] S2 Krisis（判断）スキルの確認
  - [ ] `/pri` ワークフローの確認
  - [ ] Eisenhower マトリクス実装状況
- [ ] 要件定義
  - [ ] 入力形式（自然言語 / 構造化）
  - [ ] 出力形式（Eisenhower / 独自分類）
  - [ ] 自動化トリガー（ワークフロー / MCP）
- [ ] implementation_plan.md 作成
- [ ] Creator 承認

### Phase 2: 実装 (EXECUTION)

- [ ] S2 Krisis スキルの拡張（必要に応じて）
- [ ] タスク分類パイプライン実装
- [ ] ワークフロー `/classify` or `/pri` 強化

### Phase 3: 検証 (VERIFICATION)

- [ ] 今日の wishlist でドッグフーディング
- [ ] walkthrough.md 作成
