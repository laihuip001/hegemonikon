# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → 永続化の操作インタフェースが必要
   → cli.py が担う

Q.E.D.

---

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

# Add Hegemonikon root to path for imports (mekhane package)
_THIS_DIR = Path(__file__).parent
_HEGEMONIKON_ROOT = (
    _THIS_DIR.parent.parent
)  # mekhane/anamnesis -> mekhane -> Hegemonikon
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

# Configuration
DATA_DIR = _HEGEMONIKON_ROOT / "gnosis_data"
STATE_FILE = DATA_DIR / "state.json"


# PURPOSE: Update last collected timestamp.
def update_state():
    """Update last collected timestamp."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        state = {}
        if STATE_FILE.exists():
            try:
                state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass  # TODO: Add proper error handling # noqa: AI-ALL

        state["last_collected_at"] = datetime.now().isoformat()
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[Warning] Failed to update state: {e}")


# PURPOSE: Check if collection is needed based on threshold days.
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
    # Return 0 if fresh, 1 if stale/missing (to allow simple shell checks) # noqa: AI-ALL
    return 0 if result["status"] == "fresh" else 1


# PURPOSE: 論文収集
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
            update_state()  # Update timestamp
        elif args.dry_run:
            print("[Collect] Dry run - not adding to index")
            for p in papers[:5]:
                print(f"  - {p.title[:60]}...")

        return 0
    except Exception as e:
        print(f"[Error] {e}")
        return 1


# PURPOSE: 全ソースから収集
def cmd_collect_all(args):  # noqa: AI-ALL
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
        update_state()  # Update timestamp

    return 0


# PURPOSE: 論文検索
def cmd_search(args):
    """論文検索"""
    from mekhane.anamnesis.index import GnosisIndex

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
        if r.get("url"):
            print(f"    URL: {r.get('url')}")

    print("\n" + "-" * 70)
    return 0


# PURPOSE: インデックス統計
def cmd_stats(args):
    """インデックス統計"""
    from mekhane.anamnesis.index import GnosisIndex

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

    # Show freshness
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            print(f"Last Collected: {state.get('last_collected_at', 'Unknown')}")
        except Exception:
            pass  # TODO: Add proper error handling # noqa: AI-ALL

    print("=" * 40)

    return 0


# PURPOSE: PKS 能動的プッシュ
def cmd_proactive(args):
    """PKS 能動的プッシュ"""
    from mekhane.pks.pks_engine import PKSEngine
    from mekhane.pks.narrator import PKSNarrator
    from mekhane.pks.matrix_view import PKSMatrixView

    # コンテキスト設定
    topics = [t.strip() for t in args.context.split(",")] if args.context else []

    if not topics:
        print("[PKS] --context を指定してください (例: --context 'FEP,CCL')")
        return 1

    engine = PKSEngine(threshold=args.threshold, max_push=args.limit)
    engine.set_context(topics=topics)

    print(f"[PKS] Context: {topics}")
    print(f"[PKS] Threshold: {args.threshold}, Max: {args.limit}")
    print()

    nuggets = engine.proactive_push(k=args.limit * 4)

    if not nuggets:
        print("📭 プッシュ対象の知識はありません。")
        return 0

    # Push Report
    print(engine.format_push_report(nuggets))

    # Narrator (--narrate)
    if args.narrate:
        narrator = PKSNarrator()
        narratives = narrator.narrate_batch(nuggets[:3])
        print()
        print(narrator.format_report(narratives))

    # Matrix View (--matrix)
    if args.matrix:
        matrix = PKSMatrixView()
        print()
        print(matrix.generate(nuggets))

    return 0


# PURPOSE: Link Engine — ファイル間リレーション解析
def cmd_links(args):
    """Link Engine — ファイル間リレーション解析"""
    from mekhane.pks.links.link_engine import LinkEngine

    target_dir = Path(args.directory).resolve()
    if not target_dir.exists():
        print(f"[Links] Directory not found: {target_dir}")
        return 1

    engine = LinkEngine(target_dir)
    idx = engine.build_index()

    if args.backlinks:
        # 特定ファイルの backlinks
        links = engine.get_backlinks(args.backlinks)
        print(f"\n[Backlinks for '{args.backlinks}'] {len(links)} found:\n")
        for link in links:
            print(f"  ← {link.source}:{link.line_number}  context: {link.context[:60]}")
        return 0

    if args.orphans:
        orphans = engine.get_orphans()
        print(f"\n[Orphans] {len(orphans)} files with no incoming links:\n")
        for o in orphans:
            print(f"  • {o}")
        return 0

    if args.graph == "json":
        print(engine.export_graph_json())
        return 0

    if args.graph == "mermaid":
        print(engine.export_graph_mermaid())
        return 0

    # Default: summary
    print(engine.summary_markdown())
    return 0


# PURPOSE: 関数: main
def main():
    parser = argparse.ArgumentParser(
        description="Gnōsis - Knowledge Foundation CLI",
        prog="gnosis",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # collect
    p_collect = subparsers.add_parser("collect", help="Collect papers from a source")
    p_collect.add_argument(
        "--source", "-s", required=True, help="Source: arxiv, s2, openalex"
    )
    p_collect.add_argument("--query", "-q", required=True, help="Search query")
    p_collect.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    p_collect.add_argument("--dry-run", action="store_true", help="Don't add to index")
    p_collect.set_defaults(func=cmd_collect)

    # collect-all
    p_all = subparsers.add_parser("collect-all", help="Collect from all sources")
    p_all.add_argument("--query", "-q", required=True, help="Search query")
    p_all.add_argument(
        "--limit", "-l", type=int, default=10, help="Max results per source"
    )
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
    p_check = subparsers.add_parser(
        "check-freshness", help="Check collection freshness"
    )
    p_check.add_argument(
        "--threshold", "-t", type=int, default=7, help="Threshold days (default: 7)"
    )
    p_check.set_defaults(func=cmd_check_freshness)

    # logs (Antigravity Output Panel Logs)
    from mekhane.anamnesis.antigravity_logs import cmd_logs

    p_logs = subparsers.add_parser("logs", help="Antigravity Output Panel logs")
    p_logs.add_argument(
        "--session", "-s", help="Session ID (timestamp, e.g. 20260125T145530)"
    )
    p_logs.add_argument(
        "--list", "-L", action="store_true", help="List available sessions"
    )
    p_logs.add_argument("--errors", "-e", action="store_true", help="Show errors only")
    p_logs.add_argument(
        "--models", "-m", action="store_true", help="Show detected models only"
    )
    p_logs.add_argument(
        "--tokens", "-t", action="store_true", help="Show token usage only"
    )
    p_logs.add_argument("--limit", "-l", type=int, default=10, help="Max items to show")
    p_logs.set_defaults(func=cmd_logs)

    # proactive (PKS Push)
    p_proactive = subparsers.add_parser(
        "proactive", help="PKS proactive knowledge push"
    )
    p_proactive.add_argument(
        "--context", "-c", required=True, help="Topics (comma-separated)"
    )
    p_proactive.add_argument(
        "--threshold", "-T", type=float, default=0.5, help="Relevance threshold"
    )
    p_proactive.add_argument(
        "--limit", "-l", type=int, default=5, help="Max push count"
    )
    p_proactive.add_argument(
        "--narrate", "-n", action="store_true", help="Include Narrator dialogue"
    )
    p_proactive.add_argument(
        "--matrix", "-m", action="store_true", help="Include Matrix comparison table"
    )
    p_proactive.set_defaults(func=cmd_proactive)

    # links (Link Engine)
    p_links = subparsers.add_parser("links", help="File link analysis")
    p_links.add_argument(
        "directory", nargs="?", default=".", help="Target directory (default: cwd)"
    )
    p_links.add_argument(
        "--backlinks", "-b", help="Show backlinks for a specific file/stem"
    )
    p_links.add_argument(
        "--orphans", "-o", action="store_true", help="Show orphan files"
    )
    p_links.add_argument(
        "--graph", "-g", choices=["json", "mermaid"], help="Export graph format"
    )
    p_links.set_defaults(func=cmd_links)

    # chat (Gnōsis Chat — RAG 対話)
    from mekhane.anamnesis.gnosis_chat import cmd_chat

    p_chat = subparsers.add_parser(
        "chat", help="Interactive RAG chat with knowledge base"
    )
    p_chat.add_argument(
        "question", nargs="?", default=None,
        help="Question to ask (omit for interactive mode)"
    )
    p_chat.add_argument(
        "--top-k", "-k", type=int, default=5,
        help="Number of documents to retrieve (default: 5)"
    )
    p_chat.add_argument(
        "--max-tokens", "-m", type=int, default=512,
        help="Max tokens to generate (default: 512)"
    )
    p_chat.add_argument(
        "--index", "-i", action="store_true",
        help="Index all knowledge files before chatting"
    )
    p_chat.add_argument(
        "--steering", "-s", default="hegemonikon",
        choices=["hegemonikon", "neutral", "academic"],
        help="Steering profile (default: hegemonikon)"
    )
    p_chat.set_defaults(func=cmd_chat)

    # retrieve (LLM 不使用 — 検索結果のみ返す)
    from mekhane.anamnesis.gnosis_chat import cmd_retrieve

    p_retrieve = subparsers.add_parser(
        "retrieve", help="Retrieve context only (no LLM generation)"
    )
    p_retrieve.add_argument(
        "query", help="Search query"
    )
    p_retrieve.add_argument(
        "--top-k", "-k", type=int, default=5,
        help="Number of documents to retrieve (default: 5)"
    )
    p_retrieve.set_defaults(func=cmd_retrieve)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
