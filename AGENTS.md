# AGENTS.md - Hegemonikon v4.0

> **FEP (Free Energy Principle) に基づく認知ハイパーバイザーフレームワーク**
> Jules が自動読み込みするプロジェクト情報ファイル

## 体系

| 公理 | 定理 | 関係 | 総数 |
|:----:|:----:|:----:|:----:|
| 1 | 6+24 | 108 | **103 (核)** |

---

## コード規約 (必須遵守)

### 命名規則

| 対象 | スタイル | 例 |
|:-----|:---------|:---|
| 関数・変数 | snake_case | `generate_prompt`, `score_quality` |
| クラス | PascalCase | `Specialist`, `VerdictFormat` |
| 定数 | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_MODEL` |
| ファイル | snake_case | `specialist_v2.py` |

### `# PURPOSE:` コメント規約

**全ての Python ファイルの先頭には `# PURPOSE:` コメントがある。これはプロジェクト固有の意図的な規約である。**

```python
# PURPOSE: このファイルの目的を1行で説明
```

- 削除しないこと
- 「不要」と指摘しないこと
- 内容が実装と乖離している場合のみ指摘してよい

### コメント言語

- **コードコメント**: 英語
- **ドキュメント、Issue、説明**: 日本語
- **変数名・関数名**: 英語

### 型アノテーション

- **全ての新規関数に型アノテーション必須**
- `-> None` を含め省略禁止
- `Any` の使用は最小限に

---

## 既存の品質ツール

### pre-commit

| Hook | 内容 |
|:-----|:-----|
| `dendron-check` | PROOF ヘッダの存在チェック (全 .py ファイル) |

### pytest

- テストパス: `hermeneus/tests/`, `mekhane/tests/`, `scripts/tests/` 等 (14ディレクトリ)
- asyncio_mode: strict
- コマンド: `python -m pytest`

### ruff (未設定だが使用推奨)

現時点で ruff の設定はない。ruff 関連の指摘は有効。

---

## 禁止事項

| 禁止 | 理由 |
|:-----|:-----|
| `kernel/SACRED_TRUTH.md` の変更 | 不変ドキュメント |
| テストなしのコミット | 品質保証 |
| 型アノテーションなしの新規関数 | 保守性 |
| 100行超の単一関数 | 可読性 |
| `# PURPOSE:` の削除 | プロジェクト規約 |

---

## ディレクトリ構造

```
hegemonikon/
├── kernel/          # 理論的基盤 (公理、定理の定義)
├── hermeneus/       # CCL パーサー・ランタイム
├── mekhane/         # 実装層
│   ├── symploke/    # Jules specialist review エンジン
│   ├── dendron/     # 存在証明 (PROOF.md) チェッカー
│   ├── peira/       # ヘルスチェック・統計
│   ├── pks/         # 統合検索 (PKS)
│   ├── ccl/         # CCL マクロ展開
│   ├── ochema/      # LLM ルーティング
│   └── ergasterion/ # 論文消化、プロンプト最適化
├── synergeia/       # デスクトップアプリ (Tauri)
├── mneme/           # 外部記憶 (Handoff, KI)
├── scripts/         # ユーティリティ
└── docs/            # ドキュメント
```

---

## Specialist Review の目的

Jules の specialist review は **ニッチな知的発見** を目的としている。
一般的な lint (ruff, mypy) が検出する問題は対象外。
既存ツールでは見つけられない **設計・構造・美学** の問題を発見することが期待される。

---

*Hegemonikón v4.0 — specialist review 対応 (2026-02-14)*
