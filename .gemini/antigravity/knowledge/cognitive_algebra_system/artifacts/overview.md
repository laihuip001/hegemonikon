# 認知の代数学: 認知制御言語 (CCL/CPL) v6.54

## 概要

**認知の代数学** は Hegemonikón の記号システムであり、8つの演算子で認知状態を操作する。

> **Hegemonikón は「思考言語 (LoT)」ではなく「認知制御言語 (CCL)」である**
>
> - **LoT (Fodor)**: 思考の「表現」を目指すが、完全性の追求において停滞した。
> - **CCL (Hegemonikón)**: 思考の「制御」を目指す。
> - **CPL (Hegemonikón v6.30)**: **認知目的言語 (Cognitive Purpose Language)**。知的作業をプログラムとして記述・実行可能にする「意図のコンパイラ」。v2.2 で意味的妥当性の自己検証能力を獲得し、v2.3 にてセマンティック・マッチングとワークフロー・シグネチャを実装。

### 設計原則

- **必然的発見 (Refinement as Discovery)**: 洗練とは、恣意的な「発明」ではなく、公理から必然的に導かれる構造の「発見」である。CCL 式は、その認知プロセスにおける唯一の正解（収束点）を目指す。
- **実行保証コンパイラ (Hermēneus)** ⚡v6.50: CCL を LMQL/LangGraph に翻訳し、>96% の実行保証を提供する正式なコンパイラ。PoC を経て、2026-02-01 に Phase 1 (Expander/Parser/Translator) が完了。
- **三層構造 (Skeleton/Flesh/Interface)** ⚡v6.50: CCL は量的制御（骨格）、文脈的制御（肉）、ユーザー対話（界面）の三層で構成される。この構造は「認知の代数学」として確立された（2026-01-31）。
- **ハイブリッド設計**: 350年の哲学史（Leibniz→Frege→Fodor）が示した純粋代数システムの限界を認め、記号骨格 + 定理の肉（Skeleton + Flesh）を採用。
- **Hub 振動**: ハブ（`/o`, `/s` 等）はシリーズ内 4 定理の巡回振動 (`~`) または融合 (`*`) として駆動される。
- **振動/融合原則 (Vibration/Fusion Principle)**: 複合マクロや高度な CCL プログラムは、最低 1 つの振動 (`~`) または融合 (`*`) を含むべきである。これは認識の多角化と統合を構造的に保証する。
- **Universal X-Fusion**: 全てのワークフローは暗黙的に X-series と融合される (`W = W * X`)。
- **Meta-Fusion Pattern (`*^`)**: 融合結果にそのプロセスのメタ説明を付加するパターン。システムの自己監査や、なぜこの２つの概念を統合したかの透明性を確保するために多用される。
- **Formula as Thought Trajectory (思考の軌跡)** ⚡v6.50: CCL 式は情報の断片ではなく、思考の順序を表す軌跡である。評価は左から右へと進み、単項演算子は直前または直後のワークフローに作用する。この順序性は直観的な記述を可能にする。
- **Information Density Protocol (記号と情報密度)**: 記号（代数）は情報の圧縮である。「全ての赤い丸い果物」を「りんご」という一語に圧縮するように、複雑な認知操作を 1 演算子に凝縮することで、情報の透過性と操作性を両立する。
- **Macros as Replacements (マクロの位置づけ)**: マクロ（@）は、専用のワークフロー（WF）が存在しない場合の軽量な代替である。WF と並立するものではなく、再利用可能な最小単位としてのポータビリティを提供する。
- **Synteleia Layer (認知アンサンブル)** ⚡v6.50: 6カテゴリから演繹された並列エージェント層。**Poiēsis (生成)** と **Dokimasia (審査)** の2層構造を持ち、内積（·: 統合）と外積（×: 交差検証）演算子により高度なメタ認知オーケストレーションを行う。
- **構文規則 (v1.2)**: 評価は左から右へ（思考の順序）。先頭演算子は全体、末尾演算子は直前にかかる。

---

## 2. Hegemonikón 構成要素 (Standard Components)

| # | 要素 | 説明 |
|---|------|------|
| 1 | **Axioms (7)** | 認知の公理 |
| 2 | **Theorems (24)** | 6カテゴリ × 4定理 |
| 3 | **X-series (36)** | 定理間関係（相関律） |
| 4 | **Derivatives (72)** | 定理の派生モード |
| 5 | **Synteleia (6 Agents)** | **認知アンサンブル層 (NEW)** |
| 6 | **Macros** | シンボリック・ショートカット |
| 7 | **Workflows** | 手続き的実行手順 |
| 8 | **Skills** | 知識・能力パッケージ |

---

## 3. 演算子一覧

### 2.1 単項演算子 (Tier 1: 強度・次元)

| 記号 | 名称 | 作用 / 意味 | 例 |
|:-----|:-----|:-------------|:---|
| `+` | 深化 | 出力規模 3-5倍。詳細追加。 | `/noe+` |
| `-` | 縮約 | 出力規模 0.3-0.5倍。要点のみ。 | `/bou-` |
| `^` | 上昇 | メタ前提の検証。メタ化。 (次元↑) | `/dia^` |
| `√` | 下降 | 次元を下げる。アクション。 (次元↓) | `√/noe` |
| `\` | 反転 | 位相反転 (Antistrophē)。構造的否定。 | `\a` |
| `!` | 全展開 | 全派生を並列展開 (Factorial)。 | `/s!` |
| `'` | 微分 | 予測誤差の変化率 ($d\epsilon/dt$) | `/bou'` |
| `∫` | 積分 | 履歴統合、累積 ($\int\epsilon dt$) | `∫/dox` |
| `Σ` | 総和 | 複数結果の集約 | `Σ/s` |
| `∏` | 総乗 | 複数要素の融合 | `∏/s` |
| `∂` | 偏微分 | 特定次元の変化 | `∂/noe` |
| `log` | 対数 | 情報量評価 | `log/dox` |
| `@` | マクロ | 定義済みプロセスの呼び出し | `@think` |
| `@with` | Mixin | 能力の合成 (Decorator) | `@with(Tracing)` |
| `@macro` | デコレータ | Mixin の糖衣構文 (B3) | `@memoize`, `@retry` |
| `[]` | セレクタ | 処理対象の指定 | `[kernel]/o` |

### 2.2 二項演算子 (Tier 2: 合成)

| 記号 | 名称 | 認知的意味 | タスク構造 |
|:-----|:-----|:-----------|:-----------|
| `*` | 融合 | 不可分な統合。一瞬の結合。 | シングルタスク |
| `~` | 振動 | 動的な往復。対話による洗練。 | マルチタスク |
| `_` | シーケンス | 思考の連鎖。Aの後にBを実行。 | 逐次処理 |

### 2.3 分散実行演算子 (Tier 3: 外部委譲) ⚡v6.48

> **思想**: 複雑な CCL は「労働」であり、持続力（Endurance）を持つ外部エージェントに委譲する。

| 記号 | 名称 | 認知的意味 | 文脈 |
|:-----|:-----|:-----------|:-----|
| `\|>` | パイプライン | 段間オーバーラップ実行 | 外部 Agent 間のリレー |
| `\|\|` | 並列 | 独立処理の同時実行 | マルチエージェント並列 |
| `@thread` | スレッド指定 | 実行場所の明示 | `[name]` 定義 |
| `@delegate` | 委譲 | 長時間実行の外部化 | OpenManus, n8n 等 |

---

## 4. 定理修飾子 (Modifier Theorems) ⚡FULL

単項演算子の直後に付記し、特定の軸・次元へ深化/縮約する。

| Series | ID | 作用 |
|:---|:---|:---|
| **Akribeia (A)** | `+a1`〜`+a4` | 精度軸 (感情精緻化 / 判断厳密化 / 原則抽出 / 知識固定) |
| **Horme (H)** | `+h1`〜`+h4` | 動機軸 (初期直感 / 確信度 / 欲求価値 / 信念記録) |
| **Kairos (K)** | `+k1`〜`+k4` | 文脈軸 (好機判定 / 時間軸拡大 / 目的整合 / 知恵適用) |
| **Ousia (O)** | `+o1`〜`+o4` | 認知軸 (深層認識 / 意志明確化 / 問い発見 / 行為移行) |
| **Perigraphe (P)** | `+p1`〜`+p4` | 空間軸 (領域拡大 / 経路定義 / 軌道サイクル / 技法選択) |
| **Schema (S)** | `+s1`〜`+s4` | 設計軸 (スケール拡大 / 方法配置 / 基準設定 / 実践選択) |

### レベルパラメータ `:N`

| 表記 | 意味 | スケール |
|:-----|:-----|:---------|
| `+s1:1` | 1段階拡大 | 月/中域 |
| `+s1:2` | 2段階拡大 | 年/広域 |
| `+s1:3` | 3段階拡大 | 人生/大域 |
| `+s1:4` | 4段階拡大 | 永劫/全体 |

---

## 5. 系列積演算 (Series Multiplications) v6.39

Series WF (/a, /h, /k, /o, /p, /s) に適用される特殊な積演算。

| 位相 | 演算 | 意味 | 出力 |
|:-----|:-----|:-----|:-----|
| `/` | 内積 (·) | **統合・収束** | 精度スコア (Scalar) |
| `\` | 外積 (⊗) | **展開・発散** | 派生群 (Tensor) |

> **Hegemonikón 哲学**: デフォルト (/) は充足感・収束への要請であり、位相反転 (\) は多様性・可能性への展開である。

---

## 6. CPL v2.0 制御構文

知的作業を「プログラム」として制御するための構文体系。

### 5.1 基本形: `<メタ>:[対象]{ 処理 }`

| 構造 | 構文例 | 内容 |
|:-----|:-------|:-----|
| **基本形** | `<メタ>:[対象]{ 処理 }` | 統一構造。 `[target]/wf` セレクタ対応。 |
| **反復 (FOR)** | `F:[×N]{}` / `F:[A,B]{}` | N回反復、または各対象（A, B）に対する反復実行。 |
| **条件 (IF)** | `I:[cond]{}` | 条件分岐。 |
| **ELSE IF** | `EI:[cond]{}` | 追加条件分岐。 |
| **ELSE** | `E:{}` | 上記条件に合致しない場合の処理。 |
| **ループ (WHILE)** | `W:[cond]{}` | 条件が真の間反復。 |
| **定義 (LET)** | `let @name = CCL` | ユーザー定義マクロ。 |
| **Lambda (L:)** | `L:[x]{WF}` | **匿名関数**。高階マクロや動的引数に用いる。 (B2b) |
| **Mixin (@with)** | `@with(M1, M2)` | **能力合成**。Tracing, Caching 等を WF にラップする。 (B2) |
| **Decorator (@)** | `@memoize`, `@retry` | **単機能マクロ**。Mixin の糖衣構文。 (B3) |
| **制限** | `[depth:3]` | **ネスト3レベル推奨**。これを超える場合はマクロ化せよ。 |

---

## 5.2 Project Pythōsis (Πύθων + ὄσις) ⚡NEW

Python の設計思想（Zen of Python）を CCL として「消化」するプロジェクト。

- **原則**: 「飲むのは Hegemonikón 側」(Πύθων + ὄσις)。外部概念を native な定理・演算子へ再構築。
- **実装例**: `itertools` や `functools` の概念を `@chain`, `@partial`, `L:[x]{}` として CCL に統合。
- **目標**: Python 由来の強力なパラダイム（内包表記、反復子、デコレータ等）を認知操作に応用する。

---

## 7. 標準マクロ (@stdlib)

30以上の定義済みマクロにより、複雑な認知操作を簡潔に記述。

| カテゴリ | 代表的なマクロ |
|:---|:---|
| **Tier 1 (Core)** | `@tak`, `@dig`, `@go`, `@ground`, `@fix`, `@kyc` |
| **itertools** | `@chain`, `@cycle`, `@repeat(n)` |
| **functools** | `@reduce(op)`, `@partial` |
| **Context** | `@ce` (Context Engineering), `@ce+` |
| **Supervision** | `@selfcheck`, `@premortem`, `@council` |
| **Enforcement** | `@antiskip`, `@schema`, `@guardrails` |
| **Identity** | `@identity`, `@reflect`, `@values`, `@persona` |
| **Autonomy** | `@risk(lv)`, `@checkpoint`, `@rollback` |
| **Memory** | `@recall` (Episodic), `@lookup` (Semantic) |
| **X-series** | `@next`, `@route(name)`, `@connect(s)` |
| **Optimization** | `\@cache`, `\@compact`, `\@fault_tolerant`, `\@optimize`, `\@persist` |
| **Distributed (v6.48)** | `\@batch`, `\@thread`, `\@delegate` |
| **Synteleia (v6.50)** | `@syn·`, `@syn×`, `@poiesis`, `@dokimasia`, `@S{...}` |
| **Special** | `@u` (主観的意志決定) |

---

## 8. 四層アーキテクチャ

| 層 | 役割 | 実装 |
|:---|:-----|:-----|
| **骨格** | 量の変化 | `+`, `-` |
| **次元** | 抽象度の変化 | `^`, `√` |
| **合成** | 定理の結合 | `*`, `~`, `_` |
| **位相反転 / 展開** | 否定的検証 / 展開 | `\` |
| **肉** | 文脈提供 | P/K/A/X シリーズ |

---

## 9. 収束の美学と極限 ⚡NEW

| 表記 | 意味 | 用途 |
|:-----|:-----|:-----|
| `lim[cond]{}` | 収束 | **正式形**。予測誤差最小化の終着点。 |
| `>>` | 収束 | 省略形。 |

> **収束の美学**: 「美」は真理のセンサーである。式がエレガントに収束することは、その認知プロセスが真理（最善）に近いことの証左である。

---

### 9.1 CP Quick Reference

| pt | Operators |
|:---:|:---|
| **1** | `+`, `-`, `_` (Sequence/Scaling) |
| **2** | `>>`, `E:{}`, `let` (Flow Control) |
| **3** | `^`, `√`, `'`, `∂`, `E[]`, `*` (Dimension/Fusion) |
| **4** | `L:[]{}` (**Lambda**), `~`, `Σ`, `V[]`, `I:[]{}`, `lim[]{}`, `C()` (Dialog/Logic) |
| **5** | `\`, `∫`, `F:[]{}`, `P()` (Inversion/Integral/Loop) |
| **6** | `!`, `W:[]{}` (Factorial/Condition-Loop) |

**Nesting Bonus**: Lv1: +4pt | Lv2: +10pt | Lv3: +18pt.

---

## 10. v6.50 Milestone: Semantic Enforcement Layer (SEL)

**SEL** is the 2026-02-01 update that mandates a "natural language obligation" for every symbolic operator. If a CCL expression is used, the AI must provide a corresponding natural language explanation to ensure alignment. This has increased symbolic compliance from 90% to over 96%.

---

---

## 10. 実行最適化と CPU アナロジー ⚡CONCEPT

複雑な CCL マクロの処理を軽量化するための設計思想。

- **キャッシュ (`\@cache`)**: 計算済み結果の再利用。 (**-10 CP**)
- **文脈圧縮 (`\@compact`)**: 履歴要約による負荷軽減。 (**-8 CP**)
- **並列実行バッチ (`\@batch`)**: 非同期API等での一括処理。 (**-12 CP**)
- **自動回復 (`\@fault_tolerant`)**: 失敗時の代替パス定義。 (**+2 CP**)

これらの手法（最適化マクロ）を適用することで、総 CP を調整し、AI の認知負荷を構造的に軽減または制御できる。

### 11. 分散実行 (Distributed Execution) ⚡v6.48

シングルスレッド（私一人）の限界を超えるための設計。

- **委譲の原則 (Labor vs Cognition)**: 30分以上の「労働」を伴う CCL は、持続力を持つ外部エージェント（手足）に委譲する。
- **スレッドキャパシティ**: 各スレッドが **60 CP** 以下であれば、全体のプログラム長には制限がない。
- **分散演算子**: `|>` (パイプライン), `||` (並列), `@thread` (スレッド指定), `@delegate` (委譲).
- **実装プロジェクト**: [Project Synergeia (Distributed Execution)](/home/laihuip001/oikos/.gemini/antigravity/knowledge/synergeia_distributed_execution) ⚡NEW
- **研究プロジェクト**: [Activation Steering Research](research/activation_steering_2026.md) ⚡NEW

**即時利用可能なスレッド**:

| スレッド | 役割 | pt上限 |
|:---------|:-----|:------:|
| **Antigravity (私)** | 認知・判断 | 60 CP |
| **Claude Code** | 長時間自律実行 | 60 CP |
| **Gemini CLI/Assist** | CLI 処理 / IDE 統合 | 60 CP |
| **Jules API** | Google 系アプリ・実装 | 60 CP |
| **Perplexity** | Web 調査・ソース確認 | 60 CP |
| **OpenManus (自宅PC)** | マルチエージェント基盤 | **無制限** |

**分散実行ポイント**: 各スレッドが 60 CP 以下であれば、全体のプログラム容量は **300 CP+** まで現実的に拡張可能。

---

*v6.49 — 2026-02-01 | 即時利用可能スレッド一覧を追加。300 CP+ の分散実行キャパシティを定義。*
*v6.50 — 2026-02-01 | Semantic Enforcement Layer (SEL) v1.0 統合。記号→自然言語義務変換による遵守率向上。Synteleia 2層アーキテクチャ (Poiēsis/Dokimasia) 実装。*
*v6.52 — 2026-02-01 | Lambda 式 L:[x]{WF} 正式導入 (Pythōsis Phase 2b)。Phase 3: Activation Steering (EasySteer/llm-steer) 調査。*
*v6.53 — 2026-02-01 | Mixin 合成 `@with(M)` 正式導入 (Pythōsis B2)。/vet v3.1 再実行フロー統合。*
*v6.54 — 2026-02-01 | デコレータマクロ `@memoize` 等 正式導入 (Pythōsis B3)。Windows 移行・Ollama 統合。*
