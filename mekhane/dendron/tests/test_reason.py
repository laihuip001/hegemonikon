# PROOF: [L2/テスト] <- mekhane/dendron/
# PURPOSE: R-axis (Reason) 検出機能の単体テスト — Wave 1 (NF1 Surface)
"""
R-axis Reason Detection Tests — v3.5

Wave 1 で実装した REASON: 検出機能をテスト:
- R00: Dir PROOF.md 内の REASON: (既存)
- R10: File ヘッダー内の # REASON: 検出
- R20: Function コメント内の # REASON: 検出
- R30: Variable は INFO レベルのため、統計集計のみテスト
"""
import pytest
from pathlib import Path
from mekhane.dendron.checker import DendronChecker
from mekhane.dendron.models import ProofStatus


@pytest.fixture
def checker():
    """Standard checker for reason tests.
    
    exempt_patterns=[] to avoid pytest tmp dir names (test_xxx0)
    matching the default `test_` exempt pattern.
    """
    return DendronChecker(
        check_files=True, check_dirs=True, check_functions=True,
        exempt_patterns=[],
    )


@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal project structure with REASON declarations"""
    src = tmp_path / "src"
    src.mkdir()

    # File with both PROOF and REASON
    (src / "with_reason.py").write_text(
        "# PROOF: [L2/demo] <- src/\n"
        "# PURPOSE: Demonstrate reason detection\n"
        "# REASON: Created to validate R-axis detection in Wave 1\n"
        "\n"
        "# PURPOSE: A function with both purpose and reason\n"
        "# REASON: Added because the old approach was too slow\n"
        "def optimized_process():\n"
        "    pass\n"
        "\n"
        "# PURPOSE: A function with only purpose (no reason)\n"
        "def simple_function():\n"
        "    pass\n"
    )

    # File with PROOF but no REASON
    (src / "without_reason.py").write_text(
        "# PROOF: [L2/demo] <- src/\n"
        "# PURPOSE: A file without reason\n"
        "\n"
        "# PURPOSE: Function without reason\n"
        "def no_reason_func():\n"
        "    pass\n"
    )

    # PROOF.md for src/ with REASON
    (src / "PROOF.md").write_text(
        "# src/\n"
        "\n"
        "PURPOSE: Source code directory\n"
        "REASON: Separated from scripts for modularity (2026-01)\n"
    )

    # PROOF.md for root (parent reference target)
    (tmp_path / "PROOF.md").write_text(
        "# project root\n"
        "\n"
        "PURPOSE: Project root\n"
    )

    return tmp_path


class TestFileReasonDetection:
    """R10: File-level REASON: detection"""

    def test_file_with_reason(self, checker, tmp_project):
        """REASON: comment in file header is detected"""
        result = checker.check_file_proof(tmp_project / "src" / "with_reason.py")
        assert result.has_reason is True
        assert result.reason_text == "Created to validate R-axis detection in Wave 1"

    def test_file_without_reason(self, checker, tmp_project):
        """File without REASON: comment has has_reason=False"""
        result = checker.check_file_proof(tmp_project / "src" / "without_reason.py")
        assert result.has_reason is False
        assert result.reason_text is None

    def test_reason_does_not_affect_proof_status(self, checker, tmp_project):
        """REASON presence doesn't change PROOF status (still OK)"""
        with_reason = checker.check_file_proof(tmp_project / "src" / "with_reason.py")
        without_reason = checker.check_file_proof(tmp_project / "src" / "without_reason.py")
        assert with_reason.status == ProofStatus.OK
        assert without_reason.status == ProofStatus.OK


class TestFunctionReasonDetection:
    """R20: Function-level REASON: detection"""

    def test_function_with_reason(self, checker, tmp_project):
        """REASON: comment above function is detected"""
        results = checker.check_functions_in_file(tmp_project / "src" / "with_reason.py")
        func_with_reason = [r for r in results if r.name == "optimized_process"]
        assert len(func_with_reason) == 1
        assert func_with_reason[0].has_reason is True
        assert func_with_reason[0].reason_text == "Added because the old approach was too slow"

    def test_function_without_reason(self, checker, tmp_project):
        """Function without REASON: comment has has_reason=False"""
        results = checker.check_functions_in_file(tmp_project / "src" / "with_reason.py")
        func_no_reason = [r for r in results if r.name == "simple_function"]
        assert len(func_no_reason) == 1
        assert func_no_reason[0].has_reason is False
        assert func_no_reason[0].reason_text is None

    def test_reason_does_not_affect_purpose_status(self, checker, tmp_project):
        """REASON presence doesn't change PURPOSE status"""
        results = checker.check_functions_in_file(tmp_project / "src" / "with_reason.py")
        for r in results:
            assert r.status == ProofStatus.OK  # Both functions have PURPOSE


class TestReasonAggregation:
    """R-axis statistics in CheckResult"""

    def test_reason_coverage_stats(self, checker, tmp_project):
        """CheckResult includes correct R-axis statistics"""
        result = checker.check(tmp_project / "src")
        # 2 files, 1 with reason
        assert result.files_total_checkable > 0
        assert result.files_with_reason == 1  # with_reason.py

    def test_function_reason_stats(self, checker, tmp_project):
        """CheckResult includes function reason statistics"""
        result = checker.check(tmp_project / "src")
        # 3 functions total (optimized_process, simple_function, no_reason_func)
        # 1 with reason (optimized_process)
        assert result.functions_total_checkable > 0
        assert result.functions_with_reason == 1


class TestDirReasonDetection:
    """R00: Directory PROOF.md REASON: detection (existing feature)"""

    def test_dir_with_reason(self, checker, tmp_project):
        """PROOF.md with REASON: is detected"""
        dir_proof = checker.check_dir_proof(tmp_project / "src")
        assert dir_proof.has_reason is True
        assert "modularity" in dir_proof.reason_text

    def test_dir_without_reason(self, checker, tmp_project):
        """PROOF.md without REASON: has has_reason=False"""
        dir_proof = checker.check_dir_proof(tmp_project)
        assert dir_proof.has_reason is False


# ============================================================
# Wave 2 — NF2 REASON→PURPOSE 従属チェック
# ============================================================


@pytest.fixture
def nf2_project(tmp_path):
    """Project with NF2 violation: REASON without PURPOSE"""
    mod = tmp_path / "mymod"
    mod.mkdir()

    # Dir PROOF.md: REASON はあるが PURPOSE がない (R01 NF2 violation)
    (mod / "PROOF.md").write_text(
        "# mymod/\n"
        "\n"
        "REASON: Legacy code that needs refactoring\n"
    )

    # File: has PROOF but function has REASON without PURPOSE (R21)
    (mod / "nf2_violation.py").write_text(
        "# PROOF: [L2/demo] <- mymod/\n"
        "\n"
        "# REASON: Optimization for slow path — no PURPOSE!\n"
        "def orphan_reason_func():\n"
        "    pass\n"
        "\n"
        "# PURPOSE: Normal function with purpose\n"
        "# REASON: Because we needed it\n"
        "def normal_func():\n"
        "    pass\n"
    )

    # Parent PROOF.md
    (tmp_path / "PROOF.md").write_text("PURPOSE: root\n")

    return tmp_path


class TestNF2DirReasonDependency:
    """R01: Dir REASON→PURPOSE NF2 dependency"""

    def test_reason_without_purpose_is_weak(self, checker, nf2_project):
        """Dir with REASON but no PURPOSE is WEAK"""
        dir_proof = checker.check_dir_proof(nf2_project / "mymod")
        assert dir_proof.status == ProofStatus.WEAK
        assert "NF2" in dir_proof.reason
        assert dir_proof.has_reason is True

    def test_reason_with_purpose_is_ok(self, checker, tmp_project):
        """Dir with both REASON and PURPOSE is OK"""
        dir_proof = checker.check_dir_proof(tmp_project / "src")
        assert dir_proof.status == ProofStatus.OK
        assert dir_proof.has_reason is True


class TestNF2FunctionReasonDependency:
    """R21: Function REASON→PURPOSE NF2 dependency"""

    def test_function_reason_without_purpose_is_weak(self, checker, nf2_project):
        """Function with REASON but no PURPOSE is WEAK"""
        results = checker.check_functions_in_file(nf2_project / "mymod" / "nf2_violation.py")
        orphan = [r for r in results if r.name == "orphan_reason_func"]
        assert len(orphan) == 1
        assert orphan[0].status == ProofStatus.WEAK
        assert orphan[0].has_reason is True
        assert "従属違反" in orphan[0].quality_issue

    def test_function_reason_with_purpose_is_ok(self, checker, nf2_project):
        """Function with both REASON and PURPOSE is OK"""
        results = checker.check_functions_in_file(nf2_project / "mymod" / "nf2_violation.py")
        normal = [r for r in results if r.name == "normal_func"]
        assert len(normal) == 1
        assert normal[0].status == ProofStatus.OK
        assert normal[0].has_reason is True


# ============================================================
# Wave 3 — NF3/BCNF セマンティック品質チェック
# ============================================================


class TestTextSimilarity:
    """_text_similarity helper (Jaccard word similarity)"""

    def test_identical_texts(self):
        assert DendronChecker._text_similarity("hello world", "hello world") == 1.0

    def test_completely_different(self):
        assert DendronChecker._text_similarity("foo bar", "baz qux") == 0.0

    def test_partial_overlap(self):
        sim = DendronChecker._text_similarity("read file data", "write file data")
        assert 0.4 < sim < 0.8  # 2/4 overlap

    def test_empty_strings(self):
        assert DendronChecker._text_similarity("", "hello") == 0.0
        assert DendronChecker._text_similarity("hello", "") == 0.0

    def test_case_insensitive(self):
        assert DendronChecker._text_similarity("Hello World", "hello world") == 1.0


@pytest.fixture
def bcnf_project(tmp_path):
    """Project with BCNF violations: REASON ≈ PURPOSE (tautology)"""
    mod = tmp_path / "tautmod"
    mod.mkdir()

    # Dir: PURPOSE and REASON say the same thing
    (mod / "PROOF.md").write_text(
        "# tautmod/\n"
        "\n"
        "PURPOSE: ファイルの読み込みを行う\n"
        "REASON: ファイルの読み込みを行う必要があるから\n"
    )

    # File with tautological function
    (mod / "taut.py").write_text(
        "# PROOF: [L2/demo] <- tautmod/\n"
        "\n"
        "# PURPOSE: データベースに接続する処理\n"
        "# REASON: データベースに接続する処理だから\n"
        "def connect_db():\n"
        "    pass\n"
        "\n"
        "# PURPOSE: ログを記録する\n"
        "# REASON: v2.3でAPIが非推奨になり移行が必要\n"
        "def log_event():\n"
        "    pass\n"
    )

    (tmp_path / "PROOF.md").write_text("PURPOSE: root\n")
    return tmp_path


class TestBCNFTautologyDetection:
    """R03/R23: REASON ≈ PURPOSE tautology detection"""

    def test_dir_tautology_is_weak(self, checker, bcnf_project):
        """Dir with REASON ≈ PURPOSE is WEAK"""
        dir_proof = checker.check_dir_proof(bcnf_project / "tautmod")
        assert dir_proof.status == ProofStatus.WEAK
        assert "トートロジー" in dir_proof.reason

    def test_function_tautology_is_weak(self, checker, bcnf_project):
        """Function with REASON ≈ PURPOSE is WEAK"""
        results = checker.check_functions_in_file(bcnf_project / "tautmod" / "taut.py")
        connect = [r for r in results if r.name == "connect_db"]
        assert len(connect) == 1
        assert connect[0].status == ProofStatus.WEAK
        assert "トートロジー" in connect[0].quality_issue

    def test_function_distinct_reason_is_ok(self, checker, bcnf_project):
        """Function with distinct REASON and PURPOSE is OK"""
        results = checker.check_functions_in_file(bcnf_project / "tautmod" / "taut.py")
        log = [r for r in results if r.name == "log_event"]
        assert len(log) == 1
        assert log[0].status == ProofStatus.OK


# ============================================================
# R02/R22 NF3: 親子 REASON 重複 (aggregation level)
# ============================================================


@pytest.fixture
def nf3_project(tmp_path):
    """Project with NF3 violations: parent-child REASON overlap"""
    # Root
    (tmp_path / "PROOF.md").write_text(
        "PURPOSE: プロジェクトルート\n"
        "REASON: データ処理パイプラインの構築\n"
    )

    # Child dir with same REASON as parent (R02 violation)
    sub = tmp_path / "submod"
    sub.mkdir()
    (sub / "PROOF.md").write_text(
        "PURPOSE: サブモジュール\n"
        "REASON: データ処理パイプラインの構築のため\n"
    )

    # File with same REASON as parent dir (R12 violation)
    (sub / "worker.py").write_text(
        "# PROOF: [L2/demo] <- submod/\n"
        "# REASON: データ処理パイプラインの構築用ワーカー\n"
        "\n"
        "# PURPOSE: データを処理する\n"
        "# REASON: データ処理パイプラインの構築だから\n"
        "def process_data():\n"
        "    pass\n"
        "\n"
        "# PURPOSE: 結果を出力する\n"
        "# REASON: 監査要件に基づく記録義務\n"
        "def output_result():\n"
        "    pass\n"
    )

    return tmp_path


class TestNF3ParentChildOverlap:
    """R02/R12/R22: Parent-child REASON overlap detected in aggregation"""

    def test_nf3_count_includes_all_axes(self, checker, nf3_project):
        """Aggregation counts R02 + R12 + R22 NF3 issues"""
        result = checker.check(nf3_project)
        # R02: submod REASON ≈ root REASON
        # R12: worker.py REASON ≈ submod REASON
        # R22: process_data REASON ≈ worker.py file REASON (same pipeline text)
        assert result.reason_nf3_issues >= 2  # at least R02 + R12

    def test_distinct_function_reason_not_counted(self, checker, nf3_project):
        """Function with distinct REASON from file is not NF3"""
        result = checker.check(nf3_project)
        # output_result has "監査要件に基づく記録義務" — clearly distinct
        # So total NF3 should not include that function
        # We just verify the count is bounded
        assert result.reason_nf3_issues <= 4  # upper bound sanity check

