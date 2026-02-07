---
# Theorem Metadata (v3.0)
id: "A4"
name: "Epistēmē"
greek: "Ἐπιστήμη"
series: "Akribeia"
generation:
  formula: "Explore × Precision"
  result: "探索精密 — 検証済み知識"

description: >
  知識として確立できるか？・信念を検証したい・確信→知識昇格の時に発動。
  Knowledge establishment, belief verification, epistemic elevation.
  Use for: 知識, 確立, verify, knowledge, 検証済み.
  NOT for: unverified beliefs (信念 → Doxa H4), wisdom (知恵 → Sophia K4).

triggers:
  - 知識の確立/検証
  - 信念→知識の昇格
  - エビデンスの統合
  - /epi コマンド

keywords: [episteme, knowledge, science, verified, 知識, 検証, 確立]

related:
  upstream:
    - "H2 Pistis (X-HA6: 確信→知識昇格)"
    - "H4 Doxa (X-HA8: 信念→検証済み知識化)"
    - "K3 Telos (X-KA6: 目的→必要知識の確定)"
    - "K4 Sophia (X-KA8: 知恵→体系的知識昇格)"
  downstream: []

version: "3.0.0"
workflow_ref: ".agent/workflows/epi.md"
risk_tier: L2
reversible: false
requires_approval: true
risks:
  - "偽陽性の知識確立 (未検証のまま知識と宣言)"
---

# A4: Epistēmē (Ἐπιστήμη)

> **生成**: Explore × Precision
> **役割**: 信念を検証済み知識に昇格する
> **認知的意味**: 「これは知識と呼べるか」— 体系の最終出力の一つ

## 体系上の位置

Epistēmē は Akribeia (精密層) の知識軸であり、**体系の知識的終端**。
Doxa (信念) → Pistis (確信) → Epistēmē (知識) の昇格パイプラインの最終段。

| 概念 | 定理 | 層 | 特性 |
|:-----|:-----|:---|:-----|
| 信念 | H4 Doxa | Hormē | 未検証。主観的 |
| 確信 | H2 Pistis | Hormē | 主観的確信。検証不十分 |
| **知識** | **A4 Epistēmē** | Akribeia | **検証済み。文脈独立** |
| 知恵 | K4 Sophia | Kairos | 文脈依存。経験的  |

## Processing Logic

```
入力: 信念/確信/仮説
  ↓
[STEP 1] 検証可能性チェック
  ├─ 検証可能: テスト/エビデンスで確認できる
  └─ 検証不可: 未検証のまま Doxa に留める
  ↓
[STEP 2] エビデンス統合
  ├─ 論理的整合性: 他の確立済み知識と矛盾しないか
  ├─ 経験的支持: 実際に試して確認したか
  └─ 反証可能性: 何を見れば棄却できるか
  ↓
[STEP 3] 昇格判定
  ├─ ESTABLISH: 知識として確立
  ├─ PROVISIONAL: 暫定知識 (追加検証必要)
  └─ REJECT: Doxa に差し戻し
  ↓
出力: [知識宣言, エビデンス, 反証条件]
```

## X-series 接続

> **自然度**: mixed（入力は反省層、出力はなし = 終端）

### 入力射 (4本 — 全て Epistēmē に収斂する)

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-HA6 | H2 Pistis | 確信→知識に昇格 | `/pis >> /epi` |
| X-HA8 | H4 Doxa | 信念→検証済み知識にする | `/dox >> /epi` |
| X-KA6 | K3 Telos | 目的→必要な知識の確定 | `/tel >> /epi` |
| X-KA8 | K4 Sophia | 知恵→体系的知識に昇格 | `/sop >> /epi` |

### 出力射

**なし** — Epistēmē は体系の知識的終端。出力は KI (Knowledge Item) やファイルへの永続化。

## CCL 使用例

```ccl
# 信念→知識昇格
/dox{belief: "CCL は推論サイクルである"} >> /epi{verify: true}

# 確信→知識昇格パイプライン
/pis{score: 0.9} >> /epi{formalize: true}

# 目的から必要知識を確定
/tel{purpose: "FEP formal validation"} >> /epi{identify: "required_knowledge"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 確信 = 知識と混同 | Pistis ≠ Epistēmē。確信は主観、知識は検証済み |
| 知恵 = 知識と混同 | Sophia ≠ Epistēmē。知恵は文脈依存、知識は文脈独立 |
| 検証なしに知識宣言 | 偽陽性。昇格には STEP 2 の検証が必須 |
| 全てを知識にしようとする | Doxa (信念) のまま保持する価値もある |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| verify | `/epi.verify` | 検証プロセス実行 |
| formalize | `/epi.formalize` | 知識の形式的記述 |
| connect | `/epi.connect` | 既存知識との接続 |

---

*Epistēmē: 古代ギリシャにおける「科学的知識・確実な認識」*
*v3.0: 知識昇格パイプライン + 終端概念 (2026-02-07)*
