#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- hermeneus MCP サーバー起動ラッパー
"""
Hermēneus MCP Server Launcher

hermeneus/src/ast.py と Python 標準 ast モジュールの名前衝突を回避するため、
プロジェクトルートからラッパー経由で起動する。

Usage (MCP client):
    command: /path/to/.venv/bin/python
    args: ["/path/to/scripts/hermeneus_mcp.py"]
"""
import sys
from pathlib import Path

# プロジェクトルートを PYTHONPATH に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# MCP サーバーを起動
from hermeneus.src.mcp_server import run_server
run_server()
