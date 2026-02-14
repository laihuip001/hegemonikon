"""
GatewayBridge テスト — E2E + 単体テスト

gateway_bridge.py とその PKSEngine 統合の動作を検証する。
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from mekhane.pks.gateway_bridge import GatewayBridge, _TOPIC_ALIASES
from mekhane.pks.pks_engine import KnowledgeNugget, SessionContext


# --- Fixtures ---

@pytest.fixture
def tmp_dirs(tmp_path):
    """テスト用ディレクトリ構造を作成。"""
    ideas = tmp_path / "ideas"
    doxa = tmp_path / "doxa"
    sessions = tmp_path / "sessions"
    ki = tmp_path / "ki"
    for d in [ideas, doxa, sessions, ki]:
        d.mkdir()
    return ideas, doxa, sessions, ki


@pytest.fixture
def bridge(tmp_dirs):
    """テスト用 GatewayBridge を作成。"""
    ideas, doxa, sessions, ki = tmp_dirs
    return GatewayBridge(
        ideas_dir=ideas,
        doxa_dir=doxa,
        sessions_dir=sessions,
        ki_dir=ki,
    )


def _write_idea(ideas_dir: Path, name: str, title: str, tags: str = "") -> Path:
    content = f"# {title}\n\n**タグ**: {tags}\n\n## 概要\n\nテスト用アイデア\n"
    p = ideas_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def _write_handoff(sessions_dir: Path, name: str, title: str, task: str = "") -> Path:
    content = f"---\nprimary_task: {task}\n---\n# {title}\n\nテスト用引き継ぎ\n"
    p = sessions_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def _write_ki(ki_dir: Path, name: str, title: str, ki_type: str = "原則") -> Path:
    content = f"# {title}\n\n**KI 種別**: {ki_type}\n\n[確信: 85%]\n\nテスト用 KI\n"
    p = ki_dir / name
    p.write_text(content, encoding="utf-8")
    return p


def _write_doxa(doxa_dir: Path, name: str, title: str) -> Path:
    content = f"# {title}\n\n**日付**: 2026-02-14\n\n[確信: 90%]\n\nテスト用信念\n"
    p = doxa_dir / name
    p.write_text(content, encoding="utf-8")
    return p


# ======================================================
# 1. GatewayBridge 単体テスト
# ======================================================

class TestGatewayBridgeInit:
    """初期化テスト"""

    def test_creates_with_defaults(self):
        bridge = GatewayBridge()
        assert len(bridge._sources) == 4

    def test_creates_with_custom_dirs(self, tmp_dirs):
        ideas, doxa, sessions, ki = tmp_dirs
        bridge = GatewayBridge(
            ideas_dir=ideas, doxa_dir=doxa,
            sessions_dir=sessions, ki_dir=ki,
        )
        assert bridge._sources[0].directory == ideas


class TestParseIdea:
    """Ideas パーサーテスト"""

    def test_parses_idea(self, bridge, tmp_dirs):
        ideas_dir = tmp_dirs[0]
        _write_idea(ideas_dir, "idea_20260214.md", "テストアイデア", "FEP, CCL")
        nugget = bridge._parse_idea(ideas_dir / "idea_20260214.md")
        assert nugget is not None
        assert nugget.title == "テストアイデア"
        assert "gateway:ideas:" in nugget.source
        assert nugget.relevance_score == 0.6

    def test_extracts_tags_metadata(self, bridge, tmp_dirs):
        ideas_dir = tmp_dirs[0]
        _write_idea(ideas_dir, "idea_20260214.md", "タグテスト", "FEP, CCL, 圏論")
        nugget = bridge._parse_idea(ideas_dir / "idea_20260214.md")
        assert hasattr(nugget, 'metadata')
        assert "FEP" in nugget.metadata["tags"]


class TestParseHandoff:
    """Handoff パーサーテスト"""

    def test_parses_handoff(self, bridge, tmp_dirs):
        sessions_dir = tmp_dirs[2]
        _write_handoff(sessions_dir, "handoff_20260214_2100.md", "テスト引き継ぎ", "FEP分析")
        nugget = bridge._parse_handoff(sessions_dir / "handoff_20260214_2100.md")
        assert nugget is not None
        assert "FEP分析" in nugget.title
        assert "gateway:handoff:" in nugget.source

    def test_rejects_old_handoff(self, bridge, tmp_dirs):
        sessions_dir = tmp_dirs[2]
        p = _write_handoff(sessions_dir, "handoff_20250101_0000.md", "古い引き継ぎ")
        # Manually set old mtime
        import os
        old_time = datetime(2025, 1, 1).timestamp()
        os.utime(p, (old_time, old_time))
        nugget = bridge._parse_handoff(p)
        assert nugget is None  # 30日超で除外


class TestParseKI:
    """KI パーサーテスト"""

    def test_parses_ki(self, bridge, tmp_dirs):
        ki_dir = tmp_dirs[3]
        _write_ki(ki_dir, "test_ki.md", "FEPと謙虚さ", "原則 (Principle)")
        nugget = bridge._parse_ki(ki_dir / "test_ki.md")
        assert nugget is not None
        assert "FEPと謙虚さ" in nugget.title
        assert nugget.metadata["tags"] == ["原則 (Principle)"]

    def test_skips_readme(self, bridge, tmp_dirs):
        ki_dir = tmp_dirs[3]
        (ki_dir / "README.md").write_text("# README")
        nugget = bridge._parse_ki(ki_dir / "README.md")
        assert nugget is None


class TestParseDoxa:
    """Doxa パーサーテスト"""

    def test_parses_doxa(self, bridge, tmp_dirs):
        doxa_dir = tmp_dirs[1]
        _write_doxa(doxa_dir, "dox_test.md", "テスト信念")
        nugget = bridge._parse_doxa(doxa_dir / "dox_test.md")
        assert nugget is not None
        assert "テスト信念" in nugget.title
        assert nugget.relevance_score == pytest.approx(0.72, abs=0.01)


# ======================================================
# 2. コンテキストフィルタリングテスト
# ======================================================

class TestFilterByContext:
    """多段階マッチングテスト"""

    def _make_nugget(self, title: str, abstract: str = "", tags=None):
        n = KnowledgeNugget(
            title=title, abstract=abstract,
            source="test", relevance_score=0.5,
            push_reason="test",
        )
        if tags:
            n.metadata = {"tags": tags}
        return n

    def test_direct_match(self, bridge):
        ctx = SessionContext()
        ctx.topics = ["FEP"]
        nuggets = [self._make_nugget("FEP の解析")]
        result = bridge._filter_by_context(nuggets, ctx)
        assert len(result) == 1
        assert result[0].relevance_score > 0.5

    def test_alias_expansion(self, bridge):
        ctx = SessionContext()
        ctx.topics = ["FEP"]
        # 「自由エネルギー」は FEP のエイリアス
        nuggets = [self._make_nugget("自由エネルギー原理")]
        result = bridge._filter_by_context(nuggets, ctx)
        assert len(result) == 1
        assert "関連" in result[0].push_reason

    def test_tag_match(self, bridge):
        ctx = SessionContext()
        ctx.topics = ["FEP"]
        nuggets = [self._make_nugget("謙虚さについて", tags=["FEP"])]
        result = bridge._filter_by_context(nuggets, ctx)
        assert len(result) == 1
        assert "タグ" in result[0].push_reason

    def test_no_match_low_score_excluded(self, bridge):
        ctx = SessionContext()
        ctx.topics = ["FEP"]
        nuggets = [self._make_nugget("無関係なトピック", "")]
        result = bridge._filter_by_context(nuggets, ctx)
        assert len(result) == 0

    def test_high_base_score_passes_through(self, bridge):
        ctx = SessionContext()
        ctx.topics = ["FEP"]
        n = self._make_nugget("無関係だが高スコア")
        n.relevance_score = 0.75
        result = bridge._filter_by_context([n], ctx)
        assert len(result) == 1


# ======================================================
# 3. scan() E2E テスト
# ======================================================

class TestScanE2E:
    """scan() の統合テスト"""

    def test_scan_empty_dirs(self, bridge):
        nuggets = bridge.scan()
        assert nuggets == []

    def test_scan_with_data(self, bridge, tmp_dirs):
        ideas_dir, doxa_dir, sessions_dir, ki_dir = tmp_dirs
        _write_idea(ideas_dir, "idea_20260214.md", "テストアイデア", "FEP")
        _write_ki(ki_dir, "test.md", "テスト知識", "原則")
        nuggets = bridge.scan(max_results=10)
        assert len(nuggets) == 2

    def test_scan_with_source_filter(self, bridge, tmp_dirs):
        ideas_dir, _, _, ki_dir = tmp_dirs
        _write_idea(ideas_dir, "idea_20260214.md", "アイデア")
        _write_ki(ki_dir, "test.md", "知識")
        nuggets = bridge.scan(sources=["ideas"])
        assert len(nuggets) == 1
        assert "ideas" in nuggets[0].source

    def test_scan_with_context(self, bridge, tmp_dirs):
        ideas_dir, _, sessions_dir, ki_dir = tmp_dirs
        _write_idea(ideas_dir, "idea_20260214.md", "FEP分析", "FEP")
        _write_idea(ideas_dir, "idea_20260213.md", "料理レシピ", "家事")
        ctx = SessionContext()
        ctx.topics = ["FEP"]
        nuggets = bridge.scan(context=ctx)
        assert len(nuggets) >= 1
        assert any("FEP" in n.title for n in nuggets)


# ======================================================
# 4. stats() テスト
# ======================================================

class TestStats:
    def test_stats_empty(self, bridge):
        stats = bridge.stats()
        assert "ideas" in stats
        assert stats["ideas"]["exists"]
        assert stats["ideas"]["count"] == 0

    def test_stats_with_data(self, bridge, tmp_dirs):
        _write_idea(tmp_dirs[0], "idea_20260214.md", "テスト")
        stats = bridge.stats()
        assert stats["ideas"]["count"] == 1


# ======================================================
# 5. エイリアス辞書テスト
# ======================================================

class TestTopicAliases:
    def test_fep_aliases(self):
        assert "fep" in _TOPIC_ALIASES
        aliases = _TOPIC_ALIASES["fep"]
        assert "自由エネルギー" in aliases
        assert "prediction error" in aliases

    def test_bidirectional_hgk(self):
        assert "hgk" in _TOPIC_ALIASES
        assert "hegemonikón" in _TOPIC_ALIASES
