#!/usr/bin/env python3
"""
Kairos Ingest - Handoff を Kairos インデックスに自動投入

Usage:
    python kairos_ingest.py                    # 最新1件を投入
    python kairos_ingest.py --all              # 全件を投入
    python kairos_ingest.py --file <path>      # 指定ファイルを投入
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, KairosIndex
from mekhane.symploke.adapters.mock_adapter import MockAdapter


HANDOFF_DIR = Path("/home/laihuip001/oikos/mneme/.hegemonikon/sessions")


def parse_handoff(file_path: Path) -> Document:
    """Parse a handoff markdown file into a Document."""
    content = file_path.read_text(encoding="utf-8")
    
    # Extract metadata from filename: handoff_YYYY-MM-DD_HHMM.md
    match = re.match(r"handoff_(\d{4}-\d{2}-\d{2})_(\d{4})\.md", file_path.name)
    if match:
        date_str, time_str = match.groups()
        timestamp = f"{date_str}T{time_str[:2]}:{time_str[2:]}:00"
    else:
        timestamp = datetime.now().isoformat()
    
    # Extract primary task from content (look for **主題**: or **セッション**:)
    primary_task = "Unknown"
    task_match = re.search(r"\*\*主題\*\*:\s*(.+?)(?:\n|$)", content)
    if task_match:
        primary_task = task_match.group(1).strip()
    
    return Document(
        id=f"handoff-{file_path.stem}",
        content=content[:2000],  # Truncate for embedding
        metadata={
            "timestamp": timestamp,
            "type": "handoff",
            "primary_task": primary_task,
            "file_path": str(file_path),
        }
    )


def get_handoff_files() -> list[Path]:
    """Get all handoff files sorted by date (newest first)."""
    files = list(HANDOFF_DIR.glob("handoff_*.md"))
    return sorted(files, reverse=True)


def ingest_to_kairos(docs: list[Document]) -> int:
    """Ingest documents to Kairos index (returns count)."""
    adapter = MockAdapter()
    index = KairosIndex(adapter, "kairos", dimension=768)
    index.initialize()
    
    count = index.ingest(docs)
    print(f"Ingested {count} documents to Kairos")
    return count


def main():
    parser = argparse.ArgumentParser(description="Ingest handoffs to Kairos index")
    parser.add_argument("--all", action="store_true", help="Ingest all handoff files")
    parser.add_argument("--file", type=str, help="Ingest specific file")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't ingest")
    args = parser.parse_args()
    
    if args.file:
        files = [Path(args.file)]
    elif args.all:
        files = get_handoff_files()
    else:
        # Default: latest only
        files = get_handoff_files()[:1]
    
    if not files:
        print("No handoff files found")
        return
    
    docs = []
    for f in files:
        print(f"Parsing: {f.name}")
        doc = parse_handoff(f)
        docs.append(doc)
        print(f"  → {doc.id}: {doc.metadata.get('primary_task', 'N/A')}")
    
    if args.dry_run:
        print(f"\n[Dry run] Would ingest {len(docs)} documents")
        return
    
    ingest_to_kairos(docs)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
