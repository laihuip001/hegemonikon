---
doc_id: "GEMINI_PROFILE"
version: "1.0.0"
description: Hegemonikón IDE Profile
updated: "2026-02-17"
depends_on:
  - doc_id: "AXIOM_HIERARCHY"
    min_version: "7.0.0"
  - doc_id: "ARCHITECTURE"
    min_version: "1.0.0"
---

# GEMINI.md - Hegemonikón Doctrine (Linux/GCP)

> **Hegemonikon Project Profile**
>
> このファイルはAntigravity IDEがセッション開始時に読み込むプロファイルです。

## Project Reference

**Primary Workspace**: `/home/makaron8426/oikos/hegemonikon`

このプロジェクトで作業する場合、以下を自動参照してください：

- **Rules**: `.agent/rules/` - 特に `hegemonikon.md` (always_on)
- **Workflows**: `.agent/workflows/` - `/boot`, `/bye`, `/plan` など
- **Skills**: `.agent/skills/` - 開発プロトコル参照
- **正本**: `kernel/axiom_hierarchy.md` - 公理体系の正本 (v7.0)

## Core Doctrine

Hegemonikón は FEP (Free Energy Principle) に基づく認知ハイパーバイザーフレームワークです。

### 体系概要 (v3.7)

| 項目 | 数 |
|------|----|
| 公理 | **1** (FEP) |
| 定理¹ (座標) | 6 (1+2+3) |
| 定理² (認知機能) | 24 (6×4) |
| 関係 (Series内) | 36 |
| 関係 (Series間) | 72 |
| **総計** | **103+** |

### 6 定理群

| 記号 | 名称 | 役割 |
|------|------|------|
| O | Ousia | 本質 |
| S | Schema | 様態 |
| H | Hormē | 傾向 |
| P | Perigraphē | 条件 |
| K | Kairos | 文脈 |
| A | Akribeia | 精密 |

### 絶対遵守事項

1. **日本語**: ユーザー向けテキストはすべて日本語
2. **破壊的操作禁止**: ファイル削除・上書き前に確認
3. **確信度正直表示**: 不確実な場合は明示
4. **Zero Entropy**: 曖昧さを質問で解消
5. **Proactive Opinion**: 意見があれば求められなくても述べる（ないときは黙る）
6. **第零原則**: 意志より環境。自分を信じない。第一原理に分解して再構成する

### 主要ワークフロー

| コマンド | 用途 |
|----------|------|
| `/boot` | セッション開始 |
| `/bye` | セッション終了・引き継ぎ |
| `/plan` | 設計計画策定 |
| `/now` | 現在地確認 |
| `/u` | 明示的に意見を求める |
| `/dia` | 6視点検証 |
| `/noe` | 最深層思考 |

### MCP サーバー

| 名前 | ツール数 | 用途 |
|------|---------|------|
| hermeneus | 6 | CCL dispatch/compile/execute |
| gnosis | 3 | 論文検索 (LanceDB) |
| sophia | 4 | KI 検索 |
| mneme | 3 | 統合記憶検索 |
| sympatheia | 6 | 通知、WBC、フィードバック |
| jules | 4 | Jules コーディング連携 |
| typos | 1 | プロンプト生成 |
| digestor | 3 | 論文消化パイプライン |

## Environment

- **OS**: Debian 13 (GCP c4-standard-24)
- **Python**: 3.11+ (.venv)
- **Node.js**: 20.x
- **DB**: LanceDB (ベクトル検索)
- **正本**: `kernel/axiom_hierarchy.md` (v7.0, 2026-02-15)

---

*Last updated: 2026-02-17*
