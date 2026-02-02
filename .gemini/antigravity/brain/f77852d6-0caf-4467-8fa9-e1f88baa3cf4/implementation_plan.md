# P3: SEL Enhancement Implementation Plan

> **Goal**: SEL (85-90%) を補完し、CCL 遵守率を 96%+ に引き上げる
> **Status**: 📋 Planning

## Background

SEL v1.0 で記号→言語マッピングによる遵守率向上を達成 (30% → 90%)。
しかし、根本的な実行保証には追加レイヤーが必要。

## Research Summary (2026-02-01)

### Activation Steering

| 項目 | 状況 |
|:-----|:-----|
| **ICLR 2025** | Instruction-following 向上、cross-model steering 可能 |
| **FGAA 2025** | Feature Guided Activation Additions、精度改善 |
| **API 対応** | ❌ Claude API/Gemini API は steering vector 未サポート |
| **実装可能性** | OSS LLM (LLaMA, Mistral) のみ。Synergeia では不可 |

### Grammar-Constrained Decoding

| 項目 | 状況 |
|:-----|:-----|
| **LMQL** | 制約付きデコード、eager masking |
| **Outlines** | JSON Schema 強制、Pydantic 統合 |
| **ICML 2025** | 前処理オーバーヘッド削減手法 |
| **API 対応** | ✅ OpenAI/Gemini の Structured Outputs で部分実現 |

---

## Proposed Phases

### Phase 1: Grammar-Constrained Decoding (CCL Parser + Pydantic)

**目的**: CCL 出力を JSON Schema で強制し、構造的正確性を保証

#### 1.1 [NEW] `hegemonikon/mekhane/ccl/schema_validator.py`

```python
from pydantic import BaseModel, Field

class CCLOutput(BaseModel):
    workflow: str
    operator: str = Field(pattern=r"[+\-*!^]")
    mode: str | None = None
    minimum_requirements_met: list[str]
    output: str
```

#### 1.2 [MODIFY] `/synergeia` API 呼び出し

- Gemini API の `response_schema` パラメータで CCLOutput を指定
- Claude API の `tool_use` で構造化出力を強制

#### 1.3 Verification

- 既存の `/boot+` テストケースで structured output を確認
- `minimum_requirements_met` フィールドが SEL 要件をカバーしているか検証

---

### Phase 2: Multi-Agent Verification (/vet 強化)

**目的**: 事後検証で SEL 遵守を確認し、非遵守時に再実行

#### 2.1 [MODIFY] `/vet` ワークフロー

- SEL 遵守チェックを `/vet` に統合
- `minimum_requirements` リストと実際の出力を照合
- 非遵守項目があれば再実行を提案

#### 2.2 Verification

- `/boot+` → `/vet` パイプラインで遵守率を測定

---

### Phase 3: Activation Steering (調査のみ)

**目的**: OSS LLM でのローカル実験として追跡

> [!WARNING]
> Claude/Gemini API では実装不可。OSS LLM (vLLM + LLaMA) での実験に限定。

#### 3.1 調査項目

- `llm_steer` ライブラリの動作確認
- Contrastive prompt pair の設計（CCL 遵守 vs 非遵守）
- Middle layer (8-16) への steering vector 注入

#### 3.2 Non-Goal

- Production 環境への統合は対象外

---

## Priority

| Phase | Priority | Effort | Impact |
|:------|:---------|:-------|:-------|
| Phase 1 | 🔴 High | Medium | 90% → 95% |
| Phase 2 | 🟠 Medium | Low | 95% → 96% |
| Phase 3 | 🟢 Low | High | 研究のみ |

## Verification Plan

### Phase 1 Verification

1. **Unit Test**: `schema_validator.py` の Pydantic モデル検証

   ```bash
   cd /home/makaron8426/oikos/hegemonikon && python -m pytest mekhane/ccl/test_schema_validator.py -v
   ```

2. **Integration Test**: Synergeia API での structured output

   ```bash
   cd /home/makaron8426/oikos/hegemonikon && python synergeia/test_structured_output.py
   ```

### Phase 2 Verification

1. **Manual Test**: `/boot+` → `/vet` パイプライン実行
   - `/boot+` を実行
   - `/vet` で SEL 遵守をチェック
   - 非遵守項目の検出を確認

### Phase 3 Verification

- N/A (調査フェーズのため)

---

*Created: 2026-02-01T11:45*
