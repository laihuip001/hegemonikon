# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ]

P3 → 記憶の索引が必要
   → VectorStore アダプタ統合版
   → GnosisIndexV2 が担う

Q.E.D.

---

Gnōsis Index V2 - VectorStore Adapter統合

lancedb依存からhnswlib/faiss/sqlite-vss切り替え可能な設計に移行。
既存GnosisIndexとの互換性を維持しつつ、symplokeアダプタを使用。
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np

from mekhane.symploke.factory import VectorStoreFactory
from mekhane.symploke.adapters.base import VectorStoreAdapter
from mekhane.symploke.config import VectorStoreConfig

# Embedder (既存index.pyから移行)
try:
    import onnxruntime as ort
    from tokenizers import Tokenizer

    EMBEDDER_AVAILABLE = True
except ImportError:
    EMBEDDER_AVAILABLE = False

# Paths
GNOSIS_DIR = Path(__file__).parent.parent.parent / "gnosis_data"
INDEX_DIR = Path(__file__).parent.parent.parent.parent / "mneme" / "indices"
MODELS_DIR = Path(__file__).parent.parent / "models" / "bge-small"

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass  # TODO: Add proper error handling


# PURPOSE: ONNX-based text embedding (BGE-small)
class Embedder:
    """ONNX-based text embedding (BGE-small)"""

    # PURPOSE: 内部処理: init__
    def __init__(self, model_dir: Optional[Path] = None):
        if not EMBEDDER_AVAILABLE:
            raise ImportError(
                "Embedder dependencies required: pip install onnxruntime tokenizers"
            )

        model_dir = model_dir or MODELS_DIR
        model_path = model_dir / "model.onnx"
        tokenizer_path = model_dir / "tokenizer.json"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n" "Run: python aidb-kb.py setup"
            )

        self.session = ort.InferenceSession(str(model_path))
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(pad_to_multiple_of=8)
        self.dimension = 384  # BGE-small

    # PURPOSE: 単一テキストを埋め込み
    def embed(self, text: str) -> np.ndarray:
        """単一テキストを埋め込み"""
        return self.embed_batch([text])[0]

    # PURPOSE: バッチ埋め込み
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """バッチ埋め込み"""
        encoded_batch = self.tokenizer.encode_batch(texts)

        input_ids_list = [e.ids for e in encoded_batch]
        attention_mask_list = [e.attention_mask for e in encoded_batch]

        input_ids = np.array(input_ids_list, dtype=np.int64)
        attention_mask = np.array(attention_mask_list, dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids)

        outputs = self.session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        embeddings = outputs[0]
        mask = attention_mask[:, :, None]

        # Mean pooling
        sum_embeddings = (embeddings * mask).sum(axis=1)
        sum_mask = mask.sum(axis=1)
        sum_mask[sum_mask == 0] = 1e-9
        pooled = sum_embeddings / sum_mask

        # Normalize
        norm = np.linalg.norm(pooled, axis=1, keepdims=True)
        norm[norm == 0] = 1e-12
        normalized = pooled / norm

# PURPOSE: Gnōsis論文インデックス V2
        return normalized.astype(np.float32)


class GnosisIndexV2:
    """
    Gnōsis論文インデックス V2

    VectorStoreAdapterを使用した汎用設計。
    既存GnosisIndexとの互換APIを提供。
    """

    # PURPOSE: 内部処理: init__
    def __init__(
        self,
        adapter: str = "hnswlib",
        index_dir: Optional[Path] = None,
        config: Optional[VectorStoreConfig] = None,
    ):
        self.index_dir = index_dir or INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_path = self.index_dir / f"gnosis.{adapter}"
        self.adapter_name = adapter

        # アダプタ生成
        self.store: VectorStoreAdapter = VectorStoreFactory.create(
            adapter, config=config
        )

        # Embedder (遅延初期化)
        self._embedder: Optional[Embedder] = None
        self._dimension = 384  # BGE-small default

        # 既存インデックスがあれば読み込み
        if self.index_path.exists():
            self._load()
        else:
            self.store.create_index(dimension=self._dimension)

        # 重複排除用キャッシュ
        self._primary_key_cache: set = set()
        self._title_cache: dict[str, str] = {}

    @property
    # PURPOSE: 関数: embedder
    def embedder(self) -> Embedder:
        if self._embedder is None:
            self._embedder = Embedder()
        return self._embedder

    # PURPOSE: 内部処理: load
    def _load(self) -> None:
        try:
            self.store.load(str(self.index_path))
            print(
                f"[GnosisIndexV2] Loaded {self.store.count()} vectors from {self.index_path}"
            )
        except Exception as e:
            print(f"[GnosisIndexV2] Failed to load index: {e}")
            self.store.create_index(dimension=self._dimension)

    # PURPOSE: 内部処理: save
    def _save(self) -> None:
        self.store.save(str(self.index_path))
        print(
            f"[GnosisIndexV2] Saved {self.store.count()} vectors to {self.index_path}"
        )

    @staticmethod
    def _normalize_title(title: str) -> str:
        """タイトルの正規化: 小文字化 + 非英数字除去でファジーマッチ。"""
        import re
        return re.sub(r'[^a-z0-9]', '', title.lower().strip())

    # PURPOSE: 関数: add_papers
    def add_papers(self, papers: list, dedupe: bool = True) -> int:
        if not papers:
            return 0


        if dedupe:
            new_papers = []
            for p in papers:
                pk = getattr(p, "primary_key", None) or str(id(p))
                if pk in self._primary_key_cache:
                    continue
                # Title-based fuzzy dedup (cross-source)
                title = getattr(p, "title", "")
                norm_title = self._normalize_title(title)
                if norm_title and norm_title in self._title_cache:
                    continue
                new_papers.append(p)
                self._primary_key_cache.add(pk)
                if norm_title:
                    self._title_cache[norm_title] = pk
            papers = new_papers

        if not papers:
            print("[GnosisIndexV2] No new papers to add (all duplicates)")
            return 0

        BATCH_SIZE = 32
        all_vectors = []
        all_metadata = []

        for i in range(0, len(papers), BATCH_SIZE):
            batch = papers[i : i + BATCH_SIZE]
            texts = [getattr(p, "embedding_text", str(p)) for p in batch]
            vectors = self.embedder.embed_batch(texts)

            for paper, vector in zip(batch, vectors):
                all_vectors.append(vector)
                all_metadata.append(
                    getattr(paper, "to_dict", lambda: {"text": str(paper)})()
                )

            print(f"  Processed {min(i + BATCH_SIZE, len(papers))}/{len(papers)}...")

        vectors_array = np.array(all_vectors, dtype=np.float32)
        ids = self.store.add_vectors(vectors_array, metadata=all_metadata)

        self._save()

        print(f"[GnosisIndexV2] Added {len(ids)} papers")
        return len(ids)

    # PURPOSE: 関数: search
    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if self.store.count() == 0:
            print("[GnosisIndexV2] No papers indexed yet")
            return []

        query_vector = self.embedder.embed(query)
        results = self.store.search(query_vector, k=k)

        return [{"id": r.id, "score": r.score, **r.metadata} for r in results]

    # PURPOSE: 関数: stats
    def stats(self) -> Dict[str, Any]:
        return {
            "total": self.store.count(),
            "adapter": self.adapter_name,
            "index_path": str(self.index_path),
        }

    # PURPOSE: 取得: get_stats
    def get_stats(self) -> Dict[str, Any]:
        stats = self.stats()
        return {
            "total_papers": stats["total"],
            "sources": [],
            "last_updated": "N/A",
        }
