# PROOF: [L3/テスト] <- mekhane/symploke/tests/ 対象モジュールが存在→検証が必要→test_indices が担う
"""
Symplokē Tests - Index Layer

Domain Index の単体テスト
"""

import pytest
import numpy as np
from pathlib import Path

# テスト対象
from mekhane.symploke.adapters.mock_adapter import MockAdapter
from mekhane.symploke.indices.base import (
    DomainIndex,
    SourceType,
    Document,
    IndexedResult,
)
from mekhane.symploke.indices.gnosis import GnosisIndex
from mekhane.symploke.indices.chronos import ChronosIndex
from mekhane.symploke.indices.sophia import SophiaIndex
from mekhane.symploke.indices.kairos import KairosIndex


# PURPOSE: MockAdapter テスト
class TestMockAdapter:
    """MockAdapter テスト"""

    # PURPOSE: インデックス作成
    def test_create_index(self):
        """インデックス作成"""
        adapter = MockAdapter()
        adapter.create_index(dimension=768)
        assert adapter.dimension == 768
        assert adapter.count() == 0

    # PURPOSE: ベクトル追加
    def test_add_vectors(self):
        """ベクトル追加"""
        adapter = MockAdapter()
        adapter.create_index(dimension=128)

        vectors = np.random.randn(10, 128).astype(np.float32)
        ids = adapter.add_vectors(vectors)

        assert len(ids) == 10
        assert adapter.count() == 10

    # PURPOSE: メタデータ付きベクトル追加
    def test_add_vectors_with_metadata(self):
        """メタデータ付きベクトル追加"""
        adapter = MockAdapter()
        adapter.create_index(dimension=128)

        vectors = np.random.randn(5, 128).astype(np.float32)
        metadata = [{"title": f"Doc {i}"} for i in range(5)]
        ids = adapter.add_vectors(vectors, metadata=metadata)

        assert len(ids) == 5
        assert adapter.get_metadata(0) == {"title": "Doc 0"}

    # PURPOSE: search をテストする
    def test_search(self):
        """検索"""
        adapter = MockAdapter()
        adapter.create_index(dimension=128)

        vectors = np.random.randn(20, 128).astype(np.float32)
        adapter.add_vectors(vectors)

        query = np.random.randn(128).astype(np.float32)
        results = adapter.search(query, k=5)

        assert len(results) == 5


# PURPOSE: GnosisIndex テスト
class TestGnosisIndex:
    """GnosisIndex テスト"""

    # PURPOSE: ソース種別
    def test_source_type(self):
        """ソース種別"""
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis")
        assert gnosis.source_type == SourceType.GNOSIS

    # PURPOSE: ドキュメントインジェスト
    def test_ingest(self):
        """ドキュメントインジェスト"""
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis", dimension=128)

        docs = [
            Document(id="paper1", content="Active inference paper"),
            Document(id="paper2", content="Free energy principle"),
        ]
        count = gnosis.ingest(docs)

        assert count == 2
        assert gnosis.count() == 2

    # PURPOSE: search をテストする
    def test_search(self):
        """検索"""
        adapter = MockAdapter()
        gnosis = GnosisIndex(adapter, "gnosis", dimension=128)

        docs = [
            Document(id="paper1", content="Active inference paper"),
            Document(id="paper2", content="Free energy principle"),
        ]
        gnosis.ingest(docs)

        results = gnosis.search("inference", k=2)

        assert len(results) == 2
        assert all(isinstance(r, IndexedResult) for r in results)
        assert all(r.source == SourceType.GNOSIS for r in results)


# PURPOSE: ChronosIndex テスト
class TestChronosIndex:
    """ChronosIndex テスト"""

    # PURPOSE: source_type をテストする
    def test_source_type(self):
        adapter = MockAdapter()
        chronos = ChronosIndex(adapter, "chronos", dimension=128)
        assert chronos.source_type == SourceType.CHRONOS

    # PURPOSE: ingest をテストする
    def test_ingest(self):
        adapter = MockAdapter()
        chronos = ChronosIndex(adapter, "chronos", dimension=128)

        docs = [
            Document(id="msg1", content="Hello", metadata={"session_id": "s1"}),
            Document(id="msg2", content="World", metadata={"session_id": "s1"}),
        ]
        count = chronos.ingest(docs)

        assert count == 2
        assert chronos.count() == 2

    # PURPOSE: search をテストする
    def test_search(self):
        adapter = MockAdapter()
        chronos = ChronosIndex(adapter, "chronos", dimension=128)

        docs = [Document(id=f"msg{i}", content=f"Message {i}") for i in range(5)]
        chronos.ingest(docs)

        results = chronos.search("test", k=3)
        assert len(results) <= 3
        assert all(r.source == SourceType.CHRONOS for r in results)


# PURPOSE: SophiaIndex テスト
class TestSophiaIndex:
    """SophiaIndex テスト"""

    # PURPOSE: source_type をテストする
    def test_source_type(self):
        adapter = MockAdapter()
        sophia = SophiaIndex(adapter, "sophia", dimension=128)
        assert sophia.source_type == SourceType.SOPHIA

    # PURPOSE: ingest をテストする
    def test_ingest(self):
        adapter = MockAdapter()
        sophia = SophiaIndex(adapter, "sophia", dimension=128)

        docs = [
            Document(
                id="ki1", content="Architecture patterns", metadata={"category": "arch"}
            ),
        ]
        count = sophia.ingest(docs)

        assert count == 1


# PURPOSE: KairosIndex テスト
class TestKairosIndex:
    """KairosIndex テスト"""

    # PURPOSE: source_type をテストする
    def test_source_type(self):
        adapter = MockAdapter()
        kairos = KairosIndex(adapter, "kairos", dimension=128)
        assert kairos.source_type == SourceType.KAIROS

    # PURPOSE: ingest をテストする
    def test_ingest(self):
        adapter = MockAdapter()
        kairos = KairosIndex(adapter, "kairos", dimension=128)

        docs = [
            Document(
                id="handoff1", content="Pending tasks", metadata={"status": "pending"}
            ),
        ]
        count = kairos.ingest(docs)

        assert count == 1

    # PURPOSE: get_pending_tasks をテストする
    def test_get_pending_tasks(self):
        adapter = MockAdapter()
        kairos = KairosIndex(adapter, "kairos", dimension=128)

        docs = [
            Document(id="h1", content="Pending task 1", metadata={"status": "pending"}),
            Document(
                id="h2", content="Completed task", metadata={"status": "completed"}
            ),
        ]
        kairos.ingest(docs)

        pending = kairos.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0]["doc_id"] == "h1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
