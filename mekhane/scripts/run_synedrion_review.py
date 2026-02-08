# PROOF: [L3/ユーティリティ] <- mekhane/scripts/ O4→運用スクリプトが必要→run_synedrion_review が担う
#!/usr/bin/env python3
"""
Synedrion v2.1 API Review Runner

Execute 480 orthogonal perspective reviews on hegemonikon repository.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add parent to path for import
sys.path.insert(0, str(Path(__file__).parent))

from mekhane.symploke.jules_client import JulesClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# PURPOSE: Execute Synedrion review via API.
async def run_synedrion_review(
    source: str = "sources/github/laihuip001/hegemonikon",
    branch: str = "master",
    domains: list[str] | None = None,
    axes: list[str] | None = None,
):
    """Execute Synedrion review via API."""

    # Load API key from .env.jules
    env_file = Path(__file__).parent / ".env.jules"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("JULIUS_API_KEY_1="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    else:
        api_key = os.environ.get("JULES_API_KEY")

    if not api_key:
        logger.error("No API key found. Set JULES_API_KEY or check .env.jules")
        return

    logger.info(f"Starting Synedrion v2.1 review")
    logger.info(f"  Source: {source}")
    logger.info(f"  Branch: {branch}")
    logger.info(f"  Domains: {domains or 'ALL (20)'}")
    logger.info(f"  Axes: {axes or 'ALL (24)'}")

    # PURPOSE: progress — 運用ツールの処理
    def progress(batch_num, total, completed):
        logger.info(f"  Progress: Batch {batch_num}/{total}, {completed} completed")

    async with JulesClient(api_key=api_key) as client:
        results = await client.synedrion_review(
            source=source,
            branch=branch,
            domains=domains,
            axes=axes,
            progress_callback=progress,
        )

    # Summary
    succeeded = sum(1 for r in results if r.is_success)
    failed = len(results) - succeeded

    logger.info("=" * 60)
    logger.info(f"REVIEW COMPLETE")
    logger.info(f"  Total: {len(results)} perspectives")
    logger.info(f"  Succeeded: {succeeded}")
    logger.info(f"  Failed: {failed}")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Synedrion v2.1 Review Runner")
    parser.add_argument(
        "--source",
        default="sources/github/laihuip001/hegemonikon",
        help="Repository source",
    )
    parser.add_argument("--branch", default="master", help="Branch to review")
    parser.add_argument("--domains", nargs="+", help="Filter domains")
    parser.add_argument("--axes", nargs="+", help="Filter axes")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: single perspective (Security × O1)",
    )
    args = parser.parse_args()

    if args.test:
        # Single perspective test
        asyncio.run(
            run_synedrion_review(
                source=args.source,
                branch=args.branch,
                domains=["Security"],
                axes=["O1"],
            )
        )
    else:
        asyncio.run(
            run_synedrion_review(
                source=args.source,
                branch=args.branch,
                domains=args.domains,
                axes=args.axes,
            )
        )
