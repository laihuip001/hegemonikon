#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/ A0->Existence
"""
Periskopē CLI — Deep Research from the command line.

Usage:
    python -m mekhane.periskope.cli "Free Energy Principle"
    python -m mekhane.periskope.cli "active inference" --sources gnosis sophia
    python -m mekhane.periskope.cli "search query" --no-verify --output report.md
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="periskope",
        description="Periskopē Deep Research Engine",
    )
    parser.add_argument(
        "query",
        help="Research query",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["searxng", "brave", "tavily", "semantic_scholar", "gnosis", "sophia", "kairos"],
        default=None,
        help="Search sources to use (default: all)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Max results per source (default: 10)",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip citation verification",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--searxng-url",
        default="http://localhost:8888",
        help="SearXNG base URL",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging",
    )
    parser.add_argument(
        "--digest",
        action="store_true",
        help="Auto-digest: write results to /eat incoming",
    )
    parser.add_argument(
        "--digest-depth",
        choices=["quick", "standard", "deep"],
        default="quick",
        help="Digest template depth (default: quick)",
    )
    parser.add_argument(
        "--no-expand",
        action="store_true",
        help="Disable bilingual query expansion (W3)",
    )
    parser.add_argument(
        "--multipass",
        action="store_true",
        help="Enable multi-pass search for deeper coverage (W6)",
    )
    return parser


async def main(args: argparse.Namespace) -> int:
    """Run Periskopē research."""
    from mekhane.periskope.engine import PeriskopeEngine

    engine = PeriskopeEngine(
        searxng_url=args.searxng_url,
        max_results_per_source=args.max_results,
        verify_citations=not args.no_verify,
    )

    report = await engine.research(
        query=args.query,
        sources=args.sources,
        auto_digest=args.digest,
        digest_depth=args.digest_depth,
        expand_query=not args.no_expand,
        multipass=args.multipass,
    )

    md = report.markdown()

    if args.output:
        from pathlib import Path
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(md)

    # Summary to stderr
    print(
        f"\n--- Periskopē ---\n"
        f"Query: {report.query}\n"
        f"Results: {len(report.search_results)} from {len(report.source_counts)} sources\n"
        f"Synthesis: {len(report.synthesis)} model(s)\n"
        f"Citations: {len(report.citations)} verified\n"
        f"Time: {report.elapsed_seconds:.1f}s\n",
        file=sys.stderr,
    )
    return 0


def run() -> None:
    parser = create_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    sys.exit(asyncio.run(main(args)))


if __name__ == "__main__":
    run()
