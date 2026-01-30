# PROOF: [L2/インフラ] A0→索引管理が必要→sophia が担う
"""
Sophia Index - Knowledge Items (静的知識)

Hegemonikón H3: 蒸留された知識アイテムのベクトル検索
"""

from typing import List, Dict, Any, Optional
import numpy as np

from .base import DomainIndex, SourceType, Document, IndexedResult
from ..adapters.base import VectorStoreAdapter


class SophiaIndex(DomainIndex):
    """
    Sophia: Knowledge Items のインデックス
    
    Features:
        - 静的・蒸留された知識の検索
        - カテゴリ・タグによるフィルタリング
        - 知識の階層構造対応
    
    Usage:
        adapter = HNSWlibAdapter()
        sophia = SophiaIndex(adapter, "sophia")
        sophia.initialize()
        sophia.ingest([Document(id="ki1", content="...", metadata={"category": "architecture"})])
        results = sophia.search("adapter pattern", k=10)
    """
    
    def __init__(
        self, 
        adapter: VectorStoreAdapter,
        name: str = "sophia",
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
        return SourceType.SOPHIA
    
    def _embed(self, text: str) -> np.ndarray:
        """テキストをベクトル化"""
        if self._embed_fn is not None:
            return self._embed_fn(text)
        else:
            # Stub mode
            return np.random.randn(self._dimension).astype(np.float32)
    
    def ingest(self, documents: List[Document]) -> int:
        """
        Knowledge Items をインジェスト
        
        Args:
            documents: Document のリスト
                       metadata に 'category', 'tags', 'hierarchy' を含めることを推奨
        
        Returns:
            追加されたドキュメント数
        """
        if not self._initialized:
            self.initialize()
        
        vectors = []
        metadata_list = []
        
        for doc in documents:
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
            
            self._doc_store[doc.id] = doc
        
        if vectors:
            vectors_array = np.stack(vectors)
            self._adapter.add_vectors(vectors_array, metadata=metadata_list)
        
        return len(documents)
    
    def search(
        self, 
        query: str, 
        k: int = 10,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> List[IndexedResult]:
        """
        Knowledge Items を検索
        
        Args:
            query: 検索クエリ
            k: 取得件数
            category: カテゴリフィルタ (None = 全カテゴリ)
            tags: タグフィルタ (AND条件)
        
        Returns:
            IndexedResult のリスト
        """
        if not self._initialized:
            return []
        
        query_vec = self._embed(query)
        adapter_results = self._adapter.search(query_vec, k=k * 2)
        
        results = []
        for r in adapter_results:
            # カテゴリフィルタ
            if category and r.metadata.get("category") != category:
                continue
            
            # タグフィルタ (AND)
            if tags:
                doc_tags = set(r.metadata.get("tags", []))
                if not all(t in doc_tags for t in tags):
                    continue
            
            doc_id = r.metadata.get("doc_id", str(r.id))
            doc = self._doc_store.get(doc_id)
            
            results.append(IndexedResult(
                doc_id=doc_id,
                score=r.score,
                source=self.source_type,
                content=doc.content if doc else "",
                metadata=r.metadata
            ))
        
        return results[:k]
