# Session Walkthrough

## 1. Workflow Modules v2.1 Update

15ワークフローの `modules:` をレガシー T/M-series から v2.1 ID に更新。

| Before | After | ワークフロー例 |
|--------|-------|---------------|
| M7 | A2 | /v, /chk |
| M8 | H4 | /bye, /hist |
| T3 | O3 | /why, /zet |

## 2. /v Workflow Enhancement

[v.md](file:///home/makaron8426/oikos/hegemonikon/.agent/workflows/v.md) を Executor-Auditor パターンで強化。

### 追加セクション

1. **RRP Gate** - 監査前に環境状態を検証（stale context 防止）
2. **Confidence Scoring** - 0.8未満で詳細検証トリガー
3. **v2.1 Module Refs** - M7→A2, M1→S1, M3→O3, M8→H4
4. **Evaluation Paranoia** - Gemini に評価印象を与えない注意書き
