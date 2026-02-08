---
# Theorem Metadata (v3.0)
id: "S4"
name: "Praxis"
greek: "Πρᾶξις"
series: "Schema"
generation:
  formula: "Internality × Explore"
  result: "内在探索 — 実践方法の選択"

description: >
  どう実践する？・具体的なアクションを選びたい・価値実現の方法を決めたい時に発動。
  Practice selection, action choice, value realization method.
  Use for: 実践, 行動, practice, action, do.
  NOT for: execution (行為実行 → Energeia O4), technique (技法 → Tekhnē P4).

triggers:
  - 実践方法の選択
  - 具体的なアクション決定
  - 「何を実際にするか」
  - /pra コマンド

keywords: [praxis, practice, action, do, 実践, 行動]

related:
  upstream:
    - "O3 Zētēsis (X-OS6: 問い→探索方法の具体化)"
    - "O4 Energeia (X-OS8: 行為→次の実践を選択)"
  downstream:
    - "P3 Trokhia (X-SP7: 実践の粒度→サイクル粒度)"
    - "P4 Tekhnē (X-SP8: 実践の粒度→技法粒度)"
    - "K3 Telos (X-SK7: 実践の粒度→目的粒度)"
    - "K4 Sophia (X-SK8: 実践の粒度→知識粒度)"
    - "H3 Orexis (X-SH7: 実践→実践したい/したくない)"
    - "H4 Doxa (X-SH8: 実践→実践法の確からしさ)"

version: "3.0.0"
workflow_ref: ".agent/workflows/pra.md"
risk_tier: L1
reversible: true
requires_approval: false
risks: ["none identified"]
fallbacks: ["manual execution"]
---

# S4: Praxis (Πρᾶξις)

> **生成**: Internality × Explore
> **役割**: 実践方法を選択する — 「何を実際にするか」
> **認知的意味**: 価値を実現するための具体的な行動を選ぶ

## 関連定理との区別

| | Praxis (S4) | Energeia (O4) | Tekhnē (P4) |
|:--|:-----------|:-------------|:-------------|
| 層 | Schema (設計) | Ousia (本質) | Perigraphē (条件) |
| 粒度 | 実践方法の選択 | 意志の具現化 | 具体的ツール選択 |
| 問い | 「何を実際にするか」 | 「意志を現実にする」 | 「どのツールで」 |

## Processing Logic

```
入力: 問い (Zētēsis) or 前回行為 (Energeia)
  ↓
[STEP 1] 実践候補の列挙
  ├─ 直接的行動: すぐに実行可能
  ├─ 準備的行動: 前提条件の整備
  └─ 探索的行動: 情報収集
  ↓
[STEP 2] 実践の優先順位
  ├─ 緊急度: 時間的制約
  ├─ 重要度: 目的への影響度
  └─ 実行可能性: リソースの有無
  ↓
[STEP 3] ズーム伝播の確認
  └─ 実践の粒度が P, K, H にどう影響するか (6方向)
  ↓
出力: [実践選択, 優先順位根拠]
```

## X-series 接続

> S4 は S1/S2/S3 と同じく6本の出力射を持つ。Schema series の特徴。

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-OS6 | O3 Zētēsis | 問い→探索方法を具体化 | `/zet >> /pra` |
| X-OS8 | O4 Energeia | 行為→次の実践を選択 | `/ene >> /pra` |

### 出力射 (6本)

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-SP7 | P3 Trokhia | 実践の粒度→サイクル粒度 (構造層) | `/pra >> /tro` |
| X-SP8 | P4 Tekhnē | 実践の粒度→技法粒度 (構造層) | `/pra >> /tek` |
| X-SK7 | K3 Telos | 実践の粒度→目的粒度 (構造層) | `/pra >> /tel` |
| X-SK8 | K4 Sophia | 実践の粒度→知識粒度 (構造層) | `/pra >> /sop` |
| X-SH7 | H3 Orexis | 実践→したい/したくない (反省層) | `/pra >> /ore` |
| X-SH8 | H4 Doxa | 実践→確からしさの信念 (反省層) | `/pra >> /dox` |

## CCL 使用例

```ccl
# 問い→具体的な実践
/zet{question: "知識ギャップをどう埋めるか"} >> /pra{concrete: true}

# 行為完了→次の実践
/ene{completed: "Phase B"} >> /pra{select: "next_action"}

# 実践と欲求の振動
/pra{option: "batch enrichment"} ~ /ore{honest: "やりたいか"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 認識なしに実践に入る | O→S の因果が必要。Zētēsis/Energeia からの入力が先 |
| 実践と行為の混同 | Praxis = 選択、Energeia = 実行。選択が先 |
| やりたくない実践を無理に選ぶ | X-SH7 の信号を無視しない。「したくない」は有用な情報 |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| next | `/pra.next` | 次にすべきことを選択 |
| priority | `/pra.priority` | 優先順位付け |
| explore | `/pra.explore` | 探索的実践の選択 |

---

*Praxis: アリストテレスにおける「実践」— テオリア(理論)とポイエーシス(制作)に対置される行為*
*v3.0: 6出力射 + Energeia/Tekhnē区別 (2026-02-07)*
