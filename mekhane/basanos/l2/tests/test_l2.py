# PROOF: [L2/Mekhane] <- mekhane/ A0->Auto->AddedByCI
# PURPOSE: L2 問い生成機構のテスト — G_struct と deficit factory の検証
# REASON: kernel/ の実データに対してパーサーと deficit 検出が正しく動作するか確認
"""Tests for Basanos L2 structural deficit detection."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from mekhane.basanos.l2.models import (
    Deficit,
    DeficitType,
    ExternalForm,
    HGKConcept,
    Question,
)
from mekhane.basanos.l2.g_struct import GStruct
from mekhane.basanos.l2.deficit_factories import (
    EtaDeficitFactory,
    EpsilonDeficitFactory,
    DeltaDeficitFactory,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_KERNEL_MD = textwrap.dedent("""\
    ---
    doc_id: "TEST_SERIES"
    version: "1.0"
    tier: "KERNEL"
    status: "CANONICAL"
    extends:
      axioms: [L0.FEP, L1.Flow]
      generation: "L1 × L1"
    ---

    # Τέστ (Test): テスト定理群

    > **「テストのための認識」**

    ## 定理一覧

    | ID | 名称 | 生成 | 意味 |
    |----|------|------|------|
    | O1 | **Noēsis** | I × E | 認識推論 |
    | O2 | **Boulēsis** | I × P | 意志推論 |

    ## 各定理の詳細

    ### O1: Noēsis (認識)

    > **「世界を理解するための推論」**

    - I (推論) × E (認識)

    ## 実装詳細

    ### 実現構造

    | 項目 | 内容 |
    |------|------|
    | 発動条件 | /noe |
    | 入力 | 問い Q |
""")


@pytest.fixture
def tmp_kernel(tmp_path: Path) -> Path:
    """Create a temporary kernel directory with sample files."""
    kernel = tmp_path / "kernel"
    kernel.mkdir()
    (kernel / "test_series.md").write_text(SAMPLE_KERNEL_MD)
    return kernel


@pytest.fixture
def g_struct(tmp_kernel: Path) -> GStruct:
    """Create a GStruct instance for the temp kernel."""
    return GStruct(tmp_kernel)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestModels:
    """Test core data models."""

    def test_deficit_type_values(self) -> None:
        assert DeficitType.ETA.value == "η"
        assert DeficitType.EPSILON_IMPL.value == "ε-impl"
        assert DeficitType.EPSILON_JUST.value == "ε-just"
        assert DeficitType.DELTA.value == "Δε/Δt"

    def test_external_form_creation(self) -> None:
        ef = ExternalForm(
            source_path="kernel/ousia.md",
            keywords=["Noēsis", "FEP"],
            claims=["世界を理解するための推論"],
            theorem_ids=["O1", "O2"],
        )
        assert ef.source_path == "kernel/ousia.md"
        assert "Noēsis" in ef.keywords
        assert len(ef.theorem_ids) == 2

    def test_deficit_to_question(self) -> None:
        d = Deficit(
            type=DeficitType.ETA,
            severity=0.7,
            source="Active Inference Paper",
            target="prediction error",
            description="テスト",
        )
        q = d.to_question()
        assert isinstance(q, Question)
        assert q.priority == 0.7
        assert "Active Inference Paper" in q.text
        assert not q.answered

    def test_hgk_concept(self) -> None:
        c = HGKConcept(
            doc_id="OUSIA_SERIES",
            path="kernel/ousia.md",
            title="Ousia 本質定理群",
            series="O",
            theorem_ids=["O1", "O2", "O3", "O4"],
        )
        assert c.series == "O"
        assert len(c.theorem_ids) == 4


# ---------------------------------------------------------------------------
# G_struct tests
# ---------------------------------------------------------------------------


class TestGStruct:
    """Test structural parser."""

    def test_parse_file(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        concept = g_struct.parse_file(tmp_kernel / "test_series.md")
        assert concept is not None
        assert concept.doc_id == "TEST_SERIES"
        assert concept.status == "CANONICAL"
        assert "O1" in concept.theorem_ids
        assert "O2" in concept.theorem_ids

    def test_parse_frontmatter_extends(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        concept = g_struct.parse_file(tmp_kernel / "test_series.md")
        assert concept is not None
        assert "L0.FEP" in concept.extends
        assert "L1.Flow" in concept.extends

    def test_extract_external_form(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        ef = g_struct.extract_external_form(tmp_kernel / "test_series.md")
        assert ef is not None
        assert len(ef.theorem_ids) >= 2
        assert "L0.FEP" in ef.dependencies

    def test_extract_claims(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        ef = g_struct.extract_external_form(tmp_kernel / "test_series.md")
        assert ef is not None
        assert any("テスト" in c or "認識" in c or "推論" in c for c in ef.claims)

    def test_extract_keywords(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        ef = g_struct.extract_external_form(tmp_kernel / "test_series.md")
        assert ef is not None
        assert len(ef.keywords) > 0

    def test_scan_all(self, g_struct: GStruct) -> None:
        concepts = g_struct.scan_all()
        assert len(concepts) == 1
        assert concepts[0].doc_id == "TEST_SERIES"

    def test_parse_nonexistent(self, g_struct: GStruct) -> None:
        assert g_struct.parse_file(Path("/nonexistent.md")) is None

    def test_detect_series_ousia(self, g_struct: GStruct) -> None:
        series = g_struct._detect_series("OUSIA_SERIES", "kernel/ousia.md")
        assert series == "O"

    def test_detect_series_schema(self, g_struct: GStruct) -> None:
        series = g_struct._detect_series("SCHEMA_SERIES", "kernel/schema.md")
        assert series == "S"


# ---------------------------------------------------------------------------
# Deficit factory tests
# ---------------------------------------------------------------------------


class TestEtaDeficitFactory:
    """Test η deficit detection."""

    def test_detect_unabsorbed(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        factory = EtaDeficitFactory(g_struct, tmp_kernel.parent)
        deficits = factory.detect(
            paper_keywords=["quantum cognition", "Bayesian brain"],
            paper_title="Test Paper",
        )
        assert len(deficits) >= 1
        assert all(d.type == DeficitType.ETA for d in deficits)

    def test_no_deficit_when_keyword_exists(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        factory = EtaDeficitFactory(g_struct, tmp_kernel.parent)
        deficits = factory.detect(
            paper_keywords=["Noēsis"],
            paper_title="Test Paper",
        )
        assert len(deficits) == 0

    def test_question_generation(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        factory = EtaDeficitFactory(g_struct, tmp_kernel.parent)
        deficits = factory.detect(
            paper_keywords=["novel concept"],
            paper_title="Important Paper",
        )
        assert len(deficits) >= 1
        q = deficits[0].to_question()
        assert "Important Paper" in q.text


class TestEpsilonDeficitFactory:
    """Test ε deficit detection."""

    def test_detect_impl_deficits(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        factory = EpsilonDeficitFactory(g_struct, tmp_kernel.parent)
        deficits = factory.detect_impl_deficits()
        assert len(deficits) >= 1
        assert all(d.type == DeficitType.EPSILON_IMPL for d in deficits)

    def test_detect_justification_deficits(self, g_struct: GStruct, tmp_kernel: Path) -> None:
        factory = EpsilonDeficitFactory(g_struct, tmp_kernel.parent)
        deficits = factory.detect_justification_deficits(
            gnosis_keywords=set()
        )
        assert all(d.type == DeficitType.EPSILON_JUST for d in deficits)


class TestDeltaDeficitFactory:
    """Test Δε/Δt deficit detection."""

    def test_init(self, tmp_kernel: Path) -> None:
        factory = DeltaDeficitFactory(tmp_kernel.parent)
        assert factory.project_root == tmp_kernel.parent

    def test_detect_no_git(self, tmp_kernel: Path) -> None:
        factory = DeltaDeficitFactory(tmp_kernel.parent)
        deficits = factory.detect()
        assert deficits == []


# ---------------------------------------------------------------------------
# Integration: Real kernel/
# ---------------------------------------------------------------------------


class TestRealKernel:
    """Integration test against actual kernel/ directory."""

    PROJECT_ROOT = Path("/home/makaron8426/oikos/hegemonikon")
    KERNEL_ROOT = PROJECT_ROOT / "kernel"

    @pytest.mark.skipif(
        not (Path("/home/makaron8426/oikos/hegemonikon/kernel/ousia.md").exists()),
        reason="Real kernel/ not available",
    )
    def test_parse_real_ousia(self) -> None:
        g = GStruct(self.KERNEL_ROOT)
        concept = g.parse_file(self.KERNEL_ROOT / "ousia.md")
        assert concept is not None
        assert concept.doc_id == "OUSIA_SERIES"
        assert concept.series == "O"
        assert "O1" in concept.theorem_ids

    @pytest.mark.skipif(
        not (Path("/home/makaron8426/oikos/hegemonikon/kernel/ousia.md").exists()),
        reason="Real kernel/ not available",
    )
    def test_scan_real_kernel(self) -> None:
        g = GStruct(self.KERNEL_ROOT)
        concepts = g.scan_all()
        assert len(concepts) >= 5

    @pytest.mark.skipif(
        not (Path("/home/makaron8426/oikos/hegemonikon/kernel/ousia.md").exists()),
        reason="Real kernel/ not available",
    )
    def test_real_external_form(self) -> None:
        g = GStruct(self.KERNEL_ROOT)
        ef = g.extract_external_form(self.KERNEL_ROOT / "ousia.md")
        assert ef is not None
        assert len(ef.keywords) > 0
        assert len(ef.theorem_ids) >= 4
        assert "L0.FEP" in ef.dependencies
