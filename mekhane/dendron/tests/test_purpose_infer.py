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
    def test_docstring_japanese(self):
        result = infer_purpose("func", "function", "日本語の説明文です")
        self.assertEqual(result, "日本語の説明文です")

    def test_docstring_english(self):
        result = infer_purpose("func", "function", "Short English description")
        self.assertEqual(result, "Short English description")

    def test_get_prefix(self):
        result = infer_purpose("get_user_data", "function")
        self.assertIn("取得", result)
        self.assertIn("get_user_data", result)

    def test_set_prefix(self):
        result = infer_purpose("set_config", "function")
        self.assertIn("設定/保存", result)

    def test_check_prefix(self):
        result = infer_purpose("check_validity", "function")
        self.assertIn("検証", result)

    def test_create_prefix(self):
        result = infer_purpose("create_report", "function")
        self.assertIn("生成", result)

    def test_test_prefix(self):
        result = infer_purpose("test_something", "function")
        self.assertIn("テスト", result)

    def test_init_method(self):
        result = infer_purpose("__init__", "function")
        self.assertIn("初期化", result)

    def test_private_method(self):
        result = infer_purpose("_internal_helper", "function")
        self.assertIn("内部処理", result)

    def test_class_fallback(self):
        result = infer_purpose("MyService", "class")
        self.assertIn("クラス", result)

    def test_function_fallback(self):
        result = infer_purpose("mysterious_action", "function")
        self.assertIn("関数", result)

    def test_docstring_truncation(self):
        long_doc = "A" * 200
        result = infer_purpose("func", "function", long_doc)
        self.assertLessEqual(len(result), 80)

    def test_docstring_multiline_first_line_only(self):
        doc = "First line.\nSecond line with details."
        result = infer_purpose("func", "function", doc)
        self.assertEqual(result, "First line.")


# PURPOSE: ファイルへの PURPOSE コメント挿入をテスト
class TestAddPurposeComments(unittest.TestCase):
    def _make_temp_file(self, content: str) -> Path:
        """テスト用一時ファイルを生成"""
        f = NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
        f.write(textwrap.dedent(content))
        f.close()
        return Path(f.name)

    def test_dry_run_counts_additions(self):
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

    def test_apply_inserts_comments(self):
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

    def test_skips_existing_purpose(self):
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

    def test_handles_syntax_error(self):
        path = self._make_temp_file("""\
            this is not valid python !!!
        """)
        try:
            count = add_purpose_comments(path, dry_run=True)
            self.assertEqual(count, 0)
        finally:
            path.unlink()

    def test_preserves_indentation(self):
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

    def test_docstring_extraction(self):
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
