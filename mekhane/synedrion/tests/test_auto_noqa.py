#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/synedrion/tests/
# PURPOSE: Synedrion auto_noqa の包括テスト
"""Synedrion auto_noqa Tests"""

import pytest
from pathlib import Path
from mekhane.synedrion.auto_noqa import parse_audit_file, find_file, insert_noqa


# ── parse_audit_file ─────────────────────

# PURPOSE: Test suite validating parse audit file correctness
class TestParseAuditFile:
    """監査出力パーサーのテスト"""

    # PURPOSE: Verify audit file behaves correctly
    @pytest.fixture
    def audit_file(self, tmp_path):
        """Verify audit file behavior."""
        f = tmp_path / "audit.txt"
        f.write_text("""# Audit Report

## validators.py
- ⚪ **AI-001** L42: Missing docstring
- ⚪ **AI-002** L55: Bad naming

## tracer.py
- ⚪ **AI-003** L10: Unused import
""")
        return f

    # PURPOSE: Verify parse finds files behaves correctly
    def test_parse_finds_files(self, audit_file):
        """Verify parse finds files behavior."""
        result = parse_audit_file(audit_file)
        assert "validators.py" in result
        assert "tracer.py" in result

    # PURPOSE: Verify parse finds issues behaves correctly
    def test_parse_finds_issues(self, audit_file):
        """Verify parse finds issues behavior."""
        result = parse_audit_file(audit_file)
        assert len(result["validators.py"]) == 2
        assert len(result["tracer.py"]) == 1

    # PURPOSE: Verify parse line numbers behaves correctly
    def test_parse_line_numbers(self, audit_file):
        """Verify parse line numbers behavior."""
        result = parse_audit_file(audit_file)
        lines = [ln for ln, _ in result["validators.py"]]
        assert 42 in lines
        assert 55 in lines

    # PURPOSE: Verify parse issue codes behaves correctly
    def test_parse_issue_codes(self, audit_file):
        """Verify parse issue codes behavior."""
        result = parse_audit_file(audit_file)
        codes = [code for _, code in result["validators.py"]]
        assert "AI-001" in codes
        assert "AI-002" in codes

    # PURPOSE: Verify parse empty file behaves correctly
    def test_parse_empty_file(self, tmp_path):
        """Verify parse empty file behavior."""
        f = tmp_path / "empty.txt"
        f.write_text("")
        result = parse_audit_file(f)
        assert len(result) == 0

    # PURPOSE: Verify parse no issues behaves correctly
    def test_parse_no_issues(self, tmp_path):
        """Verify parse no issues behavior."""
        f = tmp_path / "clean.txt"
        f.write_text("# Audit Report\n\n## clean.py\nNo issues found.\n")
        result = parse_audit_file(f)
        assert len(result) == 0


# ── find_file ────────────────────────────

# PURPOSE: Test suite validating find file correctness
class TestFindFile:
    """ファイル検索のテスト"""

    # PURPOSE: Verify find direct behaves correctly
    def test_find_direct(self, tmp_path):
        """Verify find direct behavior."""
        target = tmp_path / "test.py"
        target.write_text("pass")
        result = find_file("test.py", tmp_path)
        assert result == target

    # PURPOSE: Verify find recursive behaves correctly
    def test_find_recursive(self, tmp_path):
        """Verify find recursive behavior."""
        sub = tmp_path / "sub" / "dir"
        sub.mkdir(parents=True)
        target = sub / "deep.py"
        target.write_text("pass")
        result = find_file("deep.py", tmp_path)
        assert result == target

    # PURPOSE: Verify find nonexistent behaves correctly
    def test_find_nonexistent(self, tmp_path):
        """Verify find nonexistent behavior."""
        result = find_file("nonexistent.py", tmp_path)
        assert result is None


# ── insert_noqa ──────────────────────────

# PURPOSE: Test suite validating insert noqa correctness
class TestInsertNoqa:
    """noqa コメント挿入のテスト"""

    # PURPOSE: Verify source file behaves correctly
    @pytest.fixture
    def source_file(self, tmp_path):
        """Verify source file behavior."""
        f = tmp_path / "source.py"
        f.write_text("import os\nimport sys\ndef foo():\n    pass\n")
        return f

    # PURPOSE: Verify insert single behaves correctly
    def test_insert_single(self, source_file):
        """Verify insert single behavior."""
        count = insert_noqa(source_file, [(1, "AI-001")])
        assert count == 1
        content = source_file.read_text()
        assert "# noqa: AI-001" in content

    # PURPOSE: Verify insert multiple lines behaves correctly
    def test_insert_multiple_lines(self, source_file):
        """Verify insert multiple lines behavior."""
        count = insert_noqa(source_file, [(1, "AI-001"), (2, "AI-002")])
        assert count == 2

    # PURPOSE: Verify insert same line multiple codes behaves correctly
    def test_insert_same_line_multiple_codes(self, source_file):
        """Verify insert same line multiple codes behavior."""
        count = insert_noqa(source_file, [(1, "AI-001"), (1, "AI-002")])
        assert count == 1
        content = source_file.read_text()
        assert "AI-001" in content and "AI-002" in content

    # PURPOSE: Verify skip existing noqa behaves correctly
    def test_skip_existing_noqa(self, tmp_path):
        """Verify skip existing noqa behavior."""
        f = tmp_path / "already.py"
        f.write_text("import os  # noqa: AI-001\n")
        count = insert_noqa(f, [(1, "AI-002")])
        assert count == 0

    # PURPOSE: Verify skip nonexistent file behaves correctly
    def test_skip_nonexistent_file(self, tmp_path):
        """Verify skip nonexistent file behavior."""
        count = insert_noqa(tmp_path / "nope.py", [(1, "AI-001")])
        assert count == 0

    # PURPOSE: Verify out of range behaves correctly
    def test_out_of_range(self, source_file):
        """Verify out of range behavior."""
        count = insert_noqa(source_file, [(999, "AI-001")])
        assert count == 0

    # PURPOSE: Verify preserves content behaves correctly
    def test_preserves_content(self, source_file):
        """Verify preserves content behavior."""
        insert_noqa(source_file, [(3, "AI-001")])
        content = source_file.read_text()
        assert "def foo():" in content
        assert "# noqa: AI-001" in content
