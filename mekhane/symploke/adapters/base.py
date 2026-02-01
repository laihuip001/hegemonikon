# noqa: AI-ALL
"""
# PROOF: [L2/インフラ] A0→ベクトルDBアダプタが必要→base が担う
VectorStore Adapter - Abstract Base Class

Hegemonikón H3 Symplokē: ベクトルDB抽象インターフェース
差し替え可能な設計により、lancedb/hnswlib/faiss/sqlite-vssを透過的に利用可能
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import numpy as np


@dataclass
class SearchResult:
    """検索結果"""

    id: int
    score: float
    metadata: Dict[str, Any]


class VectorStoreAdapter(ABC):
    """
    ベクトルDB抽象インターフェース

    Usage:
        store = HNSWlibAdapter()
        store.create_index(768)
        ids = store.add_vectors(vectors, metadata)
        results = store.search(query, k=10)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """アダプタ名"""
        pass

    @abstractmethod
    def create_index(
        self, dimension: int, index_name: str = "default", **kwargs
    ) -> None:
        """
        インデックスを作成

        Args:
            dimension: ベクトル次元数 (e.g., 768 for text-embedding-3)
            index_name: インデックス名
            **kwargs: 実装固有のパラメータ
        """
        pass

    @abstractmethod
    def add_vectors(
        self,
        vectors: np.ndarray,
        ids: Optional[List[int]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[int]:
        """
        ベクトルを追加

        Args:
            vectors: (N, D) 形状の2次元配列
            ids: 明示的なID (Noneの場合は自動採番)
            metadata: 各ベクトルに紐づくメタデータ

        Returns:
            追加されたIDリスト
        """
        pass

    @abstractmethod
    def search(
        self, query: np.ndarray, k: int = 10, threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        類似検索

        Args:
            query: (D,) 形状のクエリベクトル
            k: 取得件数
            threshold: スコア閾値 (オプション)

        Returns:
            SearchResultのリスト
        """
        pass

    @abstractmethod
    def delete(self, ids: List[int]) -> int:
        """
        ベクトルを削除

        Args:
            ids: 削除するIDリスト

        Returns:
            削除された件数

        Raises:
            NotImplementedError: 削除非対応の実装の場合
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """
        インデックスを永続化

        Args:
            path: 保存先パス
        """
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """
        インデックスを読み込み

        Args:
            path: 読み込み元パス
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """現在のベクトル数を取得"""
        pass

    def get_metadata(self, id: int) -> Optional[Dict[str, Any]]:
        """
        メタデータを取得 (オプション実装)

        デフォルトはNone。サポートする実装でオーバーライド。
        """
        return None
