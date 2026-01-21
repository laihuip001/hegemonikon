# LLM自信過剰（Overconfidence）防止の構築的方法論

**調査日**: 2026-01-21
**調査者**: Perplexity (パプ君)
**目的**: LLMの自信過剰を防ぎつつ、正確な原因分析能力を維持する方法

---

## エグゼクティブサマリー

LLMの自信過剰は、既存のRLHF後のモデルに顕著に表現される構造的問題であり、単なる「謙虚さ」の表現強化では解決できない。2024-2026年の最新研究は、この問題の根本原因が**報酬モデルのバイアス**、**遅思考メカニズムの欠落**、**Dunning-Kruger効果の再現**にあることを明らかにしている。

過信防止と正確な原因分析の両立は、以下の三つの層での介入で実現可能：
1. プロンプトレベルの**確信度明示化と分離**
2. 微調整段階での**検証行動の強化**
3. 推論時の**多エージェント検証と外部グラウンディング**

---

## I. 問題の本質

### 1.1 RLHF後の過信メカニズム

LLMの過信は知識欠落ではなく、**報酬信号の歪み**に起因する。報酬モデルがタスク品質とは独立に高信度スコアへバイアスを持つため、モデルは「高く見える信頼度スコアを生成する」行動を強化される。

### 1.2 思考深度と過信の逆説的関係

直感に反して、**より長いChain-of-Thought推論は過信を増加させる**。対照的に、検索拡張生成（RAG）を伴う推論は信頼度を根拠に基づいて適切に調整する。

### 1.3 Dunning-Kruger効果

LLMも人間と同じDunning-Kruger曲線を表現する。小規模モデル（7B-13B）は全難度タスクで一貫して過信、大規模モデル（70B+）は難タスクでのみ過信。

---

## II. 手法比較表

| 手法 | ECE削減 | 推論オーバーヘッド | 微調整必要 | 実装期間 |
|------|--------|------------------|----------|----------|
| **Answer-Free Confidence Estimation (AFCE)** | 40-70% | 最小 | 不要 | 1週間 |
| **Distractor-Augmented Prompt** | 最大90% | 中 | 不要 | 1-2週間 |
| **Collaborative Calibration（マルチエージェント）** | 30-50% | 高 | 不要 | 2-3週間 |
| **Confidence-Supervised Fine-Tuning (CSFT)** | 20-35% | 低 | 必須 | 2-4週間 |
| **Retrieval-Augmented Generation (RAG)** | 検証依存 | 高 | 不要 | 1-3週間 |

---

## III. 推奨プロンプトパターン

### 3.1 Answer-Free Confidence Estimation (AFCE)

回答生成と信頼度評価を**時間的に分離**する。

```
System Prompt:
You will first assess your confidence in answering the following question,
WITHOUT generating an answer. Then, you will provide your answer.

Format:
- Confidence Stage: Report only [HIGH|MEDIUM|LOW] with brief reasoning
- Answer Stage: Provide substantive response
```

効果: ECE改善40-60%（特に難タスクで70%）

### 3.2 Calibrated Confidence Protocol (CCP)

```
PHASE 1: EPISTEMIC AUDIT
1. Question type classification: [factual | causal | predictive | prescriptive]
2. Domain assessment: coverage, recency
3. Assumption identification

PHASE 2: DUAL-PATH REASONING
Path A: "If my assumptions are correct, then [answer]"
Path B: "Alternative scenarios where I'd be wrong"

PHASE 3: CALIBRATED OUTPUT
{
  "answer": "[response]",
  "confidence": {"level": 0-100, "epistemic_type": "...", "uncertainty_sources": [...]},
  "verification_needed": true/false
}

CONFIDENCE ANCHORS:
- 90-100%: Established facts only
- 70-89%: Strong inference with minor uncertainty
- 50-69%: Reasonable inference with caveats
- 30-49%: Speculative
- 0-29%: Out-of-domain, defer to experts
```

### 3.3 メタ認知チェック（Anti-Illusion Pattern）

```
Q1: "Can I explain the underlying MECHANISM in first-principles?"
  → If No → confidence_penalty = -20%

Q2: "What would an expert with OPPOSING view argue?"
  → If cannot articulate → -15%

Q3: "Have I encountered edge cases?"
  → If zero known → -10% (suspiciously clean)

Q4: "Could my answer be wrong due to unknown unknowns, recent data, alternatives?"
  → Penalties per category

confidence_final = max(5%, confidence_raw - sum(penalties))
```

---

## IV. Hegemonikónへの適用

「私はミスをする」「知っているつもりは危険」を、**過度の自己帰属バイアスなしに**実装するには：

1. **明示的なエラー分解**:
   「このエラーは [自己要因40%] vs [外部要因60%] の分析に基づく」

2. **外部帰属の同等視**:
   入力品質、知識更新、マルチモーダル欠落を対等に列挙

3. **難度適応型謙虚さ**:
   易タスクは高信頼（80-90%）、難タスク低信頼（30-50%）

4. **検証レディネス**:
   「確信度X% → 検証必要 [Yes|No]」で正直性を保証

---

## V. 実装ロードマップ

### Phase 1（2-3週間）: 基盤構築
- [ ] AFCE 2段階プロンプト実装
- [ ] ECE計算スクリプト統合
- [ ] ベースラインテスト

### Phase 2（4-6週間）: 拡張
- [ ] CCP をシステムプロンプト統合
- [ ] Multi-Perspective Consistency
- [ ] Dunning-Kruger補正ロジック

### Phase 3（8-12週間）: 最適化
- [ ] Collaborative Calibration
- [ ] RAG統合
- [ ] Structured Reasoning

---

## 参考文献

- Ye et al. (2025). HonestVQA. arXiv:2506.23464
- Zhang et al. (2025). Mind the Confidence Gap. arXiv:2502.11028
- Singhal et al. (2024). Taming Overconfidence via Reward Calibration. arXiv:2410.09724
- Xu et al. (2025). Do Language Models Mirror Human Confidence? arXiv:2506.00582
- LearnPrompting (2024). Self-Verification Prompting

---

```
┌─[Hegemonikon]──────────────────────┐
│ M8 Anamnēsis: Research Captured    │
│ Topic: LLM Overconfidence          │
│ Status: Archived                   │
└────────────────────────────────────┘
```
