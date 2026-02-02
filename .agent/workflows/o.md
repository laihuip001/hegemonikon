---
description: O-series 4項振動。認識↔意志↔探求↔行為を巡回する純粋認知サイクル。
hegemonikon: Ousia
modules: [O1, O2, O3, O4]
skill_ref:
  - ".agent/skills/ousia/o1-noesis/SKILL.md"
  - ".agent/skills/ousia/o2-boulesis/SKILL.md"
  - ".agent/skills/ousia/o3-zetesis/SKILL.md"
  - ".agent/skills/ousia/o4-energeia/SKILL.md"
version: "3.1"
lineage: "v3.0 (4項振動) + SEL 統合 → v3.1"
derivatives:
  O1: [nous, phro, meta]
  O2: [desir, voli, akra]
  O3: [anom, hypo, eval]
  O4: [flow, prax, pois]
cognitive_algebra:
  definition: "/o = /noe~bou~zet~ene (4項振動)"
  operators:
    "+": "全4定理を詳細モードで順次実行"
    "-": "全4定理を縮約モードで順次実行"
    "*": "O-series 自体を問う: なぜ純粋認知層か"
sel_enforcement:
  "+":
    description: "MUST execute ALL 4 theorems in detailed mode"
    minimum_requirements:
      - "全4定理実行"
      - "各定理詳細モード"
  "-":
    description: "MAY execute all 4 theorems in condensed mode"
    minimum_requirements:
      - "サマリーのみ"
  "*":
    description: "MUST meta-analyze: why use pure cognition layer?"
    minimum_requirements:
      - "認知層選択の理由を問う"
ccl_signature: "/o+*dia"
---

# /o ワークフロー — O-series 4項振動

> **定義**: `/o` = `/noe~bou~zet~ene`
> **意味**: 認識 ↔ 意志 ↔ 探求 ↔ 行為 を巡回する純粋認知サイクル

---

## 本質

```
/o = O1 → O2 → O3 → O4 → O1' → O2' → ...
   = 認識 → 意志 → 探求 → 行為 → 認識' → ...
```

**4項振動**とは、O-series の4定理を順に巡回し、深化させていくこと。

---

## 使用法

### 基本呼び出し（4項振動開始）

```
/o
```

→ O1 Noēsis から開始し、O2 → O3 → O4 → O1' と巡回

### Series間振動

```
/o~k   → O-series ↔ K-series 間を振動
/o~s   → O-series ↔ S-series 間を振動
```

### 演算子適用

```
/o+    → 全4定理を詳細モードで順次実行
/o-    → 全4定理を縮約モードで順次実行
/o*    → 「なぜ O-series を使うか」を問う
```

### 個別定理への直接アクセス

```
/noe   → O1 Noēsis 単体
/bou   → O2 Boulēsis 単体
/zet   → O3 Zētēsis 単体
/ene   → O4 Energeia 単体
```

### 派生直接指定（手動オーバーライド）

```
/o nous  → O1派生: 本質直観（抽象的原理把握）
/o phro  → O1派生: 実践的判断（文脈依存）
/o meta  → O1派生: メタ認識（反省・信頼度評価）

/o desir → O2派生: 第一次欲動（望むこと）
/o voli  → O2派生: 第二次意志（統合）
/o akra  → O2派生: 意志-行為乖離（克服）

/o anom  → O3派生: 異常認識（問題化）
/o hypo  → O3派生: 仮説生成（創造的推測）
/o eval  → O3派生: 仮説評価（優先順位）

/o flow  → O4派生: Flow状態（没入）
/o prax  → O4派生: 自己目的的行為
/o pois  → O4派生: 産出活動（成果物）
```

---

## 派生マトリックス

| 定理 | 派生1 | 派生2 | 派生3 |
|:-----|:------|:------|:------|
| **O1 Noēsis** | `nous` 本質直観 | `phro` 実践判断 | `meta` メタ認識 |
| **O2 Boulēsis** | `desir` 第一次欲動 | `voli` 第二次意志 | `akra` 意志乖離 |
| **O3 Zētēsis** | `anom` 異常認識 | `hypo` 仮説生成 | `eval` 仮説評価 |
| **O4 Energeia** | `flow` Flow状態 | `prax` 自己目的行為 | `pois` 産出活動 |

**合計**: 12派生

---

## 各定理の概要

### O1 Noēsis（Νόησις / 認識）

**問い**: 「何を認識すべきか？」「本質は何か？」

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **nous** | 抽象的問題、原理探求 | Nous poietikos | 専門家直観 (System 1) |
| **phro** | 具体的状況、実践的判断 | Phronēsis | エキスパート判断・EI |
| **meta** | 反省が必要、信頼度疑問 | 自己参照的Nous | メタ認知 (pMFC/aPFC) |

→ 詳細: `/noe` または `.agent/skills/ousia/o1-noesis/SKILL.md`

### O2 Boulēsis（Βούλησις / 意志）

**問い**: 「何を望むか？」「どの欲動を有効にするか？」

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **desir** | 明確な望み、欲動表出 | Boulēsis基層 | Implicit wants |
| **voli** | 葛藤解決、意志統合 | Frankfurt階層意志 | Executive function |
| **akra** | 意志-行為乖離 | Akrasia理論 | Implementation intention |

→ 詳細: `/bou` または `.agent/skills/ousia/o2-boulesis/SKILL.md`

### O3 Zētēsis（Ζήτησις / 探求）

**問い**: 「何を問うべきか？」「どの仮説を追求するか？」

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **anom** | 異常・驚き、問題化 | Diaporesis | Curiosity gap |
| **hypo** | 仮説が必要、創造的推測 | Peirce Abduction Ph.1 | Generative reasoning |
| **eval** | 複数候補、評価・選別 | Peirce Abduction Ph.2 | IBE, pursuitworthiness |

→ 詳細: `/zet` または `.agent/skills/ousia/o3-zetesis/SKILL.md`

### O4 Energeia（Ἐνέργεια / 活動）

**問い**: 「どう活動するか？」「何を実現するか？」

| 派生 | 適用場面 | 古典根拠 | 現代対応 |
|:-----|:---------|:---------|:---------|
| **flow** | 没入・最適経験 | Energeia自己目的性 | Csikszentmihalyi Flow |
| **prax** | 行為自体が目的 | Praxis | Intrinsic motivation |
| **pois** | 外部成果物産出 | Poiesis | Craftsmanship |

→ 詳細: `/ene` または `.agent/skills/ousia/o4-energeia/SKILL.md`

---

## FEP 派生選択

各ワークフロー（`/noe`, `/bou`, `/zet`, `/ene`）呼び出し時、FEP Cognitive Layer が状況を分析し、最適な派生を推奨する。

```python
from mekhane.fep.derivative_selector import select_derivative

result = select_derivative(
    theorem="O1",
    problem_context="ユーザー入力テキスト"
)
# → DerivativeRecommendation(
#     theorem="O1",
#     derivative="phro",
#     confidence=0.75,
#     rationale="文脈依存度が高く、実践的判断が適切"
# )
```

### 手動オーバーライド

自動選択を上書きしたい場合：

```
/noe --derivative=nous   # 強制的に nous モードで実行
/bou --derivative=akra   # 強制的に akra モードで実行
```

---

## X-series 連携

O-series 実行後、X-series により次のステップが推奨される：

| 現在 | 推奨先 | 理由 |
|:-----|:-------|:-----|
| O1 Noēsis | S1 Metron | 認識後にスケール決定 |
| O2 Boulēsis | S2 Mekhanē | 意志後に方法配置 |
| O3 Zētēsis | K4 Sophia | 問い発見後に外部調査 |
| O4 Energeia | H4 Doxa | 活動後に記録・永続化 |

---

## 理論的背景

### 古典哲学（60%）

- **Aristotle**: Nous（理性的認識）、Phronēsis（実践的叡智）
- **Stoic**: Hegemonikon（支配的理性）、Ousia（本質）
- **Husserl**: Noēsis-Noēma 相関構造
- **Frankfurt**: 階層的意志論
- **Peirce**: Abductive Logic

### 現代認知科学（40%）

- **Kahneman**: Dual-process theory (System 1/System 2)
- **Csikszentmihalyi**: Flow theory
- **Friston**: Free Energy Principle, Active Inference
- **Metacognition**: pMFC/aPFC 監視・調整

---

## 派生消化パターン

> この設計は「派生消化パターン v1.0」として他のシリーズ（S, H, P, K, A）にも適用可能

1. **Hub作成**: `/[series].md` で定理群と派生を一覧化
2. **Phase追加**: 既存ワークフローに派生Phaseを追加
3. **FEP統合**: `derivative_selector.py` で状況に応じた派生選択

---

*v2.0 — 12派生統合Hub (2026-01-29)*
