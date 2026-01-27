#!/usr/bin/env python3
"""
Sophia Ingest - Knowledge Items を Sophia インデックスに自動投入

Usage:
    python sophia_ingest.py                    # 全KIを投入
    python sophia_ingest.py --dry-run          # パースのみ
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.indices import Document, SophiaIndex
from mekhane.symploke.adapters.mock_adapter import MockAdapter


KNOWLEDGE_DIR = Path("/home/laihuip001/oikos/.gemini/antigravity/knowledge")


def parse_ki_directory(ki_path: Path) -> list[Document]:
    """Parse a KI directory into Documents."""
    docs = []
    
    # Read metadata.json
    metadata_file = ki_path / "metadata.json"
    if not metadata_file.exists():
        return docs
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    ki_name = metadata.get("name", ki_path.name)
    summary = metadata.get("summary", "")
    
    # Read artifact files
    artifacts_dir = ki_path / "artifacts"
    if artifacts_dir.exists():
        for artifact_file in artifacts_dir.glob("*.md"):
            content = artifact_file.read_text(encoding="utf-8")
            
            doc = Document(
                id=f"ki-{ki_path.name}-{artifact_file.stem}",
                content=f"{ki_name}\n\n{summary}\n\n{content[:1500]}",  # Combine for context
                metadata={
                    "type": "knowledge_item",
                    "ki_name": ki_name,
                    "summary": summary[:200],
                    "artifact": artifact_file.name,
                    "file_path": str(artifact_file),
                }
            )
            docs.append(doc)
    
    # If no artifacts, create doc from summary
    if not docs and summary:
        docs.append(Document(
            id=f"ki-{ki_path.name}",
            content=f"{ki_name}\n\n{summary}",
            metadata={
                "type": "knowledge_item",
                "ki_name": ki_name,
                "summary": summary[:200],
            }
        ))
    
    return docs


def get_ki_directories() -> list[Path]:
    """Get all KI directories."""
    dirs = [d for d in KNOWLEDGE_DIR.iterdir() if d.is_dir()]
    return sorted(dirs)


def ingest_to_sophia(docs: list[Document]) -> int:
    """Ingest documents to Sophia index (returns count)."""
    adapter = MockAdapter()
    index = SophiaIndex(adapter, "sophia", dimension=768)
    index.initialize()
    
    count = index.ingest(docs)
    print(f"Ingested {count} documents to Sophia")
    return count


def main():
    parser = argparse.ArgumentParser(description="Ingest KIs to Sophia index")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't ingest")
    args = parser.parse_args()
    
    ki_dirs = get_ki_directories()
    print(f"Found {len(ki_dirs)} KI directories")
    
    all_docs = []
    for ki_dir in ki_dirs:
        print(f"\nParsing: {ki_dir.name}")
        docs = parse_ki_directory(ki_dir)
        for doc in docs:
            print(f"  → {doc.id}")
            all_docs.append(doc)
    
    print(f"\nTotal: {len(all_docs)} documents")
    
    if args.dry_run:
        print("\n[Dry run] Would ingest documents")
        return
    
    ingest_to_sophia(all_docs)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
