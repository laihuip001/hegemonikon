# PROOF: Hermēneus Directory

## Existence Justification

| File | L | Justification |
|:-----|:--|:--------------|
| `README.md` | L4/運用 | プロジェクト概要・ロードマップ |
| `src/ast.py` | L2/インフラ | CCL AST ノード定義 (Workflow, Condition, CPL v2.0) |
| `src/expander.py` | L2/インフラ | @macro 展開、省略形→正式形変換 |
| `src/parser.py` | L2/インフラ | CCL パーサー (CPL v2.0 対応) |
| `src/translator.py` | L2/インフラ | AST → LMQL 変換器 |
| `src/__init__.py` | L2/インフラ | パッケージ API `compile_ccl()` |
| `tests/test_parser.py` | L2/インフラ | 単体テスト (19 passed) |

## Origin

- `/zet+`: CCL 実行保証の欠落分析
- `/sop+`: ハイブリッドアーキテクチャ調査
- `/noe!`: 4層設計

## Implementation Status

| Phase | Status |
|:------|:-------|
| **Phase 1**: Expander + Parser | ✅ Complete (2026-02-01) |
| **Phase 2**: LMQL Runtime | ⏳ Pending |
| **Phase 3**: LangGraph | ⏳ Pending |

## Derivation

```
A5 公理5 (必然的存在)
  → 定理 L2.1: 必要なインフラは実装
  → hermeneus/: CCL 実行保証に必須
      → Expander, Parser, AST, Translator
```

---

*Created: 2026-01-31 | Phase 1 Completed: 2026-02-01*
