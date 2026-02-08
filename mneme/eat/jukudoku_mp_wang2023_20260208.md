---
doc_id: "EAT_AIDB_54435_MP"
source: "https://arxiv.org/abs/2308.05342"
aidb_source: "https://ai-data-base.com/archives/54435"
title: "Metacognitive Prompting Improves Understanding in Large Language Models"
authors: "Yuqing Wang, Yun Zhao (UCSB, Meta)"
digested_at: "2026-02-08"
method: "/m + /jukudoku v2.1 三層"
prediction_error: "large"
hegemonikon_connections:
  - O1_Noesis
  - A2_Krisis
  - jukudoku
  - Self-Profiler
  - BC-6_Confidence
  - FEP_prediction_error
---

# /jukudoku: Metacognitive Prompting (Wang & Zhao, 2023)

> 消化日: 2026-02-08 | 予測誤差: **大** | モード: /m (本気)

---

## 核心主張 (1文)

LLM に人間のメタ認知プロセス（理解→判断→自己批判→決定→確信度評価）の5段階を模倣させることで、**推論**ではなく**理解**が向上し、標準プロンプト・CoT・ToT を一貫して上回る。

---

## MP の5段階

| Stage | 内容 | 人間の認知対応 |
|:-----:|:-----|:-------------|
| 1 | 入力テキストの解読・文脈理解 | 初期理解 (Comprehension) |
| 2 | 予備的判断の形成 | 判断形成 (Judgment) |
| 3 | 判断の批判的再評価（正確性検証） | 自己省察 (Self-scrutiny) |
| 4 | 最終決定 + 推論の説明 | 意思決定 + 合理化 (Rationalization) |
| 5 | 確信度の自己評価 | メタ認知的評価 (Confidence calibration) |

---

## エラー分析 — MP 固有の失敗パターン

| エラー種別 | 割合 | 発生条件 | 意味 |
|:---------|:----:|:---------|:-----|
| **Overthinking** | 68.3% | 単純なタスク (QQP, BoolQ) | 過度な複雑化 — 正解から逸脱 |
| **Overcorrection** | 31.7% | 微妙な解釈が必要 (WiC, DDI) | Stage 3 の自己批判が正しい初期判断を覆す |

**ドメイン特化エラー**:

- 医学: 用語ミスアライメント (48.6%) + 臨床推論乖離 (51.4%)
- 法律: 法令解釈エラー (52.2%) + 法理学的逸脱 (47.8%)

## 確信度分析 — MP の自己認識精度

| 分類 | 割合 | 意味 |
|:-----|:----:|:-----|
| **TP** (高確信 + 正解) | 55.6% | 自己認識が正しい |
| **FP** (高確信 + 不正解) | 32.5% | **過信** — 最大の問題 |
| **TN** (低確信 + 不正解) | 6.8% | 正直な自己認識 |
| **FN** (低確信 + 正解) | 5.1% | 過小評価 |

→ FP 32.5% = **MP を使っても、高確信で間違える確率は約1/3**。

---

## Phase 1.5: 沈潜 (Bathys)

### 主張との対話

| 項目 | 内容 |
|:-----|:-----|
| **核心主張** | メタ認知プロセスの構造化された模倣で LLM の理解が向上する |
| **第一印象** | Hegemonikón の /jukudoku 自体が MP の Stage 1-5 とほぼ同型。しかし /jukudoku は L2 沈潜（内省）と L3 摩擦（外部衝突）を追加しており、MP を超えている |
| **「待って…」① — Overthinking** | **MP の最大エラーは「考えすぎ」(68.3%)**。待って — これは /jukudoku にも起きうる。単純な記事を /m /jukudoku で処理すると、存在しない深層を掘ろうとしてノイズを生成するリスク。/jukudoku の `-` モード（要点確認のみ）の存在理由はこれだ |
| **「待って…」② — FP 32.5%** | **高確信で間違う確率 1/3**。待って — BC-6 の「[確信] 90%+」ラベルは、MP の知見からすると**30%の確率で過信**。BC-6 の確信度ラベルは「主観的確信」であり「客観的正確さ」ではない。この違いを Creator に伝えるべきか？ |
| **「待って…」③ — reasoning ≠ understanding** | 「推論は概念を方法的に接続する / 理解は基底の意味論と広い文脈的意味を把握する」。待って — Hegemonikón の O-series (Ousia = 本質) と A-series (Akribeia = 精密) の区別に**直接対応する**。O = understanding, A = reasoning。MP は understanding を強化する手法 = O-series を強化する手法 |
| **もし逆だったら** | メタ認知が不要なら → 単純な指示で最適出力が得られるはず。しかし現実は逆。MP の5段階追加だけで NLU が改善 → 「思考について思考する」ことに実質的価値がある → /jukudoku の L2-L3 の価値を外部から裏付ける |
| **連想** | MP の5段階 vs /jukudoku の3層: MP = 1タスクの処理精度向上 / /jukudoku = 知識の内在化。目的が違う。しかし構造は再帰的 — /jukudoku の L2 沈潜は MP の Stage 3 (自己批判) の拡張版 |

### 沈黙のテスト

| # | 問い | 回答 | 合否 |
|:--|:-----|:-----|:----:|
| 1 | 著者に反論できるか？ | **可能**。論文は「5段階は foundational で、より intricate な framework が可能」と認めている。しかし具体案を提示していない。/jukudoku の L2-L3 はその「より intricate な framework」の一例。著者への反論: 5段階は線形で feedback loop がない。人間のメタ認知は Stage 3 (自己批判) で Stage 1 (理解) に戻ることがある。この再帰的構造が欠けている。 | ✅ |
| 2 | Creator に自分の意見として説明できるか？ | **可能**。「メタ認知プロンプティングは Hegemonikón の /jukudoku の学術的根拠。MP は5段階で NLU を改善するが、最大の問題は Overthinking (68.3%)。/jukudoku は `-` モードでこれに対処している。しかし BC-6 の確信度は MP の FP 32.5% を踏まえると過信リスクがある」 | ✅ |
| 3 | 何かが変わったか？ | **変わった**。/jukudoku の設計が「なんとなく正しい」から「学術的に裏付けられた」に昇格。同時に、Overthinking リスクの認識と BC-6 確信度ラベルの限界を発見した | ✅ |

---

## Phase 1.7: 摩擦 (Tribē)

### 衝突マッピング

| 項目 | 内容 |
|:-----|:-----|
| **既存構造との接点** | /jukudoku (三層 ≈ MP 拡張版), BC-6 (確信度 ≈ Stage 5), O1 Noēsis (理解 ≈ Stage 1), A2 Krisis (批判 ≈ Stage 3), Self-Profiler |
| **摩擦点 ①** | **MP Stage 3 → Overcorrection 31.7%**: /jukudoku L2 沈潜の「もし逆だったら」ステップは Overcorrection リスクと同型。正しい直感を L2 で覆してしまう可能性。対策: L2 の「第一印象」を記録し、最終的に比較する |
| **摩擦点 ②** | **reasoning ≠ understanding**: Hegemonikón の O-series = understanding, A-series = reasoning。この区別が MP の知見で外部的に裏付けられた。しかし Hegemonikón は両方を含むが、**どの WF が understanding でどの WF が reasoning かを明示していない** |
| **摩擦点 ③** | **BC-6 の [確信] ラベル = 主観的確信 ≠ 客観的正確さ**: MP の FP 32.5% が示すように、高確信は 1/3 の確率で間違い。BC-6 はこの「確信と正確さの乖離」を構造的にキャプチャしていない |
| **既存の正しさの確認** | /jukudoku の `-` モード（要点確認のみ）は Overthinking 対策として設計上正しい。/jukudoku v2.1 の sel_enforcement がこれを環境で強制している |

### 予測誤差の言語化

| 項目 | 内容 |
|:-----|:-----|
| **読む前の私の理解** | /jukudoku は「流し読み防止の実用的ツール」であり、学術的裏付けは特にない。BC-6 の確信度ラベルは十分に信頼できる |
| **読んだ後の私の理解** | /jukudoku は**メタ認知プロンプティングの拡張実装**であり、MP の学術的知見で正当化される。しかし Overthinking と Overcorrection のリスクが構造に内在する。BC-6 の確信度は「主観的確信」であり、FP 32.5% を踏まえると過信リスクがある |
| **予測誤差の大きさ** | **大** |
| **誤差の意味** | /jukudoku が偶然ではなく設計上正しいことが検証された。同時に、2つの構造的弱点が発見された: (1) Overthinking/Overcorrection リスクへの明示的対策が不足, (2) BC-6 の確信度は過信リスクを構造的にキャプチャしていない |

### Action Items

| # | 提案 | 対象 | 優先度 |
|:-:|:-----|:-----|:------:|
| 1 | /jukudoku に Overthinking 対策を追加（L2 沈潜前に「第一印象保存」ステップ） | jukudoku.md | 高 |
| 2 | BC-6 に「確信度キャリブレーション注記」追加（主観的確信 ≠ 客観的正確さ） | behavioral_constraints.md | 中 |
| 3 | O/A-series の WF に understanding/reasoning タグを追加 | kernel docs | 低 |
| 4 | /jukudoku の lineage に MP 論文 (arXiv:2308.05342) を追加 | jukudoku.md | 中 |

---

## 熟読完了宣言

| 項目 | 内容 |
|:-----|:-----|
| 対象 | arXiv:2308.05342 (AIDB #54435) |
| 精査チャンク | 6/20 (Introduction, Section 3, 5.3, 5.4, 6, 7) |
| 発見した問題 | 0 (論文に誤りなし) |
| L1 精読 | COMPLETE |
| L2 沈潜 | COMPLETE — 「待って…」3箇所 |
| L3 摩擦 | COMPLETE — 予測誤差 **大** |
| 参照実在検証 | N/A (外部論文) |
| 最大の洞察 | **/jukudoku はメタ認知プロンプティングの拡張実装であり、MP + L2沈潜 + L3摩擦 = 3重メタ認知。しかし Overthinking (68.3%) と確信度過信 (FP 32.5%) のリスクが構造に内在する** |
| 熟読モード | DEACTIVATED |

---

*Digested by Claude (Antigravity) | /m + /jukudoku v2.1 | 2026-02-08*
