#!/usr/bin/env python3
# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: Doxa (信念) データのエクスポート機能
"""
Doxa Exporter — 信念データのエクスポーター

~/oikos/mneme/.hegemonikon/doxa/ から beliefs.yaml と dox_*.md / doxa_*.md を
構造化フォーマットに変換してエクスポートする。
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .extractor import BaseExporter


class DoxaExporter(BaseExporter):
    """Doxa (信念) データのエクスポーター。

    対象:
    - beliefs.yaml: 信念のYAML定義
    - dox_*.md / doxa_*.md: 個別信念ドキュメント
    """

    def __init__(self, doxa_dir: Path, output_dir: Path):
        super().__init__(output_dir)
        self.doxa_dir = doxa_dir

    # PURPOSE: YAML と Markdown の両方からデータを抽出する
    def extract(self, count: int = 50, **kwargs: Any) -> list[dict[str, Any]]:
        """Doxa ディレクトリから信念データを抽出する。"""
        if not self.doxa_dir.exists():
            return []

        records: list[dict[str, Any]] = []

        # 1. beliefs.yaml からの抽出
        beliefs_path = self.doxa_dir / "beliefs.yaml"
        if beliefs_path.exists():
            try:
                content = beliefs_path.read_text(encoding="utf-8")
                beliefs = yaml.safe_load(content)
                if isinstance(beliefs, dict):
                    records.append({
                        "type": "beliefs_yaml",
                        "filename": "beliefs.yaml",
                        "data": beliefs,
                        "size_bytes": beliefs_path.stat().st_size,
                    })
            except (yaml.YAMLError, OSError):
                pass

        # 2. Markdown files (dox_*.md, doxa_*.md, etc.)
        md_files = sorted(
            [f for f in self.doxa_dir.glob("*.md") if f.name != "README.md"],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:count]

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                record = self._parse_doxa_markdown(md_file, content)
                records.append(record)
            except OSError:
                pass

        return records

    # PURPOSE: Doxa Markdown のメタデータを抽出する
    def _parse_doxa_markdown(
        self, path: Path, content: str
    ) -> dict[str, Any]:
        """Markdown ファイルから構造化データを抽出する。"""
        lines = content.split("\n")
        title = ""
        date = ""
        tags: list[str] = []

        # Extract title from first H1
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract date from > **日付**: or filename
        date_match = re.search(r"\*\*日付\*\*:\s*(\d{4}-\d{2}-\d{2})", content)
        if date_match:
            date = date_match.group(1)
        else:
            # Try filename: doxa_xxx_20260213.md or dox_xxx_2026-02-11.md
            fname_match = re.search(r"(\d{4})(\d{2})(\d{2})", path.stem)
            if fname_match:
                date = f"{fname_match.group(1)}-{fname_match.group(2)}-{fname_match.group(3)}"

        # Extract confidence
        conf_match = re.search(r"\[確信:\s*(\d+)%\]", content)
        confidence = int(conf_match.group(1)) if conf_match else None

        # Extract DX- identifiers
        dx_ids = re.findall(r"(DX-\d{3})", content)

        return {
            "type": "doxa_markdown",
            "filename": path.name,
            "title": title,
            "date": date,
            "confidence": confidence,
            "dx_ids": dx_ids,
            "size_bytes": path.stat().st_size,
            "line_count": len(lines),
            "preview": content[:300],
        }

    # PURPOSE: 抽出データを統一フォーマットに変換する
    def transform(self, records: list[dict[str, Any]], **kwargs: Any) -> Any:
        """Doxa レコードを出力形式に変換する。"""
        return {
            "source": "hegemonikon_doxa",
            "exported_at": datetime.now().isoformat(),
            "count": len(records),
            "types": {
                "yaml": sum(1 for r in records if r["type"] == "beliefs_yaml"),
                "markdown": sum(1 for r in records if r["type"] == "doxa_markdown"),
            },
            "records": records,
        }
