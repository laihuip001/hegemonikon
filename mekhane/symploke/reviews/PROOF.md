# PROOF.md — mekhane/symploke/reviews/

PURPOSE: Specialist Review の結果を永続化する
REASON: レビュー結果を蓄積し、改善サイクルを回すための記録場所が必要

> **∃ reviews/** — Specialist Review Reports

---

## 公理

```
A0: 予測誤差最小化 (Free Energy Principle)
```

---

## 演繹

```
A0: 予測誤差最小化
  ↓ [評価の必要性]
P1: コードの品質を評価し、誤差を検出する必要がある
  ↓ [Specialist Review]
P2: 専門家によるレビューを行う
  ↓ [結果の保存]
P3: レビュー結果を保存し参照可能にする必要がある
  ↓ [名前の必然性]
P4: その場所を reviews/ と呼ぶ
```

---

## 結論

```
∴ reviews/ は存在しなければならない

Q.E.D.
```
