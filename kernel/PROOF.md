# PROOF.md — 存在証明書

REASON: 予測誤差最小化の公理に基づき、不変の法則を保護するための分離された場所が必要となった。  <!-- AUTO-REASON -->

> **∃ kernel/** — この場所は存在しなければならない

---

## 公理

```
A0: 予測誤差最小化 (Free Energy Principle)
```

---

## 演繹

```
A0: 予測誤差最小化
  ↓ [FEP の定義]
P1: システムは内部モデルを持つ
  ↓ [内部モデルの性質]
P2: 内部モデルには不変の法則がある
  ↓ [不変性の要件]
P3: 不変の法則は変更から保護される必要がある
  ↓ [保護の手段]
P4: 保護には分離された場所が必要
  ↓ [名前の必然性]
P5: その場所を kernel (核) と呼ぶ
```

---

## 結論

```
∴ kernel/ は存在しなければならない

Q.E.D.
```

---

## 内容物の正当性

| ファイル | 演繹 |
|:---------|:-----|
| SACRED_TRUTH.md | P2 → 不変の法則の記述 |
| axiom_hierarchy.md | A0 → 公理体系の展開 |
| on_refinement.md | P2 → 設計哲学の法則 |
| 各series.md | A0 → 定理の演繹 |

<!-- EPISTEMIC_STATUS_START -->

## 認識論的地位 (Epistemic Status)

> 自動生成: `epistemic_status.yaml` から注入

| ID | 主張 | 地位 | 反証条件 |
|:---|:-----|:-----|:---------|
| P1 | Attention 層の階層性が Scale 座標の操作的類推 | 🟡 analogue | 浅い層=独立, 深い層=因果依存の関係が他のアーキテクチャで成立しない場合 |
| P3 | entity-based scope が X-series の操作的類推 | 🟡 analogue | entity-based scope が X-series の予測と矛盾する検索パターンを示す場合 |
| Spisak_replay | /boot⊣/bye replay が生物学的 replay と構造的に類似 | 🟡 analogue | replay 品質 η の数値化で生物学的 replay との乖離が大きい場合 |
| fep_evolution | FEP は進化論と構造的に類似した位置づけ | 🟡 analogue | FEP が進化論と異なる認識論的特性を持つことが示された場合 |
| P7 | Budget forcing が BC-9 meta-cognitive check と構造的に類似 | 🟡 analogue | Budget forcing が Meta-cognitive check と異なる認知効果を生む場合 |
| thinking_depth | 深度レベルが Gemini thinking level と構造的に類似 | 🟡 analogue | thinking level の調整が HGK 深度システムと異なる効果を示す場合 |
| P2 | π_i = V[ε_i]⁻¹ は暗黙の検索クエリとして解釈できる | 🟡 analogue | attention score の分布が精度加重 π の理論的分布と系統的に乖離する場合 |
| P6 | Sequential CoT > Parallel sampling (2.5x) | 🔵 reference | 他のアーキテクチャで並列が逐次を上回る場合 |
| P4 | Verification 除去で reasoning 精度が -1.9% 低下 | 🔵 reference | 他のモデル/タスクで Verification 除去が精度に影響しない場合 |
| P5 | Content memory 除去で 42.5% 低下 | 🔵 reference | 他のモデルで Content memory 除去が同等の影響を示さない場合 |

<!-- EPISTEMIC_STATUS_END -->
---

*kernel/ は FEP から演繹される。発明ではない。*
