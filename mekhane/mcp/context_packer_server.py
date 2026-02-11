# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→デバッグコンテキスト集約が必要→context_packer_serverが担う
"""
Context Packer MCP Server — HGK デバッグコンテキスト集約

Git状態・ログ・環境変数(安全なもののみ)を JSON で集約し、
AI に「今の環境状態」を一発で渡す MCP サーバー。

Usage:
  python mekhane/mcp/context_packer_server.py

MCP設定 (.cursor/mcp.json):
  {
    "mcpServers": {
      "context-packer": {
        "command": "python",
        "args": ["mekhane/mcp/context_packer_server.py"]
      }
    }
  }

Source: 2026-02-10 消化レポート — BetterBugs MCP パターン
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # FastMCP が未インストールの場合のフォールバック
    print("Warning: mcp package not installed. Install with: pip install mcp")
    raise SystemExit(1)

mcp = FastMCP("Hegemonikon Context Packer")

# --- Security: 公開してよい環境変数のホワイトリスト ---
SAFE_ENV_KEYS = frozenset({
    "NODE_ENV",
    "PYTHONPATH",
    "VIRTUAL_ENV",
    "SHELL",
    "LANG",
    "HOME",
    "USER",
    "PWD",
})


def _run_cmd(cmd: str, cwd: str | None = None) -> str:
    """コマンドを実行して stdout を返す。失敗時は空文字列。"""
    try:
        result = subprocess.run(
            shlex.split(cmd),
            capture_output=True,
            text=True,
            timeout=5,
            cwd=cwd,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


# PURPOSE: context_packer_server の capture debug context 処理を実行する
@mcp.tool()
def capture_debug_context(
    project_root: str = ".",
    log_file: str = "",
    log_lines: int = 50,
) -> str:
    """現在のGit状態、環境変数(安全なもののみ)、直近のログを収集してJSONで返す。
    
    Args:
        project_root: プロジェクトルートディレクトリ (デフォルト: カレント)
        log_file: 読み込むログファイルパス (デフォルト: なし)
        log_lines: ログファイルから読み込む末尾行数 (デフォルト: 50)
    """
    root = Path(project_root).resolve()

    # 1. Git Status
    git_branch = _run_cmd("git branch --show-current", cwd=str(root))
    git_status = _run_cmd("git status --porcelain", cwd=str(root))
    git_log = _run_cmd("git log --oneline -5", cwd=str(root))

    dirty_files = [
        line.strip() for line in git_status.split("\n") if line.strip()
    ]

    # 2. Log Tail
    log_content: list[str] = []
    if log_file:
        log_path = Path(log_file)
        if log_path.exists() and log_path.is_file():
            try:
                lines = log_path.read_text(encoding="utf-8").splitlines()
                log_content = lines[-log_lines:] if log_lines < len(lines) else lines
            except (OSError, UnicodeDecodeError):
                log_content = ["[ERROR: ログファイルの読み込みに失敗]"]

    # 3. Environment (Whitelist のみ)
    safe_env = {
        k: v for k, v in os.environ.items() if k in SAFE_ENV_KEYS
    }

    # 4. Python / Node versions
    python_version = _run_cmd("python3 --version")
    node_version = _run_cmd("node --version")

    # 5. Disk usage (project root)
    disk_usage = _run_cmd(f"du -sh {root}")

    context: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "git": {
            "branch": git_branch or "detached/unknown",
            "dirty_files": dirty_files,
            "dirty_count": len(dirty_files),
            "recent_commits": git_log.split("\n") if git_log else [],
        },
        "environment": safe_env,
        "runtime": {
            "python": python_version,
            "node": node_version,
        },
        "disk_usage": disk_usage,
        "recent_logs": log_content,
    }

    return json.dumps(context, indent=2, ensure_ascii=False)


# PURPOSE: context_packer_server の capture error context 処理を実行する
@mcp.tool()
def capture_error_context(
    error_message: str,
    file_path: str = "",
    line_number: int = 0,
) -> str:
    """エラー発生時のコンテキストを収集してJSONで返す。
    
    Args:
        error_message: エラーメッセージ
        file_path: エラーが発生したファイルパス
        line_number: エラーが発生した行番号
    """
    context: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": {
            "message": error_message,
            "file": file_path,
            "line": line_number,
        },
    }

    # ファイルの周辺行を取得
    if file_path and line_number > 0:
        fpath = Path(file_path)
        if fpath.exists():
            try:
                lines = fpath.read_text(encoding="utf-8").splitlines()
                start = max(0, line_number - 5)
                end = min(len(lines), line_number + 5)
                context["surrounding_code"] = {
                    "start_line": start + 1,
                    "end_line": end,
                    "lines": lines[start:end] if end <= len(lines) else lines[start:],
                }
            except (OSError, UnicodeDecodeError):
                context["surrounding_code"] = None

    # Git blame for the file
    if file_path:
        blame = _run_cmd(f"git blame -L {max(1,line_number-2)},{line_number+2} {file_path}")
        context["git_blame"] = blame if blame else None

    return json.dumps(context, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
