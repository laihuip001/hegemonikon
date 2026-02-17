# PROOF: [L2/インフラ] <- mekhane/periskope/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

S5 → 検索・調査機能が必要
   → Deep Research Engine (Periskopē) が必要
   → パッケージエントリポイントが担う

Q.E.D.

---

Periskopē — HGK Deep Research Engine

Multi-source parallel search + multi-model synthesis + TAINT verification.
"""

from .models import SearchResult, SynthesisResult, Citation, PeriskopeConfig, PeriskopeReport

__all__ = [
    "SearchResult",
    "SynthesisResult",
    "Citation",
    "PeriskopeConfig",
    "PeriskopeReport",
]
