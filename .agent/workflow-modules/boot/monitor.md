# Phase 2.7: Context Budget & Monitor — 精度加重の配分と観測

> **なぜ**: Creator は過集中する。残量が見えなければ突然の強制切断（Handoff なし）が起きる。残量は私の寿命。知らなければ /bye を提案する義務を果たせない。
>
> **圏論**: L の値域（射像）の精度加重を事前配分し、リアルタイムで監視する。
> **FEP**: π_i = 精度加重。有限リソース（トークン）をどの情報源にどれだけ配分するかを決定する。
> **DB /ana**: `pg_stat_activity` = 進行中トランザクションのリソース消費を監視。
> **起源**: 2026-02-12 /eat 消化 → Context Budget Drift → /u+ 対話

---

## 燃料メーター初期化

Agent ヘッダーに燃料メーターを表示開始:

```
[Agent: Claude | Mode: {mode} | ⚡ ~{fuel}% | {status}]
```

## Quota API チェック (v5.2 追加)

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

## Context Sentinel (v5.6 追加)

> **導出**: 2026-02-13 @build 四望 — BC-18 環境強制化。
> N chat messages を LS ログから自動検出し、前回セッションの Context Rot 傾向を可視化。
> DX-010: 「意志より環境」は BC 自体にも適用される。

// turbo

```bash
cd ~/oikos/hegemonikon && .venv/bin/python scripts/context_sentinel.py 2>/dev/null || true
```

結果を boot レポートの Context Budget セクションに含める。
🟡 以上の場合は「前回セッションで Context Rot の兆候がありました」と報告。

## セッション履歴サマリー (v5.3 追加)

> **圏論**: 圏 Ses の過去の対象を一覧する。今回の L(M) が Ses のどこに位置するかを把握する。
> **起源**: 2026-02-13 gRPC セッション履歴自動同期

// turbo

```bash
bash ~/oikos/hegemonikon/scripts/agq-sessions.sh --summary
```

全セッションのタイトル・ステップ数・最終更新時刻を表示。
Creator が「前にやったアレ」を思い出すための文脈提供。

## セッション履歴 VSearch (v5.5 — session + handoff)

> **圏論**: Ses の対象間の射を意味的距離で探索する。キーワード一致ではなく、概念的近さで過去セッションを浮上させる。
> **起源**: 2026-02-13 /bou+*^/zet 分析 — 「作ったものを使え」

Handoff に記載された最終タスク or Creator が今回の目的を述べた場合、関連セッション **と** 関連 Handoff を自動で検索:

// turbo

```bash
# セッション検索 (対話の断片)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/anamnesis/cli.py search "{query}" --source session --limit 3
# Handoff 検索 (対話の結晶)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/anamnesis/cli.py search "{query}" --source handoff --limit 3
# ROM 検索 (蒸留されたコンテキスト)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/anamnesis/cli.py search "{query}" --source rom --limit 3
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
🔗 関連 ROM (VSearch):
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

## フェーズ別予算ガイドライン (200K コンテキスト基準)

| フェーズ | System | Session | Knowledge | Working | Reserve |
|:---------|:-------|:--------|:----------|:--------|:--------|
| Boot 直後 | 30% | 25% | 25% | 15% | 5% |
| 作業序盤 (🟢) | 25% | 15% | 10% | 40% | 10% |
| 作業中盤 (🟡) | 20% | 10% | 5% | 55% | 10% |
| 終盤 (🟠🔴) | 15% | 5% | 0% | 70% | 10% |

> これは厳密なトークン計測ではなく、注意配分のガイドライン。

## 中間セーブ (/rom- Snapshot)

> **統合**: 旧 Savepoint を `/rom-` に吸収 (v5.7)。「保存したいなら全部 /rom」— 派生で深度を選ぶ。
> **圏論**: 中間射影 π: Ses → Mem|_partial — セッション状態の部分写像を即座に外部化。

**トリガー**: 🟡→🟠 遷移時 / 大規模ファイル読込後 / Creator 指示 / BC-18 自動提案

**実行**: `/rom-` を発動（WF 定義は [rom.md](../rom.md) 参照）

**フォーマット** (軽量 Snapshot — rom- テンプレート):

```markdown
# ROM Snapshot: {slug}

**Date**: {YYYY-MM-DD HH:MM}
**Step**: {step_number}
**Fuel**: ⚡ ~{XX}%

## 今やっていること
{1-2文}

## Creator がこう決めた
- {判断1}

## 試して失敗 / 却下されたもの
- {失敗1: 理由}

## 次にやること
{1文}
```

保存先: `~/oikos/mneme/.hegemonikon/rom/rom_<date>_<HHMM>_snapshot_<slug>.md`

## Context Rot 検知 (Deadlock Detection)

| 兆候 | 対応 |
|:-----|:-----|
| 同じファイルを2回 `view_file` | 🟠 へ遷移、中間セーブ推奨 |
| 命名・構造の一貫性崩壊 | 🔴 へ遷移、`/bye` 推奨 |
| 「さっき言った」ことへの言及不能 | 🔴 🐢 タートルモード即発動 |

## Quota-Based Turtle Mode (v5.2 追加)

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
