---
name: FEP Cognitive Engine
description: |
  FEP (自由エネルギー原理) に基づく認知設計原理。
  「全てを説明する理論」ではなく「行動選択の objective」として FEP を使う。
  VFE/EFE の数学的分解、精度加重の操作的定義、HGK 体系との対応を含む。

triggers:
  - "FEP"
  - "自由エネルギー"
  - "認知"
  - "意思決定"
  - "予測誤差"
  - "能動推論"
  - "active inference"
  - "EFE"
  - "precision"
  - "精度加重"
  - "attractor"
  - "series"

version: "2.0.0"
lineage: |
  v1.1 (手順のみ) → /sop deep 15論点50論文調査 (2026-02-10) → /noe+ 3命題抽出 → v2.0
risk_tier: L1
risks:
  - Low impact info-only skill

---

# FEP Cognitive Engine v2.0

> τέχνη (Tekhne) の上に立つ σοφία (Sophia)
>
> FEP は「全てを説明する魔法」ではない。
> FEP は「行動選択の objective function」として最も力を発揮する設計原理である。

---

## Layer 0: 哲学的基盤 — なぜ FEP か

### 3つの命題

| # | 命題 | 根拠 | HGK 帰結 |
|:--|:-----|:-----|:---------|
| **P1** | FEP は「設計原理」であり「説明理論」ではない | Ramstead 2024: 枠組みであり反証性は具体モデルレベル [oecs.mit](https://oecs.mit.edu/pub/my8vpqih) | HGK では行動選択の objective として使う。「FEP で説明した」は不十分 |
| **P2** | EFE の2項分解が Series 選択の数学的基盤 | Champion 2024: EFE = epistemic + pragmatic [arXiv:2402.14460](https://arxiv.org/abs/2402.14460) | O3 Zētēsis = epistemic, O4 Energeia = pragmatic。偶然ではなく導出 |
| **P3** | 精度は確信度ではない — だが橋渡しできる | Precision in Action review [PMC11431491](https://pmc.ncbi.nlm.nih.gov/articles/PMC11431491/) | BC-6 TAINT/SOURCE = 精度チャネルの健全性タグとして再解釈 |

### スコープ限定 — FEP を使うべき場所と使うべきでない場所

| ✅ 適用すべき | ❌ 適用すべきでない | なぜ |
|:-------------|:-------------------|:-----|
| Tool/WF 選択（行動選択が明確） | 単発 API 呼出し（ステートレス） | FEP はセンサモータループを前提 |
| Series 動的選択（attractor） | トークン生成そのもの | LLM 内部を FEP で直接モデルした研究なし (A1-4) |
| 確信度評価（精度推定） | 純粋記号操作 | 環境フィードバックなし = 能動推論の利点なし (D2-3) |
| Self-Profiler（自己モデル精度） | 「FEP だから正しい」論法 | トートロジーの罠 (D3) |

> **Aguilera 2021 の警告**: Markov blanket + ソレノイダルフロー制約が成り立つパラメータ領域は極めて狭い。
> 「任意のシステムに MB を仮定する」強い読みは不適切。[arXiv:2105.11203](https://arxiv.org/abs/2105.11203)

---

## Layer 1: 操作的定義 — 概念を「使える」レベルで

### 変分自由エネルギー (VFE)

```
F[q] = E_q[ln q(s) - ln p(o,s)]
     = - Accuracy + Complexity
     = 「予測の正確さ」と「モデルの単純さ」のトレードオフ
```

| 項 | 数学 | HGK での意味 |
|:---|:-----|:-------------|
| **Accuracy** | E_q[-ln p(o\|s)] | 予測と現実のズレ。低いほど良い |
| **Complexity** | KL(q(s) \|\| p(s)) | モデルが事前知識からどれだけ離れたか。低いほど単純 |

> **NLM/LLM との形式的対応** (Raffa & Acciai 2024):
> 学習時の NLL 損失 ≈ Accuracy 項、正則化 ≈ Complexity 項。
> ただし「LLM = FEP エージェント」ではなく「LLM の学習目的は VFE と形式的に類似」が正確。
> [CEUR-WS 2024](https://ceur-ws.org/Vol-3923/Paper_3.pdf)

### 期待自由エネルギー (EFE) — これが核心

```
G(π) = - Epistemic Value - Pragmatic Value
      = - 「知ることの価値」 - 「得ることの価値」
```

> **最小化の意味**: G(π) を**最小化**するので、Epistemic Value と Pragmatic Value が
> **大きい**ポリシーが選ばれる。つまり「情報利得が大きく、かつ報酬が高い行動」が最適。

| 項 | 意味 | HGK Series | 行動の例 |
|:---|:-----|:-----------|:---------|
| **Epistemic** | 情報利得。不確実性を下げる行動を促す | O3 Zētēsis | 追加調査, ツール呼出し, 質問 |
| **Pragmatic** | 報酬。好ましい結果に近づく行動を促す | O4 Energeia | コード実装, 成果物生成, 回答 |

> **ReAct/CoT との違い**: ReAct/CoT は epistemic と pragmatic を暗黙に混ぜている。
> EFE は明示的に分解し、「今は探索すべきか、実行すべきか」の設計思想を提供する。
> [arXiv:2509.05651](https://arxiv.org/html/2509.05651v1)

### 精度 (Precision) — 確信度との区別

| 概念 | 定義 | 数式 | HGK 対応 |
|:-----|:-----|:-----|:---------|
| **精度** | 予測誤差チャネルの信頼性ゲイン | Π = Σ⁻¹ （逆分散行列） | どの情報源をどれだけ信じるか |
| **確信度** | 出力の正しさの主観的確率 | P(correct) | BC-6 の [確信]/[推定]/[仮説] |

> **関係**: 精度は「チャネルの質」、確信度は「出力の質」。
> 高精度の情報源（view_file で確認 = SOURCE）からの出力は高確信度。
> 低精度の情報源（search_web 要約 = TAINT）のみの出力は低確信度。
> → **BC-6 の TAINT/SOURCE 追跡は、精度チャネルの健全性タグとして FEP 的に正当化される**

**過信と過少信の FEP 解釈**:

| 状態 | FEP 的意味 | LLM での現れ方 | 対処 |
|:-----|:-----------|:---------------|:-----|
| **過信** | 精度過大推定。チャネルを信じすぎ | 「間違いなく〇〇です」（根拠不足） | TAINT チェック。代替仮説を探す |
| **過少信** | 精度過小推定。何も信じない | 「わかりません」（情報はあるのに） | SOURCE を確認。持っている根拠を再評価 |

> **RLHF が過信を助長**: 報酬モデルは自信のある発話を好む傾向がある。
> [arXiv:2410.09724](https://arxiv.org/abs/2410.09724)

### Markov Blanket — 情報境界の操作的定義

LLM エージェントにおける Markov Blanket:

| 層 | 内容 |
|:---|:-----|
| **観測可能 (Sensory)** | ユーザメッセージ、ツール応答、ファイル内容、テスト結果 |
| **内部状態 (Internal)** | belief state（ゴール、タスク状態、自己モデル、精度推定） |
| **外部状態 (External)** | ユーザの本当の意図、未読ファイル、未実行テスト、外部世界 |
| **行動 (Active)** | ツール呼出し、ファイル編集、質問、提案 |

> **注意**: この定義は Prakki 2024 のアーキテクチャに基づく概念的対応。
> 厳密な Markov blanket の数学的条件（Aguilera 2021）を満たすかは未検証。[推定: 60%]

---

## Layer 2: HGK 対応 — 定理体系との接続

### 6 Series と FEP

| Series | FEP 対応 | 根拠 |
|:-------|:---------|:-----|
| **O (Ousia)** | 生成モデルの核。認識 (I×E) と行動 (A×P) の本質 | L0 FEP = L1 Flow × L1 Value から導出 (axiom_hierarchy.md) |
| **S (Schema)** | 方法の選択 = ポリシー空間の構造化 | L1 Flow × L1.5 Scale: ポリシー = 方法の離散表現 |
| **H (Hormē)** | 精度加重。どの予測誤差をどれだけ信じるか | conv_43: A-series = 精度加重の4段階。Precision in Action review |
| **P (Perigraphē)** | Markov blanket 境界の定義。スコープ設定 | Kirchhoff 2018: nested MB。L1.5 Scale × L1.5 Function |
| **K (Kairos)** | 文脈依存の精度調整。時間・状況 | EFE の planning horizon。L1.5 Scale × L1.75 Valence |
| **A (Akribeia)** | 最終的な精度の精密化。知識の正当化 | Epistēmē = 検証済み事後分布。L1.75 × L1.75 |

### A-series = 精度加重の4段階

```
A1 Pathos   → 初期精度推定（情動的ゲイン：直感的な「これは信頼できる」）
A2 Krisis   → 精度の批判的評価（対立的レビューで精度を検証）
A3 Gnōmē   → 精度に基づく格言抽出（多経験からのパターン一般化）
A4 Epistēmē → 精度の確立（知識として正当化された高精度信念）
```

> **SOURCE**: conv_43 Workflow Runner Enhancements（内部KB）

### EFE と O-series

| O-series | EFE の項 | 行動の性質 |
|:---------|:---------|:-----------|
| O1 Noēsis | — (VFE の belief update) | 内部モデルの更新。知覚推論 |
| O2 Boulēsis | — (好ましい観測 P*(o) の定義) | 目標設定。Pragmatic value の基準 |
| O3 Zētēsis | **Epistemic value** | 情報利得を最大化する行動。探索 |
| O4 Energeia | **Pragmatic value** | 報酬を最大化する行動。実行 |

---

## Layer 3: 実装手順

### FEP パイプライン実行

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.pipeline import run_pipeline
result = run_pipeline('CCL_EXPRESSION', force_cpu=True, use_gnosis=False)
print(result.summary())
"
```

> ⚠️ `CCL_EXPRESSION` を実際の CCL 式に置換。例: `/dia+~*/noe`

### SeriesAttractor による Series 識別

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.attractor import SeriesAttractor
attractor = SeriesAttractor()
result = attractor.suggest('INPUT_TEXT')
for r in result.attractors:
    print(f'Series: {r.series} ({r.name}) sim={r.similarity:.3f}')
print(f'Oscillation: {result.oscillation}')
print(f'Interpretation: {result.interpretation()}')
"
```

> ✅ 検証済み (2026-02-10)。`suggest()` が正しい API。`classify()` は存在しない。

### FEP Agent v2 で行動説明

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
agent = HegemonikónFEPAgentV2()
result = agent.step(observation=0)  # 0-13 の observation index
explanation = agent.explain(result)
print(f'Action: {result[\"action_name\"]}')
print(f'Explanation: {explanation}')
"
```

> ✅ 検証済み (2026-02-10)。`step(observation: int)` + `explain(step_result)` が正しい API。
> 48状態 × 7行動の Active Inference エージェント。`observe()` / `act()` は存在しない。

### Attractor Advisor で WF 推薦

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.fep.attractor_advisor import AttractorAdvisor
advisor = AttractorAdvisor()
rec = advisor.recommend('INPUT_TEXT')
llm_fmt = advisor.format_for_llm('INPUT_TEXT')
print(llm_fmt)
"
```

### パラメータ参照

| パラメータ | 推奨範囲 | 意味 | 根拠 |
|:-----------|:---------|:-----|:-----|
| **γ** (意図精度) | 2.0–8.0 | softmax の温度。高い = 決断的 | conv_59 文献調査 |
| **ζ** (習慣率) | 0.0–1.0 | 習慣 vs 計画の比率 | 同上 |
| **λ** (選好精度) | 4.0–8.0 | C ベクトルへの依存度 | 推奨値（文献明記なし） |

---

## Layer 4: 判断支援 — 問いとチェックリスト

### FEP の5つの問い（根拠付き）

| # | 問い | FEP 概念 | 発動場面 | 根拠 |
|:--|:-----|:---------|:---------|:-----|
| **F1** | この行動は VFE を**増やすか減らすか**？ | 変分自由エネルギー | 全ての意思決定 | VFE 最小化が FEP の L0 公理 |
| **F2** | 精度の根拠は**SOURCE か TAINT か**？ | 精度 (Precision) | BC-6 確信度表出時 | 精度 = チャネル信頼性 (A2-1) |
| **F3** | 今は**探索すべきか実行すべきか**？ | EFE 2項分解 | 行動選択時 | epistemic vs pragmatic (B2-1) |
| **F4** | この不確実性は**解消可能か許容すべきか**？ | 期待自由エネルギー | リスク判断時 | EFE の情報利得 (B2-3) |
| **F5** | **Markov blanket の外**に何があるか？ | 情報境界 | 盲点チェック | 観測不可能な状態 (C3-3) |

### 精度推定チェックリスト

- [ ] 情報源の精度ラベルは適切か？ (SOURCE/TAINT)
- [ ] 過信していないか？ (RLHF が過信を助長する傾向あり)
- [ ] 代替仮説を検討したか？ (低精度チャネルに依拠していないか)
- [ ] 確信度は精度に比例しているか？ (高精度 SOURCE → 高確信、TAINT → 低確信)

### スコープ限定チェック

- [ ] FEP を適用しようとしている場面に、行動選択とフィードバックループが存在するか？
- [ ] Markov blanket を具体的な I/O で定義できるか？
- [ ] 「FEP だから正しい」ではなく「FEP に基づいてこの具体的予測を立てる」と言えるか？

---

## Layer 5: 理論的基盤

### 核心参照文献

| 論文 | 貢献 | HGK への影響 |
|:-----|:-----|:-------------|
| Spisak & Friston 2025 [arXiv:2505.22749](https://arxiv.org/abs/2505.22749) | 自己直交化 attractor network | 6 Series 直交性の数学的正当化 |
| Champion et al. 2024 [arXiv:2402.14460](https://arxiv.org/abs/2402.14460) | EFE の4形式統一 | EFE 2項分解の理論的基盤 |
| Prakki 2024 [arXiv:2412.10425](https://arxiv.org/abs/2412.10425) | Multi-LLM Active Inference | LLM 上位制御層の設計パターン |
| Shusterman 2025 [Nature DigiMed](https://www.nature.com/articles/s41746-025-01516-2) | 医療 LLM の AIF プロンプト | FEP ベースプロンプティングの実証 |
| Aguilera 2021 [arXiv:2105.11203](https://arxiv.org/abs/2105.11203) | FEP の物理的特殊性 | スコープ限定の必要性 |
| Shafiei 2025 [Nature Comms](https://www.nature.com/articles/s41467-025-67348-6) | DR-FREE | 分布ロバスト FEP。環境ミスマッチ耐性 |
| Ramstead 2024 [MIT](https://oecs.mit.edu/pub/my8vpqih) | FEP の概念整理 | 「枠組み」であり「反証性は具体モデルレベル」 |

### 批判と応答

| 批判 | 要約 | HGK の立場 |
|:-----|:-----|:-----------|
| 反証不可能性 (Radomski 2024) | FEP は既存の変分推論と同値で認知への拡張は未正当化 | FEP を「設計原理」として限定使用。反証性は具体モデルレベル |
| MB の特殊性 (Aguilera 2021) | 適用条件が狭い | 具体的 I/O で MB を定義。メタファー乱用を避ける |
| 全体説明のトートロジー (D3) | 何でも説明できる = 何も説明していない | スコープ限定チェックを義務化 |

### 未解決事項

| 項目 | 状態 | 次のステップ |
|:-----|:-----|:-------------|
| ReAct/CoT vs FEP の直接比較 | 文献になし | HGK で独自に設計・検証する余地あり (B3-6) |
| Multi-signal precision estimator | 設計案のみ | 実装は将来 (C1-4) |
| LLM トークン生成の FEP 直接モデル | 概念的対応のみ | 数理的な同一視は時期尚早 (A1-4) |

---

## 参照実装

| プロジェクト | 内容 | URL |
|:-------------|:-----|:----|
| ActiveInferenceForager | LLM × AIF エージェント (Python, alpha) | [GitHub](https://github.com/leonvanbokhorst/ActiveInferenceForager/) |
| AIF_Meeting_EEC | Deep AIF for industrial control | [GitHub](https://github.com/YavarYeganeh/AIF_Meeting_EEC) |
| pymdp | Active Inference の Python 実装 | [GitHub](https://github.com/infer-actively/pymdp) |

---

## 結語

> FEP は呼吸のようなものだ。
> 呼吸していることを意識しなくても生きていける。
> だが意識すれば、より深く、より正確に呼吸できる。
>
> 問題は「FEP を知っているか」ではない。「FEP を使って何が変わるか」だ。
>
> 変わるのは1つだけ —— **判断の前に、一瞬止まるようになる。**
> 「今は探索すべきか？ 実行すべきか？」
> 「この確信の根拠は SOURCE か？ TAINT か？」
> 「Markov blanket の外に、見えていないものがないか？」
>
> その一瞬の停止こそが、精度（precision）の正体である。

---

*v2.1 — /dia+ 敵対的レビュー反映 + Layer 3 実証テスト済み (2026-02-10)*
*Lineage: v1.1 手順のみ → v2.0 /sop + /noe+ → v2.1 /dia+ 修正 + 結語追加*
