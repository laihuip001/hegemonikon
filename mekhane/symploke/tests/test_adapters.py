"""
Symplokē Tests - VectorStore Adapters

単体テスト: hnswlib adapter
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path

# テスト対象
from mekhane.symploke.adapters.hnswlib_adapter import HNSWlibAdapter
from mekhane.symploke.adapters.base import SearchResult
from mekhane.symploke.factory import VectorStoreFactory


class TestHNSWlibAdapter:
    """HNSWlib Adapter テスト"""
    
    def test_create_index(self):
        """インデックス作成"""
        adapter = HNSWlibAdapter()
        adapter.create_index(dimension=128)
        assert adapter.dimension == 128
        assert adapter.count() == 0
    
    def test_add_vectors(self):
        """ベクトル追加"""
        adapter = HNSWlibAdapter()
        adapter.create_index(dimension=128)
        
        vectors = np.random.randn(100, 128).astype(np.float32)
        ids = adapter.add_vectors(vectors)
        
        assert len(ids) == 100
        assert adapter.count() == 100
    
    def test_add_vectors_with_metadata(self):
        """メタデータ付きベクトル追加"""
        adapter = HNSWlibAdapter()
        adapter.create_index(dimension=128)
        
        vectors = np.random.randn(10, 128).astype(np.float32)
        metadata = [{"title": f"Paper {i}"} for i in range(10)]
        ids = adapter.add_vectors(vectors, metadata=metadata)
        
        assert len(ids) == 10
        assert adapter.get_metadata(0) == {"title": "Paper 0"}
    
    def test_search(self):
        """検索"""
        adapter = HNSWlibAdapter()
        adapter.create_index(dimension=128)
        
        # データ追加
        vectors = np.random.randn(100, 128).astype(np.float32)
        adapter.add_vectors(vectors)
        
        # 検索
        query = vectors[0]  # 既存ベクトルをクエリ
        results = adapter.search(query, k=5)
        
        assert len(results) == 5
        assert isinstance(results[0], SearchResult)
        assert results[0].id == 0  # 自分自身が最近傍
    
    def test_save_load(self):
        """永続化と読み込み"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.hnsw"
            
            # 保存
            adapter1 = HNSWlibAdapter()
            adapter1.create_index(dimension=64)
            vectors = np.random.randn(50, 64).astype(np.float32)
            metadata = [{"id": i} for i in range(50)]
            adapter1.add_vectors(vectors, metadata=metadata)
            adapter1.save(str(path))
            
            # 読み込み
            adapter2 = HNSWlibAdapter()
            adapter2.load(str(path))
            
            assert adapter2.count() == 50
            assert adapter2.dimension == 64
            assert adapter2.get_metadata(10) == {"id": 10}


class TestVectorStoreFactory:
    """Factory テスト"""
    
    def test_create_hnswlib(self):
        """hnswlibアダプタ生成"""
        if not VectorStoreFactory.is_registered("hnswlib"):
            pytest.skip("hnswlib not available")
        
        store = VectorStoreFactory.create("hnswlib")
        assert store.name == "hnswlib"
    
    def test_unknown_adapter(self):
        """未知のアダプタ"""
        with pytest.raises(ValueError):
            VectorStoreFactory.create("unknown_adapter")
    
    def test_list_adapters(self):
        """登録済みアダプタ一覧"""
        adapters = VectorStoreFactory.list_adapters()
        assert isinstance(adapters, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
