# 調査依頼書（深掘り版）

**テーマ**: Antigravity IDE チャット履歴の自動エクスポート方法

---

## 0. あなた（調査者）への依頼（最重要）

私は Antigravity IDE（Google の VS Code ベースエージェント IDE）のチャット履歴を **md 形式で自動保存** する方法を探している。

現状:
- 会話データは `~/.gemini/antigravity/conversations/*.pb` に Protocol Buffers 形式で保存
- .pb ファイルは**暗号化または圧縮**されており、標準的な protobuf デコードが失敗
- 公式のエクスポート機能は確認されていない

以下について、**2025-2026時点の最新情報**で回答してほしい:

1. **Antigravity IDE のチャット履歴エクスポート機能**は存在するか？（公式/非公式）
2. **Protocol Buffers ファイルのデコード方法**（.proto 定義の入手、リバースエンジニアリング手法）
3. **Google Takeout や Gemini API 経由**でのエクスポートは可能か？
4. **ブラウザ拡張/スクリプトによる DOM 抽出**の先行事例はあるか？
5. **VS Code 拡張 API** を使った会話データへのアクセス方法

完璧を求めている。**「できない」で終わらせず、代替手段と技術的詳細まで徹底的に調査してほしい。**

---

## 1. 調査対象の定義

### 1-1. 製品名・バージョン

- **Antigravity IDE**: Google の Agent-first IDE（VS Code ベース）
- **Gemini Code Assist**: 関連するが別製品。Antigravity との関係を明確にする
- **Project IDX**: クラウドベースの IDE。Antigravity ではない

### 1-2. データ形式

- 保存場所: `~/.gemini/antigravity/conversations/`
- ファイル形式: `.pb` (Protocol Buffers)
- 構造: UUID.pb 形式、サイズは数百KB〜数十MB

---

## 2. 調査すべき論点

### A. 公式エクスポート機能

1. Antigravity IDE に「会話エクスポート」メニューはあるか？
2. 設定画面やコマンドパレットでの隠し機能は？
3. `~/.gemini/antigravity/` 配下の他のファイル（知られていない設定ファイル等）にエクスポート関連の記述はあるか？

### B. Protocol Buffers デコード

1. Antigravity の .pb ファイルに使われている proto 定義は公開されているか？
2. Google の他の製品（Gemini API, Cloud AI）で類似の proto 定義はあるか？
3. バイナリ解析ツール（protoc --decode_raw, protobuf-decoder 等）での部分的デコードは可能か？
4. 暗号化されている場合、その暗号方式と鍵の管理方法は？

### C. 代替エクスポート方法

1. **Google Takeout**: Antigravity の会話データは Takeout 対象か？
2. **Gemini API**: 会話履歴を API 経由で取得できるか？（認証フロー含む）
3. **VS Code 拡張 API**: `vscode.workspace` や独自 API で会話データにアクセスできるか？
4. **ブラウザ抽出**: Agent Manager の DOM 構造から会話を抽出するスクリプトは存在するか？

### D. 先行事例・コミュニティ

1. GitHub, Reddit, Stack Overflow での Antigravity エクスポート関連の議論
2. 非公式ツールや拡張機能の存在
3. Google Cloud / Vertex AI 関連のフォーラムでの情報

---

## 3. 期待する成果物

| アイテム | 内容 |
|---|---|
| **デコード手順** | .pb を md に変換する具体的なコード/コマンド |
| **proto 定義** | 会話データの構造定義（推定含む） |
| **代替手段一覧** | 実現可能性を3段階（✅⚪❌）で評価 |
| **技術的詳細** | API エンドポイント、認証方法、レート制限等 |

---

## 4. 品質基準

- **一次情報必須**: 公式ドキュメント、GitHub リポジトリ、Google 公式ブログへのリンク
- **再現性重視**: 手順を実行すれば私の環境でも動作すること
- **不確実性の明示**: 「おそらく」「可能性がある」は避け、確信度を明示

---

**私の目的**: Antigravity での全チャット履歴を md 形式で保存し、LLM の長期記憶（エピソード記憶）として活用する。完璧を求めている。
