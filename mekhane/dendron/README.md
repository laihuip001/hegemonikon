# PROOF: [L1/定理] Dendron→存在証明CLI

> **Author**: Claude
> **Date Created**: 2026-01-31
> **Purpose**: 存在証明の検証ツール

# Dendron — 存在証明検証ツール

> 「存在誤差最小化」— FEP の予測誤差最小化を存在次元に適用

## 概要

Dendron は、コードベースの各ファイル・ディレクトリに「存在理由」が宣言されていることを検証するツールです。

## インストール

```bash
# hegemonikon 内から
python -m mekhane.dendron.cli check .
```

## 使用方法

```bash
# 全ファイルの PROOF 状態をチェック
dendron check

# 特定ディレクトリのみ
dendron check mekhane/

# カバレッジレポート
dendron check --coverage

# CI モード (失敗時に exit 1)
dendron check --ci
```

## PROOF レベル

| レベル | 対象 | 説明 |
|--------|------|------|
| L1 | 定理 | 理論的基盤、コア機能 |
| L2 | インフラ | 支援機能、ユーティリティ |
| L3 | テスト | テスト、サンプル |

## ディレクトリ構造

```
mekhane/dendron/
├── __init__.py       # パッケージ定義
├── cli.py            # CLI エントリポイント
├── checker.py        # PROOF 検証ロジック
├── reporter.py       # レポート生成
└── tests/            # テスト
```

## Doc Staleness (ドキュメント腐敗検知)

ドキュメント間の依存関係を YAML frontmatter で宣言し、上流の更新に下流が追従しているかを自動検知する。

### frontmatter の書き方

```yaml
---
doc_id: "MY_DOC"
version: "1.0.0"
updated: "2026-02-17"
depends_on:
  - doc_id: "AXIOM_HIERARCHY"
    min_version: "7.0.0"
  - doc_id: "ARCHITECTURE"
    min_version: "1.0.0"
---
```

| フィールド | 必須 | 説明 |
|:-----------|:----:|:-----|
| `doc_id` | ✅ | ドキュメント一意識別子 |
| `version` | ✅ | semver (例: `1.2.3`, `2.0.0a1`) |
| `updated` | 推奨 | `YYYY-MM-DD` 形式 |
| `depends_on` | 任意 | 上流ドキュメントの `doc_id` と `min_version` |

### 判定ルール

| ステータス | 条件 |
|:-----------|:-----|
| **OK** | 上流 version == 下流 min_version |
| **STALE** | 上流 version > 下流 min_version |
| **WARNING** | updated 日付差 > 30日 |
| **CIRCULAR** | 循環依存を検出 |

### 実行方法

```bash
# CLI
python -m mekhane.dendron.doc_staleness --check

# Boot 時: 軸 Q (Doc Health) として自動実行
```

## 関連ドキュメント

- [PROOF.md](./PROOF.md) — このディレクトリの存在証明
- [kernel/proof_levels.md](/home/makaron8426/oikos/hegemonikon/kernel/proof_levels.md) — PROOF レベル定義
