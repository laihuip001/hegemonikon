# Hermēneus Phase 4: DSPy Optimizer 統合

> **CCL**: `/mek+ [hermeneus.phase4.dspy]`
> **目的**: CCL→LMQL パイプラインの自動プロンプト最適化

---

## 概要

DSPy 3.0 を統合し、Hermēneus の LMQL 出力を自動的に最適化する。

## DSPy 3.0 特徴 (2025-08)

| 機能 | 説明 |
|:-----|:-----|
| **Signatures** | 宣言的出力仕様 |
| **Modules** | ChainOfThought, ReAct 等 |
| **Optimizers** | MIPROv2, BootstrapFewShot |
| **RLM** | 再帰的言語モデル (2026-01) |

## アーキテクチャ

```
CCL → Expander → Parser → AST → Translator → LMQL
                                                ↓
                                        ┌───────────────┐
                                        │ DSPy Optimizer│  ← NEW
                                        │   MIPROv2     │
                                        └───────┬───────┘
                                                ↓
                                          Optimized LMQL
                                                ↓
                                        Runtime → Output
```

## 実装計画

### [NEW] `hermeneus/src/optimizer.py`

```python
import dspy

class CCLSignature(dspy.Signature):
    """CCL 実行のための DSPy シグネチャ"""
    ccl_expression = dspy.InputField(desc="CCL式")
    context = dspy.InputField(desc="入力コンテキスト")
    output = dspy.OutputField(desc="構造化出力")

class CCLOptimizer:
    """DSPy ベースの CCL 最適化器"""
    
    def __init__(self, model: str = "openai/gpt-4o"):
        self.lm = dspy.LM(model)
        dspy.configure(lm=self.lm)
        
    def optimize(self, examples: list) -> dspy.Module:
        """Few-shot 例から最適化されたモジュールを生成"""
        optimizer = dspy.MIPROv2(
            metric=self._evaluate,
            num_candidates=10,
        )
        return optimizer.compile(CCLExecutor(), trainset=examples)
    
    def _evaluate(self, example, prediction):
        """出力品質メトリクス"""
        # SEL 遵守率、構造正しさ、情報密度
        pass
```

### [MODIFY] `hermeneus/src/__init__.py`

```python
from .optimizer import CCLOptimizer, optimize_ccl
```

### [NEW] `hermeneus/tests/test_optimizer.py`

```python
def test_mipro_optimization():
    optimizer = CCLOptimizer()
    examples = [
        {"ccl": "/noe+", "context": "分析対象", "expected": "..."},
        {"ccl": "/dia+", "context": "レビュー対象", "expected": "..."},
    ]
    module = optimizer.optimize(examples)
    assert module is not None
```

## 依存関係追加

```bash
pip install dspy-ai>=3.0.0
```

## メトリクス

| メトリクス | 測定方法 |
|:-----------|:---------|
| **SEL 遵守率** | 必須フィールド存在率 |
| **構造正しさ** | JSON スキーマ検証 |
| **情報密度** | トークン効率 |
| **収束速度** | 反復回数 |

## タイムライン

| 日程 | マイルストーン |
|:-----|:---------------|
| Week 1 | DSPy 3.0 環境構築 + CCLSignature 定義 |
| Week 2 | MIPROv2 統合 + 評価メトリクス実装 |
| Week 3 | テスト + 既存パイプラインへの統合 |
| Week 4 | 本番デプロイ + パフォーマンス測定 |

## リスク

| リスク | 対策 |
|:-------|:-----|
| DSPy 依存関係衝突 | venv 分離 |
| 最適化コスト (API 呼び出し) | キャッシュ活用 |
| 既存コードとの互換性 | オプショナル統合 |

---

*Phase*: 4 (Optimization Layer)
*工数見積もり*: 3-4 週間
*依存*: Phase 1-3 完了 ✅
