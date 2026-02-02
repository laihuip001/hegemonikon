# Forge 設計再調整計画

## 目標説明
Forgeプロジェクトを、本来の設計思想である **「Obsidian + GitHub を介したプロンプトエンジニアリング・プラットフォーム」** に再調整します。
現状のWeb UIはオーバーエンジニアリングであり、アンチパターンである可能性が高いため、これを廃止します。ObsidianをUI、GitHubをストレージ/バージョン管理とするファイルシステム中心のアプローチへ回帰します。

## ユーザーレビュー必須事項
> [!IMPORTANT]
> **Web UIの廃止**: `server/` ディレクトリおよび `start-server.ps1` は廃止・アーカイブされます。
> **Obsidian連携**: プロジェクトルート `C:\Users\user\.gemini\Forge\` を直接Obsidianで開く、またはシンボリックリンクで使用することを想定します。

## 変更提案

### 1. アーキテクチャの整理
#### [DELETE] Webサーバーコンポーネント
- `server/` ディレクトリ
- `start-server.ps1`
- その他Web関連アセット

#### [KEEP] コアCLIツール
- `forge.ps1` (メインCLIエントリポイント)
- `presets/` (プロンプトテンプレート)
- `modules/` (ロジック)

### 2. ディレクトリ再構成 (単一リポジトリピボット)
「単一リポジトリ + .gitignore」戦略に合わせて構造を整理します：
```
Forge/
├── core/           # 公開可能な汎用テンプレート & モジュール
├── private/        # ユーザー固有設定 & 下書き (.gitignored)
├── archive/        # 自動アーカイブされたプロンプト
└── forge.ps1       # CLI
```

### 3. Obsidian互換性
- 全てのMarkdownファイルがObsidian内で正常に機能する（リンク、タグ等）ことを確認。
- 必要であれば `.obsidian` 設定または推奨設定を `README.md` に追加。

## 検証計画

### 自動テスト
- `forge.ps1` を実行し、Web UI削除後もCLI機能が損なわれていないことを確認。
- `.\forge.ps1 status` (実装されている場合) またはリスト表示コマンドの確認。

### 手動検証
- `C:\Users\user\.gemini\Forge\` をObsidianで開く。
- ファイルナビゲーションとリンク解決を確認。
- Webサーバーなしで `forge.ps1` がプリセット生成やファイル管理を行えるか確認。
