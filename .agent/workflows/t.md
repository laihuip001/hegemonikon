---
description: T-series（拡張定理 T1-T8）を駆動し、具体的な様態機能を呼び出す。
hegemonikon: Tropos
modules: [T1, T2, T3, T4, T5, T6, T7, T8]
---

# /t: 拡張定理ワークフロー

> **Hegemonikón Layer**: Level 2b T-series (Tropos)
> **目的**: 8つの様態機能を明示的に呼び出す
> **参照**: [tropos.md](../../kernel/tropos.md)

---

## 本質

T-series は「様態」として機能する。
O-series の純粋形式を、具体的な処理様式に展開する。

| シリーズ | 性質 | 問い |
|----------|------|------|
| O-series | 本質的 | 「何であるか」 |
| **T-series** | **様態的** | **「どのように在るか」** |
| K-series | 文脈的 | 「どの状況で在るか」 |

---

## T-series 一覧

| ID | 機能 | ギリシャ名 | Skill |
|----|------|-----------|-------|
| T1 | 知覚 | Aisthēsis | m1-aisthesis |
| T2 | 判断 | Krisis | m2-krisis |
| T3 | 内省 | Theōria | m3-theoria |
| T4 | 戦略 | Phronēsis | m4-phronesis |
| T5 | 探索 | Peira | m5-peira |
| T6 | 実行 | Praxis | m6-praxis |
| T7 | 検証 | Dokimē | m7-dokime |
| T8 | 記憶 | Anamnēsis | m8-anamnesis |

---

## 発動条件

| トリガー | 説明 |
|----------|------|
| `/t` | T-series 選択画面を表示 |
| `/t [N]` | 特定の T-series を直接呼び出し |
| 暗黙発動 | 各 Workflow が自動的に対応する T を呼び出す |

---

## 暗黙発動マッピング

| Workflow | 呼び出される T-series |
|----------|---------------------|
| `/boot` | T1 (知覚), T8 (記憶) |
| `/ask` | T5 (探索) |
| `/plan` | T4 (戦略) |
| `/code` | T6 (実行) |
| `/rev` | T7 (検証), T3 (内省) |
| `/pri` | T2 (判断) |

---

## 出力形式

```
┌─[Hegemonikón]──────────────────────┐
│ T{N} {Name}: {機能}                │
│ 入力: {処理対象}                   │
│ 出力: {処理結果}                   │
└────────────────────────────────────┘
```

---

## 使用例

**例1: 直接呼び出し**
```
/t 5
→ T5 Peira（探索）を明示的に発動
→ 情報収集を実行
```

**例2: 状況確認**
```
/t
→ 現在の状況に適した T-series を提案
→ 「判断が必要 → T2 Krisis を推奨」
```

---

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| T1-T8 | /t | Ready |
