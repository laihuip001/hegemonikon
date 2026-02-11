#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ergasterion/digestor/tests/
# PURPOSE: Digestor Pipeline 改善 A-F の包括テスト
"""Digestor Improvements Tests — A-F 全項目"""

import pytest
import yaml
import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import patch, MagicMock


# ═══ テスト用 Paper モック ═══════════════════════════════

@dataclass
class MockPaper:
    """テスト用の Paper モック"""
    id: str
    title: str
    abstract: str = ""
    source: str = "arxiv"
    source_id: str = ""
    categories: list[str] = field(default_factory=list)
    published: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None

    @property
    def primary_key(self) -> str:
        if self.doi:
            return f"doi:{self.doi}"
        if self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        return f"{self.source}:{self.source_id}"

    @property
    def embedding_text(self) -> str:
        return f"{self.title} {self.abstract[:1000]}"


# ═══════════════════════════════════════════════════════════
# F: MCP Import Path Hardening
# ═══════════════════════════════════════════════════════════

class TestF_MCPImportPath:
    """F: digestor_mcp_server.py が正しく import path を設定すること"""

    def test_import_path_pattern(self):
        """import path 設定コードが他の MCP サーバーと同パターンであること"""
        mcp_path = Path(__file__).parent.parent.parent.parent / "mcp" / "digestor_mcp_server.py"
        if not mcp_path.exists():
            pytest.skip("digestor_mcp_server.py not found")
        
        content = mcp_path.read_text()
        # project root + mekhane dir の両方を追加するパターン
        assert "_mekhane_dir" in content, "Should define _mekhane_dir"
        assert "_project_root" in content, "Should define _project_root"
        assert "for _p in" in content, "Should iterate to add both paths"


# ═══════════════════════════════════════════════════════════
# E: Exponential Backoff
# ═══════════════════════════════════════════════════════════

class TestE_ExponentialBackoff:
    """E: pipeline.py に exponential backoff が実装されていること"""

    def test_backoff_in_code(self):
        """pipeline.py に exponential backoff コードが含まれること"""
        pipeline_path = Path(__file__).parent.parent / "pipeline.py"
        content = pipeline_path.read_text()
        assert "max_retries" in content
        assert "2 ** attempt" in content, "Should use exponential backoff formula"


# ═══════════════════════════════════════════════════════════
# A: SemanticMatcher
# ═══════════════════════════════════════════════════════════

class TestA_SemanticMatcher:
    """A: SemanticMatcher のベクトル類似度マッチング"""

    def test_semantic_matcher_init(self):
        """SemanticMatcher が初期化できること"""
        from mekhane.ergasterion.digestor.selector import SemanticMatcher
        matcher = SemanticMatcher()
        assert matcher._adapter is None  # Lazy load
        assert matcher._topic_vectors == {}

    def test_keyword_fallback(self):
        """semantic mode 失敗時にキーワードフォールバックすること"""
        from mekhane.ergasterion.digestor.selector import DigestorSelector
        
        # EmbeddingAdapter が ImportError を投げる場合
        with patch(
            "mekhane.ergasterion.digestor.selector.SemanticMatcher",
            side_effect=Exception("GPU unavailable"),
        ):
            selector = DigestorSelector(mode="semantic")
            # フォールバックしてキーワードモードになる
            assert selector.mode == "keyword"

    def test_keyword_mode_explicit(self):
        """keyword モードを明示指定した場合に動作すること"""
        from mekhane.ergasterion.digestor.selector import DigestorSelector
        
        topics_data = {
            "topics": [
                {"id": "fep", "query": "free energy principle active inference"},
            ]
        }
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(topics_data, f)
            f.flush()
            
            selector = DigestorSelector(topics_file=Path(f.name), mode="keyword")
        
        paper = MockPaper(
            id="1",
            title="Free Energy Principle and Active Inference",
            abstract="A review of the free energy principle and active inference.",
        )
        
        matched = selector._match_topics_keyword(paper)
        assert "fep" in matched

    def test_semantic_match_with_mock_adapter(self):
        """SemanticMatcher がモックアダプターで動作すること"""
        from mekhane.ergasterion.digestor.selector import SemanticMatcher

        matcher = SemanticMatcher()

        # Mock adapter that returns similar vectors
        mock_adapter = MagicMock()
        # Topic vector and paper vector — high similarity
        topic_vec = np.array([1.0, 0.0, 0.0])
        paper_vec = np.array([0.9, 0.1, 0.0])
        
        mock_adapter.encode.side_effect = [
            np.array([topic_vec]),  # topic query
            np.array([paper_vec]),  # paper text
        ]
        matcher._adapter = mock_adapter

        topics = [{"id": "test-topic", "query": "test query"}]
        paper = MockPaper(id="1", title="Test Paper", abstract="Test abstract")

        matches = matcher.match_topics(paper, topics, threshold=0.1)
        assert len(matches) > 0
        assert matches[0][0] == "test-topic"
        assert matches[0][1] > 0.1


# ═══════════════════════════════════════════════════════════
# B: Deduplication
# ═══════════════════════════════════════════════════════════

class TestB_Deduplication:
    """B: 既存インデックスとの重複排除"""

    @pytest.fixture
    def pipeline(self, tmp_path):
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
        from mekhane.ergasterion.digestor.selector import DigestorSelector

        topics_file = tmp_path / "topics.yaml"
        topics_file.write_text(yaml.dump({
            "topics": [{"id": "test", "query": "test topic"}]
        }))
        selector = DigestorSelector(topics_file=topics_file, mode="keyword")
        return DigestorPipeline(output_dir=tmp_path / "output", selector=selector)

    def test_deduplicate_by_primary_key(self, pipeline, tmp_path):
        """primary_key 完全一致で除外されること"""
        # 既存キーの作成
        gnosis_dir = tmp_path / "gnosis"
        gnosis_dir.mkdir()
        existing = [{"primary_key": "arxiv:2401.00001", "title": "Existing Paper"}]
        (gnosis_dir / "papers.json").write_text(json.dumps(existing))

        papers = [
            MockPaper(id="1", title="Paper One", arxiv_id="2401.00001", source_id="1"),
            MockPaper(id="2", title="Paper Two", arxiv_id="2401.00002", source_id="2"),
        ]

        # _load_existing_keys を gnosis_dir を参照するようにモック
        with patch.object(pipeline, '_load_existing_keys', return_value={"arxiv:2401.00001"}):
            result = pipeline._deduplicate_against_indices(papers)

        # Paper One は除外、Paper Two は残る
        assert len(result) == 1
        assert result[0].id == "2"

    def test_deduplicate_empty_papers(self, pipeline):
        """空リストは空リストを返すこと"""
        result = pipeline._deduplicate_against_indices([])
        assert result == []

    def test_dedup_similarity_threshold_value(self, pipeline):
        """閾値が 0.92 (偽陽性許容) であること"""
        assert pipeline.DEDUP_SIMILARITY_THRESHOLD == 0.92


# ═══════════════════════════════════════════════════════════
# C: TemplateClassifier
# ═══════════════════════════════════════════════════════════

class TestC_TemplateClassifier:
    """C: 消化テンプレート T1-T4 のセマンティック分類"""

    def test_template_classifier_init(self):
        """TemplateClassifier が初期化できること"""
        from mekhane.ergasterion.digestor.selector import TemplateClassifier
        classifier = TemplateClassifier()
        assert classifier._adapter is None
        assert classifier._prototype_vectors == {}

    def test_template_prototypes_defined(self):
        """4つの prototype description が定義されていること"""
        from mekhane.ergasterion.digestor.selector import TEMPLATE_PROTOTYPES
        assert len(TEMPLATE_PROTOTYPES) == 4
        assert "T1_mapping" in TEMPLATE_PROTOTYPES
        assert "T2_extraction" in TEMPLATE_PROTOTYPES
        assert "T3_absorption" in TEMPLATE_PROTOTYPES
        assert "T4_import" in TEMPLATE_PROTOTYPES

    def test_classify_with_mock_adapter(self):
        """TemplateClassifier がモックアダプタで Top-2 を返すこと"""
        from mekhane.ergasterion.digestor.selector import TemplateClassifier

        classifier = TemplateClassifier()

        # Mock adapter
        mock_adapter = MagicMock()
        # 4 prototype vectors (normalized)
        proto_vecs = np.array([
            [1.0, 0.0, 0.0],  # T1
            [0.0, 1.0, 0.0],  # T2
            [0.0, 0.0, 1.0],  # T3
            [0.5, 0.5, 0.0],  # T4
        ])
        # Paper vector — closest to T3
        paper_vec = np.array([0.1, 0.1, 0.95])

        mock_adapter.encode.side_effect = [
            proto_vecs,            # prototype descriptions
            np.array([paper_vec]), # paper text
        ]
        classifier._adapter = mock_adapter

        paper = MockPaper(
            id="1",
            title="Algorithm Implementation",
            abstract="Practical algorithm implementation for optimization.",
        )

        result = classifier.classify(paper)
        assert len(result) == 2  # Top-2
        # T3 should have highest score (closest vector)
        assert result[0][0] == "T3_absorption"
        assert result[0][1] > result[1][1]

    def test_digest_candidate_has_templates(self):
        """DigestCandidate に suggested_templates フィールドがあること"""
        from mekhane.ergasterion.digestor.selector import DigestCandidate
        
        paper = MockPaper(id="1", title="Test", abstract="Test")
        candidate = DigestCandidate(
            paper=paper,
            score=0.8,
            matched_topics=["fep"],
            rationale="Test",
            suggested_templates=[("T2_extraction", 0.72), ("T3_absorption", 0.58)],
        )
        assert len(candidate.suggested_templates) == 2
        assert candidate.suggested_templates[0][0] == "T2_extraction"
        assert candidate.suggested_templates[0][1] == 0.72


# ═══════════════════════════════════════════════════════════
# D: 出力フォーマット強化
# ═══════════════════════════════════════════════════════════

class TestD_OutputFormat:
    """D: incoming/ .md テンプレートの強化"""

    @pytest.fixture
    def pipeline(self, tmp_path):
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
        from mekhane.ergasterion.digestor.selector import DigestorSelector

        topics_file = tmp_path / "topics.yaml"
        topics_file.write_text(yaml.dump({
            "topics": [{"id": "test", "query": "test", "digest_to": ["/noe"]}]
        }))
        selector = DigestorSelector(topics_file=topics_file, mode="keyword")
        return DigestorPipeline(output_dir=tmp_path / "output", selector=selector)

    def test_eat_input_has_templates(self, pipeline):
        """_generate_eat_input が推奨テンプレートを含むこと"""
        from mekhane.ergasterion.digestor.selector import DigestCandidate
        
        paper = MockPaper(id="1", title="FEP Study", abstract="About free energy.", url="https://arxiv.org/1234", source_id="1234")
        candidate = DigestCandidate(
            paper=paper,
            score=0.8,
            matched_topics=["test"],
            rationale="Test",
            suggested_templates=[("T2_extraction", 0.72)],
        )
        eat_input = pipeline._generate_eat_input(candidate)
        assert "推奨テンプレート" in eat_input
        assert len(eat_input["推奨テンプレート"]) == 1
        assert eat_input["推奨テンプレート"][0]["id"] == "T2_extraction"

    def test_report_includes_templates(self, pipeline):
        """レポート JSON に suggested_templates が含まれること"""
        from mekhane.ergasterion.digestor.pipeline import DigestResult
        from mekhane.ergasterion.digestor.selector import DigestCandidate

        paper = MockPaper(id="1", title="Test", abstract="Test", url="http://test", source_id="1")
        candidate = DigestCandidate(
            paper=paper,
            score=0.5,
            matched_topics=["test"],
            rationale="Test",
            suggested_templates=[("T3_absorption", 0.65)],
        )

        result = DigestResult(
            timestamp="2026-02-11",
            source="test",
            total_papers=1,
            candidates_selected=1,
            candidates=[candidate],
            dry_run=True,
        )

        report_path = pipeline._save_report(result)
        with open(report_path) as f:
            data = json.load(f)
        
        assert "suggested_templates" in data["candidates"][0]
        assert data["candidates"][0]["suggested_templates"][0]["id"] == "T3_absorption"


# ═══════════════════════════════════════════════════════════
# Topics.yaml v2.0
# ═══════════════════════════════════════════════════════════

class TestTopicsYaml:
    """topics.yaml v2.0 の構造テスト"""

    def test_topics_yaml_has_template_hints(self):
        """全トピックに template_hint があること"""
        topics_path = Path(__file__).parent.parent / "topics.yaml"
        with open(topics_path) as f:
            data = yaml.safe_load(f)
        
        for topic in data["topics"]:
            assert "template_hint" in topic, f"Topic '{topic['id']}' missing template_hint"
            assert topic["template_hint"].startswith("T"), f"Invalid template_hint: {topic['template_hint']}"

    def test_topics_yaml_has_templates_section(self):
        """templates セクションが定義されていること"""
        topics_path = Path(__file__).parent.parent / "topics.yaml"
        with open(topics_path) as f:
            data = yaml.safe_load(f)
        
        assert "templates" in data
        assert len(data["templates"]) == 4

    def test_topics_yaml_version(self):
        """バージョンが 2.0.0 であること"""
        topics_path = Path(__file__).parent.parent / "topics.yaml"
        with open(topics_path) as f:
            data = yaml.safe_load(f)
        
        assert data["version"] == "2.0.0"
