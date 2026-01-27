"""
HNSWlib Adapter - High-speed approximate nearest neighbor search

パプ君調査結果より:
- 検索速度: <2ms (GIST-1M)
- メモリ効率: 良好
- 永続化: save_index/load_index
- 削除: 非対応
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pickle
from pathlib import Path

from .base import VectorStoreAdapter, SearchResult

try:
    import hnswlib
except ImportError:
    hnswlib = None


class HNSWlibAdapter(VectorStoreAdapter):
    """
    hnswlib ベースのベクトルストア
    
    特徴:
    - 高速検索 (<2ms for 1M vectors)
    - 低メモリ使用量
    - 永続化対応
    - 削除非対応（再構築が必要）
    """
    
    def __init__(
        self,
        space: str = "l2",
        M: int = 16,
        ef_construction: int = 200,
        max_elements: int = 1_000_000
    ):
        """
        Args:
            space: 距離空間 ("l2", "ip", "cosine")
            M: HNSW接続数 (高いほど精度↑メモリ↑)
            ef_construction: 構築時探索範囲
            max_elements: 最大ベクトル数
        """
        if hnswlib is None:
            raise ImportError(
                "hnswlib package required. Install with:\n"
                "  pip install hnswlib"
            )
        
        self.space = space
        self.M = M
        self.ef_construction = ef_construction
        self.max_elements = max_elements
        
        self.index: Optional[hnswlib.Index] = None
        self.dimension: int = 0
        self._metadata: Dict[int, Dict[str, Any]] = {}
        self._current_id: int = 0
    
    @property
    def name(self) -> str:
        return "hnswlib"
    
    def create_index(
        self, 
        dimension: int, 
        index_name: str = "default",
        **kwargs
    ) -> None:
        """インデックスを作成"""
        self.dimension = dimension
        self.index = hnswlib.Index(space=self.space, dim=dimension)
        self.index.init_index(
            max_elements=kwargs.get("max_elements", self.max_elements),
            ef_construction=kwargs.get("ef_construction", self.ef_construction),
            M=kwargs.get("M", self.M)
        )
        # 検索時の探索範囲（精度/速度トレードオフ）
        self.index.set_ef(kwargs.get("ef", 256))
        self._metadata.clear()
        self._current_id = 0
    
    def add_vectors(
        self, 
        vectors: np.ndarray, 
        ids: Optional[List[int]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """ベクトルを追加"""
        if self.index is None:
            raise RuntimeError("Index not initialized. Call create_index() first.")
        
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        
        n = len(vectors)
        
        # ID生成
        if ids is None:
            ids = list(range(self._current_id, self._current_id + n))
            self._current_id += n
        
        # 追加
        self.index.add_items(vectors, np.array(ids))
        
        # メタデータ保存
        if metadata:
            for i, vec_id in enumerate(ids):
                self._metadata[vec_id] = metadata[i] if i < len(metadata) else {}
        
        return ids
    
    def search(
        self, 
        query: np.ndarray, 
        k: int = 10,
        threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """類似検索"""
        if self.index is None or self.index.get_current_count() == 0:
            return []
        
        query = np.asarray(query, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)
        
        # 検索
        labels, distances = self.index.knn_query(query, k=min(k, self.index.get_current_count()))
        
        results = []
        for idx, (label, dist) in enumerate(zip(labels[0], distances[0])):
            if threshold is not None and dist > threshold:
                continue
            results.append(SearchResult(
                id=int(label),
                score=float(dist),
                metadata=self._metadata.get(int(label), {})
            ))
        
        return results
    
    def delete(self, ids: List[int]) -> int:
        """削除（非対応 - 再構築が必要）"""
        raise NotImplementedError(
            "hnswlib does not support deletion. "
            "Rebuild the index without the deleted vectors."
        )
    
    def save(self, path: str) -> None:
        """インデックスを永続化"""
        if self.index is None:
            raise RuntimeError("No index to save")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # インデックス保存
        self.index.save_index(str(path))
        
        # メタデータ保存 (拡張子を追加、置換ではない)
        meta_path = Path(str(path) + ".meta.pkl")
        with open(meta_path, "wb") as f:
            pickle.dump({
                "dimension": self.dimension,
                "metadata": self._metadata,
                "current_id": self._current_id,
                "space": self.space,
                "M": self.M,
                "ef_construction": self.ef_construction,
                "max_elements": self.max_elements
            }, f)
    
    def load(self, path: str) -> None:
        """インデックスを読み込み"""
        path = Path(path)
        
        # メタデータ読み込み (拡張子を追加、置換ではない)
        meta_path = Path(str(path) + ".meta.pkl")
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {meta_path}. "
                "Cannot load index without metadata."
            )
        
        with open(meta_path, "rb") as f:
            meta = pickle.load(f)
            self.dimension = meta.get("dimension", 0)
            self._metadata = meta.get("metadata", {})
            self._current_id = meta.get("current_id", 0)
            self.space = meta.get("space", "l2")
            self.M = meta.get("M", 16)
            self.ef_construction = meta.get("ef_construction", 200)
            self.max_elements = meta.get("max_elements", 1_000_000)
        
        if self.dimension == 0:
            raise ValueError("Invalid dimension (0) in metadata")
        
        # インデックス読み込み
        self.index = hnswlib.Index(space=self.space, dim=self.dimension)
        self.index.load_index(str(path), max_elements=self.max_elements)
    
    def count(self) -> int:
        """現在のベクトル数"""
        if self.index is None:
            return 0
        return self.index.get_current_count()
    
    def get_metadata(self, id: int) -> Optional[Dict[str, Any]]:
        """メタデータを取得"""
        return self._metadata.get(id)
