"""
Symplokē Search Engine

Hegemonikón H3: 4知識源の統合検索エンジン
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

from ..indices.base import DomainIndex, IndexedResult, SourceType
from .ranker import Ranker


@dataclass
class SearchConfig:
    """検索設定"""
    default_k: int = 10
    default_weights: Dict[str, float] = field(default_factory=lambda: {
        "gnosis": 0.4,
        "chronos": 0.3,
        "sophia": 0.2,
        "kairos": 0.1,
    })


class SearchEngine:
    """
    統合検索エンジン (Symplokē)
    
    複数の知識源 (Gnōsis, Chronos, Sophia, Kairos) を
    同時に検索し、結果を統合・リランキングする。
    
    Usage:
        engine = SearchEngine()
        engine.register(gnosis_index)
        engine.register(chronos_index)
        
        results = engine.search(
            "active inference",
            sources=["gnosis", "chronos"],
            k=10
        )
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        self._config = config or SearchConfig()
        self._indices: Dict[str, DomainIndex] = {}
        self._ranker = Ranker()
    
    @property
    def registered_sources(self) -> Set[str]:
        """登録済みソース一覧"""
        return set(self._indices.keys())
    
    def register(self, index: DomainIndex) -> None:
        """
        インデックスを登録
        
        Args:
            index: 登録するドメインインデックス
        """
        self._indices[index.name] = index
    
    def unregister(self, name: str) -> bool:
        """
        インデックスを登録解除
        
        Returns:
            解除できた場合 True
        """
        if name in self._indices:
            del self._indices[name]
            return True
        return False
    
    def search(
        self, 
        query: str, 
        sources: Optional[List[str]] = None,
        k: int = 10,
        weights: Optional[Dict[str, float]] = None
    ) -> List[IndexedResult]:
        """
        統合検索
        
        Args:
            query: 検索クエリ
            sources: 検索対象ソース (None = 全ソース)
            k: 最終取得件数
            weights: ソース別重み (None = デフォルト)
        
        Returns:
            リランキング済み IndexedResult のリスト
        """
        # 検索対象ソースの決定
        target_sources = sources or list(self._indices.keys())
        
        # 各ソースから検索
        source_results: Dict[str, List[IndexedResult]] = {}
        
        for source_name in target_sources:
            if source_name not in self._indices:
                continue
            
            index = self._indices[source_name]
            # 各ソースから多めに取得してリランキング
            results = index.search(query, k=k * 2)
            source_results[source_name] = results
        
        # リランキング
        effective_weights = weights or self._config.default_weights
        ranked = self._ranker.rank(source_results, effective_weights)
        
        return ranked[:k]
    
    def search_source(
        self, 
        query: str,
        source: str,
        k: int = 10
    ) -> List[IndexedResult]:
        """
        単一ソース検索 (リランキングなし)
        
        Args:
            query: 検索クエリ
            source: ソース名
            k: 取得件数
        
        Returns:
            IndexedResult のリスト
        """
        if source not in self._indices:
            raise ValueError(f"Unknown source: {source}")
        
        return self._indices[source].search(query, k=k)
    
    def stats(self) -> Dict[str, int]:
        """各ソースの統計情報"""
        return {
            name: index.count() 
            for name, index in self._indices.items()
        }
