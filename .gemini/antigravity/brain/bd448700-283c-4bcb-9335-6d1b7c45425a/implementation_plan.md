# Implementation Plan: pymdp × Hegemonikón 統合 (v2.0)

> **目的**: FEP の数学的基盤を「認知層」として実装
> **優先度**: /bou で決定した最優先事項 (Priority 1)
> **信頼度**: 78% (/noe 分析結果)

---

## アーキテクチャ決定 (/noe 分析結果)

> **核心洞察**: pymdp を「認知層」として LLM の上位に配置する

```
┌─────────────────────────────────────────────┐
│  Cognitive Layer (pymdp)                    │
│  - 信念推論 (infer_states)                  │
│  - ポリシー選択 (infer_policies)            │
│  - 行動決定 (sample_action)                 │
├─────────────────────────────────────────────┤
│  Neural Renderer (LLM)                      │
│  - テキスト生成                             │
│  - 自然言語処理                             │
└─────────────────────────────────────────────┘
```

これは STOIC の「Cognitive Substrate」パターンと同じ構造。

---

## 概要

pymdp の Agent API を Hegemonikón のワークフローにマッピングし、Active Inference の数学的プロセスを実装する。

---

## 概念マッピング

| pymdp API | Hegemonikón ワークフロー | FEP 概念 |
|:----------|:----------------------|:---------|
| `Agent.infer_states(obs)` | `/noe` (Noēsis) | Variational FE 最小化 |
| `Agent.infer_policies()` | `/bou` (Boulēsis) | Expected FE 計算 |
| `Agent.sample_action()` | `/ene` (Energeia) | 行動選択 |

---

## Phase 1: PoC 設計 (今セッション)

### 1.1 pymdp インストール確認

```bash
pip install inferactively-pymdp
```

### 1.2 最小限の Agent 実装

```python
# hegemonikon/mekhane/fep/active_inference_agent.py

from pymdp import utils
from pymdp.agent import Agent

class HegemonikónAgent:
    """FEP-based cognitive agent for Hegemonikón"""
    
    def __init__(self, num_states: list, num_obs: list, num_controls: list):
        A = utils.random_A_matrix(num_obs, num_states)
        B = utils.random_B_matrix(num_states, num_controls)
        C = utils.obj_array_uniform(num_obs)
        
        self.agent = Agent(A=A, B=B, C=C)
    
    def noesis(self, observation: list) -> dict:
        """O1 Noēsis: 信念推論 (infer_states)"""
        qs = self.agent.infer_states(observation)
        return {"beliefs": qs, "status": "inferred"}
    
    def boulesis(self) -> dict:
        """O2 Boulēsis: ポリシー推論 (infer_policies)"""
        q_pi, neg_efe = self.agent.infer_policies()
        return {"policy_posterior": q_pi, "expected_free_energy": -neg_efe}
    
    def energeia(self) -> int:
        """O4 Energeia: 行動選択 (sample_action)"""
        action = self.agent.sample_action()
        return int(action[0])  # First control factor
```

---

## Phase 2: /noe 統合 (次回セッション)

### 2.1 SKILL.md への参照追加

```markdown
## FEP Implementation

このスキルは pymdp の `infer_states()` を内部的に使用し、
観察から信念を推論する。

```python
agent.noesis(observation)  # → beliefs over hidden states
```

```

### 2.2 ワークフローへの統合

`mekhane/anamnesis/` または新規 `mekhane/fep/` ディレクトリに配置。

---

## Phase 3: STOIC 効率性パターン適用 (中期)

### 3.1 認知処理の外部化

STOIC の「Cognitive Substrate」パターンを参考に、LLM の推論を pymdp Agent に委譲する設計を検討。

### 3.2 期待される効果

- 小さなモデルでも深い推論が可能
- 再現可能な認知処理

---

## Proposed Changes

### [NEW] [active_inference_agent.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/fep/active_inference_agent.py)

最小限の pymdp ラッパークラスを実装。

### [MODIFY] [requirements.txt](file:///home/makaron8426/oikos/hegemonikon/requirements.txt)

`inferactively-pymdp` 依存関係を追加。

---

## Verification Plan

### Automated Tests

```bash
# pymdp インストール確認
pip install inferactively-pymdp
python -c "from pymdp.agent import Agent; print('OK')"

# PoC 動作確認
cd /home/makaron8426/oikos/hegemonikon
python -m pytest mekhane/fep/test_active_inference.py -v
```

### Manual Verification

1. `HegemonikónAgent` を初期化
2. ランダム観察を与えて `noesis()` を呼び出し
3. `boulesis()` でポリシー推論
4. `energeia()` で行動選択
5. 各ステップの出力がエラーなく返ることを確認

---

## リスク

| リスク | 対策 |
|:-------|:-----|
| pymdp が離散状態空間限定 | 連続環境は将来の拡張課題 |
| NumPy 依存による性能 | JAX 版 (v1.0.0-alpha) を注視 |
| 学習曲線 | ドキュメントを先に精読 |

---

*Created: 2026-01-28 / Priority: /bou Phase 5*
