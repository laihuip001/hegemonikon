#!/usr/bin/env python3
# PROOF: [L2/ユーティリティ] <- mekhane/symploke/ F5 benchmark で Gemini 3 Flash の品質を確認済み
# PURPOSE: Cortex Review Runner — Gemini 3 Flash/Pro 直接呼び出しによるコードレビュー
"""
Cortex Review Runner — Gemini 3 Flash/Pro 直接呼び出しによるコードレビュー

Jules API を経由せず、Cortex (Ochema MCP) を直接使うレビュースクリプト。
run_specialists.py の軽量版。日次 CI/CD パイプライン向け。

Usage:
    python run_cortex_review.py <target_file>
    python run_cortex_review.py <target_file> --model gemini-3-pro-preview
    python run_cortex_review.py <target_file> --output review_result.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# デフォルトモデル: F5 benchmark で Flash がコスト最適と確認
DEFAULT_MODEL = "gemini-3-flash-preview"
PRO_MODEL = "gemini-3-pro-preview"

# HGK コンテキスト (specialist_v2 の context/ から抽出)
CONTEXT_DIR = Path(__file__).parent / "context"

# レビュー用のシステムプロンプト
SYSTEM_PROMPT = """You are reviewing code for Hegemonikón, a cognitive hypervisor framework.
It uses 24 cognitive theorems (O1-O4, S1-S4, H1-H4, P1-P4, K1-K4, A1-A4) derived from FEP.
Each theorem represents a cognitive function with Greek names (Noēsis, Mekhanē, Energeia, etc.).
Focus on: correctness, naming quality, design adherence, and potential improvements.
Output: top 5 findings as structured items with severity (Critical/High/Medium/Low)."""


# PURPOSE: context/ ディレクトリから全コンテキストを結合して返す。
def load_context() -> str:
    """context/ ディレクトリから全コンテキストを結合して返す。"""
    context_parts: list[str] = []
    if CONTEXT_DIR.exists():
        for md_file in sorted(CONTEXT_DIR.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            context_parts.append(f"## {md_file.stem}\n\n{content}")
    return "\n\n---\n\n".join(context_parts)


# PURPOSE: レビュープロンプトを構築する。
def build_review_prompt(code: str, filepath: str, context: str) -> str:
    """レビュープロンプトを構築する。"""
    return f"""Review the following code from `{filepath}`.

## HGK Context
{context}

## Code to Review
```python
{code}
```

Provide your top 5 findings with severity (Critical/High/Medium/Low) and actionable recommendations."""


# PURPOSE: Ochema Cortex API を呼び出す (MCP 経由)。
def call_cortex(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 2048) -> str:
    """Ochema Cortex API を呼び出す (MCP 経由)。

    NOTE: このスクリプトは MCP 環境外で動かす場合、
    ochema の HTTP API に直接 POST する必要がある。
    MCP 環境内では mcp_ochema_ask_cortex で代替。
    """
    # MCP 環境外でのフォールバック: ochema HTTP API
    import urllib.request

    payload = json.dumps({
        "model": model,
        "message": prompt,
        "system_instruction": SYSTEM_PROMPT,
        "max_tokens": max_tokens,
    })

    try:
        req = urllib.request.Request(
            "http://localhost:8765/api/cortex/ask",
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", result.get("text", str(result)))
    except Exception as e:
        return f"[Error] Cortex API call failed: {e}"


# PURPOSE: main の処理
def main() -> None:
    parser = argparse.ArgumentParser(description="Cortex Code Review (Gemini 3)")
    parser.add_argument("target", help="レビュー対象ファイル")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        choices=[DEFAULT_MODEL, PRO_MODEL],
                        help=f"使用モデル (default: {DEFAULT_MODEL})")
    parser.add_argument("--output", "-o", help="結果出力ファイル")
    parser.add_argument("--max-lines", type=int, default=200,
                        help="レビュー対象の最大行数 (default: 200)")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: {target_path} not found", file=sys.stderr)
        sys.exit(1)

    code = target_path.read_text(encoding="utf-8")
    lines = code.splitlines()
    if len(lines) > args.max_lines:
        code = "\n".join(lines[:args.max_lines])
        print(f"⚠ Truncated to {args.max_lines} lines (original: {len(lines)})")

    context = load_context()
    prompt = build_review_prompt(code, str(target_path), context)

    print(f"📋 Reviewing {target_path} with {args.model}...")
    print(f"   Context: {len(context)} chars from {CONTEXT_DIR}")
    print(f"   Code: {len(lines)} lines")

    result = call_cortex(prompt, model=args.model)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(
            f"# Cortex Review: {target_path}\n\n"
            f"**Model**: {args.model}\n\n"
            f"---\n\n{result}\n",
            encoding="utf-8",
        )
        print(f"✅ Result saved to {output_path}")
    else:
        print(f"\n{'='*60}")
        print(result)
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
