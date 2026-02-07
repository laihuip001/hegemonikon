---
# Theorem Metadata (v3.0)
id: "S2"
name: "Mekhanē"
greek: "Μηχανή"
series: "Schema"
generation:
  formula: "Internality × Function"
  result: "内在機能 — 方法の選択と配置"

description: >
  どの方法で？・アプローチを選びたい・方法を配置したい時に発動。
  Method selection, approach design, strategy configuration.
  Use for: 方法, アプローチ, method, approach, how.
  NOT for: technique/tool selection (技法 → Tekhnē P4).

triggers:
  - 方法・アプローチの選択
  - 戦略の設計
  - 「どうやるか」の問い
  - /mek コマンド

keywords: [mekhane, method, machine, mechanism, 方法, アプローチ]

related:
  upstream:
    - "O1 Noēsis (X-OS2: 本質理解→方法)"
    - "O2 Boulēsis (X-OS4: 目的定義→達成手段)"
  downstream:
    - "P3 Trokhia (X-SP5: 方法→サイクル)"
    - "P4 Tekhnē (X-SP6: 方法→技法)"
    - "K3 Telos (X-SK5: 方法→目的整合)"
    - "K4 Sophia (X-SK6: 方法→知恵充足)"
    - "H1 Propatheia (X-SH3: 方法→直感)"
    - "H2 Pistis (X-SH4: 方法→確信)"

version: "3.0.0"
workflow_ref: ".agent/workflows/mek.md"
risk_tier: L1
reversible: true
requires_approval: false
---

# S2: Mekhanē (Μηχανή)

> **生成**: Internality × Function
> **役割**: 方法を選択し配置する
> **認知的意味**: 「どのアプローチで実現するか」— 設計の中核

## Tekhnē (P4) との区別

| | Mekhanē (S2) | Tekhnē (P4) |
|:--|:-------------|:-------------|
| 層 | Schema (設計) | Perigraphē (条件) |
| 問い | 「どのアプローチで」 | 「どのツール/技法で」 |
| 例 | 「TDD で行く」 | 「pytest を使う」 |
| 出力先 | P, K, H (6方向) | K のみ (2方向) |

## Processing Logic

```
入力: 目的 (Boulēsis) / 認識 (Noēsis)
  ↓
[STEP 1] 方法候補の生成
  ├─ 既知パターン: 過去の成功方法
  ├─ 推奨方法: ベストプラクティス
  └─ 新規方法: 革新的アプローチ
  ↓
[STEP 2] 方法の評価
  ├─ 目的整合性 (X-SK5)
  ├─ 知識充足度 (X-SK6)
  └─ 直感チェック (X-SH3)
  ↓
[STEP 3] ズーム伝播の確認
  └─ 方法のスケールが P, K, H にどう影響するか
  ↓
出力: [方法選択, 根拠, 伝播影響]
```

## X-series 接続

> S2 は S1 と並ぶズームチェーン起点。6本の出力射を持つ。

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-OS2 | O1 Noēsis | 本質理解→どの方法で実装するか | `/noe >> /mek` |
| X-OS4 | O2 Boulēsis | 目的定義→達成手段を設計する | `/bou >> /mek` |

### 出力射 (6本)

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-SP5 | P3 Trokhia | 方法の粒度→サイクル設計 (構造層) | `/mek >> /tro` |
| X-SP6 | P4 Tekhnē | 方法の粒度→技法選択 (構造層) | `/mek >> /tek` |
| X-SK5 | K3 Telos | 方法の粒度→目的整合 (構造層) | `/mek >> /tel` |
| X-SK6 | K4 Sophia | 方法の粒度→知恵充足 (構造層) | `/mek >> /sop` |
| X-SH3 | H1 Propatheia | 方法→「これでいける」の直感 (反省層) | `/mek >> /pro` |
| X-SH4 | H2 Pistis | 方法→方法への確信度 (反省層) | `/mek >> /pis` |

## CCL 使用例

```ccl
# 目的→方法設計
/bou+{goal: "Phase D1"} >> /mek+{select: true}

# 方法→確信チェック
/mek+{method: "batch enrichment"} >> /pis{honest: true}

# 方法→目的整合
/mek+{plan: "ready"} >> /tel{verify: "手段は目的に向かっているか"}

# /mek+ (詳細) = 詳細な方法分析
# /mek- (簡潔) = 方法を一行で選択
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 認識なしに方法を選ぶ | X-OS2/4 が必要。O→S の因果を飛ばさない |
| ズーム伝播を無視 | 6方向に影響する。全ての影響を確認 |
| 方法と技法を混同 | Mekhanē = アプローチ、Tekhnē = ツール |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| comp | `/mek.comp` | 方法の構成要素分析 |
| inve | `/mek.inve` | 方法の逆転 (反対のアプローチ) |
| adap | `/mek.adap` | 方法の適応 (文脈に合わせる) |

---

*Mekhanē: 古代ギリシャにおける「機械・仕掛け・手段」*
*v3.0: ズームチェーン起点 + Tekhnē区別 + 6出力射 (2026-02-07)*
