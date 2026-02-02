# Prompt Engineering Literacy & Action Mechanisms (A3-PE)

This document codifies the "教養" (literacy) of prompt engineering within the Hegemonikón framework, specifically focusing on instruction mechanisms, verb taxonomy, and naturalized ideation techniques.

## 1. Instruction Mechanisms: "Teach" (教えて) vs. "Think" (考えて)

The shift from simple information retrieval to deep reasoning is controlled by the semantic framing of the prompt.

| Instruction | Mental Mode | Mechanism (Active Inference) | Output Characteristics |
|:---|:---|:---|:---|
| **"Tell" (教えて)** | **Retrieval** | Minimizes prediction error by fetching existing high-precision data. | Factual, concise, conclusion-first. |
| **"Think" (考えて)** | **Generation** | Induces self-correction loops (CoT) to explore state space. | Process-oriented, multi-perspective. |

### Action Mechanisms (作用機序)

- **Precision Shifting**: "Think" instructions lower the precision of immediate responses, forcing a search for deeper coherence (System 2 thinking).
- **Token Probability**: "Think" increases the probability of analytical connectors (e.g., "however," "if we consider").
- **Priors Calibration**: Advanced prompt patterns function as a "Precision Filter" (A-Series weighting).

## 2. Instruction Taxonomy (The Four Pillars)

The Hegemonikón framework classifies instructions into four cognitive modes, mapped to theorem layers:

| Mode | Theorem | Verbs | Internal State | Output Pattern |
|:---|:---|:---|:---|:---|
| **Tell** | H4 Doxa | 教えて、説明して、定義して | Retrieval / Summarization | Conclusion-first, factual. |
| **Think** | O1 Noēsis | 考えて、分析して、推論して | Inference / Logic Search | Step-by-step, analytical. |
| **Create** | S2 Mekhanē | 作って、生成して、設計して | Generation / Composition | Creative, structural. |
| **Evaluate** | A2 Krisis | 評価して、批評して、検証して | Judgment / Auditing | Critique-focused, criteria-based. |

### Decision Matrix: "Tell" vs. "Think"

- Use **"Tell"** for factual retrieval, definitions, and summarizing large contexts.
- Use **"Think"** for problem solving, architectural design, and root cause analysis.

## 3. High-Fidelity Triggers

- **"Step-by-step" (段階的に)**: Triggers P2 Hodos (Pathways).
- **"From a different perspective" (別の視点から)**: Triggers A-Series Prism (Lateral shift).
- **"As a professional [Role]" (プロの[Role]として)**: Triggers P4 Tekhnē (Skill specialization).

## 4. A3-PE: The Literacy Skill (/gno lit)

Implemented in v6.5, `A3-PE` is a principle-extraction skill triggered by `/gno lit`. It extracts "maxims" (Gnōmai) for effective instruction.

### Sub-modes (Derivatives)

- **didact**: Educational mode teaching taxonomies.
- **feed**: Analysis of context to suggest actionable improvements.
- **mech**: Mechanism deep-dive explaining the "Why" behind success.

## 5. Naturalized Ideation Techniques (AI Zen Integration)

Key ideation frameworks from "AI Zen" are recast as Hegemonikón Theorem Modes.

### 5.1 Concretization (6W3H)

Trigger: `/bou` (Phase 4.5).

- What, Why, Who, Whom, Where, When, How, How Much, How Many.

### 5.2 Strategic Blueprinting (Lean Canvas)

Trigger: `/s` (Stage 3).

- Specialized for business and project modeling.

### 5.3 Divergence Modes

Trigger: `/noe` (Phase 2).

- **Analogy**: Natural metaphors.
- **10x**: Moonshot goal scaling.
- **Gap**: Intentional imperfection/MVP.
- **Art**: Aesthetic/Symbolic shifting.
- **Random**: Stochastic combination.
- **Alien**: Cross-domain paradigm shifts.

## 6. Principles of Prompt Literacy (A3 Gnōmē)

1. **Law of Cognitive Mode**: The verb determines the LLM's "Retrieval vs. Search" weighting.
2. **Law of Explicit Logic**: Forcing intermediate reasoning (CoT) acts as a physical pathway for logic.
3. **The Bias of Ambiguity**: Qualitative words act as "Entropy Magnifiers," causing default to least resistance.
4. **Diorthōsis (Self-Correction)**: Literate prompts include verification instructions (Krisis) to catch divergence.
5. **Semantic Distinction (Literal vs. Metaphorical)**: 「これは比喩である」と「これは実証されたメカニズムである」を明確に区別せよ。比喩は認識の足場（Scaffolding）として、メカニズムは実行の骨格（Skeleton）として使い分けることで、プロンプトの解像度を制御する。
6. **Internalized Aesthetic Principle**: 強制的な規則（Rules.md）による束縛よりも、システムとの「対話の美しさ」を重視せよ。意味的な必然性から立ち上がる自発的な発動こそが、真の洗練（Catharsis）をもたらす。

---
*Codified: 2026-02-01 | A3-PE Standard v6.6*
