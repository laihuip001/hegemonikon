# PROOF: [L3/ユーティリティ] <- mekhane/scripts/ O4→運用スクリプトが必要→collect_results が担う
#!/usr/bin/env python3
"""
Synedrion v2.1 Result Collector

Collect and summarize results from Jules sessions via API.
No web UI needed - all done programmatically.

Usage:
    # Check specific session
    python collect_results.py --session 12036265788757663589

    # List recent sessions
    python collect_results.py --list 10

    # Generate summary report
    python collect_results.py --report
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class SessionSummary:
    """Summary of a Jules session."""

    session_id: str
    state: str
    title: str
    created: str
    duration_seconds: Optional[int]
    has_pr: bool
    pr_url: Optional[str]
    pr_title: Optional[str]
    is_silent: bool  # No issues found
    findings_count: int


class JulesResultCollector:
    """Collect and analyze Jules session results."""

    BASE_URL = "https://jules.googleapis.com/v1alpha"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}

    async def get_session(self, session_id: str) -> dict:
        """Get session details from API."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/sessions/{session_id}"
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": resp.status, "message": await resp.text()}

    async def list_sessions(self, limit: int = 20) -> list[dict]:
        """List recent sessions."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.BASE_URL}/sessions?pageSize={limit}"
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("sessions", [])
                else:
                    logger.error(f"List error: {resp.status}")
                    return []

    def parse_session(self, data: dict) -> SessionSummary:
        """Parse session data into summary."""
        # Extract PR info
        outputs = data.get("outputs", [])
        pr = outputs[0].get("pullRequest", {}) if outputs else {}

        # Calculate duration
        created = data.get("createTime", "")
        updated = data.get("updateTime", "")
        duration = None
        if created and updated:
            try:
                from dateutil import parser as dt_parser

                t1 = dt_parser.parse(created)
                t2 = dt_parser.parse(updated)
                duration = int((t2 - t1).total_seconds())
            except Exception as e:
                logger.error(f"Failed to parse dates (created='{created}', updated='{updated}'): {e}")
                duration = None

        # Check if silent (no output = no issues found)
        is_silent = data.get("state") == "COMPLETED" and not outputs

        # Extract title (first 100 chars of prompt)
        title = data.get("title", data.get("prompt", ""))[:100]

        return SessionSummary(
            session_id=data.get("id", ""),
            state=data.get("state", "UNKNOWN"),
            title=title,
            created=created,
            duration_seconds=duration,
            has_pr=bool(pr),
            pr_url=pr.get("url"),
            pr_title=pr.get("title"),
            is_silent=is_silent,
            findings_count=len(outputs),
        )

    async def get_summary(self, session_id: str) -> SessionSummary:
        """Get summary for a single session."""
        data = await self.get_session(session_id)
        if "error" in data:
            return SessionSummary(
                session_id=session_id,
                state="ERROR",
                title=str(data.get("message", "")),
                created="",
                duration_seconds=None,
                has_pr=False,
                pr_url=None,
                pr_title=None,
                is_silent=False,
                findings_count=0,
            )
        return self.parse_session(data)

    async def generate_report(self, session_ids: list[str]) -> dict:
        """Generate aggregate report from multiple sessions."""
        summaries = await asyncio.gather(
            *[self.get_summary(sid) for sid in session_ids]
        )

        total = len(summaries)
        completed = sum(1 for s in summaries if s.state == "COMPLETED")
        with_pr = sum(1 for s in summaries if s.has_pr)
        silent = sum(1 for s in summaries if s.is_silent)
        failed = sum(1 for s in summaries if s.state in ("FAILED", "ERROR"))
        in_progress = sum(1 for s in summaries if s.state == "IN_PROGRESS")

        # Categorize by findings
        issues_found = [s for s in summaries if s.has_pr]
        no_issues = [s for s in summaries if s.is_silent]
        errors = [s for s in summaries if s.state in ("FAILED", "ERROR")]

        return {
            "generated_at": datetime.now().isoformat(),
            "stats": {
                "total_sessions": total,
                "completed": completed,
                "in_progress": in_progress,
                "with_findings": with_pr,
                "silent_no_issues": silent,
                "failed": failed,
            },
            "pr_urls": [s.pr_url for s in issues_found if s.pr_url],
            "sessions": [asdict(s) for s in summaries],
        }

    def print_summary(self, summary: SessionSummary):
        """Print formatted summary."""
        status_icon = {
            "COMPLETED": "✅",
            "IN_PROGRESS": "⏳",
            "FAILED": "❌",
            "ERROR": "❌",
            "WAITING_FOR_APPROVAL": "⏸️",
        }.get(summary.state, "❓")

        print(f"\n{'━' * 60}")
        print(f"{status_icon} Session: {summary.session_id}")
        print(f"   State: {summary.state}")
        print(f"   Title: {summary.title[:80]}...")
        if summary.duration_seconds:
            mins = summary.duration_seconds // 60
            secs = summary.duration_seconds % 60
            print(f"   Duration: {mins}m {secs}s")
        if summary.is_silent:
            print(f"   Result: SILENCE (no issues found)")
        elif summary.has_pr:
            print(f"   PR: {summary.pr_url}")
            print(f"   PR Title: {summary.pr_title}")
        print(f"{'━' * 60}")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Synedrion v2.1 Result Collector")
    parser.add_argument("--session", help="Check specific session ID")
    parser.add_argument("--list", type=int, help="List N recent sessions")
    parser.add_argument("--report", help="Generate report from session IDs file (JSON)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Load API key
    env_file = Path(__file__).parent / ".env.jules"
    api_key = None
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("JULIUS_API_KEY_1="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    api_key = api_key or os.environ.get("JULES_API_KEY")

    if not api_key:
        print("❌ No API key found")
        sys.exit(1)

    collector = JulesResultCollector(api_key)

    if args.session:
        summary = await collector.get_summary(args.session)
        if args.json:
            print(json.dumps(asdict(summary), indent=2, ensure_ascii=False))
        else:
            collector.print_summary(summary)

    elif args.list:
        sessions = await collector.list_sessions(args.list)
        print(f"\n📋 Recent {len(sessions)} Sessions:\n")
        for s in sessions:
            summary = collector.parse_session(s)
            if args.json:
                print(json.dumps(asdict(summary), ensure_ascii=False))
            else:
                collector.print_summary(summary)

    elif args.report:
        with open(args.report) as f:
            session_ids = json.load(f)
        report = await collector.generate_report(session_ids)
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            stats = report["stats"]
            print(f"\n{'═' * 60}")
            print(f"📊 Synedrion v2.1 Report")
            print(f"{'═' * 60}")
            print(f"Total Sessions: {stats['total_sessions']}")
            print(f"  ✅ Completed: {stats['completed']}")
            print(f"  ⏳ In Progress: {stats['in_progress']}")
            print(f"  🔍 With Findings: {stats['with_findings']}")
            print(f"  🔇 Silent (no issues): {stats['silent_no_issues']}")
            print(f"  ❌ Failed: {stats['failed']}")
            print(f"\n📝 PRs Created:")
            for url in report["pr_urls"]:
                print(f"  • {url}")
            print(f"{'═' * 60}")

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
