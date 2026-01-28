"""
Gnōsis CLI - コマンドラインインタフェース

Usage:
    python -m mekhane.anamnesis.cli collect --source arxiv --query "transformer" --limit 10
    python mekhane/anamnesis/cli.py search "attention mechanism"
    python mekhane/anamnesis/cli.py stats
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime, timedelta
from mekhane.anamnesis.ux_utils import print_header, print_success, print_error, print_warning, Spinner

# Add Hegemonikon root to path for imports (mekhane package)
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = _THIS_DIR.parent.parent  # mekhane/anamnesis -> mekhane -> Hegemonikon
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

# Configuration
DATA_DIR = _HEGEMONIKON_ROOT / "gnosis_data"
STATE_FILE = DATA_DIR / "state.json"


def update_state():
    """Update last collected timestamp."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        state = {}
        if STATE_FILE.exists():
            try:
                state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        state["last_collected_at"] = datetime.now().isoformat()
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        print_warning(f"Failed to update state: {e}")


def cmd_check_freshness(args):
    """
    Check if collection is needed based on threshold days.
    Output JSON: {"status": "fresh"|"stale"|"missing", "days_elapsed": int|null}
    """
    threshold = timedelta(days=args.threshold)
    result = {"status": "missing", "days_elapsed": None}
    
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            last_str = state.get("last_collected_at")
            if last_str:
                last_time = datetime.fromisoformat(last_str)
                elapsed = datetime.now() - last_time
                days = elapsed.days
                
                if elapsed > threshold:
                    result = {"status": "stale", "days_elapsed": days}
                else:
                    result = {"status": "fresh", "days_elapsed": days}
        except Exception:
            result = {"status": "error", "days_elapsed": None}
            
    print(json.dumps(result))
    # Return 0 if fresh, 1 if stale/missing (to allow simple shell checks)
    return 0 if result["status"] == "fresh" else 1


def cmd_collect(args):
    """論文収集"""
    from mekhane.anamnesis.collectors.arxiv import ArxivCollector
    from mekhane.anamnesis.collectors.semantic_scholar import SemanticScholarCollector
    from mekhane.anamnesis.collectors.openalex import OpenAlexCollector
    from mekhane.anamnesis.index import GnosisIndex
    
    collectors = {
        "arxiv": ArxivCollector,
        "semantic_scholar": SemanticScholarCollector,
        "s2": SemanticScholarCollector,
        "openalex": OpenAlexCollector,
        "oa": OpenAlexCollector,
    }
    
    source = args.source.lower()
    if source not in collectors:
        print_error(f"Unknown source: {args.source}")
        print_error(f"Available: {', '.join(collectors.keys())}")
        return 1
    
    print_header(f"Collect: {source}")
    print(f"Query: {args.query}, Limit: {args.limit}")
    
    try:
        with Spinner(f"Collecting from {source}..."):
            collector = collectors[source]()
            papers = collector.search(args.query, max_results=args.limit)

        print_success(f"Found {len(papers)} papers")
        
        if papers and not args.dry_run:
            with Spinner("Indexing..."):
                index = GnosisIndex()
                added = index.add_papers(papers)
            print_success(f"Added {added} to index")
            update_state()  # Update timestamp
        elif args.dry_run:
            print_warning("Dry run - not adding to index")
            for p in papers[:5]:
                print(f"  - {p.title[:60]}...")
        
        return 0
    except Exception as e:
        print_error(str(e))
        return 1


def cmd_collect_all(args):
    """全ソースから収集"""
    from mekhane.anamnesis.collectors.arxiv import ArxivCollector
    from mekhane.anamnesis.collectors.semantic_scholar import SemanticScholarCollector
    from mekhane.anamnesis.collectors.openalex import OpenAlexCollector
    from mekhane.anamnesis.index import GnosisIndex
    
    collectors = [
        ("arxiv", ArxivCollector()),
        ("semantic_scholar", SemanticScholarCollector()),
        ("openalex", OpenAlexCollector()),
    ]
    
    print_header(f"Collect All: {args.query}")
    
    all_papers = []
    for name, collector in collectors:
        try:
            with Spinner(f"Collecting from {name}..."):
                papers = collector.search(args.query, max_results=args.limit)
            print_success(f"{name}: Found {len(papers)} papers")
            all_papers.extend(papers)
        except Exception as e:
            print_error(f"{name}: {e}")
    
    if all_papers and not args.dry_run:
        with Spinner("Indexing..."):
            index = GnosisIndex()
            added = index.add_papers(all_papers, dedupe=True)
        print_success(f"Added {added} unique papers to index")
        update_state()  # Update timestamp
    
    return 0


def cmd_search(args):
    """論文検索"""
    from mekhane.anamnesis.index import GnosisIndex
    
    print_header(f"Search: {args.query}")
    
    with Spinner("Searching index..."):
        index = GnosisIndex()
        results = index.search(args.query, k=args.limit)
    
    if not results:
        print_warning("No results found")
        return 0
    
    print_success(f"Found {len(results)} results:")
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
    from mekhane.anamnesis.index import GnosisIndex
    
    index = GnosisIndex()
    stats = index.stats()
    
    print_header("Gnōsis Index Statistics")
    print(f"Total Papers: {stats['total']}")
    print(f"With DOI: {stats.get('unique_dois', 0)}")
    print(f"With arXiv ID: {stats.get('unique_arxiv', 0)}")
    print("\nBy Source:")
    for source, count in stats.get("sources", {}).items():
        print(f"  {source}: {count}")
    
    # Show freshness
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            print(f"Last Collected: {state.get('last_collected_at', 'Unknown')}")
        except:
            pass
            
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
    
    # check-freshness
    p_check = subparsers.add_parser("check-freshness", help="Check collection freshness")
    p_check.add_argument("--threshold", "-t", type=int, default=7, help="Threshold days (default: 7)")
    p_check.set_defaults(func=cmd_check_freshness)
    
    # logs (Antigravity Output Panel Logs)
    from mekhane.anamnesis.antigravity_logs import cmd_logs
    p_logs = subparsers.add_parser("logs", help="Antigravity Output Panel logs")
    p_logs.add_argument("--session", "-s", help="Session ID (timestamp, e.g. 20260125T145530)")
    p_logs.add_argument("--list", "-L", action="store_true", help="List available sessions")
    p_logs.add_argument("--errors", "-e", action="store_true", help="Show errors only")
    p_logs.add_argument("--models", "-m", action="store_true", help="Show detected models only")
    p_logs.add_argument("--tokens", "-t", action="store_true", help="Show token usage only")
    p_logs.add_argument("--limit", "-l", type=int, default=10, help="Max items to show")
    p_logs.set_defaults(func=cmd_logs)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
