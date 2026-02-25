# PROOF: [L2/Mekhane] <- mekhane/dendron/tests/ A0->Auto->AddedByCI
# PROOF: [L2/テスト] <- mekhane/dendron/
# PURPOSE: REASON 自動推定機能の単体テスト
# REASON: REASON カバレッジ改善 (F1) のために reason_infer.py と同時に作成
"""
REASON Auto-Inferer Tests

テスト対象:
- infer_reason: 関数/クラスの REASON 推定
- infer_file_reason: ファイルレベルの REASON 推定
- add_reason_comments: REASON コメントの自動挿入
- get_file_creation_date: Git/mtime フォールバック
"""
import pytest
from pathlib import Path
from mekhane.dendron.reason_infer import (
    infer_reason,
    infer_file_reason,
    add_reason_comments,
    get_file_creation_date,
)


# PURPOSE: 関数/クラスの REASON 推定テスト
class TestInferReason:
    """関数/クラスの REASON 推定テスト"""

    # PURPOSE: 日本語の背景パターンを docstring から抽出する
    def test_from_docstring_japanese_background(self):
        """日本語の背景パターンを docstring から抽出する"""
        reason = infer_reason("foo", "function", docstring="背景: APIが不安定だったため")
        assert "背景" in reason

    # PURPOSE: 英語の Motivation パターンを docstring から抽出する
    def test_from_docstring_english_motivation(self):
        """英語の Motivation パターンを docstring から抽出する"""
        reason = infer_reason("foo", "function", docstring="Motivation: reduce API latency")
        assert "Motivation" in reason

    # PURPOSE: PURPOSE テキストから REASON を推定する
    def test_from_purpose_text(self):
        """PURPOSE テキストから REASON を推定する"""
        reason = infer_reason("foo", "function", purpose_text="データを検証する")
        assert "データを検証する" in reason
        assert "を実現するために作成" in reason

    # PURPOSE: fix_ プレフィックスからバグ修正を推定する
    def test_from_name_pattern_fix(self):
        """fix_ プレフィックスからバグ修正を推定する"""
        reason = infer_reason("fix_login", "function")
        assert "バグ修正" in reason

    # PURPOSE: migrate_ プレフィックスから移行を推定する
    def test_from_name_pattern_migrate(self):
        """migrate_ プレフィックスから移行を推定する"""
        reason = infer_reason("migrate_db", "function")
        assert "移行" in reason

    # PURPOSE: test_ プレフィックスから品質保証を推定する
    def test_from_name_pattern_test(self):
        """test_ プレフィックスから品質保証を推定する"""
        reason = infer_reason("test_foo", "function")
        assert "品質保証" in reason

    # PURPOSE: 名前パターンに一致しない関数のフォールバック
    def test_fallback_function(self):
        """名前パターンに一致しない関数のフォールバック"""
        reason = infer_reason("calculate", "function")
        assert "関数" in reason
        assert "calculate" in reason

    # PURPOSE: クラスのフォールバック
    def test_fallback_class(self):
        """クラスのフォールバック"""
        reason = infer_reason("Calculator", "class")
        assert "クラス" in reason
        assert "Calculator" in reason

    # PURPOSE: __init__ の特別処理
    def test_init_function(self):
        """__init__ の特別処理"""
        reason = infer_reason("__init__", "function")
        assert "初期化" in reason


# PURPOSE: ファイルレベルの REASON 推定テスト
class TestInferFileReason:
    """ファイルレベルの REASON 推定テスト"""

    # PURPOSE: Git のないディレクトリでも mtime フォールバックで動作する
    def test_fallback_without_git(self, tmp_path):
        """Git のないディレクトリでも mtime フォールバックで動作する"""
        f = tmp_path / "test.py"
        f.write_text("# PROOF: [L1]\nx = 1\n")
        reason = infer_file_reason(f)
        # mtime ベースの日付か "初回実装" が返る
        assert reason  # 空でない

    # PURPOSE: 戻り値は文字列型
    def test_returns_string(self, tmp_path):
        """戻り値は文字列型"""
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        reason = infer_file_reason(f)
        assert isinstance(reason, str)


# PURPOSE: Git/mtime フォールバックテスト
class TestGetFileCreationDate:
    """Git/mtime フォールバックテスト"""

    # PURPOSE: Git 管理外のディレクトリでは mtime にフォールバック
    def test_non_git_directory(self, tmp_path):
        """Git 管理外のディレクトリでは mtime にフォールバック"""
        f = tmp_path / "test.py"
        f.write_text("x = 1\n")
        date = get_file_creation_date(f)
        # mtime から YYYY-MM-DD が取得できる
        assert date is not None
        assert len(date) == 10  # YYYY-MM-DD

    # PURPOSE: 存在しないファイルでは None を返す
    def test_nonexistent_file(self, tmp_path):
        """存在しないファイルでは None を返す"""
        f = tmp_path / "nonexistent.py"
        date = get_file_creation_date(f)
        assert date is None


# PURPOSE: REASON コメント自動挿入テスト
class TestAddReasonComments:
    """REASON コメント自動挿入テスト"""

    # PURPOSE: ドライランでファイルが変更されない
    def test_dry_run_no_writes(self, tmp_path):
        """ドライランでファイルが変更されない"""
        f = tmp_path / "test.py"
        content = (
            "# PROOF: [L1]\n"
            "# PURPOSE: テスト用\n"
            "def foo():\n"
            "    pass\n"
        )
        f.write_text(content)
        file_count, func_count = add_reason_comments(f, dry_run=True)
        assert f.read_text() == content  # 変更なし

    # PURPOSE: 既に REASON がある場合はスキップ
    def test_skips_existing_reason(self, tmp_path):
        """既に REASON がある場合はスキップ"""
        f = tmp_path / "test.py"
        content = (
            "# PROOF: [L1]\n"
            "# REASON: 既存の理由\n"
            "# PURPOSE: テスト用\n"
            "# REASON: 関数の理由\n"
            "def foo():\n"
            "    pass\n"
        )
        f.write_text(content)
        file_count, func_count = add_reason_comments(f, dry_run=True)
        assert file_count == 0
        assert func_count == 0

    # PURPOSE: --apply でファイルに REASON が書き込まれる
    def test_apply_writes_file_reason(self, tmp_path):
        """--apply でファイルに REASON が書き込まれる"""
        f = tmp_path / "test.py"
        content = (
            "# PROOF: [L1]\n"
            "def foo():\n"
            "    pass\n"
        )
        f.write_text(content)
        file_count, func_count = add_reason_comments(f, dry_run=False)
        new_content = f.read_text()
        assert "REASON:" in new_content
        assert file_count == 1

    # PURPOSE: --apply で関数に REASON が書き込まれる
    def test_apply_writes_func_reason(self, tmp_path):
        """--apply で関数に REASON が書き込まれる"""
        f = tmp_path / "test.py"
        content = (
            "# PROOF: [L1]\n"
            "# REASON: ファイルレベル\n"
            "\n"
            "import os\n"
            "import sys\n"
            "\n"
            "X = 1\n"
            "\n"
            "# PURPOSE: テスト用関数\n"
            "def foo():\n"
            "    pass\n"
        )
        f.write_text(content)
        file_count, func_count = add_reason_comments(f, dry_run=False)
        new_content = f.read_text()
        assert file_count == 0  # 既にファイルレベル REASON あり
        assert func_count >= 1  # 関数に REASON 追加
        assert new_content.count("REASON:") >= 2  # 既存 + 追加

    # PURPOSE: 構文エラーのファイルでもクラッシュしない
    def test_syntax_error_file(self, tmp_path):
        """構文エラーのファイルでもクラッシュしない"""
        f = tmp_path / "bad.py"
        f.write_text("# PROOF: [L1]\ndef foo(:\n")
        file_count, func_count = add_reason_comments(f, dry_run=True)
        # ファイルレベルは検出可能、関数レベルは 0
        assert func_count == 0
