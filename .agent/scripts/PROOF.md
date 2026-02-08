# PROOF.md — 存在証明書

PURPOSE: scripts モジュールの実装
REASON: scripts の機能が必要だった

> **∃ scripts/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón プロジェクト` の一部として存在が要請される
2. **機能公理**: `scripts モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `bidirectional_linker.py` | bidirectional_linker.py — SE-6 Scalable Foundation実装 |
| `check_environment.py` | check_environment.py - 環境設定チェックスクリプト |
| `detect-handoff.py` | Handoff 形式検知・自動記録スクリプト |
| `detect-t-series.py` | T-series 発動検知スクリプト |
| `diagnose_error.py` | diagnose_error.py - Antigravity/Perplexity エラー診断スクリプト |
| `dispatch-stats.py` | Dispatch Log 自動集計スクリプト |
| `update-workflow-registry.py` | ワークフロー命名規則ドキュメントの自動更新スクリプト |

---

*Generated: 2026-02-08 by generate_proofs.py*
