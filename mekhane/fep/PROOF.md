# PROOF.md — 存在証明書

PURPOSE: 自由エネルギー原理 (FEP) に基づく認知評価・意思決定エンジンを実装する
REASON: Hegemonikón の理論的基盤 (FEP) を実際の評価・判断に具現化する実装が必要だった

> **∃ fep/** — この場所は存在しなければならない

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
P1: Hegemonikón は FEP に基づく認知フレームワークである
  ↓ [実装の必要性]
P2: FEP を実装するコードが必要
  ↓ [直接実装]
P3: FEP の直接実装を格納する場所が必要
  ↓ [名前の必然性]
P4: その場所を fep/ (Free Energy Principle) と呼ぶ
```

---

## 結論

```
∴ fep/ は存在しなければならない

Q.E.D.
```

---

## 内容物の正当性

| ファイル/ディレクトリ | 演繹 |
|:---------------------|:-----|
| derivative_selector/ | P2 → 派生選択の実装 |
| fep_bridge.py | P2 → FEP と CCL の橋渡し |
| fep_agent.py | P2 → FEP エージェント実装 |
| parameters/ | P2 → FEP パラメータ管理 |

---

*fep/ は FEP から演繹される。発明ではない。*