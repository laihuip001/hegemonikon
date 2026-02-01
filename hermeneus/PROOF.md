# PROOF: Hermēneus Directory

## Existence Justification

| File | L | Justification |
|:-----|:--|:--------------|
| `README.md` | L4/運用 | プロジェクト概要・ロードマップ |
| `docs/` | L4/運用 | 設計ドキュメント置き場 |
| `src/` | L2/インフラ | ソースコード置き場 |
| `tests/` | L2/インフラ | テスト置き場 |

## Origin

- `/zet+`: CCL 実行保証の欠落分析
- `/sop+`: ハイブリッドアーキテクチャ調査
- `/noe!`: 4層設計

## Derivation

```
A5 公理5 (必然的存在)
  → 定理 L2.1: 必要なインフラは実装
  → hermeneus/: CCL 実行保証に必須
      → Expander, Parser, AST, Translator
```

---

*Created: 2026-01-31*
