"""
# PROOF: [L2/インフラ] <- mekhane/symploke/adapters/ A0→ベクトルDBアダプタが必要→embedding_adapter が担う
EmbeddingAdapter - sentence-transformers を使用した実ベクトル検索アダプタ

MockAdapter とは異なり、実際の埋め込み計算と類似度検索を行う。
"""

import os
from typing import List, Dict, Any, Optional
import numpy as np
from .base import VectorStoreAdapter, SearchResult

# 環境変数でモデルを切り替え可能 (bge-m3 移行 Step 1)
DEFAULT_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-m3")


class EmbeddingAdapter(VectorStoreAdapter):
    """
    sentence-transformers を使用した本番用アダプタ

    Usage:
        adapter = EmbeddingAdapter()  # EMBEDDING_MODEL 環境変数 or デフォルト
        adapter.create_index(384)     # MiniLM: 384d, bge-m3: 1024d
        ids = adapter.add_vectors(vectors, metadata=[...])
        results = adapter.search(query_vector, k=5)
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self._model_name = model_name
        self._model = None  # Lazy load
        self._dimension: Optional[int] = None
        self._vectors: List[np.ndarray] = []
        self._metadata: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 0

    @property
    def name(self) -> str:
        return f"embedding:{self._model_name}"

    @property
    def dimension(self) -> Optional[int]:
        return self._dimension

    def _get_model(self):
        """Lazy load sentence-transformers model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to vectors."""
        model = self._get_model()
        return model.encode(texts, convert_to_numpy=True)

    def create_index(
        self, dimension: int, index_name: str = "default", **kwargs
    ) -> None:
        self._dimension = dimension
        self._vectors = []
        self._metadata = {}
        self._next_id = 0

    def add_vectors(
        self,
        vectors: np.ndarray,
        ids: Optional[List[int]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[int]:
        if self._dimension is None:
            raise RuntimeError("Index not created. Call create_index first.")

        if vectors.ndim != 2:
            raise ValueError(f"Expected 2D array, got {vectors.ndim}D")

        n = vectors.shape[0]

        # ID 生成
        if ids is None:
            ids = list(range(self._next_id, self._next_id + n))
            self._next_id += n

        # ベクトル保存（正規化）
        for i, vec in enumerate(vectors):
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self._vectors.append(vec.copy())
            if metadata and i < len(metadata):
                self._metadata[ids[i]] = metadata[i]
            else:
                self._metadata[ids[i]] = {}

        return ids

    def search(
        self, query: np.ndarray, k: int = 10, threshold: Optional[float] = None
    ) -> List[SearchResult]:
        if self._dimension is None:
            raise RuntimeError("Index not created.")

        if len(self._vectors) == 0:
            return []

        # クエリを正規化
        query_norm = np.linalg.norm(query)
        if query_norm > 0:
            query = query / query_norm

        # コサイン類似度計算
        scores = []
        for i, vec in enumerate(self._vectors):
            score = float(np.dot(query, vec))
            scores.append((i, score))

        # スコア降順ソート
        scores.sort(key=lambda x: x[1], reverse=True)

        # 上位 k 件を返す
        results = []
        for idx, score in scores[:k]:
            if threshold is not None and score < threshold:
                break
            results.append(
                SearchResult(id=idx, score=score, metadata=self._metadata.get(idx, {}))
            )

        return results

    def delete(self, ids: List[int]) -> int:
        raise NotImplementedError("EmbeddingAdapter does not support delete yet")

    def save(self, path: str) -> None:
        import pickle

        data = {
            "dimension": self._dimension,
            "vectors": self._vectors,
            "metadata": self._metadata,
            "next_id": self._next_id,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str) -> None:
        import pickle

        with open(path, "rb") as f:
            data = pickle.load(f)
        self._dimension = data["dimension"]
        self._vectors = data["vectors"]
        self._metadata = data["metadata"]
        self._next_id = data["next_id"]

    def count(self) -> int:
        return len(self._vectors)

    def get_metadata(self, id: int) -> Optional[Dict[str, Any]]:
        return self._metadata.get(id)
