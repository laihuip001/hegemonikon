#!/usr/bin/env python3
# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: Gateway Ideas データのエクスポート機能
"""
Ideas Exporter — Gateway Ideas のエクスポーター

~/oikos/mneme/.hegemonikon/ideas/ から idea_*.md ファイルを
構造化フォーマットに変換してエクスポートする。
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .extractor import BaseExporter


class IdeasExporter(BaseExporter):
    """Gateway Ideas のエクスポーター。

    対象: ~/oikos/mneme/.hegemonikon/ideas/idea_*.md
    各 Idea は Markdown 形式で、日時・タグ・ソース等のメタデータを含む。
    """

    def __init__(self, ideas_dir: Path, output_dir: Path):
        super().__init__(output_dir)
        self.ideas_dir = ideas_dir

    # PURPOSE: Ideas ディレクトリから構造化データを抽出する
    def extract(self, count: int = 50, **kwargs: Any) -> list[dict[str, Any]]:
        """Ideas ディレクトリから Idea ファイルを抽出する。"""
        if not self.ideas_dir.exists():
            return []

        records: list[dict[str, Any]] = []

        idea_files = sorted(
            self.ideas_dir.glob("idea_*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:count]

        for idea_file in idea_files:
            try:
                content = idea_file.read_text(encoding="utf-8")
                record = self._parse_idea(idea_file, content)
                records.append(record)
            except OSError:
                pass

        # Also check archived ideas
        archived_dir = self.ideas_dir / "archived"
        if archived_dir.exists():
            archived_files = sorted(
                archived_dir.glob("idea_*.md"),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )[:count]
            for idea_file in archived_files:
                try:
                    content = idea_file.read_text(encoding="utf-8")
                    record = self._parse_idea(idea_file, content)
                    record["archived"] = True
                    records.append(record)
                except OSError:
                    pass

        return records[:count]

    # PURPOSE: Idea Markdown から構造化メタデータを抽出する
    def _parse_idea(self, path: Path, content: str) -> dict[str, Any]:
        """Idea Markdown ファイルを解析する。"""
        lines = content.split("\n")
        title = ""
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract datetime from > **日時**: ...
        dt_match = re.search(r"\*\*日時\*\*:\s*(.+)", content)
        idea_datetime = dt_match.group(1).strip() if dt_match else ""

        # Extract tags from > **タグ**: tag1, tag2, ...
        tag_match = re.search(r"\*\*タグ\*\*:\s*(.+)", content)
        tags: list[str] = []
        if tag_match:
            tags = [t.strip() for t in tag_match.group(1).split(",")]

        # Extract source from > **ソース**: ...
        source_match = re.search(r"\*\*ソース\*\*:\s*(.+)", content)
        source = source_match.group(1).strip() if source_match else ""

        # Extract date from filename: idea_20260213_161747.md
        fname_match = re.search(
            r"idea_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})", path.stem
        )
        file_date = ""
        if fname_match:
            g = fname_match.groups()
            file_date = f"{g[0]}-{g[1]}-{g[2]}T{g[3]}:{g[4]}:{g[5]}"

        # Extract H2 sections as key topics
        sections = re.findall(r"^## (.+)$", content, re.MULTILINE)

        return {
            "type": "idea",
            "filename": path.name,
            "title": title,
            "datetime": idea_datetime or file_date,
            "tags": tags,
            "source": source,
            "sections": sections,
            "archived": False,
            "size_bytes": path.stat().st_size,
            "line_count": len(lines),
            "preview": content[:300],
        }

    # PURPOSE: Ideas データを統一フォーマットに変換する
    def transform(self, records: list[dict[str, Any]], **kwargs: Any) -> Any:
        """Ideas レコードを出力形式に変換する。"""
        all_tags: set[str] = set()
        for r in records:
            all_tags.update(r.get("tags", []))

        return {
            "source": "hegemonikon_gateway_ideas",
            "exported_at": datetime.now().isoformat(),
            "count": len(records),
            "active": sum(1 for r in records if not r.get("archived")),
            "archived": sum(1 for r in records if r.get("archived")),
            "all_tags": sorted(all_tags),
            "records": records,
        }
