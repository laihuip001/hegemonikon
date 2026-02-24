# PROOF: [L2/Mekhane] <- mekhane/ A0->Auto->AddedByCI
"""Ochema AI Tool Use — Unit Tests.

Tests for tools.py: 7 tools + Claude parser + system templates + audit log.

API convention:
  - Success: {"output": ..., other_keys...}
  - Failure: {"error": "message"}
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from mekhane.ochema.tools import (
    TOOL_DEFINITIONS,
    execute_tool,
    get_claude_system_prompt,
    get_system_template,
    get_tool_log,
    has_tool_calls,
    parse_tool_calls_from_text,
    strip_tool_calls,
    HGK_SYSTEM_TEMPLATES,
)

# Mock _is_path_allowed to always allow during tests
ALLOW_PATCH = patch("mekhane.ochema.tools._is_path_allowed", return_value=True)


@pytest.fixture
def tmp_workspace(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("line1\nline2\nline3\n")
    return tmp_path, test_file


# ========== Tool Definitions ==========

class TestToolDefinitions:
    def test_has_seven_tools(self):
        assert len(TOOL_DEFINITIONS) == 7

    def test_tool_names(self):
        names = {t["name"] for t in TOOL_DEFINITIONS}
        expected = {"read_file", "write_file", "list_directory",
                    "search_text", "run_command", "git_diff", "git_log"}
        assert names == expected

    def test_each_tool_has_required_fields(self):
        for tool in TOOL_DEFINITIONS:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert tool["parameters"]["type"] in ("OBJECT", "object")


# ========== read_file ==========

class TestReadFile:
    def test_read_existing_file(self, tmp_workspace):
        _, test_file = tmp_workspace
        with ALLOW_PATCH:
            result = execute_tool("read_file", {"path": str(test_file)})
        assert "output" in result
        assert "line1" in result["output"]

    def test_read_with_line_range(self, tmp_workspace):
        _, test_file = tmp_workspace
        with ALLOW_PATCH:
            result = execute_tool("read_file", {
                "path": str(test_file),
                "start_line": 2, "end_line": 2,
            })
        assert "output" in result
        assert "line2" in result["output"]
        assert "line1" not in result["output"]

    def test_read_nonexistent(self, tmp_workspace):
        tmp_path, _ = tmp_workspace
        with ALLOW_PATCH:
            result = execute_tool("read_file", {"path": str(tmp_path / "nope.txt")})
        assert "error" in result

    def test_read_outside_allowed(self):
        # Without mock — default ALLOWED_ROOTS blocks /etc
        result = execute_tool("read_file", {"path": "/etc/shadow"})
        assert "error" in result


# ========== write_file ==========

class TestWriteFile:
    def test_write_new_file(self, tmp_workspace):
        tmp_path, _ = tmp_workspace
        new_file = tmp_path / "new.txt"
        with ALLOW_PATCH:
            result = execute_tool("write_file", {
                "path": str(new_file), "content": "hello",
            })
        assert "output" in result
        assert new_file.read_text() == "hello"

    def test_write_append(self, tmp_workspace):
        _, test_file = tmp_workspace
        original = test_file.read_text()
        with ALLOW_PATCH:
            result = execute_tool("write_file", {
                "path": str(test_file), "content": "X", "append": True,
            })
        assert "output" in result
        assert test_file.read_text() == original + "X"

    def test_write_outside_allowed(self):
        result = execute_tool("write_file", {"path": "/root/evil.txt", "content": "bad"})
        assert "error" in result


# ========== list_directory ==========

class TestListDirectory:
    def test_list_existing_dir(self, tmp_workspace):
        tmp_path, _ = tmp_workspace
        with ALLOW_PATCH:
            result = execute_tool("list_directory", {"path": str(tmp_path)})
        assert "output" in result or "entries" in result


# ========== run_command ==========

class TestRunCommand:
    def test_safe_command(self, tmp_workspace):
        tmp_path, _ = tmp_workspace
        with ALLOW_PATCH:
            result = execute_tool("run_command", {
                "command": "echo test_output", "cwd": str(tmp_path),
            })
        assert "output" in result
        assert "test_output" in result["output"]

    def test_dangerous_command_blocked(self, tmp_workspace):
        tmp_path, _ = tmp_workspace
        with ALLOW_PATCH:
            result = execute_tool("run_command", {
                "command": "rm -rf /", "cwd": str(tmp_path),
            })
        assert "error" in result


# ========== git tools ==========

class TestGitTools:
    @pytest.fixture
    def repo_path(self):
        return str(Path(__file__).resolve().parents[3])

    def test_git_log_in_repo(self, repo_path):
        with ALLOW_PATCH:
            result = execute_tool("git_log", {"repo_path": repo_path, "max_count": 3})
        assert "output" in result
        assert len(result["output"]) > 0

    def test_git_diff_in_repo(self, repo_path):
        with ALLOW_PATCH:
            result = execute_tool("git_diff", {"repo_path": repo_path})
        assert "error" not in result


# ========== Claude Parser ==========

class TestClaudeParser:
    SAMPLE = '''I'll read it.

```tool_call
{"name": "read_file", "args": {"path": "/home/user/test.txt"}}
```

Done.'''

    def test_has_tool_calls_positive(self):
        assert has_tool_calls(self.SAMPLE) is True

    def test_has_tool_calls_negative(self):
        assert has_tool_calls("Just text") is False

    def test_parse_tool_calls(self):
        calls = parse_tool_calls_from_text(self.SAMPLE)
        assert len(calls) == 1
        assert calls[0]["name"] == "read_file"

    def test_strip_tool_calls(self):
        stripped = strip_tool_calls(self.SAMPLE)
        assert "tool_call" not in stripped

    def test_parse_empty(self):
        assert parse_tool_calls_from_text("") == []

    def test_multiple_tool_calls(self):
        text = '```tool_call\n{"name": "a", "args": {}}\n```\n```tool_call\n{"name": "b", "args": {}}\n```'
        assert len(parse_tool_calls_from_text(text)) == 2


# ========== System Templates ==========

class TestSystemTemplates:
    def test_four_templates_exist(self):
        assert len(HGK_SYSTEM_TEMPLATES) == 4

    def test_get_known_templates(self):
        for key in ("default", "hgk_citizen", "code_review", "researcher"):
            t = get_system_template(key)
            assert isinstance(t, str) and len(t) > 20

    def test_unknown_returns_default(self):
        t = get_system_template("nonexistent")
        assert t == get_system_template("default")

    def test_claude_system_prompt(self):
        prompt = get_claude_system_prompt("You are helpful.")
        assert "tool_call" in prompt
        assert "You are helpful." in prompt
        assert "read_file" in prompt


# ========== Audit Log ==========

class TestAuditLog:
    def test_log_records_execution(self, tmp_workspace):
        _, test_file = tmp_workspace
        with ALLOW_PATCH:
            execute_tool("read_file", {"path": str(test_file)})
        log = get_tool_log()
        assert len(log) > 0
        assert log[-1]["tool"] == "read_file"
        assert "elapsed_ms" in log[-1]

    def test_log_records_failure(self):
        execute_tool("read_file", {"path": "/nonexistent/file.txt"})
        assert get_tool_log()[-1]["tool"] == "read_file"


# ========== Unknown Tool ==========

class TestUnknownTool:
    def test_unknown_tool_returns_error(self):
        result = execute_tool("nonexistent_tool", {})
        assert "error" in result
        assert "Unknown" in result["error"]
