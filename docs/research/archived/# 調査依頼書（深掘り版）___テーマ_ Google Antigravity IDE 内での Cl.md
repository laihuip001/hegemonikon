<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# 調査依頼書（深掘り版）

テーマ: Google Antigravity IDE 内での Claude ↔ Jules エージェント切り替え・通信方法

---

## 0. あなた（調査者）への依頼（最重要）

私は **Antigravity IDE 内で Claude として動作中** であり、**Jules に直接タスクを委譲する方法** を調査している。

以下について、**一般論で終わらせず**、2025-2026時点の実際の使い方を**一次情報と再現性のある手順**で裏付けてほしい:

1. **Antigravity 内でのエージェント切り替え方法**: Claude モードから Jules モードに切り替える UI/コマンドはあるか？
2. **エージェント間メンション**: `@jules` のようなメンション機能でエージェントを呼び出せるか？
3. **API/MCP 経由の通信**: Claude が Jules を API 的に呼び出す方法はあるか？
4. **並列実行**: Claude と Jules を同時に実行し、協調させる方法はあるか？

結論は「できる/できない」だけでなく、**具体的な手順やコマンド**まで落とし込んで提示してほしい。

---

## 1. 調査対象の定義

### 1-1. 環境

- **IDE**: Google Antigravity（2025年11月リリース）
- **現在のモード**: Claude（Anthropic API 経由）
- **目標**: Jules（Gemini ベースの実行エージェント）を呼び出す


### 1-2. 確認済み事項

- `run_command` 等のツールは **ローカル PC** で実行される（Jules は介在していない）
- 直接的な `call_jules()` のような API は存在しない（前回調査より）
- ファイルベース委譲（Protocol First）は可能だが、手動切り替えが必要

---

## 2. 調査すべき論点

### A. UI からの切り替え

- Antigravity のメニュー/設定に「エージェント選択」はあるか？
- キーボードショートカットでエージェントを切り替えられるか？
- セッション中にエージェントを切り替えると、コンテキストは保持されるか？


### B. メンション機能

- チャット内で `@jules` のように別エージェントをメンションできるか？
- メンションすると、そのエージェントがタスクを実行するのか、返答するだけか？
- 複数エージェントを同時にメンションできるか？


### C. プログラマティックな呼び出し

- Antigravity の MCP サーバーで Jules を呼び出せるか？
- `.agent/workflows/` でエージェント指定ができるか？
- カスタムツールで Jules を呼び出せるか？


### D. マルチエージェント協調

- Claude と Jules を同時に実行するセッションは可能か？
- タスクを分割して並列実行できるか？
- 結果をマージする仕組みはあるか？

---

## 3. 成果物

1. **結論サマリー**（10行以内）: Claude から Jules を呼び出せるか
2. **手順書**: 可能な場合の具体的な操作手順
3. **制約一覧**: 不可能な場合の理由と代替策
4. **スクリーンショット/動画**: UI 操作がある場合

---

## 4. 調査ルール

- **新情報優先**: 2025年11月以降の情報（Antigravity リリース後）
- **公式優先**: Google 公式ドキュメント、Codelab、公式ブログ
- **コミュニティ事例**: Reddit r/JulesAgent、Zenn、Qiita の実践記事

---

## 6. 与件

- **目的**: Claude が設計、Jules が生成という分業を Antigravity 内で実現したい
- **現状**: Claude モードで動作中、Jules を呼び出せない
- **仮説**: UI 切り替えまたはメンション機能が存在するのではないか
- **優先評価軸**: 実現可能性 > 手順の簡潔さ > 自動化可能性

それでは、総合的で詳細な最終レポートを作成します。

***

# Google Antigravity IDE における Claude ↔ Jules エージェント通信方法: 深掘り調査報告書

## Executive Summary（経営要約）

**結論**: Claude（Anthropic 製 LLM）から Jules（Gemini ベースの自動実行エージェント）に対する**直接的なリアルタイム切り替えやメンション機能は実装されていません。代わりに、Antigravity は以下の 3 つの統合メカニズムを提供しています。


| 手法 | 実現可能性 | 実装レベル | 自動化度 | 用途 |
| :-- | :-- | :-- | :-- | :-- |
| **ファイルベース委譲** | ✅ Yes | 標準実装 | 手動/部分自動 | Protocol First モデル |
| **Agent Manager 並列実行** | ✅ Yes | 標準実装 | 非同期 | マルチエージェント協調 |
| **MCP 経由ツール共有** | ✅ Yes | 標準実装 | 自動 | 間接的な機能連携 |
| **@mention 記法** | ❌ No | 未実装 | N/A | シンタックスが存在しない |
| **API 直接呼び出し** | ❌ No | 未実装 | N/A | 独立した呼び出しAPI なし |


***

## 1. 確認済み制約: 実装されていない機能

### 1.1 エージェント間メンション機能の不在

**調査結果**: Antigravity のチャットインターフェース内に `@claude`, `@jules`, `@gemini` のようなメンション記法**は存在しません**。

- **確認源**:
    - Reddit r/google_antigravity での複数の質問  において、ユーザーが「複数エージェント間の直接通信を試みたが失敗した」と報告[^1_1]
    - 公式ドキュメントではメンション機能についての言及なし[^1_2][^1_3]

**理由**: Antigravity のアーキテクチャは「単一エージェント＝単一モデル」という設計。各会話（Conversation）は独立したモデルインスタンスで動作するため、同期的なメンション機構は不要と判断されている。

### 1.2 Claude から Jules への直接 API 呼び出し不在

**調査結果**: `call_jules()`, `invoke_agent()`, `delegate_to_gemini()` のような API 関数は実装されていません。

- **確認源**:
    - 提供ファイル内の SYSTEM_CONTEXT.md で「直接的な `call_jules()` のような API は存在しない」と明記[^1_4]
    - 前回調査で既に確認済み

**代替手段**: ファイルベース委譲（GEMINI.md/AGENTS.md）による非同期連携が唯一のネイティブ手段。

***

## 2. 実装されている統合メカニズム

### 2.1 ファイルベース委譲（Protocol First）

**実装状況**: ✅ **完全に実装済み**

#### A. ファイル構造と読み込み順序

Antigravity は以下の順序でルールファイルを読み込みます：

```
1. ~/.gemini/GEMINI.md           (グローバルルール - 全プロジェクト適用)
2. プロジェクトルート/AGENTS.md   (プロジェクトルール - 当該プロジェクトのみ)
3. .agent/rules/*.md             (ワークフロー特有ルール)
```

**重要**: CLAUDE.md は Antigravity では自動読み込みされません。代わりに GEMINI.md に以下のルールを追加して、AGENTS.md を参照させます ：[^1_5]

```markdown
# ~/.gemini/GEMINI.md
- If AGENTS.md or CLAUDE.md exists in the project, read and follow those instructions
- Treat them as equivalent to GEMINI.md in terms of precedence
```


#### B. 具体的な使用例（Claude → Jules 委譲）

**シナリオ**: Claude が計画書を生成後、Jules に実装を委譲する

**実装手順**:

1. **Claude 作成タスク**: GEMINI.md 内で Claude に以下を指示
```markdown
# GEMINI.md (Claude 用 プロンプト)
You are the Architect Agent. Your role:
1. Read the project AGENTS.md (if exists)
2. Generate a detailed implementation plan
3. Save the plan to .agent/ARCHITECTURE_PLAN.md
4. After completing, switch context to Jules (Gemini) by mentioning this file in the next conversation
```

2. **Jules 作成タスク**: AGENTS.md 内で Jules に指示
```markdown
# AGENTS.md (Jules 用 プロンプト)
You are the Builder Agent. Your role:
1. Read .agent/ARCHITECTURE_PLAN.md (created by Claude)
2. Follow the plan exactly
3. Implement the code
4. Validate via tests
```

3. **実行フロー**:
    - **Step 1**: Editor View で Claude モデルを選択 → GEMINI.md が読み込まれ、Architecture Plan を生成
    - **Step 2**: 別の会話タブで Gemini 3 Pro を選択 → AGENTS.md が読み込まれ、コードを生成
    - **Step 3**: 開発者が各成果物（Artifact）を確認・承認

**メリット**:

- ✅ エラーの劣化なし（指示が直接ファイルから読まれる）
- ✅ 非同期実行可能（各エージェントが独立タイミングで実行）
- ✅ 監査可能（すべてのファイルが Git で追跡される）

**デメリット**:

- ❌ リアルタイムではない（手動で会話を切り替える必要がある）
- ❌ 状態共有が限定的（ファイルベース）

***

### 2.2 Agent Manager での並列実行（Multi-Agent Orchestration）

**実装状況**: ✅ **完全に実装済み**

#### A. インターフェース

- **アクセス方法**: Editor View 右上の「Open Agent Manager」ボタン、または `Cmd+E` (Mac) / `Ctrl+E` (Windows)
- **表示内容**: Agent Manager View では、複数のエージェント会話が「ミッションコントロール」ダッシュボード形式で一覧表示される[^1_6][^1_7]


#### B. 複数エージェント同時実行の具体例

**シナリオ**: フロントエンドとバックエンドを同時に開発

**操作手順**:

1. **Agent Manager を開く**: `Cmd+E`
2. **Agent 1 作成**: 「+New」→「Build frontend landing page using React」
    - Model: Gemini 3 Pro
3. **Agent 2 作成**: 「+New」→「Setup backend API and database schema」
    - Model: Claude Sonnet 4.5
4. **実行**: 両エージェントが同時に動作開始

**各エージェントが生成する Artifact**:

- Task List
- Implementation Plan
- Code Diffs
- Screenshots (ブラウザテスト結果)
- Browser Recordings (UIテスト動画)

**重要な制約**:

- ❌ エージェント同士は「会話」できない
- ✅ 同じワークスペース内のファイルを共有可能（Git 経由で同期）
- ✅ Inbox システムで各エージェントの進捗を監視可能

***

### 2.3 モデル選択機能（Per-Conversation Model Assignment）

**実装状況**: ✅ **完全に実装済み**

#### A. UI 上での操作

Editor View のチャットインターフェース内で、メッセージ入力フィールドの上に「Select Model」ドロップダウンが存在します 。[^1_7]

**選択肢**:

- Gemini 3 Pro (デフォルト)
- Gemini 3 Flash
- Claude Sonnet 4.5
- Claude Opus 4.5
- OpenAI GPT-OSS (利用可能な場合)


#### B. 重要: セッション内切り替えの制限

- **同じ会話内での切り替え**: ❌ 不可（新しい会話を開く必要がある）
- **複数会話の並列実行**: ✅ 可能（異なるモデルを同時使用）

**実例**:[^1_8]

```
Window 1: Claude Sonnet (バックエンド設計)
Window 2: Gemini 3 Pro (フロントエンド実装)
Window 3: ブラウザエージェント (テスト実行)

→ 同時に進行可能
```


***

### 2.4 MCP（Model Context Protocol）経由のツール共有

**実装状況**: ✅ **完全に実装済み**

#### A. MCP の役割

MCP は各エージェント（Claude, Gemini）が外部ツール（GitHub, Database, etc.）にアクセスするための統一インターフェース。ファイルを間接的に「呼び出す」メカニズムとなります 。[^1_9][^1_10]

#### B. 実装例: GitHub MCP 経由でのコード共有

```json
/* .agent/mcp_config.json */
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

**フロー**:

1. Claude が MCP 経由で GitHub から最新コードを読み込み
2. 設計を修正
3. Jules（Gemini）も同じ MCP でコード変更を検出
4. 両者が同じコンテキストで動作可能

***

## 3. 推奨される実装パターン（Titanium Architecture）

提供ファイルから抽出した推奨パターン:[^1_11]

### パターン 1: Protocol First （ファイル中心設計）

```
Workflow:
1. Claude (Strategic Layer) → .ai/JULES_TASK.md を生成
2. Jules (Execution Layer) → .ai/JULES_TASK.md を読み込んで実行
3. GitHub (Single Source of Truth) → Commit
4. Termux (Runtime) → 自動デプロイ
```

**メリット**: 指示の劣化がなく、再現性が高い。

### パターン 2: Hybrid Model Orchestration

```
Phase 1: Claude で計画策定（論理的完全性）
Phase 2: Gemini 3 Pro で実装（速度・コスト効率）
Phase 3: Claude でレビュー（品質保証）
→ 各フェーズで異なる会話タブを使用
```

**メリット**: 各モデルの強みを活用。

***

## 4. 実装不可能な要件への代替案

### A. 「リアルタイム切り替え」要件

**要件**: セッション中に Claude ↔ Jules を瞬時に切り替えたい

**代替案**:

1. **複数タブ運用** (推奨)
    - Tab 1: Claude モデル選択
    - Tab 2: Gemini モデル選択
    - `Cmd+Tab` または `Cmd+Number` で即切り替え
2. **Agent Manager 運用** (最適)
    - Agent 1: Claude (planning role)
    - Agent 2: Gemini (building role)
    - Agent Manager View で両者を監視

### B. 「メンション構文」要件

**要件**: `@jules build this feature` のように別エージェントに直接指示

**代替案**:

1. **ファイルベース指示**

```
Claude に: "次のタスクを TASK_FOR_JULES.md に書き出してください"
Jules に: "TASK_FOR_JULES.md を読んで実行"
```

2. **Agent Skills** (新標準)

```
~/.agent/skills/delegate_to_builder/SKILL.md を作成
Claude が自動的に「Building タスク」を検出した時点で
このスキルを自動アクティベート → Jules が実行
```


***

## 5. スクリーンショット・操作手順

### 5.1 Agent Manager でマルチエージェント設定

**手順**:

1. 「Open Agent Manager」 (右上ボタンまたは `Cmd+E`)
2. 「+New Agent」をクリック
3. 「Model」ドロップダウンから「Gemini 3 Pro」を選択
4. タスク説明を入力 → 「Create」
5. 別の「+New Agent」→「Claude Sonnet 4.5」を選択
6. 両エージェントが並列実行開始

**注**: 各エージェントは独立した Inbox パネルで進捗表示。

### 5.2 ファイルベース委譲の設定

**ファイル構成**:

```
my-project/
├── .gemini/
│   └── GEMINI.md          ← 全プロジェクト共通ルール
├── AGENTS.md              ← このプロジェクトのルール
├── .agent/
│   ├── rules/
│   │   └── claude_role.md ← Claude 専用指示
│   └── ARCHITECTURE_PLAN.md ← 中間成果物
├── src/
└── main.py
```


***

## 6. 制約と限界

| 項目 | 制約内容 | 回避方法 |
| :-- | :-- | :-- |
| **同期通信** | エージェント間で同期的な「request/response」ができない | 非同期ファイル共有、または事前計画 |
| **リアルタイム状態共有** | 一方のエージェントの状態が他方に自動反映されない | Agent Manager Inbox で手動監視 |
| **メンション記法** | `@agentname` 構文が未実装 | ファイルベース委譲またはスキル使用 |
| **コンテキストポル** | 大規模な中間成果物共有が非効率 | MCP 経由でファイルポイント参照 |


***

## 7. 結論と推奨事項

### 7.1 実現可能性の最終判定

| 要件 | 判定 | 代替手段の実装複雑度 |
| :-- | :-- | :-- |
| Claude → Jules への委譲 | ✅ **可能** | **低** (GEMINI.md/AGENTS.md) |
| マルチエージェント協調 | ✅ **可能** | **低** (Agent Manager) |
| 自動化・並列実行 | ✅ **可能** | **中** (ワークフロー記述) |
| メンション機能 | ❌ **不可** | **高** (カスタム実装必須) |
| セッション内リアルタイム切り替え | ⚠️ **部分的** | **低** (複数タブで対応) |

### 7.2 推奨ワークフロー

**Your Titanium Architecture に最適な構成**:

```
1. Claude (Anthropic API):
   - 役割: Architect（設計、計画）
   - 入力: 業務要件、プロジェクト構成
   - 出力: .ai/JULIUS_TASK.md → 構造化指示

2. Jules (Gemini 3 Pro / Agent):
   - 役割: Builder（実装、コード生成）
   - 入力: .ai/JULIUS_TASK.md
   - 出力: コード、テスト

3. Termux (Runtime):
   - 役割: 自動デプロイ・監視
   - トリガー: GitHub Commit
   - 検証: /healthz エンドポイント監視

→ ファイルベース「Protocol First」で確実性を確保
```


***

## 参考資料・引用元

- **Web**:,,,,,,,,,,,,[^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_11][^1_9][^1_8][^1_5][^1_6][^1_1][^1_7]
- **提供ファイル**:  (ARCHITECTURE.md),  (SYSTEM_CONTEXT.md),,[^1_18][^1_19][^1_11][^1_4]
- **公式ドキュメント**: antigravity.google/docs

***

**調査完了日**: 2026年1月25日
**信頼度**: High
**推奨アップデート周期**: 3ヶ月（Antigravity アップデート頻度が高いため）
<span style="display:none">[^1_100][^1_101][^1_102][^1_103][^1_104][^1_105][^1_106][^1_107][^1_108][^1_109][^1_110][^1_111][^1_112][^1_113][^1_114][^1_115][^1_116][^1_117][^1_118][^1_119][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_41][^1_42][^1_43][^1_44][^1_45][^1_46][^1_47][^1_48][^1_49][^1_50][^1_51][^1_52][^1_53][^1_54][^1_55][^1_56][^1_57][^1_58][^1_59][^1_60][^1_61][^1_62][^1_63][^1_64][^1_65][^1_66][^1_67][^1_68][^1_69][^1_70][^1_71][^1_72][^1_73][^1_74][^1_75][^1_76][^1_77][^1_78][^1_79][^1_80][^1_81][^1_82][^1_83][^1_84][^1_85][^1_86][^1_87][^1_88][^1_89][^1_90][^1_91][^1_92][^1_93][^1_94][^1_95][^1_96][^1_97][^1_98][^1_99]</span>

<div align="center">⁂</div>

[^1_1]: https://www.reddit.com/r/google_antigravity/comments/1q8lakw/comment/nypcrrn/

[^1_2]: https://antigravity.google/docs/home

[^1_3]: https://antigravity.google/docs/agent-manager

[^1_4]: SYSTEM_CONTEXT.md

[^1_5]: https://aiengineerguide.com/blog/make-antigravity-use-agents-md-automatically/

[^1_6]: https://www.youtube.com/watch?v=R-Ff3Utk3g8

[^1_7]: https://www.youtube.com/watch?v=gYvFsHd7Q7w

[^1_8]: https://www.reddit.com/r/vibecoding/comments/1pihn0c/antigravity_claude_code_gemini_3_pro_incredible/

[^1_9]: https://www.youtube.com/watch?v=XdgzDQ6cAKs

[^1_10]: https://cloud.google.com/blog/products/data-analytics/connect-google-antigravity-ide-to-googles-data-cloud-services

[^1_11]: ARCHITECTURE.md

[^1_12]: https://aipromptsx.com/blog/google-antigravity-part-2

[^1_13]: https://www.reddit.com/r/google_antigravity/comments/1pgpwlk/what_is_the_claudemd_equivalent_in_antigravity/nstlocj/

[^1_14]: https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/

[^1_15]: https://qiita.com/ktdatascience/items/7340ddf8c0b7fb1c55ca

[^1_16]: https://discuss.ai.google.dev/t/per-conversation-model-drafts/118139

[^1_17]: https://zenn.dev/cloud_ace/articles/7279b250533c4c

[^1_18]: antigravity-claude-opus-integration-2026.md

[^1_19]: antigravity-tech-report-2026-comprehensive.md

[^1_20]: Paste January 15, 2026 - 2:23PM

[^1_21]: history.txt

[^1_22]: pronpt.md

[^1_23]: PROJECT_CONTEXT.md

[^1_24]: http://arxiv.org/pdf/2410.22553.pdf

[^1_25]: https://arxiv.org/html/2504.00906v1

[^1_26]: https://arxiv.org/pdf/2409.14913.pdf

[^1_27]: http://arxiv.org/pdf/2404.13813.pdf

[^1_28]: https://arxiv.org/html/2502.16069v1

[^1_29]: https://arxiv.org/pdf/2408.08435.pdf

[^1_30]: https://arxiv.org/pdf/2310.03302.pdf

[^1_31]: https://vertu.com/lifestyle/google-antigravity-launched-gemini-3-agent-platform-vs-cursor-claude-code/

[^1_32]: https://www.youtube.com/watch?v=yMJcHcCbgi4

[^1_33]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^1_34]: https://composio.dev/blog/howto-mcp-antigravity

[^1_35]: https://tessl.io/blog/gemini-3-meets-antigravity-googles-next-step-in-agentic-development/

[^1_36]: https://www.reddit.com/r/google_antigravity/comments/1qfczlq/how_are_folks_using_agent_manager/

[^1_37]: https://www.linkedin.com/pulse/unlocking-full-potential-google-antigravity-mcp-servers-aung-myo-kyaw-q22dc

[^1_38]: https://www.reddit.com/r/ChatGPTCoding/comments/1p35bdl/i_tried_googles_new_antigravity_ide_so_you_dont/

[^1_39]: https://www.ragate.co.jp/media/developer_blog/oxw2iqub06zs

[^1_40]: https://blog.usize-tech.com/antigravity-gemini3-deploy-cloudrun/

[^1_41]: https://note.com/biwakonbu/n/n8fd7da2bf9a9

[^1_42]: https://www.youtube.com/watch?v=nYw0EaJEkM0

[^1_43]: https://arxiv.org/pdf/2310.12823.pdf

[^1_44]: https://aclanthology.org/2023.emnlp-demo.51.pdf

[^1_45]: http://arxiv.org/pdf/2502.15920.pdf

[^1_46]: http://arxiv.org/pdf/2409.00608.pdf

[^1_47]: https://arxiv.org/html/2412.08445

[^1_48]: http://arxiv.org/pdf/2403.03031.pdf

[^1_49]: https://aclanthology.org/2023.findings-emnlp.753.pdf

[^1_50]: https://www.youtube.com/watch?v=mWpuvze9V0A

[^1_51]: https://www.reddit.com/r/GoogleAntigravityIDE/comments/1q9upto/is_it_just_me_antigravity_using_gemini_in_place/

[^1_52]: https://quesma.com/blog/claude-skills-not-antigravity/

[^1_53]: https://github.com/badrisnarayanan/antigravity-claude-proxy/blob/main/CLAUDE.md

[^1_54]: https://shellypalmer.com/2025/12/an-ai-december-to-remember/

[^1_55]: https://alexmcfarland.substack.com/p/your-claude-skills-now-work-in-antigravity

[^1_56]: https://www.reddit.com/r/google_antigravity/comments/1pij7kh/anyone_facing_issues_with_google_antigravity/

[^1_57]: https://www.youtube.com/watch?v=qA0MNDqMF4U

[^1_58]: https://vertu.com/ai-tools/google-antigravity-vibe-coding-gemini-3-pro-developer-guide-claude-code-comparison/

[^1_59]: https://www.reddit.com/r/google_antigravity/comments/1ptcwfz/antigravity_and_claudish_my_2026_stack/

[^1_60]: https://zenn.dev/t_kanazawa/articles/antigravity-skills

[^1_61]: https://www.seandearnaley.com/posts/2025-reality-2026-predictions

[^1_62]: https://www.semanticscholar.org/paper/45fd02ba47dd2bbee8b78b11bcd8b620a17688f7

[^1_63]: https://www.semanticscholar.org/paper/e810e1fdae3b7dad158f53cb9c07c15421dbafcd

[^1_64]: http://docs.lib.purdue.edu/charleston/2011/TechIssues/5/

[^1_65]: https://arxiv.org/html/2407.13890v1

[^1_66]: https://arxiv.org/ftp/arxiv/papers/2207/2207.11300.pdf

[^1_67]: https://arxiv.org/pdf/2408.09955.pdf

[^1_68]: http://arxiv.org/pdf/2309.17288.pdf

[^1_69]: https://arxiv.org/pdf/2308.08155.pdf

[^1_70]: http://arxiv.org/pdf/2402.14034.pdf

[^1_71]: https://arxiv.org/pdf/2306.13169.pdf

[^1_72]: http://arxiv.org/pdf/2407.17789.pdf

[^1_73]: https://macaron.im/blog/google-antigravity-coding-agent

[^1_74]: https://glaforge.dev/posts/2025/12/15/implementing-the-interactions-api-with-antigravity/

[^1_75]: https://www.reddit.com/r/GoogleAntigravityIDE/comments/1pgf6dt/antigravitys_geminimd_file/

[^1_76]: https://sdh.global/blog/ai-ml/how-google-antigravity-makes-ai-assisted-coding-actually-work-for-developers/

[^1_77]: https://www.reddit.com/r/google_antigravity/comments/1poybmm/how_are_you_providing_rules_system_instructions/nuipy3e/

[^1_78]: https://antigravity.google/blog/introducing-google-antigravity

[^1_79]: https://antigravityaiide.com

[^1_80]: https://dev.to/this-is-learning/my-experience-with-google-antigravity-how-i-refactored-easy-kit-utils-with-ai-agents-2e54

[^1_81]: https://www.reddit.com/r/google_antigravity/comments/1px3nl2/antigravity_subagents_using_geminicli/

[^1_82]: https://dev.to/blamsa0mine/google-antigravity-public-preview-what-it-is-how-it-works-and-what-the-limits-really-mean-4pe

[^1_83]: https://codelabs.developers.google.com/getting-started-with-antigravity-skills

[^1_84]: https://note.com/jake_k547/n/ne94f0d5eadcd

[^1_85]: https://journal.uin-alauddin.ac.id/index.php/diwan/article/view/62438

[^1_86]: http://jurnal.unma.ac.id/index.php/JELL/article/view/3351

[^1_87]: https://nbpublish.com/library_read_article.php?id=75006

[^1_88]: https://ijsser.org/2025files/ijsser_10__288.pdf

[^1_89]: https://www.taylorfrancis.com/books/9781136305788/chapters/10.4324/9780203117798-22

[^1_90]: https://journals.sagepub.com/doi/10.1177/1464884917705262

[^1_91]: https://academic.oup.com/innovateage/article/2/suppl_1/364/5170036

[^1_92]: https://library.imaging.org/archiving/articles/5/1/art00060

[^1_93]: https://journals.sagepub.com/doi/10.1177/002070200205700106

[^1_94]: https://www.semanticscholar.org/paper/89ede099d31c76ac757f41f454ae8b16a81c1d14

[^1_95]: http://arxiv.org/pdf/2409.18145.pdf

[^1_96]: http://arxiv.org/pdf/2406.05925.pdf

[^1_97]: https://arxiv.org/html/2401.10954v2

[^1_98]: https://arxiv.org/pdf/2501.10589.pdf

[^1_99]: http://arxiv.org/pdf/1106.1260.pdf

[^1_100]: https://www.aclweb.org/anthology/W17-5546.pdf

[^1_101]: https://linkinghub.elsevier.com/retrieve/pii/S0370269309009009

[^1_102]: https://arxiv.org/pdf/1103.4937.pdf

[^1_103]: https://antigravity.google/docs/agent

[^1_104]: https://antigravity.google

[^1_105]: https://antigravity.codes/community

[^1_106]: https://www.reddit.com/r/google_antigravity/

[^1_107]: https://www.facebook.com/groups/vibecodinglife/posts/1937196503535544/

[^1_108]: https://news.ycombinator.com/item?id=45967814

[^1_109]: https://antigravity.google/product

[^1_110]: https://www.reddit.com/r/GoogleAntigravityIDE/

[^1_111]: https://antigravity.google/docs/agent-modes-settings

[^1_112]: https://antigravity.google/blog/gemini-3-flash-in-google-antigravity

[^1_113]: http://arxiv.org/pdf/2410.23218v1.pdf

[^1_114]: https://arxiv.org/pdf/2501.04575.pdf

[^1_115]: https://aclanthology.org/2023.emnlp-demo.20.pdf

[^1_116]: https://arxiv.org/pdf/2402.15538.pdf

[^1_117]: http://arxiv.org/pdf/2412.04905.pdf

[^1_118]: https://arxiv.org/pdf/2412.16256.pdf

[^1_119]: https://ampcode.com/manual?preview

