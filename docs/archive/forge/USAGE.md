# Forge CLI 使用ガイド

## クイックスタート

PowerShellからForge CLIを実行します：

```powershell
cd c:\Users\user\.gemini\Forge
.\forge.ps1 help
```

## コマンド一覧

### 1. モジュール一覧表示

```powershell
# 全モジュール一覧
.\forge.ps1 list

# カテゴリ別一覧
.\forge.ps1 list protocols
.\forge.ps1 list focus
.\forge.ps1 list knowledge
```

### 2. モジュール読み込み

```powershell
# モジュール名の一部で検索・表示
.\forge.ps1 load "決断"
.\forge.ps1 load "Module 04"
.\forge.ps1 load "TDD"
```

### 3. キーワード検索

```powershell
# ファイル名と内容を検索
.\forge.ps1 search "推論"
.\forge.ps1 search "セキュリティ"
.\forge.ps1 search "RAG"
```

### 4. ディレクトリ構造

```powershell
.\forge.ps1 tree
```

## カテゴリ一覧

| カテゴリ | 説明 |
|----------|------|
| `find` | 🔎 見つける - 情報収集・探索 |
| `expand` | 🧠📊 考える/広げる - 発散思考 |
| `focus` | 🧠🎯 考える/絞る - 収束思考 |
| `prepare` | ⚡🔧 働きかける/固める - 準備 |
| `create` | ⚡✨ 働きかける/生み出す - 創造 |
| `reflect` | 🔄 振り返る - 評価・改善 |
| `protocols` | 🛡️ プロトコル - 品質管理 |
| `knowledge` | 📚 知識ベース - 参考資料 |
| `helpers` | 🔧 ヘルパー - 補助ツール |

## 実行例

```
PS> .\forge.ps1 tree

🔥 Forge - ディレクトリ構造

Forge/
├── 📄 README.md
├── 📄 The Cognitive Hypervisor Architecture.md
│
├── modules/
│   ├── find/                  (5 files)
│   ├── think/
│   │   ├── expand/            (9 files)
│   │   └── focus/             (11 files)
│   ├── act/
│   │   ├── prepare/           (5 files)
│   │   └── create/            (7 files)
│   └── reflect/               (5 files)
│
├── protocols/                 (25 files)
├── knowledge/                 (22 files)
└── helpers/                   (31 files)
```
