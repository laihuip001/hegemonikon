# Synteleia Phase 5' — 6軸エージェント完備

## 目標

1軸1エージェントの**正規化された6軸モデル**を完成させ、外積モードの土台を固める。

---

## 現状分析

### Poiēsis 層 (O, S, H) — 3エージェント ✅

| 軸 | エージェント | 役割 |
|:---|:-------------|:-----|
| O | OusiaAgent | 本質・存在 |
| S | SchemaAgent | 構造・設計 |
| H | HormeAgent | 動機・意図 |

### Dokimasia 層 (P, K, A) — 現在5エージェント ⚠️

| 軸 | エージェント | 役割 |
|:---|:-------------|:-----|
| P | PerigrapheAgent | 境界・スコープ |
| K | KairosAgent | 時宜・タイミング |
| **A** | OperatorAgent | 演算子理解 (A2.lex) |
| **A** | LogicAgent | 論理矛盾 (A2.ration) |
| **A** | CompletenessAgent | 完全性 (A2.epo) |

**問題**: A 軸に 3 サブエージェントが分散 → 1軸1エージェントの原則に違反

---

## 提案: AkribeiaAgent (統合)

### [NEW] akribeia_agent.py

A 軸の3エージェントを統合する**ファサード**:

```python
class AkribeiaAgent(AuditAgent):
    """精度・判定統合エージェント (A2 Krisis)"""
    
    name = "AkribeiaAgent"
    description = "記号理解・論理矛盾・完全性を統合検証"
    
    def __init__(self):
        self.sub_agents = [
            OperatorAgent(),
            LogicAgent(),
            CompletenessAgent(),
        ]
    
    def audit(self, target: AuditTarget) -> AgentResult:
        # 全サブエージェントの結果を集約
        all_issues = []
        for agent in self.sub_agents:
            if agent.supports(target.target_type):
                result = agent.audit(target)
                all_issues.extend(result.issues)
        
        return AgentResult(
            agent_name=self.name,
            passed=...,
            issues=all_issues,
            confidence=0.85,
        )
```

### [MODIFY] orchestrator.py

`dokimasia_agents` を P, K, A の 3 に正規化:

```diff
- from .dokimasia import (
-     PerigrapheAgent, KairosAgent, 
-     OperatorAgent, LogicAgent, CompletenessAgent
- )
+ from .dokimasia import PerigrapheAgent, KairosAgent, AkribeiaAgent

- self.dokimasia_agents = [
-     PerigrapheAgent(), KairosAgent(),
-     OperatorAgent(), LogicAgent(), CompletenessAgent()
- ]
+ self.dokimasia_agents = [
+     PerigrapheAgent(), KairosAgent(), AkribeiaAgent()
+ ]
```

---

## TDD サイクル

| Test | 内容 |
|:-----|:-----|
| `test_akribeia_init` | 3 サブエージェント初期化 |
| `test_akribeia_audit` | 統合監査結果 |
| `test_6axis_structure` | 3+3=6 エージェント |

---

## 効果

| Before | After |
|:-------|:------|
| 3 + 5 = 8 | 3 + 3 = **6** |
| A 軸分散 | A 軸統合 |
| 外積困難 | 外積可能 (3×3) |
