# dev-rules リポジトリ参照インデックス

> **ソース**: `G:\その他のパソコン\太郎\dev\dev-rules\`
> **目的**: 旧 dev-rules リポジトリへの参照
> **注意**: Hegemonikon とは設計思想が異なるため、参照のみ

---

## ディレクトリ構成

```
dev-rules/
├── constitution/      # 開発憲章（14ファイル）
│   ├── 00_orchestration.md
│   ├── 01_environment.md
│   ├── 02_logic.md
│   ├── 03_security.md
│   ├── 04_lifecycle.md
│   ├── 05_meta_cognition.md
│   ├── 06_style.md
│   ├── 07_testing.md
│   ├── 08_git.md
│   └── 09_structure.md
├── prompts/           # プロンプトテンプレート
│   ├── modules/
│   ├── protocols/
│   └── system/
├── GEMINI.md          # 旧カーネル設定
└── README.md
```

---

## Hegemonikon との対応

| dev-rules | Hegemonikon 対応 |
|:---|:---|
| constitution/00_orchestration | → kernel/doctrine.md（進化版） |
| constitution/05_meta_cognition | → M-Series Skill（実装済み） |
| constitution/07_testing | → M7 Dokimē |
| GEMINI.md | → kernel/doctrine.md（統合済み） |

---

## 参照方法

```powershell
# dev-rules の constitution を参照
view_file "G:\その他のパソコン\太郎\dev\dev-rules\constitution\07_testing.md"

# prompts を参照
view_file "G:\その他のパソコン\太郎\dev\dev-rules\prompts\_index.md"
```

---

## 注意

- **太郎 rules.md**: Flow AI 固有の設定。Hegemonikon とは関係なし
- **GitHub laihuip001/dev-rules**: このリポジトリのミラー
