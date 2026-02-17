# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/periskope/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

S5 → 検索機能のCLI統合が必要
   → 検索エンジンの操作インタフェースが必要
   → cli.py が担う

Q.E.D.

---

Periskopē CLI - コマンドラインインタフェース

Usage:
    python -m mekhane.periskope.cli search --query "free energy principle"
    python mekhane/periskope/cli.py health
"""

import argparse
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional, Callable, Any

# Add Hegemonikon root to path for imports
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = (
    _THIS_DIR.parent.parent
)  # mekhane/periskope -> mekhane -> Hegemonikon
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.periskope.searchers.searxng import SearXNGSearcher, CATEGORY_GENERAL, CATEGORY_SCIENCE, CATEGORY_NEWS, CATEGORY_IT
from mekhane.periskope.models import SearchResult


# PURPOSE: Execute search via SearXNG
async def cmd_search(args: argparse.Namespace) -> int:
    """Execute search via SearXNG."""
    searcher = SearXNGSearcher(base_url=args.url)

    categories = []
    if args.science:
        categories.append(CATEGORY_SCIENCE)
    if args.news:
        categories.append(CATEGORY_NEWS)
    if args.it:
        categories.append(CATEGORY_IT)
    if not categories:
        categories = [CATEGORY_GENERAL]

    print(f"[Search] Query: {args.query}")
    print(f"[Search] Categories: {categories}")

    try:
        results = await searcher.search(
            query=args.query,
            categories=categories,
            max_results=args.limit,
            language=args.lang
        )

        if not results:
            print("No results found.")
            return 0

        print(f"\nFound {len(results)} results:\n")
        print("-" * 70)

        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r.title}")
            print(f"    URL: {r.url}")
            print(f"    Source: {r.source.value} | Relevance: {r.relevance:.2f}")
            print(f"    Snippet: {r.snippet}")
            if r.timestamp:
                print(f"    Time: {r.timestamp}")

        print("\n" + "-" * 70)
        return 0

    except Exception as e:
        print(f"[Error] Search failed: {e}")
        return 1
    finally:
        await searcher.close()


# PURPOSE: Check SearXNG health
async def cmd_health(args: argparse.Namespace) -> int:
    """Check SearXNG health."""
    searcher = SearXNGSearcher(base_url=args.url)
    try:
        is_healthy = await searcher.health_check()
        if is_healthy:
            print(f"✅ SearXNG at {args.url} is HEALTHY")
            return 0
        else:
            print(f"❌ SearXNG at {args.url} is UNHEALTHY")
            return 1
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return 1
    finally:
        await searcher.close()


# PURPOSE: CLI Entry Point wrapper for async functions
def cmd_wrapper(func: Callable[[argparse.Namespace], Any]) -> Callable[[argparse.Namespace], int]:
    def wrapper(args: argparse.Namespace) -> int:
        return asyncio.run(func(args))
    return wrapper


# PURPOSE: CLI Entry Point
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Periskopē - Deep Research CLI",
        prog="periskope",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # search
    p_search = subparsers.add_parser("search", help="Execute search")
    p_search.add_argument("--query", "-q", required=True, help="Search query")
    p_search.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    p_search.add_argument("--url", default="http://localhost:8888", help="SearXNG URL")
    p_search.add_argument("--lang", default="ja-JP", help="Language code")
    p_search.add_argument("--science", action="store_true", help="Search science category")
    p_search.add_argument("--news", action="store_true", help="Search news category")
    p_search.add_argument("--it", action="store_true", help="Search IT category")
    p_search.set_defaults(func=cmd_wrapper(cmd_search))

    # health
    p_health = subparsers.add_parser("health", help="Check search engine health")
    p_health.add_argument("--url", default="http://localhost:8888", help="SearXNG URL")
    p_health.set_defaults(func=cmd_wrapper(cmd_health))

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
