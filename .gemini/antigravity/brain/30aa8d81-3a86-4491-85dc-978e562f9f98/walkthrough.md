# /zet ワークフロー v2.3 完全再設計 — ウォークスルー

> 日時: 2026-01-28  
> 成果: `/zet` v2.3（ハイブリッド + Claude特化）

---

## 成果サマリー

| 項目 | Before (v2.2) | After (v2.3) |
|------|---------------|--------------|
| 行数 | 271行 | 331行 (+22%) |
| 構造 | 冒頭凝縮のみ | **ハイブリッド** |
| Claude対応 | なし | **専用セクション追加** |

---

## Phase 1: KI復元 ✅

Chronotopic Precision を `/zet` に統合:

- 2025後半優先（相対日付: 過去6ヶ月）
- 世代フィルタ（2024以前は参考）
- Cut-off明示

## Phase 2: 冒頭凝縮型 ✅

パプ君調査結果に基づく優先順位:

1. 出力フォーマット
2. タスク定義
3. 時間制約
4. スタイル

## Phase 3: ハイブリッド復元 + Claude特化 ✅

### 追加セクション

1. **調査対象の定義** — 用語揺れ防止
2. **調査すべき論点** — 網羅性担保（A/B/C構造）
3. **成果物構成** — 出力フォーマット固定
4. **調査ルール** — Chronotopic Precision + 一般ルール
5. **Claude処理最適化** — Lost in the Middle対策、XML+Markdown

### Claude 4.5 最適化の知見

| 知見 | 詳細 |
|------|------|
| Lost in the Middle | 中盤 -15〜20pp |
| 最適フォーマット | XML + Markdown |
| 段落 vs 箇条書き | 段落が1.5倍詳細 |
| Prompt Caching | 90%トークン削減 |

---

## 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| [zet.md](file:///home/makaron8426/oikos/.agent/workflows/zet.md) | v2.3 ハイブリッド + Claude特化 |
| [zet_redesign_summary.md](file:///home/makaron8426/oikos/.gemini/antigravity/knowledge/search_exploration_optimization/artifacts/workflows/zet_redesign_summary.md) | KI更新 |
| [metadata.json](file:///home/makaron8426/oikos/.gemini/antigravity/knowledge/search_exploration_optimization/metadata.json) | summary更新 |
