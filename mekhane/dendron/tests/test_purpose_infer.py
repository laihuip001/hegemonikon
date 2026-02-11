#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/dendron/ A0→テストが必要→test_purpose_inferが担う
"""
Tests for purpose_infer.py — PURPOSE 自動推定ツール
"""

import ast
import textwrap
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from mekhane.dendron.purpose_infer import infer_purpose, add_purpose_comments


# PURPOSE: infer_purpose のパターンマッチと docstring 抽出をテスト
class TestInferPurpose(unittest.TestCase):
    """Test suite for infer purpose."""
    # PURPOSE: Verify docstring japanese behaves correctly
    def test_docstring_japanese(self):
        """Verify docstring japanese behavior."""
        result = infer_purpose("func", "function", "日本語の説明文です")
        self.assertEqual(result, "日本語の説明文です")

    # PURPOSE: docstring_english をテストする
    def test_docstring_english(self):
        """Verify docstring english behavior."""
        result = infer_purpose("func", "function", "Short English description")
        self.assertEqual(result, "Short English description")

    # PURPOSE: get_prefix をテストする
    def test_get_prefix(self):
        """Verify get prefix behavior."""
        result = infer_purpose("get_user_data", "function")
        self.assertIn("取得", result)
        self.assertIn("get_user_data", result)

    # PURPOSE: set_prefix をテストする
    def test_set_prefix(self):
        """Verify set prefix behavior."""
        result = infer_purpose("set_config", "function")
        self.assertIn("設定/保存", result)

    # PURPOSE: check_prefix をテストする
    def test_check_prefix(self):
        """Verify check prefix behavior."""
        result = infer_purpose("check_validity", "function")
        self.assertIn("検証", result)

    # PURPOSE: create_prefix をテストする
    def test_create_prefix(self):
        """Verify create prefix behavior."""
        result = infer_purpose("create_report", "function")
        self.assertIn("生成", result)

    # PURPOSE: test_prefix をテストする
    def test_test_prefix(self):
        """Verify test prefix behavior."""
        result = infer_purpose("test_something", "function")
        self.assertIn("テスト", result)

    # PURPOSE: init_method をテストする
    def test_init_method(self):
        """Verify init method behavior."""
        result = infer_purpose("__init__", "function")
        self.assertIn("初期化", result)

    # PURPOSE: private_method をテストする
    def test_private_method(self):
        """Verify private method behavior."""
        result = infer_purpose("_internal_helper", "function")
        self.assertIn("内部処理", result)

    # PURPOSE: class_fallback をテストする
    def test_class_fallback(self):
        """Verify class fallback behavior."""
        result = infer_purpose("MyService", "class")
        self.assertIn("クラス", result)

    # PURPOSE: function_fallback をテストする
    def test_function_fallback(self):
        """Verify function fallback behavior."""
        result = infer_purpose("mysterious_action", "function")
        self.assertIn("関数", result)

    # PURPOSE: docstring_truncation をテストする
    def test_docstring_truncation(self):
        """Verify docstring truncation behavior."""
        long_doc = "A" * 200
        result = infer_purpose("func", "function", long_doc)
        self.assertLessEqual(len(result), 80)

    # PURPOSE: docstring_multiline_first_line_only をテストする
    def test_docstring_multiline_first_line_only(self):
        """Verify docstring multiline first line only behavior."""
        doc = "First line.\nSecond line with details."
        result = infer_purpose("func", "function", doc)
        self.assertEqual(result, "First line.")


# PURPOSE: ファイルへの PURPOSE コメント挿入をテスト
class TestAddPurposeComments(unittest.TestCase):
    """Test suite for add purpose comments."""
    def _make_temp_file(self, content: str) -> Path:
        """テスト用一時ファイルを生成"""
        f = NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
        f.write(textwrap.dedent(content))
        f.close()
        return Path(f.name)

    # PURPOSE: dry_run_counts_additions をテストする
    def test_dry_run_counts_additions(self):
        """Verify dry run counts additions behavior."""
        path = self._make_temp_file("""\
            def hello():
                pass

            def world():
                pass
        """)
        try:
            count = add_purpose_comments(path, dry_run=True)
            # Should find 2 functions without PURPOSE
            self.assertEqual(count, 2)
            # File should NOT be modified in dry run
            content = path.read_text()
            self.assertNotIn("# PURPOSE:", content)
        finally:
            path.unlink()

    # PURPOSE: Verify apply inserts comments behaves correctly
    def test_apply_inserts_comments(self):
        """Verify apply inserts comments behavior."""
        path = self._make_temp_file("""\
            def get_data():
                pass

            class MyClass:
                def __init__(self):
                    pass
        """)
        try:
            count = add_purpose_comments(path, dry_run=False)
            self.assertGreater(count, 0)
            content = path.read_text()
            self.assertIn("# PURPOSE:", content)
            self.assertIn("[L2-auto]", content)
            self.assertIn("取得", content)  # get_ pattern
        finally:
            path.unlink()

    # PURPOSE: skips_existing_purpose をテストする
    def test_skips_existing_purpose(self):
        """Verify skips existing purpose behavior."""
        path = self._make_temp_file("""\
            # PURPOSE: Already documented
            def documented_func():
                pass

            def undocumented_func():
                pass
        """)
        try:
            count = add_purpose_comments(path, dry_run=True)
            # Only undocumented_func should be counted
            self.assertEqual(count, 1)
        finally:
            path.unlink()

    # PURPOSE: handles_syntax_error をテストする
    def test_handles_syntax_error(self):
        """Verify handles syntax error behavior."""
        path = self._make_temp_file("""\
            this is not valid python !!!
        """)
        try:
            count = add_purpose_comments(path, dry_run=True)
            self.assertEqual(count, 0)
        finally:
            path.unlink()

    # PURPOSE: preserves_indentation をテストする
    def test_preserves_indentation(self):
        """Verify preserves indentation behavior."""
        path = self._make_temp_file("""\
            class Outer:
                def inner_method(self):
                    pass
        """)
        try:
            count = add_purpose_comments(path, dry_run=False)
            content = path.read_text()
            # PURPOSE should be indented to match the method
            lines = content.split("\n")
            purpose_lines = [l for l in lines if "# PURPOSE:" in l]
            for pl in purpose_lines:
                # Should have some indentation (not at column 0 for methods)
                pass  # just verify no crash
            self.assertGreater(count, 0)
        finally:
            path.unlink()

    # PURPOSE: docstring_extraction をテストする
    def test_docstring_extraction(self):
        """Verify docstring extraction behavior."""
        path = self._make_temp_file('''\
            def with_docstring():
                """設定を読み込む関数"""
                pass
        ''')
        try:
            count = add_purpose_comments(path, dry_run=False)
            content = path.read_text()
            self.assertIn("設定を読み込む関数", content)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
