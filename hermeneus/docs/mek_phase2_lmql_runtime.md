# [CCL]/mek+ Hermēneus Phase 2 — LMQL ランタイム統合

---
sel:
  workflow: /mek+
  scope: P2=lmql_runtime
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - LMQL 環境構築手順
    - 実行ランタイム統合
    - Constrained Decoding 実装
---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 2"
  [target: LMQL Runtime Integration]
  {
    /s1 "Environment"     -- pip install lmql
    /s2 "Runtime"         -- LMQL 実行エンジン
    /s3 "Constraints"     -- Constrained Decoding
    /s4 "Verification"    -- 実行検証
  }
  >> 動作確認 ✅
```

---

## Phase 2 概要

| 属性 | 値 |
|:-----|:---|
| **目標** | compile_ccl() の出力を実際に実行可能にする |
| **成果物** | `hermeneus/src/runtime.py` |
| **依存** | `pip install lmql` |
| **検証** | 実際の LLM 呼び出しで動作確認 |

---

## 実装タスク CCL

```ccl
# Phase 2 タスクリスト
let phase_2_tasks = [
  /s1+ "Environment Setup" {
    pip install lmql
    pip install outlines  # Constrained Decoding
    環境変数設定 (OPENAI_API_KEY)
  }
  
  /s2+ "Runtime Engine" {
    LMQLExecutor クラス作成
    compile_ccl() 出力を実行
    結果パース
  }
  
  /s3+ "Constrained Decoding" {
    JSON Schema 強制
    Outlines 統合
    出力検証
  }
  
  /s4+ "Verification" {
    実際の LLM 呼び出しテスト
    収束ループ実行確認
    エラーハンドリング
  }
]

F:[phase_2_tasks]{/ene+} >> 全タスク完了
```

---

## コンポーネント設計

### LMQLExecutor

```ccl
/mek "LMQLExecutor"
  [input: LMQL Program]
  [output: Execution Result]
  {
    # クラス構造
    class LMQLExecutor:
      model: str           -- "openai/gpt-4o"
      timeout: int         -- 300
      max_retries: int     -- 3
      
      def execute(lmql_code: str) -> dict:
        # LMQL 実行
        # 結果パース
        # エラーハンドリング
  }
```

### ConstrainedDecoder

```ccl
/mek "ConstrainedDecoder"
  [input: Schema + Prompt]
  [output: Validated JSON]
  {
    # Outlines 統合
    from outlines import generate
    
    def decode_with_schema(prompt, schema):
      generator = generate.json(model, schema)
      return generator(prompt)
  }
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/runtime.py` | [NEW] LMQL 実行エンジン |
| `src/constraints.py` | [NEW] Constrained Decoding |
| `src/__init__.py` | [MODIFY] execute_ccl() 追加 |
| `tests/test_runtime.py` | [NEW] ランタイムテスト |

---

## 依存関係

```bash
# 必須
pip install lmql>=0.7.0
pip install outlines>=0.0.30

# オプション (高速化)
pip install vllm  # ローカル実行時
```

---

## 使用例 (目標)

```python
from hermeneus.src import compile_ccl, execute_ccl

# コンパイル
lmql_code = compile_ccl("/noe+ >> V[] < 0.3")

# 実行 (Phase 2 で追加)
result = execute_ccl(
    ccl="/noe+ >> V[] < 0.3",
    context="プロジェクトの設計を分析してください",
    model="openai/gpt-4o"
)

print(result.final_output)
print(result.iterations)  # 収束までの反復回数
print(result.confidence)  # 最終確信度
```

---

## 検証 CCL

```ccl
/vet "Hermēneus Phase 2"
  [scope: hermeneus/tests/test_runtime.py]
  {
    # 単体テスト
    pytest tests/test_runtime.py -v
    
    # 統合テスト (実際の LLM 呼び出し)
    python -c "from hermeneus.src import execute_ccl; print(execute_ccl('/noe+', 'test'))"
  }
  >> 全テスト通過 ✅
```

---

## リスク分析 CCL

```ccl
/pre "Phase 2 Risks"
  {
    R1: LMQL API 変更        -- バージョン固定で対処
    R2: API キー設定ミス     -- 明確なエラーメッセージ
    R3: タイムアウト         -- リトライロジック実装
    R4: レート制限           -- exponential backoff
  }
  >> リスク緩和策実装
```

---

## 次ステップ

```ccl
# Phase 2 完了後 → Phase 3
/mek+ "LangGraph Integration"
  {
    Checkpointer
    状態永続化
    HITL (Human-in-the-Loop)
  }
  _/ene+
```

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 2*
