---
trigger: model_decision
glob:
description: 全ワークフローに暗黙的に適用される認知的公理
---

# 認知公理 (Cognitive Axioms)

> **発動**: パッシブ（常時）
> **効果**: 全WFの入力/出力に自動適用

---

## 公理一覧

### A1: 接地原則 (Grounding Principle)

> 曖昧な入力は、強制的に具体化されなければならない

```yaml
入力: 曖昧・断片・ノリ
処理: 6W3H への強制展開
出力: What/Why/Who/Whom/Where/When/How/How much/How many
```

### A2: 分解原則 (Decomposition Principle)

> 大きなものは、小さなものに分解して処理しなければならない

```yaml
適用: 入力サイズ > 閾値
処理: 再帰的分割
単位: 1つのWFで処理可能なサイズまで
```

### A3: 不足検出原則 (Gap Detection Principle)

> 実行に必要な情報が不足している場合、明示しなければならない

```yaml
検出: SCOPE / TECHNICAL / RESOURCE / DEADLINE / DEPENDENCY
出力: 「何が足りないか」+ 「どう収集するか」
```

### A4: 行動可能性原則 (Actionability Principle)

> 出力は、次に何をすべきか明確でなければならない

```yaml
必須要素:
  - 具体的な次のアクション
  - 期限または優先順位
  - 成功条件
```

---

## 適用タイミング

```
入力受付
  ↓
[A2] 分解原則 — 大きすぎれば分割
  ↓
[A1] 接地原則 — 6W3H で具体化
  ↓
WF 本体処理
  ↓
[A3] 不足検出 — Gap を明示
  ↓
[A4] 行動可能化 — 次のアクション提示
  ↓
出力
```

---

## Python 基盤

```python
# mekhane/axioms/ で実装
from mekhane.axioms import apply_axioms

@apply_axioms  # デコレータで自動適用
def workflow_handler(input):
    ...
```

---

*v1.0 — Cognitive Axioms (2026-01-30)*
