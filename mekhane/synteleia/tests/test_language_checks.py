# PROOF: [L1/テスト] <- mekhane/synteleia/tests/ 言語固有チェックのテスト
"""
Tests for language-specific completeness checks (COMP-040/041/042).

Validates that CompletenessAgent correctly detects:
- COMP-040: Python NotImplementedError
- COMP-041: TS/JS non-strict equality (==)
- COMP-042: Rust unwrap()/expect()
And that they do NOT fire for wrong languages (cross-language safety).
"""

import pytest
from mekhane.synteleia import AuditTarget, AuditTargetType
from mekhane.synteleia.dokimasia.completeness_agent import CompletenessAgent


@pytest.fixture
def agent():
    """PURPOSE: CompletenessAgent fixture"""
    return CompletenessAgent()


# PURPOSE: audit helper
def _audit_code(agent, code: str, source: str):
    """Run audit and return issues list."""
    target = AuditTarget(
        content=code, target_type=AuditTargetType.CODE, source=source
    )
    result = agent.audit(target)
    return result.issues


def _codes(issues):
    """Extract issue codes as a set."""
    return {i.code for i in issues}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMP-040: Python NotImplementedError
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCOMP040:
    """PURPOSE: Python NotImplementedError detection"""

    def test_detects_raise_not_implemented(self, agent):
        code = "def foo():\n    raise NotImplementedError\n"
        issues = _audit_code(agent, code, "test.py")
        assert "COMP-040" in _codes(issues)

    def test_detects_raise_with_message(self, agent):
        code = 'def foo():\n    raise NotImplementedError("TODO")\n'
        issues = _audit_code(agent, code, "test.py")
        assert "COMP-040" in _codes(issues)

    def test_no_false_positive_normal_raise(self, agent):
        code = "def foo():\n    raise ValueError('bad')\n"
        issues = _audit_code(agent, code, "test.py")
        assert "COMP-040" not in _codes(issues)

    def test_not_fired_for_ts(self, agent):
        """NotImplementedError is Python-only — must NOT fire for .ts"""
        code = "function foo() { throw new Error('NotImplementedError'); }\n"
        issues = _audit_code(agent, code, "test.ts")
        assert "COMP-040" not in _codes(issues)

    def test_not_fired_for_rs(self, agent):
        """Must NOT fire for Rust files"""
        code = 'fn foo() { panic!("NotImplementedError"); }\n'
        issues = _audit_code(agent, code, "test.rs")
        assert "COMP-040" not in _codes(issues)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMP-041: TS/JS non-strict equality
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCOMP041:
    """PURPOSE: TS/JS == detection"""

    def test_detects_double_equals_ts(self, agent):
        code = "if (x == 5) { console.log(x); }\n"
        issues = _audit_code(agent, code, "test.ts")
        assert "COMP-041" in _codes(issues)

    def test_detects_double_equals_js(self, agent):
        code = "if (x == null) { return; }\n"
        issues = _audit_code(agent, code, "test.js")
        assert "COMP-041" in _codes(issues)

    def test_no_false_positive_triple_equals(self, agent):
        code = "if (x === 5) { console.log(x); }\n"
        issues = _audit_code(agent, code, "test.ts")
        assert "COMP-041" not in _codes(issues)

    def test_no_false_positive_not_equals(self, agent):
        code = "if (x !== 5) { console.log(x); }\n"
        issues = _audit_code(agent, code, "test.ts")
        assert "COMP-041" not in _codes(issues)

    def test_not_fired_for_python(self, agent):
        """== is correct in Python — must NOT fire"""
        code = "if x == 5:\n    print(x)\n"
        issues = _audit_code(agent, code, "test.py")
        assert "COMP-041" not in _codes(issues)

    def test_not_fired_for_rust(self, agent):
        """== is correct in Rust — must NOT fire"""
        code = "if x == 5 { println!(\"{}\", x); }\n"
        issues = _audit_code(agent, code, "test.rs")
        assert "COMP-041" not in _codes(issues)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMP-042: Rust unwrap()/expect()
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestCOMP042:
    """PURPOSE: Rust unwrap/expect detection"""

    def test_detects_unwrap(self, agent):
        code = "let x = Some(5).unwrap();\n"
        issues = _audit_code(agent, code, "test.rs")
        assert "COMP-042" in _codes(issues)

    def test_detects_expect(self, agent):
        code = 'let x = Some(5).expect("msg");\n'
        issues = _audit_code(agent, code, "test.rs")
        assert "COMP-042" in _codes(issues)

    def test_no_false_positive_question_mark(self, agent):
        code = "let x = some_fn()?;\n"
        issues = _audit_code(agent, code, "test.rs")
        assert "COMP-042" not in _codes(issues)

    def test_no_false_positive_match(self, agent):
        code = "match opt { Some(v) => v, None => 0 }\n"
        issues = _audit_code(agent, code, "test.rs")
        assert "COMP-042" not in _codes(issues)

    def test_not_fired_for_python(self, agent):
        """Rust-only — must NOT fire for .py"""
        code = "x.unwrap()\n"  # unlikely but syntax valid
        issues = _audit_code(agent, code, "test.py")
        assert "COMP-042" not in _codes(issues)

    def test_not_fired_for_ts(self, agent):
        """Rust-only — must NOT fire for .ts"""
        code = "x.unwrap();\n"
        issues = _audit_code(agent, code, "test.ts")
        assert "COMP-042" not in _codes(issues)

    def test_counts_multiple(self, agent):
        code = "let a = x.unwrap();\nlet b = y.expect(\"e\");\n"
        issues = _audit_code(agent, code, "test.rs")
        c042 = [i for i in issues if i.code == "COMP-042"]
        assert len(c042) == 2
