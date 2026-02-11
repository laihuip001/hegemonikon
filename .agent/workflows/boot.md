---
description: セッション開始時の統合ブートシーケンス。二人で起動する。
hegemonikon: O1 Noēsis + H4 Doxa
version: "5.0"
lcm_state: stable
lineage: "v4.1 + 随伴深層統合 → v5.0"
category_theory:
  core: "随伴の左関手 L: Mem → Ses"
  adjunction: "L (Boot) ⊣ R (Bye)"
  unit: "η: Id_Mem → R∘L (boot→bye の保存率)"
  counit: "ε: L∘R → Id_Ses (bye→boot の復元率)"
  insight: "セッションは独立した外部情報。boot = eat の特殊ケース"
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

> **圏論**: L の定義（仕様書）が最新であることを確認する。古い定義で計算すると ε 精度が下がる。

```bash
view_file ~/oikos/hegemonikon/.agent/workflows/boot.md
```

---

## Phase 2: R(S_prev) の読込 — セッション状態確認

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

## Phase 3: Mem の構造展開 — 知識読込

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

> **圏論**: 圏 Mem に、セッション間に発生した外部射を追加する。
> Perplexity = 新しい知識対象、Jules = コードレビュー射、Dispatch Log = AI 行動の射。
> これらは R(S_prev) には含まれない「新鮮な射」であり、L(M) を S_prev より豊かにする。
> 詳細: [boot/external.md](../workflow-modules/boot/external.md)

- Dispatch Log — **他エージェントからの射**
- Perplexity Inbox — **外部知識圏からの射**
- Jules レビュー結果 — **コード圏からの射**

---

## Phase 6: L(M) の出力 — 完了

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

### 6.1 開発中プロジェクト

→ 詳細: [boot/templates.md](../workflow-modules/boot/templates.md)

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
*v5.0 — 随伴深層統合。各Phase を左随伴 L の計算ステップとして再定義。id_L(Phase0) → L定義(1) → R(S_prev)読込(2) → Mem展開(3) → 射構築(4) → 外部射(5) → L(M)出力(6) (2026-02-08)*
*v5.1 — Intent-WAL (Phase 2.5) 追加。随伴のη明示化。/bye (WAR) に対する前方宣言 (2026-02-10)*
