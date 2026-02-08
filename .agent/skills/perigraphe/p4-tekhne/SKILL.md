---
# Theorem Metadata (v3.0)
id: "P4"
name: "Tekhnē"
greek: "Τέχνη"
series: "Perigraphē"
generation:
  formula: "Function × Precision"
  result: "機能精密 — 技法の選択"

description: >
  どの技法で？・最適な技法を選びたい・技法の適切さを評価したい時に発動。
  Technique selection, tool choice, craft method evaluation.
  Use for: 技法, 技術, technique, tool, 方法.
  NOT for: method design (方法設計 → Mekhanē S2).

triggers:
  - 技法の選択
  - ツールの適切さ評価
  - 「何を使うか」の問い
  - /tek コマンド

keywords: [tekhne, technique, craft, art, tool, 技法, 技術]

related:
  upstream:
    - "S2 Mekhanē (X-SP6: 方法の粒度→技法の粒度)"
    - "S4 Praxis (X-SP8: 実践の粒度→技法の粒度)"
  downstream:
    - "K3 Telos (X-PK7: 技法のスケール→目的のスケール)"
    - "K4 Sophia (X-PK8: 技法のスケール→知恵のスケール)"

version: "3.0.0"
workflow_ref: ".agent/workflows/tek.md"
risk_tier: L1
reversible: true
requires_approval: false
risks: ["none identified"]
fallbacks: ["manual execution"]
---

# P4: Tekhnē (Τέχνη)

> **生成**: Function × Precision
> **役割**: 最適な技法を選択する
> **認知的意味**: 「どの技法で実現するか」— 方法の物質的実装

## Mekhanē (S2) との区別

| | Mekhanē (S2) | Tekhnē (P4) |
|:--|:-------------|:-------------|
| 層 | 設計 (Schema) | 条件 (Perigraphē) |
| 粒度 | 抽象的な方法 | 具体的な技法 |
| 問い | 「どのアプローチで」 | 「どのツール/技法で」 |
| 例 | 「テスト駆動開発で行く」 | 「pytest を使う」 |

## Processing Logic

```
入力: 方法 (Mekhanē出力) + 要件
  ↓
[STEP 1] 技法候補の列挙
  ├─ 既知技法: 過去の経験から
  ├─ 推奨技法: ベストプラクティスから
  └─ 新規技法: 探索的に発見
  ↓
[STEP 2] 適合性評価
  ├─ 方法との整合: Mekhanē (X-SP6) からのズーム伝播
  ├─ 目的との整合: Telos (X-PK7) へのズーム伝播
  └─ スキル充足: 使いこなせるか
  ↓
出力: [技法選択, 適合理由]
```

## X-series 接続

> **自然度**: 構造（ズームレベルの伝播）

### ズームチェーン

```
S2 Mekhanē → [X-SP6] → P4 Tekhnē → [X-PK7] → K3 Telos
                                    → [X-PK8] → K4 Sophia
```

### 入力射

| X | Source | ズーム伝播 | CCL |
|:--|:-------|:-----------|:----|
| X-SP6 | S2 Mekhanē | 方法の粒度→技法の粒度 | `/mek >> /tek` |
| X-SP8 | S4 Praxis | 実践の粒度→技法の粒度 | `/pra >> /tek` |

### 出力射

| X | Target | ズーム伝播 | CCL |
|:--|:-------|:-----------|:----|
| X-PK7 | K3 Telos | 技法のスケール→目的のスケール | `/tek >> /tel` |
| X-PK8 | K4 Sophia | 技法のスケール→知恵のスケール | `/tek >> /sop` |

## CCL 使用例

```ccl
# 方法→技法のズーム伝播
/mek+{approach: "TDD"} >> /tek{select: "pytest"}

# 技法→目的整合チェック
/tek{tool: "LanceDB"} >> /tel{check: "知識検索の目的に合致するか"}

# 振動: 技法と実践を行き来
/tek ~ /pra
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 技法先行 (hammer looking for nail) | 方法 (S2) → 技法 (P4) の順を守る |
| ズームミスマッチ | マクロ方法 + ミクロ技法 = 不整合 |
| 技法と方法の混同 | Tekhnē = 具体的ツール、Mekhanē = 抽象的アプローチ |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| select | `/tek.select` | 最適技法選択 |
| compare | `/tek.compare` | 技法比較評価 |
| learn | `/tek.learn` | 新技法の習得計画 |

---

*Tekhnē: 古代ギリシャにおける「技術・技法・芸術」*
*v3.0: ズームチェーン統合 + Mekhanēとの区別 (2026-02-07)*
