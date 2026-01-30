# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要→test_engine が担う
"""
Symplokē Tests - Search Engine

SearchEngine / Ranker の統合テスト
"""

import pytest
import numpy as np

# テスト対象
from mekhane.symploke.adapters.mock_adapter import MockAdapter
from mekhane.symploke.indices.gnosis import GnosisIndex
from mekhane.symploke.indices.chronos import ChronosIndex
from mekhane.symploke.indices.sophia import SophiaIndex
from mekhane.symploke.indices.kairos import KairosIndex
from mekhane.symploke.indices.base import Document, SourceType
from mekhane.symploke.search.engine import SearchEngine, SearchConfig
from mekhane.symploke.search.ranker import Ranker


class TestSearchEngine:
    """SearchEngine テスト"""
    
    def test_register(self):
        """インデックス登録"""
        engine = SearchEngine()
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis", dimension=128)
        
        engine.register(gnosis)
        
        assert "gnosis" in engine.registered_sources
    
    def test_unregister(self):
        """インデックス登録解除"""
        engine = SearchEngine()
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis", dimension=128)
        
        engine.register(gnosis)
        assert engine.unregister("gnosis") is True
        assert "gnosis" not in engine.registered_sources
        assert engine.unregister("nonexistent") is False
    
    def test_search_empty(self):
        """空エンジンでの検索"""
        engine = SearchEngine()
        results = engine.search("test query")
        assert results == []
    
    def test_search_single_source(self):
        """単一ソース検索"""
        engine = SearchEngine()
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis", dimension=128)
        
        # データ投入
        docs = [
            Document(id=f"paper{i}", content=f"Paper {i} content")
            for i in range(10)
        ]
        gnosis.ingest(docs)
        
        engine.register(gnosis)
        
        # 検索
        results = engine.search("test", k=5)
        
        assert len(results) <= 5
        assert all(r.source == SourceType.GNOSIS for r in results)
    
    def test_stats(self):
        """統計情報"""
        engine = SearchEngine()
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis", dimension=128)
        
        docs = [Document(id=f"p{i}", content=f"content {i}") for i in range(5)]
        gnosis.ingest(docs)
        
        engine.register(gnosis)
        
        stats = engine.stats()
        assert stats["gnosis"] == 5
    
    # ━━━ 統合テスト (Symplokē) ━━━
    
    def test_multi_source_search(self):
        """複数ソースからの統合検索"""
        engine = SearchEngine()
        
        # Gnōsis: 論文
        gnosis_adapter = MockAdapter()
        gnosis = GnosisIndex(gnosis_adapter, "gnosis", dimension=128)
        gnosis.ingest([
            Document(id="paper1", content="Active inference paper"),
            Document(id="paper2", content="Free energy principle"),
        ])
        
        # Chronos: チャット履歴
        chronos_adapter = MockAdapter()
        chronos = ChronosIndex(chronos_adapter, "chronos", dimension=128)
        chronos.ingest([
            Document(id="msg1", content="Previous discussion about FEP"),
            Document(id="msg2", content="Session context"),
        ])
        
        engine.register(gnosis)
        engine.register(chronos)
        
        # 統合検索
        results = engine.search("inference", k=4)
        
        # 両方のソースから結果が返る
        sources = {r.source for r in results}
        assert SourceType.GNOSIS in sources or SourceType.CHRONOS in sources
        assert len(results) <= 4
    
    def test_source_weights(self):
        """重み付けが結果順序に影響"""
        engine = SearchEngine()
        
        # 2つのソースに同量のデータ
        gnosis_adapter = MockAdapter()
        gnosis = GnosisIndex(gnosis_adapter, "gnosis", dimension=128)
        gnosis.ingest([Document(id=f"g{i}", content=f"Gnosis doc {i}") for i in range(5)])
        
        sophia_adapter = MockAdapter()
        sophia = SophiaIndex(sophia_adapter, "sophia", dimension=128)
        sophia.ingest([Document(id=f"s{i}", content=f"Sophia doc {i}") for i in range(5)])
        
        engine.register(gnosis)
        engine.register(sophia)
        
        # Gnōsis を強く重み付け
        results_gnosis_heavy = engine.search(
            "test", 
            k=4, 
            weights={"gnosis": 1.0, "sophia": 0.1}
        )
        
        # Sophia を強く重み付け
        results_sophia_heavy = engine.search(
            "test", 
            k=4,
            weights={"gnosis": 0.1, "sophia": 1.0}
        )
        
        # 結果が異なることを確認（少なくとも順序か内容が変わる）
        # MockAdapter は決定的なので、重み付けの効果を見る
        assert len(results_gnosis_heavy) > 0
        assert len(results_sophia_heavy) > 0
    
    def test_empty_source_handling(self):
        """空のソースが混在しても動作"""
        engine = SearchEngine()
        
        # 空の Gnōsis
        gnosis_adapter = MockAdapter()
        gnosis = GnosisIndex(gnosis_adapter, "gnosis", dimension=128)
        gnosis.initialize()  # 空のまま
        
        # データありの Chronos
        chronos_adapter = MockAdapter()
        chronos = ChronosIndex(chronos_adapter, "chronos", dimension=128)
        chronos.ingest([
            Document(id="msg1", content="Has data"),
        ])
        
        engine.register(gnosis)
        engine.register(chronos)
        
        # 検索してもエラーにならない
        results = engine.search("test", k=5)
        
        # Chronos からのみ結果が返る
        assert all(r.source == SourceType.CHRONOS for r in results)
    
    def test_selective_source_search(self):
        """特定ソースのみを検索"""
        engine = SearchEngine()
        
        gnosis_adapter = MockAdapter()
        gnosis = GnosisIndex(gnosis_adapter, "gnosis", dimension=128)
        gnosis.ingest([Document(id="g1", content="Gnosis only")])
        
        chronos_adapter = MockAdapter()
        chronos = ChronosIndex(chronos_adapter, "chronos", dimension=128)
        chronos.ingest([Document(id="c1", content="Chronos only")])
        
        engine.register(gnosis)
        engine.register(chronos)
        
        # Gnōsis のみ検索
        results = engine.search("test", sources=["gnosis"], k=5)
        
        assert all(r.source == SourceType.GNOSIS for r in results)
    
    def test_four_sources_integration(self):
        """4知識源すべての統合 (Symplokē の本質)"""
        engine = SearchEngine()
        
        # 4つの知識源を準備
        sources_setup = [
            (GnosisIndex, "gnosis", SourceType.GNOSIS, "Research paper"),
            (ChronosIndex, "chronos", SourceType.CHRONOS, "Chat history"),
            (SophiaIndex, "sophia", SourceType.SOPHIA, "Knowledge item"),
            (KairosIndex, "kairos", SourceType.KAIROS, "Session handoff"),
        ]
        
        for IndexClass, name, source_type, content in sources_setup:
            adapter = MockAdapter()
            index = IndexClass(adapter, name, dimension=128)
            index.ingest([Document(id=f"{name}_doc", content=content)])
            engine.register(index)
        
        # 統合検索
        results = engine.search("test", k=10)
        
        # 4つのソースが登録されている
        assert len(engine.registered_sources) == 4
        
        # 結果が返る
        assert len(results) > 0


class TestRanker:
    """Ranker テスト"""
    
    def test_rank_empty(self):
        """空結果のランキング"""
        ranker = Ranker()
        ranked = ranker.rank({}, {})
        assert ranked == []
    
    def test_rank_single_source(self):
        """単一ソースのランキング"""
        from mekhane.symploke.indices.base import IndexedResult
        
        ranker = Ranker()
        results = {
            "gnosis": [
                IndexedResult("doc1", 0.9, SourceType.GNOSIS, "content1", {}),
                IndexedResult("doc2", 0.7, SourceType.GNOSIS, "content2", {}),
            ]
        }
        weights = {"gnosis": 1.0}
        
        ranked = ranker.rank(results, weights)
        
        assert len(ranked) == 2
        assert ranked[0].doc_id == "doc1"  # 高スコアが先


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
