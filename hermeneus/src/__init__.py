# PROOF: [L2/インフラ] <- hermeneus/src/ Hermēneus パッケージ
"""
Hermēneus — CCL 実行保証コンパイラ

CCL (Cognitive Control Language) をパース・展開・実行する。

Usage:
    from hermeneus.src.parser import CCLParser
    from hermeneus.src.ccl_ast import Workflow, Sequence, Oscillation

    parser = CCLParser()
    ast = parser.parse("/noe+_/dia")

NOTE: 以前は大量の re-export をしていたが、循環インポートの温床になるため
      各モジュールからの直接インポートに移行した (2026-02-10)。
      旧: from hermeneus.src import Workflow
      新: from hermeneus.src.ccl_ast import Workflow
"""

__version__ = "0.8.1"  # Phase 8.1: 後方互換 re-export (MCP キャッシュ対策)


# =============================================================================
# 後方互換 re-export (レイジーインポート)
# 循環インポートを避けるため __getattr__ で遅延ロードする。
# MCP サーバープロセスが古い import パスを使っている場合に対応。
# =============================================================================

# PURPOSE: 後方互換: from hermeneus.src import X をサポート
def __getattr__(name: str):
    """後方互換: from hermeneus.src import X をサポート"""
    _lazy_imports = {
        # audit.py
        "get_audit_report": "hermeneus.src.audit",
        "query_audits": "hermeneus.src.audit",
        # registry.py
        "list_workflows": "hermeneus.src.registry",
        "get_workflow": "hermeneus.src.registry",
        "WorkflowRegistry": "hermeneus.src.registry",
    }
    if name in _lazy_imports:
        import importlib
        module = importlib.import_module(_lazy_imports[name])
        return getattr(module, name)
    raise AttributeError(f"module 'hermeneus.src' has no attribute {name!r}")


# PURPOSE: CCL 式を LMQL プログラムにコンパイル
def compile_ccl(
    ccl: str,
    macros: dict = None,
    model: str = "openai/gpt-4o"
) -> str:
    """CCL 式を LMQL プログラムにコンパイル

    Args:
        ccl: CCL 式 (例: "/noe+ >> V[] < 0.3")
        macros: マクロ定義 (例: {"think": "/noe+"})
        model: 使用する LLM モデル

    Returns:
        LMQL プログラムコード

    Example:
        >>> lmql_code = compile_ccl("/noe+")
        >>> print(lmql_code)
    """
    from hermeneus.src.expander import Expander
    from hermeneus.src.parser import CCLParser
    from hermeneus.src.translator import LMQLTranslator

    # Step 1: 展開
    expander = Expander(macro_registry=macros or {})
    expansion = expander.expand(ccl)

    # Step 2: パース
    parser = CCLParser()
    ast = parser.parse(expansion.expanded)

    # Step 3: 翻訳
    translator = LMQLTranslator(model=model)
    lmql_code = translator.translate(ast)

    return lmql_code


# =============================================================================
# CLI Entry Point
# =============================================================================

# PURPOSE: CLI エントリーポイント
def main():
    """CLI エントリーポイント"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m hermeneus.src <ccl_expression>")
        print("Example: python -m hermeneus.src '/noe+ >> V[] < 0.3'")
        sys.exit(1)

    ccl = sys.argv[1]

    print(f"CCL: {ccl}")
    print("=" * 60)

    try:
        lmql_code = compile_ccl(ccl)
        print(lmql_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
