# Synergeia — マルチエージェント協調 CCL 実行

> **核心**: 単一 AI の限界 (60pt) を超えるため、CCL 式を複数スレッドに分散実行する

## v2 Architecture (2026-02-13~)

```
CCL 式
    │
    ▼
bridge.py (Python) ──POST──> n8n WF-17 (Webhook)
                                  │
                              CCL Parser
                                  │
                            Thread Switch
                          ┌───┬───┬───┐
                          │   │   │   │
                       Ochēma Jules Pplx Herm
                          │   │   │   │
                          └───┴───┴───┘
                              Merge
                                │
                            Response
```

## Quick Start

```python
from synergeia import dispatch

# 単一実行
result = dispatch("/noe+", context="Synergeia の設計を分析")

# CLI
python -m synergeia.bridge "/noe+ || /sop+"
python -m synergeia.bridge --health
```

## スレッド

| スレッド | CCL | バックエンド |
|:---------|:----|:------------|
| Ochēma | `/noe`, `/dia`, `/bou`, `/zet`, `/u` | Ochēma MCP → LLM |
| Jules | `/s`, `/mek`, `/ene`, `/pra` | Jules MCP → Gemini |
| Perplexity | `/sop` | Perplexity API |
| Hermēneus | default | Hermēneus MCP → LMQL |

## 依存

- **n8n** (`localhost:5678`) — Sympatheia 経由で稼働
- **HGK API** (`localhost:8765`) — MCP ツールへの HTTP bridge

## v0.1 Archive

v0.1 (Python subprocess ベース) のコードは `_archive_v01/` に保存。

---

*Synergeia v2.0.0 — 2026-02-13*
