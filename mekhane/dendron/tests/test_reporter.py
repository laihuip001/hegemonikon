# PROOF: [L3/テスト] <- mekhane/dendron/
"""
Dendron Reporter テスト

reporter.py の各出力形式 (TEXT, MARKDOWN, CI, JSON) が
L1/L2 統計を正しく出力することを検証する。
"""

import io
import json
import pytest

from mekhane.dendron.checker import CheckResult, FileProof, ProofStatus
from mekhane.dendron.reporter import DendronReporter, ReportFormat


# ── Fixtures ──────────────────────────────────────

# PURPOSE: テスト用の CheckResult を生成し、各形式の出力検証に使う
@pytest.fixture
def result_passing():
    """L2 Purpose 統計を含む合格結果"""
    return CheckResult(
        total_files=5,
        files_with_proof=4,
        files_missing_proof=0,
        files_invalid_proof=0,
        files_exempt=1,
        files_orphan=0,
        file_proofs=[],
        dir_proofs=[],
        total_functions=10,
        functions_with_purpose=8,
        functions_missing_purpose=0,
        functions_weak_purpose=2,
        level_stats={"L1": 1, "L2": 3},
    )


# PURPOSE: 不合格の CheckResult を生成し、FAIL 出力の検証に使う
@pytest.fixture
def result_failing():
    """不合格結果"""
    from pathlib import Path

    return CheckResult(
        total_files=3,
        files_with_proof=1,
        files_missing_proof=2,
        files_invalid_proof=0,
        files_exempt=0,
        files_orphan=0,
        file_proofs=[
            FileProof(path=Path("foo.py"), status=ProofStatus.MISSING),
            FileProof(path=Path("bar.py"), status=ProofStatus.MISSING),
        ],
        dir_proofs=[],
        total_functions=5,
        functions_with_purpose=3,
        functions_missing_purpose=1,
        functions_weak_purpose=1,
    )


# ── TEXT format ───────────────────────────────────

class TestTextFormat:
    """TEXT 形式の出力検証"""

    # PURPOSE: TEXT 形式で L2 Purpose セクションが出力されることを検証する
    def test_includes_purpose_section(self, result_passing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_passing, ReportFormat.TEXT)
        output = buf.getvalue()

        assert "L2 Purpose:" in output
        assert "OK:      8" in output
        assert "Weak:    2" in output
        assert "Missing: 0" in output

    # PURPOSE: TEXT 形式で PASS/FAIL が正しく表示されることを検証する
    def test_pass_indicator(self, result_passing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_passing, ReportFormat.TEXT)
        assert "✅ PASS" in buf.getvalue()

    # PURPOSE: TEXT 形式で FAIL 時に missing ファイルが表示されることを検証する
    def test_fail_indicator(self, result_failing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_failing, ReportFormat.TEXT)
        output = buf.getvalue()
        assert "❌ FAIL" in output
        assert "Missing PROOF:" in output


# ── CI format ────────────────────────────────────

class TestCIFormat:
    """CI 形式の出力検証"""

    # PURPOSE: CI 形式で Purpose サマリー行が出力されることを検証する
    def test_includes_purpose_summary(self, result_passing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_passing, ReportFormat.CI)
        output = buf.getvalue()

        assert "Purpose:" in output
        assert "8 ok" in output
        assert "2 weak" in output

    # PURPOSE: CI 形式で FAIL 時にファイルリストが出力されることを検証する
    def test_fail_lists_files(self, result_failing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_failing, ReportFormat.CI)
        output = buf.getvalue()
        assert "❌" in output
        assert "2 files missing" in output


# ── JSON format ──────────────────────────────────

class TestJSONFormat:
    """JSON 形式の出力検証"""

    # PURPOSE: JSON 形式で purpose オブジェクトが含まれることを検証する
    def test_includes_purpose_object(self, result_passing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_passing, ReportFormat.JSON)
        data = json.loads(buf.getvalue())

        assert "purpose" in data
        assert data["purpose"]["ok"] == 8
        assert data["purpose"]["weak"] == 2
        assert data["purpose"]["missing"] == 0
        assert data["purpose"]["total"] == 10

    # PURPOSE: JSON 形式で is_passing が正しく出力されることを検証する
    def test_is_passing_field(self, result_passing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_passing, ReportFormat.JSON)
        data = json.loads(buf.getvalue())
        assert data["is_passing"] is True

    # PURPOSE: JSON 形式で不合格時の missing_files が正しく出力されることを検証する
    def test_failing_missing_files(self, result_failing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_failing, ReportFormat.JSON)
        data = json.loads(buf.getvalue())
        assert data["is_passing"] is False
        assert len(data["missing_files"]) == 2


# ── Markdown format ──────────────────────────────

class TestMarkdownFormat:
    """Markdown 形式の出力検証"""

    # PURPOSE: Markdown 形式で L2 Purpose Quality テーブルが出力されることを検証する
    def test_includes_purpose_table(self, result_passing):
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result_passing, ReportFormat.MARKDOWN)
        output = buf.getvalue()

        assert "## L2 Purpose Quality" in output
        assert "| OK | 8 |" in output
        assert "| Weak | 2 |" in output


# ── Edge cases ───────────────────────────────────

class TestEdgeCases:
    """エッジケースの検証"""

    # PURPOSE: function が 0 件のとき Purpose セクションが出力されないことを検証する
    def test_no_functions_no_purpose_section(self):
        result = CheckResult(
            total_files=1,
            files_with_proof=1,
            files_missing_proof=0,
            files_invalid_proof=0,
            files_exempt=0,
            files_orphan=0,
            file_proofs=[],
            dir_proofs=[],
            total_functions=0,
            functions_with_purpose=0,
            functions_missing_purpose=0,
            functions_weak_purpose=0,
        )
        buf = io.StringIO()
        reporter = DendronReporter(output=buf)
        reporter.report(result, ReportFormat.TEXT)
        assert "L2 Purpose:" not in buf.getvalue()

    # PURPOSE: coverage 計算で exempt ファイルが分母から除外されることを検証する
    def test_coverage_excludes_exempt(self):
        result = CheckResult(
            total_files=3,
            files_with_proof=2,
            files_missing_proof=0,
            files_invalid_proof=0,
            files_exempt=1,
            files_orphan=0,
            file_proofs=[],
            dir_proofs=[],
        )
        assert result.coverage == 100.0
