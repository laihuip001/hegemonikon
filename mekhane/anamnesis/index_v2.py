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

# Japanese morphological pre-tokenization (optional)
try:
    from janome.tokenizer import Tokenizer as JanomeTokenizer
    _janome = JanomeTokenizer()
    _JANOME_AVAILABLE = True
except ImportError:
    _janome = None
    _JANOME_AVAILABLE = False

# Content word POS tags for Japanese (same as cone_builder)
_JA_CONTENT_POS = {'名詞', '動詞', '形容詞', '副詞'}
_JA_EXCLUDE_DETAILS = {'非自立', '接尾', '数'}

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

    # PURPOSE: Embedder の構成と依存関係の初期化
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

    # PURPOSE: 日本語テキストを形態素分解してスペース区切りにする。
    @staticmethod
    def preprocess_ja(text: str) -> str:
        """日本語テキストを形態素分解してスペース区切りにする。

        BGE-small の WordPiece トークナイザは空白で初期分割するため、
        janome で事前に意味単位で分割しておくことで、
        サブワード境界が意味的に正しくなる。

        英数字やASCII部分はそのまま通す (混在テキスト対応)。
        """
        if not _JANOME_AVAILABLE or not text:
            return text

        # 日本語文字を含まない場合はスキップ
        import re
        if not re.search(r'[\u3000-\u9fff\uf900-\ufaff]', text):
            return text

        try:
            tokens = []
            for token in _janome.tokenize(text):
                pos = token.part_of_speech.split(',')[0]
                detail = token.part_of_speech.split(',')[1] if ',' in token.part_of_speech else ''
                if pos in _JA_CONTENT_POS and detail not in _JA_EXCLUDE_DETAILS:
                    # 内容語: 基本形があれば使う
                    base = token.base_form if token.base_form != '*' else token.surface
                    tokens.append(base)
                else:
                    # 機能語: 原形を保持
                    tokens.append(token.surface)
            # Merge consecutive ASCII tokens (e.g., 'E','2','E' → 'E2E')
            merged = []
            for t in tokens:
                if t.isascii() and t.strip() and merged and merged[-1].isascii() and merged[-1].strip():
                    merged[-1] += t
                else:
                    merged.append(t)
            return ' '.join(merged)
        except Exception:
            return text  # fallback: 原文をそのまま返す

    # PURPOSE: バッチ埋め込み
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """バッチ埋め込み (日本語前処理つき)"""
        # Japanese pre-tokenization
        processed = [self.preprocess_ja(t) for t in texts]
        encoded_batch = self.tokenizer.encode_batch(processed)

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


# PURPOSE: GnosisIndexV2 の機能を提供する
class GnosisIndexV2:
    """
    Gnōsis論文インデックス V2

    VectorStoreAdapterを使用した汎用設計。
    既存GnosisIndexとの互換APIを提供。
    """

    # PURPOSE: GnosisIndexV2 の構成と依存関係の初期化
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

    # PURPOSE: index_v2 の embedder 処理を実行する
    @property
    # PURPOSE: embedder — 知識基盤の処理
    def embedder(self) -> Embedder:
        if self._embedder is None:
            self._embedder = Embedder()
        return self._embedder

    # PURPOSE: 永続化された状態の復元
    def _load(self) -> None:
        try:
            self.store.load(str(self.index_path))
            print(
                f"[GnosisIndexV2] Loaded {self.store.count()} vectors from {self.index_path}"
            )
        except Exception as e:
            print(f"[GnosisIndexV2] Failed to load index: {e}")
            self.store.create_index(dimension=self._dimension)

    # PURPOSE: 状態のディスク永続化
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

    # PURPOSE: 論文データのインデックスへの追加
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

    # PURPOSE: セマンティック検索の実行
    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if self.store.count() == 0:
            print("[GnosisIndexV2] No papers indexed yet")
            return []

        query_vector = self.embedder.embed(query)
        results = self.store.search(query_vector, k=k)

        return [{"id": r.id, "score": r.score, **r.metadata} for r in results]

    # PURPOSE: インデックスの統計情報を集計
    def stats(self) -> Dict[str, Any]:
        return {
            "total": self.store.count(),
            "adapter": self.adapter_name,
            "index_path": str(self.index_path),
        }

    # PURPOSE: インデックス統計の取得（ヘルスチェック用）
    def get_stats(self) -> Dict[str, Any]:
        stats = self.stats()
        return {
            "total_papers": stats["total"],
            "sources": [],
            "last_updated": "N/A",
        }
