# Pythōsis ロードマップ

> **CCL**: `/hod.backcast`

---

## Phase 1: 基盤構築 ✅

- [x] builtins → WF 分類 (wf_classification.md)
- [x] stdlib → マクロ (@chain, @cycle, @repeat, @reduce, @partial)

## Phase 2: Lambda 導入 ✅

- [x] Lambda 記法決定 → `L:[x]{WF}` (ccl/operators.md v6.52)
- [x] @partial 活用例の拡充
- [ ] Lambda 構文の実験検証

## Phase 3: 人気ライブラリ消化 ✅

> **設計文書**: [popular_libs.md](designs/popular_libs.md)

| # | ライブラリ | 消化形態 | 状態 |
|:-:|:-----------|:---------|:----:|
| 1 | `typing` | `/epi.typed` 派生 | ✅ |
| 2 | `dataclasses` | `/dox.structured` 派生 | ✅ |
| 3 | `contextlib` | `@scoped` v2 | ✅ |
| 4 | `asyncio` | Synergeia 統合 | ✅ |

## Phase 4: Zen 抽出 ✅

> **設計文書**: [zen_extraction.md](designs/zen_extraction.md)

- [x] Python Zen → Hegemonikón 原則 (17 格言マッピング)
- [x] 明示性原則の体系化 (原則 2)
- [x] 縮約優先原則の適用 (原則 3)

## Phase 5: 高度な統合 — 達成確認 (2026-02-10)

- [x] 並行思考モデル → `||`, `|>`, Synergeia で消化済み 🟢
- [x] 型システム (動的) → `/epi.typed`, `?T` で消化済み 🟢
- [x] エラーハンドリング (本質) → `@scoped(suppress:)`, Hermēneus fallback で消化済み 🟡

### 意図的スコープ外 🚫

- 🚫 `try/except` CCL 構文 — 模倣になる。本質は消化済み
- 🚫 静的型検証 — CCL は LLM 解釈言語。静的検証は不適合

---

*Pythōsis Roadmap v1.0*
