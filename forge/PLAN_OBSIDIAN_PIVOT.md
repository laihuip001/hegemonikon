# Forge 設計再調整計画 & タスク (2026-01-15)

このドキュメントは、Forgeプロジェクトを本来の「Obsidian + GitHub」中心の設計に回帰させるための計画書です。
Web UIの廃止と、CLIツールの強化・整理を含みます。

---

## 📅 タスク (Task List)

- [x] 設計思想の再確認
    - [x] Web UIの廃止決定 (Over-engineering / Anti-pattern)
    - [x] Obsidian連携へのピボット方針策定
- [/] 再計画
    - [x] 実装計画の作成（本ドキュメント）
    - [ ] ディレクトリ構成の最終決定
- [ ] 実行 (Execution)
    - [ ] `server/` ディレクトリおよび `start-server.ps1` の削除
    - [ ] `forge.ps1` の動作検証 (Web依存の排除確認)
    - [ ] ルートディレクトリの整理 (.gitignore, README更新)
    - [ ] Obsidianでの動作確認

---

## 📝 実装計画 (Implementation Plan)

### 目標
Forgeを「ObsidianをUI、GitHubをストレージとするプロンプトエンジニアリング基盤」として再定義する。

### 変更内容

#### 1. コンポーネント削除
- **[DELETE] Web Server**: `server/`, `start-server.ps1`
  - 現状のWeb UIはメンテナンスコストが高く、Obsidianの標準機能で代替可能であるため削除します。

#### 2. ディレクトリ構成の整理 (Single Repo)
```
Forge/
├── core/           # 公開・共有用 (Templates, Modules)
├── private/        # 個人用 (Configs, Drafts) - .gitignore推奨
├── archive/        # 自動保存先
└── forge.ps1       # CLIツール
```

#### 3. Obsidian連携
- ユーザーは `Forge/` フォルダをObsidianのVaultとして開く（またはVault内に配置する）ことを想定。
- Markdownリンク、タグ、プロパティがObsidian内で正しく機能するようにファイルを整備する。

### 検証手順
1. `server/` 削除後、`.\forge.ps1` がエラーなく動作すること。
2. Obsidianでプロジェクトフォルダを開き、ファイル間のリンクが機能すること。
