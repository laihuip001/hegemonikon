#!/usr/bin/env python3
# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: Knowledge Item (KI) データのエクスポート機能
"""
KI Exporter — Knowledge Item のエクスポーター

~/.gemini/antigravity/knowledge/ から KI (Markdown ファイル / ディレクトリ) を
構造化フォーマットに変換してエクスポートする。
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .extractor import BaseExporter


class KIExporter(BaseExporter):
    """Knowledge Item (KI) のエクスポーター。

    対象: ~/.gemini/antigravity/knowledge/ 配下の .md ファイルとディレクトリ。
    各 KI はトップレベルのファイルまたはディレクトリ (内部に .md ファイル) として存在する。
    """

    def __init__(self, knowledge_dir: Path, output_dir: Path):
        super().__init__(output_dir)
        self.knowledge_dir = knowledge_dir

    # PURPOSE: KI ディレクトリを再帰走査しデータを抽出する
    def extract(self, count: int = 50, **kwargs: Any) -> list[dict[str, Any]]:
        """Knowledge ディレクトリから KI を抽出する。"""
        if not self.knowledge_dir.exists():
            return []

        records: list[dict[str, Any]] = []

        # Top-level entries (files and directories)
        entries = sorted(self.knowledge_dir.iterdir(), key=lambda p: p.name)

        for entry in entries[:count]:
            if entry.name.startswith("."):
                continue

            if entry.is_file() and entry.suffix == ".md":
                record = self._parse_ki_file(entry)
                records.append(record)
            elif entry.is_dir():
                record = self._parse_ki_directory(entry)
                records.append(record)

        return records

    # PURPOSE: 単一 KI ファイルからメタデータを抽出する
    def _parse_ki_file(self, path: Path) -> dict[str, Any]:
        """Markdown KI ファイルを解析する。"""
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            return {
                "type": "ki_file",
                "name": path.stem,
                "filename": path.name,
                "error": "read_failed",
            }

        lines = content.split("\n")
        title = ""
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract KI type from > **KI 種別**: ...
        ki_type_match = re.search(r"\*\*KI 種別\*\*:\s*(.+)", content)
        ki_type = ki_type_match.group(1).strip() if ki_type_match else "unknown"

        # Extract date
        date_match = re.search(r"\*\*導出日\*\*:\s*(\d{4}-\d{2}-\d{2})", content)
        date = date_match.group(1) if date_match else ""

        # Extract confidence
        conf_match = re.search(r"\[確信:\s*(\d+)%\]", content)
        confidence = int(conf_match.group(1)) if conf_match else None

        return {
            "type": "ki_file",
            "name": path.stem,
            "filename": path.name,
            "title": title,
            "ki_type": ki_type,
            "date": date,
            "confidence": confidence,
            "size_bytes": path.stat().st_size,
            "line_count": len(lines),
            "preview": content[:300],
        }

    # PURPOSE: KI ディレクトリを解析し内容を集約する
    def _parse_ki_directory(self, dir_path: Path) -> dict[str, Any]:
        """KI ディレクトリ (複数ファイルで構成) を解析する。"""
        md_files = list(dir_path.rglob("*.md"))
        total_size = sum(f.stat().st_size for f in md_files if f.exists())

        # Try to get summary from README.md or first .md file
        summary = ""
        readme = dir_path / "README.md"
        if readme.exists():
            try:
                content = readme.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.startswith("# "):
                        summary = line[2:].strip()
                        break
            except OSError:
                pass
        elif md_files:
            try:
                content = md_files[0].read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.startswith("# "):
                        summary = line[2:].strip()
                        break
            except OSError:
                pass

        return {
            "type": "ki_directory",
            "name": dir_path.name,
            "summary": summary,
            "file_count": len(md_files),
            "total_size_bytes": total_size,
            "files": [f.name for f in md_files[:10]],
        }

    # PURPOSE: KI データを統一フォーマットに変換する
    def transform(self, records: list[dict[str, Any]], **kwargs: Any) -> Any:
        """KI レコードを出力形式に変換する。"""
        return {
            "source": "hegemonikon_knowledge_items",
            "exported_at": datetime.now().isoformat(),
            "count": len(records),
            "types": {
                "files": sum(1 for r in records if r["type"] == "ki_file"),
                "directories": sum(1 for r in records if r["type"] == "ki_directory"),
            },
            "records": records,
        }
