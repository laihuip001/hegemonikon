# PROOF: [L2/Mekhanē] <- mekhane/periskope/
"""
PROOF: [L2/Mekhanē] This file must exist.

P3 → Need for external research capabilities.
   → Interface for executing Periskopē search and synthesis.
   → cli.py provides this interface.

Q.E.D.
"""

# PURPOSE: Command-line interface for Periskopē Deep Research Engine.

import argparse
import asyncio
import sys
from typing import List

from mekhane.periskope.models import SearchResult, SearchSource
from mekhane.periskope.searchers.internal_searcher import GnosisSearcher, SophiaSearcher, KairosSearcher

# Optional imports for external searchers
try:
    from mekhane.periskope.searchers.searxng import SearXNGSearcher
except ImportError:
    SearXNGSearcher = None

try:
    from mekhane.periskope.searchers.exa_searcher import ExaSearcher
except ImportError:
    ExaSearcher = None


async def run_search(query: str, sources: List[str], limit: int) -> List[SearchResult]:
    results: List[SearchResult] = []
    tasks = []

    for source_str in sources:
        # Convert string to enum for safer handling if needed,
        # but string comparison works with str, Enum.
        try:
            source = SearchSource(source_str)
        except ValueError:
            print(f"Warning: Invalid source '{source_str}'")
            continue

        if source == SearchSource.GNOSIS:
            tasks.append(GnosisSearcher().search(query, max_results=limit))
        elif source == SearchSource.SOPHIA:
            tasks.append(SophiaSearcher().search(query, max_results=limit))
        elif source == SearchSource.KAIROS:
            tasks.append(KairosSearcher().search(query, max_results=limit))
        elif source == SearchSource.SEARXNG:
            if SearXNGSearcher:
                tasks.append(SearXNGSearcher().search(query, max_results=limit))
            else:
                print("Warning: SearXNG searcher not available.")
        elif source == SearchSource.EXA:
            if ExaSearcher:
                tasks.append(ExaSearcher().search(query, max_results=limit))
            else:
                print("Warning: Exa searcher not available.")
        else:
            print(f"Warning: Source '{source}' not implemented in CLI.")

    if tasks:
        search_results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for res in search_results_list:
            if isinstance(res, list):
                results.extend(res)
            elif isinstance(res, Exception):
                print(f"Error during search: {res}")

    return results


def print_results(results: List[SearchResult]):
    print(f"Found {len(results)} results:\n")
    for i, res in enumerate(results, 1):
        print(f"[{i}] {res.title}")
        print(f"    Source: {res.source}")
        if res.url:
            print(f"    URL: {res.url}")
        snippet = res.snippet.replace("\n", " ")
        if len(snippet) > 100:
            snippet = snippet[:97] + "..."
        print(f"    Snippet: {snippet}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Periskopē Deep Research Engine CLI")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--sources", nargs="+",
                        choices=[s.value for s in SearchSource],
                        default=["gnosis", "sophia"],
                        help="Sources to search")
    parser.add_argument("--limit", type=int, default=5, help="Max results per source")

    args = parser.parse_args()

    print(f"Searching for '{args.query}' in {args.sources}...")

    try:
        results = asyncio.run(run_search(args.query, args.sources, args.limit))
        print_results(results)
    except KeyboardInterrupt:
        print("\nSearch interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
