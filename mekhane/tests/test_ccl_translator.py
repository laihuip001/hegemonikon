# PROOF: [L2/テスト] <- mekhane/tests/
"""
Tests for CCL -> LMQL Translator
"""

import pytest
from hermeneus.src.translator import LMQLTranslator
from hermeneus.src.ccl_ast import MacroRef

def test_translate_macro_expansion():
    """Test that macros are properly expanded and translated into LMQL."""
    translator = LMQLTranslator(model="test-model")

    # Test a known builtin macro, e.g., @wake
    # Note: wake is typically defined as "/boot+_@dig_@plan" or similar
    macro_ref = MacroRef(name="wake")

    lmql_output = translator._translate_macro(macro_ref)

    # Verify that the fallback is not used
    assert "未定義マクロ" not in lmql_output
    assert "未定義" not in lmql_output

    # Since it's translated, it should be an LMQL query based on the expanded AST (e.g. sequence execution)
    assert "@lmql.query" in lmql_output
    assert "from" in lmql_output
    assert '"test-model"' in lmql_output

def test_translate_unknown_macro():
    """Test that an unknown macro falls back appropriately."""
    translator = LMQLTranslator(model="test-model")

    macro_ref = MacroRef(name="this_macro_does_not_exist_xyz123")

    lmql_output = translator._translate_macro(macro_ref)

    # Should use the fallback template
    assert "未定義マクロ @this_macro_does_not_exist_xyz123 のフォールバック実行" in lmql_output
    assert "@lmql.query" in lmql_output
    assert '"test-model"' in lmql_output
