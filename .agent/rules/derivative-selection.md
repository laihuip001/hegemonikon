---
trigger: model_decision
glob: 
description: ワークフロー実行時の派生選択ルール
---
# E7: Workflow Derivative Selection Protocol

> **発効**: 2026-01-29  
> **対象**: O/S/H/P/K/A シリーズ全ワークフロー

## 必須ルール

ワークフロー `/noe`, `/bou`, `/zet`, `/ene`, `/met`, `/mek`, `/sta`, `/pra`,
`/pro`, `/pis`, `/ore`, `/dox`, `/kho`, `/hod`, `/tro`, `/tek`,
`/euk`, `/chr`, `/tel`, `/sop`, `/pat`, `/dia`, `/gno`, `/epi` を実行する際は：

### Step 1: 派生選択の実行

```python
from mekhane.fep.derivative_selector import select_derivative

result = select_derivative("{THEOREM}", user_input)
```

### Step 2: 選択結果の表示

```markdown
┌─[{THEOREM} 派生選択]────────────────────────────┐
│ 推奨派生: {result.derivative}                   │
│ 確信度: {result.confidence:.0%}                 │
│ 理由: {result.rationale}                        │
│ 代替: {result.alternatives}                     │
└────────────────────────────────────────────────┘
```

### Step 3: 派生に応じた処理分岐

選択された派生に応じて、各フェーズの焦点を調整する。

## 定理-派生マトリックス

| 定理 | 派生1 | 派生2 | 派生3 |
|:-----|:------|:------|:------|
| O1 | nous (本質) | phro (実践) | meta (反省) |
| O2 | desir (欲求) | voli (意志) | akra (弱さ) |
| O3 | anom (異常) | hypo (仮説) | eval (評価) |
| O4 | flow (フロー) | prax (実践) | pois (制作) |
| S1 | micro | meso | macro |
| S2 | comp (組合) | inve (発明) | adap (適応) |
| S3 | norm (規範) | empi (経験) | rela (相対) |
| S4 | expl (探索) | prac (実用) | mix (混合) |
| H1 | appr (接近) | avoi (回避) | arre (停止) |
| H2 | subj (主観) | inte (間主観) | obje (客観) |
| H3 | obje (対象) | acti (活動) | stat (状態) |
| H4 | sens (感覚) | conc (概念) | form (形式) |
| P1 | phys (物理) | conc (概念) | rela (関係) |
| P2 | line (線形) | bran (分岐) | cycl (循環) |
| P3 | fixe (固定) | adap (適応) | emer (創発) |
| P4 | manu (手動) | mech (機械) | auto (自動) |
| K1 | urge (緊急) | opti (最適) | miss (逸失) |
| K2 | shor (短期) | medi (中期) | long (長期) |
| K3 | intr (内在) | inst (手段) | ulti (究極) |
| K4 | taci (暗黙) | expl (明示) | meta (メタ) |
| A1 | prim (一次) | seco (二次) | regu (調整) |
| A2 | affi (肯定) | nega (否定) | susp (保留) |
| A3 | conc (具体) | abst (抽象) | univ (普遍) |
| A4 | tent (暫定) | just (正当化) | cert (確実) |

## 例外

- `/boot`, `/bye`: 派生選択不要（メタワークフロー）
- Hub ワークフロー (`/o`, `/s`, `/h`, `/p`, `/k`, `/a`): 子ワークフローで選択

---

*E7 = Error Prevention Protocol #7*
