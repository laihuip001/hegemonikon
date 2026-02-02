#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→handoff_search が担う
"""
Handoff & Conversation Search - /boot 時に関連 Handoff と会話ログを検索

Usage:
    python handoff_search.py "query"                # Similar handoffs + conversations
    python handoff_search.py --latest               # Show latest handoff
    python handoff_search.py --recent 3             # Show 3 most recent
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timedelta

# Configure module logger
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mekhane.symploke.kairos_ingest import (
    get_handoff_files,
    parse_handoff,
    get_conversation_files,
    parse_conversation,
)
from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
from mekhane.symploke.indices import Document

# Handoff インデックスの永続化パス
HANDOFF_INDEX_PATH = Path(
    "/home/laihuip001/oikos/mneme/.hegemonikon/indices/handoffs.pkl"
)
# 会話ログインデックスの永続化パス (Kairos と共有)
CONVERSATION_INDEX_PATH = Path(
    "/home/laihuip001/oikos/mneme/.hegemonikon/indices/kairos.pkl"
)


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
        {"doc_id": d.id, "idx": i, "primary_task": d.metadata.get("primary_task", "")}
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


# スコア調整設定
SCORE_BOOST = {
    "handoff": 0.08,  # 構造化された総括は価値が高い
    "conversation": 0.0,  # 生の会話は基準値
    "conversation_chunk": 0.0,  # チャンクも基準値
}


def adjust_score(score: float, doc_type: str) -> float:
    """タイプに基づいてスコアを調整する。

    Handoff は構造化された総括なので、生の会話より価値が高いとみなす。
    時間減衰は実装しない（原則・洞察の価値は時間に依存しない）。
    """
    boost = SCORE_BOOST.get(doc_type, 0.0)
    return min(1.0, score + boost)


def extract_keywords(doc: Document, max_keywords: int = 5) -> List[str]:
    """Handoff からキーワードを抽出（Proactive Recall 用）"""
    content = doc.content
    keywords = []

    # primary_task をキーワードとして抽出
    primary_task = doc.metadata.get("primary_task", "")
    if primary_task:
        keywords.append(primary_task)

    # 日本語の重要そうなキーワードを抽出（簡易版）
    import re

    # カタカナ語を抽出
    katakana = re.findall(r"[ァ-ヴー]{3,}", content)
    keywords.extend(katakana[:3])

    # 英語の重要そうな語を抽出
    english = re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)*", content)
    keywords.extend(english[:3])

    return list(set(keywords))[:max_keywords]


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
    /boot 統合 API: モードに応じた Handoff と会話ログを返す

    Args:
        mode: "fast" (/boot-), "standard" (/boot), "detailed" (/boot+)
        context: 現在のコンテキスト（検索クエリに使用）

    Returns:
        dict: {
            "latest": Document,           # 最新の Handoff
            "related": List[Document],    # 関連する Handoff
            "conversations": List[Document],  # 関連する会話ログ ← NEW
            "count": int                  # 関連件数 (handoff + conversation)
        }
    """
    # モードによる関連件数
    related_count = {
        "fast": 0,  # /boot- : 最新のみ
        "standard": 3,  # /boot  : 最新 + 関連 3
        "detailed": 10,  # /boot+ : 最新 + 関連 10
    }.get(mode, 3)

    conv_count = {
        "fast": 0,  # /boot- : なし
        "standard": 2,  # /boot  : 関連会話 2
        "detailed": 5,  # /boot+ : 関連会話 5
    }.get(mode, 2)

    docs = load_handoffs()
    if not docs:
        return {"latest": None, "related": [], "conversations": [], "count": 0}

    latest = docs[0]

    # 検索クエリ
    query = context or latest.metadata.get("primary_task", latest.content[:200])

    # 関連 Handoff 検索
    related = []
    if related_count > 0:
        results = search_handoffs(query, top_k=related_count + 1)
        related = [doc for doc, score in results if doc.id != latest.id][:related_count]

    # 関連会話ログ検索 (Kairos Index を使用)
    conversations = []
    if conv_count > 0 and CONVERSATION_INDEX_PATH.exists():
        try:
            adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
            adapter.load(str(CONVERSATION_INDEX_PATH))
            query_vec = adapter.encode([query])[0]
            results = adapter.search(query_vec, k=conv_count)

            # ファイルパスからドキュメントを再構築
            for r in results:
                file_path = r.metadata.get("file_path")
                if file_path and Path(file_path).exists():
                    doc = parse_conversation(Path(file_path))
                    # スコア調整を適用
                    adjusted_score = adjust_score(r.score, "conversation")
                    doc.metadata["score"] = adjusted_score
                    doc.metadata["raw_score"] = r.score
                    conversations.append(doc)
        except Exception as e:
            print(f"⚠️ Conversation search error: {e}")

    # Proactive Recall: 最新 Handoff からキーワードを抽出し、追加検索
    proactive_memories = []
    if mode == "detailed" and latest:
        keywords = extract_keywords(latest)
        if keywords and CONVERSATION_INDEX_PATH.exists():
            try:
                proactive_query = " ".join(keywords[:3])
                adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
                adapter.load(str(CONVERSATION_INDEX_PATH))
                query_vec = adapter.encode([proactive_query])[0]
                results = adapter.search(query_vec, k=3)

                for r in results:
                    file_path = r.metadata.get("file_path")
                    if file_path and Path(file_path).exists():
                        # 重複チェック
                        if not any(
                            c.metadata.get("file_path") == file_path
                            for c in conversations
                        ):
                            doc = parse_conversation(Path(file_path))
                            doc.metadata["score"] = adjust_score(
                                r.score, "conversation"
                            )
                            doc.metadata["proactive"] = (
                                True  # Proactive Recall でヒット
                            )
                            proactive_memories.append(doc)
            except Exception as e:
                logger.error(f"⚠️ Proactive recall error: {e}", exc_info=True)

    return {
        "latest": latest,
        "related": related,
        "conversations": conversations,
        "proactive": proactive_memories,  # NEW: Proactive Recall 結果
        "count": len(related) + len(conversations) + len(proactive_memories),
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

    if result.get("related"):
        lines.append(f"🔗 関連 Handoff ({len(result['related'])}件):")
        for doc in result["related"]:
            lines.append(f"  • {doc.metadata.get('primary_task', doc.id)}")
            lines.append(f"    時刻: {doc.metadata.get('timestamp', 'Unknown')}")
        lines.append("")

    # NEW: 会話ログ表示
    if result.get("conversations"):
        lines.append(f"💬 関連する過去の会話 ({len(result['conversations'])}件):")
        for doc in result["conversations"]:
            score = doc.metadata.get("score", 0)
            msg_count = doc.metadata.get("msg_count", 0)
            title = doc.metadata.get("title", doc.id)
            lines.append(f"  • {title} ({msg_count} msgs, score: {score:.2f})")
            lines.append(f"    ID: {doc.id}")
        lines.append("")

    # NEW: Proactive Recall 表示
    if result.get("proactive"):
        lines.append(f"🧠 自動浮上した記憶 ({len(result['proactive'])}件):")
        for doc in result["proactive"]:
            score = doc.metadata.get("score", 0)
            title = doc.metadata.get("title", doc.id)
            lines.append(f"  ✨ {title} (score: {score:.2f})")

    return "\n".join(lines)


def show_latest(n: int = 1):
    """Show N most recent handoffs."""
    docs = load_handoffs()[:n]
    for doc in docs:
        print(f"\n{'='*60}")
        print(f"📄 {doc.id}")
        print(f"主題: {doc.metadata.get('primary_task', 'Unknown')}")
        print(f"時刻: {doc.metadata.get('timestamp', 'Unknown')}")
        print("-" * 60)
        print(doc.content[:500] + "..." if len(doc.content) > 500 else doc.content)


def main():
    parser = argparse.ArgumentParser(description="Search handoffs for /boot")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--latest", action="store_true", help="Show latest handoff")
    parser.add_argument("--recent", type=int, help="Show N most recent handoffs")
    parser.add_argument("-k", type=int, default=3, help="Number of results")
    parser.add_argument(
        "--boot",
        choices=["fast", "standard", "detailed"],
        help="/boot mode: fast (-), standard, detailed (+)",
    )
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
        print(f'🔍 Searching: "{args.query}"\n')
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
