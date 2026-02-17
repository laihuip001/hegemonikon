# PROOF: [L3/テスト] <- mekhane/dendron/
"""
Doc Staleness Checker テスト

doc_staleness.py の各機能の単体テスト。
"""

from pathlib import Path

import pytest

from mekhane.dendron.doc_staleness import (
    DocStalenessChecker,
    DocDependency,
    DocInfo,
    StalenessResult,
    _parse_version,
)


# ─── Helpers ──────────────────────────────────────


# PURPOSE: テスト用に frontmatter 付き .md ファイルを生成するファクトリを提供する
@pytest.fixture
def create_md(tmp_path):
    """frontmatter 付き .md ファイルを生成するファクトリ."""
    def _create(
        name: str,
        doc_id: str,
        version: str,
        depends_on: list[dict] | None = None,
        updated: str = "2026-02-17",
        subdir: str = "",
    ) -> Path:
        """Verify create behavior."""
        import yaml

        meta: dict = {
            "doc_id": doc_id,
            "version": version,
            "updated": updated,
        }
        if depends_on:
            meta["depends_on"] = depends_on

        content = f"---\n{yaml.dump(meta, allow_unicode=True)}---\n\n# {doc_id}\n\nContent.\n"
        target_dir = tmp_path / subdir if subdir else tmp_path
        target_dir.mkdir(parents=True, exist_ok=True)
        p = target_dir / name
        p.write_text(content, encoding="utf-8")
        return p

    return _create


# ─── Version Parse Tests ════════════════════════


# PURPOSE: バージョン文字列パースの単体テスト
class TestVersionParse:
    """Semver パースの基本テスト."""

    # PURPOSE: 基本的なバージョン比較
    def test_basic(self) -> None:
        assert _parse_version("1.0.0") == (1, 0, 0)
        assert _parse_version("7.0.0") == (7, 0, 0)

    # PURPOSE: バージョン大小比較
    def test_comparison(self) -> None:
        assert _parse_version("2.0.0") > _parse_version("1.0.0")
        assert _parse_version("1.1.0") > _parse_version("1.0.0")
        assert _parse_version("1.0.1") > _parse_version("1.0.0")
        assert not (_parse_version("1.0.0") > _parse_version("1.0.0"))


# ─── Scan Tests ═════════════════════════════════


# PURPOSE: scan() メソッドのテスト
class TestScan:
    """scan() の基本テスト."""

    # PURPOSE: frontmatter 付き .md を scan で検出する
    def test_scan_finds_docs(self, create_md, tmp_path) -> None:
        create_md("upstream.md", "UPSTREAM", "2.0.0")
        create_md("downstream.md", "DOWNSTREAM", "1.0.0", depends_on=[
            {"doc_id": "UPSTREAM", "min_version": "2.0.0"},
        ])

        checker = DocStalenessChecker()
        docs = checker.scan(tmp_path)
        assert len(docs) == 2
        ids = {d.doc_id for d in docs}
        assert ids == {"UPSTREAM", "DOWNSTREAM"}

    # PURPOSE: frontmatter なしの .md は対象外
    def test_no_frontmatter_skipped(self, tmp_path) -> None:
        (tmp_path / "plain.md").write_text("# No frontmatter\n\nJust text.\n")
        checker = DocStalenessChecker()
        docs = checker.scan(tmp_path)
        assert len(docs) == 0

    # PURPOSE: knowledge_items/ 以下は除外
    def test_knowledge_items_excluded(self, create_md, tmp_path) -> None:
        create_md("ki_doc.md", "KI_DOC", "1.0.0", subdir="knowledge_items")
        create_md("normal.md", "NORMAL", "1.0.0")
        checker = DocStalenessChecker()
        docs = checker.scan(tmp_path)
        assert len(docs) == 1
        assert docs[0].doc_id == "NORMAL"


# ─── Check Tests ════════════════════════════════


# PURPOSE: check() メソッドの判定ロジックテスト
class TestCheck:
    """check() の判定ロジックテスト."""

    # PURPOSE: 上流 v2.0 > 下流 min 1.0 → STALE
    def test_stale_detection(self, create_md, tmp_path) -> None:
        create_md("upstream.md", "UPSTREAM", "2.0.0")
        create_md("downstream.md", "DOWNSTREAM", "1.0.0", depends_on=[
            {"doc_id": "UPSTREAM", "min_version": "1.0.0"},
        ])

        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        results = checker.check()

        stale = [r for r in results if r.status == "STALE"]
        assert len(stale) == 1
        assert stale[0].doc_id == "DOWNSTREAM"
        assert stale[0].upstream_id == "UPSTREAM"

    # PURPOSE: 上流 v1.0 == 下流 min 1.0 → OK
    def test_ok_when_up_to_date(self, create_md, tmp_path) -> None:
        create_md("upstream.md", "UPSTREAM", "1.0.0")
        create_md("downstream.md", "DOWNSTREAM", "1.0.0", depends_on=[
            {"doc_id": "UPSTREAM", "min_version": "1.0.0"},
        ])

        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        results = checker.check()

        ok = [r for r in results if r.status == "OK"]
        assert len(ok) == 1

    # PURPOSE: 上流 updated が31日前 → WARNING
    def test_warning_old_date(self, create_md, tmp_path) -> None:
        create_md("upstream.md", "UPSTREAM", "1.0.0", updated="2026-01-01")
        create_md("downstream.md", "DOWNSTREAM", "1.0.0",
                  updated="2026-02-17",
                  depends_on=[
                      {"doc_id": "UPSTREAM", "min_version": "1.0.0"},
                  ])

        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        results = checker.check()

        warnings = [r for r in results if r.status == "WARNING"]
        assert len(warnings) == 1
        assert "日付差" in warnings[0].detail

    # PURPOSE: A→B→A の循環 → CIRCULAR
    def test_circular_dependency(self, create_md, tmp_path) -> None:
        create_md("a.md", "DOC_A", "1.0.0", depends_on=[
            {"doc_id": "DOC_B", "min_version": "1.0.0"},
        ])
        create_md("b.md", "DOC_B", "1.0.0", depends_on=[
            {"doc_id": "DOC_A", "min_version": "1.0.0"},
        ])

        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        results = checker.check()

        circular = [r for r in results if r.status == "CIRCULAR"]
        assert len(circular) == 2  # both edges flagged

    # PURPOSE: 存在しない doc_id を参照 → STALE
    def test_missing_upstream(self, create_md, tmp_path) -> None:
        create_md("downstream.md", "DOWNSTREAM", "1.0.0", depends_on=[
            {"doc_id": "NONEXISTENT", "min_version": "1.0.0"},
        ])

        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        results = checker.check()

        stale = [r for r in results if r.status == "STALE"]
        assert len(stale) == 1
        assert "見つからない" in stale[0].detail


# ─── Doc Health Tests ═══════════════════════════


# PURPOSE: doc_health_pct() の計算テスト
class TestDocHealth:
    """doc_health_pct() のテスト."""

    # PURPOSE: 4件中2件STALE → 50%
    def test_doc_health_pct(self, create_md, tmp_path) -> None:
        create_md("up1.md", "UP1", "2.0.0")
        create_md("up2.md", "UP2", "2.0.0")
        create_md("ok_doc.md", "OK_DOC", "1.0.0", depends_on=[
            {"doc_id": "UP1", "min_version": "2.0.0"},
            {"doc_id": "UP2", "min_version": "2.0.0"},
        ])
        create_md("stale_doc.md", "STALE_DOC", "1.0.0", depends_on=[
            {"doc_id": "UP1", "min_version": "1.0.0"},
            {"doc_id": "UP2", "min_version": "1.0.0"},
        ])

        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        checker.check()
        pct = checker.doc_health_pct()
        assert pct == 50.0

    # PURPOSE: 依存なしは100%
    def test_no_deps_is_100(self, create_md, tmp_path) -> None:
        create_md("root.md", "ROOT", "1.0.0")
        checker = DocStalenessChecker()
        checker.scan(tmp_path)
        checker.check()
        assert checker.doc_health_pct() == 100.0
