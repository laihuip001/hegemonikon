---
# Theorem Metadata (v3.0)
id: "K3"
name: "Telos"
greek: "Τέλος"
series: "Kairos"
generation:
  formula: "Function × Explore"
  result: "機能探索 — 目的の確認と自問"

description: >
  何のためにやっている？・目的を自問したい・手段と目的が入れ替わっていないか？時に発動。
  Purpose verification, means-ends check, goal alignment.
  Use for: 目的, 何のため, why, purpose.
  NOT for: desire (欲求 → Orexis H3), knowledge (知識 → Sophia K4).

triggers:
  - 目的の自問
  - 手段と目的の入れ替わり防止
  - Why の連鎖
  - /tel コマンド

keywords: [telos, purpose, goal, end, finality, 目的, 何のため]

related:
  upstream:
    - "S2 Mekhanē (X-SK5: 方法→目的整合性)"
    - "S4 Praxis (X-SK7: 実践→目的整合性)"
    - "P3 Trokhia (X-PK5: サイクル→反復の目的)"
    - "P4 Tekhnē (X-PK7: 技法→目的整合性)"
    - "H1 Propatheia (X-HK2: 直感→目的修正)"
    - "H3 Orexis (X-HK4: 欲求→目的書き換え ⚠️)"
  downstream:
    - "A3 Gnōmē (X-KA5: 目的→原則演繹)"
    - "A4 Epistēmē (X-KA6: 目的→必要知識確定)"

version: "3.0.0"
workflow_ref: ".agent/workflows/tel.md"
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "欲求による目的上書き (X-HK4)"
  - "手段の目的化"
---

# K3: Telos (Τέλος)

> **生成**: Function × Explore
> **役割**: 「何のために」を問い続ける
> **認知的意味**: 手段と目的の入れ替わりを防ぐ自問ツール

## When to Use

### ✓ Trigger

- 「これ何のためにやってるんだっけ」
- 手段が目的化している疑い
- Five Whys (/why) の起点
- 行動の正当性確認

### ✗ Not Trigger

- 欲求の同定 → `/ore`
- 知恵の探求 → `/sop`

## Processing Logic

```
入力: 現在の活動 / 手段
  ↓
[STEP 1] 目的の問い
  ├─ L1: 「何のためにこれをしているか」
  ├─ L2: 「その目的のさらに上の目的は」
  └─ L3: 「最終的に何に至るか」
  ↓
[STEP 2] 手段-目的の整合性チェック
  ├─ 整合: 手段は目的に向かっている
  ├─ 漂流: 手段が目的から離れている
  └─ 転倒: 手段が目的になっている ⚠️
  ↓
[STEP 3] 欲求バイアスチェック
  ├─ X-HK4: 欲求が目的を書き換えていないか
  └─ 元の目的と現在の目的は同一か
  ↓
出力: [目的確認, 整合/漂流/転倒, 修正提案]
```

## X-series 接続

> **自然度**: 反省（注意を向ければ気づく）

### 入力射 (6本)

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-SK5 | S2 Mekhanē | 方法の粒度→目的の粒度 (構造層) | `/mek >> /tel` |
| X-SK7 | S4 Praxis | 実践の粒度→目的の粒度 (構造層) | `/pra >> /tel` |
| X-PK5 | P3 Trokhia | サイクルのスケール→目的のスケール (構造層) | `/tro >> /tel` |
| X-PK7 | P4 Tekhnē | 技法のスケール→目的のスケール (構造層) | `/tek >> /tel` |
| X-HK2 | H1 Propatheia | 直感→直感が目的を修正 | `/pro >> /tel` |
| X-HK4 ⚠️ | H3 Orexis | 欲求→欲求が目的を書き換える | `/ore >> /tel` |

### 出力射

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-KA5 | A3 Gnōmē | 目的→目的から原則を演繹 | `/tel >> /gno` |
| X-KA6 | A4 Epistēmē | 目的→必要な知識の確定 | `/tel >> /epi` |

## CCL 使用例

```ccl
# 定期的な目的自問
/tel{ask: "96体系の充実は何のためか"}

# 手段-目的の整合性チェック
/mek{method: "D1 Skill充実"} >> /tel{verify: "手段は目的に向かっているか"}

# Five Whys
/tel{level: "L1"} >> /tel{level: "L2"} >> /tel{level: "L3"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 目的を後付けする | 行動→正当化 は逆。目的→行動 |
| 欲求で目的を書き換える | X-HK4 のバイアス。「欲しいから」≠「目的だから」 |
| 常に Why を問い続ける | 分析麻痺。3層 (L1-L3) で止める |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| why | `/tel.why` | Five Whys (根本目的到達) |
| align | `/tel.align` | 手段-目的整合チェック |
| drift | `/tel.drift` | 目的漂流の検出 |

---

*Telos: アリストテレスにおける「目的・終極・完成」*
*v3.0: 6入力射 + バイアスチェック統合 (2026-02-07)*
