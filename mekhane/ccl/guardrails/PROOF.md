# PROOF.md — 存在証明書

PURPOSE: CCL 式のバリデーションとガードレール
REASON: 不正な CCL 式を実行前に検出・拒否する安全機構が必要だった

> **∃ guardrails/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `CCL (Cognitive Command Language) のパーサーとジェネレーターを実装する` の一部として存在が要請される
2. **機能公理**: `CCL 式のバリデーションとガードレール` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | Guardrails sub-package |
| `validators.py` | CCL Output Validator - 出力検証モジュール |

---

*Generated: 2026-02-08 by generate_proofs.py*
