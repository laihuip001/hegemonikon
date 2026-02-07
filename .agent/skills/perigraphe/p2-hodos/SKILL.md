---
# Theorem Metadata (v3.0)
id: "P2"
name: "Hodos"
greek: "Ὁδός"
series: "Perigraphē"
generation:
  formula: "Scale × Explore"
  result: "スケール探索 — 到達経路の定義"

description: >
  どのルートで進む？・道筋を決めたい・経路を定義したい時に発動。
  Path definition, route planning, journey mapping.
  Use for: 道筋, 経路, route, path, ルート.
  NOT for: 反復的なサイクル (→ Trokhia P3).

triggers:
  - 到達経路の定義
  - ルート計画
  - 段階的ステップの設計
  - /hod コマンド

keywords: [hodos, path, route, way, journey, 道, 経路]

related:
  upstream:
    - "S1 Metron (X-SP2: 測定基準→到達経路を制約)"
    - "S3 Stathmos (X-SP4: 評価基準→達成への道筋)"
  downstream:
    - "K1 Eukairia (X-PK3: 経路→今この道を進むべきか)"
    - "K2 Chronos (X-PK4: 経路→この道にかかる時間)"

version: "3.0.0"
workflow_ref: ".agent/workflows/hod.md"
risk_tier: L1
reversible: true
requires_approval: false
---

# P2: Hodos (Ὁδός)

> **生成**: Scale × Explore
> **役割**: 到達経路を定義する（直線的な道筋）
> **認知的意味**: 「どのルートで目的地に向かうか」を設計する

## When to Use

### ✓ Trigger

- A 地点から B 地点へのルート計画
- 段階的な実装ステップの設計
- マイルストーンの定義
- 「どう進めるか」の道筋

### ✗ Not Trigger

- 反復サイクル → `/tro` (Trokhia: 周回)
- 領域の定義 → `/kho` (Khōra: 場)
- 一回限りの実行 → `/ene` (Energeia: 行為)

## Processing Logic

```
入力: 出発点 + 目的地
  ↓
[STEP 1] 経路候補の生成
  ├─ 直行ルート: 最短経路
  ├─ 安全ルート: リスク最小化
  └─ 探索ルート: 学習最大化
  ↓
[STEP 2] マイルストーン設計
  ├─ 中間目標の設定
  └─ 各区間の見積もり
  ↓
[STEP 3] ズームレベル確認 (構造層)
  ├─ 測定基準のズーム (S1) から伝播 → X-SP2
  └─ 時間のズーム (K2) と整合 → X-PK4
  ↓
出力: [経路定義, マイルストーン, 所要時間]
```

## X-series 接続

> **自然度**: 構造（ズームレベルの伝播）

### 入力射

| X | Source | ズーム伝播 | CCL |
|:--|:-------|:-----------|:----|
| X-SP2 | S1 Metron | 測定のスケール→経路のスケール | `/met >> /hod` |
| X-SP4 | S3 Stathmos | 評価のスケール→道筋のスケール | `/sta >> /hod` |

### 出力射

| X | Target | ズーム伝播 | CCL |
|:--|:-------|:-----------|:----|
| X-PK3 | K1 Eukairia | 経路のスケール→好機のスケール | `/hod >> /euk` |
| X-PK4 | K2 Chronos | 経路のスケール→時間のスケール | `/hod >> /chr` |

## CCL 使用例

```ccl
# 評価基準から道筋を導出
/sta{criteria: "96要素充実度"} >> /hod{milestone: true}

# 道の時間見積もり
/hod{route: "B→D→C"} >> /chr{estimate: true}

# 経路と好機の同時評価
/hod{path: "planned"} >> /euk{question: "今この道を進むべきか"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 目的地なしに道を定義 | Boulēsis→Hodos の因果が必要 |
| Trokhia との混同 | Hodos = 直線 (A→B), Trokhia = 周回 (A→...→A) |
| ズーム不整合 | マクロ測定 + ミクロ経路 = ギャップ |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| direct | `/hod.direct` | 最短経路 |
| safe | `/hod.safe` | リスク最小経路 |
| explore | `/hod.explore` | 学習最大経路 |

---

*Hodos: 古代ギリシャにおける「道・旅路・方法」*
*v3.0: ズームチェーン統合 + X-series全接続 (2026-02-07)*
