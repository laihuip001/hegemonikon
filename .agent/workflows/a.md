---
description: A-series 4項振動。感情↔判定↔原則↔知識を巡回する精度保証サイクル。
hegemonikon: Akribeia
modules: [A1, A2, A3, A4]
skill_ref:
  - ".agent/skills/akribeia/a1-pathos/SKILL.md"
  - ".agent/skills/akribeia/a2-krisis/SKILL.md"
  - ".agent/skills/akribeia/a3-gnome/SKILL.md"
  - ".agent/skills/akribeia/a4-episteme/SKILL.md"
version: "4.1"
layer: "Δ"
lineage: "v4.0 (4項振動化) + SEL 統合 → v4.1"
cognitive_algebra:
  definition: "/a = /pat~dia~gno~epi (4項振動)"
  operators:
    "+": "全4定理を詳細モードで順次実行"
    "-": "全4定理を縮約モードで順次実行"
    "*": "A-series 自体を問う: なぜ精度を問うか"
sel_enforcement:
  "+":
    description: "MUST execute ALL 4 theorems in detailed mode"
    minimum_requirements:
      - "全4定理実行"
      - "各定理詳細モード"
      - "精度保証出力"
  "-":
    description: "MAY execute all 4 theorems in condensed mode"
    minimum_requirements:
      - "サマリーのみ"
  "*":
    description: "MUST meta-analyze: why question accuracy?"
    minimum_requirements:
      - "精度層選択の理由を問う"
derivatives: [prim, seco, regu, affi, nega, susp, conc, abst, univ, tent, just, cert]
ccl_signature: "/a+_/dia"
children:
  - "/pat"   # A1 Pathos (メタ感情)
  - "/dia"   # A2 Krisis (判定力)
  - "/gno"   # A3 Gnōmē (格言)
  - "/epi"   # A4 Epistēmē (知識)
  - "/vet"   # A2+A4 派生
---

# /a: 精度定理ワークフロー (12派生対応)

> **Hegemonikón Layer**: Akribeia (A-series)
> **目的**: 感情・判断・見識・知識の4軸で精度を保証する

---

## 発動条件

| トリガー | 説明 |
| :-------- | :---- |
| `/a` または `/akri` | Akribeia シリーズを起動 |
| `/a [1-4]` | 特定の定理を指定して起動 |
| 精度・検証が必要 | 判断・知識の確定 |

---

## A-series 定理一覧

| # | ID | Name | Greek | 役割 |
| :-: | :-- | :--- | :---- | :--- |
| 1 | **A1** | Pathos | Πάθος | **精度感情** — 感情の精緻化・言語化 |
| 2 | **A2** | Krisis | Κρίσις | **精度判断** — 判断・決定の精度確保 |
| 3 | **A3** | Gnōmē | Γνώμη | **精度見識** — 見識・洞察の形成 |
| 4 | **A4** | Epistēmē | Ἐπιστήμη | **精度知識** — 知識の確定・固定 |

---

## Process

### `/a` (全体駆動)

```text
入力: 対象 X
  ↓
[A1 Pathos] 感情を精緻化（主観的反応）
  ↓
[A2 Krisis] 判断を確定（決定基準）
  ↓
[A3 Gnōmē] 見識を形成（洞察抽出）
  ↓
[A4 Epistēmē] 知識として固定（KI 生成候補）
  ↓
出力: 精度保証済み知見
```

### `/a 2` (A2 Krisis 単体)

```text
入力: 判断対象
  ↓
SKILL.md 参照: .agent/skills/akribeia/a2-krisis/SKILL.md
  ↓
[STEP 1] 判断基準の明確化
[STEP 2] 代替案の比較
[STEP 3] 決定と根拠の出力
  ↓
出力: 精度保証済み判断
```

### `/a 4` (A4 Epistēmē 単体)

```text
入力: 知見
  ↓
SKILL.md 参照: .agent/skills/akribeia/a4-episteme/SKILL.md
  ↓
[STEP 1] 知識の構造化
[STEP 2] KI 生成候補判定
[STEP 3] 固定化 or 保留
  ↓
出力: 確定知識 / KI 候補
```

---

## 出力形式

```markdown
┌─[Hegemonikón]──────────────────────┐
│ A{N} {Name}: 精度処理完了          │
│ 対象: {対象}                       │
│ 精度: {0-100}%                     │
│ KI候補: {Yes/No}                   │
│ 次の推奨: → O{X} / K{Y}            │
└────────────────────────────────────┘
```

---

## X-series 接続

```mermaid
graph LR
    H1[H1 Propatheia] -->|X-HA1| A1[A1 Pathos]
    K1[K1 Eukairia] -->|X-KA2| A2[A2 Krisis]
    K3[K3 Telos] -->|X-KA3| A3[A3 Gnōmē]
    K4[K4 Sophia] -->|X-KA4| A4[A4 Epistēmē]
    A4 -->|X-AO1| O1[O1 Noēsis]
```

---

## Hegemonikon Status

| Module | Workflow | Status |
| :----- | :------- | :----- |
| A1-A4 | /a | v2.1 Ready |
