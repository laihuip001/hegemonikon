# PROOF.md — 存在証明書

PURPOSE: tests_root モジュールの実装
REASON: tests_root の機能が必要だった

> **∃ tests_root/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón の実装コード (Mēkhanē) を格納し、認知ハイパーバイザーの全機能を提供する` の一部として存在が要請される
2. **機能公理**: `tests_root モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `test_encoding.py` | Tests for encoding.py - Text-to-Observation encoding. |
| `test_fep_agent.py` | Tests for Hegemonikón FEP Agent |
| `test_fep_bridge.py` | Tests for FEP Bridge - Workflow Integration Layer. |
| `test_fep_config.py` | Tests for FEP config module. |
| `test_llm_evaluator.py` | Tests for LLM Evaluator - Hierarchical Hybrid Evaluation. |
| `test_synedrion.py` | Synedrion テストスイート |
| `test_vault.py` | Test writing a new file. |

---

*Generated: 2026-02-08 by generate_proofs.py*
