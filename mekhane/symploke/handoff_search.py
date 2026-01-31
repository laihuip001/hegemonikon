#!/usr/bin/env python3
# PROOF: [L2/インフラ] A0→知識管理が必要→handoff_search が担う
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


# Handoff インデックスの永続化パス
HANDOFF_INDEX_PATH = Path("/home/laihuip001/oikos/mneme/.hegemonikon/indices/handoffs.pkl")


def load_handoffs() -> List[Document]:
    """Load all handoffs as documents."""
    files = get_handoff_files()
    return [parse_handoff(f) for f in files]


def build_handoff_index(docs: List[Document] = None) -> EmbeddingAdapter:
    """Build and save handoff index."""
    if docs is None:
        docs = load_handoffs()
    
    if not docs:
        return None
    
    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    
    # Encode all docs
    texts = [d.content for d in docs]
    doc_vectors = adapter.encode(texts)
    
    # Create index
    adapter.create_index(dimension=doc_vectors.shape[1])
    metadata = [
        {
            "doc_id": d.id,
            "idx": i,
            "primary_task": d.metadata.get("primary_task", "")
        }
        for i, d in enumerate(docs)
    ]
    adapter.add_vectors(doc_vectors, metadata=metadata)
    
    # Save
    HANDOFF_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    adapter.save(str(HANDOFF_INDEX_PATH))
    print(f"💾 Handoff index saved: {len(docs)} docs")
    
    return adapter


def load_handoff_index() -> EmbeddingAdapter:
    """Load saved handoff index."""
    adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
    adapter.load(str(HANDOFF_INDEX_PATH))
    return adapter


def search_handoffs(query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
    """Search handoffs by semantic similarity using cached index."""
    docs = load_handoffs()
    if not docs:
        return []
    
    # 永続化インデックスを使用（なければビルド）
    if HANDOFF_INDEX_PATH.exists():
        adapter = load_handoff_index()
    else:
        adapter = build_handoff_index(docs)
        if adapter is None:
            return []
    
    # Search
    query_vector = adapter.encode([query])[0]
    results = adapter.search(query_vector, k=top_k)
    
    # Match results to docs (using idx from metadata)
    matched = []
    for r in results:
        idx = r.metadata.get("idx", r.id)
        if idx < len(docs):
            matched.append((docs[idx], r.score))
    
    return matched


def get_boot_handoffs(mode: str = "standard", context: str = None) -> dict:
    """
    /boot 統合 API: モードに応じた Handoff を返す
    
    Args:
        mode: "fast" (/boot-), "standard" (/boot), "detailed" (/boot+)
        context: 現在のコンテキスト（検索クエリに使用）
    
    Returns:
        dict: {
            "latest": Document,           # 最新の Handoff
            "related": List[Document],    # 関連する Handoff
            "count": int                  # 関連件数
        }
    """
    # モードによる関連件数
    related_count = {
        "fast": 0,       # /boot- : 最新のみ
        "standard": 3,   # /boot  : 最新 + 関連 3
        "detailed": 10   # /boot+ : 最新 + 関連 10
    }.get(mode, 3)
    
    docs = load_handoffs()
    if not docs:
        return {"latest": None, "related": [], "count": 0}
    
    latest = docs[0]
    
    # 関連検索
    related = []
    if related_count > 0 and context:
        results = search_handoffs(context, top_k=related_count + 1)
        # 最新を除外
        related = [doc for doc, score in results if doc.id != latest.id][:related_count]
    elif related_count > 0:
        # コンテキストなしの場合は最新から抽出
        query = latest.metadata.get("primary_task", latest.content[:200])
        results = search_handoffs(query, top_k=related_count + 1)
        related = [doc for doc, score in results if doc.id != latest.id][:related_count]
    
    return {
        "latest": latest,
        "related": related,
        "count": len(related)
    }


def format_boot_output(result: dict, verbose: bool = False) -> str:
    """
    /boot 用の出力フォーマット
    """
    lines = []
    
    if result["latest"]:
        doc = result["latest"]
        lines.append("📋 最新 Handoff:")
        lines.append(f"  ID: {doc.id}")
        lines.append(f"  主題: {doc.metadata.get('primary_task', 'Unknown')}")
        lines.append(f"  時刻: {doc.metadata.get('timestamp', 'Unknown')}")
        if verbose:
            lines.append(f"  内容: {doc.content[:300]}...")
        lines.append("")
    
    if result["related"]:
        lines.append(f"🔗 関連 Handoff ({result['count']}件):")
        for doc in result["related"]:
            lines.append(f"  • {doc.metadata.get('primary_task', doc.id)}")
            lines.append(f"    時刻: {doc.metadata.get('timestamp', 'Unknown')}")
    
    return "\n".join(lines)


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
    parser.add_argument("--boot", choices=["fast", "standard", "detailed"], 
                       help="/boot mode: fast (-), standard, detailed (+)")
    parser.add_argument("--context", type=str, help="Context for /boot search")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # /boot mode
    if args.boot:
        result = get_boot_handoffs(mode=args.boot, context=args.context)
        print(format_boot_output(result, verbose=args.verbose))
        return
    
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
