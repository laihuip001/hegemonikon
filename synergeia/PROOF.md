# PROOF — Synergeia 存在証明

REASON: 単一 AI の認知負荷制限 (60pt) を超える複雑な CCL 処理を、複数エージェント協調実行で解決する必要があった  <!-- AUTO-REASON -->

> 各ファイルの存在理由を証明する

## ファイル一覧 (v2)

| ファイル | 存在理由 |
|:---------|:---------|
| `README.md` | プロジェクト概要、v2 アーキテクチャ |
| `PROOF.md` | 本ファイル。存在証明の記録 |
| `bridge.py` | n8n webhook への薄い Python ラッパー (v2 core) |
| `__init__.py` | v2 公開 API の re-export |
| `architecture.md` | 分散実行アーキテクチャの技術仕様 |
| `threads.md` | 利用可能スレッドの詳細仕様 |
| `experiments/` | 実験ログの格納ディレクトリ |
| `tests/` | テストスイート (test_bridge.py, test_integration.py) |
| `_archive_v01/` | v0.1 コードのアーカイブ (8ファイル) |

## n8n WF

| WF | パス | 役割 |
|:---|:-----|:-----|
| WF-17 | `mekhane/ergasterion/n8n/wf17_synergeia_coordinator.json` | 分散 CCL 実行 Coordinator |

## 依存関係

- `hegemonikon/mekhane/ergasterion/n8n/` — Sympatheia n8n インフラ
- `hegemonikon/hermeneus/` — CCL パーサー (MCP 経由)
- HGK API (`localhost:8765`) — MCP ツールへの HTTP bridge

---

*Created: 2026-02-01 | Updated: 2026-02-13 (v2 刷新)*
