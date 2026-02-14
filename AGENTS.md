# AGENTS.md - Hegemonikon v5.0

> **FEP (Free Energy Principle) に基づく認知ハイパーバイザーフレームワーク**
> Jules が自動読み込みするプロジェクト情報ファイル

## 認知フレームワーク概要

Hegemonikón は**唯一の公理 (FEP: 予測誤差最小化)** から全体系を導出する:

```
1 公理 (FEP) → 6 座標 → 24 定理 (6 Series × 4) → 108 関係
```

| Series | 名称 | 役割 | 例 |
|:-------|:-----|:-----|:---|
| **O** | Ousia (本質) | 認識・意志・探求・行為 | `/noe` = 深い認識 |
| **S** | Schema (様態) | 解釈・方法・計画・実践 | `/mek` = 方法配置 |
| **H** | Hormē (傾向) | 直感・確信・欲求・信念 | `/pis` = 確信度評価 |
| **P** | Perigraphē (条件) | 文脈・資源・制約・時間 | 環境条件の配置 |
| **K** | Kairos (文脈) | 機会・知恵・統合・精度 | `/sop` = 知恵の調査 |
| **A** | Akribeia (精密) | 厳密性・判定・知識・検証 | `/dia` = 判定力 |

---

## 設計5原則

| # | 原則 | 意味 | コード上の判定基準 |
|:--|:-----|:-----|:-----------------|
| 1 | **Reduced Complexity** | 10倍→1/10に圧縮 | 不要な抽象化がない |
| 2 | **Intuitive Logic** | 説明不要の構造 | 関数名だけで動作が分かる |
| 3 | **Obsessive Detail** | 細部に神が宿る | エッジケースが処理されている |
| 4 | **Form Follows Function** | 機能→美 | 装飾的なコードがない |
| 5 | **Consistency Over Cleverness** | パターン優先 | 既存パターンに従っている |

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

## モジュール依存フロー

```
kernel/ (理論) → hermeneus/ (CCL) → mekhane/ (実装)
                                      ├── symploke/ ← specialist review
                                      ├── dendron/  ← 品質チェック
                                      ├── peira/    ← 健全性監視
                                      ├── ochema/   ← LLM ルーティング
                                      └── ergasterion/ ← 論文分析
```

---

## Specialist Review の目的

Jules の specialist review は **ニッチな知的発見** を目的としている。
一般的な lint (ruff, mypy) が検出する問題は対象外。
既存ツールでは見つけられない **設計・構造・美学** の問題を発見することが期待される。

**良いフィードバックとは**:

1. 設計レベルの洞察 — 隠れた結合、責務の肥大化
2. 美的判断 — 視覚的リズム、命名の調和
3. パターン逸脱 — 確立された設計哲学からの偏差
4. 問題がなければ **SILENCE** — 問題を製造しない

---

## Knowledge Base CLI

プロジェクトの知識基盤 (34K+ ドキュメント) を検索するための CLI が利用可能:

```bash
# 知識検索
./scripts/hegemonikon-kb search "free energy principle prediction"

# 論文検索
./scripts/hegemonikon-kb paper "attention mechanism"

# CCL 構文解析
./scripts/hegemonikon-kb ccl "/noe+_/dia"

# システム状態
./scripts/hegemonikon-kb status
```

> **Note**: Gateway への接続が必要 (`HGK_GATEWAY_URL`, `HGK_GATEWAY_TOKEN`)。
> オフラインの場合は `mekhane/symploke/context/*.md` にプリ生成されたドメイン知識がある。

---

## ドメイン知識 (context/)

`mekhane/symploke/context/` にテーマ別のドメイン知識ファイルがある:

| ファイル | 内容 |
|:---------|:-----|
| `hgk_knowledge.md` | FEP 概要、6 Series、設計原則、アーキテクチャパターン |
| `fep_foundation.md` | FEP 理論基盤の詳細 |
| `design_patterns.md` | 設計パターンとアーキテクチャ |
| `ccl_language.md` | CCL 言語の構文と使い方 |
| `quality_assurance.md` | 品質保証パターン (PROOF.md, Dendron) |

レビュー時に対象ファイルのドメインに応じてこれらを参照すること。

---

*Hegemonikón v6.0 — KB Bridge 統合 (2026-02-14)*
