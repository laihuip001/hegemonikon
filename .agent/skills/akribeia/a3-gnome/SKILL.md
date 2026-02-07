---
# Theorem Metadata (v3.0)
id: "A3"
name: "Gnōmē"
greek: "Γνώμη"
series: "Akribeia"
generation:
  formula: "Explore × Valence"
  result: "探索傾向 — 原則・教訓の抽出"

description: >
  教訓は何か？・原則を抽出したい・格言として定式化したい時に発動。
  Principle extraction, lesson learned, maxim formulation.
  Use for: 教訓, 原則, 格言, principle, lesson.
  NOT for: raw knowledge (知識 → Epistēmē A4), desire (欲求 → Orexis H3).

triggers:
  - 原則の抽出
  - 教訓の言語化
  - 「この経験から学んだことは」
  - /gno コマンド

keywords: [gnome, maxim, principle, lesson, 格言, 原則, 教訓]

related:
  upstream:
    - "H2 Pistis (X-HA5: 確信→原則抽出)"
    - "H4 Doxa (X-HA7: 信念→教訓を引き出す)"
    - "K3 Telos (X-KA5: 目的→原則演繹)"
    - "K4 Sophia (X-KA7: 知恵→格言抽出)"
  downstream: []

version: "3.0.0"
workflow_ref: ".agent/workflows/gno.md"
risk_tier: L1
reversible: true
requires_approval: false
---

# A3: Gnōmē (Γνώμη)

> **生成**: Explore × Valence
> **役割**: 経験から原則・教訓を抽出する
> **認知的意味**: 「このことから何を学んだか」を格言にする

## 体系上の位置

Gnōmē は Akribeia (精密層) の教訓軸であり、**体系の教訓的終端**。
Epistēmē (知識) が事実を扱うのに対し、Gnōmē は**行動指針**を扱う。

| 概念 | 定理 | 出力 |
|:-----|:-----|:-----|
| 知識 | A4 Epistēmē | 「Xは真である」 |
| **教訓** | **A3 Gnōmē** | **「Xすべきである」** |

## Processing Logic

```
入力: 経験 / 信念 / 目的
  ↓
[STEP 1] 出来事の要約
  ├─ 何が起きたか
  ├─ 何が予想と違ったか
  └─ 何がうまくいったか
  ↓
[STEP 2] 原則の抽出
  ├─ 一般化: 特定事例 → 汎用原則
  ├─ 制約条件: いつこの原則が適用されるか
  └─ 反例: この原則が成り立たない場合は
  ↓
[STEP 3] 格言への定式化
  ├─ 1行サマリー (格言)
  ├─ 根拠 (なぜこう言えるか)
  └─ 適用範囲 (どこまで有効か)
  ↓
出力: [格言, 根拠, 適用範囲]
```

## X-series 接続

> **自然度**: mixed（入力は反省層、出力はなし = 終端）

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-HA5 | H2 Pistis | 確信→確信から原則を抽出 | `/pis >> /gno` |
| X-HA7 | H4 Doxa | 信念→信念から教訓を引き出す | `/dox >> /gno` |
| X-KA5 | K3 Telos | 目的→目的から原則を演繹 | `/tel >> /gno` |
| X-KA7 | K4 Sophia | 知恵→知恵から格言を抽出 | `/sop >> /gno` |

### 出力射

**なし** — Gnōmē は体系の教訓的終端。出力は Doxa ファイルや格言集への永続化。

## CCL 使用例

```ccl
# 信念から教訓を抽出
/dox{belief: "ズームレベルの伝播"} >> /gno{extract: true}

# 目的から原則を演繹
/tel{purpose: "96体系"} >> /gno{deduce: "設計原則"}

# 知恵→格言
/sop{research: "FEP"} >> /gno{formulate: "格言"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 経験なしに格言を作る | 空虚な一般化。入力射 (Doxa/Pistis) からの経験が必要 |
| 格言を知識と混同 | Gnōmē = 「すべき」, Epistēmē = 「である」 |
| 反例を無視する | 原則には適用範囲がある。「常に」は疑う |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| extract | `/gno.extract` | 経験から抽出 |
| analogy | `/gno.analogy` | アナロジーで原則化 |
| critique | `/gno.critique` | 既存原則の批判 |

---

*Gnōmē: 古代ギリシャにおける「格言・判断力・意見」*
*v3.0: 終端概念 + Epistēmēとの区別 (2026-02-07)*
