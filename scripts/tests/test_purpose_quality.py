#!/usr/bin/env python3
# PROOF: [L2/テスト] <- scripts/tests/
# PURPOSE: purpose_quality_check.py のテスト
"""PURPOSE Quality Checker Tests"""

import pytest
from pathlib import Path

# Import directly (scripts/ 配下なので sys.path 調整)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from purpose_quality_check import check_file, DEGENERATE_PATTERNS


class TestDegeneratePatterns:
    """形骸化パターン定義テスト"""

    def test_patterns_exist(self):
        assert len(DEGENERATE_PATTERNS) > 0

    def test_patterns_are_tuples(self):
        for p in DEGENERATE_PATTERNS:
            assert isinstance(p, tuple)
            assert len(p) == 2

    def test_pattern_hints_non_empty(self):
        for pattern, hint in DEGENERATE_PATTERNS:
            assert len(hint) > 0


class TestCheckFile:
    """check_file 関数テスト"""

    def test_clean_file(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text(
            "# PURPOSE: 統一論文スキーマとして異なるソースからの論文を正規化する\n"
            "class Paper:\n"
            "    pass\n",
            encoding="utf-8",
        )
        issues = check_file(f)
        assert issues == []

    def test_degenerate_init(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text(
            "# PURPOSE: 内部処理: init__\n"
            "def __init__(self):\n"
            "    pass\n",
            encoding="utf-8",
        )
        issues = check_file(f)
        assert len(issues) >= 1
        assert issues[0]["line"] == 1
        assert "init__" in issues[0]["content"]

    def test_degenerate_repr(self, tmp_path):
        f = tmp_path / "repr.py"
        f.write_text("# PURPOSE: 内部処理: repr__\n", encoding="utf-8")
        issues = check_file(f)
        assert len(issues) >= 1

    def test_degenerate_function(self, tmp_path):
        f = tmp_path / "func.py"
        f.write_text("# PURPOSE: 関数: calculate\n", encoding="utf-8")
        issues = check_file(f)
        assert len(issues) >= 1
        assert "calculate" in issues[0]["content"]

    def test_degenerate_property(self, tmp_path):
        f = tmp_path / "prop.py"
        f.write_text("# PURPOSE: 取得: name\n", encoding="utf-8")
        issues = check_file(f)
        assert len(issues) >= 1

    def test_issue_structure(self, tmp_path):
        f = tmp_path / "check.py"
        f.write_text("# PURPOSE: 内部処理: str__\n", encoding="utf-8")
        issues = check_file(f)
        assert len(issues) == 1
        issue = issues[0]
        assert "file" in issue
        assert "line" in issue
        assert "content" in issue
        assert "hint" in issue

    def test_multiple_issues(self, tmp_path):
        f = tmp_path / "multi.py"
        f.write_text(
            "# PURPOSE: 内部処理: init__\n"
            "# PURPOSE: 良い注釈\n"
            "# PURPOSE: 関数: foo\n",
            encoding="utf-8",
        )
        issues = check_file(f)
        assert len(issues) == 2  # init__ + foo

    def test_nonexistent_file(self, tmp_path):
        f = tmp_path / "nope.py"
        with pytest.raises(FileNotFoundError):
            check_file(f)

    def test_binary_file(self, tmp_path):
        f = tmp_path / "binary.py"
        f.write_bytes(b"\x80\x81\x82\x83")
        issues = check_file(f)
        assert issues == []

    def test_mixed_good_and_bad(self, tmp_path):
        f = tmp_path / "mixed.py"
        f.write_text(
            "# PURPOSE: 統一論文スキーマ — 良い注釈\n"
            "# PURPOSE: 内部処理: init__\n"
            "# PURPOSE: FEP に基づく認知評価を実行する — 良い注釈\n",
            encoding="utf-8",
        )
        issues = check_file(f)
        assert len(issues) == 1

    def test_japanese_content(self, tmp_path):
        f = tmp_path / "jp.py"
        f.write_text(
            "# PURPOSE: 統一論文スキーマ\n"
            "class Paper:\n"
            "    # PURPOSE: 重複排除用プライマリキー\n"
            "    pass\n",
            encoding="utf-8",
        )
        issues = check_file(f)
        assert issues == []

    def test_line_numbers_correct(self, tmp_path):
        f = tmp_path / "lines.py"
        f.write_text(
            "# Good line 1\n"
            "# Good line 2\n"
            "# PURPOSE: 内部処理: init__\n"
            "# Good line 4\n",
            encoding="utf-8",
        )
        issues = check_file(f)
        assert issues[0]["line"] == 3

    def test_internal_method_generic(self, tmp_path):
        f = tmp_path / "method.py"
        f.write_text("# PURPOSE: 内部処理: configure\n", encoding="utf-8")
        issues = check_file(f)
        assert len(issues) >= 1
        assert "WHY" in issues[0]["hint"]
