# PROOF.md — 存在証明書

PURPOSE: searchers モジュールの実装
REASON: searchers の機能が必要だった

> **∃ searchers/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón の実装コード (Mēkhanē) を格納し、認知ハイパーバイザーの全機能を提供する` の一部として存在が要請される
2. **機能公理**: `searchers モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | Periskopē searchers — pluggable search source adapters. |
| `brave_searcher.py` | Brave Search API client for Periskopē. |
| `internal_searcher.py` | Internal knowledge searcher for Periskopē. |
| `playwright_searcher.py` | Playwright-based searcher for Periskopē. |
| `searxng.py` | SearXNG search client for Periskopē. |
| `semantic_scholar_searcher.py` | Semantic Scholar API client for Periskopē. |
| `tavily_searcher.py` | Tavily Search API client for Periskopē. |

---

*Generated: 2026-02-08 by generate_proofs.py*
