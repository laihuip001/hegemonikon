#!/usr/bin/env python3
# PROOF: [L1/テスト] <- mekhane/exagoge/tests/
# PURPOSE: Exagoge extractor モジュールのユニットテスト
"""
Exagoge Extractor Tests

BaseExporter の ETL パイプラインと HandoffExporter の
extract/transform/export を検証する。
"""

import json
from pathlib import Path

import pytest


# ------ fixtures ------

@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """エクスポート出力先の一時ディレクトリ。"""
    out = tmp_path / "export_out"
    out.mkdir()
    return out


@pytest.fixture
def tmp_sessions(tmp_path: Path) -> Path:
    """テスト用 Handoff ファイルを含む一時ディレクトリ。"""
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    # Create 3 test handoff files
    for i in range(3):
        hf = sessions / f"handoff_2026-02-{10 + i:02d}_2200.md"
        hf.write_text(
            f"# Session {i + 1}\n\nTest handoff content for session {i + 1}.\n"
            f"Some details about what was accomplished.\n",
            encoding="utf-8",
        )
    return sessions


# ------ ExportResult tests ------

# PURPOSE: ExportResult データクラスの基本動作を検証する
class TestExportResult:
    def test_success_result(self) -> None:
        from mekhane.exagoge.extractor import ExportResult

        result = ExportResult(success=True, record_count=5, format="json")
        assert result.success is True
        assert result.record_count == 5
        assert result.format == "json"
        assert result.errors == []
        assert result.exported_at  # non-empty timestamp

    def test_failure_result(self) -> None:
        from mekhane.exagoge.extractor import ExportResult

        result = ExportResult(success=False, errors=["something broke"])
        assert result.success is False
        assert len(result.errors) == 1


# ------ HandoffExporter tests ------

# PURPOSE: HandoffExporter の ETL パイプラインを検証するテストクラス
class TestHandoffExporter:
    def test_extract_returns_records(
        self, tmp_sessions: Path, tmp_output: Path
    ) -> None:
        from mekhane.exagoge.extractor import HandoffExporter

        exporter = HandoffExporter(tmp_sessions, tmp_output)
        records = exporter.extract(count=10)
        assert len(records) == 3
        assert all("filename" in r for r in records)
        assert all("size_bytes" in r for r in records)
        assert all("line_count" in r for r in records)

    def test_extract_with_limit(
        self, tmp_sessions: Path, tmp_output: Path
    ) -> None:
        from mekhane.exagoge.extractor import HandoffExporter

        exporter = HandoffExporter(tmp_sessions, tmp_output)
        records = exporter.extract(count=2)
        assert len(records) == 2

    def test_extract_empty_dir(self, tmp_path: Path, tmp_output: Path) -> None:
        from mekhane.exagoge.extractor import HandoffExporter

        empty = tmp_path / "empty_sessions"
        empty.mkdir()
        exporter = HandoffExporter(empty, tmp_output)
        records = exporter.extract()
        assert records == []

    def test_extract_nonexistent_dir(
        self, tmp_path: Path, tmp_output: Path
    ) -> None:
        from mekhane.exagoge.extractor import HandoffExporter

        missing = tmp_path / "no_such_dir"
        exporter = HandoffExporter(missing, tmp_output)
        records = exporter.extract()
        assert records == []

    def test_transform_structure(
        self, tmp_sessions: Path, tmp_output: Path
    ) -> None:
        from mekhane.exagoge.extractor import HandoffExporter

        exporter = HandoffExporter(tmp_sessions, tmp_output)
        records = exporter.extract()
        transformed = exporter.transform(records)
        assert transformed["source"] == "hegemonikon_handoffs"
        assert transformed["count"] == 3
        assert len(transformed["records"]) == 3

    def test_export_creates_json_file(
        self, tmp_sessions: Path, tmp_output: Path
    ) -> None:
        from mekhane.exagoge.extractor import HandoffExporter

        exporter = HandoffExporter(tmp_sessions, tmp_output)
        result = exporter.export(format="json")
        assert result.success is True
        assert result.output_path is not None
        assert result.output_path.exists()
        assert result.record_count == 3

        # Verify JSON content
        data = json.loads(result.output_path.read_text(encoding="utf-8"))
        assert data["source"] == "hegemonikon_handoffs"
        assert len(data["records"]) == 3
