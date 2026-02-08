"""
# PROOF: [L2/インフラ] <- mekhane/symploke/adapters/ A0→ベクトルDBアダプタが必要→mock_adapter が担う
MockAdapter - テスト用ダミーアダプタ

データ無しでインターフェースの検証を可能にする
"""

from typing import List, Dict, Any, Optional
import numpy as np
from .base import VectorStoreAdapter, SearchResult


# PURPOSE: テスト用 Mock アダプタ
class MockAdapter(VectorStoreAdapter):
    """
    テスト用 Mock アダプタ

    実際のベクトル演算を行わず、インターフェースの
    contract のみを検証するためのダミー実装。

    Usage:
        adapter = MockAdapter()
        adapter.create_index(768)
        ids = adapter.add_vectors(np.zeros((10, 768)))
        results = adapter.search(np.zeros(768), k=5)
    """

    def __init__(self):
        self._dimension: Optional[int] = None
        self._vectors: List[np.ndarray] = []
        self._metadata: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 0

    # PURPOSE: name の処理
    @property
    def name(self) -> str:
        return "mock"

    # PURPOSE: dimension の処理
    @property
    def dimension(self) -> Optional[int]:
        return self._dimension

    # PURPOSE: index を生成する
    def create_index(
        self, dimension: int, index_name: str = "default", **kwargs
    ) -> None:
        self._dimension = dimension
        self._vectors = []
        self._metadata = {}
        self._next_id = 0

    # PURPOSE: vectors を追加する
    def add_vectors(
        self,
        vectors: np.ndarray,
        ids: Optional[List[int]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[int]:
        if self._dimension is None:
            raise RuntimeError("Index not created. Call create_index first.")

        if vectors.ndim != 2 or vectors.shape[1] != self._dimension:
            raise ValueError(
                f"Expected shape (N, {self._dimension}), got {vectors.shape}"
            )

        n = vectors.shape[0]

        # ID 生成
        if ids is None:
            ids = list(range(self._next_id, self._next_id + n))
            self._next_id += n

        # ベクトル保存
        for i, vec in enumerate(vectors):
            self._vectors.append(vec.copy())
            if metadata and i < len(metadata):
                self._metadata[ids[i]] = metadata[i]
            else:
                self._metadata[ids[i]] = {}

        return ids

    # PURPOSE: search を検索する
    def search(
        self, query: np.ndarray, k: int = 10, threshold: Optional[float] = None
    ) -> List[SearchResult]:
        if self._dimension is None:
            raise RuntimeError("Index not created.")

        if len(self._vectors) == 0:
            return []

        # Mock: 単純に最初の k 件を返す (スコアはランダム)
        results = []
        for i in range(min(k, len(self._vectors))):
            results.append(
                SearchResult(
                    id=i,
                    score=1.0 - (i * 0.1),
                    metadata=self._metadata.get(i, {}),  # 降順スコア
                )
            )

        return results

    # PURPOSE: delete を削除する
    def delete(self, ids: List[int]) -> int:
        # Mock: 削除はサポートしない（テスト用）
        raise NotImplementedError("MockAdapter does not support delete")

    # PURPOSE: save を保存する
    def save(self, path: str) -> None:
        # Mock: 永続化は何もしない
        pass

    # PURPOSE: load をロードする
    def load(self, path: str) -> None:
        # Mock: 読み込みは何もしない
        pass

    # PURPOSE: count の処理
    def count(self) -> int:
        return len(self._vectors)

    # PURPOSE: metadata を取得する
    def get_metadata(self, id: int) -> Optional[Dict[str, Any]]:
        return self._metadata.get(id)
