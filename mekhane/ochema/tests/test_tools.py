#!/usr/bin/env python3
"""Tests for ochema tools — AI ファイル操作基盤のユニットテスト."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mekhane.ochema.tools import (
    TOOL_DEFINITIONS,
    _is_path_allowed,
    execute_tool,
)


class TestPathSecurity:
    """Path permission checks."""

    def test_allowed_oikos(self):
        assert _is_path_allowed(str(Path.home() / "oikos/test.py"))

    def test_allowed_tmp(self):
        assert _is_path_allowed("/tmp/test.txt")

    def test_denied_etc(self):
        assert not _is_path_allowed("/etc/passwd")

    def test_denied_root(self):
        assert not _is_path_allowed("/root/.ssh/id_rsa")

    def test_denied_home_direct(self):
        assert not _is_path_allowed(str(Path.home() / ".bashrc"))

    def test_denied_empty(self):
        assert not _is_path_allowed("")


class TestToolDefinitions:
    """Tool definition structure validation."""

    def test_has_5_tools(self):
        assert len(TOOL_DEFINITIONS) == 5

    def test_all_have_required_fields(self):
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool

    def test_tool_names(self):
        names = {t["name"] for t in TOOL_DEFINITIONS}
        assert names == {"read_file", "write_file", "list_directory", "search_text", "run_command"}


class TestReadFile:
    """read_file tool tests."""

    def test_read_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello\nworld\n")
        result = execute_tool("read_file", {"path": str(f)})
        assert "output" in result
        assert "hello" in result["output"]

    def test_read_nonexistent(self, tmp_path):
        result = execute_tool("read_file", {"path": str(tmp_path / "nope.txt")})
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_read_denied_path(self):
        result = execute_tool("read_file", {"path": "/etc/passwd"})
        assert "error" in result
        assert "denied" in result["error"].lower()

    def test_read_line_range(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3\nline4\n")
        result = execute_tool("read_file", {"path": str(f), "start_line": 2, "end_line": 3})
        assert "output" in result
        assert "line2" in result["output"]
        assert "line3" in result["output"]
        assert "line1" not in result["output"]


class TestWriteFile:
    """write_file tool tests."""

    def test_write_new_file(self, tmp_path):
        target = tmp_path / "new.txt"
        result = execute_tool("write_file", {"path": str(target), "content": "test content"})
        assert "output" in result
        assert target.read_text() == "test content"

    def test_write_append(self, tmp_path):
        target = tmp_path / "append.txt"
        target.write_text("first\n")
        execute_tool("write_file", {"path": str(target), "content": "second\n", "append": True})
        assert target.read_text() == "first\nsecond\n"

    def test_write_denied_path(self):
        result = execute_tool("write_file", {"path": "/etc/evil.txt", "content": "hack"})
        assert "error" in result
        assert "denied" in result["error"].lower()


class TestListDirectory:
    """list_directory tool tests."""

    def test_list_tmp(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.py").write_text("b")
        result = execute_tool("list_directory", {"path": str(tmp_path)})
        assert "entries" in result
        names = {e["name"] for e in result["entries"]}
        assert "a.txt" in names
        assert "b.py" in names

    def test_list_nonexistent(self, tmp_path):
        result = execute_tool("list_directory", {"path": str(tmp_path / "nope")})
        assert "error" in result

    def test_list_denied(self):
        result = execute_tool("list_directory", {"path": "/root"})
        assert "error" in result


class TestSearchText:
    """search_text tool tests."""

    def test_search_basic(self, tmp_path):
        (tmp_path / "test.py").write_text("def hello():\n    pass\n")
        result = execute_tool("search_text", {
            "pattern": "hello",
            "directory": str(tmp_path),
        })
        assert "matches" in result
        assert result["count"] > 0

    def test_search_denied(self):
        result = execute_tool("search_text", {
            "pattern": "root",
            "directory": "/etc",
        })
        assert "error" in result


class TestRunCommand:
    """run_command tool tests."""

    def test_echo(self, tmp_path):
        result = execute_tool("run_command", {
            "command": "echo hello",
            "cwd": str(tmp_path),
        })
        assert "output" in result
        assert "hello" in result["output"]
        assert result["exit_code"] == 0

    def test_blocked_dangerous(self, tmp_path):
        result = execute_tool("run_command", {
            "command": "rm -rf /",
            "cwd": str(tmp_path),
        })
        assert "error" in result
        assert "blocked" in result["error"].lower()

    def test_timeout(self, tmp_path):
        # Mock MAX_CMD_TIMEOUT to a short value to avoid pytest-timeout conflict
        with patch("mekhane.ochema.tools.MAX_CMD_TIMEOUT", 2):
            result = execute_tool("run_command", {
                "command": "sleep 5",
                "cwd": str(tmp_path),
            })
        assert "error" in result
        assert "timed out" in result["error"].lower()


class TestUnknownTool:
    """Error handling for unknown tools."""

    def test_unknown_tool(self):
        result = execute_tool("fake_tool", {})
        assert "error" in result
        assert "Unknown" in result["error"]
