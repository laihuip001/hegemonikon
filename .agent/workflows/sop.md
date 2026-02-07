---
description: K4 Sophia（知恵）を発動し、Perplexityに調査を依頼する。深掘り版調査依頼書を生成。
hegemonikon: K4 Sophia
version: "7.0"
lcm_state: stable
triggers: ["調べて", "教えて", "Perplexityに聞いて", "パプ君に聞いて", "リサーチ"]
derivatives:
  "+": 詳細調査（完全リサーチ依頼書、複数視点）
  "-": 即調査（1質問のみ、簡潔）
  "*": メタ調査（調査方針自体を問う）
trigonon:
  series: K
  type: Mixed
  theorem: K4
  coordinates: [Function, U]
  bridge: [S, H]
  anchor_via: [P, A]
  morphisms:
    ">>S": [/met, /mek, /sta, /pra]
    ">>H": [/pro, /pis, /ore, /dox]
modes: [surf, deep, prag, track]
---

# /sop: 情報収集ワークフロー (Sophia)

> **Hegemonikón**: K4 Sophia（知恵）
> **目的**: 外部ソースから情報を収集する — Perplexity 調査依頼を生成
> **役割**: observe 行動 — 環境からの知識取得
>
> **制約**: PHASE 0 (目的確認) を完了するまで PHASE 1 に進んではならない。
> 外部検索の前に、必ず PHASE 0.5 で内部KB検索を実施すること。

---

## サブモジュール

| ファイル | 内容 |
|----------|------|
| [modes.md](sop/modes.md) | 調査モード (surf/deep/prag/track) |
| [templates.md](sop/templates.md) | 調査依頼書テンプレート集 |

---

## 本質

| ステップ | ワークフロー | 役割 |
|:---------|:------------|:-----|
| 問いを立てる | O3 /zet | 問いの発見 |
| 情報を集める | K4 /sop | 知識取得 |
| 深く分析する | O1 /noe | 深い認識 |

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/sop [質問]` | 深掘り版調査依頼書（デフォルト） |
| `/sop simple [質問]` | 簡易版（従来形式） |
| `/sop context [質問]` | 文脈共有ブロック付き |
| `/sop assist [意図]` | Claude が質問案を提案 |

---

## PHASE 0: 目的確認（必須）

> [!IMPORTANT]
> 以下を明確にしてから PHASE 1 に進むこと。

| 項目 | 記入 |
|:-----|:-----|
| **決定事項** | この調査の結果、何を決定するか（1文） |
| **仮説** | 〇〇ではないか？ という事前予想 |
| **反証可能性** | 間違っていた場合、どう検証するか |

---

## PHASE 0.5: 内部 KB 検索（AIDB + Gnosis）

> 外部検索の前に、まず内部で消化済みの知識を確認する。

```bash
# AIDB 検索
cd ~/oikos/hegemonikon && \
.venv/bin/python mekhane/peira/scripts/aidb-kb.py search "[キーワード]" --top 5

# Gnosis ベクトル検索（必ずこちらを使用。grep 禁止）
.venv/bin/python mekhane/anamnesis/cli.py search "[キーワード]"
```

---

## PHASE 1: 調査依頼書生成

> テンプレート: [sop/templates.md](sop/templates.md)

### Hybrid Model（冒頭最適化）

Perplexity は冒頭 500-2000 トークンを優先処理:

| 優先度 | セクション | 内容 |
|:-------|:-----------|:-----|
| **1** | 出力形式 | 構造化テーブル（4列: 項目, 値, 根拠, URL） |
| **2** | タスク定義 | 1-2文で意図を明示 |
| **3** | 時間制約 | 過去6ヶ月優先 |

---

## PHASE 2: 論点設計

> 「例」として列挙するのではなく、**必須項目**として指定する。

| パターン | 例 |
|:---------|:---|
| 避ける | 「認知科学における〇〇を調べてください。例: ...」 |
| 推奨 | 論点を必須項目として番号付きで列挙 |

推奨フォーマット:

```
A. 認知科学における〇〇
- A1: 直観的〇〇 vs 分析的〇〇 の区別は存在するか？
- A2: メタ認知との関係はどう定義されているか？
- A3: 2020年以降の主要論文における新分類は？
```

---

## PHASE 3: 品質チェック

- [ ] 決定事項明確
- [ ] 仮説設定
- [ ] 反証可能性
- [ ] 最新優先（過去6ヶ月）
- [ ] 論点が必須項目として列挙
- [ ] 単一トピック
- [ ] 出力形式明示

---

## PHASE 4: Creator との対話

```
→ この調査依頼書でよいですか？
→ 追加したい論点はありますか？
→ パプ君にコピペして実行しますか？
```

---

## モード

> 詳細: [sop/modes.md](sop/modes.md)

| モード | 目的 | Scale |
|:-------|:-----|:------|
| `surf` | 広く浅く概要把握 | Micro |
| `deep` | 徹底的に調査 | Macro |
| `prag` | 使える情報・手順 | Meso |
| `track` | 調査進捗追跡 | Meso |

---

## Artifact 自動保存

出力先: `~/oikos/mneme/.hegemonikon/workflows/sop_<topic>_<date>.md`

完了時の出力:

- 保存先パスを表示
- 「パプ君にコピペして実行」を提示

---

## Digestor 連携

| ステップ | 内容 |
|:---------|:-----|
| /sop 調査 | Perplexity で情報収集 |
| Gnosis 収集 | 論文をベクトルDBに追加 |
| digestor 選定 | 適切な消化モジュール選択 |
| /eat 消化 | Hegemonikon に統合 |
| 既存WF強化 | 消化結果を反映 |

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| K4 Sophia | /sop | v7.0 Ready |

> **制約リマインダ**: 目的確認 (PHASE 0) → 内部KB検索 (PHASE 0.5) → 調査依頼 (PHASE 1)。順序を守ること。

---

*v7.0 — FBR 適用 (2026-02-07)*

---

## @complete: 射の提案 (暗黙発動 L1)

> WF完了時、`/x` 暗黙発動プロトコルにより射を提案する。
> 計算ツール: `python mekhane/taxis/morphism_proposer.py sop`

```
/sop 完了 → @complete 発動
→ 結果に確信がありますか？ (Y: Anchor優先 / N: Bridge優先 / 完了)
```
