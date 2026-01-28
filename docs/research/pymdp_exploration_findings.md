# pymdp 探索 — 包括的知見レポート v2.0

> **セッション**: 2026-01-28
> **目的**: pymdp-Hegemonikón 統合の深掘り探索、次セッションへの引き継ぎ

---

## 1. 実験サマリー

| # | 実験名 | 主要発見 |
|:--|:-------|:---------|
| 1 | 連続観測での信念累積 | 観測順序が重要、最後の観測が支配的 |
| 2 | 対立観測の効果 | 緊急+低確信 → act 66% (緊急が優位) |
| 3 | Epochē 閾値特定 | 閾値候補: **2.02** (obs 3 = medium urgency) |
| 4 | 行列特性分析 | C = [-2, +2, 0, +0.5, +1, -1, +0.5, +1.5] |
| 5 | 全状態の信念遷移 | obs 1 (clear) のみ phantasia:clear に遷移 |
| 6 | 政策ごとの期待遷移 | observe→clear, act→granted+active |
| 7 | EFE 分解 | act は EFE 0.076 低い |

---

## 2. 行動別の状態遷移パターン

### observe (a=0): 観察行動

```
任意状態 → (clear, *, passive)
           phantasia 明確化、horme 沈静化
```

- uncertain → clear への遷移: 25%
- clear → clear 維持: 37%
- **設計意図**: 観察は理解を深め、衝動を抑制

### act (a=1): 行動

```
任意状態 → (*, granted, active)
           assent 付与、horme 活性化
```

- withheld → granted への遷移: 37%
- clear + act → granted + active: 48%
- **設計意図**: 行動は同意を意味し、衝動を活性化

---

## 3. 観測→状態マッピング (完全版)

| 観測 | 名前 | MAP 状態 |
|:-----|:-----|:---------|
| 0 | ambiguous context | uncertain/withheld/passive |
| 1 | **clear context** | **clear/withheld/passive** |
| 2 | low urgency | uncertain/withheld/passive |
| 3 | medium urgency | uncertain/withheld/passive |
| 4 | **high urgency** | uncertain/withheld/**active** |
| 5 | low confidence | uncertain/withheld/passive |
| 6 | medium confidence | uncertain/withheld/passive |
| 7 | **high confidence** | uncertain/**granted**/passive |

**発見**:

- obs 1 (clear) だけが phantasia:clear に導く
- obs 4 (high urgency) だけが horme:active に導く
- obs 7 (high confidence) だけが assent:granted に導く

---

## 4. C ベクトル (選好) の解釈

```
観測    インデックス   選好値   意味
──────────────────────────────────────────
ambiguous    0         -2.0    強い嫌悪 (Zero Entropy 違反)
clear        1         +2.0    強い選好 (Zero Entropy 推進)
low_u        2          0.0    中立
medium_u     3         +0.5    わずかに選好
high_u       4         +1.0    選好 (緊急対応)
low_c        5         -1.0    嫌悪 (Epochē 誘導)
medium_c     6         +0.5    わずかに選好
high_c       7         +1.5    選好 (確信)
```

**設計思想**:

- **Zero Entropy**: 曖昧さを嫌い、明確さを好む
- **Epochē**: 低確信を嫌う (しかし-1.0 なので曖昧ほどではない)
- **緊急度**: 高緊急 (+1.0) は行動を促進する選好

---

## 5. EFE (期待自由エネルギー) の構造

```
EFE = Epistemic value + Pragmatic value
    = 情報獲得価値 + 選好達成価値
```

### clear context 観測後

| 行動 | EFE | 選択確率 |
|:-----|:----|:---------|
| observe | 2.149 | 22.9% |
| act | 2.073 | **77.1%** |

**解釈**: EFE が低いほど好ましい → act が選択される

---

## 6. 次セッションへの課題

### 高優先度

1. **複数モダリティ同時処理**: 現在は 1 観測のみ。テキストから (context, urgency, confidence) を同時に処理したい
2. **連続観測の累積効果**: 最後の観測が支配的なのは設計ミス？履歴を保持する仕組みが必要
3. **Epochē 閾値の検証**: 2.02 が妥当か、実運用データで確認

### 中優先度

1. **B 行列の調整**: observe→clear 確率 (25%) は低すぎないか？
2. **C ベクトルの調整**: 選好値のバランス検証

### 低優先度

1. **学習機能**: B 行列を経験から更新
2. **階層モデル**: より複雑な状態空間

---

## 7. コードリファレンス

| ファイル | 役割 |
|:---------|:-----|
| `mekhane/fep/fep_agent.py` | FEP Agent (A/B/C/D 行列含む) |
| `mekhane/fep/state_spaces.py` | 状態空間定義 |
| `mekhane/fep/encoding.py` | テキスト→観測変換 |
| `scripts/fep_demo.py` | 基本デモ |
| `scripts/fep_experiment.py` | インタラクティブ実験 |
| `docs/architecture/pymdp_integration_guide.md` | 統合ガイド |

---

## 8. コミット履歴 (本セッション)

```
a8cb2d01 feat: encoding.py + 探索知見レポート
7963bb57 docs: pymdp-Hegemonikón 統合ガイド + インタラクティブ実験
aa975a71 feat: pymdp Stoic-FEP 改良 + デモスクリプト
4522ff2b feat: pymdp Active Inference 統合 PoC
a24db405 doctrine: Stoic-FEP Correspondence
bd110a9f docs: STOIC vs Hegemonikón 比較分析
166dc323 kernel: O1 Noēsis に Recursive Self-Evidencing
```

---

*pymdp 探索レポート v2.0 — 次セッションへ引き継ぎ*
