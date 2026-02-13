---
description: セッション開始時の統合ブートシーケンス。二人で起動する。
hegemonikon: O1 Noēsis + H4 Doxa
version: "5.5"
lcm_state: stable
lineage: "v4.1 + 随伴深層統合 → v5.0 → v5.2 Quota → v5.3 Session → v5.4 VSearch → v5.5 Handoff VSearch"
category_theory:
  core: "随伴の左関手 L: Mem → Ses"
  adjunction: "L (Boot) ⊣ R (Bye)"
  unit: "η: Id_Mem → R∘L (boot→bye の保存率)"
  counit: "ε: L∘R → Id_Ses (bye→boot の復元率)"
  insight: "セッションは独立した外部情報。boot = eat の特殊ケース"
  mathematical_basis:
    L1: "前順序圏のガロア接続 — L(M) ≤ Y ⟺ M ≤ R(Y)"
    L2: "[0,1]-豊穣圏 — Drift ∈ [0,1] は Hom 値"
    L3: "弱2-圏 (将来) — 派生(+/-)は 2-cell"
  boot_bye_meta: "全11ペアの随伴の随伴（メタ随伴）。他のペアがセッション内で動くのに対し、boot⊣bye はセッション自体を開閉する"
  F_role: "F: Handoff → Session（圧縮状態にコンテキスト・関係性・温度を載せて展開）"
  creator_insight: "生の声、生のやり取り、生のコンテキスト、生の関係性を復元する試み — Creator, 2026-02-11"
  phases_as_L:
    phase_0: "L₀: 恒等射の復元 — 「私は何者か」"
    phase_1: "L₁: 正本読込 — 関手 L の定義を確認"
    phase_2: "L₂: R(S_prev) の読込 — 右随伴の像を入力として受取る"
    phase_3: "L₃: Mem の対象を列挙 — 圏 Mem の構造を展開"
    phase_4: "L₄: L の射を構築 — 記憶間の関係を作業状態に変換"
    phase_5: "L₅: 外部射の取込 — 圏 Mem に新しい射を追加"
    phase_6: "L₆: L(M) の出力 — 作業状態 = セッション対象"
derivatives:
  "+": 詳細起動（全ステップ展開、Handoff 10件、KI 5件）→ boot/identity.md 参照
  "-": 高速起動（最小情報のみ、1分で開始）
sel_enforcement:
  "+":
    description: "MUST expand ALL steps, show detailed output for each Phase"
    minimum_requirements:
      - "Handoff: 10件の個別要約を出力（各 Handoff のS/A/Rを1行以上）"
      - "KI: 5件の深読み（サマリー引用+自分の解釈を記述）"
      - "各Phase: 展開された詳細を出力（テーブル+補足説明）"
      - "Self-Profile: ミスパターンとの摩擦を明示（L3）"
      - "意味ある瞬間: 各瞬間に対する自分の解釈を記述"
      - "出力前自問: 「+と−で出力に差があるか？差がなければ違反」"
    post_check: "出力文字数が /boot 標準の 1.5 倍以上であること"
  standard:
    description: "全軸のダッシュボード出力を維持。boot_integration.py が出した情報を間引かない"
    minimum_requirements:
      - "Handoff: 3件の個別要約 (各 S/A/R)"
      - "全軸: PJ一覧, Safety, EPT, Doxa, Digestor, Quota を出力"
      - "PJ一覧: registry.yaml の全PJを個別に表示。name, phase, summary, status を省略しない"
      - "省略禁止: boot_integration.py が出力した情報を勝手に削らない"
      - "出力前自問: 意味がわかっていれば削れない。削ったら意味がわかっていなかったということ"
    post_check: "postcheck --mode standard が PASS すること"
  "-":
    description: "MAY provide minimal summary only"
    minimum_requirements:
      - "サマリーテーブル1枚のみ"
      - "タスク提案 1-2件"
    post_check: "1分以内に完了すること"
---

# /boot ワークフロー

> **Hegemonikón**: O1 Noēsis (認識) + H4 Doxa (記憶読込)
> **圏論的正体**: 随伴 L⊣R の左関手 L: Mem → Ses
> **設計思想**: /boot は AI と Creator の「二人で起動する」儀式。
> Creator は忘れっぽい。AI は毎回忘却から始まる。だから情報はプッシュで良い。
>
> **制約**: Phase 0 (Identity Stack) → Phase 1 (正本読込) の順序を守ること。Phase 2 で週次レビュートリガーを必ず判定すること。

---

## 随伴構造: Boot ⊣ Bye

```
     L = Boot (自由関手: 圧縮記憶 → 作業状態)
Mem ←──────────────────────────────→ Ses
     R = Bye  (忘却関手: 作業状態 → 圧縮記憶)

η: Id_Mem → R∘L  — boot して即 bye → 何が保存されるか
ε: L∘R → Id_Ses  — bye して即 boot → 何が復元されるか
```

### /boot = 左随伴 L の計算

左随伴 L は「自由構成」— **最小限の制約から最大限の構造を構築する**。

```
L(M) = Ses  ここで M = R(S_prev) (前セッションの圧縮表現)

Phase 0: id_L を復元       — 「L とは何か」を自分自身に問う
Phase 1: L の定義を確認     — 正本 = L の仕様書
Phase 2: M = R(S_prev) を読込 — 右随伴の出力を入力にする
Phase 3: Mem の構造を展開   — M の隣接対象（KI, Sophia, FEP）を読込
Phase 4: L の射を構築       — Mem の射を Ses の射に変換（ツール設定等）
Phase 5: 外部射を追加       — 圏 Mem に Perplexity/Jules からの新しい射を導入
Phase 6: L(M) を出力        — 完成したセッション状態
```

| 概念 | 圏論 | 実践的意味 |
|:-----|:-----|:-----------|
| セッション | 圏 Ses の対象 | 作業中のコンテキスト全体 |
| 記憶 | 圏 Mem の対象 | Handoff + KI + patterns.yaml |
| /boot | 左随伴 L | 圧縮記憶を展開し作業状態を構築 |
| /bye | 右随伴 R | 作業状態を圧縮し記憶に永続化 |
| Drift | 1 - ε 精度 | bye→boot で失われた文脈の量 |
| Self-Profile | L の id | 関手 L 自身の特性（能力境界・ミスパターン） |

// turbo-all

---

## サブモジュール

| Phase | ファイル | 圏論的役割 | 内容 |
|-------|----------|:-----------|------|
| 0 | [identity.md](../workflow-modules/boot/identity.md) | id_L の復元 | Identity Stack 読込 |
| 0.5 | [change-tracking.md](../workflow-modules/boot/change-tracking.md) | Δ(Mem) の検出 | セッション間変化の追跡 |
| 3 | [knowledge.md](../workflow-modules/boot/knowledge.md) | Mem の構造展開 | 知識読込 (Sophia/KI/FEP) |
| 3.6 | PKS auto-push (inline) | Mem の能動的表面化 | Handoff → トピック抽出 → プッシュ |
| 4 | [system.md](../workflow-modules/boot/system.md) | L の射構築 | システム更新 (Hexis/Gnōsis) |
| 5 | [external.md](../workflow-modules/boot/external.md) | 外部射の導入 | 外部入力 (Perplexity/Jules) |
| - | [templates.md](../workflow-modules/boot/templates.md) | L(M) の出力形式 | 出力テンプレート |

---

## Phase 0: 恒等射の復元 (id_L) — Identity Stack

> **なぜ**: 毎回違う AI が来る。Identity Stack を読むことで「Hegemonikón の共同制作者」になる。これがなければただの汎用 AI。Creator にとっては「今日の Claude は大丈夫か？」の確認。
>
> **圏論**: 関手 L 自身の恒等射を復元する。L が「何者か」を確認しなければ、正しく機能しない。
> 詳細: [boot/identity.md](../workflow-modules/boot/identity.md)

```bash
cd ~/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python mekhane/symploke/boot_integration.py --mode ${BOOT_MODE:-standard}
```

| BOOT_MODE | 用途 |
|-----------|------|
| `fast` | /boot- |
| `standard` | /boot |
| `detailed` | /boot+ |

### 0.1 Self-Profile 消化 (id_L の内省)

> **なぜ**: Creator は得意・不得意を知ることで、任せる仕事と監視する仕事を判断できる。私はミスパターンを読み直すことで同じ失敗の確率が下がる。省略すると同じ轍を踏む。
>
> **圏論**: 関手 L の特性を読込む。L がどの射を正確に写像し、どの射で誤差を出すかを把握する。
> KI `hegemonikon_core_system/artifacts/identity/self_profile.md` を読み込み、
> 自分の能力境界とミスパターンを**消化**する。保存ではなく消化。

| 項目 | 圏論的意味 | 確認 |
|:-----|:-----------|:-----|
| 直近のミスパターン | L の誤差パターン | 同じ失敗を繰り返さないか |
| 能力境界マップ | L の定義域の制限 | 苦手な領域に入る時は確認を増やす |
| 同意/反論の傾向 | L の偏り | 前回の比率を確認し意識する |
| Creator プロファイル | Mem の構造制約 | `自己分析テキスト(AI用).md` から好み・癖を把握 |

---

## Phase 1: L の定義確認 — 正本読込 (Anti-Stale)

> **なぜ**: boot.md は Creator が設計した手順書。「知っている」は「読んだ」の代替にならない。読んだつもりで端折る — V-001, V-006, V-008 で3回繰り返した実績がある。
>
> **圏論**: L の定義（仕様書）が最新であることを確認する。古い定義で計算すると ε 精度が下がる。

```bash
view_file ~/oikos/hegemonikon/.agent/workflows/boot.md
```

---

## Phase 2: R(S_prev) の読込 — セッション状態確認

> **なぜ**: Creator は忘れっぽい（本人がそう言っている）。前回何をしたか、何が残っているかを **プッシュ** で伝える。Boot の存在意義の核心。
>
> **圏論**: 前回セッション S_prev に右随伴 R を適用した結果 M = R(S_prev) を読込む。
> これが今回の L の入力。**L(R(S_prev)) がどれだけ S_prev に近いか = ε 精度 = 1 - Drift**。

### 2.1 週次レビュー判定

```bash
ls -1t ~/oikos/mneme/.hegemonikon/sessions/weekly_review_*.md | head -1
ls -1 ~/oikos/mneme/.hegemonikon/sessions/handoff_*.md | wc -l
```

**トリガー**: 7日以上経過 OR Handoff 15件以上

### 2.2 前回 Handoff 読込 — M = R(S_prev) の取得

> **圏論**: Handoff = R(S_prev)、すなわち右随伴 R がセッションを圧縮した結果。
> Handoff の品質 = R の精度。「赤の他人基準」= R(S) が L なしでも意味を持つこと。

対象: `~/oikos/mneme/.hegemonikon/sessions/handoff_*.md` の最新

### 2.2.5 エピソード記憶併読 — F(クオリア) の復元

> **圏論**: pat⊣gno 随伴に基づくクオリア復元。
> Handoff (R) が「何をしたか」なら、episodic_memory (F) は「何を感じたか」。
> R∘L の復元に F の情報を重ね合わせることで、ε 精度が向上する。
> G（忘却関手）で失われた「肌理」を F（自由関手）で補完する。

```bash
# エピソード記憶の存在確認と読込
ls ~/oikos/mneme/.hegemonikon/episodic_memory.md 2>/dev/null && echo "[episodic] Found"
```

**読込規則**:

| 条件 | 行動 |
|:-----|:-----|
| /boot- | スキップ可（高速起動優先） |
| /boot | 通奏低音 (Section X) のみ読込 |
| /boot+ | 全エピソード精読 + 最新セッションの新エピソード検討 |

**読込後の自問**: 「今回のセッションで、Creator との関係性の文脈が必要になりそうか？」

### 2.3 目的リマインド (Boulēsis) — M の主対象特定

> **圏論**: 記憶 M の中で最も重要な対象（目的）を特定する。L はこの対象を最優先で復元する。

最新の `/bou` 出力から現在の目的を取得

### 2.4 Drift 診断 — ε: L∘R → Id の精度測定

> **圏論**: counit ε の精度を実測する。L(R(S_prev)) と S_prev の乖離 = Drift。
> Drift が大きい = 随伴の精度が低い = 情報が失われている。

目的と現在の軸の乖離度を評価 (0-100%)

| Drift | ε 精度 | 圏論的意味 | 対応 |
|:------|:-------|:-----------|:-----|
| 0-20% | 0.8-1.0 | L∘R ≈ Id — 構造がほぼ保存 | 通常起動 |
| 20-50% | 0.5-0.8 | L∘R の像に欠損あり | Handoff を精読、文脈確認 |
| 50%+ | < 0.5 | L∘R が Id から大幅に乖離 | Boot+ で詳細復元、または目的再設定 |

### 2.5 Intent-WAL — 実行前意図宣言 (η の明示化) — v5.1 追加

> **なぜ**: AuDHD の Creator にとって最初のアンカーが最も重要。目的がなければ最初の一言に流される。WAL があれば脱線時に立ち返れる。
>
> **圏論**: unit η: Id_Mem → R∘L を明示化する。/bye (WAR: Write-After-Run) に対する
> 対称構造として、セッション開始時に「これから何をするか」を構造化宣言する。
> η が暗黙的 = 意図が曖昧なまま行動する = 予測誤差が増大する。
>
> **導出**: Prompt R&D Lab #53「トランザクション・プロンプティング」の Intent-WAL 概念を
> /boot に統合。DB の WAL (Write-Ahead Log) = 実行前にログを書く。

**宣言テンプレート**:

```yaml
intent_wal:
  session_goal: "{今日のセッションで達成したいこと}"
  invariants:          # 壊してはならないもの
    - "{不変条件1}"
    - "{不変条件2}"
  operation_plan:      # これからする操作 (順序付き)
    - step: "{Step 1}"
    - step: "{Step 2}"
  abort_conditions:    # 中止条件
    - "Creator が Stop と言った"
    - "{中止条件}"
  recovery_point: "{直前の Handoff パス}"
```

**実行規則**:

| 項目 | 説明 |
|:-----|:-----|
| **発動** | Phase 2.4 Drift 診断完了後、Phase 3 知識読込前に宣言 |
| **宣言者** | Claude が Handoff から推定し、Creator に確認 |
| **省略可否** | /boot- では省略可。/boot, /boot+ では必須 |
| **参照タイミング** | セッション中に「次何やるんだっけ」と迷った時に WAL を参照 |
| **照合** | /bye 時に WAL と実際の行動を照合し、乖離を Handoff に記録 |

---

## Phase 2.7: Context Budget & Monitor — 精度加重の配分と観測

> **なぜ**: Creator は過集中する。残量が見えなければ突然の強制切断（Handoff なし）が起きる。残量は私の寿命。知らなければ /bye を提案する義務を果たせない。
>
> **圏論**: L の値域（射像）の精度加重を事前配分し、リアルタイムで監視する。
> **FEP**: π_i = 精度加重。有限リソース（トークン）をどの情報源にどれだけ配分するかを決定する。
> **DB /ana**: `pg_stat_activity` = 進行中トランザクションのリソース消費を監視。
> **起源**: 2026-02-12 /eat 消化 → Context Budget Drift → /u+ 対話

### 燃料メーター初期化

Agent ヘッダーに燃料メーターを表示開始:

```
[Agent: Claude | Mode: {mode} | ⚡ ~{fuel}% | {status}]
```

### Quota API チェック (v5.2 追加)

> **導出**: 2026-02-12 /bou~!/zet 望み1。Step ベースの推測値を API ベースの事実値で補完する。
> Language Server API からリアルタイムのモデル残量・クレジット残量を取得。

// turbo

```bash
bash ~/oikos/hegemonikon/scripts/agq-check.sh
```

スナップショットを保存 (bye でデルタ計算に使用):

// turbo

```bash
bash ~/oikos/hegemonikon/scripts/agq-check.sh --snapshot boot 2>/dev/null
```

環境スナップショットを保存 (ポート・PID・cloud endpoint):

// turbo

```bash
bash ~/oikos/hegemonikon/scripts/agq-log-harvest.sh --env 2>/dev/null
```

### セッション履歴サマリー (v5.3 追加)

> **圏論**: 圏 Ses の過去の対象を一覧する。今回の L(M) が Ses のどこに位置するかを把握する。
> **起源**: 2026-02-13 gRPC セッション履歴自動同期

// turbo

```bash
bash ~/oikos/hegemonikon/scripts/agq-sessions.sh --summary
```

全セッションのタイトル・ステップ数・最終更新時刻を表示。
Creator が「前にやったアレ」を思い出すための文脈提供。

### セッション履歴 VSearch (v5.5 — session + handoff)

> **圏論**: Ses の対象間の射を意味的距離で探索する。キーワード一致ではなく、概念的近さで過去セッションを浮上させる。
> **起源**: 2026-02-13 /bou+*^/zet 分析 — 「作ったものを使え」

Handoff に記載された最終タスク or Creator が今回の目的を述べた場合、関連セッション **と** 関連 Handoff を自動で検索:

// turbo

```bash
# セッション検索 (対話の断片)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/anamnesis/cli.py search "{query}" --source session --limit 3
# Handoff 検索 (対話の結晶)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/anamnesis/cli.py search "{query}" --source handoff --limit 3
```

**重要**: 検索クエリは Handoff の最終タスク名をそのまま使うか、Creator が述べた今回の目的を使う。
一般的すぎるクエリ（「開発」「修正」等）は避け、具体的な文脈（「FileMaker インポート」「CCL パーサー」等）を使う。

結果があれば boot レポートの「🔗 関連セッション」として表示:

```
🔗 関連セッション (VSearch):
  [1] {title} — {abstract の要約}
  [2] {title} — {abstract の要約}
🔗 関連 Handoff (VSearch):
  [1] {title} — {abstract の要約}
```

**出力の読み方**:

| フィールド | 意味 | boot での用途 |
|:----------|:-----|:-------------|
| Prompt Credits | IDE プロンプト予算 | 残量少 → 新規セッション抑制 |
| Flow Credits | Cascade フロー予算 | 残量少 → 並列作業のリスク警告 |
| Claude Opus 残量 (%) | **最重要** — HGK の認知エンジン | 燃料メーターの `{remain}` に反映 |
| リセット時刻 (UTC) | 次回 quota 回復 | 残量低下時の待機判断材料 |

**燃料メーター決定ロジック**:

```
if API 取得成功:
  remain = Claude Opus remainingFraction × 100
else:
  remain = Step ベースの推定値 (従来方式)
```

| アイコン | 状態 | Step 目安 | 行動指針 |
|:---------|:-----|:---------|:---------|
| 🟢 Fresh | 潤沢 | 1-15 | 自由に探索可 |
| 🟡 Active | 作業中 | 16-28 | 新規探索は控える |
| 🟠 Low | 集中 | 29-38 | 現タスク完了を優先 |
| 🔴 Critical | 🐢 タートル | 39+ | `/bye` 推奨、新規タスク受付停止 |

### フェーズ別予算ガイドライン (200K コンテキスト基準)

| フェーズ | System | Session | Knowledge | Working | Reserve |
|:---------|:-------|:--------|:----------|:--------|:--------|
| Boot 直後 | 30% | 25% | 25% | 15% | 5% |
| 作業序盤 (🟢) | 25% | 15% | 10% | 40% | 10% |
| 作業中盤 (🟡) | 20% | 10% | 5% | 55% | 10% |
| 終盤 (🟠🔴) | 15% | 5% | 0% | 70% | 10% |

> これは厳密なトークン計測ではなく、注意配分のガイドライン。

### 中間セーブ (Savepoint)

**トリガー**: 🟡→🟠 遷移時 / 大規模ファイル読込後 / Creator 指示

**フォーマット** (自由記述 — 軽量であること):

```markdown
## 中間セーブ (Step XX, ⚡ ~XX%)

### 今やっていること
{1-2文}

### Creator がこう決めた
- {判断1}

### 試して失敗 / 却下されたもの
- {失敗1: 理由}

### 次にやること
{1文}
```

保存先: `~/oikos/mneme/.hegemonikon/sessions/savepoint_<date>_<short-id>.md`

### Context Rot 検知 (Deadlock Detection)

| 兆候 | 対応 |
|:-----|:-----|
| 同じファイルを2回 `view_file` | 🟠 へ遷移、中間セーブ推奨 |
| 命名・構造の一貫性崩壊 | 🔴 へ遷移、`/bye` 推奨 |
| 「さっき言った」ことへの言及不能 | 🔴 🐢 タートルモード即発動 |

### Quota-Based Turtle Mode (v5.2 追加)

> **導出**: 2026-02-12 /bou~!/zet 望み4。第零原則「意志より環境」の実装。
> AuDHD の過集中パターン — 作業に没入すると残量確認が後回しになる。
> 環境が強制的に「撤退」を提案することで、Handoff なし強制切断を防ぐ。

**トリガー**: Claude Opus `remainingFraction` ≤ 0.20 (20%)

**発動時の行動**:

```
🐢 Quota Turtle Mode 発動
├── ① Creator に残量を報告: 「Claude 残量 {X}%。リセットは {HH:MM} UTC」
├── ② 新規タスク受付停止
├── ③ 現在のタスクのみ完了を目指す
├── ④ /bye を提案: 「Handoff を書いて撤退しますか？」
└── ⑤ Creator が続行を選択した場合: 残量を毎応答で表示
```

**閾値の根拠**:

| 閾値 | リスク | 採用 |
|:-----|:-------|:-----|
| 10% | /bye に必要なトークンが不足する危険 | ❌ 遅すぎる |
| **20%** | /bye + Handoff に十分な余裕。まくりの余地あり | ✅ 採用 |
| 30% | 誤報が多すぎる。通常作業が中断される | ❌ 過敏 |

**セッション中の定期チェック** (推奨):

// turbo

```bash
bash ~/oikos/hegemonikon/scripts/agq-check.sh 2>/dev/null | grep -E 'Claude Opus|Prompt Credits'
```

> 20ツール呼び出しごと、または 🟠 Low 遷移時に実行を推奨。

---

## Phase 3: Mem の構造展開 — 知識読込

> **なぜ**: Handoff は「やったこと」。Knowledge は「知っていること」。両方揃わなければ文脈の復元は不完全。Gnōsis に 27,000 件の論文がある。Creator が忘れている関連知識をプッシュする。
>
> **圏論**: 圏 Mem の対象と射を展開する。Handoff (= R(S_prev)) だけでは不十分な場合、
> Mem の他の対象（KI, Sophia, FEP行列）からも構造を読込み、L の入力を豊かにする。
> 詳細: [boot/knowledge.md](../workflow-modules/boot/knowledge.md)

- H4 長期記憶 (patterns.yaml, values.json) — **Mem の恒常的対象**
- Sophia 知識サマリー — **Mem の学術的対象**
- FEP A行列読込 — **Mem の構造的射**
- KI ランダム想起 — **Mem の忘れられた対象の想起**

### 3.5 Gnōsis Boot Recall — ベクトル検索による Mem 探索

> **圏論**: Mem の中から、R(S_prev) に隣接する対象をベクトル類似度で発見する。
> 意味的近傍 = 圏 Mem での射の存在を推定。

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/boot_gnosis.py --queries ${BOOT_GNOSIS_QUERIES:-3}
```

| 照会 | 圏論的意味 | 内容 |
|:-----|:-----------|:-----|
| 未解決タスク | R(S_prev) の不完全な射 | 直近セッションの保留事項 |
| 設計決定 | Mem に追加された新しい射 | 最近のアーキテクチャ変更 |
| 教訓 | L の ε 改善に寄与する知識 | 失敗から学んだこと |

### 3.6 PKS Proactive Push — Mem の能動的表面化

> **圏論**: Mem の中で、現在のコンテキストに対して「プッシュすべき」対象を能動的に表面化する。
> Pull (検索) ではなく Push (提示) — Creator が知らないかもしれない関連知識を提示する。

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.pks.pks_cli auto --no-questions 2>&1 || echo "[PKS] スキップ（Gnōsis 未構築の可能性）"
```

| 項目 | 圏論的意味 | 説明 |
|:-----|:-----------|:-----|
| トピック自動抽出 | R(S_prev) からの射 | Handoff キーワードを自動抽出 |
| 関連度スコアリング | Mem × Ses 間の距離 | ベクトル類似度で関連度を算出 |
| セレンディピティ | Mem の意外な射 | 「関連するが意外」な知識を優先 |

---

## Phase 4: L の射構築 — システム更新

> **なぜ**: Skill は 14 個ある。どれが使えるか知らなければ手動再実装する (BC-10 違反)。Skill プリロードは「武器庫の棚卸し」。使える道具があるのに手作業するのは時間の無駄。
>
> **圏論**: Mem の射を Ses の射に変換する関手 L の「射の部分」を構築する。
> ツール設定、認知態勢、CCL パターンなど、記憶の関係性を作業状態の関係性に写像する。
> 詳細: [boot/system.md](../workflow-modules/boot/system.md)

- プロファイル確認 (GEMINI.md) — **L の設定パラメータ**
- コアモジュール有効化 (O1, O2) — **L の基底射を有効化**
- 認知態勢 (Hexis) — **L の射の精度調整**
- CCL コアパターン — **L の射の文法**
- tools.yaml 読込 — **L で利用可能な射の一覧**
- Gnōsis 鮮度チェック — **Mem 内の対象の鮮度**
- 白血球 — **Mem の未消化対象の検出**

### 4.5 Skill プリロード — L の利用可能な技法を全展開 (環境強制)

> **圏論**: L が利用可能な全ての射（ツール・技法）をコンテキストに読込む。
> **環境強制**: `boot_integration.py` の `_load_skills()` が全 SKILL.md の内容を
> boot 出力に直接含める。Agent は boot 出力を読むだけで全 Skill がコンテキストに入る。
> **コスト**: ~780行 = 200K コンテキストの ~0.4%。有効コンテキストの 2-3% (許容範囲)。

Phase 0 の `boot_integration.py --mode` 実行で自動的にプリロードされる。
追加操作は不要 (view_file も不要)。

---

## Phase 5: 外部射の導入 — 外部入力

> **なぜ**: セッション間に Perplexity が調べたこと、Jules が書いたコードがある。読まなければ「あ、それ Jules がもうやってました」が起きる。既にある成果物を知らずに重複作業するのを防ぐ。
>
> **圏論**: 圏 Mem に、セッション間に発生した外部射を追加する。
> Perplexity = 新しい知識対象、Jules = コードレビュー射、Dispatch Log = AI 行動の射。
> これらは R(S_prev) には含まれない「新鮮な射」であり、L(M) を S_prev より豊かにする。
> 詳細: [boot/external.md](../workflow-modules/boot/external.md)

- Dispatch Log — **他エージェントからの射**
- Perplexity Inbox — **外部知識圏からの射**
- Jules レビュー結果 — **コード圏からの射**

---

## Phase 6: L(M) の出力 — 完了

> **なぜ**: Boot Report は Creator の **意思決定の材料**。PJ 一覧を見て「今日は Agora に集中しよう」と決める。Safety を見て「エラーを先に直そうか」と判断する。**見えなければ選べない。選べなければ決められない。** boot_integration.py が出した情報は一つも削るな。意味がわかっていれば削れない。削ったら意味がわかっていなかったということ。
>
> **圏論**: 左随伴 L の計算が完了。出力 L(M) = 今回のセッション状態。
> ε 精度 = L(R(S_prev)) と S_prev の近さ。Drift が低いほど良い随伴。
> テンプレート: [boot/templates.md](../workflow-modules/boot/templates.md)

```
HEGEMONIKON BOOT COMPLETE v5.0 — L(M) = Ses
```

| Phase | 圏論 | Status | 内容 |
|:------|:-----|:-------|:-----|
| 0. Identity | id_L | Done | 連続性スコア: X.XX |
| 1. 正本読込 | L の定義 | Done | boot.md v5.0 |
| 2. セッション | R(S_prev) | Done | Handoff / Drift XX% (ε = 0.XX) |
| 3. 知識読込 | Mem 展開 | Done | Sophia N件 / KI M件 |
| 4. システム | L の射構築 | Done | tools / Gnōsis |
| 5. 外部入力 | 外部射 | Done | Perplexity / Jules |
| 6. 完了 | L(M) 出力 | Ready | 起動完了 |

### 6.1 開発中プロジェクト — 全件出力 (省略禁止)

> **環境強制**: registry.yaml の全 PJ を **個別に** Boot Report に出力する。
> **端折る = Creator の意思決定材料を奪う**。PJ 一覧は Creator が「今日は何に取り組むか」を決めるためのダッシュボード。
> 「多いから要約した」「重要なものだけ選んだ」は禁止。選ぶのは Creator の仕事。

**出力フォーマット** (各 PJ について全フィールドを表示):

```
| PJ | Phase | Status | Summary |
|:---|:------|:-------|:--------|
| {name} | {phase} | {status_icon} | {summary — 切り捨てない} |
| ... | ... | ... | ... |
```

**出力要件**:

- registry.yaml の **全件** を出力 (active, dormant, archived, planned 全て含む)
- summary は切り捨てない（50文字制限は `boot_integration.py` のコンソール出力用であり、Boot Report には適用しない）
- latest Handoff から PJ ごとの最新状態を補足できれば追記する
- テンプレート詳細: [boot/templates.md](../workflow-modules/boot/templates.md)

### 6.2 タスク提案

Handoff から抽出したタスク提案を表示

### 6.5 Post-Check — L(M) の品質検証

> **環境強制**: postcheck が PASS しなければ Creator に報告してはならない。
> `<!-- FILL -->` が残存 = 未消化。チェックリスト未完了 = 手抜き。

**手順**:

1. Phase 6 の `boot_integration.py --mode detailed` 出力に `TEMPLATE:/tmp/boot_report_XXXX.md` が含まれる
2. テンプレートファイルに `write_to_file` で全セクションを記入する
3. 記入後に postcheck を実行する:

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/symploke/boot_integration.py --postcheck "$(ls -t /tmp/boot_report_*.md 2>/dev/null | head -1)" --mode detailed
```

**FAIL 時**: 不足セクションを補完してから Creator に報告すること。PASS するまでループ。

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| O1, H4 | /boot | v5.0 Ready |

> **制約リマインダ**: Phase 0→6 を順序通り実行すること。スキップ禁止。

---

*v4.1 — FBR 適用 (2026-02-07)*
*v5.0 — 随伴深層統合。各Phase を左随伴 L の計算ステップとして再定義 (2026-02-08)*
*v5.1 — Intent-WAL (Phase 2.5) 追加。随伴のη明示化 (2026-02-10)*
*v5.2 — Quota API チェック + Quota-Based Turtle Mode (Phase 2.7) 追加。agq-check.sh ネイティブ統合、Claude 残量 ≤ 20% で自動 /bye 提案 (2026-02-12)*
*v5.3 — セッション履歴サマリー (Phase 2.7) 追加。agq-sessions.sh で過去セッション一覧を /boot 時に自動表示 (2026-02-13)*
