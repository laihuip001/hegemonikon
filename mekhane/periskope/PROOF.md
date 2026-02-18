# Periskopē PROOF.md

> **存在証明**: 全コンポーネントの動作確認

## ファイル構成

```
mekhane/periskope/
├── __init__.py           # パッケージ定義
├── models.py             # データモデル (SearchResult, Citation, etc.)
├── engine.py             # オーケストレーター (4Phase パイプライン)
├── synthesizer.py        # 多モデル合成 (Cortex/Gemini)
├── citation_agent.py     # 引用検証 + BC-6 TAINT 自動分類
├── cli.py                # コマンドライン IF
├── searchers/
│   ├── __init__.py       # searcher 公開
│   ├── searxng.py        # SearXNG (Docker, 70+ エンジン)
│   ├── exa_searcher.py   # Exa (セマンティック検索)
│   └── internal_searcher.py  # Gnōsis + Sophia + Kairos
├── tests/
│   ├── test_searchers.py       # S1: SearXNG (5 tests)
│   ├── test_internal_searchers.py  # S2: Internal (7 tests)
│   ├── test_synthesizer.py     # S3: Synthesizer (6 tests)
│   ├── test_citation_agent.py  # S4: CitationAgent (9 tests)
│   └── test_engine.py         # S5: Engine (5 tests)
└── PROOF.md              # この文書
```

## S1: SearXNG Docker + Client (2026-02-15)

```
test_searchers.py  — 5 tests, all passed
```

## S2: Exa + Internal Searchers (2026-02-15)

| テスト | 結果 |
|:-------|:-----|
| test_gnosis_search | ✅ PASSED |
| test_gnosis_search_with_filter | ✅ PASSED |
| test_sophia_search | ✅ PASSED |
| test_sophia_with_custom_dir | ✅ PASSED |
| test_kairos_search | ✅ PASSED |
| test_kairos_with_empty_dir | ✅ PASSED |
| test_all_internal_searchers | ✅ PASSED |

## S3: Multi-Model Synthesizer (2026-02-15)

| テスト | 結果 |
|:-------|:-----|
| test_format_results | ✅ PASSED |
| test_extract_citations | ✅ PASSED |
| test_extract_confidence | ✅ PASSED |
| test_divergence_single_model | ✅ PASSED |
| test_divergence_two_models | ✅ PASSED |
| test_gemini_synthesis (Cortex API) | ✅ PASSED |

## S4: Citation Agent (2026-02-15)

| テスト | 結果 |
|:-------|:-----|
| test_compute_similarity_exact | ✅ PASSED |
| test_compute_similarity_partial | ✅ PASSED |
| test_compute_similarity_none | ✅ PASSED |
| test_extract_claims | ✅ PASSED |
| test_extract_claims_no_refs | ✅ PASSED |
| test_verify_with_content | ✅ PASSED |
| test_verify_no_url | ✅ PASSED |
| test_verify_no_claim | ✅ PASSED |
| test_verify_fabricated | ✅ PASSED |

## S5: Engine + CLI (2026-02-15)

| テスト | 結果 |
|:-------|:-----|
| test_report_markdown_empty | ✅ PASSED |
| test_report_markdown_with_results | ✅ PASSED |
| test_engine_init | ✅ PASSED |
| test_engine_research_internal_only (API) | ✅ PASSED |
| test_engine_research_full (API) | ✅ PASSED |

## Sprint 状態

| Sprint | 内容 | テスト | 状態 |
|:-------|:-----|:-------|:-----|
| **S1** | models + SearXNG Docker + searxng.py | 5/5 | ✅ 完了 |
| **S2** | exa + internal searchers | 7/7 | ✅ 完了 |
| **S3** | synthesizer (Cortex) | 6/6 | ✅ 完了 |
| **S4** | CitationAgent | 9/9 | ✅ 完了 |
| **S5** | engine + CLI | 5/5 | ✅ 完了 |
| **合計** | | **32/32** | ✅ **全完了** |

## 追加修復

- `mekhane/ochema/proto/__init__.py`: v8 proto 定義復元 (リファクタリング時の消失バグ修正)
