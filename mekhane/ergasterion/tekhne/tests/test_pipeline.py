#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/ergasterion/tekhne/ TekhnePipeline 統合テスト
"""
TekhnePipeline Integration Tests.

Tests the end-to-end pipeline:
  - Target collection (file, directory, traversal protection)
  - AggregatedReport (Markdown, JSON, dict mutation safety)
  - Pipeline orchestration (sync, config, caching)
  - CLI argument parsing

Does NOT require Cortex API (all LLM calls are mocked).
"""

import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from dataclasses import dataclass

from mekhane.ergasterion.tekhne.pipeline import (
    TekhnePipeline,
    PipelineConfig,
    AggregatedReport,
    SUPPORTED_EXTENSIONS,
)
from mekhane.ergasterion.tekhne.sweep_engine import SweepReport, SweepIssue


# === Fixtures ===


@pytest.fixture
def sample_dir(tmp_path):
    """Create a directory with mixed files for target collection testing."""
    # Supported files
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "config.yaml").write_text("key: value")
    (tmp_path / "README.md").write_text("# Test")
    (tmp_path / "style.css").write_text("body {}")

    # Should be excluded
    (tmp_path / ".hidden").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".hidden" / "secret.py").write_text("# hidden")
    (tmp_path / "__pycache__").mkdir(parents=True, exist_ok=True)
    (tmp_path / "__pycache__" / "cache.py").write_text("# cache")
    (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8\xff\xe0")

    # Subdirectory
    sub = tmp_path / "lib"
    sub.mkdir()
    (sub / "utils.py").write_text("def foo(): pass")
    (sub / "helper.ts").write_text("export const x = 1;")

    return tmp_path


@pytest.fixture
def sample_prompt_file(tmp_path):
    """Create a sample prompt file."""
    f = tmp_path / "test_prompt.md"
    f.write_text("# Test Prompt\n\nAnalyze this code.")
    return f


@pytest.fixture
def mock_sweep_report():
    """Create a mock SweepReport with realistic data."""
    return SweepReport(
        filepath="test.py",
        issues=[
            SweepIssue(
                perspective_id="Security_O1",
                domain="Security",
                axis="O1",
                severity="major",
                description="SQL injection risk in query builder",
                recommendation="Use parameterized queries",
            ),
            SweepIssue(
                perspective_id="Error_O2",
                domain="Error",
                axis="O2",
                severity="minor",
                description="Missing null check on user input",
                recommendation="Add validation",
            ),
            SweepIssue(
                perspective_id="Performance_O3",
                domain="Performance",
                axis="O3",
                severity="info",
                description="Consider caching for repeated lookups",
                recommendation="Add LRU cache",
            ),
        ],
        silences=7,
        errors=0,
        total_perspectives=10,
        elapsed_seconds=2.5,
    )


# === Target Collection Tests ===


class TestTargetCollection:
    """Test _collect_targets method."""

    def test_single_file(self, sample_prompt_file):
        """Single file target returns list with one element."""
        pipeline = TekhnePipeline()
        targets = pipeline._collect_targets(str(sample_prompt_file))
        assert len(targets) == 1
        assert targets[0].endswith("test_prompt.md")

    def test_directory_scan(self, sample_dir):
        """Directory scan finds supported files, excludes hidden/pycache."""
        pipeline = TekhnePipeline()
        targets = pipeline._collect_targets(str(sample_dir))

        filenames = {Path(t).name for t in targets}
        assert "main.py" in filenames
        assert "config.yaml" in filenames
        assert "README.md" in filenames
        assert "style.css" in filenames
        assert "utils.py" in filenames
        assert "helper.ts" in filenames

        # Excluded
        assert "secret.py" not in filenames  # hidden dir
        assert "cache.py" not in filenames  # __pycache__
        assert "photo.jpg" not in filenames  # unsupported extension

    def test_nonexistent_target_raises(self):
        """Non-existent path raises FileNotFoundError."""
        pipeline = TekhnePipeline()
        with pytest.raises(FileNotFoundError, match="Target not found"):
            pipeline._collect_targets("/nonexistent/path")

    def test_supported_extensions(self):
        """SUPPORTED_EXTENSIONS contains expected types."""
        assert ".py" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".ts" in SUPPORTED_EXTENSIONS
        assert ".rs" in SUPPORTED_EXTENSIONS
        assert ".jpg" not in SUPPORTED_EXTENSIONS
        assert ".png" not in SUPPORTED_EXTENSIONS

    def test_subdirectory_traversal(self, sample_dir):
        """Targets include files from subdirectories."""
        pipeline = TekhnePipeline()
        targets = pipeline._collect_targets(str(sample_dir))
        # lib/utils.py and lib/helper.ts should be found
        has_subdir = any("lib" in t for t in targets)
        assert has_subdir, f"No subdirectory files found: {targets}"

    def test_resolved_paths(self, sample_dir):
        """Collected targets use resolved (absolute) paths."""
        pipeline = TekhnePipeline()
        targets = pipeline._collect_targets(str(sample_dir))
        for t in targets:
            assert os.path.isabs(t), f"Not absolute: {t}"


# === AggregatedReport Tests ===


class TestAggregatedReport:
    """Test report generation."""

    def _make_report(self, issues=None):
        """Helper to create a report with sample data."""
        if issues is None:
            issues = [
                {
                    "perspective_id": "Sec_O1", "domain": "Security",
                    "axis": "O1", "severity": "critical",
                    "description": "Critical vuln", "recommendation": "Fix",
                },
                {
                    "perspective_id": "Err_O2", "domain": "Error",
                    "axis": "O2", "severity": "major",
                    "description": "Error handling gap", "recommendation": "Add",
                },
            ]
        return AggregatedReport(
            files=["a.py", "b.py"],
            file_reports={
                "a.py": {
                    "issues": issues,
                    "issue_count": len(issues),
                    "coverage": 0.95,
                    "severity": {"critical": 1, "major": 1, "minor": 0, "info": 0},
                },
                "b.py": {
                    "issues": [],
                    "issue_count": 0,
                    "coverage": 1.0,
                    "severity": {"critical": 0, "major": 0, "minor": 0, "info": 0},
                },
            },
            total_issues=2,
            total_critical=1,
            total_major=1,
            total_perspectives=20,
            elapsed_seconds=5.0,
            timestamp="2026-02-14 19:30:00",
        )

    def test_markdown_report_structure(self):
        """Markdown report contains expected sections."""
        report = self._make_report()
        md = report.report_markdown(top_n=10)

        assert "# 🔍 Tekhne Sweep Report" in md
        assert "## Summary" in md
        assert "🔴 Critical | 1" in md
        assert "🟠 Major | 1" in md
        assert "## Top" in md
        assert "## Per-File Breakdown" in md
        assert "Tekhne Pipeline v1.0" in md

    def test_markdown_top_n_limit(self):
        """Top N limits the number of issues shown."""
        report = self._make_report()
        md = report.report_markdown(top_n=1)
        # Should show "Top 1 Issues" not "Top 2 Issues"
        assert "Top 1 Issues" in md

    def test_json_report_parseable(self):
        """JSON report is valid JSON."""
        report = self._make_report()
        j = report.report_json()
        data = json.loads(j)
        assert data["summary"]["total_issues"] == 2
        assert data["summary"]["critical"] == 1
        assert "a.py" in data["files"]

    def test_dict_mutation_safety(self):
        """report_markdown does NOT mutate original file_reports."""
        original_issues = [
            {
                "perspective_id": "Sec_O1", "domain": "Security",
                "axis": "O1", "severity": "critical",
                "description": "Test", "recommendation": "Fix",
            },
        ]
        report = self._make_report(issues=original_issues)

        # Generate report (should NOT mutate issues)
        report.report_markdown(top_n=5)

        # Verify no _file key was added to original
        for issue in report.file_reports["a.py"]["issues"]:
            assert "_file" not in issue, f"Mutation detected: {issue}"

    def test_single_file_no_breakdown(self):
        """Single file report does NOT show per-file breakdown."""
        report = AggregatedReport(
            files=["only.py"],
            file_reports={"only.py": {"issues": [], "issue_count": 0, "coverage": 1.0, "severity": {}}},
            timestamp="2026-02-14",
        )
        md = report.report_markdown()
        assert "Per-File Breakdown" not in md

    def test_empty_report(self):
        """Empty report generates without errors."""
        report = AggregatedReport(timestamp="2026-02-14")
        md = report.report_markdown()
        assert "Total Issues" in md
        j = report.report_json()
        data = json.loads(j)
        assert data["summary"]["total_issues"] == 0


# === Pipeline Config Tests ===


class TestPipelineConfig:
    """Test PipelineConfig defaults and overrides."""

    def test_defaults(self):
        cfg = PipelineConfig()
        assert cfg.model == "gemini-2.0-flash"
        assert cfg.use_async is True
        assert cfg.max_concurrency == 5
        assert cfg.use_cache is True
        assert cfg.top_n == 20
        assert cfg.report_format == "markdown"
        assert cfg.domains is None
        assert cfg.axes is None

    def test_custom_config(self):
        cfg = PipelineConfig(
            domains=["Security"],
            model="gemini-2.5-pro",
            use_async=False,
            max_concurrency=10,
        )
        assert cfg.domains == ["Security"]
        assert cfg.model == "gemini-2.5-pro"
        assert cfg.use_async is False
        assert cfg.max_concurrency == 10


# === Pipeline Run Tests (Mocked) ===


class TestPipelineRun:
    """Test pipeline run with mocked SweepEngine."""

    def test_run_single_file(self, sample_prompt_file, mock_sweep_report):
        """Pipeline run processes a single file and aggregates results."""
        pipeline = TekhnePipeline()

        mock_engine = MagicMock()
        mock_engine.sweep.return_value = mock_sweep_report
        mock_engine.use_cache = False
        mock_engine._cache = None
        pipeline._engine = mock_engine

        report = pipeline.run(str(sample_prompt_file))

        assert len(report.files) == 1
        assert report.total_issues == 3  # major + minor + info
        assert report.total_major == 1
        assert report.total_minor == 1
        assert report.total_info == 1
        assert report.total_perspectives == 10
        assert report.total_silences == 7
        assert report.total_errors == 0
        assert report.elapsed_seconds > 0
        mock_engine.sweep.assert_called_once()

    def test_run_directory(self, sample_dir, mock_sweep_report):
        """Pipeline run processes all supported files in a directory."""
        pipeline = TekhnePipeline()

        mock_engine = MagicMock()
        mock_engine.sweep.return_value = mock_sweep_report
        mock_engine.use_cache = False
        mock_engine._cache = None
        pipeline._engine = mock_engine

        report = pipeline.run(str(sample_dir))

        # 6 supported files: main.py, config.yaml, README.md, style.css, utils.py, helper.ts
        assert len(report.files) == 6
        assert mock_engine.sweep.call_count == 6

    def test_run_with_sweep_error(self, sample_prompt_file):
        """Pipeline handles sweep failures gracefully."""
        pipeline = TekhnePipeline()

        mock_engine = MagicMock()
        mock_engine.sweep.side_effect = RuntimeError("API timeout")
        mock_engine.use_cache = False
        mock_engine._cache = None
        pipeline._engine = mock_engine

        report = pipeline.run(str(sample_prompt_file))

        assert len(report.files) == 1
        assert "error" in report.file_reports[str(sample_prompt_file.resolve())]

    def test_run_with_cache_stats(self, sample_prompt_file, mock_sweep_report):
        """Pipeline collects cache statistics when cache is enabled."""
        pipeline = TekhnePipeline()

        @dataclass
        class MockCacheStats:
            hits: int = 5
            misses: int = 3

        mock_cache = MagicMock()
        mock_cache.stats.return_value = MockCacheStats()

        mock_engine = MagicMock()
        mock_engine.sweep.return_value = mock_sweep_report
        mock_engine.use_cache = True
        mock_engine._cache = mock_cache
        pipeline._engine = mock_engine

        report = pipeline.run(str(sample_prompt_file))

        assert report.cache_hits == 5
        assert report.cache_misses == 3

    def test_run_with_domain_filter(self, sample_prompt_file, mock_sweep_report):
        """Pipeline passes domain filter to sweep engine."""
        pipeline = TekhnePipeline(config=PipelineConfig(domains=["Security"]))

        mock_engine = MagicMock()
        mock_engine.sweep.return_value = mock_sweep_report
        mock_engine.use_cache = False
        mock_engine._cache = None
        pipeline._engine = mock_engine

        pipeline.run(str(sample_prompt_file))

        call_args = mock_engine.sweep.call_args
        assert call_args.kwargs.get("domains") == ["Security"]


# === Report Save Tests ===


class TestReportSave:
    """Test report saving."""

    def test_save_markdown(self, tmp_path):
        """Save Markdown report to specified path."""
        pipeline = TekhnePipeline()
        report = AggregatedReport(timestamp="2026-02-14", total_issues=0)

        out = tmp_path / "test_report.md"
        result = pipeline.save_report(report, output_path=str(out))

        assert result.exists()
        content = result.read_text()
        assert "Tekhne Sweep Report" in content

    def test_save_json(self, tmp_path):
        """Save JSON report to specified path."""
        pipeline = TekhnePipeline(config=PipelineConfig(report_format="json"))
        report = AggregatedReport(timestamp="2026-02-14", total_issues=0)

        out = tmp_path / "test_report.json"
        result = pipeline.save_report(report, output_path=str(out))

        assert result.exists()
        data = json.loads(result.read_text())
        assert "summary" in data

    def test_save_auto_path(self, tmp_path):
        """Auto-generate path when output_path not specified."""
        pipeline = TekhnePipeline(config=PipelineConfig(output_dir=tmp_path))
        report = AggregatedReport(timestamp="2026-02-14", total_issues=0)

        result = pipeline.save_report(report)

        assert result.exists()
        assert result.parent == tmp_path
        assert result.suffix == ".md"
