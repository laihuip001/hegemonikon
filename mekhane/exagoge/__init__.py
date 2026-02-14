# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: Exagoge パッケージ — データエクスポート・変換機能
"""
mekhane.exagoge — Exagoge (ἐξαγωγή, "export/extraction")

Hegemonikón の内部データを外部形式に変換するためのパイプライン。

主な機能:
- Handoff/Doxa/KI を構造化フォーマット (JSON, YAML, CSV) にエクスポート
- CDP (Claude Desktop Protocol) 互換のエクスポート
- プロンプトテンプレートライブラリの管理

Usage:
    from mekhane.exagoge import Exporter
    exporter = Exporter()
    exporter.export_handoffs(format="json")
"""

from pathlib import Path

__version__ = "0.1.0"
EXAGOGE_ROOT = Path(__file__).parent
LIBRARY_DIR = EXAGOGE_ROOT / "library"
