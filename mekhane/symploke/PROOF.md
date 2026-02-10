# PROOF.md — 存在証明書

PURPOSE: 複数の認知モジュールを統合し、/boot シーケンスやオーケストレーション機能を提供する
REASON: 個別モジュールを協調動作させるための統合層が不在だった

> **∃ symploke/** — この場所は存在しなければならない

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
P1: システムは複数の要素を統合する
  ↓ [統合の必要性]
P2: 要素間の連結 (connection) が必要
  ↓ [検索と発見]
P3: 連結を発見・検索する仕組みが必要
  ↓ [名前の必然性]
P4: その場所を symploke/ (編み合わせ) と呼ぶ
```

**語源**: συμπλοκή (symplokē) = 編み合わせ、絡み合い

---

## 結論

```
∴ symploke/ は存在しなければならない

Q.E.D.
```

---

## 内容物の正当性

| ファイル/ディレクトリ | 演繹 |
|:---------------------|:-----|
| search/ | P3 → 意味的検索 |
| embeddings/ | P3 → ベクトル表現 |
| backlinker/ | P3 → 逆リンク発見 |

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `boot_integration.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/ A0→継続する私が必要→boot_integration が担う |
| `boot_axes.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/ A0→統合処理の複雑性→分割が必要→boot_axes が担う |
| `config.py` | # PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識システムには設定が必要→config が担う |

---

*symploke/ は FEP から演繹される。発明ではない。*