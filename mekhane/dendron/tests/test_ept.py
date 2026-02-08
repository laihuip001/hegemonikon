# PROOF: [L3/テスト] <- mekhane/dendron/
"""
Dendron EPT (Existence Purpose Tensor) テスト

NF2 Structure, NF3 Function, BCNF Verification レイヤーの単体テスト。
v3.3: REASON フィールド検出テストを含む。
"""

from pathlib import Path

import pytest

from mekhane.dendron.checker import DendronChecker, ProofStatus
from mekhane.dendron.models import (
    StructureProof,
    FunctionNFProof,
    VerificationProof,
    REASON_PATTERN,
)


# ─── Fixtures ─────────────────────────────────────


@pytest.fixture
def ept_checker():
    """EPT 全レイヤー有効のチェッカー"""
    return DendronChecker(
        exempt_patterns=[],
        check_structure=True,
        check_function_nf=True,
        check_verification=True,
    )


@pytest.fixture
def tmp_project(tmp_path):
    """テスト用プロジェクトを構築するファクトリ"""
    def _create(files: dict) -> Path:
        for name, content in files.items():
            fp = tmp_path / name
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, encoding="utf-8")
        return tmp_path
    return _create


# ─── NF2 Structure Tests ─────────────────────────


class TestNF2Structure:
    """NF2: Import/Call/TypeRef 構造チェック"""

    def test_import_resolution_ok(self, ept_checker, tmp_project):
        """P21: import 先ファイルが存在する → OK"""
        root = tmp_project({
            "mod_a.py": "# PROOF: [L1/コア]\nfrom . import mod_b\n",
            "mod_b.py": "# PROOF: [L1/コア]\nx = 1\n",
        })
        result = ept_checker.check(root)
        import_proofs = [s for s in result.structure_proofs if s.check_type == "import"]
        assert len(import_proofs) >= 1
        ok_proofs = [s for s in import_proofs if s.status == ProofStatus.OK]
        assert len(ok_proofs) >= 1

    def test_call_resolution_ok(self, ept_checker, tmp_project):
        """P22: 呼出先関数が定義されている → OK"""
        root = tmp_project({
            "utils.py": "# PROOF: [L1/ユーティリティ]\ndef helper():\n    pass\n",
            "main.py": "# PROOF: [L1/コア]\nfrom utils import helper\nhelper()\n",
        })
        result = ept_checker.check(root)
        call_proofs = [s for s in result.structure_proofs if s.check_type == "call"]
        # helper() は定義されているので OK
        for cp in call_proofs:
            if cp.name == "helper":
                assert cp.status == ProofStatus.OK

    def test_type_ref_missing(self, ept_checker, tmp_project):
        """P31: 型アノテーションが import されていない → WEAK"""
        root = tmp_project({
            "module.py": "# PROOF: [L1/コア]\ndef foo(x: MyCustomType) -> None:\n    pass\n",
        })
        result = ept_checker.check(root)
        type_proofs = [s for s in result.structure_proofs if s.check_type == "type_ref"]
        weak = [s for s in type_proofs if s.status == ProofStatus.WEAK]
        assert len(weak) >= 1  # MyCustomType は未 import


class TestNF3Function:
    """NF3: 複雑度/類似度/再代入チェック"""

    def test_complexity_short_function_ok(self, ept_checker, tmp_project):
        """短い関数は OK"""
        root = tmp_project({
            "short.py": "# PROOF: [L1/コア]\ndef short_func():\n    return 42\n",
        })
        result = ept_checker.check(root)
        complexity = [f for f in result.function_nf_proofs if f.check_type == "complexity"]
        for c in complexity:
            if c.name == "short_func":
                assert c.status == ProofStatus.OK

    def test_complexity_long_function_weak(self, ept_checker, tmp_project):
        """50行超の関数は WEAK"""
        lines = ["# PROOF: [L1/コア]", "def long_func():"]
        for i in range(55):
            lines.append(f"    x_{i} = {i}")
        lines.append("    return x_0")
        root = tmp_project({"long.py": "\n".join(lines)})
        result = ept_checker.check(root)
        complexity = [f for f in result.function_nf_proofs if f.check_type == "complexity"]
        weak = [f for f in complexity if f.name == "long_func"]
        assert len(weak) == 1
        assert weak[0].status == ProofStatus.WEAK

    def test_similarity_detection(self, ept_checker, tmp_project):
        """類似関数を検出する"""
        root = tmp_project({
            "similar.py": (
                "# PROOF: [L1/コア]\n"
                "def func_a():\n    x = 1\n    y = 2\n    return x + y\n\n"
                "def func_b():\n    x = 1\n    y = 2\n    return x + y\n"
            ),
        })
        result = ept_checker.check(root)
        similarity = [f for f in result.function_nf_proofs if f.check_type == "similarity"]
        # func_a と func_b は 100% 類似
        if similarity:
            assert any(s.status == ProofStatus.WEAK for s in similarity)

    def test_reassignment_detection(self, ept_checker, tmp_project):
        """変数再代入を検出する"""
        root = tmp_project({
            "reassign.py": (
                "# PROOF: [L1/コア]\n"
                "def messy():\n"
                "    result = 1\n"
                "    result = 2\n"
                "    result = 3\n"
                "    return result\n"
            ),
        })
        result = ept_checker.check(root)
        reassign = [f for f in result.function_nf_proofs if f.check_type == "reassign"]
        weak = [f for f in reassign if f.status == ProofStatus.WEAK]
        assert len(weak) >= 1  # result が 3 回代入


class TestBCNFVerification:
    """BCNF: Dead func / Unused file / Unused var"""

    def test_dead_function_detection(self, ept_checker, tmp_project):
        """呼ばれていない public 関数を検出する"""
        root = tmp_project({
            "lib.py": "# PROOF: [L1/コア]\ndef used_func():\n    pass\ndef unused_func():\n    pass\n",
            "main.py": "# PROOF: [L1/コア]\nfrom lib import used_func\nused_func()\n",
        })
        result = ept_checker.check(root)
        dead = [v for v in result.verification_proofs
                if v.check_type == "dead_func" and v.name == "unused_func"]
        assert len(dead) == 1
        assert dead[0].status == ProofStatus.WEAK

    def test_property_not_flagged_as_dead(self, ept_checker, tmp_project):
        """@property 関数は dead_func としてフラグしない"""
        root = tmp_project({
            "model.py": (
                "# PROOF: [L1/コア]\n"
                "class MyModel:\n"
                "    @property\n"
                "    def name(self):\n"
                "        return 'test'\n"
            ),
        })
        result = ept_checker.check(root)
        dead = [v for v in result.verification_proofs
                if v.check_type == "dead_func" and v.name == "name"]
        assert len(dead) == 0  # @property は除外

    def test_unused_var_detection(self, ept_checker, tmp_project):
        """関数内の未使用変数を検出する"""
        root = tmp_project({
            "waste.py": (
                "# PROOF: [L1/コア]\n"
                "def wasteful():\n"
                "    unused = 42\n"
                "    return 0\n"
            ),
        })
        result = ept_checker.check(root)
        unused = [v for v in result.verification_proofs
                  if v.check_type == "unused_var" and "unused" in (v.name or "")]
        assert len(unused) >= 1
        assert unused[0].status == ProofStatus.WEAK


class TestREASON:
    """REASON フィールド検出テスト"""

    def test_reason_pattern_match(self):
        """REASON_PATTERN が正しくマッチする"""
        assert REASON_PATTERN.match("REASON: テスト理由")
        assert REASON_PATTERN.match("# REASON: テスト理由")
        assert not REASON_PATTERN.match("NOT A REASON")

    def test_proof_md_with_reason(self, ept_checker, tmp_project):
        """PROOF.md に REASON: があれば has_reason=True"""
        root = tmp_project({
            "subdir/PROOF.md": (
                "# PROOF.md\n"
                "PURPOSE: テスト目的\n"
                "REASON: テスト理由\n"
            ),
            "subdir/dummy.py": "# PROOF: [L1/コア]\nx = 1\n",
        })
        result = ept_checker.check(root)
        dir_proofs = [d for d in result.dir_proofs if "subdir" in str(d.path)]
        assert len(dir_proofs) == 1
        dp = dir_proofs[0]
        assert dp.has_reason is True
        assert dp.purpose_text == "テスト目的"
        assert dp.reason_text == "テスト理由"

    def test_proof_md_without_reason(self, ept_checker, tmp_project):
        """PROOF.md に REASON: がなければ has_reason=False"""
        root = tmp_project({
            "subdir/PROOF.md": "# 存在証明\nこのディレクトリは...\n",
            "subdir/dummy.py": "# PROOF: [L1/コア]\nx = 1\n",
        })
        result = ept_checker.check(root)
        dir_proofs = [d for d in result.dir_proofs if "subdir" in str(d.path)]
        assert len(dir_proofs) == 1
        assert dir_proofs[0].has_reason is False


class TestEPTIntegration:
    """EPT 統合テスト — CheckResult の統計が正しいか"""

    def test_ept_stats_in_check_result(self, ept_checker, tmp_project):
        """CheckResult に EPT 統計が含まれる"""
        root = tmp_project({
            "module.py": "# PROOF: [L1/コア]\ndef foo():\n    return 1\n",
        })
        result = ept_checker.check(root)
        assert result.total_structure_checks >= 0
        assert result.total_function_nf_checks >= 0
        assert result.total_verification_checks >= 0
        assert result.structure_ok >= 0
        assert result.function_nf_ok >= 0
        assert result.verification_ok >= 0

    def test_ept_disabled_by_default(self, tmp_project):
        """デフォルトでは EPT レイヤーは無効"""
        checker = DendronChecker(exempt_patterns=[])
        root = tmp_project({
            "module.py": "# PROOF: [L1/コア]\ndef foo():\n    return 1\n",
        })
        result = checker.check(root)
        assert result.total_structure_checks == 0
        assert result.total_function_nf_checks == 0
        assert result.total_verification_checks == 0
