#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/anamnesis/tests/
# PURPOSE: Gnōsis モジュールのテストカバレッジ拡大
"""Gnōsis Test Suite — lancedb_compat, pb_parser, night_review, cli"""

import json
import pytest
from pathlib import Path
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch
from dataclasses import asdict


# ═══════════════════════════════════════
# 1. LanceDB Compatibility Layer
# ═══════════════════════════════════════

from mekhane.anamnesis.lancedb_compat import get_table_names


class TestGetTableNames:
    """lancedb_compat.get_table_names — API互換レイヤーテスト"""

    def test_new_api_with_tables_attribute(self):
        """New API: list_tables() returns object with .tables"""
        db = MagicMock()
        resp = MagicMock()
        resp.tables = ["knowledge", "papers"]
        db.list_tables.return_value = resp
        result = get_table_names(db)
        assert result == ["knowledge", "papers"]

    def test_new_api_returns_list(self):
        """New API: list_tables() returns plain list"""
        db = MagicMock()
        db.list_tables.return_value = ["t1", "t2"]
        result = get_table_names(db)
        assert result == ["t1", "t2"]

    def test_fallback_old_api(self):
        """Old API fallback: table_names()"""
        db = MagicMock(spec=[])  # No list_tables
        db.table_names = MagicMock(return_value=["old_table"])
        result = get_table_names(db)
        assert result == ["old_table"]

    def test_new_api_exception_falls_back(self):
        """If list_tables() raises, fall back to table_names()"""
        db = MagicMock()
        db.list_tables.side_effect = RuntimeError("broken")
        db.table_names.return_value = ["fallback"]
        result = get_table_names(db)
        assert result == ["fallback"]

    def test_empty_tables(self):
        db = MagicMock()
        resp = MagicMock()
        resp.tables = []
        db.list_tables.return_value = resp
        assert get_table_names(db) == []


# ═══════════════════════════════════════
# 2. Protocol Buffers Parser
# ═══════════════════════════════════════

from mekhane.anamnesis.pb_parser import parse_varint, extract_text_from_pb, save_as_markdown


class TestParseVarint:
    """Varint デコードテスト"""

    def test_single_byte(self):
        # 0x05 = 5 (no continuation bit)
        val, pos = parse_varint(bytes([0x05]), 0)
        assert val == 5
        assert pos == 1

    def test_two_bytes(self):
        # 150 = 0x96 0x01 (continuation bit on first byte)
        val, pos = parse_varint(bytes([0x96, 0x01]), 0)
        assert val == 150
        assert pos == 2

    def test_zero(self):
        val, pos = parse_varint(bytes([0x00]), 0)
        assert val == 0
        assert pos == 1

    def test_max_single_byte(self):
        val, pos = parse_varint(bytes([0x7F]), 0)
        assert val == 127
        assert pos == 1

    def test_offset_start(self):
        val, pos = parse_varint(bytes([0xFF, 0x05, 0x00]), 1)
        assert val == 5
        assert pos == 2

    def test_multi_byte_large(self):
        # 300 = 0xAC 0x02
        val, pos = parse_varint(bytes([0xAC, 0x02]), 0)
        assert val == 300
        assert pos == 2


class TestExtractTextFromPb:
    """PBファイルからテキスト抽出テスト"""

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.pb"
        f.write_bytes(b"")
        result = extract_text_from_pb(f)
        assert result == []

    def test_binary_junk(self, tmp_path):
        f = tmp_path / "junk.pb"
        f.write_bytes(b"\x00\x01\x02\x03\x04")
        result = extract_text_from_pb(f)
        assert isinstance(result, list)

    def test_embedded_text(self, tmp_path):
        """PB with length-delimited field containing Japanese text"""
        # Field 1, wire type 2 (length-delimited) = tag 0x0A
        text = "これはテストの日本語テキストです。少なくとも十文字以上の文字列。"
        encoded = text.encode("utf-8")
        # Tag(1, LEN) + varint length + data
        data = bytes([0x0A]) + bytes([len(encoded)]) + encoded
        f = tmp_path / "test.pb"
        f.write_bytes(data)
        result = extract_text_from_pb(f)
        assert len(result) > 0
        assert text in result[0]


class TestSaveAsMarkdown:
    """Markdown出力テスト"""

    def test_save_creates_file(self, tmp_path):
        output = tmp_path / "out.md"
        save_as_markdown(["Long text " * 20], output, "test.pb")
        assert output.exists()

    def test_save_content_header(self, tmp_path):
        output = tmp_path / "out.md"
        save_as_markdown(["x" * 200], output, "source.pb")
        content = output.read_text(encoding="utf-8")
        assert "source.pb" in content
        assert "記憶の発掘" in content

    def test_save_empty_list(self, tmp_path):
        output = tmp_path / "out.md"
        save_as_markdown([], output, "empty.pb")
        assert output.exists()

    def test_short_texts_filtered(self, tmp_path):
        output = tmp_path / "out.md"
        save_as_markdown(["short", "x" * 200], output, "test.pb")
        content = output.read_text(encoding="utf-8")
        # Short text (< 100 chars) should not appear as a section
        assert "short" not in content


# ═══════════════════════════════════════
# 3. Night Review
# ═══════════════════════════════════════

from mekhane.anamnesis.night_review import (
    SessionInfo,
    NightReview,
    generate_review_prompt,
    parse_review_response,
)


class TestSessionInfo:
    """SessionInfo データクラステスト"""

    def test_create(self):
        s = SessionInfo(
            session_id="abc-123",
            title="テストセッション",
            objective="テスト目的",
            created_at="2026-02-08T10:00:00",
            modified_at="2026-02-08T12:00:00",
            artifacts=[],
        )
        assert s.session_id == "abc-123"
        assert s.title == "テストセッション"

    def test_with_artifacts(self):
        s = SessionInfo(
            session_id="abc",
            title="t",
            objective="o",
            created_at=None,
            modified_at=None,
            artifacts=[{"type": "walkthrough", "summary": "Test summary"}],
        )
        assert len(s.artifacts) == 1
        assert s.artifacts[0]["type"] == "walkthrough"


class TestNightReview:
    """NightReview データクラステスト"""

    def test_create(self):
        r = NightReview(
            date="2026-02-08",
            summary="今日の成果",
            learnings=["学び1"],
            tasks=["タスク1"],
            sessions_processed=3,
            generated_at="2026-02-08T23:00:00",
        )
        assert r.sessions_processed == 3
        assert len(r.learnings) == 1


class TestGenerateReviewPrompt:
    """プロンプト生成テスト"""

    def test_generates_prompt(self):
        sessions = [
            SessionInfo(
                session_id="abc",
                title="テスト",
                objective="目的",
                created_at="2026-02-08T10:00:00",
                modified_at="2026-02-08T12:00:00",
                artifacts=[{"type": "walkthrough", "summary": "成果サマリ"}],
            )
        ]
        prompt = generate_review_prompt(sessions, date(2026, 2, 8))
        assert "2026-02-08" in prompt
        assert "テスト" in prompt
        assert "Hegemonikón" in prompt or "ナイトレビュー" in prompt

    def test_multiple_sessions(self):
        sessions = [
            SessionInfo("a", "Session A", "Obj A", None, None, []),
            SessionInfo("b", "Session B", "Obj B", None, None, []),
        ]
        prompt = generate_review_prompt(sessions, date(2026, 2, 8))
        assert "Session A" in prompt
        assert "Session B" in prompt

    def test_empty_sessions(self):
        prompt = generate_review_prompt([], date(2026, 2, 8))
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestParseReviewResponse:
    """APIレスポンスパースのテスト"""

    def test_parse_full_response(self):
        response = """
## 今日の変更サマリ
テストカバレッジを大幅に拡大した。
3つの本番バグを発見・修正した。

## 学び・気づき
- 自動リファクタリングツールの危険性
- テスト駆動開発の重要性
- 日本語キーとの互換性

## 明日に引き継ぐタスク候補
- [ ] Gnōsis プロアクティブ化
- [ ] PURPOSE 品質昇格
"""
        review = parse_review_response(response, date(2026, 2, 8), 5)
        assert review.date == "2026-02-08"
        assert review.sessions_processed == 5
        assert len(review.learnings) >= 2
        assert len(review.tasks) >= 2

    def test_parse_summary_only(self):
        response = """
## 変更サマリ
作業を行った。
"""
        review = parse_review_response(response, date(2026, 2, 8), 1)
        assert "作業を行った" in review.summary

    def test_parse_empty(self):
        review = parse_review_response("", date(2026, 2, 8), 0)
        assert review.sessions_processed == 0
        assert review.summary == ""

    def test_parse_truncates(self):
        """Learnings and tasks are capped at 5"""
        many_items = "\n".join([f"- 学び{i}" for i in range(10)])
        response = f"## 学び\n{many_items}"
        review = parse_review_response(response, date(2026, 2, 8), 1)
        assert len(review.learnings) <= 5


# ═══════════════════════════════════════
# 4. CLI State Management
# ═══════════════════════════════════════

class TestCLIState:
    """cli.py のstate管理テスト（モジュール変数をモンキーパッチ）"""

    def test_update_state(self, tmp_path):
        import mekhane.anamnesis.cli as cli_mod
        original_dir = cli_mod.DATA_DIR
        original_file = cli_mod.STATE_FILE
        try:
            cli_mod.DATA_DIR = tmp_path
            cli_mod.STATE_FILE = tmp_path / "state.json"
            cli_mod.update_state()
            assert cli_mod.STATE_FILE.exists()
            state = json.loads(cli_mod.STATE_FILE.read_text())
            assert "last_collected_at" in state
        finally:
            cli_mod.DATA_DIR = original_dir
            cli_mod.STATE_FILE = original_file

    def test_check_freshness_missing(self, tmp_path, capsys):
        import mekhane.anamnesis.cli as cli_mod
        original_file = cli_mod.STATE_FILE
        try:
            cli_mod.STATE_FILE = tmp_path / "nonexistent.json"
            args = MagicMock()
            args.threshold = 7
            result = cli_mod.cmd_check_freshness(args)
            assert result == 1  # stale/missing
            captured = capsys.readouterr()
            output = json.loads(captured.out.strip())
            assert output["status"] == "missing"
        finally:
            cli_mod.STATE_FILE = original_file

    def test_check_freshness_fresh(self, tmp_path, capsys):
        import mekhane.anamnesis.cli as cli_mod
        original_file = cli_mod.STATE_FILE
        try:
            state_file = tmp_path / "state.json"
            state_file.write_text(json.dumps({
                "last_collected_at": datetime.now().isoformat()
            }))
            cli_mod.STATE_FILE = state_file
            args = MagicMock()
            args.threshold = 7
            result = cli_mod.cmd_check_freshness(args)
            assert result == 0  # fresh
            captured = capsys.readouterr()
            output = json.loads(captured.out.strip())
            assert output["status"] == "fresh"
        finally:
            cli_mod.STATE_FILE = original_file

    def test_check_freshness_stale(self, tmp_path, capsys):
        import mekhane.anamnesis.cli as cli_mod
        original_file = cli_mod.STATE_FILE
        try:
            state_file = tmp_path / "state.json"
            old_time = (datetime.now() - timedelta(days=30)).isoformat()
            state_file.write_text(json.dumps({
                "last_collected_at": old_time
            }))
            cli_mod.STATE_FILE = state_file
            args = MagicMock()
            args.threshold = 7
            result = cli_mod.cmd_check_freshness(args)
            assert result == 1  # stale
            captured = capsys.readouterr()
            output = json.loads(captured.out.strip())
            assert output["status"] == "stale"
            assert output["days_elapsed"] >= 29
        finally:
            cli_mod.STATE_FILE = original_file
