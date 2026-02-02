# FEP Persistence & Auto-Epochē 実装計画 v2

> **Goal 1**: A行列 Dirichlet 学習を `/bye` で保存、`/boot` で読込
> **Goal 2**: 高エントロピー時に自動 `/epo` 推奨

---

## /noe 発見: 重大な不備

| 問題 | 影響 | 解決策 |
|:-----|:-----|:-------|
| FEP インスタンスはワークフローごとに新規生成 | 学習が蓄積されない | ファイルを介して状態共有 |
| `update_A_dirichlet()` の呼び出しが未定義 | A行列が更新されない | ヘルパー関数で一連の処理を実行 |

---

## STAGE 0: Blindspot + Scale

| カテゴリ | リスク | 解決策 |
|:---------|:-------|:-------|
| Dependencies | **高 → 解決** | `run_fep_with_learning()` で状態管理 |
| Scope | 中 | encoding.py + SKILL.md のみ変更 |

📏 **Scale**: Meso

---

## STAGE 1: Strategy Selection

**Explore/Exploit**: Exploit（確実性重視）

**選択**: Plan B (Robust) — ヘルパー関数で一連の処理をカプセル化

---

## STAGE 3: Blueprint

### [MODIFY] [encoding.py](file:///home/laihuip001/oikos/hegemonikon/mekhane/fep/encoding.py)

```python
def run_fep_with_learning(
    obs_tuple: Tuple[int, int, int],
    a_matrix_path: str = "/home/laihuip001/oikos/mneme/.hegemonikon/fep/learned_A.npy",
    learning_rate: float = 50.0,
) -> Dict:
    """FEP 推論 + Dirichlet 学習 + 永続化を一連で実行。
    
    処理フロー: load → step → update_A_dirichlet → save
    
    Returns:
        agent.step() の結果 + should_epoche フラグ
    """
    from mekhane.fep import HegemonikónFEPAgent
    import os
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    # 1. 学習済み A-Matrix があれば読込
    agent.load_learned_A(a_matrix_path)
    
    # 2. 推論実行
    flat_obs = obs_tuple[0] + 2 * obs_tuple[1] + obs_tuple[2]
    result = agent.step(observation=flat_obs)
    
    # 3. Dirichlet 更新
    agent.update_A_dirichlet(observation=flat_obs, learning_rate=learning_rate)
    
    # 4. 保存
    os.makedirs(os.path.dirname(a_matrix_path), exist_ok=True)
    agent.save_learned_A(a_matrix_path)
    
    # 5. Auto-Epochē フラグ
    result["should_epoche"] = result.get("entropy", 0) >= 2.0
    
    return result


def should_trigger_epoche(agent_result: Dict, threshold: float = 2.0) -> bool:
    """高エントロピー時に Epochē を推奨するか判定。"""
    return agent_result.get("entropy", 0.0) >= threshold
```

---

### [MODIFY] [o1-noesis/SKILL.md](file:///home/laihuip001/oikos/.agent/skills/ousia/o1-noesis/SKILL.md)

FEP Cognitive Layer セクションの使用コードを更新:

```python
from mekhane.fep.encoding import (
    encode_noesis_output,
    run_fep_with_learning,
    generate_fep_feedback_markdown,
)

# PHASE 5 の結果から観察値を生成
obs = encode_noesis_output(
    confidence_score=phase5_result["confidence_score"],
    uncertainty_zones=phase5_result["uncertainty_zones"],
)

# FEP 推論 + 学習 + 永続化
result = run_fep_with_learning(obs)

# 出力生成
feedback = generate_fep_feedback_markdown(result, f"conf={phase5_result['confidence_score']}")
print(feedback)

# Auto-Epochē
if result["should_epoche"]:
    print("⚠️ 高エントロピー検出 → /epo を推奨")
```

---

### [DELETE] bye.md, boot.md の変更

`/bye`, `/boot` への変更は **不要** になった。
`run_fep_with_learning()` が毎回 load/save するため。

---

## Verification Plan

```bash
PYTHONPATH=. pytest tests/test_fep_agent.py -v -k "learning"
```

---

## 実装順序

1. `encoding.py` に `run_fep_with_learning()` + `should_trigger_epoche()` 追加
2. テスト追加
3. O1 Noēsis SKILL.md の FEP Cognitive Layer を更新
4. O2 Boulēsis SKILL.md も同様に更新
