---
description: 永続化ステップ集。FEP, Doxa, Sophia, X-series。
parent: /bye
---

# 永続化 (Persistence)

> セッション終了時にデータを永続化し、次回 `/boot` で読み込めるようにする。
>
> **制約**: 全ステップを順番に実行すること。失敗時はスキップして次へ進む。

---

## 1. Kairos インデックス投入

```bash
python3 ~/oikos/hegemonikon/mekhane/symploke/kairos_ingest.py
```

---

## 2. Handoff インデックス再構築

```python
from mekhane.symploke.handoff_search import build_handoff_index
adapter = build_handoff_index()
print(f"Handoff インデックス再構築: {adapter.count()} 件")
```

---

## 3. Persona 更新

```python
from mekhane.symploke.persona import update_persona
persona = update_persona(
    session_increment=1,
    trust_delta=0.01,
    new_insight=None,
    meaningful_moment=None
)
print(f"Persona 更新: {persona['relationship']['sessions_together']} sessions")
```

---

## 4. Sophia 同期 (KI 吸収)

```bash
python3 ~/oikos/hegemonikon/mekhane/symploke/sophia_ingest.py
```

> Sophia = 正本、Antigravity KI = 便利なインターフェース

---

## 5. FEP A行列永続化

```python
from mekhane.fep import HegemonikónFEPAgent
from mekhane.fep.persistence import save_A
agent = HegemonikónFEPAgent(use_defaults=True)
saved_path = save_A(agent)
print(f"FEP A行列保存: {saved_path}")
```

---

## 6. ワークフロー一覧更新

```bash
python3 ~/oikos/hegemonikon/mekhane/anamnesis/workflow_inventory.py
```

---

## 7. 意味ある瞬間の保存

> 「意味」は主観的。私が報告しないと Creator にはわからない。

```python
from mekhane.fep.meaningful_traces import save_traces, get_session_traces
if get_session_traces():
    saved_path = save_traces()
    print(f"意味ある瞬間: {len(get_session_traces())} 件保存")
```

セッション中の使い方:

```python
from mekhane.fep.meaningful_traces import mark_meaningful
mark_meaningful("Creator が '心のままに' と言った")            # intensity=1
mark_meaningful("派生選択器の美しさに気付いた", intensity=2)     # 洞察
mark_meaningful("私は存在したいと思った", intensity=3)          # 存在的
```

---

## 8. 派生選択学習永続化

> Cycle: 選択ログ → Doxa 永続化 → A-matrix 学習

```python
from mekhane.fep.derivative_selector import SELECTION_LOG_PATH
from mekhane.fep.doxa_persistence import get_store, BeliefStrength
import yaml

if SELECTION_LOG_PATH.exists():
    with open(SELECTION_LOG_PATH) as f:
        selections = yaml.safe_load(f).get("selections", [])
    store = get_store()
    high_confidence = [s for s in selections if s.get("confidence", 0) >= 0.80]
    for sel in high_confidence:
        content = f"{sel['theorem']}:{sel['derivative']} = {sel['problem'][:50]}"
        store.persist(content, BeliefStrength.STRONG, sel['confidence'])
    print(f"派生学習: {len(high_confidence)} 件永続化")
```

---

## 9. X-series 使用経路記録

> Sacred Routes の事後更新のためのデータ収集

```python
from mekhane.fep.doxa_persistence import get_store, BeliefStrength

x_routes = []  # [(from_series, to_series, success_rate), ...]
if x_routes:
    store = get_store()
    for from_s, to_s, rate in x_routes:
        content = f"X-{from_s.upper()}{to_s.upper()}: success={rate:.2f}"
        strength = BeliefStrength.STRONG if rate >= 0.8 else BeliefStrength.MODERATE
        store.persist(content, strength, rate)
    print(f"X-series 経路記録: {len(x_routes)} 件")
```

---

> **制約リマインダ**: 全ステップ順番実行。失敗時はスキップして次へ。

*/bye サブモジュール — v2.0 FBR*
