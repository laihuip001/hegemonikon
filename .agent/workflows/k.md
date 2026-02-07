---
description: K-series 4定理Limit。L1.5×L1.75 の極限演算で文脈判断の統合を生成。
hegemonikon: Kairos
modules: [K1, K2, K3, K4]
skill_ref:
  - ".agent/skills/kairos/k1-eukairia/SKILL.md"
  - ".agent/skills/kairos/k2-chronos/SKILL.md"
  - ".agent/skills/kairos/k3-telos/SKILL.md"
  - ".agent/skills/kairos/k4-sophia/SKILL.md"
version: "6.0"
layer: "Δ"
lineage: "v5.2 + Limit演算復元 → v6.0"
cognitive_algebra:
  generation: "L1.5 × L1.75"
  coordinates:
    axis_1: "Scale/Function"
    axis_2: "Valence/Precision"
  definition: "/k = lim(K1·K2·K3·K4)"
  interpretation: "4定理の内積 → 最適収束点"
  operators:
    "+": "Limit強度↑ — 全4定理を詳細に収束"
    "-": "Limit強度↓ — 縮約収束"
    "*": "Limit対象自体を問う: なぜ文脈を問うか"
sel_enforcement:
  "+":
    description: "MUST execute ALL 4 theorems with deep convergence"
    minimum_requirements:
      - "全4定理実行"
      - "各定理詳細モード"
      - "融合ステップ必須"
  "-":
    description: "MAY execute with condensed convergence"
    minimum_requirements:
      - "サマリーのみ"
  "*":
    description: "MUST meta-analyze: why question context?"
    minimum_requirements:
      - "文脈層選択の理由を問う"
derivatives: [urge, opti, miss, shor, medi, long, intr, inst, ulti, taci, expl, meta]
absorbed:
  - "/pri.md v3.0 (2026-01-28)"
children:
  - "/euk"   # K1 Eukairia (好機)
  - "/chr"   # K2 Chronos (時間)
  - "/tel"   # K3 Telos (目的)
  - "/sop"   # K4 Sophia (情報収集)
anti_skip: enabled
ccl_signature: "/k+?k1"
---

# /k: 文脈定理ワークフロー (Kairos)

> **Hegemonikón Layer**: Kairos (K-series)
> **定義**: `/k` = `lim(K1·K2·K3·K4)` — L1.5×L1.75 の極限演算
> **目的**: 好機・時間・目的・知恵の4定理を**1つの文脈的判断に収束**させる
> **統合**: /pri (優先順位判定) を吸収済み
>
> **制約**: 全4定理 → 融合(Convergence)。途中の省略は`-`モード実行時のみ許容。

---

## Limit / Colimit

| 演算 | 記号 | 圏論 | 意味 |
|:-----|:-----|:-----|:-----|
| `/k` | `/` | **Limit** | 4定理 → 最適な1収束点 |
| `\k` | `\` | **Colimit** | 4定理 → 全組み合わせに展開 |
| `/k+` | `+` | Limit強度↑ | より深い収束 |
| `/k-` | `-` | Limit強度↓ | 軽い収束 |

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/k` または `/kairos` | Kairos シリーズを起動 |
| `/k [1-4]` | 特定の定理を指定して起動 |
| `/k pri` | **優先順位判定モード** (Eisenhower Matrix) ← 旧 /pri |
| `/k pri auto` | 現在のチャットから自動抽出して分類 |
| 「どれを先に？」 | 暗黙的トリガー → `/k pri` |

---

## K-series 定理一覧

| # | ID | Name | Greek | 生成 | 役割 |
|:-:|:---|:-----|:------|:-----|:-----|
| 1 | **K1** | Eukairia | Εὐκαιρία | Scale × Valence | **好機判定** — 今が適時か |
| 2 | **K2** | Chronos | Χρόνος | Scale × Precision | **時間配置** — 時間軸上の配置 |
| 3 | **K3** | Telos | Τέλος | Function × Valence | **目的整合** — 目的との整合確認 |
| 4 | **K4** | Sophia | Σοφία | Function × Precision | **知恵適用** — 経験からの知恵 |

---

## 処理フロー

### `/k` (Limit — 収束)

1. **[K1 Eukairia]** Scale×Valence: 好機判定(今か？待つか？)
2. **[K2 Chronos]** Scale×Precision: 時間配置(いつ？どの期間？)
3. **[K3 Telos]** Function×Valence: 目的整合(目的に合うか？)
4. **[K4 Sophia]** Function×Precision: 知恵適用(過去の経験は？)
5. **⊕ Convergence**: 4定理の出力を**1つの文脈的判断**に融合

### `/k [N]` (単体駆動)

SKILL.md を参照し、指定定理のみ実行。

---

## `/k pri`: 優先順位判定モード

> **Origin**: 旧 `/pri.md` v3.0 を吸収
> **設計思想**: 「雑な入力 → 整理された出力」

### 処理フロー

1. **Precondition Check** (発動前確認)
2. **タスク抽出** (Input Extraction)
3. **評価** — Goal Alignment (40%) + Urgency (30%) + Commitment (30%)
4. **分類** (Eisenhower Matrix)
5. **Q2 保護メカニズム**
6. **出力**: Priority Decision → Artifact 保存

### Eisenhower Matrix

| 象限 | 定義 | アクション |
|:-----|:-----|:-----------|
| **Q1** | 重要 & 緊急 | 🔥 即時実行 → `/ene` |
| **Q2** | 重要 & 非緊急 | 🛡️ 計画・保護 → `/s` |
| **Q3** | 非重要 & 緊急 | 📤 委任・縮小 |
| **Q4** | 非重要 & 非緊急 | 🗑️ 削除・後回し |

### Urgency マッピング

| 時間軸 | 期限 | urgency |
|:-------|:-----|:-------:|
| today | ≤ 24h | 1.0 |
| 3days | ≤ 72h | 0.8 |
| week | ≤ 7d | 0.6 |
| 3weeks | ≤ 21d | 0.4 |
| 2months | ≤ 60d | 0.2 |

### Q2 保護メカニズム

> Q2 タスクは日常のQ1/Q3に埋もれやすい。強制的に浮上させる。

```yaml
min_q2_ratio: 0.2     # 出力の 20% 以上は Q2 を含める
q2_boost: 0.15        # Q2 タスクの priority_score に +0.15 ボーナス
daily_q2_slot: 1      # Top 3 に必ず 1 つは Q2 を含める
```

---

## 出力形式

| 項目 | 内容 |
|:-----|:-----|
| 定理 | K{N} {Name} |
| 対象 | {対象} |
| 判定 | {Go/Wait/Pass} |
| 時間軸 | {即時/短期/中期/長期} |
| 次の推奨 | → A{X} / O{Y} |

---

## X-series 接続

```mermaid
graph LR
    P1[P1 Khōra] -->|X-PK1| K1[K1 Eukairia]
    P2[P2 Hodos] -->|X-PK3| K1
    P3[P3 Trokhia] -->|X-PK5| K3[K3 Telos]
    P4[P4 Tekhnē] -->|X-PK7| K3
    K1 -->|X-KA2| A2[A2 Krisis]
    K3 -->|X-KA3| A3[A3 Gnōmē]
    K4[K4 Sophia] -->|X-KA4| A4[A4 Epistēmē]
```

---

## Hegemonikon Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| K1-K4 + Pri | /k | v6.0 Ready |

---

*v6.0 — Limit演算復元 (2026-02-07)*
