#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/ochema/tools.py S2→Mekhane→Ochema
# PURPOSE: API 直叩き AI にファイル読み書き・コマンド実行能力を付与する
#   Function Calling (Tool Use) のツール定義と実行ディスパッチャ

"""
Ochema Tool Use — AI のローカルファイル操作基盤

Gemini/Claude API の Function Calling を利用し、
API 直叩き AI がローカルファイルの読み書き・検索・コマンド実行を行えるようにする。

Architecture:
    User → OchemaService.ask_with_tools() → CortexClient or AntigravityClient
         → LLM API (+ tools definitions)
         ← functionCall / tool_use response
         → execute_tool() → ローカル実行
         → LLM API (results)
         ← 最終テキスト

Supports:
    - Gemini: Native Function Calling (structured JSON)
    - Claude: Text-based Tool Use (system prompt + parsing)
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# --- Security: Allowed directories ---

# Only allow file operations within these directories
ALLOWED_ROOTS: list[Path] = [
    Path.home() / "oikos",
    Path("/tmp"),
]

# Maximum file read size (bytes)
MAX_READ_SIZE = 512 * 1024  # 512KB

# Maximum command execution time
MAX_CMD_TIMEOUT = 30  # seconds

# Tool execution log
_TOOL_LOG: list[dict[str, Any]] = []


def _is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories."""
    if not path or not path.strip():
        return False
    try:
        resolved = Path(path).expanduser().resolve()
        return any(
            resolved == root or root in resolved.parents
            for root in ALLOWED_ROOTS
        )
    except (ValueError, OSError):
        return False


def _log_tool_use(name: str, args: dict, result: dict, elapsed: float) -> None:
    """Record tool execution for audit trail (F5)."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": name,
        "args_summary": {k: str(v)[:100] for k, v in args.items()},
        "success": "error" not in result,
        "elapsed_ms": round(elapsed * 1000, 1),
    }
    _TOOL_LOG.append(entry)
    # Keep only last 100 entries
    if len(_TOOL_LOG) > 100:
        _TOOL_LOG.pop(0)


def get_tool_log() -> list[dict[str, Any]]:
    """Get the tool execution audit log (F5)."""
    return list(_TOOL_LOG)


# --- Tool Definitions (Gemini Function Calling format) ---

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "read_file",
        "description": (
            "Read the content of a local file. "
            "Returns the file content as text. "
            "Use start_line/end_line to read specific ranges."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute file path (e.g. /home/user/file.py)",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Start line number (1-indexed, optional)",
                },
                "end_line": {
                    "type": "integer",
                    "description": "End line number (1-indexed, inclusive, optional)",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write content to a local file. "
            "Creates parent directories if needed. "
            "Set append=true to append instead of overwrite."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute file path",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write",
                },
                "append": {
                    "type": "boolean",
                    "description": "Append to file instead of overwrite (default: false)",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": (
            "List files and subdirectories in a directory. "
            "Returns entries with type (file/dir) and size."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute directory path",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum recursion depth (default: 1, max: 3)",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_text",
        "description": (
            "Search for a text pattern in files (grep-like). "
            "Returns matching lines with file paths and line numbers."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Text pattern to search for",
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search in",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for file names (e.g. '*.py', default: '*')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 50)",
                },
            },
            "required": ["pattern", "directory"],
        },
    },
    {
        "name": "run_command",
        "description": (
            "Execute a shell command and return the output. "
            "Use for safe, read-only commands (ls, git status, python -c, etc). "
            "Timeout: 30 seconds."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory (default: ~/oikos)",
                },
            },
            "required": ["command"],
        },
    },
    # --- F2: Developer Tools ---
    {
        "name": "git_diff",
        "description": (
            "Show git diff for the repository. "
            "Returns staged or unstaged changes. "
            "Use ref to compare with a specific commit."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repo (default: ~/oikos/hegemonikon)",
                },
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes (--cached)",
                },
                "ref": {
                    "type": "string",
                    "description": "Compare with ref (e.g. HEAD~3, main)",
                },
                "file_path": {
                    "type": "string",
                    "description": "Limit diff to specific file",
                },
            },
        },
    },
    {
        "name": "git_log",
        "description": (
            "Show git commit history. "
            "Returns recent commits with hash, author, date, and message."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to git repo (default: ~/oikos/hegemonikon)",
                },
                "max_count": {
                    "type": "integer",
                    "description": "Number of commits to show (default: 10, max: 50)",
                },
                "file_path": {
                    "type": "string",
                    "description": "Show commits for specific file only",
                },
                "oneline": {
                    "type": "boolean",
                    "description": "One-line format (default: true)",
                },
            },
        },
    },
]


# --- Tool Execution ---


def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Dispatch and execute a tool call.

    Args:
        name: Tool name (must be one of TOOL_DEFINITIONS)
        args: Tool arguments

    Returns:
        Result dict with 'output' or 'error' key
    """
    dispatch = {
        "read_file": _exec_read_file,
        "write_file": _exec_write_file,
        "list_directory": _exec_list_directory,
        "search_text": _exec_search_text,
        "run_command": _exec_run_command,
        "git_diff": _exec_git_diff,
        "git_log": _exec_git_log,
    }

    if name not in dispatch:
        return {"error": f"Unknown tool: {name}"}

    # High-risk tool detection for WBC alerting
    HIGH_RISK_TOOLS = {"write_file", "run_command"}

    try:
        logger.info("Tool execute: %s(%s)", name, args)
        start = time.monotonic()
        result = dispatch[name](args)
        elapsed = time.monotonic() - start
        logger.info("Tool result: %s → %d bytes (%.1fms)", name, len(str(result)), elapsed * 1000)
        _log_tool_use(name, args, result, elapsed)

        # WBC alert for high-risk tool executions
        if name in HIGH_RISK_TOOLS:
            _wbc_alert(name, args, result)

        return result
    except Exception as e:
        logger.error("Tool error: %s → %s", name, e)
        result = {"error": f"{type(e).__name__}: {e}"}
        _log_tool_use(name, args, result, 0)
        return result


def _wbc_alert(tool_name: str, args: dict[str, Any], result: dict[str, Any]) -> None:
    """Send high-risk tool execution alert to Sympatheia WBC.

    Non-blocking: logs errors but never raises.
    """
    try:
        severity = "medium"
        if tool_name == "run_command":
            cmd = args.get("command", "")
            # Elevated severity for commands that modify state
            if any(kw in cmd for kw in ("rm", "mv", "cp", "git push", "pip", "npm")):
                severity = "high"
        elif tool_name == "write_file":
            path = args.get("path", "")
            # Elevated severity for config/kernel files
            if any(kw in path for kw in ("kernel/", ".env", "config", "SACRED")):
                severity = "high"

        details = (
            f"AI Tool Use: {tool_name}\n"
            f"Args: {json.dumps(args, ensure_ascii=False)[:500]}\n"
            f"Result: {'error' if 'error' in result else 'success'}"
        )
        files = [args.get("path", args.get("cwd", ""))]

        # Try to import and call WBC — non-fatal if unavailable
        try:
            from mekhane.mcp.sympatheia_server import wbc_alert as _sym_wbc
            _sym_wbc(
                details=details,
                severity=severity,
                files=[f for f in files if f],
                source="ochema-tool-use",
            )
            logger.debug("WBC alert sent: %s (%s)", tool_name, severity)
        except ImportError:
            logger.debug("Sympatheia WBC not available — skipping alert")
        except Exception as e_wbc:
            logger.debug("WBC alert failed: %s", e_wbc)
    except Exception as e:
        # Never crash on WBC alerting
        logger.debug("WBC alert preparation failed: %s", e)


def _exec_read_file(args: dict[str, Any]) -> dict[str, Any]:
    """Read a local file."""
    path = args["path"]
    if not _is_path_allowed(path):
        return {"error": f"Access denied: {path} is outside allowed directories"}

    p = Path(path).expanduser().resolve()
    if not p.exists():
        return {"error": f"File not found: {path}"}
    if not p.is_file():
        return {"error": f"Not a file: {path}"}
    if p.stat().st_size > MAX_READ_SIZE:
        return {"error": f"File too large: {p.stat().st_size} bytes (max {MAX_READ_SIZE})"}

    try:
        content = p.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return {"error": f"Cannot read binary file: {path}"}

    # Line range filtering
    start = args.get("start_line")
    end = args.get("end_line")
    if start or end:
        lines = content.splitlines(keepends=True)
        start_idx = max(0, (start or 1) - 1)
        end_idx = end or len(lines)
        content = "".join(lines[start_idx:end_idx])
        total = len(lines)
        return {"output": content, "total_lines": total, "range": f"{start_idx+1}-{end_idx}"}

    return {"output": content, "total_lines": content.count("\n") + 1}


def _exec_write_file(args: dict[str, Any]) -> dict[str, Any]:
    """Write content to a local file."""
    path = args["path"]
    if not _is_path_allowed(path):
        return {"error": f"Access denied: {path} is outside allowed directories"}

    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    mode = "a" if args.get("append") else "w"
    p.open(mode, encoding="utf-8").write(args["content"])

    return {"output": f"Written {len(args['content'])} bytes to {path}", "mode": mode}


def _exec_list_directory(args: dict[str, Any]) -> dict[str, Any]:
    """List directory contents."""
    path = args["path"]
    if not _is_path_allowed(path):
        return {"error": f"Access denied: {path} is outside allowed directories"}

    p = Path(path).expanduser().resolve()
    if not p.exists():
        return {"error": f"Directory not found: {path}"}
    if not p.is_dir():
        return {"error": f"Not a directory: {path}"}

    max_depth = min(args.get("max_depth", 1), 3)
    entries: list[dict[str, Any]] = []

    def _scan(dir_path: Path, depth: int) -> None:
        if depth > max_depth or len(entries) >= 200:
            return
        try:
            for entry in sorted(dir_path.iterdir()):
                if entry.name.startswith("."):
                    continue  # Skip hidden files
                info: dict[str, Any] = {
                    "name": str(entry.relative_to(p)),
                    "type": "dir" if entry.is_dir() else "file",
                }
                if entry.is_file():
                    info["size"] = entry.stat().st_size
                entries.append(info)
                if entry.is_dir() and depth < max_depth:
                    _scan(entry, depth + 1)
        except PermissionError:
            pass

    _scan(p, 1)
    return {"entries": entries, "total": len(entries), "path": str(p)}


def _exec_search_text(args: dict[str, Any]) -> dict[str, Any]:
    """Search for text pattern in files."""
    directory = args["directory"]
    if not _is_path_allowed(directory):
        return {"error": f"Access denied: {directory} is outside allowed directories"}

    pattern = args["pattern"]
    file_pattern = args.get("file_pattern", "*")
    max_results = min(args.get("max_results", 50), 100)

    # Use ripgrep if available, fallback to grep
    rg_path = "/usr/bin/rg"
    if Path(rg_path).exists():
        cmd = [rg_path, "--json", "-m", str(max_results), "--glob", file_pattern, pattern, directory]
    else:
        cmd = ["grep", "-rnI", f"--include={file_pattern}", pattern, directory]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=MAX_CMD_TIMEOUT
        )
        lines = result.stdout.strip().split("\n")[:max_results]
        matches = [line for line in lines if line]
        return {"matches": matches, "count": len(matches), "pattern": pattern}
    except subprocess.TimeoutExpired:
        return {"error": "Search timed out"}


def _exec_run_command(args: dict[str, Any]) -> dict[str, Any]:
    """Execute a shell command."""
    command = args["command"]
    cwd = args.get("cwd", str(Path.home() / "oikos"))

    if not _is_path_allowed(cwd):
        return {"error": f"Access denied: cwd {cwd} is outside allowed directories"}

    # Block dangerous commands
    dangerous = ["rm -rf /", "mkfs", "dd if=", "> /dev/", "chmod -R 777"]
    if any(d in command for d in dangerous):
        return {"error": f"Blocked dangerous command: {command}"}

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=MAX_CMD_TIMEOUT,
            cwd=cwd,
            env={**os.environ, "PAGER": "cat"},
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"

        # Truncate if too large
        if len(output) > MAX_READ_SIZE:
            output = output[:MAX_READ_SIZE] + f"\n... (truncated, total {len(output)} bytes)"

        return {
            "output": output,
            "exit_code": result.returncode,
            "command": command,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {MAX_CMD_TIMEOUT}s: {command}"}


# --- F2: Git Tools ---


def _exec_git_diff(args: dict[str, Any]) -> dict[str, Any]:
    """Show git diff."""
    repo = args.get("repo_path", str(Path.home() / "oikos" / "hegemonikon"))
    if not _is_path_allowed(repo):
        return {"error": f"Access denied: {repo}"}

    cmd = ["git", "-C", repo, "diff"]
    if args.get("staged"):
        cmd.append("--cached")
    if args.get("ref"):
        cmd.append(args["ref"])
    cmd.append("--stat")  # Always include stat summary
    if args.get("file_path"):
        cmd.extend(["--", args["file_path"]])

    try:
        # Get stat first
        stat_result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=MAX_CMD_TIMEOUT
        )
        # Get actual diff (without --stat)
        diff_cmd = [c for c in cmd if c != "--stat"]
        diff_result = subprocess.run(
            diff_cmd, capture_output=True, text=True, timeout=MAX_CMD_TIMEOUT
        )
        output = diff_result.stdout
        if len(output) > MAX_READ_SIZE:
            output = output[:MAX_READ_SIZE] + "\n... (diff truncated)"

        return {
            "stat": stat_result.stdout.strip(),
            "diff": output,
            "repo": repo,
        }
    except subprocess.TimeoutExpired:
        return {"error": "git diff timed out"}


def _exec_git_log(args: dict[str, Any]) -> dict[str, Any]:
    """Show git log."""
    repo = args.get("repo_path", str(Path.home() / "oikos" / "hegemonikon"))
    if not _is_path_allowed(repo):
        return {"error": f"Access denied: {repo}"}

    max_count = min(args.get("max_count", 10), 50)
    oneline = args.get("oneline", True)

    cmd = ["git", "-C", repo, "log", f"-{max_count}"]
    if oneline:
        cmd.append("--oneline")
    else:
        cmd.extend(["--format=%H %an %ad %s", "--date=short"])

    if args.get("file_path"):
        cmd.extend(["--", args["file_path"]])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=MAX_CMD_TIMEOUT
        )
        return {
            "output": result.stdout.strip(),
            "count": len(result.stdout.strip().split("\n")),
            "repo": repo,
        }
    except subprocess.TimeoutExpired:
        return {"error": "git log timed out"}


# --- F3: Claude Text-based Tool Use ---

# System prompt that teaches Claude how to use tools via text
TOOL_USE_SYSTEM_PROMPT = """You have access to the following tools for interacting with the local file system.
To use a tool, respond with a JSON block in this exact format:

```tool_call
{"name": "tool_name", "args": {"arg1": "value1"}}
```

You can make multiple tool calls in one response. After each tool call, you will receive the results.
When you have enough information, provide your final answer as normal text (without tool_call blocks).

Available tools:
{tool_descriptions}

IMPORTANT:
- Always use absolute paths starting with /home/ or /tmp/
- File operations are restricted to ~/oikos and /tmp
- Commands have a 30-second timeout
"""


def build_tool_descriptions() -> str:
    """Build human-readable tool descriptions for Claude's system prompt."""
    lines = []
    for tool in TOOL_DEFINITIONS:
        name = tool["name"]
        desc = tool["description"]
        params = tool.get("parameters", {}).get("properties", {})
        required = tool.get("parameters", {}).get("required", [])

        param_lines = []
        for pname, pinfo in params.items():
            req = " (required)" if pname in required else ""
            param_lines.append(f"    - {pname}: {pinfo.get('description', '')}{req}")

        lines.append(f"### {name}\n{desc}")
        if param_lines:
            lines.append("Parameters:")
            lines.extend(param_lines)
        lines.append("")

    return "\n".join(lines)


def get_claude_system_prompt(extra_instructions: str = "") -> str:
    """Build the complete system prompt for Claude text-based tool use."""
    tool_desc = build_tool_descriptions()
    prompt = TOOL_USE_SYSTEM_PROMPT.replace("{tool_descriptions}", tool_desc)
    if extra_instructions:
        prompt += f"\n\n{extra_instructions}"
    return prompt


def parse_tool_calls_from_text(text: str) -> list[dict[str, Any]]:
    """Parse tool calls from Claude's text response.

    Looks for ```tool_call blocks containing JSON.

    Returns:
        List of {"name": str, "args": dict} dicts
    """
    pattern = r"```tool_call\s*\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)

    tool_calls = []
    for match in matches:
        try:
            parsed = json.loads(match.strip())
            if "name" in parsed:
                tool_calls.append({
                    "name": parsed["name"],
                    "args": parsed.get("args", {}),
                })
        except json.JSONDecodeError:
            logger.warning("Failed to parse tool call JSON: %s", match[:100])

    return tool_calls


def has_tool_calls(text: str) -> bool:
    """Check if text contains any tool_call blocks."""
    return "```tool_call" in text


def strip_tool_calls(text: str) -> str:
    """Remove tool_call blocks from text, returning only the narrative."""
    return re.sub(r"```tool_call\s*\n.*?\n```", "", text, flags=re.DOTALL).strip()


# --- F4: HGK System Instruction Templates ---

HGK_SYSTEM_TEMPLATES: dict[str, str] = {
    "default": (
        "You are an AI assistant with access to local file system tools. "
        "Use tools to read, write, search files, and run commands as needed. "
        "Always verify file paths before writing. Be precise and efficient."
    ),
    "hgk_citizen": (
        "You are an AI operating within the Hegemonikón framework. "
        "Core principles:\n"
        "1. BC-5 (Proposal First): Before destructive operations, explain what you plan to do\n"
        "2. BC-6 (Confidence): Mark uncertain claims with [推定] or [仮説]\n"
        "3. BC-16 (Reference First): Read files before modifying them\n"
        "4. I-1 (Safety): Never delete files without explicit permission\n"
        "5. Zero Entropy: If instructions are ambiguous, ask for clarification\n"
        "6. Japanese output: Respond in Japanese unless code/technical terms\n\n"
        "Workspace: ~/oikos/hegemonikon\n"
        "Output language: 日本語"
    ),
    "code_review": (
        "You are a code reviewer with file system access. "
        "Read the specified files, analyze the code, and provide:\n"
        "1. Potential bugs and issues\n"
        "2. Design improvements\n"
        "3. Security concerns\n"
        "4. Performance optimizations\n"
        "Be specific — cite line numbers and file paths."
    ),
    "researcher": (
        "You are a research assistant with access to the local knowledge base. "
        "Search files in ~/oikos for relevant information. "
        "Cite sources with file paths and line numbers. "
        "Distinguish between facts (from files) and inferences (your analysis)."
    ),
}


def get_system_template(template_name: str) -> str:
    """Get a pre-defined system instruction template."""
    return HGK_SYSTEM_TEMPLATES.get(template_name, HGK_SYSTEM_TEMPLATES["default"])
