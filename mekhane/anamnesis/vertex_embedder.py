# PROOF: [L2/Mekhane] <- mekhane/anamnesis/vertex_embedder.py S2→Mekhane→Implementation
import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class VertexEmbedder:
    """
    Google Cloud Vertex AI テキストエンベディング (text-embedding-004) を使用する
    Embedder の代替クラス。既存の Embedder と互換性のあるインターフェースを提供。
    """
    
    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        self._dimension = 768
        self._use_gpu = False
        
        try:
            # Vertex AI 初期化 (google-genai SDK互換)
            project = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0769843349")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")
            
            # Application Default Credentials が必要なため自動解決に任せる
            self.client = genai.Client(vertexai=True, project=project, location=location)
            logger.info(f"[VertexEmbedder] initialized. model: {model_name}, dim: {self._dimension}")
        except Exception as e:
            logger.error(f"[VertexEmbedder] initialization failed: {e}")
            raise e

    def embed(self, text: str) -> list[float]:
        """単一テキストの埋め込みベクトルを取得"""
        try:
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"[VertexEmbedder] embed error: {e}")
            raise e

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """複数テキストの埋め込みベクトルをバッチ取得
        Vertex AI API はデフォルトで最大250件の入力をサポート(それ以上は分割が必要)
        """
        try:
            BATCH_SIZE = 250
            all_embeddings = []
            
            for i in range(0, len(texts), BATCH_SIZE):
                batch_texts = texts[i:i + BATCH_SIZE]
                result = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch_texts,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                )
                all_embeddings.extend([e.values for e in result.embeddings])
                
            return all_embeddings
        except Exception as e:
            logger.error(f"[VertexEmbedder] embed_batch error: {e}")
            raise e
