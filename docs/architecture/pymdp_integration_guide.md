# pymdp-Hegemonikón 統合ガイド

> **自由エネルギー原理 (FEP) による認知エージェントの数学的基盤**

---

## 1. なぜ pymdp なのか

### Hegemonikón の課題

Hegemonikón は 60 要素の公理体系を持つが、現状は**ヒューリスティック**に依存:

| 現状 | 問題 |
|:-----|:-----|
| `/noe` の信頼度スコア | 主観的数値 (0-100) |
| `/bou` の優先順位判定 | 言語的推論のみ |
| `/ene` の行動選択 | 決定論的 |

### pymdp が解決するもの

pymdp は**数学的に正当化された**意思決定フレームワークを提供:

```
現象 → 数式 → 実装
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
不確実性 → エントロピー H(Q) → agent.infer_states()
優先度 → 期待自由エネルギー G(π) → agent.infer_policies()
行動 → 政策サンプリング → agent.sample_action()
```

---

## 2. Stoic-FEP 対応表

| ストア派概念 | FEP 数式 | pymdp メソッド | Hegemonikón |
|:-------------|:---------|:---------------|:------------|
| **Phantasia** (印象) | Prior P(s) | `D` 行列 | 初期信念 |
| **Synkatathesis** (同意) | Posterior Q(s) | `infer_states()` | O1 Noēsis |
| **Hormē** (衝動) | Action a* | `sample_action()` | O4 Energeia |
| **Prohairesis** (理性的選択) | Policy π* | `infer_policies()` | O2 Boulēsis |

---

## 3. 具体的な実用シナリオ

### シナリオ A: `/noe` の信頼度定量化

**Before (言語的)**:

```
信頼度: 75%
不確実領域: ドメイン知識
```

**After (FEP)**:

```python
result = agent.infer_states(observation)
entropy = result["entropy"]  # 1.983

# エントロピー → 信頼度変換
confidence = 1.0 - (entropy / max_entropy)  # 0.01 ~ 1.00
```

**利点**: エントロピーは観測データから**自動計算**される。主観ではない。

---

### シナリオ B: `/bou` の優先順位判定

**Before (言語的)**:

```
優先順位:
  1. pymdp 統合 — 即実行
  2. H3 更新 — 長期目標
```

**After (FEP)**:

```python
q_pi, neg_efe = agent.infer_policies()

# Expected Free Energy で順位付け
for task, policy_idx in tasks.items():
    print(f"{task}: G(π) = {-neg_efe[policy_idx]:.3f}")
```

**利点**: EFE は**探索と活用のバランス**を自動的に考慮。

---

### シナリオ C: Epochē (判断停止) の自動検出

```python
result = agent.infer_states(observation)

# 高エントロピー = 判断不能
if result["entropy"] > EPOCHĒ_THRESHOLD:
    print("⚠️ Epochē 発動: 判断を保留します")
    # /epo ワークフローを提案
```

---

## 4. 現在の制限

| 制限 | 原因 | 回避策 |
|:-----|:-----|:-------|
| pymdp 0.0.1 のみ | pip で最新版インストール不可 | 基本機能は十分 |
| 離散状態空間 | pymdp の設計 | 状態を適切に離散化 |
| LLM との直接統合なし | アーキテクチャ | Cognitive Layer で橋渡し |

---

## 5. 今後の展開

### Phase A: 即時可能

- [x] デモスクリプト完成
- [ ] `/noe` にエントロピー出力を追加
- [ ] `/bou` に EFE ランキングを追加

### Phase B: 中期

- [ ] Cognitive Layer の完全設計
- [ ] LLM 出力 → 状態空間マッピング
- [ ] 複数モダリティ対応

### Phase C: 長期

- [ ] 学習 (B 行列更新)
- [ ] 階層的生成モデル
- [ ] リアルタイム推論

---

## 6. 使用例: クイックスタート

```python
from mekhane.fep import HegemonikónFEPAgent

# 1. Agent 初期化
agent = HegemonikónFEPAgent(use_defaults=True)

# 2. O1 Noēsis: 観測から信念を推論
result = agent.infer_states(observation=1)  # clear context
print(f"MAP 状態: {result['map_state_names']}")
print(f"不確実性: {result['entropy']:.3f}")

# 3. O2 Boulēsis: ポリシー選択
q_pi, neg_efe = agent.infer_policies()
print(f"observe 確率: {q_pi[0]:.2%}")
print(f"act 確率: {q_pi[1]:.2%}")

# 4. O4 Energeia: 行動実行
action = agent.sample_action()
print(f"選択行動: {'observe' if action == 0 else 'act'}")
```

---

## 7. 結論

**pymdp は Hegemonikón に以下を提供**:

| 提供する価値 | 説明 |
|:-------------|:-----|
| **数学的正当化** | FEP に基づく理論的根拠 |
| **定量化** | エントロピー、EFE による客観的数値 |
| **自動化** | 信念更新、政策選択の自動計算 |
| **一貫性** | Stoic 哲学との形式的対応 |

> 「予測誤差最小化」という Hegemonikón の統一原理が、
> pymdp によって**計算可能な実装**となった。

---

*v1.0 — 2026-01-28*
