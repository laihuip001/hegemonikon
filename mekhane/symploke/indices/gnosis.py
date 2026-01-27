"""
Gnōsis Index - 論文データ (外部知識)

Hegemonikón H3: 外部論文・研究データのベクトル検索
"""

from typing import List, Dict, Any, Optional
import numpy as np

from .base import DomainIndex, SourceType, Document, IndexedResult
from ..adapters.base import VectorStoreAdapter


class GnosisIndex(DomainIndex):
    """
    Gnōsis: 論文・外部知識のインデックス
    
    Features:
        - arXiv / Semantic Scholar からの論文インジェスト
        - 抽象・タイトル・キーワードのベクトル化
        - 類似論文検索
    
    Usage:
        adapter = HNSWlibAdapter()
        gnosis = GnosisIndex(adapter, "gnosis")
        gnosis.initialize()
        gnosis.ingest([Document(id="paper1", content="...")])
        results = gnosis.search("active inference", k=10)
    """
    
    def __init__(
        self, 
        adapter: VectorStoreAdapter,
        name: str = "gnosis",
        dimension: int = 768,
        embed_fn: Optional[callable] = None
    ):
        """
        Args:
            adapter: ベクトルストアアダプタ
            name: インデックス名
            dimension: ベクトル次元数
            embed_fn: テキスト→ベクトル変換関数 (None = stub mode)
        """
        super().__init__(adapter, name, dimension)
        self._embed_fn = embed_fn
        self._doc_store: Dict[str, Document] = {}
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.GNOSIS
    
    def _embed(self, text: str) -> np.ndarray:
        """テキストをベクトル化"""
        if self._embed_fn is not None:
            return self._embed_fn(text)
        else:
            # Stub mode: ランダムベクトルを返す
            return np.random.randn(self._dimension).astype(np.float32)
    
    def ingest(self, documents: List[Document]) -> int:
        """
        論文ドキュメントをインジェスト
        
        Args:
            documents: Document のリスト
        
        Returns:
            追加されたドキュメント数
        """
        if not self._initialized:
            self.initialize()
        
        vectors = []
        metadata_list = []
        
        for doc in documents:
            # ベクトル化
            if doc.embedding is not None:
                vec = np.array(doc.embedding, dtype=np.float32)
            else:
                vec = self._embed(doc.content)
            
            vectors.append(vec)
            metadata_list.append({
                "doc_id": doc.id,
                "source": self.source_type.value,
                **doc.metadata
            })
            
            # ドキュメント保存
            self._doc_store[doc.id] = doc
        
        if vectors:
            vectors_array = np.stack(vectors)
            self._adapter.add_vectors(vectors_array, metadata=metadata_list)
        
        return len(documents)
    
    def search(
        self, 
        query: str, 
        k: int = 10,
        **kwargs
    ) -> List[IndexedResult]:
        """
        論文を検索
        
        Args:
            query: 検索クエリ
            k: 取得件数
        
        Returns:
            IndexedResult のリスト
        """
        if not self._initialized:
            return []
        
        query_vec = self._embed(query)
        adapter_results = self._adapter.search(query_vec, k=k)
        
        results = []
        for r in adapter_results:
            doc_id = r.metadata.get("doc_id", str(r.id))
            doc = self._doc_store.get(doc_id)
            
            results.append(IndexedResult(
                doc_id=doc_id,
                score=r.score,
                source=self.source_type,
                content=doc.content if doc else "",
                metadata=r.metadata
            ))
        
        return results
