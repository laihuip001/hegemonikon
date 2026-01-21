"""
Gnōsis CLI - コマンドラインインタフェース

Usage:
    python -m gnosis.cli collect --source arxiv --query "transformer" --limit 10
    python -m gnosis.cli search "attention mechanism"
    python -m gnosis.cli stats
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent to path for standalone execution
sys.path.insert(0, str(Path(__file__).parent.parent))


def cmd_collect(args):
    """論文収集"""
    from gnosis.collectors.arxiv import ArxivCollector
    from gnosis.collectors.semantic_scholar import SemanticScholarCollector
    from gnosis.collectors.openalex import OpenAlexCollector
    from gnosis.index import GnosisIndex
    
    collectors = {
        "arxiv": ArxivCollector,
        "semantic_scholar": SemanticScholarCollector,
        "s2": SemanticScholarCollector,
        "openalex": OpenAlexCollector,
        "oa": OpenAlexCollector,
    }
    
    source = args.source.lower()
    if source not in collectors:
        print(f"Unknown source: {args.source}")
        print(f"Available: {', '.join(collectors.keys())}")
        return 1
    
    print(f"[Collect] Source: {source}, Query: {args.query}, Limit: {args.limit}")
    
    try:
        collector = collectors[source]()
        papers = collector.search(args.query, max_results=args.limit)
        print(f"[Collect] Found {len(papers)} papers")
        
        if papers and not args.dry_run:
            index = GnosisIndex()
            added = index.add_papers(papers)
            print(f"[Collect] Added {added} to index")
        elif args.dry_run:
            print("[Collect] Dry run - not adding to index")
            for p in papers[:5]:
                print(f"  - {p.title[:60]}...")
        
        return 0
    except Exception as e:
        print(f"[Error] {e}")
        return 1


def cmd_collect_all(args):
    """全ソースから収集"""
    from gnosis.collectors.arxiv import ArxivCollector
    from gnosis.collectors.semantic_scholar import SemanticScholarCollector
    from gnosis.collectors.openalex import OpenAlexCollector
    from gnosis.index import GnosisIndex
    
    collectors = [
        ("arxiv", ArxivCollector()),
        ("semantic_scholar", SemanticScholarCollector()),
        ("openalex", OpenAlexCollector()),
    ]
    
    print(f"[CollectAll] Query: {args.query}, Limit per source: {args.limit}")
    
    all_papers = []
    for name, collector in collectors:
        try:
            print(f"  Collecting from {name}...")
            papers = collector.search(args.query, max_results=args.limit)
            print(f"    Found {len(papers)} papers")
            all_papers.extend(papers)
        except Exception as e:
            print(f"    Error: {e}")
    
    if all_papers and not args.dry_run:
        index = GnosisIndex()
        added = index.add_papers(all_papers, dedupe=True)
        print(f"[CollectAll] Added {added} unique papers to index")
    
    return 0


def cmd_search(args):
    """論文検索"""
    from gnosis.index import GnosisIndex
    
    print(f"[Search] Query: {args.query}")
    
    index = GnosisIndex()
    results = index.search(args.query, k=args.limit)
    
    if not results:
        print("No results found")
        return 0
    
    print(f"\nFound {len(results)} results:\n")
    print("-" * 70)
    
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.get('title', 'Untitled')[:70]}")
        print(f"    Source: {r.get('source')} | Citations: {r.get('citations', 'N/A')}")
        print(f"    Authors: {r.get('authors', '')[:60]}...")
        print(f"    Abstract: {r.get('abstract', '')[:150]}...")
        if r.get('url'):
            print(f"    URL: {r.get('url')}")
    
    print("\n" + "-" * 70)
    return 0


def cmd_stats(args):
    """インデックス統計"""
    from gnosis.index import GnosisIndex
    
    index = GnosisIndex()
    stats = index.stats()
    
    print("\n[Gnōsis Index Statistics]")
    print("=" * 40)
    print(f"Total Papers: {stats['total']}")
    print(f"With DOI: {stats.get('unique_dois', 0)}")
    print(f"With arXiv ID: {stats.get('unique_arxiv', 0)}")
    print("\nBy Source:")
    for source, count in stats.get("sources", {}).items():
        print(f"  {source}: {count}")
    print("=" * 40)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Gnōsis - Knowledge Foundation CLI",
        prog="gnosis",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # collect
    p_collect = subparsers.add_parser("collect", help="Collect papers from a source")
    p_collect.add_argument("--source", "-s", required=True, help="Source: arxiv, s2, openalex")
    p_collect.add_argument("--query", "-q", required=True, help="Search query")
    p_collect.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    p_collect.add_argument("--dry-run", action="store_true", help="Don't add to index")
    p_collect.set_defaults(func=cmd_collect)
    
    # collect-all
    p_all = subparsers.add_parser("collect-all", help="Collect from all sources")
    p_all.add_argument("--query", "-q", required=True, help="Search query")
    p_all.add_argument("--limit", "-l", type=int, default=10, help="Max results per source")
    p_all.add_argument("--dry-run", action="store_true", help="Don't add to index")
    p_all.set_defaults(func=cmd_collect_all)
    
    # search
    p_search = subparsers.add_parser("search", help="Search indexed papers")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    p_search.set_defaults(func=cmd_search)
    
    # stats
    p_stats = subparsers.add_parser("stats", help="Show index statistics")
    p_stats.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
