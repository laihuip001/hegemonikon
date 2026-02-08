# PROOF.md — 存在証明書

PURPOSE: テスト・実験用ユーティリティスクリプト
REASON: peira モジュールの動作検証用スクリプトが必要だった

> **∃ scripts/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `実験・プロトタイプスクリプトを格納し、新機能の検証環境を提供する` の一部として存在が要請される
2. **機能公理**: `テスト・実験用ユーティリティスクリプト` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `aidb-kb.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `arxiv-collector.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `chat-history-kb.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `cleanup-datefix.py` | cleanup-datefix.py |
| `cleanup-duplicates.py` | cleanup-duplicates.py |
| `doc_maintenance.py` | Module: doc_maintenance.py |
| `import_takeout.py` | Takeout Importer for Hegemonikón (Robustness Enhanced) |
| `merge-manifests.py` | merge-manifests.py |
| `note-collector.py` | note.com 記事収集スクリプト v2 |
| `perplexity_api.py` | Perplexity API Client (パプ君) |
| `phase2-save-urls.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `phase3-fast-collect.py` | phase3-fast-collect.py |
| `phase3-fetch-simple.py` | phase3-fetch-simple.py |
| `phase3-get-batch.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `phase3-merge-manifests.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `phase3-save-batch-parallel.py` | phase3-save-batch-parallel.py |
| `phase3-save-batch.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |
| `restore-missing.py` | PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要 |

---

*Generated: 2026-02-08 by generate_proofs.py*
