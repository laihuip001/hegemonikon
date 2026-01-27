"""
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
MODELS_DIR = Path(__file__).parent.parent / "models" / "bge-small"  # forge/models/bge-small

# Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class Embedder:
    """ONNX-based text embedding (BGE-small)"""
    
    def __init__(self):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        import numpy as np
        
        self.np = np
        
        model_path = MODELS_DIR / "model.onnx"
        tokenizer_path = MODELS_DIR / "tokenizer.json"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                "Run: python aidb-kb.py setup"
            )
        
        self.session = ort.InferenceSession(str(model_path))
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(pad_to_multiple_of=8)
    
    def embed(self, text: str) -> list:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list]:
        encoded_batch = self.tokenizer.encode_batch(texts)

        input_ids_list = [e.ids for e in encoded_batch]
        attention_mask_list = [e.attention_mask for e in encoded_batch]

        input_ids = self.np.array(input_ids_list, dtype=self.np.int64)
        attention_mask = self.np.array(attention_mask_list, dtype=self.np.int64)
        token_type_ids = self.np.zeros_like(input_ids)
        
        outputs = self.session.run(None, {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        })
        
        embeddings = outputs[0]
        mask = attention_mask[:, :, None]

        # Mean pooling
        sum_embeddings = (embeddings * mask).sum(axis=1)
        sum_mask = mask.sum(axis=1)
        sum_mask[sum_mask == 0] = 1e-9  # Avoid division by zero
        pooled = sum_embeddings / sum_mask

        # Normalize
        norm = self.np.linalg.norm(pooled, axis=1, keepdims=True)
        norm[norm == 0] = 1e-12  # Avoid division by zero
        normalized = pooled / norm
        
        return normalized.tolist()


class GnosisIndex:
    """Gnōsis論文インデックス"""
    
    TABLE_NAME = "papers"
    
    def __init__(self, lance_dir: Optional[Path] = None):
        if lancedb is None:
            raise ImportError("lancedb package required: pip install lancedb")
        
        self.lance_dir = lance_dir or LANCE_DIR
        self.lance_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = lancedb.connect(str(self.lance_dir))
        self.embedder: Optional[Embedder] = None
    
    def _get_embedder(self) -> Embedder:
        if self.embedder is None:
            self.embedder = Embedder()
        return self.embedder
    
    def _filter_new_papers(self, papers: list[Paper]) -> list[Paper]:
        """
        データベースに存在しない論文のみを抽出
        """
        if not papers:
            return []

        # 1. 入力バッチ内の重複排除 (最初のものを残す)
        unique_papers = []
        seen_keys = set()
        for p in papers:
            if p.primary_key not in seen_keys:
                unique_papers.append(p)
                seen_keys.add(p.primary_key)
        
        if self.TABLE_NAME not in self.db.table_names():
            return unique_papers

        table = self.db.open_table(self.TABLE_NAME)

        # 2. データベース内の存在チェック
        input_keys = list(seen_keys)
        existing_keys = set()

        BATCH_SIZE = 1000
        for i in range(0, len(input_keys), BATCH_SIZE):
            batch_keys = input_keys[i : i + BATCH_SIZE]
            # エスケープ処理
            keys_str = ", ".join(f"'{k.replace('\'', '\'\'')}'" for k in batch_keys)

            try:
                results = table.search().where(f"primary_key IN ({keys_str})").select(["primary_key"]).limit(None).to_arrow()
                batch_existing = results["primary_key"].to_pylist()
                existing_keys.update(batch_existing)
            except Exception as e:
                # クエリエラーの場合はログを出してスキップ (重複として扱わない、または安全側に倒して全部追加?
                # ここではエラーが出ても続行するが、チェックできなかったものは新規扱いになる)
                print(f"[GnosisIndex] Warning: Duplicate check failed for batch: {e}")
                pass

        # 3. 既存のキーを除外
        final_papers = [p for p in unique_papers if p.primary_key not in existing_keys]
        return final_papers
    
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
        
        # 重複排除
        if dedupe:
            papers = self._filter_new_papers(papers)
        
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
    
    def get_by_primary_key(self, primary_key: str) -> Optional[dict]:
        """primary_keyで論文取得"""
        if self.TABLE_NAME not in self.db.table_names():
            return None
        
        table = self.db.open_table(self.TABLE_NAME)
        
        try:
            results = table.search().where(f"primary_key = '{primary_key}'").limit(1).to_list()
            return results[0] if results else None
        except Exception:
            return None
