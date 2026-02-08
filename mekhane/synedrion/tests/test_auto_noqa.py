#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/synedrion/tests/
# PURPOSE: Synedrion auto_noqa の包括テスト
"""Synedrion auto_noqa Tests"""

import pytest
from pathlib import Path
from mekhane.synedrion.auto_noqa import parse_audit_file, find_file, insert_noqa


# ── parse_audit_file ─────────────────────

class TestParseAuditFile:
    """監査出力パーサーのテスト"""

    @pytest.fixture
    def audit_file(self, tmp_path):
        f = tmp_path / "audit.txt"
        f.write_text("""# Audit Report

## validators.py
- ⚪ **AI-001** L42: Missing docstring
- ⚪ **AI-002** L55: Bad naming

## tracer.py
- ⚪ **AI-003** L10: Unused import
""")
        return f

    def test_parse_finds_files(self, audit_file):
        result = parse_audit_file(audit_file)
        assert "validators.py" in result
        assert "tracer.py" in result

    def test_parse_finds_issues(self, audit_file):
        result = parse_audit_file(audit_file)
        assert len(result["validators.py"]) == 2
        assert len(result["tracer.py"]) == 1

    def test_parse_line_numbers(self, audit_file):
        result = parse_audit_file(audit_file)
        lines = [ln for ln, _ in result["validators.py"]]
        assert 42 in lines
        assert 55 in lines

    def test_parse_issue_codes(self, audit_file):
        result = parse_audit_file(audit_file)
        codes = [code for _, code in result["validators.py"]]
        assert "AI-001" in codes
        assert "AI-002" in codes

    def test_parse_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        result = parse_audit_file(f)
        assert len(result) == 0

    def test_parse_no_issues(self, tmp_path):
        f = tmp_path / "clean.txt"
        f.write_text("# Audit Report\n\n## clean.py\nNo issues found.\n")
        result = parse_audit_file(f)
        assert len(result) == 0


# ── find_file ────────────────────────────

class TestFindFile:
    """ファイル検索のテスト"""

    def test_find_direct(self, tmp_path):
        target = tmp_path / "test.py"
        target.write_text("pass")
        result = find_file("test.py", tmp_path)
        assert result == target

    def test_find_recursive(self, tmp_path):
        sub = tmp_path / "sub" / "dir"
        sub.mkdir(parents=True)
        target = sub / "deep.py"
        target.write_text("pass")
        result = find_file("deep.py", tmp_path)
        assert result == target

    def test_find_nonexistent(self, tmp_path):
        result = find_file("nonexistent.py", tmp_path)
        assert result is None


# ── insert_noqa ──────────────────────────

class TestInsertNoqa:
    """noqa コメント挿入のテスト"""

    @pytest.fixture
    def source_file(self, tmp_path):
        f = tmp_path / "source.py"
        f.write_text("import os\nimport sys\ndef foo():\n    pass\n")
        return f

    def test_insert_single(self, source_file):
        count = insert_noqa(source_file, [(1, "AI-001")])
        assert count == 1
        content = source_file.read_text()
        assert "# noqa: AI-001" in content

    def test_insert_multiple_lines(self, source_file):
        count = insert_noqa(source_file, [(1, "AI-001"), (2, "AI-002")])
        assert count == 2

    def test_insert_same_line_multiple_codes(self, source_file):
        count = insert_noqa(source_file, [(1, "AI-001"), (1, "AI-002")])
        assert count == 1
        content = source_file.read_text()
        assert "AI-001" in content and "AI-002" in content

    def test_skip_existing_noqa(self, tmp_path):
        f = tmp_path / "already.py"
        f.write_text("import os  # noqa: AI-001\n")
        count = insert_noqa(f, [(1, "AI-002")])
        assert count == 0

    def test_skip_nonexistent_file(self, tmp_path):
        count = insert_noqa(tmp_path / "nope.py", [(1, "AI-001")])
        assert count == 0

    def test_out_of_range(self, source_file):
        count = insert_noqa(source_file, [(999, "AI-001")])
        assert count == 0

    def test_preserves_content(self, source_file):
        insert_noqa(source_file, [(3, "AI-001")])
        content = source_file.read_text()
        assert "def foo():" in content
        assert "# noqa: AI-001" in content
