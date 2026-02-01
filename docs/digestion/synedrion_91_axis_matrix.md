# Jules Synedrion 完全評価軸マトリックス

> **Generated**: 2026-02-01 10:42 JST
> **Source**: 503 PRs from Jules Synedrion
> **Purpose**: 91種類の評価軸の完全カタログ

---

## 📊 評価軸サマリー

| カテゴリ | コード範囲 | 軸数 | 説明 |
|:---------|:-----------|:----:|:-----|
| AI-Risk | AI-001〜AI-022 | 22 | AI 生成コードのリスク |
| Async | AS-001〜AS-012 | 12 | 非同期処理の品質 |
| CognitiveLoad | CL-001〜CL-015 | 15 | 認知負荷/可読性 |
| EmotionalSocial | ES-001〜ES-018 | 18 | チーム協力/心理的安全 |
| Theory | TH-001〜TH-016 | 16 | FEP/ストア派理論 |
| Aesthetics | AE-001〜AE-008 | 8 | コード美学 |
| **Total** | | **91** | |

---

## 🎯 カテゴリ別詳細

### AI-Risk (22軸)

AI 生成コードに特有のリスクパターンを検出。

| Code | 名称 | Hegemonikón 対応 |
|:-----|:-----|:-----------------|
| AI-001 | Naming Hallucination | A2 Krisis |
| AI-002 | Mapping Hallucination | A2 Krisis |
| AI-003 | Resource Hallucination | A2 Krisis |
| AI-004 | Logic Hallucination | A2 Krisis |
| AI-005 | Incomplete Code | S3 Stathmos |
| AI-006 | DRY Violation | S3 Stathmos |
| AI-007 | Pattern Inconsistency | AE-004 |
| AI-008 | Self-Contradiction | A2 Krisis |
| AI-009 | Security Vulnerabilities | Safety |
| AI-010 | Input Validation | Safety |
| AI-011 | Over-Optimization | S1 Metron |
| AI-012 | Context Loss | O1 Noēsis |
| AI-013 | Style Inconsistency | AE-004 |
| AI-014 | Excessive Comment | AE-002 |
| AI-015 | Copy-Paste Trace | AI-006 |
| AI-016 | Dead Code | S3 Stathmos |
| AI-017 | Magic Number | S3 Stathmos |
| AI-018 | Hardcoded Path | P1 Khōra |
| AI-019 | Implicit Type Conversion | Safety |
| AI-020 | Exception Swallowing | Safety |
| AI-021 | Resource Leak | Safety |
| AI-022 | Race Condition | Safety |

---

### Async (12軸)

非同期処理の正確性と効率性を評価。

| Code | 名称 | Hegemonikón 対応 |
|:-----|:-----|:-----------------|
| AS-001 | Event Loop Blocking | S4 Praxis |
| AS-002 | Orphaned Task | S4 Praxis |
| AS-003 | Cancellation Handling | S4 Praxis |
| AS-004 | Resource Management | Safety |
| AS-005 | Gather Limit | S1 Metron |
| AS-006 | Timeout Setting | K2 Chronos |
| AS-007 | Retry Logic | S4 Praxis |
| AS-008 | Connection Pool | S4 Praxis |
| AS-009 | TaskGroup Usage | S4 Praxis |
| AS-010 | Signal Handling | Safety |
| AS-011 | Async Iterator | S4 Praxis |
| AS-012 | Lock Contention | Safety |

---

### CognitiveLoad (15軸)

コードの理解しやすさと認知負荷を評価。

| Code | 名称 | Hegemonikón 対応 |
|:-----|:-----|:-----------------|
| CL-001 | Variable Scope | S1 Metron |
| CL-002 | Abstraction Layer | S2 Mekhanē |
| CL-003 | Mental Model Hole | O1 Noēsis |
| CL-004 | Chunking Efficiency | S1 Metron |
| CL-005 | Prior Knowledge | A4 Epistēmē |
| CL-006 | Temporary Variable Load | S1 Metron |
| CL-007 | Nesting Depth | S1 Metron |
| CL-008 | Code Density | S1 Metron |
| CL-009 | Pattern Recognition | O1 Noēsis |
| CL-010 | Domain Concept | A4 Epistēmē |
| CL-011 | Cognitive Walkthrough | O1 Noēsis |
| CL-012 | Context Switch | K2 Chronos |
| CL-013 | Error Handling Consistency | S3 Stathmos |
| CL-014 | Naming Convention | AE-001 |
| CL-015 | Comment Quality | AE-002 |

---

### EmotionalSocial (18軸)

チーム協力と心理的安全性を評価。

| Code | 名称 | Hegemonikón 対応 |
|:-----|:-----|:-----------------|
| ES-001 | Review Bias | A2 Krisis |
| ES-002 | Code Review Tone | H3 Orexis |
| ES-003 | Team Cooperation | H3 Orexis |
| ES-004 | Newcomer Friendliness | H3 Orexis |
| ES-005 | Emotional Messages | H1 Propatheia |
| ES-006 | Document Affinity | A4 Epistēmē |
| ES-007 | Change History Transparency | S3 Stathmos |
| ES-008 | Responsibility Boundary | P1 Khōra |
| ES-009 | Collaboration Barrier | H3 Orexis |
| ES-010 | Knowledge Transferability | A4 Epistēmē |
| ES-011 | Burnout Risk | H3 Orexis |
| ES-012 | Pair Programming Suitability | H3 Orexis |
| ES-013 | Async Collaboration | H3 Orexis |
| ES-014 | Diversity and Inclusion | H3 Orexis |
| ES-015 | Onboarding Barrier | H3 Orexis |
| ES-016 | Review Fatigue | H3 Orexis |
| ES-017 | Technical Discussion Quality | A4 Epistēmē |
| ES-018 | Approval Bias | A2 Krisis |

---

### Theory (16軸)

FEP/ストア派理論への準拠を評価。

| Code | 名称 | Hegemonikón 対応 |
|:-----|:-----|:-----------------|
| TH-001 | Predictive Error Bug | Axiom 1 (FEP) |
| TH-002 | Belief State Consistency | H4 Doxa |
| TH-003 | Markov Blanket | Axiom 2 |
| TH-004 | Dichotomy of Control | Axiom 5 (Stoic) |
| TH-005 | Causal Structure Transparency | X12 |
| TH-006 | Self-Evidence | A4 Epistēmē |
| TH-007 | Active Inference Pattern | Axiom 1 (FEP) |
| TH-008 | Variational Free Energy | Axiom 1 (FEP) |
| TH-009 | Hierarchical Predictive | O1 Noēsis |
| TH-010 | Stoic Normative | Axiom 5 (Stoic) |
| TH-011 | JTB Knowledge | A4 Epistēmē |
| TH-012 | Epistemic Humility | H2 Pistis |
| TH-013 | CMoC Suitability | Axiom 6 (CMoC) |
| TH-014 | Teleological Consistency | K3 Telos |
| TH-015 | System Boundary | P1 Khōra |
| TH-016 | Homeostasis | Axiom 3 |

---

### Aesthetics (8軸)

コードの美学と一貫性を評価。

| Code | 名称 | Hegemonikón 対応 |
|:-----|:-----|:-----------------|
| AE-001 | Import Order | S3 Stathmos |
| AE-002 | Comment Quality | A4 Epistēmē |
| AE-003 | Error Message Clarity | H3 Orexis |
| AE-004 | Format Consistency | S3 Stathmos |
| AE-005 | Document Structure | A4 Epistēmē |
| AE-006 | Metaphor Consistency | A4 Epistēmē |
| AE-007 | Visual Rhythm | S1 Metron |
| AE-008 | Simplicity | S1 Metron |

---

## 📐 CCL 統合サマリー

```ccl
# 完全監査（91軸すべて）
/dia --mode=synedrion-full

# カテゴリ別監査
/dia --mode=ai-risk      # 22軸
/dia --mode=async        # 12軸
/dia --mode=cognitive    # 15軸
/dia --mode=social       # 18軸
/dia --mode=theory       # 16軸
/dia --mode=aesthetics   # 8軸

# 重点監査（Critical + High のみ）
/dia --mode=critical     # 約30軸
```

---

## 🔗 91軸と Hegemonikón 24定理の対応

| Hegemonikón | 関連軸数 | 主要軸 |
|:------------|:--------:|:-------|
| O1 Noēsis | 5 | CL-003, CL-009, CL-011, AI-012, TH-009 |
| A2 Krisis | 6 | AI-001〜AI-004, AI-008, ES-001, ES-018 |
| A4 Epistēmē | 8 | CL-005, CL-010, ES-006, ES-010, ES-017, TH-006, TH-011, AE-002/005/006 |
| H3 Orexis | 12 | ES-002〜ES-016 (大部分) |
| S1 Metron | 7 | CL-001, CL-004, CL-006〜CL-008, AI-011, AE-007/008 |
| S3 Stathmos | 6 | AI-005, AI-006, AI-016, AI-017, ES-007, AE-001/004 |
| S4 Praxis | 8 | AS-001〜AS-003, AS-007〜AS-009, AS-011 |
| Safety | 8 | AI-009, AI-010, AI-019〜AI-022, AS-004, AS-010, AS-012 |
| K2 Chronos | 2 | AS-006, CL-012 |
| K3 Telos | 1 | TH-014 |
| P1 Khōra | 3 | AI-018, ES-008, TH-015 |
| Axioms | 8 | TH-001〜TH-004, TH-007, TH-008, TH-010, TH-013, TH-016 |

---

*Complete 91-Axis Taxonomy extracted from 503 Jules Synedrion PRs*
