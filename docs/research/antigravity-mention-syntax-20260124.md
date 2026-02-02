# Antigravity IDE メンション機能（@ syntax）調査結果

> **Source**: Perplexity 調査 2026-01-24
> **品質**: 公式ドキュメント + 実務検証記事 + 設計パターン推論
> **用途**: Prompt-Lang v2 設計への入力

---

## Executive Summary

1. Antigravity の `@` メンションは「**ローカル/MCP リソースをチャットのコンテキストに明示的にアタッチする仕組み**」
2. サポートリソース: ファイル、ディレクトリ、MCP サーバ、ワークフロー、会話履歴/Knowledge
3. 会話サマリ（直近20件）は新規チャット開始時に自動ヘッダ注入される
4. レート制限は「トークン数」ではなく「エージェントのワーク量」ベース

---

## 1. 製品定義

### 1.1 Antigravity の位置づけ

| 製品 | 説明 |
|------|------|
| **Google Antigravity** | Agent-first IDE。VS Code ベースの独立デスクトップアプリ |
| **Gemini Code Assist** | GCP/Vertex AI/VS Code 向けコーディング支援ブランド（別ライン） |
| **Project IDX** | 2023-2024年のブラウザIDEプロジェクト（後継として Antigravity 登場） |

### 1.2 提供形態

- **Antigravity デスクトップ IDE**: VS Code ベース + Agent Manager + MCP 統合
- **Gemini Code Assist VS Code 拡張**: 既存 VS Code への追加（Agent Manager なし）
- **Google Cloud / Vertex AI 側**: ブラウザ IDE / Cloud Shell Editor（別プロダクト）

---

## 2. @ メンション機能一覧

### 2.1 サポートリソース

| リソース種別 | 構文例 | サポート状況 | 挙動 |
|-------------|--------|-------------|------|
| **ファイル** | `@path/to/file.py` | ✅ 確定 | read_file で読み込み、関連部分のみ注入 |
| **ディレクトリ** | `@src/` | ✅ 確定 | ファイルリスト列挙 → 必要なファイルのみ read |
| **MCP サーバ** | `@mcp:server_name:` | ✅ 確定 | MCP ツールを会話で使用可能に |
| **ワークフロー** | `/workflow-name` | ✅ 確定 | 保存済みプロンプトテンプレート呼び出し |
| **会話履歴** | `@Conversation Title` | 🔶 高確度 | 会話サマリ（KI）を高優先度で注入 |
| **シンボル** | `@ClassName.method` | ⚪ 未公開 | LSP 経由で定義位置特定の可能性 |
| **URL** | `@https://...` | ❌ 未サポート | ブラウザツール経由で処理 |
| **Artifacts** | （明示構文なし） | 🔶 間接 | 開いた Artifact が次の入力に含まれる |
| **Knowledge Items** | （会話 @ で参照） | ✅ 確定 | 自動抽出・保存・再利用 |

### 2.2 他ツールとの比較

| ツール | メンション対象 | 典型構文 | 特徴 |
|--------|---------------|---------|------|
| **Antigravity** | ファイル/Dir/MCP/会話/KI | `@file`, `@mcp:*` | エージェント + MCP 統合が強い |
| **Cursor** | Files/Folders/Symbols/Docs | `@filename`, `@folder/` | `.cursorrules` による制御 |
| **Copilot** | @workspace/#file/#sym | `@workspace`, `#file` | GitHub エコシステム密結合 |
| **Claude Code** | ファイル/Dir/MCP | `@file.ts`, `@/path` | `CLAUDE.md` による憲法 |

---

## 3. コンテキスト注入の詳細

### 3.1 アーキテクチャ

```
ユーザー入力（+ @ リソース）
    ↓
ツール呼び出し計画（read_file, list_dir, MCP, browser）
    ↓
実行結果を内部メモリに蓄積
    ↓
会話履歴一部 + ファイル抜粋 + Knowledge要約 + Artifacts要約
    ↓
モデルに投入
    ↓
追加ツール呼び出し or 応答
```

### 3.2 優先度（推測）

1. **固定**: システムプロンプト、安全性ガードレール
2. **高優先**: Rules/Workflows、Knowledge Items、Artifacts
3. **中優先**: 直近チャット履歴、@ 指定ファイル抜粋
4. **低優先**: 古い履歴（自動要約→圧縮）

### 3.3 トランケーション

- 巨大ファイル: 関数シグネチャ・コメントのみ抽出
- 長時間会話: 古い履歴を自動要約・圧縮
- Claude Code / Copilot と同様のパターン

---

## 4. 会話履歴と Knowledge の自動注入

### 4.1 観測された挙動

- 新規会話開始時、**直近 ~20 件の会話サマリ（3-4行）+ 会話 ID** がヘッダに自動付与
- `.gemini/antigravity/brain` ディレクトリから読み出し
- ワークスペースを跨いだ「文脈のにじみ」が発生

### 4.2 Knowledge Items (KI)

- 会話やコードから自動抽出
- 長期的な知識として保存・再利用
- 公式ドキュメントで説明されている機能

### 4.3 過去会話の @ 参照

- UI 上で過去会話タイトルの左に `@` が付いて候補として出現
- 選択すると、その会話の KI 要約が現在のチャットに高優先度で追加

---

## 5. 制限事項と回避策

### 5.1 レートリミット

| プラン | クォータ | リセット |
|--------|---------|---------|
| 無料 | 大きめ上限 | 週次 |
| Pro/Ultra | 高い上限 | 5時間ごと |

- **消費ベース**: トークン数ではなく「エージェントのワーク量」
- **回避**: @dir 乱用を避け、対象ディレクトリを小さく区切る

### 5.2 ファイル制限

- バイナリ: MCP/ブラウザ経由で処理（@ では不可）
- 巨大ログ: 関連セクション抜き出しでファイル作成

### 5.3 セキュリティ

- `.env` / secrets へのアクセスは可能だが要ポリシー設定
- ダミー値を渡す / MCP root 設定で除外

### 5.4 会話履歴リーク

- 別ワークスペースの会話が新規チャットに混入する可能性
- **回避**: History から削除、brain ディレクトリクリア

---

## 6. ベストプラクティス

### 6.1 過去会話の続行

1. 重要な会話に固有タイトルを付ける
2. 新しい会話で `@<会話タイトル>` を明示参照
3. 重要決定事項は別途ファイル化 → `@file` 参照

### 6.2 複数ファイルレビュー

1. トピックごとにファイルをグルーピング
2. サブツリー単位で @ 指定
3. 結果を Artifact/Knowledge に残す

### 6.3 ドキュメント参照コーディング

1. ドキュメントをリポジトリに配置 → `@docs/` 参照
2. 大規模ドキュメントは章単位に分割
3. 外部スキーマは MCP 経由で参照

### 6.4 MCP 連携ワークフロー

```
Find bugs in @agent.py @requirements.txt
Categorise them and create summary
Then using @mcp:rube_mcp: send to <email>
```

---

## 7. Hegemonikón / Prompt-Lang v2 への示唆

### 7.1 @mention ディレクティブ設計

```prompt-lang
# @ = リソースID宣言（テキスト展開ではない）
@file("src/api/controller.py", priority = HIGH)
@dir("src/models/", filter = "*.ts", depth = 2)
@conv("<conversation-title>")
@mcp("gnosis").tool("search").with(@file("query.txt"))
```

### 7.2 設計原則

1. **@ = 制約宣言**: どの部分を何トークン注入するかはエージェント戦略に委ねる
2. **リソース種別の型レベル区別**: `@file`, `@dir`, `@conv`, `@ki`, `@artifact`, `@mcp`
3. **優先度ヒント**: `priority = HIGH/MEDIUM/LOW`

### 7.3 実装上の注意

1. 会話履歴の自動注入を「前提にしない」→ 明示的 `@conv` で宣言
2. 大規模リポジトリでは `@dir` にフィルタ/深度制限を付ける
3. MCP と @ の統合を第一級にする

---

## 8. 根拠リンク

### Google 公式

- [Gemini 3 発表 + Antigravity 概要](https://blog.google/products-and-platforms/products/gemini/gemini-3/)
- [Antigravity 公式ブログ](https://antigravity.google/blog/introducing-google-antigravity)
- [Knowledge 機能ドキュメント](https://antigravity.google/docs/knowledge)
- [MCP Integration ドキュメント](https://antigravity.google/docs/mcp)

### レートリミット・料金

- [Datastudios 料金分析](https://www.datastudios.org/post/is-google-antigravity-free-to-use-pricing-limits-and-what-developers-should-expect)
- [Pro/Ultra レートリミット強化](https://blog.google/feed/new-antigravity-rate-limits-pro-ultra-subsribers/)

### Tips・実務記事

- [Mete Atamel: Antigravity Tips & Tricks](https://atamel.dev/posts/2025/12-01_antigravity_editor_tips/)
- [Composio: MCP + Antigravity ガイド](https://composio.dev/blog/howto-mcp-antigravity)

### 会話履歴・Knowledge

- [reddit: 会話サマリ自動注入の解析](https://www.reddit.com/r/google_antigravity/comments/1pc6qa4/ysk_antigravity_will_provide_all_of_your/)
- [AI Forum: 会話削除方法](https://discuss.ai.google.dev/t/how-to-delete-conversation-antigravity/114671)

### 他ツール比較

- [Cursor: @ Mentions ドキュメント](https://cursor.com/ja/docs/context/mentions)
- [Copilot: Chat cheat sheet](https://code.visualstudio.com/docs/copilot/reference/workspace-context)
- [Claude Code: JetBrains 統合](https://code.claude.com/docs/en/jetbrains)

---

*生成日: 2026-01-24 | Hegemonikón M5 Peira + Perplexity*
