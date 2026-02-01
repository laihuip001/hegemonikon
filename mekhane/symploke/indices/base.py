# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/symploke/indices/ A0→索引管理が必要→base が担う
"""
Symplokē Domain Index - Abstract Base Class

Hegemonikón H3: 4知識源 (Gnōsis, Chronos, Sophia, Kairos) の共通インターフェース
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from ..adapters.base import VectorStoreAdapter, SearchResult


class SourceType(Enum):
    """知識ソース種別"""

    GNOSIS = "gnosis"  # 論文 (外部知識)
    CHRONOS = "chronos"  # チャット履歴 (時系列)
    SOPHIA = "sophia"  # Knowledge Items (静的知識)
    KAIROS = "kairos"  # Handoff (文脈)


@dataclass
class Document:
    """インデックス用ドキュメント"""

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class IndexedResult:
    """ドメイン固有検索結果"""

    doc_id: str
    score: float
    source: SourceType
    content: str
    metadata: Dict[str, Any]


class DomainIndex(ABC):
    """
    ドメイン固有インデックスの抽象基底クラス

    各知識源 (Gnōsis, Chronos, Sophia, Kairos) は
    このクラスを継承して、ドメイン固有のロジックを実装する。

    Usage:
        class GnosisIndex(DomainIndex):
            @property
            def source_type(self) -> SourceType:
                return SourceType.GNOSIS

            def ingest(self, documents: List[Document]) -> int:
                # 論文データのインジェスト
                ...
    """

    def __init__(self, adapter: "VectorStoreAdapter", name: str, dimension: int = 768):
        """
        Args:
            adapter: ベクトルストアアダプタ
            name: インデックス名
            dimension: ベクトル次元数 (default: text-embedding-3-small)
        """
        self._adapter = adapter
        self._name = name
        self._dimension = dimension
        self._initialized = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def adapter(self) -> "VectorStoreAdapter":
        return self._adapter

    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """ソース種別 (gnosis/chronos/sophia/kairos)"""
        pass

    def initialize(self) -> None:
        """インデックスを初期化"""
        if not self._initialized:
            self._adapter.create_index(dimension=self._dimension, index_name=self._name)
            self._initialized = True

    @abstractmethod
    def ingest(self, documents: List[Document]) -> int:
        """
        ドキュメントをベクトル化して追加

        Args:
            documents: インデックス対象ドキュメント

        Returns:
            追加されたドキュメント数
        """
        pass

    @abstractmethod
    def search(self, query: str, k: int = 10, **kwargs) -> List[IndexedResult]:
        """
        テキストクエリで検索

        Args:
            query: 検索クエリ
            k: 取得件数
            **kwargs: ドメイン固有パラメータ

        Returns:
            IndexedResult のリスト
        """
        pass

    def count(self) -> int:
        """現在のドキュメント数"""
        return self._adapter.count()

    def save(self, path: str) -> None:
        """インデックスを永続化"""
        self._adapter.save(path)

    def load(self, path: str) -> None:
        """インデックスを読み込み"""
        self._adapter.load(path)
        self._initialized = True
