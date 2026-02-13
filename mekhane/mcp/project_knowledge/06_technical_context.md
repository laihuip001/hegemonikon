# Technical Context — プロジェクト構成

## ディレクトリ構造

```
~/oikos/hegemonikon/          # プロジェクトルート
├── kernel/                   # 不変の公理体系 (SACRED_TRUTH)
│   ├── axiom_hierarchy.md    # 公理階層定義
│   ├── ousia.md              # O-series 定理
│   ├── schema.md             # S-series 定理
│   ├── horme.md              # H-series 定理
│   └── SACRED_TRUTH.md       # 変更禁止の核心
├── hermeneus/                # CCL パーサー + ワークフロー実行エンジン
│   └── src/
│       ├── dispatch.py       # CCL 構文解析
│       ├── executor.py       # WorkflowExecutor
│       ├── macro_executor.py # マクロ展開・実行
│       └── runtime.py        # CCL ランタイム
├── mekhane/                  # 実装モジュール群
│   ├── mcp/                  # MCP サーバー群
│   │   ├── hgk_gateway.py    # 出張 Gateway (10ツール)
│   │   └── project_knowledge/# ← このディレクトリ
│   ├── pks/                  # 知識基盤
│   │   └── semantic_scholar.py
│   ├── anamnesis/            # Gnōsis 知識検索
│   ├── ergasterion/          # 工房 (Digestor等)
│   └── peira/                # ヘルスチェック
├── .agent/                   # エージェント設定
│   ├── rules/                # BC, Safety Invariants
│   ├── workflows/            # WF 定義 (.md)
│   └── skills/               # Skill 定義
└── designs/                  # 設計ドキュメント
```

## 主要コンポーネント

| コンポーネント | パス | 役割 |
|:-------------|:-----|:-----|
| Hermēneus | hermeneus/ | CCL 解析・実行エンジン |
| Gateway | mekhane/mcp/hgk_gateway.py | MCP リモートサーバー |
| Gnōsis | mekhane/anamnesis/ | 学術知識ベース |
| Digestor | mekhane/ergasterion/digestor/ | 論文消化パイプライン |
| Peira | mekhane/peira/ | ヘルスチェック |
| Dendron | mekhane/ergasterion/dendron/ | コード品質チェック |

## MCP 接続

| サーバー | 用途 |
|:---------|:-----|
| gnosis | 学術論文検索 |
| hermeneus | CCL パース・実行 |
| digestor | 消化パイプライン |
| semantic-scholar | Semantic Scholar API |
| memory | Knowledge Graph |
| mneme | 統合検索 |
| exa | Web 検索 |
| jules | Google コーディング AI |

## Git

- **リポジトリ**: `laihuip001/hegemonikon` (GitHub)
- **ブランチ**: `main`
- **Handoff 保存先**: `~/oikos/mneme/.hegemonikon/sessions/`
