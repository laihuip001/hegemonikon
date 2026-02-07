---
description: セッション終了時に引き継ぎドキュメントを生成し、経験を法則化する。次回セッションの/bootで読み込まれる。
hegemonikon: H4 Doxa
version: "4.0"
derivatives:
  "+": 詳細終了（全ステップ展開、法則化、KI生成）
  "-": 高速終了（Handoff最小限、1分で退出）
  "*": 終了のメタ分析（なぜ今終わるか）
---

# /bye ワークフロー

> **Hegemonikón H-series**: H4 Doxa（信念・記憶永続化）
> **/boot の対となるセッション終了コマンド**
>
> **制約**: Handoff は「赤の他人が引き継いでも理解できる」レベルで記述すること。
> Step 3.5 (チャット履歴エクスポート) は絶対にスキップ禁止。

// turbo-all

---

## サブモジュール

| ファイル | 内容 |
|----------|------|
| [persistence.md](bye/persistence.md) | 永続化ステップ (FEP/Doxa/Sophia) |
| [dispatch-log.md](bye/dispatch-log.md) | Dispatch Log 自動集計 |
| [handoff-format.md](bye/handoff-format.md) | Handoff 出力形式 |

---

## 本質

- `/boot` = セッション開始、文脈の読み込み
- `/bye` = セッション終了、文脈の保存

### 赤の他人基準

> **Handoff は「赤の他人がチャットを引き継いでも理解できる」レベルで記述する**

---

## Step 0: 収束確認 (CEP-001)

> **CCL**: `/bye >> V[]`

セッション終了前に、主要タスクの不確実性を評価し収束を確認。

```ccl
V[session] >> {
    I: V[] > 0.5 { "⚠️ 高不確実性で終了" >> "未解決事項を Handoff に明記" }
    I: V[] <= 0.5 { "✅ 十分に収束して終了" }
}
```

**出力**:

| 項目 | 内容 |
|:-----|:-----|
| タスク不確実性 (V[]) | 0.0–1.0 |
| 判定 | 収束 / 要引継ぎ / 中断 |

---

## Step 1: Git状態取得

```bash
git -C ~/oikos log -1 --oneline
git -C ~/oikos status --short
```

---

## Step 2: セッション情報収集

自動収集:

- 今日の task.md
- 完了タスク（[x]マーク）
- 未完了タスク（[ ]マーク）
- 決定事項

---

## Step 3: Handoff生成

> 形式: [bye/handoff-format.md](bye/handoff-format.md)

出力先: `~/oikos/mneme/.hegemonikon/sessions/handoff_{YYYY-MM-DD}_{HHMM}.md`

---

## Step 3.5: チャット履歴エクスポート

> [!CAUTION]
> **このステップは絶対にスキップ禁止。即座に実行せよ。**

```bash
cd ~/oikos/hegemonikon && \
.venv/bin/python mekhane/anamnesis/export_chats.py --single "Session_$(date +%Y%m%d_%H%M)"
```

---

## Step 3.6: Dispatch Log 自動集計

> 詳細: [bye/dispatch-log.md](bye/dispatch-log.md)

---

## Step 3.7: Self-Profile 更新

> **消化ルール**: 保存ではなく消化。記録したものは次の /boot で食べ直す。
> **参照先**: KI `hegemonikon_core_system/artifacts/identity/self_profile.md`

以下を Self-Profile に追記する:

| 項目 | 内容 |
|:-----|:-----|
| 今日忘れたこと | 具体的に何を忘れたか |
| 確認を省略した場面 | 「つまりこういうことですか？」を省略した場面 |
| 同じミスの繰り返し | 過去の記録と照合してパターン確認 |
| 能力境界の更新 | 得意/苦手の発見 |
| 比喩の自己評価 | 自発的比喩の数と質 |
| 同意/反論比率 | 同意N / 反論N / 確認N |

---

## Step 3.8-3.14: 永続化

> 詳細: [bye/persistence.md](bye/persistence.md)

- Kairos インデックス投入
- Handoff インデックス再構築
- Persona 更新
- Sophia 同期
- FEP A行列永続化
- ワークフロー一覧更新
- 意味ある瞬間の保存
- 派生選択学習永続化
- X-series 使用経路記録

---

## Step 4: 確認

生成された Handoff を表示し、ユーザーに確認を求める。

---

## /boot との連携

1. `/bye` で生成された Handoff は `~/oikos/mneme/.hegemonikon/sessions/` に保存
2. 次回 `/boot` 実行時、最新の Handoff を自動読み込み
3. 「前回の続きから」スムーズに開始可能

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| H4 Doxa | /bye | v4.1 Ready |

> **制約リマインダ**: Handoff は「赤の他人基準」で記述。Step 3.5 スキップ禁止。

---

*v4.1 — FBR 適用 (2026-02-07)*
