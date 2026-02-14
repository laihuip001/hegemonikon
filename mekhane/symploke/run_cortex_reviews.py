#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- mekhane/symploke/ O4→Cortex直叩きレビュー→run_cortex_reviews が担う
# PURPOSE: CortexClient (Gemini API 直叩き) による Specialist Reviews 実行
"""
Cortex Specialist Reviews v1.0

Jules API の代わりに CortexClient (Gemini API 直叩き) でレビューを実行する。
LS の不安定性を回避し、レビューテキストを直接取得。

Usage:
    # dry-run (プロンプト確認のみ)
    python run_cortex_reviews.py --target mekhane/ochema/cortex_client.py --dry-run

    # 実行 (サンプル 3 人)
    python run_cortex_reviews.py --target mekhane/ochema/cortex_client.py --sample 3

    # git-diff モード (変更ファイル自動取得)
    python run_cortex_reviews.py --target-mode git-diff --sample 5

    # カテゴリ指定
    python run_cortex_reviews.py --target mekhane/ochema/cortex_client.py -c security

    # モデル指定
    python run_cortex_reviews.py --target mekhane/ochema/cortex_client.py --model gemini-2.5-pro
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Local imports
try:
    from specialist_v2 import (
        ALL_SPECIALISTS,
        Specialist,
        generate_prompt,
        get_all_categories,
        get_specialists_by_category,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from specialist_v2 import (
        ALL_SPECIALISTS,
        Specialist,
        generate_prompt,
        get_all_categories,
        get_specialists_by_category,
    )

# CortexClient import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mekhane.ochema.cortex_client import CortexClient, CortexError

# === Settings ===
DEFAULT_MODEL = os.getenv("CORTEX_REVIEW_MODEL", "gemini-2.0-flash")
DEFAULT_DELAY = float(os.getenv("CORTEX_REVIEW_DELAY", "1.0"))
REVIEWS_DIR = Path("mekhane/symploke/reviews")
PROJECT_ROOT = Path(__file__).parent.parent.parent


# PURPOSE: ターゲットファイルのソースコードを読み込み、レビュープロンプトに埋め込む
def read_target_source(target_file: str) -> str:
    """Read target file source code for inline review."""
    full_path = PROJECT_ROOT / target_file
    if not full_path.exists():
        return f"[ERROR: File not found: {target_file}]"
    try:
        content = full_path.read_text(encoding="utf-8")
        # Truncate very large files
        lines = content.split("\n")
        if len(lines) > 500:
            content = "\n".join(lines[:500]) + f"\n\n... (truncated, {len(lines)} total lines)"
        return content
    except Exception as e:
        return f"[ERROR reading {target_file}: {e}]"


# PURPOSE: Specialist プロンプトを Cortex 向けに変換 — PR 作成指示をテキスト出力指示に置換
def adapt_prompt_for_cortex(
    spec: Specialist,
    target_file: str,
    source_code: str,
) -> str:
    """Adapt specialist prompt for Cortex (text review instead of PR)."""
    base_prompt = generate_prompt(spec, target_file)

    # Replace file creation instruction with direct output instruction
    base_prompt = base_prompt.replace(
        "**重要**: 上記ファイルを作成してコミットしてください。",
        "**重要**: レビュー結果を直接テキストで出力してください。ファイル作成は不要です。",
    )

    # Prepend source code for inline review
    adapted = f"""以下のソースコードをレビューしてください。

## ソースコード (`{target_file}`)

```python
{source_code}
```

---

{base_prompt}"""

    return adapted


# PURPOSE: git diff で変更ファイルを取得 (run_specialists.py の select_targets を簡易化)
def get_git_diff_files(max_files: int = 10) -> list[str]:
    """Get changed Python files from git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1..HEAD", "--", "*.py"],
            capture_output=True, text=True, timeout=10,
            cwd=str(PROJECT_ROOT),
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        if not files:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached", "--", "*.py"],
                capture_output=True, text=True, timeout=10,
                cwd=str(PROJECT_ROOT),
            )
            files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        # Filter out test files, prioritize larger files
        scored = []
        for f in files:
            score = 1.0
            if "test_" in f or "conftest" in f:
                score = 0.3
            elif "__init__" in f:
                score = 0.1
            scored.append((score, f))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [f for _, f in scored[:max_files]]
    except Exception as e:
        print(f"WARNING: git-diff failed: {e}")
        return []


# PURPOSE: 単一の Specialist レビューを CortexClient で実行
def run_single_review(
    client: CortexClient,
    spec: Specialist,
    target_file: str,
    source_code: str,
    output_dir: Path,
) -> dict:
    """Run a single specialist review via CortexClient.

    Returns:
        dict with id, name, category, status, review_text, file_path, etc.
    """
    prompt = adapt_prompt_for_cortex(spec, target_file, source_code)

    start_time = time.time()
    try:
        resp = client.ask(
            prompt,
            system_instruction=(
                f"あなたは {spec.name} です。{spec.domain} の専門家として、"
                f"以下の原理に基づいてコードレビューを行います: {spec.principle}\n"
                "レビュー結果をマークダウン形式で出力してください。"
            ),
            max_tokens=4096,
        )
        elapsed = time.time() - start_time

        # Save review to file
        review_file = output_dir / f"{spec.id.lower()}_review.md"
        review_content = f"""# {spec.name} レビュー

> **ID**: {spec.id}
> **Target**: `{target_file}`
> **Model**: {resp.model}
> **Tokens**: {resp.token_usage.get('total_tokens', '?')}
> **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

{resp.text}
"""
        review_file.write_text(review_content, encoding="utf-8")

        return {
            "id": spec.id,
            "name": spec.name,
            "category": spec.category,
            "status": "completed",
            "model": resp.model,
            "tokens": resp.token_usage.get("total_tokens", 0),
            "elapsed": round(elapsed, 1),
            "review_file": str(review_file),
            "review_length": len(resp.text),
        }

    except CortexError as e:
        elapsed = time.time() - start_time
        return {
            "id": spec.id,
            "name": spec.name,
            "category": spec.category,
            "status": "failed",
            "error": str(e),
            "elapsed": round(elapsed, 1),
        }


# PURPOSE: メイン実行 — CLI パーサー + バッチレビュー
def main():
    """Main execution."""
    available_categories = ["all"] + get_all_categories()

    parser = argparse.ArgumentParser(
        description="Cortex Specialist Reviews v1.0 — Gemini API 直叩きレビュー"
    )
    parser.add_argument(
        "--target", "-t",
        default="mekhane/ochema/cortex_client.py",
        help="Target file to review",
    )
    parser.add_argument(
        "--target-mode",
        choices=["fixed", "git-diff"],
        default="fixed",
        help="Target selection mode",
    )
    parser.add_argument(
        "--category", "-c",
        choices=available_categories,
        default="all",
        help="Specialist category",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Gemini model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--sample", "-s",
        type=int,
        help="Random sample N specialists",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay between requests (default: {DEFAULT_DELAY}s)",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="",
        help="Output directory for reviews",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without executing",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available categories",
    )
    parser.add_argument(
        "--quota",
        action="store_true",
        help="Show current Gemini quota",
    )

    args = parser.parse_args()

    # Category list
    if args.list_categories:
        print("=== Available Categories ===")
        for cat in get_all_categories():
            count = len(get_specialists_by_category(cat))
            print(f"  {cat}: {count}人")
        print(f"\n  all: {len(ALL_SPECIALISTS)}人")
        return

    # Quota check
    if args.quota:
        client = CortexClient()
        quota = client.retrieve_quota()
        print("=== Gemini Quota ===")
        for bucket in quota.get("buckets", []):
            model = bucket.get("modelId", "?")
            remaining = bucket.get("remainingFraction", 0)
            reset = bucket.get("resetTime", "?")
            bar = "█" * int(remaining * 20) + "░" * (20 - int(remaining * 20))
            print(f"  {model:30s} |{bar}| {remaining*100:.1f}%  (reset: {reset})")
        return

    # Target selection
    if args.target_mode == "git-diff":
        targets = get_git_diff_files()
    else:
        targets = [args.target]

    if not targets:
        print("ERROR: No target files found.")
        return

    # Specialist filtering
    if args.category == "all":
        specialists = list(ALL_SPECIALISTS)
    else:
        specialists = get_specialists_by_category(args.category)

    # Random sampling
    if args.sample:
        import random
        specialists = random.sample(specialists, min(args.sample, len(specialists)))

    # Output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = Path(
        args.output_dir if args.output_dir
        else f"logs/cortex_reviews/{timestamp}"
    )

    # Summary
    print(f"{'='*60}")
    print(f"Cortex Specialist Reviews v1.0")
    print(f"{'='*60}")
    print(f"  Model:        {args.model}")
    print(f"  Targets:      {len(targets)} files")
    print(f"  Specialists:  {len(specialists)}")
    print(f"  Output:       {output_dir}")
    print(f"  Delay:        {args.delay}s")
    print(f"{'='*60}")

    if args.dry_run:
        for target in targets[:1]:
            source = read_target_source(target)
            for spec in specialists[:2]:
                print(f"\n--- {spec.id} {spec.name} ({spec.category}) ---")
                prompt = adapt_prompt_for_cortex(spec, target, source)
                print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        remaining = len(specialists) - 2
        if remaining > 0:
            print(f"\n  ... and {remaining} more specialists")
        return

    # Execute reviews
    client = CortexClient(model=args.model)
    all_results = []

    for file_idx, target in enumerate(targets, 1):
        print(f"\n[{file_idx}/{len(targets)}] {target}")
        print("-" * 40)

        source = read_target_source(target)
        file_output_dir = output_dir / Path(target).stem
        file_output_dir.mkdir(parents=True, exist_ok=True)

        for i, spec in enumerate(specialists):
            if i > 0:
                time.sleep(args.delay)

            print(f"  [{i+1}/{len(specialists)}] {spec.id} {spec.name[:30]}...", end=" ")
            result = run_single_review(client, spec, target, source, file_output_dir)

            if result["status"] == "completed":
                tokens = result.get("tokens", 0)
                elapsed = result.get("elapsed", 0)
                print(f"✅ ({tokens} tok, {elapsed}s)")
            else:
                print(f"❌ {result.get('error', 'unknown')[:50]}")

            all_results.append(result)

    # Summary report
    completed = sum(1 for r in all_results if r["status"] == "completed")
    failed = sum(1 for r in all_results if r["status"] == "failed")
    total_tokens = sum(r.get("tokens", 0) for r in all_results)

    print(f"\n{'='*60}")
    print(f"=== Results ===")
    print(f"  Completed: {completed}/{len(all_results)}")
    print(f"  Failed:    {failed}/{len(all_results)}")
    print(f"  Tokens:    {total_tokens:,}")
    success_rate = (completed / len(all_results) * 100) if all_results else 0
    print(f"  Rate:      {success_rate:.1f}%")
    print(f"  Output:    {output_dir}")
    print(f"{'='*60}")

    # Save summary
    summary_file = output_dir / "summary.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "version": "cortex-1.0",
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "targets": targets,
        "total_specialists": len(all_results),
        "completed": completed,
        "failed": failed,
        "total_tokens": total_tokens,
        "success_rate": round(success_rate, 1),
        "results": all_results,
    }
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nSummary saved: {summary_file}")


if __name__ == "__main__":
    main()
