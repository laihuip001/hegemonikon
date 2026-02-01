# PROOF: [L2/インフラ] A0→索引管理が必要→__init__ が担う
"""
Symplokē Indices Package

4知識源のドメイン固有インデックス
"""

from .base import DomainIndex, SourceType, Document, IndexedResult
from .gnosis import GnosisIndex
from .chronos import ChronosIndex
from .sophia import SophiaIndex
from .kairos import KairosIndex

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
