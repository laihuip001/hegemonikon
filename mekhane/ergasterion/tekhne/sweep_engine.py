#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/ergasterion/tekhne/ A0→プロンプト品質の広域スキャンが必要→sweep_engineが担う
"""
Sweep Engine — Flash × 480次元プロンプト品質広域スキャン

480 Perspectives (20 Domains × 24 Axes) を Gemini Flash で並列スキャンし、
プロンプトの品質問題を多角的に検出する。

Architecture:
  PerspectiveMatrix (perspectives.yaml)
    → 480 review prompts
    → CortexClient.ask_batch (gemini-2.0-flash)
    → SweepReport (issues + statistics)

Usage:
  engine = SweepEngine()
  report = engine.sweep("path/to/prompt.skill.md")
  top_issues = report.top_issues(n=20)  # → Deep Engine に渡す

FEP mapping: Function axiom Explore — 広域探索で盲点を逃さない
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Project root for imports
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# === Data Structures ===


@dataclass
class SweepIssue:
    """A single issue found by a perspective scan."""

    perspective_id: str  # e.g. "Security-O1"
    domain: str  # e.g. "Security"
    axis: str  # e.g. "O1"
    severity: str  # "critical" | "major" | "minor" | "info"
    description: str
    recommendation: str = ""
    location: str = ""  # optional file:line reference

    @property
    def severity_weight(self) -> int:
        """Numeric weight for sorting."""
        return {"critical": 4, "major": 3, "minor": 2, "info": 1}.get(
            self.severity, 0
        )


@dataclass
class SweepReport:
    """Result of a 480-dimension sweep scan."""

    filepath: str
    issues: list[SweepIssue] = field(default_factory=list)
    silences: int = 0  # perspectives that found nothing
    errors: int = 0  # perspectives that failed
    total_perspectives: int = 0
    elapsed_seconds: float = 0.0

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def coverage(self) -> float:
        """Fraction of perspectives that completed successfully."""
        if self.total_perspectives == 0:
            return 0.0
        return (self.total_perspectives - self.errors) / self.total_perspectives

    def top_issues(self, n: int = 20) -> list[SweepIssue]:
        """Return top N issues sorted by severity (highest first)."""
        return sorted(self.issues, key=lambda i: i.severity_weight, reverse=True)[:n]

    def by_domain(self) -> dict[str, list[SweepIssue]]:
        """Group issues by domain."""
        grouped: dict[str, list[SweepIssue]] = {}
        for issue in self.issues:
            grouped.setdefault(issue.domain, []).append(issue)
        return grouped

    def by_severity(self) -> dict[str, int]:
        """Count issues by severity."""
        counts: dict[str, int] = {
            "critical": 0,
            "major": 0,
            "minor": 0,
            "info": 0,
        }
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

    def summary(self) -> str:
        """Human-readable summary."""
        sev = self.by_severity()
        lines = [
            f"{'=' * 60}",
            f"🔍 Sweep Report: {self.filepath}",
            f"{'=' * 60}",
            f"  Perspectives scanned: {self.total_perspectives}",
            f"  Issues found: {self.issue_count}",
            f"  Silences (no issues): {self.silences}",
            f"  Errors: {self.errors}",
            f"  Coverage: {self.coverage:.1%}",
            f"  Elapsed: {self.elapsed_seconds:.1f}s",
            f"",
            f"  Severity breakdown:",
            f"    🔴 Critical: {sev['critical']}",
            f"    🟠 Major: {sev['major']}",
            f"    🟡 Minor: {sev['minor']}",
            f"    🔵 Info: {sev['info']}",
        ]

        # Top domains
        by_domain = self.by_domain()
        if by_domain:
            lines.append("")
            lines.append("  Top domains with issues:")
            for domain, issues in sorted(
                by_domain.items(), key=lambda x: len(x[1]), reverse=True
            )[:5]:
                lines.append(f"    {domain}: {len(issues)} issues")

        lines.append(f"{'=' * 60}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "filepath": self.filepath,
            "issue_count": self.issue_count,
            "silences": self.silences,
            "errors": self.errors,
            "total_perspectives": self.total_perspectives,
            "coverage": self.coverage,
            "elapsed_seconds": self.elapsed_seconds,
            "severity": self.by_severity(),
            "issues": [
                {
                    "perspective_id": i.perspective_id,
                    "domain": i.domain,
                    "axis": i.axis,
                    "severity": i.severity,
                    "description": i.description,
                    "recommendation": i.recommendation,
                }
                for i in self.issues
            ],
        }


# === Response Parser ===

_SEVERITY_KEYWORDS = {
    "critical": ["critical", "重大", "致命"],
    "major": ["major", "高", "重要"],
    "minor": ["minor", "軽微", "低"],
    "info": ["info", "情報", "参考"],
}


def _parse_sweep_response(
    response_text: str,
    perspective_id: str,
    domain: str,
    axis: str,
) -> list[SweepIssue]:
    """Parse a Gemini response into SweepIssue objects.

    Handles both structured and unstructured responses.
    SILENCE responses return empty list.
    """
    text = response_text.strip()

    # Check for SILENCE
    if "SILENCE" in text.upper() and "no issues" in text.lower():
        return []

    # Strip markdown code fences (LLMs often wrap JSON in ```json ... ```)
    import re
    fence_match = re.match(r'^```(?:json)?\s*\n(.*?)```\s*$', text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # Try JSON parse first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [
                SweepIssue(
                    perspective_id=perspective_id,
                    domain=domain,
                    axis=axis,
                    severity=item.get("severity", "info").lower(),
                    description=item.get("issue", item.get("description", "")),
                    recommendation=item.get("recommendation", ""),
                    location=item.get("location", ""),
                )
                for item in data
                if isinstance(item, dict) and item.get("issue", item.get("description"))
            ]
        elif isinstance(data, dict) and data.get("issue", data.get("description")):
            return [
                SweepIssue(
                    perspective_id=perspective_id,
                    domain=domain,
                    axis=axis,
                    severity=data.get("severity", "info").lower(),
                    description=data.get("issue", data.get("description", "")),
                    recommendation=data.get("recommendation", ""),
                    location=data.get("location", ""),
                )
            ]
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: text-based parsing
    issues = []

    # Detect severity from text
    detected_severity = "info"
    text_lower = text.lower()
    for sev, keywords in _SEVERITY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            detected_severity = sev
            break

    # If there's substantive content (not just silence), extract it
    if len(text) > 50 and "SILENCE" not in text.upper():
        # Split into sections by "---" or numbered items
        sections = [s.strip() for s in text.split("---") if s.strip()]
        if len(sections) <= 1:
            # Try splitting by numbered items
            import re
            sections = re.split(r'\n\d+\.', text)
            sections = [s.strip() for s in sections if s.strip() and len(s.strip()) > 20]

        if sections:
            for section in sections[:5]:  # Max 5 issues per perspective
                issues.append(
                    SweepIssue(
                        perspective_id=perspective_id,
                        domain=domain,
                        axis=axis,
                        severity=detected_severity,
                        description=section[:500],  # Truncate long descriptions
                        recommendation="",
                    )
                )
        else:
            # Single issue from the entire response
            issues.append(
                SweepIssue(
                    perspective_id=perspective_id,
                    domain=domain,
                    axis=axis,
                    severity=detected_severity,
                    description=text[:500],
                    recommendation="",
                )
            )

    return issues


# === Sweep Engine ===


class SweepEngine:
    """Flash × 480-dimension prompt quality sweep scanner.

    Uses PerspectiveMatrix (20 Domains × 24 Axes) to generate
    perspective-specific review prompts, then sends them to
    Gemini Flash via CortexClient for rapid scanning.

    Usage:
        engine = SweepEngine()
        report = engine.sweep("path/to/prompt.skill.md")
        print(report.summary())
        top = report.top_issues(n=20)  # → pass to DeepEngine
    """

    DEFAULT_MODEL = "gemini-2.0-flash"
    DEFAULT_BATCH_SIZE = 60
    DEFAULT_DELAY = 0.3  # seconds between batch items
    MAX_CONTENT_LENGTH = 4000  # truncate input to save tokens

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        delay: float = DEFAULT_DELAY,
        use_cache: bool = True,
    ):
        self.model = model
        self.batch_size = batch_size
        self.delay = delay
        self.use_cache = use_cache
        self._matrix = None
        self._client = None
        self._cache = None

    def _get_cache(self):
        """Lazy-load ResponseCache."""
        if self._cache is None:
            from mekhane.ergasterion.tekhne.response_cache import ResponseCache
            self._cache = ResponseCache()
        return self._cache

    def _get_matrix(self):
        """Lazy-load PerspectiveMatrix."""
        if self._matrix is None:
            from mekhane.synedrion.prompt_generator import PerspectiveMatrix
            self._matrix = PerspectiveMatrix.load()
        return self._matrix

    def _get_client(self):
        """Lazy-load CortexClient."""
        if self._client is None:
            from mekhane.ochema.cortex_client import CortexClient
            self._client = CortexClient(model=self.model, temperature=0.3, max_tokens=1024)
        return self._client

    def sweep(
        self,
        filepath: str,
        max_perspectives: Optional[int] = None,
        domains: Optional[list[str]] = None,
        axes: Optional[list[str]] = None,
    ) -> SweepReport:
        """Run a full sweep scan on a prompt file.

        Args:
            filepath: Path to the prompt file to scan
            max_perspectives: Limit number of perspectives (for testing)
            domains: Filter to specific domains (e.g. ["Security", "Error"])
            axes: Filter to specific axes (e.g. ["O1", "O2"])

        Returns:
            SweepReport with all found issues
        """
        start_time = time.time()

        # Read input
        content = Path(filepath).read_text(encoding="utf-8")
        if len(content) > self.MAX_CONTENT_LENGTH:
            content = content[: self.MAX_CONTENT_LENGTH] + "\n\n[... truncated ...]"

        # Get perspectives
        matrix = self._get_matrix()
        perspectives = matrix.all_perspectives()

        # Apply filters
        if domains:
            perspectives = [p for p in perspectives if p.domain_id in domains]
        if axes:
            perspectives = [p for p in perspectives if p.axis_id in axes]
        if max_perspectives:
            perspectives = perspectives[:max_perspectives]

        logger.info(
            "Sweep: %d perspectives × 1 file (%s)",
            len(perspectives),
            filepath,
        )

        # Build batch tasks
        system_instruction = (
            "You are a prompt quality reviewer. "
            "Analyze the given prompt from your specific perspective. "
            "Report issues in JSON format: [{\"severity\": \"critical|major|minor|info\", "
            "\"issue\": \"description\", \"recommendation\": \"fix\"}]. "
            "If no issues from your perspective, respond with: SILENCE: No issues found"
        )

        tasks = []
        for p in perspectives:
            review_prompt = matrix.generate_prompt(p)
            combined = f"{review_prompt}\n\n---\n\n## Prompt Under Review\n\n{content}"
            tasks.append({"prompt": combined})

        # Execute batch
        client = self._get_client()
        report = SweepReport(
            filepath=filepath,
            total_perspectives=len(perspectives),
        )

        # Check cache and split into cached/uncached
        cache = self._get_cache() if self.use_cache else None
        cached_results: dict[int, str] = {}  # index -> cached text
        uncached_indices: list[int] = []

        for i, task in enumerate(tasks):
            if cache:
                hit = cache.get(
                    prompt=task["prompt"],
                    model=self.model,
                    system_instruction=system_instruction,
                )
                if hit:
                    cached_results[i] = hit["text"]
                    continue
            uncached_indices.append(i)

        cache_hits = len(cached_results)
        logger.info(
            "Cache: %d hits, %d to fetch",
            cache_hits, len(uncached_indices),
        )

        # Fetch uncached in batches
        uncached_tasks = [tasks[i] for i in uncached_indices]
        fetched: dict[int, str] = {}

        for batch_start in range(0, len(uncached_tasks), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(uncached_tasks))
            batch_tasks = uncached_tasks[batch_start:batch_end]

            logger.info(
                "Batch %d-%d / %d",
                batch_start + 1,
                batch_end,
                len(uncached_tasks),
            )

            try:
                responses = client.ask_batch(
                    batch_tasks,
                    default_model=self.model,
                    default_system_instruction=system_instruction,
                    delay=self.delay,
                )

                for j, resp in enumerate(responses):
                    global_idx = uncached_indices[batch_start + j]
                    fetched[global_idx] = resp.text

                    # Store in cache
                    if cache and not resp.text.startswith("[ERROR]"):
                        cache.put(
                            prompt=tasks[global_idx]["prompt"],
                            model=self.model,
                            response_text=resp.text,
                            system_instruction=system_instruction,
                        )

            except Exception as e:
                logger.error("Batch %d-%d failed: %s", batch_start + 1, batch_end, e)
                report.errors += batch_end - batch_start

        # Merge and parse all results
        all_texts = {**cached_results, **fetched}
        for i, persp in enumerate(perspectives):
            text = all_texts.get(i)
            if text is None:
                report.errors += 1
                continue
            if text.startswith("[ERROR]"):
                report.errors += 1
                continue

            parsed = _parse_sweep_response(
                text,
                perspective_id=persp.id,
                domain=persp.domain_id,
                axis=persp.axis_id,
            )

            if parsed:
                report.issues.extend(parsed)
            else:
                report.silences += 1

        report.elapsed_seconds = time.time() - start_time
        return report

    async def sweep_async(
        self,
        filepath: str,
        max_perspectives: Optional[int] = None,
        domains: Optional[list[str]] = None,
        axes: Optional[list[str]] = None,
        max_concurrency: int = 5,
    ) -> SweepReport:
        """Async sweep — processes perspectives concurrently.

        Uses CortexClient.ask_batch_async() with semaphore-based
        concurrency control. ~5-10x faster than sync sweep().

        Args:
            filepath: Path to the prompt file to scan
            max_perspectives: Limit number of perspectives (for testing)
            domains: Filter to specific domains
            axes: Filter to specific axes
            max_concurrency: Max concurrent API requests (default: 5)

        Returns:
            SweepReport with all found issues
        """
        start_time = time.time()

        # Read input
        content = Path(filepath).read_text(encoding="utf-8")
        if len(content) > self.MAX_CONTENT_LENGTH:
            content = content[: self.MAX_CONTENT_LENGTH] + "\n\n[... truncated ...]"

        # Get perspectives
        matrix = self._get_matrix()
        perspectives = matrix.all_perspectives()

        # Apply filters
        if domains:
            perspectives = [p for p in perspectives if p.domain_id in domains]
        if axes:
            perspectives = [p for p in perspectives if p.axis_id in axes]
        if max_perspectives:
            perspectives = perspectives[:max_perspectives]

        logger.info(
            "Sweep (async, concurrency=%d): %d perspectives × 1 file (%s)",
            max_concurrency,
            len(perspectives),
            filepath,
        )

        # Build batch tasks
        system_instruction = (
            "You are a prompt quality reviewer. "
            "Analyze the given prompt from your specific perspective. "
            "Report issues in JSON format: [{\"severity\": \"critical|major|minor|info\", "
            "\"issue\": \"description\", \"recommendation\": \"fix\"}]. "
            "If no issues from your perspective, respond with: SILENCE: No issues found"
        )

        tasks = []
        for p in perspectives:
            review_prompt = matrix.generate_prompt(p)
            combined = f"{review_prompt}\n\n---\n\n## Prompt Under Review\n\n{content}"
            tasks.append({"prompt": combined})

        # Execute async batch
        client = self._get_client()
        report = SweepReport(
            filepath=filepath,
            total_perspectives=len(perspectives),
        )

        try:
            responses = await client.ask_batch_async(
                tasks,
                default_model=self.model,
                default_system_instruction=system_instruction,
                max_concurrency=max_concurrency,
            )

            for resp, persp in zip(responses, perspectives):
                if resp.text.startswith("[ERROR]"):
                    report.errors += 1
                    continue

                parsed = _parse_sweep_response(
                    resp.text,
                    perspective_id=persp.id,
                    domain=persp.domain_id,
                    axis=persp.axis_id,
                )

                if parsed:
                    report.issues.extend(parsed)
                else:
                    report.silences += 1

        except Exception as e:
            logger.error("Async sweep failed: %s", e)
            report.errors += len(tasks)

        report.elapsed_seconds = time.time() - start_time
        return report


# === CLI ===


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Sweep Engine — Flash × 480 Dimension Prompt Quality Scan"
    )
    parser.add_argument("filepath", help="Path to prompt file to scan")
    parser.add_argument(
        "--model",
        default=SweepEngine.DEFAULT_MODEL,
        help=f"Gemini model (default: {SweepEngine.DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Max perspectives to scan (for testing)",
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=None,
        help="Filter to specific domains (e.g. Security Error)",
    )
    parser.add_argument(
        "--axes",
        nargs="+",
        default=None,
        help="Filter to specific axes (e.g. O1 O2 S1)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Show top N issues (default: 20)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if not Path(args.filepath).exists():
        print(f"Error: {args.filepath} not found", file=sys.stderr)
        sys.exit(1)

    engine = SweepEngine(model=args.model)
    report = engine.sweep(
        args.filepath,
        max_perspectives=args.max,
        domains=args.domains,
        axes=args.axes,
    )

    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.summary())
        print()

        top = report.top_issues(n=args.top)
        if top:
            print(f"📋 Top {len(top)} Issues:")
            print("-" * 60)
            for i, issue in enumerate(top, 1):
                sev_icon = {
                    "critical": "🔴",
                    "major": "🟠",
                    "minor": "🟡",
                    "info": "🔵",
                }.get(issue.severity, "⚪")
                print(
                    f"  {i:2d}. {sev_icon} [{issue.perspective_id}] {issue.description[:80]}"
                )
                if issue.recommendation:
                    print(f"      → {issue.recommendation[:80]}")


if __name__ == "__main__":
    main()
