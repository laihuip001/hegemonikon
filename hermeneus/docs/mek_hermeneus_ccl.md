# [CCL]/mek+ Hermēneus — CCL 実行保証コンパイラ

---
sel:
  workflow: /mek+
  scope: P1=hermeneus
  output_format: CCL Skill Definition
  quality_gate: 
    - 明確なシグネチャ
    - 対応構文リスト
    - 使用例
---

## CCL シグネチャ

```
/mek+ "Hermēneus"
  [target: CCL → LMQL]
  {compile_ccl()} 
  >> 実行保証 > 96%
```

---

## スキル概要

| 属性 | 値 |
|:-----|:---|
| **名前** | Hermēneus (Ἑρμηνεύς) |
| **意味** | 翻訳者、解釈者 |
| **機能** | CCL → LMQL コンパイル |
| **目標** | >96% 実行保証 (ハイブリッドアーキテクチャ) |

---

## アーキテクチャ CCL

```ccl
# 4層ハイブリッドアーキテクチャ
let hermeneus_layers = [
  /s1+ "Optimization"   -- DSPy Teleprompter
  /s2+ "Control"        -- LMQL DSL
  /s3+ "Execution"      -- LangGraph
  /s4+ "Verification"   -- Multi-Agent Debate
]

# パイプライン
F:[hermeneus_layers]{
  /s+_/ene
} >> 信頼度 > 0.96
```

---

## コンポーネント CCL

### Expander (省略形展開)

```ccl
/mek "Expander"
  [input: CCL省略形]
  [output: CCL正式形]
  {
    @macro → 展開
    >> → lim[]{}
    /noe → /o1
  }
```

### Parser (構文解析)

```ccl
/mek "Parser"
  [input: CCL正式形]
  [output: AST]
  {
    # 対応構文
    /wf[+-^!']          -- ワークフロー + 演算子
    A_B_C               -- シーケンス
    A*B                 -- 融合
    A~B                 -- 振動
    A >> cond           -- 収束
    lim[cond]{body}     -- 収束(正式)
    F:[×N]{body}        -- FOR
    I:[cond]{then}      -- IF
    W:[cond]{body}      -- WHILE
    L:[x]{body}         -- Lambda
  }
```

### Translator (LMQL変換)

```ccl
/mek "Translator"
  [input: AST]
  [output: LMQL Program]
  {
    Workflow   → @lmql.query
    Sequence   → Step 1,2,3...
    Convergence → while loop
    Operators  → where constraints
  }
```

---

## 対応演算子マトリクス

| 演算子 | 意味 | LMQL 制約 |
|:-------|:-----|:----------|
| `+` | 深化 | `len(RESULT) > 500` |
| `-` | 縮約 | `len(RESULT) < 300` |
| `^` | 上昇 | `'前提' in RESULT` |
| `!` | 全展開 | `len(RESULT) > 800` |
| `\` | 反転 | `'しかし' in RESULT` |

---

## 使用例

```python
from hermeneus.src import compile_ccl

# 単純なワークフロー
lmql = compile_ccl("/noe+")

# 収束ループ
lmql = compile_ccl("/noe+ >> V[] < 0.3")

# シーケンス
lmql = compile_ccl("/s+_/ene")

# CPL 制御構文
lmql = compile_ccl("F:[×3]{/dia}")
lmql = compile_ccl("I:[V[] > 0.5]{/noe+} E:{/noe-}")
```

---

## テスト CCL

```ccl
/vet "Hermēneus"
  [scope: hermeneus/tests/]
  {pytest tests/test_parser.py -v}
  >> 19/19 passed ✅
```

---

## 次フェーズ CCL

```ccl
# Phase 2: LMQL 統合
/mek+ "LMQL Runtime"
  {pip install lmql}
  _/ene+

# Phase 3: LangGraph
/mek+ "Orchestration"
  {LangGraph + Checkpointer}
  _/ene+
```

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus*
