# PROOF: [L2/インフラ] <- mekhane/symploke/indices/ A0→索引管理が必要→__init__ が担う
"""
Symplokē Indices Package

4知識源のドメイン固有インデックス

Note: Index クラス (GnosisIndex 等) は遅延インポート。
      numpy + VectorStoreAdapter の起動コストを回避するため。
      base の軽量型 (Document 等) のみモジュールレベルでロード。
"""

from .base import DomainIndex, SourceType, Document, IndexedResult

__all__ = [
    "DomainIndex",
    "SourceType",
    "Document",
    "IndexedResult",
    "GnosisIndex",
    "ChronosIndex",
    "SophiaIndex",
    "KairosIndex",
]

# 遅延インポート: 重い依存 (numpy, VectorStoreAdapter) を使用時まで遅延
_LAZY_IMPORTS = {
    "GnosisIndex": ".gnosis",
    "ChronosIndex": ".chronos",
    "SophiaIndex": ".sophia",
    "KairosIndex": ".kairos",
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        import importlib
        module = importlib.import_module(_LAZY_IMPORTS[name], __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
