#!/usr/bin/env python3
# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: Exagoge CLI — ワンコマンドで HGK データをエクスポート
"""
Exagoge CLI — Hegemonikón データエクスポートツール

Usage:
    python -m mekhane.exagoge.cli --type all --format json --output ./exports/
    python -m mekhane.exagoge.cli --type handoff,doxa --count 20
    python -m mekhane.exagoge.cli --type ki --format json
"""

import argparse
import sys
from pathlib import Path

from .doxa_exporter import DoxaExporter
from .extractor import HandoffExporter
from .ideas_exporter import IdeasExporter
from .ki_exporter import KIExporter

# Default paths
DEFAULT_SESSIONS_DIR = Path.home() / "oikos/mneme/.hegemonikon/sessions"
DEFAULT_DOXA_DIR = Path.home() / "oikos/mneme/.hegemonikon/doxa"
DEFAULT_KI_DIR = Path.home() / ".gemini/antigravity/knowledge"
DEFAULT_IDEAS_DIR = Path.home() / "oikos/mneme/.hegemonikon/ideas"
DEFAULT_OUTPUT_DIR = Path.home() / "oikos/hegemonikon/exports"

VALID_TYPES = {"handoff", "doxa", "ki", "ideas", "all"}


def build_parser() -> argparse.ArgumentParser:
    """CLI引数パーサーを構築する。"""
    parser = argparse.ArgumentParser(
        prog="exagoge",
        description="Hegemonikón データエクスポートツール",
    )
    parser.add_argument(
        "--type", "-t",
        default="all",
        help="エクスポート対象 (handoff,doxa,ki,ideas,all) カンマ区切り",
    )
    parser.add_argument(
        "--format", "-f",
        default="json",
        choices=["json", "yaml"],
        help="出力形式 (default: json)",
    )
    parser.add_argument(
        "--output", "-o",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"出力先ディレクトリ (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=50,
        help="最大レコード数 (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルに書かず標準出力に表示",
    )
    return parser


def resolve_types(type_str: str) -> set[str]:
    """タイプ文字列をセットに変換する。"""
    if type_str == "all":
        return {"handoff", "doxa", "ki", "ideas"}
    types = {t.strip() for t in type_str.split(",")}
    invalid = types - VALID_TYPES
    if invalid:
        print(f"❌ 不明なタイプ: {invalid}", file=sys.stderr)
        sys.exit(1)
    return types


def main() -> None:
    """CLI メインエントリーポイント。"""
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output)
    target_types = resolve_types(args.type)
    total_exported = 0
    results = []

    print(f"📦 Exagoge — エクスポート開始")
    print(f"   対象: {', '.join(sorted(target_types))}")
    print(f"   形式: {args.format}")
    print(f"   出力: {output_dir}")
    print()

    exporters = {
        "handoff": lambda: HandoffExporter(
            sessions_dir=DEFAULT_SESSIONS_DIR,
            output_dir=output_dir,
        ),
        "doxa": lambda: DoxaExporter(
            doxa_dir=DEFAULT_DOXA_DIR,
            output_dir=output_dir,
        ),
        "ki": lambda: KIExporter(
            knowledge_dir=DEFAULT_KI_DIR,
            output_dir=output_dir,
        ),
        "ideas": lambda: IdeasExporter(
            ideas_dir=DEFAULT_IDEAS_DIR,
            output_dir=output_dir,
        ),
    }

    for type_name in sorted(target_types):
        if type_name not in exporters:
            continue

        exporter = exporters[type_name]()
        print(f"  ▸ {type_name}... ", end="", flush=True)

        if args.dry_run:
            records = exporter.extract(count=args.count)
            print(f"✅ {len(records)} 件 (dry-run)")
            total_exported += len(records)
        else:
            result = exporter.export(format=args.format, count=args.count)
            if result.success:
                print(f"✅ {result.record_count} 件 → {result.output_path}")
                total_exported += result.record_count
                results.append(result)
            else:
                print(f"❌ {result.errors}")

    print()
    print(f"📊 合計: {total_exported} 件エクスポート完了")


if __name__ == "__main__":
    main()
