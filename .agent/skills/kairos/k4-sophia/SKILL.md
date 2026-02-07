---
# Theorem Metadata (v3.0)
id: "K4"
name: "Sophia"
greek: "Σοφία"
series: "Kairos"
generation:
  formula: "Function × Precision"
  result: "機能精密 — 知恵の探求・調査"

description: >
  何を調べるべき？・知恵は足りているか？・外部知識が必要な時に発動。
  Wisdom seeking, research invocation, knowledge sufficiency check.
  Use for: 調査, 知恵, 研究, research, wisdom, 十分か.
  NOT for: verified knowledge (検証済み知識 → Epistēmē A4).

triggers:
  - 外部調査の必要性
  - 知識の不足感
  - Perplexity/論文検索の起点
  - /sop コマンド

keywords: [sophia, wisdom, research, investigation, 知恵, 調査]

related:
  upstream:
    - "S2 Mekhanē (X-SK6: 方法→知恵の充足度)"
    - "S4 Praxis (X-SK8: 実践→知識の充足度)"
    - "P3 Trokhia (X-PK6: サイクル→反復に必要な知恵)"
    - "P4 Tekhnē (X-PK8: 技法→必要な知識)"
    - "H2 Pistis (X-HK6: 確信→「何を知るべきか」を決定)"
    - "H4 Doxa (X-HK8: 信念→知恵の源泉を選ぶ ⚠️)"
  downstream:
    - "A3 Gnōmē (X-KA7: 知恵→格言抽出)"
    - "A4 Epistēmē (X-KA8: 知恵→体系的知識昇格)"

version: "3.0.0"
workflow_ref: ".agent/workflows/sop.md"
risk_tier: L2
reversible: true
requires_approval: false
risks:
  - "確証バイアス: 信念が知恵の源泉を選り好み (X-HK8)"
---

# K4: Sophia (Σοφία)

> **生成**: Function × Precision
> **役割**: 知恵を探求し、知識の充足度を評価する
> **認知的意味**: 「十分に知っているか」— 知識ギャップの自覚

## Epistēmē (A4) との区別

| | Sophia (K4) | Epistēmē (A4) |
|:--|:-----------|:--------------|
| 層 | Kairos (文脈) | Akribeia (精密) |
| 性質 | **文脈依存**。状況による知恵 | **文脈独立**。検証済み事実 |
| 問い | 「この状況で何を知るべきか」 | 「これは知識として確立できるか」 |
| 出力 | 調査結果、洞察 | 形式的知識宣言 |

## Processing Logic

```
入力: 知識ギャップの認識
  ↓
[STEP 1] 充足度チェック
  ├─ 十分: 現在の知識で行動可能
  ├─ 不足: 調査が必要
  └─ 不明: 何が不足かもわからない
  ↓
[STEP 2] 調査戦略 (不足時)
  ├─ 内部: Gnōsis RAG (ベクトル検索)
  ├─ 外部: Perplexity / 論文検索
  └─ 対話: Creator に質問
  ↓
[STEP 3] バイアスチェック
  ├─ X-HK8: 信念が情報源を偏らせていないか
  └─ 確証バイアス: 都合の良い情報だけ集めていないか
  ↓
出力: [調査結果, 知識充足度, 次ステップ]
```

## X-series 接続

> K4 は6入力を受ける。確証バイアスリスクあり。

### 入力射 (6本)

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-SK6 | S2 Mekhanē | 方法の粒度→知恵の粒度 (構造層) | `/mek >> /sop` |
| X-SK8 | S4 Praxis | 実践の粒度→知識の粒度 (構造層) | `/pra >> /sop` |
| X-PK6 | P3 Trokhia | サイクル→知恵のスケール (構造層) | `/tro >> /sop` |
| X-PK8 | P4 Tekhnē | 技法→知識のスケール (構造層) | `/tek >> /sop` |
| X-HK6 | H2 Pistis | 確信→知るべきことを決定 (反省層) | `/pis >> /sop` |
| X-HK8 ⚠️ | H4 Doxa | 信念→知恵の源泉の選好 (反省層) | `/dox >> /sop` |

### 出力射

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-KA7 | A3 Gnōmē | 知恵→格言を抽出 | `/sop >> /gno` |
| X-KA8 | A4 Epistēmē | 知恵→知識に昇格 | `/sop >> /epi` |

## CCL 使用例

```ccl
# 方法選択後の知識充足チェック
/mek+{plan: "ready"} >> /sop{check: "knowledge_gap?"}

# Perplexity 調査依頼
/sop+{topic: "Markov blanket boundaries", source: "perplexity"}

# 知恵→知識昇格パイプライン
/sop{research: "done"} >> /epi{formalize: true}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 信念で情報源を選ぶ | X-HK8 の確証バイアス。多様な情報源を探る |
| 調査なしに行動する | 知識ギャップの無自覚は危険 |
| 知恵 = 知識と混同 | Sophia は文脈依存、Epistēmē は文脈独立 |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| deep | `/sop.deep` | 深掘り調査 (Perplexity) |
| quick | `/sop.quick` | 簡易知識チェック |
| gap | `/sop.gap` | 知識ギャップ分析 |

---

*Sophia: 古代ギリシャにおける「知恵・叡智」*
*v3.0: 6入力射 + 確証バイアス検出 + Epistēmē区別 (2026-02-07)*
