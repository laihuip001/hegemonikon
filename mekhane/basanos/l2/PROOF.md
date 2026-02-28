# PROOF.md — 存在証明書

PURPOSE: l2 モジュールの実装
REASON: l2 の機能が必要だった

> **∃ l2/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `偉人評議会 (Basanos) の多角的レビュー機能を実装する` の一部として存在が要請される
2. **機能公理**: `l2 モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | Basanos L2: Structural Deficit Detection |
| `cli.py` | PURPOSE: Basanos L2 問い生成 CLI — deficit 検出→問い生成→優先度表示 |
| `deficit_factories.py` | Deficit factories for Basanos L2. |
| `g_semantic.py` | G_semantic: LLM-based translation of HGK terms to general ac |
| `g_struct.py` | G_struct: Mechanical parser for kernel/ markdown files. |
| `history.py` | Deficit history persistence for Basanos L2. |
| `hom.py` | Hom computation for Basanos L2. |
| `models.py` | Core data models for Basanos L2 structural deficit detection |
| `resolver.py` | Auto-resolution loop for Basanos L3. |

---

*Generated: 2026-02-08 by generate_proofs.py*
