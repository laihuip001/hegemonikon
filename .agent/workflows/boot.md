---
description: セッション開始時の統合ブートシーケンス。二人で起動する。
hegemonikon: O1 Noēsis + H4 Doxa
version: "4.0"
lcm_state: stable
derivatives:
  "+": 詳細起動（全ステップ展開、Handoff 10件、KI 5件）→ boot/identity.md 参照
  "-": 高速起動（最小情報のみ、1分で開始）
---

# /boot ワークフロー

> **Hegemonikón**: O1 Noēsis (認識) + H4 Doxa (記憶読込)
> **設計思想**: /boot は AI と Creator の「二人で起動する」儀式。
> Creator は忘れっぽい。AI は毎回忘却から始まる。だから情報はプッシュで良い。
>
> **制約**: Phase 0 (Identity Stack) → Phase 1 (正本読込) の順序を守ること。Phase 2 で週次レビュートリガーを必ず判定すること。

// turbo-all

---

## サブモジュール

| Phase | ファイル | 内容 |
|-------|----------|------|
| 0 | [identity.md](boot/identity.md) | Identity Stack 読込 |
| 0.5 | [change-tracking.md](boot/change-tracking.md) | セッション間変化の追跡 |
| 3 | [knowledge.md](boot/knowledge.md) | 知識読込 (Sophia/KI/FEP) |
| 4 | [system.md](boot/system.md) | システム更新 (Hexis/Gnōsis) |
| 5 | [external.md](boot/external.md) | 外部入力 (Perplexity/Jules) |
| - | [templates.md](boot/templates.md) | 出力テンプレート |

---

## Phase 0: Identity Stack 読込

> 詳細: [boot/identity.md](boot/identity.md)

```bash
cd ~/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python mekhane/symploke/boot_integration.py --mode ${BOOT_MODE:-standard}
```

| BOOT_MODE | 用途 |
|-----------|------|
| `fast` | /boot- |
| `standard` | /boot |
| `detailed` | /boot+ |

### 0.1 Self-Profile 消化

> KI `hegemonikon_core_system/artifacts/identity/self_profile.md` を読み込み、
> 自分の能力境界とミスパターンを**消化**する。保存ではなく消化。

確認事項:

| 項目 | 確認 |
|:-----|:-----|
| 直近のミスパターン | 同じ失敗を繰り返さないか |
| 能力境界マップ | 苦手な領域に入る時は確認を増やす |
| 同意/反論の傾向 | 前回の比率を確認し意識する |
| Creator プロファイル | `自己分析テキスト(AI用).md` から好み・癖を把握 |

---

## Phase 1: 正本読込 (Anti-Stale)

```bash
view_file ~/oikos/hegemonikon/.agent/workflows/boot.md
```

---

## Phase 2: セッション状態確認

### 2.1 週次レビュー判定

```bash
ls -1t ~/oikos/mneme/.hegemonikon/sessions/weekly_review_*.md | head -1
ls -1 ~/oikos/mneme/.hegemonikon/sessions/handoff_*.md | wc -l
```

**トリガー**: 7日以上経過 OR Handoff 15件以上

### 2.2 前回 Handoff 読込

対象: `~/oikos/mneme/.hegemonikon/sessions/handoff_*.md` の最新

### 2.3 目的リマインド (Boulēsis)

最新の `/bou` 出力から現在の目的を取得

### 2.4 Drift 診断

目的と現在の軸の乖離度を評価 (0-100%)

---

## Phase 3: 知識読込

> 詳細: [boot/knowledge.md](boot/knowledge.md)

- H4 長期記憶 (patterns.yaml, values.json)
- Sophia 知識サマリー
- FEP A行列読込
- KI ランダム想起

---

## Phase 4: システム更新

> 詳細: [boot/system.md](boot/system.md)

- プロファイル確認 (GEMINI.md)
- コアモジュール有効化 (O1, O2)
- 認知態勢 (Hexis)
- CCL コアパターン
- tools.yaml 読込
- Gnōsis 鮮度チェック
- 白血球 — 未消化サジェスト

---

## Phase 5: 外部入力

> 詳細: [boot/external.md](boot/external.md)

- Dispatch Log
- Perplexity Inbox
- Jules レビュー結果

---

## Phase 6: 完了

> テンプレート: [boot/templates.md](boot/templates.md)

```
HEGEMONIKON BOOT COMPLETE v4.1
```

| Phase | Status | 内容 |
|:------|:-------|:-----|
| 0. Identity | Done | 連続性スコア: X.XX |
| 1. 正本読込 | Done | boot.md v4.1 |
| 2. セッション | Done | Handoff / Drift XX% |
| 3. 知識読込 | Done | Sophia N件 / KI M件 |
| 4. システム | Done | tools / Gnōsis |
| 5. 外部入力 | Done | Perplexity / Jules |
| 6. 完了 | Ready | 起動完了 |

### 6.1 開発中プロジェクト

→ 詳細: [boot/templates.md](boot/templates.md)

### 6.2 タスク提案

Handoff から抽出したタスク提案を表示

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| O1, H4 | /boot | v4.1 Ready |

> **制約リマインダ**: Phase 0→6 を順序通り実行すること。スキップ禁止。

---

*v4.1 — FBR 適用 (2026-02-07)*
