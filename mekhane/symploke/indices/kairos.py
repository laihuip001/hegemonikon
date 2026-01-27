"""
Kairos Index - Handoff (文脈)

Hegemonikón H3: セッション間引き継ぎ (Handoff) のベクトル検索
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from .base import DomainIndex, SourceType, Document, IndexedResult
from ..adapters.base import VectorStoreAdapter


class KairosIndex(DomainIndex):
    """
    Kairos: Handoff (セッション間文脈) のインデックス
    
    Features:
        - セッション終了時の引き継ぎ情報検索
        - 未完了タスク・待機中タスクの追跡
        - 文脈の継続性確保
    
    Usage:
        adapter = HNSWlibAdapter()
        kairos = KairosIndex(adapter, "kairos")
        kairos.initialize()
        kairos.ingest([Document(id="handoff_20260127", content="...", metadata={"status": "pending"})])
        results = kairos.search("previous session context", k=5)
    """
    
    def __init__(
        self, 
        adapter: VectorStoreAdapter,
        name: str = "kairos",
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
        return SourceType.KAIROS
    
    def _embed(self, text: str) -> np.ndarray:
        """テキストをベクトル化"""
        if self._embed_fn is not None:
            return self._embed_fn(text)
        else:
            # Stub mode
            return np.random.randn(self._dimension).astype(np.float32)
    
    def ingest(self, documents: List[Document]) -> int:
        """
        Handoff をインジェスト
        
        Args:
            documents: Document のリスト
                       metadata に 'session_date', 'status', 'priority_tasks' を含めることを推奨
        
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
        status: Optional[str] = None,
        recent_days: Optional[int] = None,
        **kwargs
    ) -> List[IndexedResult]:
        """
        Handoff を検索
        
        Args:
            query: 検索クエリ
            k: 取得件数
            status: ステータスフィルタ ('pending', 'completed', 'blocked')
            recent_days: 直近N日以内に限定
        
        Returns:
            IndexedResult のリスト
        """
        if not self._initialized:
            return []
        
        query_vec = self._embed(query)
        adapter_results = self._adapter.search(query_vec, k=k * 2)
        
        now = datetime.now()
        results = []
        
        for r in adapter_results:
            # ステータスフィルタ
            if status and r.metadata.get("status") != status:
                continue
            
            # 日数フィルタ
            if recent_days and "session_date" in r.metadata:
                session_date = r.metadata["session_date"]
                if isinstance(session_date, str):
                    session_date = datetime.fromisoformat(session_date.split("T")[0])
                age_days = (now - session_date).days
                if age_days > recent_days:
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
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        未完了タスクを取得
        
        Handoff の metadata から status='pending' のものを抽出
        """
        pending = []
        for doc_id, doc in self._doc_store.items():
            if doc.metadata.get("status") == "pending":
                pending.append({
                    "doc_id": doc_id,
                    "content": doc.content[:200],  # 先頭200文字
                    "metadata": doc.metadata
                })
        return pending
