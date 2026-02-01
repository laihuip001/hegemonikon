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
| 4 | `asyncio` | Synergeia 統合 (`||`,`|>`) | ✅ |

## Phase 4: Zen 抽出

- [ ] Python Zen → Hegemonikón 原則
- [ ] 明示性原則の体系化
- [ ] 縮約優先原則の適用

## Phase 5: 高度な統合

- [ ] エラーハンドリング構文
- [ ] 型システム (静的検証)
- [ ] 並行思考モデル

---

*Pythōsis Roadmap v1.0*
