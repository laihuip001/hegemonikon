# Insight Promotion Protocol (v5.6)

The **Insight Promotion Protocol** defines how "Internal Gnōsis" (wisdom discovered during dialogue) is crystallized into formal Knowledge Items (KIs) or H4 Doxa beliefs.

## 1. Flow of Wisdom

1. **Mining (v5.1)**: `insight_miner.py` extracts matches via regex patterns (`gnome`, `principle`, `discovery`, `decision`).
2. **Scoring (v5.2)**: `score_insight_quality` filters noise and ranks candidates.
3. **Comprehensive Review (v5.6)**: Full 630+ insight review with tier-based classification.
4. **Promotion (v5.6)**:
    - **Tier 1 (score ≥ 0.85)**: Immediate KI integration — 19 insights.
    - **Tier 2 (score 0.7-0.84)**: Review-then-integrate — 174 insights.
    - **Tier 3 (score 0.4-0.7)**: Reference only — 270+ insights.

## 2. Selection Criteria for Promotion

| Level | Action | Criterion |
| :--- | :--- | :--- |
| **Gnome (v6.55)** | Promoted to KI | Universal truth or "Hegemonikón Axiom". (e.g., "Wash external nutrients in native theorems") |
| **Principle** | Promoted to `/doxa` | Operational rule that constrains future behavior. (e.g., "PROOF coverage must be 100%") |
| **Discovery** | Added to KI | Technical breakthrough or solution to a specific hurdle. (e.g., virtual scroll workaround) |
| **Decision** | Added to Handoff/KI | Crucial forks in project roadmaps. |

## 3. The 2026-02-01 Comprehensive Promotion

**Mining Results**:

- **Total Extracted**: 536 insights (463 from conversation logs + 73 from Handoffs)
- **Tier 1 (Immediate)**: 19 insights
- **Tier 2 (Review)**: 174 insights
- **Tier 3 (Reference)**: 343 insights

**Initial Assessment Error**: The first pass only promoted 6 insights (1.1% of total). Creator's challenge "6件だけで良いの？" triggered comprehensive re-mining.

**Key Insights Promoted** (2026-02-01):

| # | Insight | KI Updated |
|:--|:--------|:-----------|
| 1 | 「削減」と「洗練」は違う。洗練とは、必然的な構造を発見すること。 | Quality Standards ✅ |
| 2 | 「どう書くか」より「何が必然か」。 | Quality Standards ✅ |
| 3 | 「どんな仕組みも形骸化する」 | Quality Standards ✅ |
| 4 | 証明の深さ ∝ ファイルの「存在責任」の重さ | Quality Standards ✅ |
| 5 | 三層構造 (Skeleton/Flesh/Interface) | CCL System ✅ |
| 6 | Hegemonikón は Creator の認知を FEP 的に外在化・最適化するシミュレーション環境 | Active Inference ✅ |

## 4. Promotion Mechanics

To promote an insight:

1. **Tag as KI Candidate**: Include in the `/bye` handoff's "Insight Report" section.
2. **Artifact Generation**: The Background Agent (or the AI in next session) converts candidates into markdown artifacts within the appropriate KI directory.
3. **Metadata Update**: The KI's `metadata.json` is updated with a reference to the source conversation.

## 5. Anti-Lazy Principle (v5.6)

> **"6件だけで良いの？" — 怠惰は禁止**

- Full insight mining is **mandatory** at least once per week.
- Promotion thresholds must be explicit (score ≥ 0.85 for Tier 1).
- 1% promotion rate is a red flag; target is 3-5% of extracted insights.

---
*Codified: 2026-02-01 | Series: Anamnēsis / Quality Engineering*
*Updated: 2026-02-01 v5.6 — Comprehensive Mining Integration*
