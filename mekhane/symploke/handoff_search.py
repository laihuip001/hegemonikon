#!/usr/bin/env python3
"""
Handoff Search - /boot 時に関連 Handoff を検索

Usage:
    python handoff_search.py "query"                # Similar handoffs
    python handoff_search.py --latest               # Show latest handoff
    python handoff_search.py --recent 3             # Show 3 most recent
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.kairos_ingest import get_handoff_files, parse_handoff
from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
from mekhane.symploke.indices import Document


def load_handoffs() -> List[Document]:
    """Load all handoffs as documents."""
    files = get_handoff_files()
    return [parse_handoff(f) for f in files]


def search_handoffs(query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
    """Search handoffs by semantic similarity."""
    docs = load_handoffs()
    if not docs:
        return []
    
    # Initialize embedding adapter
    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    
    # Encode all docs
    texts = [d.content for d in docs]
    doc_vectors = adapter.encode(texts)
    
    # Create index and add vectors
    adapter.create_index(dimension=doc_vectors.shape[1])
    metadata = [{"doc_id": d.id, "primary_task": d.metadata.get("primary_task", "")} for d in docs]
    adapter.add_vectors(doc_vectors, metadata=metadata)
    
    # Search
    query_vector = adapter.encode([query])[0]
    results = adapter.search(query_vector, k=top_k)
    
    # Match results to docs
    matched = []
    for r in results:
        idx = r.id
        if idx < len(docs):
            matched.append((docs[idx], r.score))
    
    return matched


def show_latest(n: int = 1):
    """Show N most recent handoffs."""
    docs = load_handoffs()[:n]
    for doc in docs:
        print(f"\n{'='*60}")
        print(f"📄 {doc.id}")
        print(f"主題: {doc.metadata.get('primary_task', 'Unknown')}")
        print(f"時刻: {doc.metadata.get('timestamp', 'Unknown')}")
        print("-"*60)
        print(doc.content[:500] + "..." if len(doc.content) > 500 else doc.content)


def main():
    parser = argparse.ArgumentParser(description="Search handoffs for /boot")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--latest", action="store_true", help="Show latest handoff")
    parser.add_argument("--recent", type=int, help="Show N most recent handoffs")
    parser.add_argument("-k", type=int, default=3, help="Number of results")
    args = parser.parse_args()
    
    if args.latest:
        show_latest(1)
    elif args.recent:
        show_latest(args.recent)
    elif args.query:
        print(f"🔍 Searching: \"{args.query}\"\n")
        results = search_handoffs(args.query, top_k=args.k)
        
        if not results:
            print("No matching handoffs found.")
            return
        
        for doc, score in results:
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📊 Score: {score:.3f}")
            print(f"📄 {doc.id}")
            print(f"主題: {doc.metadata.get('primary_task', 'Unknown')}")
            print(f"時刻: {doc.metadata.get('timestamp', 'Unknown')}")
            print()
    else:
        # Default: show latest
        show_latest(1)


if __name__ == "__main__":
    main()
