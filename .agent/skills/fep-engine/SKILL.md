---
name: FEP Cognitive Engine
description: FEP (自由エネルギー原理) に基づく認知評価・意思決定エンジン
triggers:
  - "FEP"
  - "自由エネルギー"
  - "認知"
  - "意思決定"
  - "予測誤差"
  - "能動推論"
  - "active inference"
  - "EFE"
  - "パイプライン"
  - "attractor"
  - "series"
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "none"
fallbacks:
  - "manual"
---

# FEP Cognitive Engine

> **目的**: 自由エネルギー原理に基づく認知評価と意思決定。
> CCL 式から Series 識別 → PW 解決 → Cone 構築の全パイプラインを実行。

## 発動条件

- CCL 式の認知評価が必要な時
- 意思決定の根拠を FEP で説明する時
- Agent の行動選択を Active Inference で評価する時

## 手順

### Step 1: FEP パイプライン実行

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.pipeline import run_pipeline
result = run_pipeline('CCL_EXPRESSION', force_cpu=True, use_gnosis=False)
print(result.summary())
"
```

> ⚠️ `CCL_EXPRESSION` を実際の CCL 式に置換。例: `/dia+~*/noe`

### Step 2: SeriesAttractor による Series 識別

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.attractor import SeriesAttractor
attractor = SeriesAttractor()
result = attractor.classify('INPUT_TEXT')
print(f'Series: {result.series}')
print(f'Oscillation: {result.oscillation}')
print(f'Similarity: {result.similarity:.3f}')
"
```

> ⚠️ `INPUT_TEXT` を入力テキストに置換。

### Step 3: FEP Agent v2 で行動説明

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
agent = HegemonikónFEPAgentV2()
agent.observe('OBSERVATION_TEXT')
action = agent.act()
explanation = agent.explain()
print(f'Action: {action}')
print(f'Explanation: {explanation}')
"
```

### Step 4: Attractor Advisor で WF 推薦

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.attractor_advisor import AttractorAdvisor
advisor = AttractorAdvisor()
rec = advisor.recommend('INPUT_TEXT')
llm_fmt = advisor.format_for_llm('INPUT_TEXT')
print(llm_fmt)
"
```

---

*v1.1 — import パス検証済み (2026-02-08)*
