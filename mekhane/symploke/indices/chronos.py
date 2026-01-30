# PROOF: [L2/インフラ] A0→索引管理が必要→chronos が担う
"""
Chronos Index - チャット履歴 (時系列)

Hegemonikón H3: セッション間のチャット履歴ベクトル検索
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from .base import DomainIndex, SourceType, Document, IndexedResult
from ..adapters.base import VectorStoreAdapter


class ChronosIndex(DomainIndex):
    """
    Chronos: チャット履歴のインデックス
    
    Features:
        - 時系列順序の保持
        - 時間減衰関数によるスコア調整
        - セッションID・ターンIDでのフィルタリング
    
    Usage:
        adapter = HNSWlibAdapter()
        chronos = ChronosIndex(adapter, "chronos")
        chronos.initialize()
        chronos.ingest([Document(id="msg1", content="...", metadata={"timestamp": ...})])
        results = chronos.search("previous discussion", k=10)
    """
    
    def __init__(
        self, 
        adapter: VectorStoreAdapter,
        name: str = "chronos",
        dimension: int = 768,
        embed_fn: Optional[callable] = None,
        decay_rate: float = 0.1  # 時間減衰率
    ):
        """
        Args:
            adapter: ベクトルストアアダプタ
            name: インデックス名
            dimension: ベクトル次元数
            embed_fn: テキスト→ベクトル変換関数 (None = stub mode)
            decay_rate: 時間減衰率 (高いほど新しいメッセージを優先)
        """
        super().__init__(adapter, name, dimension)
        self._embed_fn = embed_fn
        self._decay_rate = decay_rate
        self._doc_store: Dict[str, Document] = {}
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.CHRONOS
    
    def _embed(self, text: str) -> np.ndarray:
        """テキストをベクトル化"""
        if self._embed_fn is not None:
            return self._embed_fn(text)
        else:
            # Stub mode
            return np.random.randn(self._dimension).astype(np.float32)
    
    def _apply_time_decay(self, score: float, timestamp: Optional[datetime]) -> float:
        """時間減衰を適用"""
        if timestamp is None:
            return score
        
        now = datetime.now()
        age_hours = (now - timestamp).total_seconds() / 3600
        decay = np.exp(-self._decay_rate * age_hours / 24)  # 日単位で減衰
        return score * decay
    
    def ingest(self, documents: List[Document]) -> int:
        """
        チャット履歴をインジェスト
        
        Args:
            documents: Document のリスト
                       metadata に 'timestamp', 'session_id', 'turn_id' を含めることを推奨
        
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
        session_id: Optional[str] = None,
        apply_decay: bool = True,
        **kwargs
    ) -> List[IndexedResult]:
        """
        チャット履歴を検索
        
        Args:
            query: 検索クエリ
            k: 取得件数
            session_id: 特定セッションに限定 (None = 全セッション)
            apply_decay: 時間減衰を適用するか
        
        Returns:
            IndexedResult のリスト
        """
        if not self._initialized:
            return []
        
        query_vec = self._embed(query)
        adapter_results = self._adapter.search(query_vec, k=k * 2)  # 多めに取得
        
        results = []
        for r in adapter_results:
            # セッションフィルタ
            if session_id and r.metadata.get("session_id") != session_id:
                continue
            
            doc_id = r.metadata.get("doc_id", str(r.id))
            doc = self._doc_store.get(doc_id)
            
            # 時間減衰
            score = r.score
            if apply_decay and "timestamp" in r.metadata:
                ts = r.metadata["timestamp"]
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)
                score = self._apply_time_decay(score, ts)
            
            results.append(IndexedResult(
                doc_id=doc_id,
                score=score,
                source=self.source_type,
                content=doc.content if doc else "",
                metadata=r.metadata
            ))
        
        # スコア降順で再ソート
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:k]
