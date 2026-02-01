# Hermēneus — CCL 実行保証コンパイラ

> **Ἑρμηνεύς** (Hermēneus) = 翻訳者、解釈者
> CCL を実行可能な形式に翻訳し、実行保証を提供する

---

## 概要

Hermēneus は CCL (Cognitive Control Language) を LMQL/LangGraph に翻訳し、
ハイブリッドアーキテクチャによる**実行保証（>96% 信頼度）**を実現するコンパイラ。

## クイックスタート

```python
from hermeneus.src import compile_ccl, execute_ccl

# CCL → LMQL 変換
lmql_code = compile_ccl("/noe+ >> V[] < 0.3")
print(lmql_code)

# CCL 実行 (LMQL ランタイム経由)
result = execute_ccl("/noe+", context="分析対象")
print(result.output)
```

## アーキテクチャ

```
CCL Human → Expander → Parser → AST → Translator → LMQL → Runtime → Output
              │          │        │         │          │          │
              │          │        │         │          │          └─ HITL Controller
              │          │        │         │          └─ Constrained Decoding
              │          │        │         └─ LMQL Template
              │          │        └─ Workflow/Sequence/ConvergenceLoop/CPL
              │          └─ 正式形変換
              └─ 省略形展開 (@macro も)
```

## 4層構造

| 層 | 技術 | 役割 | 状態 |
|:---|:-----|:-----|:-----|
| **最適化** | DSPy | 自動プロンプト改善 | ⏳ Phase 4 |
| **制御** | LMQL/Guidance | 構造化生成 | ✅ 完了 |
| **実行** | LangGraph | オーケストレーション | ✅ 完了 |
| **検証** | Constrained Decoding | 出力保証 | ✅ 完了 |

## 実装済みモジュール

```
hermeneus/
├── README.md               # このファイル
├── PROOF.md                # Hegemonikón 公理対応
├── docs/                   # 設計ドキュメント
├── src/                    # ソースコード (~100KB)
│   ├── __init__.py         # パッケージ API
│   ├── ast.py              # AST 定義 (11 ノード型)
│   ├── expander.py         # 省略形展開
│   ├── parser.py           # CCL パーサー (F:/I:/W:/L: 対応)
│   ├── translator.py       # LMQL 変換
│   ├── runtime.py          # LMQL 実行エンジン
│   ├── constraints.py      # Constrained Decoding
│   ├── graph.py            # LangGraph 統合
│   ├── checkpointer.py     # 状態永続化
│   └── hitl.py             # Human-in-the-Loop
└── tests/                  # テスト (50 件)
    ├── test_parser.py
    ├── test_runtime.py
    └── test_graph.py
```

## 現状

| Phase | 内容 | 状態 |
|:------|:-----|:-----|
| 1 | Expander + Parser 正式版 | ✅ 完了 |
| 2 | LMQL ランタイム統合 | ✅ 完了 |
| 3 | LangGraph + HITL | ✅ 完了 |
| 4 | Multi-Agent Debate + Audit | ✅ 完了 |
| 4b | Prover (mypy/Lean4) | ✅ 完了 |
| 5 | CLI + Production | ✅ 完了 |
| 6 | Workflow Executor + Synergeia | ✅ 完了 |
| 7 | MCP Server (AI 自己統合) | ✅ 完了 |

**テスト**: `pytest hermeneus/tests/ -v` → 125/125 パス

## MCP 統合 (AI 自己統合)

Antigravity IDE から Hermēneus を直接呼び出す:

```json
// settings.json に追加
{
  "mcp.servers": {
    "hermeneus": {
      "command": "python",
      "args": ["-m", "hermeneus.src.mcp_server"],
      "cwd": "/home/laihuip001/oikos/hegemonikon"
    }
  }
}
```

### MCP ツール

| ツール | 機能 |
|:-------|:-----|
| `hermeneus_execute` | CCL ワークフローを実行 |
| `hermeneus_compile` | CCL を LMQL にコンパイル |
| `hermeneus_audit` | 監査レポートを取得 |
| `hermeneus_list_workflows` | ワークフロー一覧 |

## CLI

```bash
# コンパイル
python -m hermeneus.src compile "/noe+ >> V[] < 0.3"

# 実行
python -m hermeneus.src execute "/noe+" --context "分析対象"

# 検証 (Multi-Agent Debate)
python -m hermeneus.src verify "/ene+" --rounds 3 --min-conf 0.7

# 監査レポート
python -m hermeneus.src audit --period last_7_days

# 型チェック
python -m hermeneus.src typecheck mycode.py --strict
```

## API リファレンス

### メイン関数

| 関数 | 引数 | 戻り値 |
|:-----|:-----|:-------|
| `compile_ccl(ccl, macros, model)` | CCL 式 | LMQL コード |
| `execute_ccl(ccl, context, config)` | CCL 式 + コンテキスト | ExecutionResult |
| `verify_execution(ccl, output)` | CCL + 出力 | ConsensusResult |
| `verify_code(code)` | Python コード | ProofResult |
| `build_graph(ccl)` | CCL 式 | CompiledGraph |

### AST ノード

| ノード | 説明 | 例 |
|:-------|:-----|:---|
| `Workflow` | ワークフロー | `/noe+` |
| `Sequence` | シーケンス | `/s+ _ /ene` |
| `ConvergenceLoop` | 収束ループ | `/noe >> V[]<0.3` |
| `ForLoop` | 反復 | `F:[×3]{/dia}` |
| `IfCondition` | 条件分岐 | `I:[V[]>0.5]{/noe+}` |
| `WhileLoop` | 条件ループ | `W:[E[]>0.3]{/dia}` |
| `Lambda` | ラムダ | `L:[x]{x+}` |

---

*Created: 2026-01-31 | Updated: 2026-02-01 (Phase 1-5 完了 / 89 tests)*
