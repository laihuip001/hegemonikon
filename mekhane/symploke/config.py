# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/symploke/
"""
PROOF: [L2/インフラ]

A0 → 知識システムには設定が必要
   → 環境変数/YAMLからの設定ロード
   → config.py が担う

Q.E.D.

---

Symplokē Configuration

統合設定ファイル。環境変数またはYAMLからロード。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
import os


# PURPOSE: ベクトルストア設定
@dataclass
class VectorStoreConfig:
    """ベクトルストア設定"""

    # アダプタ選択
    adapter: Literal["hnswlib", "faiss", "sqlite-vss", "lancedb"] = "hnswlib"

    # 共通
    dimension: int = 384  # BGE-small default

    # パス
    base_path: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "SYMPLOKE_DATA", "/home/makaron8426/oikos/mneme/indices"
            )  # noqa: AI-ALL
        )
    )

    # hnswlib固有
    hnsw_M: int = 16
    hnsw_ef_construction: int = 200
    hnsw_ef: int = 256
    hnsw_max_elements: int = 1_000_000

    # faiss固有
    faiss_nlist: int = 4096
    faiss_nprobe: int = 256

    def __post_init__(self):
        if isinstance(self.base_path, str):
            self.base_path = Path(self.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)


# PURPOSE: 埋め込みモデル設定
@dataclass
class EmbedderConfig:
    """埋め込みモデル設定"""

    model_type: Literal["bge-small", "openai", "sentence-transformers"] = "bge-small"
    model_path: Optional[Path] = None
    dimension: int = 384  # BGE-small default
    batch_size: int = 32

    def __post_init__(self):
        if self.model_path is None and self.model_type == "bge-small":
            # デフォルトパス
            self.model_path = (
                Path(__file__).parent.parent.parent / "models" / "bge-small"
            )


# PURPOSE: Symploke config の実装
@dataclass
class SymplokeConfig:
    """統合設定"""

    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    embedder: EmbedderConfig = field(default_factory=EmbedderConfig)

    # 検索設定
    default_k: int = 10
    rerank: bool = False

    # PURPOSE: 環境変数から設定を読み込み
    @classmethod
    def from_env(cls) -> "SymplokeConfig":
        """環境変数から設定を読み込み"""
        return cls(
            vector_store=VectorStoreConfig(
                adapter=os.environ.get("SYMPLOKE_ADAPTER", "hnswlib"),
                dimension=int(os.environ.get("SYMPLOKE_DIMENSION", "384")),
            ),
            embedder=EmbedderConfig(
                model_type=os.environ.get("SYMPLOKE_EMBEDDER", "bge-small"),
            ),
        )
