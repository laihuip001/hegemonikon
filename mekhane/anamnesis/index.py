# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → 論文のセマンティック索引が必要
   → index.py が担う

Q.E.D.

---

Gnōsis Index - LanceDB統合 + 重複排除
"""

import sys
from pathlib import Path
from typing import Optional

try:
    import lancedb
except ImportError:
    lancedb = None

from mekhane.anamnesis.models.paper import Paper, merge_papers

# Paths
GNOSIS_DIR = Path(__file__).parent.parent.parent / "gnosis_data"
LANCE_DIR = GNOSIS_DIR / "lancedb"
MODELS_DIR = (
    Path(__file__).parent.parent / "models" / "bge-small"
)  # forge/models/bge-small

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass  # TODO: Add proper error handling


# PURPOSE: Text embedding with automatic GPU acceleration.
class Embedder:
    """Text embedding with automatic GPU acceleration.

    Strategy:
      1. CUDA available → sentence-transformers on GPU (fp16, ~1175MB VRAM for bge-m3)
      2. CUDA OOM → sentence-transformers on CPU (same model)
      3. Fallback → ONNX Runtime on CPU (bge-small, legacy)
    """

    # PURPOSE: Embedder の構成と依存関係の初期化
    def __init__(self, force_cpu: bool = False, model_name: str = "BAAI/bge-m3"):
        import numpy as np
        self.np = np
        self._use_gpu = False
        self._st_model = None
        self._ort_session = None
        self._tokenizer = None
        self.model_name = model_name

        # GPU detection with fp16
        if not force_cpu:
            try:
                import torch
                if torch.cuda.is_available():
                    from sentence_transformers import SentenceTransformer
                    try:
                        self._st_model = SentenceTransformer(
                            model_name, device='cuda',
                            model_kwargs={'torch_dtype': torch.float16},
                        )
                        self._use_gpu = True
                        vram_mb = torch.cuda.memory_allocated() / 1e6
                        print(f"[Embedder] GPU mode (CUDA fp16, {vram_mb:.0f}MB VRAM)")
                        return
                    except RuntimeError as e:
                        # CUDA OOM — fall through to CPU
                        if "out of memory" in str(e).lower():
                            print(f"[Embedder] CUDA OOM, falling back to CPU")
                            torch.cuda.empty_cache()
                        else:
                            raise
            except ImportError:
                pass  # torch or sentence-transformers not installed

        # CPU with sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(model_name, device='cpu')
            self._use_gpu = False
            print(f"[Embedder] CPU mode (sentence-transformers: {model_name})")
            return
        except ImportError:
            pass

        # ONNX fallback (original implementation)
        self._init_onnx()
        print("[Embedder] CPU mode (ONNX)")

    # PURPOSE: Initialize ONNX Runtime session (original implementation).
    def _init_onnx(self):
        """Initialize ONNX Runtime session (original implementation)."""
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_path = MODELS_DIR / "model.onnx"
        tokenizer_path = MODELS_DIR / "tokenizer.json"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n" "Run: python aidb-kb.py setup"
            )

        self._ort_session = ort.InferenceSession(str(model_path))
        self._tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self._tokenizer.enable_truncation(max_length=512)
        self._tokenizer.enable_padding(pad_to_multiple_of=8)

    # PURPOSE: テキストをベクトル空間に射影
    def embed(self, text: str) -> list:
        return self.embed_batch([text])[0]

    # PURPOSE: GPU embedding via sentence-transformers.
    def embed_batch(self, texts: list[str]) -> list[list]:
        if self._st_model is not None:
            return self._embed_st(texts)
        return self._embed_onnx(texts)

    # PURPOSE: Embedding via sentence-transformers (GPU or CPU).
    def _embed_st(self, texts: list[str]) -> list[list]:
        """Embedding via sentence-transformers (GPU or CPU)."""
        embeddings = self._st_model.encode(
            texts, batch_size=32, normalize_embeddings=True
        )
        return embeddings.tolist()

    # PURPOSE: CPU embedding via ONNX Runtime (original implementation).
    def _embed_onnx(self, texts: list[str]) -> list[list]:
        """CPU embedding via ONNX Runtime (original implementation)."""
        encoded_batch = self._tokenizer.encode_batch(texts)

        input_ids_list = [e.ids for e in encoded_batch]
        attention_mask_list = [e.attention_mask for e in encoded_batch]

        input_ids = self.np.array(input_ids_list, dtype=self.np.int64)
        attention_mask = self.np.array(attention_mask_list, dtype=self.np.int64)
        token_type_ids = self.np.zeros_like(input_ids)

        outputs = self._ort_session.run(
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
        sum_mask[sum_mask == 0] = 1e-9  # Avoid division by zero
        pooled = sum_embeddings / sum_mask

        # Normalize
        norm = self.np.linalg.norm(pooled, axis=1, keepdims=True)
# PURPOSE: Gnōsis論文インデックス
        norm[norm == 0] = 1e-12  # Avoid division by zero
        normalized = pooled / norm

        return normalized.tolist()


# PURPOSE: Gnōsis論文インデックス
class GnosisIndex:
    """Gnōsis論文インデックス"""

    TABLE_NAME = "papers"

    # PURPOSE: GnosisIndex の構成と依存関係の初期化
    def __init__(self, lance_dir: Optional[Path] = None):
        if lancedb is None:
            raise ImportError("lancedb package required: pip install lancedb")

        self.lance_dir = lance_dir or LANCE_DIR
        self.lance_dir.mkdir(parents=True, exist_ok=True)

        self.db = lancedb.connect(str(self.lance_dir))
        self.embedder: Optional[Embedder] = None
        self._primary_key_cache: set[str] = set()

    # PURPOSE: 既存primary_keyとtitleをキャッシュ
    def _get_embedder(self) -> Embedder:
        if self.embedder is None:
            self.embedder = Embedder()
        return self.embedder

    # PURPOSE: 既存primary_keyとtitleをキャッシュ
    def _load_primary_keys(self):
        """既存primary_keyとtitleをキャッシュ"""
        if self.TABLE_NAME not in self.db.table_names():
            return

        table = self.db.open_table(self.TABLE_NAME)
        try:
            df = table.search().select(["primary_key", "title"]).limit(None).to_pandas()
            self._primary_key_cache = set(df["primary_key"].tolist())
            # Title cache: normalized_title -> primary_key
            self._title_cache: dict[str, str] = {}
            for _, row in df.iterrows():
                norm = self._normalize_title(row.get("title", ""))
                if norm:
                    self._title_cache[norm] = row["primary_key"]
        except Exception:
            pass

    @staticmethod
    def _normalize_title(title: str) -> str:
        """タイトルの正規化: 小文字化 + 非英数字除去でファジーマッチ。"""
        import re
        return re.sub(r'[^a-z0-9]', '', title.lower().strip())

    # PURPOSE: 論文をインデックスに追加
    def add_papers(self, papers: list[Paper], dedupe: bool = True) -> int:
        """
        論文をインデックスに追加

        Args:
            papers: 追加する論文リスト
            dedupe: 重複排除を行うか

        Returns:
            追加された論文数
        """
        if not papers:
            return 0

        embedder = self._get_embedder()

        # 重複排除: primary_key + title fuzzy match
        if dedupe:
            self._load_primary_keys()
            title_cache = getattr(self, '_title_cache', {})
            new_papers = []
            for p in papers:
                # Check 1: primary_key exact match
                if p.primary_key in self._primary_key_cache:
                    continue
                # Check 2: normalized title match (cross-source dedup)
                norm_title = self._normalize_title(p.title)
                if norm_title and norm_title in title_cache:
                    # Same paper from different source — skip
                    continue
                new_papers.append(p)
                self._primary_key_cache.add(p.primary_key)
                if norm_title:
                    title_cache[norm_title] = p.primary_key
            papers = new_papers

        if not papers:
            print("[GnosisIndex] No new papers to add (all duplicates)")
            return 0

        # 埋め込み生成
        data = []
        BATCH_SIZE = 32

        for i in range(0, len(papers), BATCH_SIZE):
            batch_papers = papers[i : i + BATCH_SIZE]
            texts = [p.embedding_text for p in batch_papers]
            vectors = embedder.embed_batch(texts)

            for paper, vector in zip(batch_papers, vectors):
                record = paper.to_dict()
                record["vector"] = vector
                data.append(record)

            print(f"  Processed {min(i + BATCH_SIZE, len(papers))}/{len(papers)}...")

        # LanceDBに追加
        if self.TABLE_NAME in self.db.table_names():
            table = self.db.open_table(self.TABLE_NAME)
            table.add(data)
        else:
            self.db.create_table(self.TABLE_NAME, data=data)

        print(f"[GnosisIndex] Added {len(data)} papers")
        return len(data)

    # PURPOSE: セマンティック検索
    def search(self, query: str, k: int = 10) -> list[dict]:
        """
        セマンティック検索

        Args:
            query: 検索クエリ
            k: 取得件数

        Returns:
            検索結果のリスト
        """
        if self.TABLE_NAME not in self.db.table_names():
            print("[GnosisIndex] No papers indexed yet")
            return []

        embedder = self._get_embedder()
        query_vector = embedder.embed(query)

        table = self.db.open_table(self.TABLE_NAME)
        results = table.search(query_vector).limit(k).to_list()

        return results

    # PURPOSE: インデックス統計
    def stats(self) -> dict:
        """インデックス統計"""
        if self.TABLE_NAME not in self.db.table_names():
            return {"total": 0, "sources": {}}

        table = self.db.open_table(self.TABLE_NAME)
        df = table.to_pandas()

        sources = df["source"].value_counts().to_dict()

        return {
            "total": len(df),
            "sources": sources,
            "unique_dois": df["doi"].notna().sum(),
            "unique_arxiv": df["arxiv_id"].notna().sum(),
        }

    # PURPOSE: primary_keyで論文取得
    def get_by_primary_key(self, primary_key: str) -> Optional[dict]:
        """primary_keyで論文取得"""
        if self.TABLE_NAME not in self.db.table_names():
            return None

        table = self.db.open_table(self.TABLE_NAME)

        try:
            results = (
                table.search()
                .where(f"primary_key = '{primary_key}'")
                .limit(1)
                .to_list()
            )
            return results[0] if results else None
        except Exception:
            return None
