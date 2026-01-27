# Jules リポジトリ設定ガイド

## hegemonikon リポジトリ設定

### 1. Setup Script

```bash
#!/bin/bash
# Hegemonikón環境セットアップ

# Python仮想環境セットアップ
python3.11 -m venv .venv
source .venv/bin/activate

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt

# 開発用依存関係
pip install pytest pytest-asyncio aiohttp

# MCP SDK（オプション）
pip install mcp

# 環境確認
python --version
echo "Setup complete!"
```

---

### 2. Environment Variables

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHONPATH` | `/app` | Python パス |
| `HEGEMONIKON_ENV` | `development` | 実行環境 |
| `LOG_LEVEL` | `INFO` | ログレベル |

> ⚠️ **注意**: API キーは環境変数に設定しない（セキュリティリスク）

---

### 3. Network Access

**推奨: 有効化**

理由:

- pip パッケージのインストール
- 外部 API テスト（必要な場合）
- Git submodule の取得

---

### 4. Memories

**推奨: 有効化**

理由:

- hegemonikon の構造を学習
- 過去のタスクから文脈を継承
- 効率的なタスク実行

---

## agents.md 設定案

Jules は `/app/agents.md` を読み込んで環境ヒントを取得する。
hegemonikon 用の agents.md を作成するべき:

```markdown
# agents.md - Hegemonikón

## Project Overview
Hegemonikón is a cognitive hypervisor framework based on:
- Free Energy Principle (FEP)
- Stoic Philosophy
- Common Model of Cognition (CMoC)

## Tech Stack
- Python 3.11
- Async/await patterns
- MCP (Model Context Protocol)

## Directory Structure
- `kernel/` - Core theorems (O/S/H/P/K series)
- `mekhane/` - Implementation layer
- `mcp/` - MCP servers
- `docs/` - Documentation

## Coding Standards
- Greek naming conventions for philosophy concepts
- Type annotations required
- docstrings in Japanese or English

## Default Branch
- `master` (NOT main)

## Testing
- pytest for unit tests
- pytest-asyncio for async tests
```

---

## パフォーマンス最適化

### スナップショットの活用

1. Setup script を実行して成功させる
2. 「Run and snapshot」で環境を保存
3. 次回以降は **スナップショットから起動**（高速）

### 推奨スナップショット内容

- Python 3.11 + venv
- 主要依存パッケージ（aiohttp, pytest 等）
- MCP SDK

---

*作成日: 2026-01-27*
