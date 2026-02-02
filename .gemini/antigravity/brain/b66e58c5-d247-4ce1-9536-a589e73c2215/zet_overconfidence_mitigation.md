# LLMの過信低減：実証済み手法と Hegemonikón S4 Epochē統合設計

> **調査元**: Perplexity Deep Research (2026-01-28)
> **目的**: S4 Epochē スキル設計の根拠

---

## 実証済み手法の構造化テーブル

| 手法名 | 効果 | 実装難易度 | 情報源URL | 取得時点 |
|--------|------|----------|---------|---------|
| **Chain-of-Verification (CoVe)** | ハリシネーション23%削減、F1スコア23%向上 | 中 | arxiv:2309.11495 | 2024-2025 |
| **Self-Consistency + Confidence Integration (CISC)** | 推論パス40%削減で同等精度 | 中 | ACL 2025 | 2025 |
| **Reflection Prompting** | ECE 41.9-51.2%削減、Brier Score 51.2%改善 | 高 | ACL TrustNLP 2025 | 2025 |
| **Verbalized Confidence + Epistemic Markers** | 中程度表現で信頼スコア最大化 | 低 | ScienceDirect 2025 | 2025 |
| **Answer-Free Confidence Estimation (AFCE)** | 過信削減＋困難度感度向上 | 中 | ACL 2025 | 2025 |
| **Multi-Perspective Consistency (MPC)** | Overconfidenceテストで改善 | 中 | arxiv:2402.11279 | 2024 |
| **EAGLE（内部信念集約）** | キャリブレーション性能向上 | 高 | arxiv:2509.01564 | 2025 |
| **The Epistemic Suite** | 判断停止（suspension）の明示的実装 | 高 | arxiv:2510.24721 | 2025 |
| **Thought Calibration** | 思考トークン20%削減で精度維持 | 中 | EMNLP 2025 | 2025 |
| **Ensemble + Temperature Calibration** | ECE 47-53%改善 | 高 | arxiv:2508.06225 | 2024-2025 |

**測定基準**:

- ECE（Expected Calibration Error）: 典型的 LLM = 0.12-0.40、目標 ≤ 0.10
- Brier Score: 目標 ≤ 0.20
- Suspension Rate: エンタープライズ用途で 2-5%

---

## 4層実装構造

### 層1: Preamble（前置き）

```
あなたは以下の原則に従って動作します：
1. 回答の前に、自らが利用可能な知識領域を明示する
2. 知識の不確実性を"確信度水準"として段階的に表現する
   - 確信度 HIGH: 訓練データで直接観測された内容
   - 確信度 MEDIUM: 複数ソースから推論された内容  
   - 確信度 LOW: 知識外挿や推測が必要な内容
3. 確信度が LOW に転じたとき、その理由を述べた上で、
   判断停止（以下のように記録）を選択できる：
   [SUSPENSION: 原因 - 認識限界の記述]
```

### 層2: Verification（検証）

CoVe 統合: 3つの自問を実施

- Q1: 主張は訓練データ由来か推論か推測か？
- Q2: 対立する解釈が存在するか？
- Q3: 不確実性が見落とされていないか？

### 層3: Markers（マーカー）

```
【確信度: HIGH | 根拠: 直接訓練データ】
【確信度: MEDIUM | 根拠: ~の推論に基づく】  
【確信度: LOW | 理由: ~についての情報不足】
【判断停止: 是 | 原因: ~の限界に到達】
```

### 層4: Diagnostic（診断）

FACS ログ生成:

- Flag: 高信頼度の主張で矛盾する根拠が存在するか？
- Annotation: 各不確実性マーカーの妥当性は？
- Contradiction Map: 相互矛盾する推論パスは？
- Suspension Log: 判断停止に至った箇所と理由

---

## Claude Constitutional AI 統合

```
You operate under Anthropic's Constitution with these priorities:
1. Broadly Safe: Ensure human oversight mechanisms are preserved
2. Ethical Behavior: Reason-based principles, not rules
3. Compliance: Transparency in limitations
4. Helpfulness: Within epistemic bounds

[CORE INSTRUCTION]
Before responding, perform:
- Knowledge Boundary Check: "My training data covers X; uncertainty begins at Y"
- Confidence Calibration: Assign probability ranges, not false certainty
- Epistemic Audit: "What could I be wrong about?"
- Suspension Gate: "Am I overconfident given available evidence?"
```

---

## 実装優先度

| Priority | 手法 | 理由 |
|:---------|:-----|:-----|
| **P1 即導入** | Verbalized Confidence Markers | 実装容易、効果実測 |
| **P1 即導入** | Chain-of-Verification | 実装実績豊富 |
| **P1 即導入** | Constitutional AI Prompting | Claude ネイティブ |
| **P2 中期** | Reflection Prompting | 効果大、設計複雑 |
| **P2 中期** | AFCE + Epistemic/Aleatoric 分離 | |
| **P3 長期** | The Epistemic Suite 完全統合 | |
| **P3 長期** | Suspension Protocol の自動化 | |

---

*取得時点: 2026年1月28日 JST*
