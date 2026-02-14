#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/ergasterion/tekhne/ A0→SweepEngine部品の統合→end-to-endパイプライン
"""
Tekhne Pipeline — SweepEngine end-to-end orchestrator.

Orchestrates the full review pipeline:
  1. Target selection (files/directories)
  2. PerspectiveMatrix filtering (domain/axis)
  3. Sweep execution (sync or async)
  4. Result aggregation across multiple files
  5. Markdown report generation
  6. Cache statistics reporting

Usage:
    # CLI
    python -m mekhane.ergasterion.tekhne.pipeline path/to/file.py --top 20
    python -m mekhane.ergasterion.tekhne.pipeline path/to/dir/ --domains Security Error

    # API
    pipeline = TekhnePipeline()
    result = pipeline.run("path/to/file.py", domains=["Security"])
    print(result.report_markdown())

FEP mapping: Function axiom — Explore (sweep) → Exploit (aggregate + report)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mekhane.ergasterion.tekhne.sweep_engine import SweepEngine

logger = logging.getLogger(__name__)

# Importable extensions for sweep targets
SUPPORTED_EXTENSIONS = {
    ".py", ".md", ".yaml", ".yml", ".json", ".toml",
    ".js", ".ts", ".tsx", ".jsx", ".html", ".css",
    ".rs", ".go", ".sh", ".sql",
}


# === Data Structures ===


@dataclass
class PipelineConfig:
    """Configuration for a pipeline run."""

    # Perspective filtering
    domains: Optional[list[str]] = None
    axes: Optional[list[str]] = None
    max_perspectives: Optional[int] = None

    # Execution
    model: str = "gemini-2.0-flash"
    use_async: bool = True
    max_concurrency: int = 5
    use_cache: bool = True

    # Report
    top_n: int = 20
    output_dir: Optional[Path] = None
    report_format: str = "markdown"  # "markdown" or "json"


@dataclass
class AggregatedReport:
    """Aggregated results across multiple files."""

    files: list[str] = field(default_factory=list)
    file_reports: dict[str, dict[str, Any]] = field(default_factory=dict)
    total_issues: int = 0
    total_critical: int = 0
    total_major: int = 0
    total_minor: int = 0
    total_info: int = 0
    total_perspectives: int = 0
    total_silences: int = 0
    total_errors: int = 0
    elapsed_seconds: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    timestamp: str = ""

    def report_markdown(self, top_n: int = 20) -> str:
        """Generate a Markdown report."""
        lines = [
            f"# 🔍 Tekhne Sweep Report",
            f"",
            f"> Generated: {self.timestamp}",
            f"> Files scanned: {len(self.files)}",
            f"> Total perspectives: {self.total_perspectives}",
            f"> Elapsed: {self.elapsed_seconds:.1f}s",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Value |",
            f"|:-------|------:|",
            f"| 🔴 Critical | {self.total_critical} |",
            f"| 🟠 Major | {self.total_major} |",
            f"| 🟡 Minor | {self.total_minor} |",
            f"| 🔵 Info | {self.total_info} |",
            f"| **Total Issues** | **{self.total_issues}** |",
            f"| Silences | {self.total_silences} |",
            f"| Errors | {self.total_errors} |",
            f"| Cache hits | {self.cache_hits} |",
            f"| Cache misses | {self.cache_misses} |",
        ]

        # Top issues across all files (copy to avoid mutating internal state)
        all_issues = []
        for fp, report_dict in self.file_reports.items():
            for issue in report_dict.get("issues", []):
                enriched = {**issue, "_file": fp}
                all_issues.append(enriched)

        severity_order = {"critical": 4, "major": 3, "minor": 2, "info": 1}
        all_issues.sort(
            key=lambda x: severity_order.get(x.get("severity", "info"), 0),
            reverse=True,
        )

        if all_issues:
            lines.extend([
                f"",
                f"## Top {min(top_n, len(all_issues))} Issues",
                f"",
                f"| # | Severity | Domain | Axis | File | Description |",
                f"|--:|:---------|:-------|:-----|:-----|:------------|",
            ])
            for i, issue in enumerate(all_issues[:top_n], 1):
                sev_icon = {
                    "critical": "🔴", "major": "🟠",
                    "minor": "🟡", "info": "🔵",
                }.get(issue.get("severity", ""), "⚪")
                filename = Path(issue.get("_file", "")).name
                lines.append(
                    f"| {i} | {sev_icon} {issue.get('severity', '')} "
                    f"| {issue.get('domain', '')} "
                    f"| {issue.get('axis', '')} "
                    f"| {filename} "
                    f"| {issue.get('description', '')[:80]} |"
                )

        # Per-file breakdown
        if len(self.files) > 1:
            lines.extend([
                f"",
                f"## Per-File Breakdown",
                f"",
                f"| File | Issues | Critical | Major | Coverage |",
                f"|:-----|-------:|---------:|------:|---------:|",
            ])
            for fp in self.files:
                report = self.file_reports.get(fp, {})
                sev = report.get("severity", {})
                lines.append(
                    f"| {Path(fp).name} "
                    f"| {report.get('issue_count', 0)} "
                    f"| {sev.get('critical', 0)} "
                    f"| {sev.get('major', 0)} "
                    f"| {report.get('coverage', 0):.0%} |"
                )

        lines.extend([
            f"",
            f"---",
            f"*Tekhne Pipeline v1.0 — {self.total_perspectives} perspectives × {len(self.files)} files*",
        ])

        return "\n".join(lines)

    def report_json(self) -> str:
        """Generate a JSON report."""
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "summary": {
                    "files": len(self.files),
                    "total_issues": self.total_issues,
                    "critical": self.total_critical,
                    "major": self.total_major,
                    "minor": self.total_minor,
                    "info": self.total_info,
                    "perspectives": self.total_perspectives,
                    "elapsed_seconds": self.elapsed_seconds,
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                },
                "files": self.file_reports,
            },
            ensure_ascii=False,
            indent=2,
        )


# === Pipeline ===


class TekhnePipeline:
    """End-to-end SweepEngine orchestrator.

    Manages the full lifecycle:
      Target → Filter → Sweep → Aggregate → Report

    Supports both single-file and directory scanning.
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self._engine: Optional[SweepEngine] = None

    def _get_engine(self):
        """Lazy-load SweepEngine."""
        if self._engine is None:
            from mekhane.ergasterion.tekhne.sweep_engine import SweepEngine
            self._engine = SweepEngine(
                model=self.config.model,
                use_cache=self.config.use_cache,
            )
        return self._engine

    def _collect_targets(self, path: str) -> list[str]:
        """Collect target files from a path (file or directory).

        Resolves symlinks and validates paths to prevent traversal attacks.
        """
        p = Path(path).resolve()
        if p.is_file():
            return [str(p)]
        elif p.is_dir():
            base = p
            targets = []
            for f in sorted(p.rglob("*")):
                resolved = f.resolve()
                # Path traversal guard: ensure resolved path is under base
                if not str(resolved).startswith(str(base)):
                    logger.warning("Skipping symlink escape: %s -> %s", f, resolved)
                    continue
                if (
                    resolved.is_file()
                    and resolved.suffix in SUPPORTED_EXTENSIONS
                    and not any(
                        part.startswith(".")
                        for part in resolved.relative_to(base).parts
                    )
                    and "__pycache__" not in str(resolved)
                ):
                    targets.append(str(resolved))
            return targets
        else:
            raise FileNotFoundError(f"Target not found: {path}")

    def _aggregate_sweep(
        self,
        report: AggregatedReport,
        sweep_report: Any,
        filepath: str,
    ) -> None:
        """Aggregate a single sweep result into the report (DRY helper)."""
        report_dict = sweep_report.to_dict()
        report.file_reports[filepath] = report_dict

        sev = sweep_report.by_severity()
        report.total_issues += sweep_report.issue_count
        report.total_critical += sev.get("critical", 0)
        report.total_major += sev.get("major", 0)
        report.total_minor += sev.get("minor", 0)
        report.total_info += sev.get("info", 0)
        report.total_perspectives += sweep_report.total_perspectives
        report.total_silences += sweep_report.silences
        report.total_errors += sweep_report.errors

    def _finalize_cache_stats(self, report: AggregatedReport) -> None:
        """Populate cache statistics from engine."""
        engine = self._engine
        if engine and engine.use_cache and engine._cache:
            cache_stats = engine._cache.stats()
            report.cache_hits = cache_stats.hits
            report.cache_misses = cache_stats.misses

    def run(
        self,
        target: str,
        domains: Optional[list[str]] = None,
        axes: Optional[list[str]] = None,
        max_perspectives: Optional[int] = None,
        top_n: Optional[int] = None,
    ) -> AggregatedReport:
        """Run the full pipeline synchronously.

        Args:
            target: Path to file or directory to scan
            domains: Override config domains filter
            axes: Override config axes filter
            max_perspectives: Override config max_perspectives
            top_n: Override config top_n

        Returns:
            AggregatedReport with all results
        """
        domains = domains or self.config.domains
        axes = axes or self.config.axes
        max_perspectives = max_perspectives or self.config.max_perspectives

        start = time.time()
        files = self._collect_targets(target)
        engine = self._get_engine()

        logger.info("Pipeline: %d files to scan", len(files))

        report = AggregatedReport(
            files=files,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        for filepath in files:
            logger.info("Scanning: %s", filepath)
            try:
                sweep_report = engine.sweep(
                    filepath=filepath,
                    max_perspectives=max_perspectives,
                    domains=domains,
                    axes=axes,
                )
                self._aggregate_sweep(report, sweep_report, filepath)
            except Exception as e:
                logger.error("Failed to scan %s: %s", filepath, e)
                report.file_reports[filepath] = {"error": str(e)}

        self._finalize_cache_stats(report)
        report.elapsed_seconds = time.time() - start
        return report

    async def run_async(
        self,
        target: str,
        domains: Optional[list[str]] = None,
        axes: Optional[list[str]] = None,
        max_perspectives: Optional[int] = None,
        top_n: Optional[int] = None,
    ) -> AggregatedReport:
        """Run the full pipeline asynchronously.

        Uses sweep_async() for concurrent perspective processing.
        Files are still processed sequentially to avoid API saturation.
        """
        domains = domains or self.config.domains
        axes = axes or self.config.axes
        max_perspectives = max_perspectives or self.config.max_perspectives

        start = time.time()
        files = self._collect_targets(target)
        engine = self._get_engine()

        logger.info("Pipeline (async): %d files to scan", len(files))

        report = AggregatedReport(
            files=files,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        for filepath in files:
            logger.info("Scanning (async): %s", filepath)
            try:
                sweep_report = await engine.sweep_async(
                    filepath=filepath,
                    max_perspectives=max_perspectives,
                    domains=domains,
                    axes=axes,
                    max_concurrency=self.config.max_concurrency,
                )
                self._aggregate_sweep(report, sweep_report, filepath)
            except Exception as e:
                logger.error("Failed to scan %s: %s", filepath, e)
                report.file_reports[filepath] = {"error": str(e)}

        self._finalize_cache_stats(report)
        report.elapsed_seconds = time.time() - start
        return report

    def save_report(
        self,
        report: AggregatedReport,
        output_path: Optional[str] = None,
    ) -> Path:
        """Save report to file.

        Args:
            report: The aggregated report
            output_path: Explicit path, or auto-generate in output_dir

        Returns:
            Path to saved report file
        """
        if output_path:
            path = Path(output_path).resolve()
        else:
            out_dir = self.config.output_dir or Path.home() / ".cache" / "hegemonikon" / "tekhne" / "reports"
            out_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = "json" if self.config.report_format == "json" else "md"
            path = out_dir / f"sweep_report_{ts}.{ext}"

        content = (
            report.report_json()
            if self.config.report_format == "json"
            else report.report_markdown(top_n=self.config.top_n)
        )
        path.write_text(content, encoding="utf-8")
        logger.info("Report saved: %s", path)
        return path


# === CLI ===


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tekhne Pipeline — SweepEngine end-to-end orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single file
  python -m mekhane.ergasterion.tekhne.pipeline prompt.md

  # Scan with domain filter
  python -m mekhane.ergasterion.tekhne.pipeline prompt.md --domains Security Error

  # Scan a directory with limited perspectives
  python -m mekhane.ergasterion.tekhne.pipeline src/ --max-perspectives 10

  # Output JSON report
  python -m mekhane.ergasterion.tekhne.pipeline prompt.md --format json -o report.json

  # Async mode with concurrency control
  python -m mekhane.ergasterion.tekhne.pipeline prompt.md --async --concurrency 10
""",
    )
    parser.add_argument("target", help="File or directory to scan")
    parser.add_argument(
        "--domains", nargs="+", help="Filter to specific domains"
    )
    parser.add_argument(
        "--axes", nargs="+", help="Filter to specific axes (e.g. O1 O2)"
    )
    parser.add_argument(
        "--max-perspectives", type=int, help="Max perspectives to use"
    )
    parser.add_argument(
        "--top", type=int, default=20, help="Top N issues to show (default: 20)"
    )
    parser.add_argument(
        "--model", default="gemini-2.0-flash", help="Model to use"
    )
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Report format (default: markdown)",
    )
    parser.add_argument(
        "-o", "--output", help="Output file path"
    )
    parser.add_argument(
        "--async", dest="use_async", action="store_true",
        help="Use async mode for faster scanning",
    )
    parser.add_argument(
        "--concurrency", type=int, default=5,
        help="Max concurrent API requests (async mode, default: 5)",
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Disable response cache"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose logging"
    )

    args = parser.parse_args()

    # Logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Config
    config = PipelineConfig(
        domains=args.domains,
        axes=args.axes,
        max_perspectives=args.max_perspectives,
        model=args.model,
        use_async=args.use_async,
        max_concurrency=args.concurrency,
        use_cache=not args.no_cache,
        top_n=args.top,
        report_format=args.format,
    )

    # Run
    pipeline = TekhnePipeline(config=config)

    if args.use_async:
        report = asyncio.run(
            pipeline.run_async(args.target, top_n=args.top)
        )
    else:
        report = pipeline.run(args.target, top_n=args.top)

    # Output
    if args.output:
        path = pipeline.save_report(report, output_path=args.output)
        print(f"Report saved: {path}")
    else:
        if config.report_format == "json":
            print(report.report_json())
        else:
            print(report.report_markdown(top_n=args.top))

    # Summary stats
    if report.total_critical > 0:
        print(f"\n⚠️  {report.total_critical} critical issues found!")


if __name__ == "__main__":
    main()
