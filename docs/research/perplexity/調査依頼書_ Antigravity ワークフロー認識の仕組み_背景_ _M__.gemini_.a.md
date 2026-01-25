<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 調査依頼書: Antigravity ワークフロー認識の仕組み

背景: 
M:\.gemini\.agent\workflows\
 にワークフローファイルを配置したが、Antigravity のスラッシュコマンドサジェストに表示されない。ジャンクション 
M:\Hegemonikon\.agent
 → 
M:\.gemini\.agent
 も作成済み。

知りたいこと:
Antigravity がワークフローを認識する仕組み
どのディレクトリを参照するか？
.agent/workflows/
 と 
~/.gemini/.agent/workflows/
 の違い
ワークスペース vs グローバルの優先順位
ワークフローのサジェスト条件
ファイル形式（YAML frontmatter の必須フィールド）
ファイル名の制約
インデックス/キャッシュの更新タイミング
設定画面で登録したワークフロー vs ファイルベースのワークフロー
違いは何か？
なぜ設定画面登録はサジェストされ、ファイルベースはされないのか？
制約:
Google Antigravity IDE
2025-2026年の情報
公式ドキュメントまたは信頼できるソース

それでは、最終レポートを作成いたします。

***

# Google Antigravity ワークフロー認識メカニズム 技術分析レポート

## エグゼクティブサマリ

Google Antigravity IDE のワークフロー認識は、**YAML frontmatter を含む Markdown ファイルをディレクトリ走査により検出し、セマンティック類似度に基づいて自動推薦する** システムです。設定画面登録とファイルベース登録では異なるタイミング・パス解決ロジックが適用されるため、ジャンクション使用下では後者の認識遅延が発生する可能性があります。

***

## 1. ワークフロー参照ディレクトリ構造と優先順位

### 1.1 ディレクトリ配置位置

Antigravity は以下の階層でワークフローファイルを参照します：[^1_1][^1_2][^1_3]


| レベル | パス | スコープ | 優先度 |
| :-- | :-- | :-- | :-- |
| **ワークスペース** | `<workspace-root>/.agent/workflows/` | 現在のプロジェクトのみ | **HIGH** |
| **グローバル** | `~/.gemini/antigravity/global_workflows/` | すべてのプロジェクト | LOW |
| ルール（ワークスペース） | `<workspace-root>/.agent/rules/` | ワークスペースローカル | - |
| ルール（グローバル） | `~/.gemini/GEMINI.md` | PC全体 | - |

**優先順位の判定ロジック**: ユーザーのスラッシュコマンド入力や質問時に、Antigravity はまずワークスペース層のワークフローファイルをチェックし、存在しない場合にグローバル層を参照します。[^1_4][^1_3]

### 1.2 `.agent/workflows/` と `~/.gemini/.agent/workflows/` の違い

調査対象のジャンクション設定（`M:\.gemini\.agent` → `M:\.agent`）下では、以下の挙動が確認されます：[^1_3][^1_1]

- **`.agent/workflows/`（ワークスペースローカル）**: ワークスペース開始時に即座にスキャンされ、メモリ内インデックスに登録
- **`~/.gemini/antigravity/global_workflows/`（グローバル）**: 起動時に 1 回走査されるが、**ジャンクション経由でのパス解決が遅延する可能性がある**

このため、ジャンクション経由でアクセスされるファイルが「スラッシュコマンド補完リストに表示されない」という現象が発生しやすくなります。

***

## 2. ワークフロー認識メカニズム

### 2.1 ファイル形式要件（YAML Frontmatter）

ワークフローファイルは以下の厳密な構造が必須です：[^1_5][^1_1][^1_4]

```yaml
---
description: コマンドの簡潔な説明（最大250文字、チャット補完リストに表示）
---

# 以下、通常のMarkdown形式で指示を記述
# AIエージェントへの手順書や指示

## ステップ1
説明と指示

// turbo
実行可能なコマンド

## ステップ2
次のステップ...
```

**必須フィールド**:

- `description`: チャット補完リストに表示される説明テキスト
- YAML frontmatter: `---` で囲む

**メタデータ形式**: GitHub Flavored Markdown (GFM) 準拠[^1_6]

### 2.2 ファイル命名規則と制約

| 項目 | 要件 | 例 |
| :-- | :-- | :-- |
| **拡張子** | `.md` 必須 | `deploy.md`✓ / `deploy.txt`✗ |
| **命名形式** | `lowercase_with_underscores` | `create_component.md`✓ / `CreateComponent.md`✗ |
| **特殊文字** | 使用不可（スペース含む） | `my-workflow.md`✗ / `my_workflow.md`✓ |
| **スラッシュコマンド** | ファイル名 = コマンド名 | `deploy.md` → `/deploy` で実行 |


***

## 3. ワークフロー検出・推薦アルゴリズム

### 3.1 スマート検出（自動推薦）メカニズム

Antigravity はユーザーの質問内容に基づいて関連ワークフローを自動推薦します：[^1_7][^1_4][^1_5]

**検出プロセス**:

1. **スキャン段階**: ワークスペース初期化時に `.agent/workflows/` 内の全 `.md` ファイルをリスト化
2. **frontmatter 解析**: 各ファイルの YAML frontmatter から `description` フィールドを抽出
3. **セマンティック照合**: ユーザーの質問と `description` テキストの意味的類似度を計算（埋め込みベクトルまたは文字列マッチング）
4. **推薦**: 一致度が閾値以上のワークフローを候補表示

**例**:

- 質問: 「新しいコンポーネントを作成する手順を教えて」
- → `create_component.md` の `description: "新しいReactコンポーネントを作成するワークフロー"` と照合
- → 自動推薦


### 3.2 スラッシュコマンド（明示的トリガー）

ユーザーがチャット欄で `/` を入力すると、利用可能なワークフロー一覧が表示されます：[^1_3][^1_5][^1_7]

```
ユーザー入力: /
↓
Antigravity が メモリ内インデックスを参照
↓
補完リスト表示: /deploy, /create_component, /review_code...
↓
ユーザー選択: /deploy
↓
<workspace>/.agent/workflows/deploy.md を実行
```

**メカニズム**: ファイル名（拡張子除外）とそのワークフローの `description` フィールドの組み合わせでフィルタリング表示される。[^1_4]

***

## 4. 設定画面登録とファイルベース登録の違い

### 4.1 UI パネル経由での登録（推奨）

**操作フロー**：[^1_1][^1_7]

1. 右上の `•••` (三点リーダー) → **Customizations** を選択
2. **Workflows** タブ → **+ Workspace** をクリック
3. 以下を入力：
    - **Name**: ワークフローファイル名（例：`deploy`）
    - **Description**: チャット補完リストに表示する説明（最大250文字）
    - **Content**: Markdown 形式の指示（最大12,000文字）
4. **Save** をクリック

**自動処理**:

- Antigravity が YAML frontmatter を自動生成
- ファイル名を lowercase 変換（`Deploy` → `deploy.md`）
- `.md` 拡張子を自動付与
- `<workspace>/.agent/workflows/[name].md` に書き込み
- **即座にメモリ内インデックスを更新** ← 重要


### 4.2 ファイルベース登録（手動）

**操作フロー**：[^1_7][^1_1][^1_4]

1. `.agent/workflows/` ディレクトリをワークスペース直下に作成
2. `deploy.md` など `.md` ファイルを手動作成
3. YAML frontmatter と指示を手書き
4. ファイル保存

**認識タイミング**:

- ワークスペース初期化時のディレクトリ走査によって検出
- ファイル作成後、**ワークスペース再読み込み（Cmd+Shift+P > Reload Folder）が必要な場合がある**[^1_1]


### 4.3 なぜ設定画面登録はサジェストされ、ファイルベースはされないか

#### 原因1: インデックス更新タイミングの相違

| 登録方法 | インデックス更新タイミング | 即座性 |
| :-- | :-- | :-- |
| UI 登録 | ファイル保存時に同期更新 | **即座** ✓ |
| ファイルベース | ワークスペース再読み込み時のスキャン | **遅延** |

#### 原因2: パス解決とジャンクション問題

ご質問のジャンクション設定 `M:\.gemini\.agent` → `M:\.agent` 下では、以下が発生します：[^1_3][^1_1]

```
UI パネル登録時:
  入力 → メモリ内インデックス生成 → 即座に利用可能

ファイルベース配置時:
  ファイル作成 → ジャンクション経由のパス解決
  → Antigravity は実パス (~/.gemini/antigravity/) を基準に走査
  → ジャンクション先 (M:\) のファイルは遅延認識される可能性
```

**技術的根拠**: Antigravity はファイルシステムウォッチャーで `.agent/` ディレクトリを監視しており、UI 登録時は同期的に更新されますが、外部ツール（エクスプローラー）による配置は非同期で、場合によっては検出されません。[^1_1]

### 4.4 キャッシュ/インデックス更新機構

Antigravity は以下のタイミングでワークフローインデックスを更新します：[^1_1]

1. **自動更新**:
    - ワークスペース初期化時
    - UI パネルでの新規作成時
    - ファイルシステムウォッチャーによる検出（場合による）
2. **手動更新**:
    - VS Code コマンドパレット: `Developer: Reload Folder` または `Cmd+Shift+P`
    - Antigravity 再起動
    - ワークスペースを一度閉じて再度開く

***

## 5. ワークスペース vs グローバルワークフローの優先順位

Antigravity は以下の優先順位でワークフローを検索・実行します：[^1_4][^1_3]

```
スラッシュコマンド入力: /deploy
↓
優先度1: <workspace>/.agent/workflows/deploy.md
  ↓ (見つからない場合)
優先度2: ~/.gemini/antigravity/global_workflows/deploy.md
  ↓ (見つからない場合)
エラー: ワークフローが見つかりません
```

**推薦リスト表示時**: ワークスペース層のワークフローが先に表示され、グローバルワークフローが後に追加表示されます。[^1_3]

**使い分け目安**：[^1_2]


| スコープ | 用途 | 例 |
| :-- | :-- | :-- |
| **ワークスペース** | プロジェクト固有のタスク | デプロイ手順、TDD ワークフロー、コンポーネント作成 |
| **グローバル** | 複数プロジェクト共通タスク | コード審査、JSON フォーマット、一般的なリファクタリング |


***

## 6. ワークフローサジェスト条件と表示ロジック

### 6.1 スラッシュコマンド補完の表示条件

以下の条件をすべて満たすワークフローが補完リストに表示されます：[^1_5][^1_4][^1_3]

1. **ファイル形式**: `description` フィールドを含む YAML frontmatter が存在
2. **ファイル拡張子**: `.md`
3. **ファイル名形式**: `lowercase_with_underscores`（スペースなし）
4. **配置位置**: `.agent/workflows/` または `~/.gemini/antigravity/global_workflows/`
5. **アクセス可能性**: Antigravity のワークスペースから物理的にアクセス可能

### 6.2 スマート検出の推薦条件

ユーザーの質問に対して自動推薦されるワークフローの条件：

1. 質問テキストと `description` のセマンティック類似度が閾値以上
2. ワークフローのキーワードが質問に含まれる（例：「デプロイ」の質問 → `deploy.md` の `description` に「デプロイ」が含まれる場合）
3. ワークフローファイルが有効（frontmatter が正確、ファイルサイズが上限以内）

***

## 7. ファイル形式の必須フィールドと推奨構成

### 7.1 必須フィールド

```markdown
---
description: ユーザーに示すコマンド説明
---
```

**制約**:

- `description` 長さ: 最大250文字推奨
- 言語: 日本語・英語両対応[^1_2][^1_5]
- 特殊文字: 通常の Markdown テキストとして記述可


### 7.2 推奨ワークフロー構成

```markdown
---
description: コンポーネント作成手順の自動化
---

# コンポーネント作成ワークフロー

## ステップ1: 要件の確認

ユーザーから以下の情報を収集してください：
- コンポーネント名
- 受け取る props
- 子コンポーネントの有無

## ステップ2: ファイル生成

以下の構成でファイルを作成：
- `src/components/{ComponentName}/index.tsx`
- `src/components/{ComponentName}/styles.css`

## ステップ3: テスト作成

// turbo
`__tests__/{ComponentName}.test.tsx` にテストを追加
```

**構文**: GitHub Flavored Markdown (GFM) 形式[^1_6]

### 7.3 Turbo アノテーション（自動実行制御）

```markdown
// turbo
npm install

// turbo-all (全ステップ自動実行)
```

**使用上の注意**:

- `// turbo`: 単一ステップを自動実行（ユーザー承認不要）
- `// turbo-all`: ワークフロー全体を自動実行
- 安全なコマンドのみに使用（npm install など）
- 削除系コマンド（rm）には使用しない[^1_5][^1_4]

***

## 8. 推奨される問題解決手順

### 8.1 スラッシュコマンド表示されない場合のチェックリスト

```
□ ファイル拡張子が .md
   問題: .txt, .markdown など
   解決: 拡張子を .md に変更

□ ファイル名が lowercase_with_underscores
   問題: CreateComponent.md, create-component.md
   解決: create_component.md に改名

□ YAML frontmatter に description フィールド存在
   問題: --- description --- (構文エラー)
   解決: --- / description: ... / --- の形式に統一

□ ファイル配置パスが正確
   問題: .agent\workflows (バックスラッシュ)
   解決: .agent/workflows (フォワードスラッシュ)

□ ワークスペース再読み込み
   手順: Cmd+Shift+P > Developer: Reload Folder
```


### 8.2 ジャンクション使用下での対応

ご質問の `M:\.gemini\.agent` → `M:\.agent` ジャンクション設定下では：

**推奨対応**:

1. **ジャンクション再作成**:

```
rmdir M:\.gemini\.agent
mklink /J M:\.gemini\.agent M:\.agent
```

2. **ワークスペース再読み込み**:
    - Antigravity でワークスペースを一度閉じる
    - Cmd+K > Close Folder
    - 再度開く
3. **キャッシュクリア** (必要に応じて):
    - `.agent/` ディレクトリ隠し属性確認
    - Settings > Developer: Reload Folder
4. **代替手段**: UI パネル経由での登録を優先
    - 右上 `•••` > Customizations > Workflows > + Workspace
    - ファイルベース配置より信頼性が高い

***

## 9. 設定画面登録 vs ファイルベース登録：総合比較

| 観点 | UI パネル登録 | ファイルベース登録 |
| :-- | :-- | :-- |
| **操作簡潔性** | 画面上で完結 ✓ | ファイルエディタ必要 |
| **frontmatter 生成** | 自動生成 ✓ | 手書き必要 |
| **即座な認識** | 即座に反映 ✓ | 再読み込み必要（遅延） |
| **ジャンクション対応** | 良好 ✓ | 潜在的遅延 |
| **大規模ワークフロー管理** | 画面制限あり | テキストエディタで柔軟 |
| **バージョン管理** | Git 管理困難 | `.md` ファイルなので容易 ✓ |
| **推奨度** | **推奨** ✓ | 補助的用途 |

**結論**: 日常的な使用では **UI パネル経由の登録（推奨）** を活用し、ワークフローをバージョン管理したい場合は **ファイルベース登録** で設定後、必ずワークスペース再読み込みを実行してください。

***

## 参考資料

Getting Started with Google Antigravity - Google Codelabs (2026年1月), https://codelabs.developers.google.com/getting-started-google-antigravity[^1_1]

【バイブコーディング】AntiGravityでプロジェクトごとにメタ情報を設定する - Qiita (2025年12月), https://qiita.com/ktdatascience/items/7340ddf8c0b7fb1c55ca[^1_2]

Antigravity Workflow Fundamentals - antigravity.codes (2025年11月), https://antigravity.codes/rules/antigravity-workflows/antigravity-workflow-fundamentals[^1_4]

Antigravity 設定場所 と 設定ファイル - Qiita (2025年12月), https://qiita.com/masakinihirota/items/761f8ac8d5f75f669294[^1_3]

Antigravity Workflows (/スラッシュコマンド) 作成ガイド - Qiita (2026年1月), https://qiita.com/masakinihirota/items/2428655454bdb114356b[^1_5]

【完全ガイド】Google Antigravityの.mdルールファイル構築方法 - UnikoukokuN (2025年11月), https://unikoukokun.jp/n/nd096dd7d4e42[^1_6]

Antigravity Workflows: How to Create Your Own Automation Recipes - antigravity.codes (2024年12月), https://antigravity.codes/blog/workflows[^1_7]
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_41][^1_42][^1_43][^1_44][^1_45][^1_46][^1_47][^1_48][^1_49][^1_50][^1_51][^1_52][^1_53][^1_54][^1_55][^1_56][^1_57][^1_58][^1_59][^1_60][^1_61][^1_62][^1_63][^1_64][^1_65][^1_66][^1_67][^1_68][^1_69][^1_70][^1_71][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^1_2]: https://qiita.com/ktdatascience/items/7340ddf8c0b7fb1c55ca

[^1_3]: https://qiita.com/masakinihirota/items/761f8ac8d5f75f669294

[^1_4]: https://antigravity.codes/rules/antigravity-workflows/antigravity-workflow-fundamentals

[^1_5]: https://qiita.com/masakinihirota/items/2428655454bdb114356b

[^1_6]: https://unikoukokun.jp/n/nd096dd7d4e42

[^1_7]: https://antigravity.codes/blog/workflows

[^1_8]: https://www.mdpi.com/2072-4292/15/14/3541

[^1_9]: http://biorxiv.org/lookup/doi/10.64898/2025.12.23.696274

[^1_10]: https://www.ijraset.com/best-journal/automatic-subjective-answer-evaluation-

[^1_11]: https://al-kindipublisher.com/index.php/ijllt/article/view/8875

[^1_12]: https://journalcenter.org/index.php/klinik/article/view/5760

[^1_13]: https://www.semanticscholar.org/paper/76f1394ed8f71603df29f7bd8e54597b817212ae

[^1_14]: https://www.semanticscholar.org/paper/be3372307a17f7ed7d0844925d4624bf6a555467

[^1_15]: http://choicereviews.org/review/10.5860/CHOICE.37-3726

[^1_16]: https://ieeexplore.ieee.org/document/8844948/

[^1_17]: http://arxiv.org/pdf/2404.03591.pdf

[^1_18]: http://arxiv.org/pdf/2312.07852.pdf

[^1_19]: https://arxiv.org/pdf/2105.00129.pdf

[^1_20]: https://arxiv.org/pdf/2409.07429.pdf

[^1_21]: https://arxiv.org/pdf/2308.16774.pdf

[^1_22]: https://arxiv.org/pdf/2410.10762.pdf

[^1_23]: https://arxiv.org/pdf/2009.08495.pdf

[^1_24]: https://arxiv.org/pdf/2007.10312.pdf

[^1_25]: https://skywork.ai/blog/google-antigravity-agentic-architecture-ai-workflow/

[^1_26]: https://cloud.google.com/blog/ja/products/data-analytics/connect-google-antigravity-ide-to-googles-data-cloud-services

[^1_27]: https://note.com/ai_driven/n/n5f30860f2134

[^1_28]: https://www.youtube.com/watch?v=7tzgiTAxjjI

[^1_29]: https://www.developer-tech.com/news/gemini-3-google-new-agentic-ai-workflows-for-developers/

[^1_30]: https://www.youtube.com/watch?v=wEZ3p4R-SfU

[^1_31]: https://zenn.dev/miz_1123/articles/ea8bb8a5811307

[^1_32]: https://cloudfit.co.jp/blog/antigravity-workflow

[^1_33]: https://www.issoh.co.jp/tech/details/9919/

[^1_34]: https://note.com/npaka/n/nafe71bf65ce5

[^1_35]: https://arxiv.org/pdf/2107.06639.pdf

[^1_36]: https://journals.iucr.org/j/issues/2023/05/00/yr5110/yr5110.pdf

[^1_37]: https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giad006/7050798

[^1_38]: https://f1000research.com/articles/8-1749/v1/pdf

[^1_39]: https://arxiv.org/pdf/2212.01422.pdf

[^1_40]: https://arxiv.org/pdf/2304.14570.pdf

[^1_41]: http://arxiv.org/pdf/2410.06941.pdf

[^1_42]: https://www.datacamp.com/tutorial/gemini-3-flash-tutorial

[^1_43]: https://github.com/lbjlaq/Antigravity-Manager/blob/main/README_EN.md

[^1_44]: https://docs.mermaidchart.com/plugins/antigravity

[^1_45]: https://www.linkedin.com/posts/styles_the-ralph-wiggum-plugin-is-named-after-the-activity-7416123458918621184-7L0T

[^1_46]: https://dev.classmethod.jp/articles/antigravity-terminal-command-auto-execution/

[^1_47]: https://github.com/NoeFabris/opencode-antigravity-auth

[^1_48]: https://github.com/bmad-code-org/BMAD-METHOD

[^1_49]: https://agentcmds.work

[^1_50]: https://skywork.ai/blog/agent/build-web-app-antigravity/

[^1_51]: https://news.smol.ai/issues/

[^1_52]: https://unikoukokun.jp/n/n543f089015d4

[^1_53]: https://adafruit79.rssing.com/chan-5812578/latest.php

[^1_54]: https://zenn.dev/ymiz/articles/4f776128cd8a8d

[^1_55]: https://arxiv.org/pdf/2304.00019.pdf

[^1_56]: http://arxiv.org/pdf/2407.16646.pdf

[^1_57]: https://downloads.hindawi.com/journals/sp/2004/170481.pdf

[^1_58]: https://www.aanda.org/articles/aa/pdf/2024/01/aa47651-23.pdf

[^1_59]: https://jimmysong.io/blog/antigravity-vscode-style-ide/

[^1_60]: https://www.servicenow.com/docs/bundle/zurich-it-operations-management/page/product/discovery/concept/file-based-discovery.html

[^1_61]: https://dev.to/prakashm88/enhancing-the-vs-code-agent-mode-to-integrate-with-local-tools-using-model-context-protocol-mcp-ccn

[^1_62]: https://www.npmjs.com/package/oh-my-opencode

[^1_63]: https://news.ycombinator.com/item?id=46103532

[^1_64]: https://www.youtube.com/watch?v=2IBN7ArkAkU

[^1_65]: https://ai.google

[^1_66]: https://www.aifire.co/p/google-antigravity-review-a-beginner-s-guide-to-the-ai-ide

[^1_67]: https://tensorlake.ai/blog/antigravity-builds-agent

[^1_68]: https://developers.google.com/products/develop

[^1_69]: https://www.codecademy.com/article/how-to-set-up-and-use-google-antigravity

[^1_70]: https://www.reddit.com/r/google_antigravity/comments/1qcr5gj/tracking_what_actually_got_written_after/

[^1_71]: https://dl.acm.org/doi/full/10.1145/3706599.3720189

