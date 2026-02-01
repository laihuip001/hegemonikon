# Hermēneus — CCL 実行保証コンパイラ

> **Ἑρμηνεύς** (Hermēneus) = 翻訳者、解釈者
> CCL を実行可能な形式に翻訳し、実行保証を提供する

---

## 概要

Hermēneus は CCL (Cognitive Control Language) を LMQL/LangGraph に翻訳し、
ハイブリッドアーキテクチャによる**実行保証（>96% 信頼度）**を実現するコンパイラ。

## アーキテクチャ

```
CCL Human → Expander → Parser → AST → LMQL → LLM → Validator → Output
             │          │        │      │              │
             │          │        │      └─ Constrained Decoding
             │          │        └─ Workflow/Sequence/ConvergenceLoop
             │          └─ 正式形変換
             └─ 省略形展開
```

## 4層構造

| 層 | 技術 | 役割 |
|:---|:-----|:-----|
| **最適化** | DSPy | 自動プロンプト改善 |
| **制御** | LMQL/Guidance | 構造化生成 |
| **実行** | LangGraph | オーケストレーション |
| **検証** | Constrained Decoding | 出力保証 |

## ディレクトリ構造

```
hermeneus/
├── README.md           # このファイル
├── docs/               # 設計ドキュメント
├── src/                # ソースコード
│   ├── expander.py     # 省略形展開
│   ├── parser.py       # CCL パーサー
│   ├── ast.py          # AST 定義
│   ├── translator.py   # LMQL 変換
│   └── validator.py    # 出力検証
└── tests/              # テスト
```

## 現状

- ✅ PoC 完了: `mekhane/ccl/lmql_translator.py`
- ❌ 正式版: 未実装

## ロードマップ

| Phase | 内容 | 工数 |
|:------|:-----|:-----|
| 1 | Expander + Parser 正式版 | M |
| 2 | LMQL ランタイム統合 | L |
| 3 | Constrained Decoding | M |
| 4 | LangGraph 統合 | L |

---

*Created: 2026-01-31*
