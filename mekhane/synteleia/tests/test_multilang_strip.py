# PROOF: [L1/テスト] <- mekhane/synteleia/tests/ 多言語 strip テスト
"""
Tests for strip_strings_and_comments multilang support.

Covers: JS/TS comments, template literals, regex literals,
Python docstrings, and mixed-language edge cases.
"""

import pytest

from mekhane.synteleia.pattern_loader import strip_strings_and_comments


class TestJSComments:
    """JS/TS コメント strip"""

    def test_line_comment(self):
        code = "const x = 1; // this is a comment"
        result = strip_strings_and_comments(code)
        assert "//" not in result
        assert "const x = 1;" in result

    def test_block_comment(self):
        code = "const x = /* inline */ 1;"
        result = strip_strings_and_comments(code)
        assert "inline" not in result
        assert "const x =" in result
        assert "1;" in result

    def test_multiline_block_comment(self):
        code = """/**
 * JSDoc comment
 * @param x description
 */
function foo() {}"""
        result = strip_strings_and_comments(code)
        assert "JSDoc" not in result
        assert "@param" not in result
        assert "function foo()" in result

    def test_block_comment_with_brackets(self):
        """ブロックコメント内の括弧が strip される"""
        code = "/* { ( [ ] ) } */ const x = 1;"
        result = strip_strings_and_comments(code)
        assert "{" not in result.split("const")[0]
        assert "const x = 1;" in result


class TestTemplateLiterals:
    """JS/TS テンプレートリテラル strip"""

    def test_simple_template(self):
        code = "const msg = `hello world`;"
        result = strip_strings_and_comments(code)
        assert "hello world" not in result
        assert "const msg =" in result

    def test_template_with_brackets(self):
        """テンプレートリテラル内の括弧が strip される — COMP-030 偽陽性の根本原因"""
        code = "const msg = `value is ${x} items`;"
        result = strip_strings_and_comments(code)
        assert "${x}" not in result

    def test_template_with_unbalanced_braces(self):
        """テンプレートリテラル内の不対応括弧が括弧カウントに影響しない"""
        code = "const re = `{{{`;"
        result = strip_strings_and_comments(code)
        open_count = result.count("{")
        close_count = result.count("}")
        assert open_count == close_count, (
            f"Unbalanced braces after strip: {{ = {open_count}, }} = {close_count}"
        )


class TestRegexLiterals:
    """JS/TS 正規表現リテラル strip"""

    def test_regex_after_equals(self):
        code = "const re = /[{}]+/g;"
        result = strip_strings_and_comments(code)
        assert "[{}]" not in result

    def test_regex_after_paren(self):
        code = 'str.match(/^(\\w+)\\s*=/)';
        result = strip_strings_and_comments(code)
        assert "\\w+" not in result

    def test_regex_not_division(self):
        """除算の / は strip しない"""
        code = "const ratio = a / b;"
        result = strip_strings_and_comments(code)
        assert "a" in result
        assert "b" in result

    def test_regex_with_escaped_slash(self):
        code = r"const re = /path\/to\/file/;"
        result = strip_strings_and_comments(code)
        assert "path" not in result


class TestPythonCompat:
    """Python 構文の後方互換性"""

    def test_python_hash_comment(self):
        code = "x = 1  # comment"
        result = strip_strings_and_comments(code)
        assert "comment" not in result
        assert "x = 1" in result

    def test_python_docstring(self):
        code = '"""This is a docstring"""\nx = 1'
        result = strip_strings_and_comments(code)
        assert "docstring" not in result
        assert "x = 1" in result

    def test_python_single_docstring(self):
        code = "'''Another docstring'''\nx = 1"
        result = strip_strings_and_comments(code)
        assert "Another" not in result

    def test_python_string_with_brackets(self):
        code = 'msg = "hello {name}"'
        result = strip_strings_and_comments(code)
        assert "{name}" not in result


class TestRustCompat:
    """Rust 構文の互換性"""

    def test_rust_line_comment(self):
        code = "let x = 1; // comment"
        result = strip_strings_and_comments(code)
        assert "comment" not in result

    def test_rust_block_comment(self):
        code = "let x = /* value */ 1;"
        result = strip_strings_and_comments(code)
        assert "value" not in result

    def test_rust_string(self):
        code = 'let msg = "hello {}";'
        result = strip_strings_and_comments(code)
        assert "hello" not in result


class TestEdgeCases:
    """エッジケース"""

    def test_empty_string(self):
        assert strip_strings_and_comments("") == ""

    def test_no_comments_or_strings(self):
        code = "const x = 1 + 2;"
        result = strip_strings_and_comments(code)
        assert result.strip() == code.strip()

    def test_mixed_languages_safe(self):
        """Python の # と JS の // が共存しても安全"""
        code = "x = 1  # py comment\ny = 2  // js comment"
        result = strip_strings_and_comments(code)
        assert "py comment" not in result
        assert "js comment" not in result
        assert "x = 1" in result
        assert "y = 2" in result

    def test_bracket_balance_after_strip(self):
        """strip 後に括弧がバランスするか (実際の TypeScript コード)"""
        code = """
export function foo(): boolean {
    const re = /[{}]+/;
    const msg = `hello {world}`;
    // { unbalanced in comment }
    /* { block } */
    return true;
}
"""
        result = strip_strings_and_comments(code)
        for open_b, close_b in [("(", ")"), ("[", "]"), ("{", "}")]:
            o = result.count(open_b)
            c = result.count(close_b)
            assert o == c, (
                f"Unbalanced '{open_b}'/'{close_b}': {o} vs {c}\n"
                f"Stripped content:\n{result}"
            )
