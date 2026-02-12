# Peras 収束パターン — `~*` 演算子の実装仕様

> **帰属先**: CCL 演算子 `~*` (convergent oscillation) の内部アルゴリズム
> **元分類**: ccl/macros/converge.md → 再帰属 (2026-02-12)
> **理由**: マクロではなく演算子の実装仕様であるため。公理から演繹されるべき

---

## 定義

```yaml
operator: ~* (convergent oscillation)
parameters:
  threshold_high: float (default: 0.3)
  threshold_low: float (default: 0.1)
expansion: |
  # C1: 対比 — 4定理の出力を並列比較、矛盾を検出
  F:[T1,T2,T3,T4]{ @selfcheck }
  _
  # C2: 解消 — 分散ベースの分岐統合
  I:[V[outputs] > $threshold_high]{
    /dia.root{conflict} _ @reduce(*){T1,T2,T3,T4}
  }
  EI:[V[outputs] > $threshold_low]{
    @reduce(*){T1,T2,T3,T4}
  }
  E:{
    Σ[outputs]
  }
  _
  # C3: 検証 — 確信度付き出力
  /dia-{convergence_result} _ /pis{convergence_result}
```

---

## 処理フロー

```
C1: 対比 (Contrast)
├─ 4定理の出力を @selfcheck で自己検証
├─ 各出力の要点を1行で抽出
└─ 出力間の分散 V[outputs] を計算

C2: 解消 (Resolve)
├─ V > threshold_high → /dia.root で根源探索 → 重み付け融合
├─ V > threshold_low  → 通常融合
└─ V ≤ threshold_low  → 単純集約

C3: 検証 (Verify)
├─ /dia- で PASS/FAIL
├─ /pis で確信度 (C/U)
└─ 出力テーブル生成
```

---

## 出力テーブル

| 項目 | 内容 |
|:-----|:-----|
| 矛盾度 | V[outputs] = {0.0-1.0} |
| 解消法 | {root/weighted/simple} |
| 統合判断 | {1文} |
| 確信度 | {C/U} ({confidence}%) |

---

## 借用元

| WF | 借用構造 | 適用先 |
|:---|:---------|:-------|
| `/dia` | @selfcheck | C1 |
| `/bou` | 衝動スコア (分散分岐) | C2 |
| `/dox` | 確信度(C/U)強制 | C3 |
| `/ene` | Blocking Gate | C1→C2 |

---

## 複雑度

| マクロ | pt |
|:-------|:--:|
| `@converge` | 5 |
| `@converge{threshold_high=X}` | 6 |

*Hub WF Convergence Deepening v1.0*
