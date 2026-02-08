#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- hermeneus MCP サーバー起動ラッパー
"""
Hermēneus MCP Server Launcher

hermeneus/src/ast.py と Python 標準 ast モジュールの名前衝突を回避するため、
プロジェクトルートからラッパー経由で起動する。

Usage (MCP client):
    command: /path/.venv/bin/python
    args: ["/path/to/scripts/hermeneus_mcp.py"]
"""
import sys
import os
import json
from pathlib import Path

# 起動環境ログ (stderr = MCP 通信に干渉しない)
startup_info = {
    "event": "hermeneus_mcp_startup",
    "cwd": os.getcwd(),
    "python": sys.executable,
    "pid": os.getpid(),
}
print(json.dumps(startup_info), file=sys.stderr)

# プロジェクトルートを PYTHONPATH に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# MCP サーバーを起動
from hermeneus.src.mcp_server import run_server
run_server()
