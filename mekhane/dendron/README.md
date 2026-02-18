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

## 関連ドキュメント

- [PROOF.md](./PROOF.md) — このディレクトリの存在証明
- [kernel/proof_levels.md](/home/makaron8426/oikos/hegemonikon/kernel/proof_levels.md) — PROOF レベル定義
