# PROOF.md — 存在証明書

PURPOSE: Store specialist review outputs (Jules)
REASON: Specialist feedback must be persisted for analysis

> **∃ reviews/** — この場所は存在しなければならない

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
P1: システムは自己修正を行う
  ↓ [修正の前提]
P2: 誤差の検出と報告が必要
  ↓ [報告の保存]
P3: 報告を永続化する場所が必要
  ↓ [名前の必然性]
P4: その場所を reviews/ と呼ぶ
```

---

## 結論

```
∴ reviews/ は存在しなければならない

Q.E.D.
```
