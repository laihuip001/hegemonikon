# PROOF: [L2/インフラ] <- mekhane/dendron/
"""
Dendron — 存在証明検証ツール

Hegemonikón の各ファイル・ディレクトリに「存在理由」が
宣言されていることを検証するツール。
"""

from .checker import DendronChecker, ProofStatus, ProofLevel, MetaLayer, FileProof, FunctionProof, VariableProof, DirProof, StructureProof, FunctionNFProof, VerificationProof, CheckResult
from .reporter import DendronReporter, ReportFormat

__version__ = "3.0.0"

__all__ = [
    "DendronChecker",
    "DocStalenessChecker",
    "ProofStatus",
    "ProofLevel",
    "MetaLayer",
    "FileProof",
    "FunctionProof",
    "VariableProof",
    "DirProof",
    "StructureProof",
    "FunctionNFProof",
    "VerificationProof",
    "CheckResult",
    "DendronReporter",
    "ReportFormat",
]


# PURPOSE: DocStalenessChecker を遅延 import し、python -m 実行時の RuntimeWarning を回避する
def __getattr__(name: str):  # type: ignore[no-untyped-def]
    if name == "DocStalenessChecker":
        from .doc_staleness import DocStalenessChecker
        return DocStalenessChecker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


