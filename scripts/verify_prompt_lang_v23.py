#!/usr/bin/env python3
"""Prompt-Lang v2.3 品質検証スクリプト"""
import sys
import io
from pathlib import Path

# Path setup
sys.path.insert(0, str(Path(__file__).parent.parent / "mekhane" / "mcp"))
sys.path.insert(0, str(Path(__file__).parent.parent / "mekhane"))

# Suppress stdout during import
_orig = sys.stdout
sys.stdout = io.StringIO()
from prompt_lang_mcp_server import generate_prompt_lang
sys.stdout = _orig

cases = [
    ("コードレビューでバグを検出するスキル", "technical", ".prompt"),
    ("論文の要点を3行で要約するスキル", "summarization", ".prompt"),
    ("RAGパイプラインで関連ドキュメントを検索するスキル", "rag", ".prompt"),
    ("FEPに基づく能動推論の調査をまとめるスキル", "research", ".prompt"),
]

for req, domain, fmt in cases:
    print(f"\n{'='*60}")
    print(f"Domain: {domain} | Req: {req}")
    print(f"{'='*60}")
    result = generate_prompt_lang(req, domain, fmt)
    print(result)

    # v2.3 features check
    checks = {
        "Safety": "安全基盤制約" in result,
        "Failure": "失敗ケース" in result or "Pre-Mortem" in result,
        "Archetype": "Archetype" in result,
        "Context_tool": "tool:" in result,
        "Schema_json": "```json" in result,
        "Examples_3": result.count("@example") >= 3 or result.count("input:") >= 3,
    }
    print(f"\n[v2.3 施策チェック]")
    for k, v in checks.items():
        status = "✅" if v else "❌"
        print(f"  {status} {k}")
    
    # Count lines as rough quality indicator
    lines = result.strip().split("\n")
    print(f"  📏 行数: {len(lines)}")

print("\n" + "="*60)
print("検証完了")
