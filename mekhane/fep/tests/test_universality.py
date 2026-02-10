"""Tests for mekhane.fep.universality — Kalon (圏論的普遍性検証)."""

import json
import pytest

from mekhane.fep.universality import (
    FactorizationResult,
    KalonResult,
    build_kalon_prompt,
    find_universal_candidate,
    format_kalon_output,
    kalon_score,
    kalon_verify,
    parse_kalon_response,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_candidates():
    """Standard 5-candidate set matching /noe PHASE 2 output."""
    return {
        "V1": "リソース無限なら全自動化で効率を極限まで高める",
        "V2": "機能を最小限に削減し本質に集中する",
        "V3": "業界の常識を完全に破壊して新パラダイムを作る",
        "V4": "データ駆動で最適解を機械的に探索する",
        "Synthesis": "本質的な機能を自動化し、データに基づく効率化を実現する",
    }


@pytest.fixture
def sample_factorizations():
    """Factorization results where Synthesis generalizes V1, V2, V4 but not V3."""
    return [
        FactorizationResult("V1", "Synthesis", True, "V1 is a special case", 0.8),
        FactorizationResult("V2", "Synthesis", True, "V2 is a special case", 0.9),
        FactorizationResult("V3", "Synthesis", False, "V3 is independent", 0.7),
        FactorizationResult("V4", "Synthesis", True, "V4 is a special case", 0.85),
        FactorizationResult("Synthesis", "V1", False, "Synthesis is more general", 0.8),
        FactorizationResult("Synthesis", "V2", False, "Synthesis is more general", 0.9),
        FactorizationResult("Synthesis", "V3", False, "Independent directions", 0.7),
        FactorizationResult("Synthesis", "V4", False, "Synthesis is more general", 0.85),
    ]


# ---------------------------------------------------------------------------
# TestBuildPrompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    """build_kalon_prompt: プロンプトに全候補ペアが含まれるか。"""

    def test_contains_all_candidates(self, sample_candidates):
        prompt = build_kalon_prompt(sample_candidates)
        for name in sample_candidates:
            assert name in prompt

    def test_contains_all_candidate_content(self, sample_candidates):
        prompt = build_kalon_prompt(sample_candidates)
        for content in sample_candidates.values():
            assert content in prompt

    def test_pair_count(self, sample_candidates):
        """5 candidates → C(5,2) = 10 pairs."""
        prompt = build_kalon_prompt(sample_candidates)
        assert prompt.count("### ペア") == 10

    def test_empty_candidates(self):
        prompt = build_kalon_prompt({})
        assert "候補解一覧" in prompt

    def test_single_candidate(self):
        prompt = build_kalon_prompt({"only": "唯一の候補"})
        assert "only" in prompt
        # No pair headers
        assert "### ペア" not in prompt


# ---------------------------------------------------------------------------
# TestParseResponse
# ---------------------------------------------------------------------------

class TestParseResponse:
    """parse_kalon_response: JSON/パターンマッチのパース。"""

    def test_json_parse(self, sample_candidates):
        response = json.dumps([
            {"source": "V1", "target": "Synthesis",
             "factorizable": True, "reasoning": "V1 is specific", "confidence": 0.8},
            {"source": "V3", "target": "Synthesis",
             "factorizable": False, "reasoning": "Independent", "confidence": 0.7},
        ])
        results = parse_kalon_response(response, sample_candidates)
        assert len(results) == 2
        assert results[0].factorizable is True
        assert results[1].factorizable is False

    def test_json_with_surrounding_text(self, sample_candidates):
        response = 'Here is my analysis:\n' + json.dumps([
            {"source": "V2", "target": "Synthesis",
             "factorizable": True, "reasoning": "test", "confidence": 0.9},
        ]) + '\nEnd of analysis.'
        results = parse_kalon_response(response, sample_candidates)
        assert len(results) == 1
        assert results[0].source == "V2"

    def test_fallback_pattern_match(self, sample_candidates):
        response = "V1 は Synthesis の特殊ケース: YES\nV3 は Synthesis: NO"
        results = parse_kalon_response(response, sample_candidates)
        # Should find at least some matches
        assert len(results) >= 1

    def test_empty_response(self, sample_candidates):
        results = parse_kalon_response("", sample_candidates)
        assert len(results) == 0


# ---------------------------------------------------------------------------
# TestFindUniversal
# ---------------------------------------------------------------------------

class TestFindUniversal:
    """find_universal_candidate: 普遍的候補の特定。"""

    def test_synthesis_is_universal(self, sample_candidates, sample_factorizations):
        universal, uniqueness, diagram = find_universal_candidate(
            sample_candidates, sample_factorizations
        )
        assert universal == "Synthesis"
        assert uniqueness == "MED"  # 3/4 = 75%
        assert "V1" in diagram["Synthesis"]
        assert "V2" in diagram["Synthesis"]
        assert "V4" in diagram["Synthesis"]
        assert "V3" not in diagram["Synthesis"]

    def test_all_generalized(self, sample_candidates):
        """If one candidate generalizes all others → HIGH uniqueness."""
        facs = [
            FactorizationResult("V1", "Synthesis", True, "", 0.9),
            FactorizationResult("V2", "Synthesis", True, "", 0.9),
            FactorizationResult("V3", "Synthesis", True, "", 0.9),
            FactorizationResult("V4", "Synthesis", True, "", 0.9),
        ]
        universal, uniqueness, _ = find_universal_candidate(sample_candidates, facs)
        assert universal == "Synthesis"
        assert uniqueness == "HIGH"

    def test_no_factorizations(self, sample_candidates):
        """No factorizations → first candidate, LOW."""
        universal, uniqueness, _ = find_universal_candidate(sample_candidates, [])
        assert uniqueness == "LOW"

    def test_low_confidence_ignored(self, sample_candidates):
        """Factorizations with confidence < 0.3 should be ignored."""
        facs = [
            FactorizationResult("V1", "Synthesis", True, "", 0.1),  # Too low
            FactorizationResult("V2", "Synthesis", True, "", 0.2),  # Too low
        ]
        _, uniqueness, diagram = find_universal_candidate(sample_candidates, facs)
        assert len(diagram.get("Synthesis", [])) == 0

    def test_single_candidate(self):
        candidates = {"only": "唯一"}
        universal, uniqueness, _ = find_universal_candidate(candidates, [])
        assert universal == "only"


# ---------------------------------------------------------------------------
# TestKalonScore
# ---------------------------------------------------------------------------

class TestKalonScore:
    """kalon_score: 経済性スコア。"""

    def test_perfect_score(self, sample_candidates):
        """All candidates covered → 1.0."""
        diagram = {
            "Synthesis": ["V1", "V2", "V3", "V4"],
            "V1": [], "V2": [], "V3": [], "V4": [],
        }
        score = kalon_score("Synthesis", sample_candidates, diagram)
        assert score == 1.0

    def test_partial_score(self, sample_candidates):
        """3/4 candidates covered → 0.75."""
        diagram = {
            "Synthesis": ["V1", "V2", "V4"],
            "V1": [], "V2": [], "V3": [], "V4": [],
        }
        score = kalon_score("Synthesis", sample_candidates, diagram)
        assert score == 0.75

    def test_zero_score(self, sample_candidates):
        """No candidates covered → 0.0."""
        diagram = {
            "Synthesis": [],
            "V1": [], "V2": [], "V3": [], "V4": [],
        }
        score = kalon_score("Synthesis", sample_candidates, diagram)
        assert score == 0.0

    def test_single_candidate(self):
        """Single candidate → 1.0 (trivially universal)."""
        score = kalon_score("only", {"only": "x"}, {"only": []})
        assert score == 1.0


# ---------------------------------------------------------------------------
# TestKalonVerify
# ---------------------------------------------------------------------------

class TestKalonVerify:
    """kalon_verify: 統合テスト。"""

    def test_full_verification(self, sample_candidates, sample_factorizations):
        result = kalon_verify(sample_candidates, sample_factorizations)
        assert isinstance(result, KalonResult)
        assert result.universal_candidate == "Synthesis"
        assert result.kalon_score == 0.75
        assert result.uniqueness == "MED"
        assert len(result.factorizations) == len(sample_factorizations)

    def test_no_factorizations(self, sample_candidates):
        result = kalon_verify(sample_candidates)
        assert isinstance(result, KalonResult)
        assert result.kalon_score == 0.0
        assert result.uniqueness == "LOW"

    def test_beauty_statement_perfect(self, sample_candidates):
        facs = [
            FactorizationResult("V1", "Synthesis", True, "", 0.9),
            FactorizationResult("V2", "Synthesis", True, "", 0.9),
            FactorizationResult("V3", "Synthesis", True, "", 0.9),
            FactorizationResult("V4", "Synthesis", True, "", 0.9),
        ]
        result = kalon_verify(sample_candidates, facs)
        assert "完全な普遍解" in result.beauty_statement

    def test_beauty_statement_partial(self, sample_candidates, sample_factorizations):
        result = kalon_verify(sample_candidates, sample_factorizations)
        assert "独立" in result.beauty_statement


# ---------------------------------------------------------------------------
# TestFormatOutput
# ---------------------------------------------------------------------------

class TestFormatOutput:
    """format_kalon_output: 出力フォーマット。"""

    def test_contains_phase_header(self, sample_candidates, sample_factorizations):
        result = kalon_verify(sample_candidates, sample_factorizations)
        output = format_kalon_output(result)
        assert "PHASE 3: Kalon" in output

    def test_contains_universal_candidate(self, sample_candidates, sample_factorizations):
        result = kalon_verify(sample_candidates, sample_factorizations)
        output = format_kalon_output(result)
        assert "Synthesis" in output

    def test_contains_kalon_score(self, sample_candidates, sample_factorizations):
        result = kalon_verify(sample_candidates, sample_factorizations)
        output = format_kalon_output(result)
        assert "0.75" in output
