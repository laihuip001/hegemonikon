# PROOF.md — 存在証明書

PURPOSE: _archive_v01 モジュールの実装
REASON: _archive_v01 の機能が必要だった

> **∃ _archive_v01/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón プロジェクト` の一部として存在が要請される
2. **機能公理**: `_archive_v01 モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `claude_api.py` | Claude API Client for Synergeia |
| `coordinator.py` | Synergeia Coordinator (簡易版) |
| `experiment_001.py` | Synergeia Experiment 001: 並列CCL実行 |
| `fep_selector.py` | Synergeia FEP Selector — 不確実性に基づく最適スレッド選択 |
| `gemini_api.py` | Gemini API Client for Synergeia |
| `interactive.py` | Synergeia Interactive Coordinator |
| `jules_api.py` | Jules API Client for Synergeia |
| `jules_dashboard.py` | Jules Usage Dashboard & PR Retrieval |

---

*Generated: 2026-02-08 by generate_proofs.py*
