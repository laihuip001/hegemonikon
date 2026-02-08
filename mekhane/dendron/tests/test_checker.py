# PROOF: [L3/テスト] <- mekhane/dendron/
"""
Dendron Checker テスト

checker.py の各メソッドの単体テスト。
v2.6: Purpose 品質チェック (WEAK 検出) のテストを含む。
"""

from pathlib import Path

import pytest

from mekhane.dendron.checker import (
    DendronChecker,
    ProofStatus,
    ProofLevel,
    FileProof,
    FunctionProof,
    VariableProof,
    CheckResult,
    PURPOSE_PATTERN,
    WEAK_PURPOSE_PATTERNS,
)


# ─── Fixtures ─────────────────────────────────────


# PURPOSE: 標準チェッカー (exempt パターンなし)。
@pytest.fixture
def checker():
    """標準チェッカー (exempt パターンなし)。
    pytest の tmp ディレクトリ名に 'test_' が含まれるため、
    L1/L2 テストでは exempt パターンを無効化する。"""
    return DendronChecker(exempt_patterns=[])


# PURPOSE: 除外パターン付きチェッカー (exemption テスト専用)
@pytest.fixture
def checker_with_exemptions():
    """除外パターン付きチェッカー (exemption テスト専用)"""
    return DendronChecker()


# PURPOSE: 一時 Python ファイルを生成するファクトリ
@pytest.fixture
def tmp_py_file(tmp_path):
    """一時 Python ファイルを生成するファクトリ"""
    def _create(content: str, name: str = "sample_module.py") -> Path:
        f = tmp_path / name
        f.write_text(content, encoding="utf-8")
        return f
    return _create


# ─── L1: PROOF Header Tests ──────────────────────


# PURPOSE: L1 ファイル PROOF ヘッダーのテスト
class TestFileProof:
    """L1 ファイル PROOF ヘッダーのテスト"""

    # PURPOSE: valid_proof_with_parent をテストする
    def test_valid_proof_with_parent(self, checker, tmp_py_file):
        f = tmp_py_file('# PROOF: [L2/インフラ] <- mekhane/dendron/\n"Module docstring"\n')
        result = checker.check_file_proof(f)
        assert result.status == ProofStatus.OK
        assert result.level == ProofLevel.L2
        assert result.parent == "mekhane/dendron/"

    # PURPOSE: missing_proof をテストする
    def test_missing_proof(self, checker, tmp_py_file):
        f = tmp_py_file('"Module without proof"\ndef foo():\n    pass\n')
        result = checker.check_file_proof(f)
        assert result.status == ProofStatus.MISSING

    # PURPOSE: orphan_proof をテストする
    def test_orphan_proof(self, checker, tmp_py_file):
        f = tmp_py_file('# PROOF: [L1/定理]\n"Module with proof but no parent"\n')
        result = checker.check_file_proof(f)
        assert result.status == ProofStatus.ORPHAN

    # PURPOSE: exempt_pycache をテストする
    def test_exempt_pycache(self, checker_with_exemptions):
        path = Path("__pycache__/something.pyc")
        assert checker_with_exemptions.is_exempt(path) is True

    # PURPOSE: exempt_venv をテストする
    def test_exempt_venv(self, checker_with_exemptions):
        path = Path(".venv/lib/site-packages/foo.py")
        assert checker_with_exemptions.is_exempt(path) is True

    # PURPOSE: not_exempt_normal をテストする
    def test_not_exempt_normal(self, checker_with_exemptions):
        path = Path("mekhane/dendron/checker.py")
        assert checker_with_exemptions.is_exempt(path) is False


# ─── L1: Parent Validation Tests ─────────────────


# PURPOSE: 親参照の検証テスト
class TestParentValidation:
    """親参照の検証テスト"""

    # PURPOSE: special_parent_fep をテストする
    def test_special_parent_fep(self, checker):
        valid, _ = checker.validate_parent("FEP")
        assert valid is True

    # PURPOSE: special_parent_external をテストする
    def test_special_parent_external(self, checker):
        valid, _ = checker.validate_parent("external")
        assert valid is True

    # PURPOSE: path_traversal_rejected をテストする
    def test_path_traversal_rejected(self, checker):
        valid, reason = checker.validate_parent("../../etc/passwd")
        assert valid is False
        assert "パストラバーサル" in reason

    # PURPOSE: absolute_path_rejected をテストする
    def test_absolute_path_rejected(self, checker):
        valid, reason = checker.validate_parent("/etc/passwd")
        assert valid is False
        assert "絶対パス" in reason

    # PURPOSE: too_long_path_rejected をテストする
    def test_too_long_path_rejected(self, checker):
        valid, reason = checker.validate_parent("a" * 300)
        assert valid is False
        assert "長すぎる" in reason


# ─── L2: Purpose Comment Tests ───────────────────


# PURPOSE: L2 Purpose コメントのテスト
class TestPurposeCheck:
    """L2 Purpose コメントのテスト"""

    # PURPOSE: function_with_purpose をテストする
    def test_function_with_purpose(self, checker, tmp_py_file):
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "# PURPOSE: ユーザー認証を一元化する\n"
            "def authenticate(user, password):\n"
            "    pass\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        public = [r for r in results if not r.is_dunder]
        assert len(public) == 1
        assert public[0].status == ProofStatus.OK
        assert public[0].purpose_text == "ユーザー認証を一元化する"

    # PURPOSE: function_without_purpose をテストする
    def test_function_without_purpose(self, checker, tmp_py_file):
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "def authenticate(user, password):\n"
            "    pass\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        public = [r for r in results if not r.is_dunder]
        assert len(public) == 1
        assert public[0].status == ProofStatus.MISSING

    # PURPOSE: class_with_purpose をテストする
    def test_class_with_purpose(self, checker, tmp_py_file):
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "# PURPOSE: 認証ロジックをカプセル化する\n"
            "class AuthService:\n"
            "    pass\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        classes = [r for r in results if r.name == "AuthService"]
        assert len(classes) == 1
        assert classes[0].status == ProofStatus.OK

    # PURPOSE: private_function_exempt をテストする
    def test_private_function_exempt(self, checker, tmp_py_file):
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "def _helper():\n"
            "    pass\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        private = [r for r in results if r.is_private]
        assert len(private) == 1
        assert private[0].status == ProofStatus.EXEMPT

    # PURPOSE: dunder_skipped をテストする
    def test_dunder_skipped(self, checker, tmp_py_file):
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "class Foo:\n"
            "    def __init__(self):\n"
            "        pass\n"
            "    def __repr__(self):\n"
            "        pass\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        dunders = [r for r in results if r.is_dunder]
        assert len(dunders) == 0

    # PURPOSE: purpose_above_decorator をテストする
    def test_purpose_above_decorator(self, checker, tmp_py_file):
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "# PURPOSE: プロパティとしてカバレッジを公開する\n"
            "@property\n"
            "def coverage(self):\n"
            "    return 100.0\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        public = [r for r in results if not r.is_dunder]
        assert len(public) == 1
        assert public[0].status == ProofStatus.OK


# ─── L2: WEAK Purpose Quality Tests ─────────────


# PURPOSE: v2.6 Purpose 品質検証のテスト
class TestPurposeQuality:
    """v2.6 Purpose 品質検証のテスト"""

    # PURPOSE: 「を表す」パターンの検出
    def test_weak_wo_arawasu(self, checker):
        """「を表す」パターンの検出"""
        issue = checker._validate_purpose_quality("PROOF の状態を表す列挙型")
        assert issue is not None
        assert "を表す" in issue

    # PURPOSE: 「を保持する」パターンの検出
    def test_weak_wo_hoji_suru(self, checker):
        """「を保持する」パターンの検出"""
        issue = checker._validate_purpose_quality("ファイル情報を保持するデータクラス")
        assert issue is not None
        assert "を保持する" in issue

    # PURPOSE: 「を提供する」パターンの検出
    def test_weak_wo_teikyou_suru(self, checker):
        """「を提供する」パターンの検出"""
        issue = checker._validate_purpose_quality("検証ロジックを提供するクラス")
        assert issue is not None
        assert "を提供する" in issue

    # PURPOSE: 良い Purpose は None を返す
    def test_good_purpose_passes(self, checker):
        """良い Purpose は None を返す"""
        issue = checker._validate_purpose_quality("チェック結果の分類と後続処理の分岐を可能にする")
        assert issue is None

    # PURPOSE: 動詞が明確な Purpose は通過する
    def test_good_purpose_with_action_verb(self, checker):
        """動詞が明確な Purpose は通過する"""
        issue = checker._validate_purpose_quality("ファイル内の PROOF ヘッダーを検出し、その妥当性を検証する")
        assert issue is None

    # PURPOSE: WEAK Purpose がファイルチェックで検出される
    def test_weak_status_in_file(self, checker, tmp_py_file):
        """WEAK Purpose がファイルチェックで検出される"""
        content = (
            "# PROOF: [L2/テスト] <- sample/\n"
            "# PURPOSE: 状態を表す列挙型\n"
            "class MyEnum:\n"
            "    pass\n"
        )
        f = tmp_py_file(content)
        results = checker.check_functions_in_file(f)
        public = [r for r in results if not r.is_dunder]
        assert len(public) == 1
        assert public[0].status == ProofStatus.WEAK
        assert public[0].quality_issue is not None


# ─── Integration: check() method ─────────────────


# PURPOSE: check() メソッドの統合テスト
class TestCheckIntegration:
    """check() メソッドの統合テスト"""

    # PURPOSE: Dendron が自分自身をチェックできる
    def test_dendron_self_check(self):
        """Dendron が自分自身をチェックできる"""
        real_checker = DendronChecker()  # 標準 exempt パターン付き
        dendron_path = Path(__file__).parent.parent
        result = real_checker.check(dendron_path)

        assert result.total_files > 0
        assert result.coverage > 0
        assert result.functions_with_purpose > 0
        assert result.functions_weak_purpose == 0

    # PURPOSE: 空ディレクトリは 100% カバレッジ
    def test_empty_dir(self, checker, tmp_path):
        """空ディレクトリは 100% カバレッジ"""
        result = checker.check(tmp_path)
        assert result.coverage == 100.0
        assert result.is_passing is True


# ─── PURPOSE_PATTERN regex tests ─────────────────


# PURPOSE: PURPOSE_PATTERN 正規表現のテスト
class TestPurposePattern:
    """PURPOSE_PATTERN 正規表現のテスト"""

    # PURPOSE: basic_match をテストする
    def test_basic_match(self):
        m = PURPOSE_PATTERN.search("# PURPOSE: テストする")
        assert m is not None
        assert m.group(1).strip() == "テストする"

    def test_with_extra_spaces(self):
        m = PURPOSE_PATTERN.search("#  PURPOSE:  テストする")
        assert m is not None

    def test_no_match_without_hash(self):
        m = PURPOSE_PATTERN.search("PURPOSE: テストする")
        assert m is None

    # PURPOSE: no_match_empty をテストする
    def test_no_match_empty(self):
        m = PURPOSE_PATTERN.search("# PURPOSE:")
        assert m is None


# ── L3: Variable / Type Hint Tests ─────────────────


# PURPOSE: L3 変数・型ヒントのテスト
class TestVariableCheck:
    """L3 変数・型ヒントのテスト"""

    # PURPOSE: 型ヒント付き public 関数 → OK
    def test_function_with_type_hints(self, checker, tmp_py_file):
        """型ヒント付き public 関数 → OK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef greet(name: str) -> str:\n    return f"Hello {name}"\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        assert len(hints) == 2  # return + arg
        assert all(r.status == ProofStatus.OK for r in hints)

    # PURPOSE: 戻り値の型ヒントなし → MISSING
    def test_function_missing_return_hint(self, checker, tmp_py_file):
        """戻り値の型ヒントなし → MISSING"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef greet(name: str):\n    return f"Hello {name}"\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        missing = [r for r in hints if r.status == ProofStatus.MISSING]
        assert len(missing) == 1
        assert "-> ???" in missing[0].name

    # PURPOSE: 引数の型ヒストなし → MISSING
    def test_function_missing_arg_hint(self, checker, tmp_py_file):
        """引数の型ヒストなし → MISSING"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef greet(name) -> str:\n    return f"Hello {name}"\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        missing = [r for r in hints if r.status == ProofStatus.MISSING]
        assert len(missing) == 1
        assert "(name)" in missing[0].name

    # PURPOSE: private 関数はスキップ
    def test_private_function_skipped(self, checker, tmp_py_file):
        """private 関数はスキップ"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef _internal(x):\n    return x\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        assert len(hints) == 0

    # PURPOSE: 1文字変数 (ホワイトリスト外) → WEAK
    def test_short_name_detected(self, checker, tmp_py_file):
        """1文字変数 (ホワイトリスト外) → WEAK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef calc() -> int:\n    q = 42\n    return q\n')
        results = checker.check_variables_in_file(f)
        short = [r for r in results if r.check_type == "short_name"]
        assert len(short) == 1
        assert short[0].name == "q"
        assert short[0].status == ProofStatus.WEAK

    # PURPOSE: ループ変数 (i, j, k) は許容
    def test_loop_var_allowed(self, checker, tmp_py_file):
        """ループ変数 (i, j, k) は許容"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef loop() -> None:\n    for i in range(10):\n        x = i\n')
        results = checker.check_variables_in_file(f)
        short = [r for r in results if r.check_type == "short_name"]
        # i と x はどちらも _LOOP_VAR_NAMES に含まれる
        assert len(short) == 0

    # PURPOSE: *args に型ヒントあり → OK
    def test_vararg_with_hint(self, checker, tmp_py_file):
        """*args に型ヒントあり → OK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef gather(*args: int) -> None:\n    pass\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        vararg_hints = [r for r in hints if "*args" in r.name]
        assert len(vararg_hints) == 1
        assert vararg_hints[0].status == ProofStatus.OK

    # PURPOSE: *args に型ヒントなし → MISSING
    def test_vararg_without_hint(self, checker, tmp_py_file):
        """*args に型ヒントなし → MISSING"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef gather(*args) -> None:\n    pass\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        missing = [r for r in hints if r.status == ProofStatus.MISSING and "*args" in r.name]
        assert len(missing) == 1

    # PURPOSE: **kwargs に型ヒントあり → OK
    def test_kwarg_with_hint(self, checker, tmp_py_file):
        """**kwargs に型ヒントあり → OK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef configure(**kwargs: str) -> None:\n    pass\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        kwarg_hints = [r for r in hints if "**kwargs" in r.name]
        assert len(kwarg_hints) == 1
        assert kwarg_hints[0].status == ProofStatus.OK

    # PURPOSE: **kwargs に型ヒントなし → MISSING
    def test_kwarg_without_hint(self, checker, tmp_py_file):
        """**kwargs に型ヒントなし → MISSING"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef configure(**kwargs) -> None:\n    pass\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        missing = [r for r in hints if r.status == ProofStatus.MISSING and "**kwargs" in r.name]
        assert len(missing) == 1

    # PURPOSE: キーワード専用引数 (*, key) の型ヒントを検査
    def test_kwonlyargs_checked(self, checker, tmp_py_file):
        """キーワード専用引数 (*, key) の型ヒントを検査"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef action(*, key: str) -> None:\n    pass\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        key_hints = [r for r in hints if "(key)" in r.name]
        assert len(key_hints) == 1
        assert key_hints[0].status == ProofStatus.OK

    # PURPOSE: キーワード専用引数に型ヒントなし → MISSING
    def test_kwonlyargs_missing_hint(self, checker, tmp_py_file):
        """キーワード専用引数に型ヒントなし → MISSING"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\ndef action(*, key) -> None:\n    pass\n')
        results = checker.check_variables_in_file(f)
        hints = [r for r in results if r.check_type == "type_hint"]
        missing = [r for r in hints if r.status == ProofStatus.MISSING and "(key)" in r.name]
        assert len(missing) == 1


# ── L0: Directory PROOF.md Tests ────────────────────


# PURPOSE: L0 ディレクトリ PROOF.md のテスト
class TestDirProof:
    """L0 ディレクトリ PROOF.md のテスト"""

    # PURPOSE: PROOF.md が存在 → OK
    def test_dir_with_proof_md(self, checker, tmp_path):
        """PROOF.md が存在 → OK"""
        proof = tmp_path / "PROOF.md"
        proof.write_text("# PROOF: [L0/テスト] <- parent/\n\nテスト用。\n")
        result = checker.check_dir_proof(tmp_path)
        assert result.status == ProofStatus.OK
        assert result.has_proof_md is True

    # PURPOSE: PROOF.md なし → MISSING
    def test_dir_without_proof_md(self, checker, tmp_path):
        """PROOF.md なし → MISSING"""
        result = checker.check_dir_proof(tmp_path)
        assert result.status == ProofStatus.MISSING
        assert result.has_proof_md is False

    # PURPOSE: 空の PROOF.md → WEAK
    def test_dir_with_empty_proof_md(self, checker, tmp_path):
        """空の PROOF.md → WEAK"""
        proof = tmp_path / "PROOF.md"
        proof.write_text("")
        result = checker.check_dir_proof(tmp_path)
        assert result.status == ProofStatus.WEAK
        assert result.has_proof_md is True
        assert "空" in result.reason

    # PURPOSE: 除外ディレクトリ → EXEMPT
    def test_dir_exempt(self, checker_with_exemptions, tmp_path):
        """除外ディレクトリ → EXEMPT"""
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        result = checker_with_exemptions.check_dir_proof(pycache)
        assert result.status == ProofStatus.EXEMPT


# ── L2: English WEAK Purpose Tests ──────────────────


# PURPOSE: 英語 WEAK パターンの回帰テスト
class TestEnglishWeakPurpose:
    """英語 WEAK パターンの回帰テスト"""

    # PURPOSE: 'Handles X' は WHAT であり WEAK
    def test_english_weak_handles(self, checker, tmp_py_file):
        """'Handles X' は WHAT であり WEAK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\n# PURPOSE: Handles the user data\ndef process(data: str) -> None:\n    pass\n')
        results = checker.check_functions_in_file(f)
        weak = [r for r in results if r.status == ProofStatus.WEAK]
        assert len(weak) == 1

    def test_english_weak_manages(self, checker, tmp_py_file):
        """'Manages X' は WHAT であり WEAK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\n# PURPOSE: Manages the connection pool\ndef manage(pool: list) -> None:\n    pass\n')
        results = checker.check_functions_in_file(f)
        weak = [r for r in results if r.status == ProofStatus.WEAK]
        assert len(weak) == 1

    def test_english_good_purpose(self, checker, tmp_py_file):
        """良い英語 PURPOSE (WHY) → OK"""
        f = tmp_py_file('# PROOF: [L2/x] <- parent/\n# PURPOSE: Prevent memory leaks by closing idle connections after timeout\ndef cleanup(pool: list) -> None:\n    pass\n')
        results = checker.check_functions_in_file(f)
        ok = [r for r in results if r.status == ProofStatus.OK]
        assert len(ok) == 1

