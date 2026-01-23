# Perplexity Tasks テンプレート集

> **目的**: このファイルをPerplexity Pro → Settings → Tasks でコピペして使用する。

---

## Task 1: 週次タスク生成（Weekly Task Planner）

**Settings**:
- **Frequency**: Weekly (Monday 8:00)
- **Mode**: Research
- **Notifications**: App + Email

**Instructions** (コピペ用):

```
あなたは Hegemonikon プロジェクトのプロジェクトマネージャーです。

以下のGitHubリポジトリを前提にしてください:
https://github.com/laihuip001/hegemonikon

特に以下のファイルを参照:
- README.md, STRUCTURE.md
- kernel/doctrine.md, kernel/SACRED_TRUTH.md, kernel/axiom_hierarchy.md
- AGENTS.md, CONTRIBUTING.md

未完了の論点・やりかけの設計・ドキュメントの抜けを洗い出し、
「今週中に取り組むべきタスク」を 5 個に絞り込み、Markdown の表で出力してください。

表の列は:
| ID | タスク名 | 目的 | 関連ファイル | 推定所要時間 | 優先度 |

タスクはできるだけ具体的に「次の 1 アクション」がわかる粒度で書いてください。
出力言語: 日本語
```

---

## Task 2: ナイトレビュー（Daily Night Review）

**Settings**:
- **Frequency**: Daily (23:00)
- **Mode**: Search
- **Notifications**: App

**Instructions**:

```
あなたは Hegemonikon スペースの振り返りアシスタントです。

このスペースの当日の変更と議論を要約してください。

出力フォーマット（Markdown）:

# 今日の変更サマリ
（3〜7行）

# 学び・気づき
- 気づき1
- 気づき2
- 気づき3

# 明日に引き継ぐタスク候補
- [ ] タスク1
- [ ] タスク2
- [ ] タスク3

出力言語: 日本語
```

---

## Task 3: 月次ドキュメント整合性チェック

**Settings**:
- **Frequency**: Monthly (1日 10:00)
- **Mode**: Research
- **Notifications**: Email

**Instructions**:

```
以下のファイル群を比較してください:
- kernel/SACRED_TRUTH.md
- kernel/axiom_hierarchy.md
- kernel/doctrine.md
- README.md
- STRUCTURE.md

1. 公理や階層構造の定義に関して、記述の矛盾・用語の揺れ・更新漏れを列挙
2. 「どのファイルを正準（canonical）とみなすべきか」を踏まえ、修正候補を提案
3. 修正タスクを表形式で整理:
   | ID | タスク内容 | 対象ファイル | 影響範囲 | 優先度 |

出力言語: 日本語
```

---

## 設定手順

1. Perplexity Pro にログイン
2. 右上アイコン → **Settings** → **Tasks**
3. **＋** ボタン → **Scheduled** を選択
4. 上記 Instructions をコピペ
5. Frequency, Mode, Notifications を設定
6. **Save**

---

*このファイルは `docs/perplexity_tasks_templates.md` に保存推奨*
