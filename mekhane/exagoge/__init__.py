# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: Exagoge パッケージ — データエクスポート・変換機能
"""
mekhane.exagoge — Exagoge (ἐξαγωγή, "export/extraction")

Hegemonikón の内部データを外部形式に変換するためのパイプライン。

主な機能:
- Handoff/Doxa/KI/Ideas を構造化フォーマット (JSON, YAML) にエクスポート
- CLI ツールによるワンコマンドエクスポート

Usage:
    from mekhane.exagoge import HandoffExporter, DoxaExporter, KIExporter, IdeasExporter
    from mekhane.exagoge.cli import main as export_cli

    # プログラマティック使用
    exporter = DoxaExporter(doxa_dir=Path("..."), output_dir=Path("..."))
    result = exporter.export(format="json")

    # CLI 使用
    python -m mekhane.exagoge.cli --type all --format json
"""

from pathlib import Path

from .doxa_exporter import DoxaExporter
from .extractor import BaseExporter, ExportResult, HandoffExporter
from .ideas_exporter import IdeasExporter
from .ki_exporter import KIExporter

__version__ = "0.2.0"
__all__ = [
    "BaseExporter",
    "ExportResult",
    "HandoffExporter",
    "DoxaExporter",
    "KIExporter",
    "IdeasExporter",
]

EXAGOGE_ROOT = Path(__file__).parent
LIBRARY_DIR = EXAGOGE_ROOT / "library"
