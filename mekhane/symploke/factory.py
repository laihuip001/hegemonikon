# PROOF: [L2/インフラ] <- mekhane/symploke/ S2→複数ベクトルDB対応が必要→factory が担う
"""
PROOF: [L2/インフラ]

A0 → 複数ベクトルDB対応が必要
   → ファクトリパターンでアダプタ生成
   → factory.py が担う

Q.E.D.

---

VectorStore Factory

アダプタを動的に生成するファクトリパターン実装。
"""

from typing import Dict, Type, Optional
from .adapters.base import VectorStoreAdapter
from .config import VectorStoreConfig


class VectorStoreFactory:
    """
    ベクトルストアファクトリ

    Usage:
        # 登録 (起動時に一度)
        VectorStoreFactory.register("hnswlib", HNSWlibAdapter)

        # 生成
        store = VectorStoreFactory.create("hnswlib", dimension=768)
    """

    _adapters: Dict[str, Type[VectorStoreAdapter]] = {}

    @classmethod
    def register(cls, name: str, adapter_class: Type[VectorStoreAdapter]) -> None:
        """アダプタを登録"""
        cls._adapters[name.lower()] = adapter_class

    @classmethod
    def create(
        cls, name: str, config: Optional[VectorStoreConfig] = None, **kwargs
    ) -> VectorStoreAdapter:
        """
        アダプタを生成

        Args:
            name: アダプタ名 (hnswlib, faiss, sqlite-vss)
            config: 設定オブジェクト
            **kwargs: アダプタ固有のパラメータ (configより優先)

        Returns:
            VectorStoreAdapter実装

        Raises:
            ValueError: 未知のアダプタ名
        """
        name = name.lower()
        if name not in cls._adapters:
            available = ", ".join(cls._adapters.keys()) or "(none registered)"
            raise ValueError(f"Unknown adapter: '{name}'. " f"Available: {available}")

        # configからパラメータを抽出（kwargsで上書き可能）
        adapter_kwargs = {}
        if config is not None:
            if name == "hnswlib":
                adapter_kwargs = {
                    "M": config.hnsw_M,
                    "ef_construction": config.hnsw_ef_construction,
                    "max_elements": config.hnsw_max_elements,
                }
            elif name == "faiss":
                adapter_kwargs = {
                    "nlist": config.faiss_nlist,
                    "nprobe": config.faiss_nprobe,
                }

        # kwargsで上書き
        adapter_kwargs.update(kwargs)

        adapter = cls._adapters[name](**adapter_kwargs)
        return adapter

    @classmethod
    def list_adapters(cls) -> list[str]:
        """登録済みアダプタ一覧"""
        return list(cls._adapters.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """アダプタが登録済みか確認"""
        return name.lower() in cls._adapters


# === 自動登録 ===
def _register_adapters():
    """利用可能なアダプタを自動登録"""
    try:
        from .adapters.hnswlib_adapter import HNSWlibAdapter

        VectorStoreFactory.register("hnswlib", HNSWlibAdapter)
    except ImportError:
        pass  # TODO: Add proper error handling

    # 将来の拡張用
    # try:
    #     from .adapters.faiss_adapter import FAISSAdapter
    #     VectorStoreFactory.register("faiss", FAISSAdapter)
    # except ImportError:
    #     pass


# モジュール読み込み時に自動登録
_register_adapters()
