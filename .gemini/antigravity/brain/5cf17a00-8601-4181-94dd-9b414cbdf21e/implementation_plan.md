# /mek+ Hermeneus Phase 4: DSPy Optimizer

---
sel:
  workflow: /mek+
  scope: P1=hermeneus-phase4
  output_format: CCL Skill Definition + Synergeia Pipeline
  quality_gate:
    - CCL 式で全ステップを記述
    - DSPy API 統合
    - 自動プロンプト最適化
---

## CCL シグネチャ

```ccl
/mek+ "Hermeneus Phase 4: DSPy Optimizer"
  [target: optimizer.py]
  {auto_optimize_prompt()}
  >> "accuracy > 0.9"
```

---

## 背景

```ccl
let @hermeneus_status = (
  phase1: [✓] "Expander, Parser, Translator"
  phase2: [✓] "LMQL Runtime"
  phase3: [✓] "LangGraph + HITL + Constrained Decoding"
  phase4: [ ] "DSPy Optimizer"  # ← 今回
)
```

---

## DSPy とは

```ccl
/sop+ "DSPy 2026"
  {
    概要: "自動プロンプト最適化フレームワーク"
    核心: [
      "Teleprompter: 最適プロンプト探索",
      "Signature: 入出力スキーマ定義",
      "Module: LM 呼び出しの抽象化"
    ]
  }
```

---

## メイン CCL プログラム

```ccl
# Phase 4 分散実行 (Total: ~45 CP)

let @research = @thread[perplexity]{
  /sop+ "DSPy Python 2026, pip install dspy-ai, Teleprompter, optimization metrics"
  >> "実装例 3件以上"
}

let @design = @thread[antigravity]{
  /noe+^s2 "optimizer.py 設計"
  [input: @research]
  {
    components: [
      "CCLSignature: CCL→DSPy Signature 変換",
      "CCLOptimizer: Teleprompter ラッパー",
      "OptimizationConfig: 最適化パラメータ"
    ]
  }
  >> "アーキテクチャ図"
}

let @implement = @thread[claude]{
  /s+_/ene "optimizer.py 実装"
  [input: @design]
  [scope: hermeneus/src/]
  {
    create: "hermeneus/src/optimizer.py"
    modify: "hermeneus/src/__init__.py"
    test: "hermeneus/tests/test_optimizer.py"
  }
  >> "pytest pass"
}

let @review = @thread[antigravity]{
  /dia+\a2 "最適化ロジックレビュー"
  [input: @implement]
  {
    checks: [
      "DSPy API 正しい使用",
      "最適化ループの収束保証",
      "リソースリーク防止"
    ]
  }
  >> "blocker = 0"
}

# パイプライン
@research |> @design |> @implement |> @review
>> lim[V[] < 0.2]{
  I:[blocker > 0]{ @fix _@implement _@review }
}
```

---

## optimizer.py 設計 CCL

```ccl
/s+ "optimizer.py"
  [target: hermeneus/src/optimizer.py]
  {
    # クラス階層
    class CCLSignature:
      "CCL AST → DSPy Signature 変換"
      input: AST
      output: dspy.Signature
      
    class CCLOptimizer:
      "Teleprompter によるプロンプト最適化"
      config: OptimizationConfig
      methods: [
        "optimize(ccl, examples) -> OptimizedProgram",
        "evaluate(program, test_set) -> Metrics",
        "save(program, path)"
      ]
      
    class OptimizationConfig:
      "最適化パラメータ"
      fields: [
        "metric: Callable[[Example], float]",
        "num_trials: int = 10",
        "teleprompter: str = 'BootstrapFewShot'"
      ]
  }
  >> "compile + mypy pass"
```

---

## 検証 CCL

```ccl
/vet "Phase 4"
  [scope: hermeneus/]
  {
    F:[test_files]{
      pytest: "-v"
    }
    
    # 最適化動作確認
    manual: |
      from hermeneus.src.optimizer import CCLOptimizer
      opt = CCLOptimizer()
      result = opt.optimize("/noe+", examples=[...])
      assert result.accuracy > 0.8
  }
  >> "all green"
```

---

## 収束条件

```ccl
lim[V[] < 0.15]{
  tests: "35 + new > 40 pass"
  optimize("/noe+"): "accuracy > 0.85"
  blocker: 0
}
```

---

## 成果物マトリクス

| ファイル | アクション | CCL | サイズ目安 |
|:---------|:-----------|:----|:-----------|
| [optimizer.py](file:///home/makaron8426/oikos/hegemonikon/hermeneus/src/optimizer.py) | **NEW** | `/s+` | ~300 行 |
| [__init__.py](file:///home/makaron8426/oikos/hegemonikon/hermeneus/src/__init__.py) | **MODIFY** | `/ene` | +5 行 |
| [test_optimizer.py](file:///home/makaron8426/oikos/hegemonikon/hermeneus/tests/test_optimizer.py) | **NEW** | `/dia` | ~100 行 |

---

*Generated: 2026-02-01 13:55 | /mek+ Synergeia Distributed Execution v2*
