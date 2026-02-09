# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → 永続化された知識が「自ら語りかけてくる」必要がある
   → proactive_push.py が担う

Q.E.D.

---

Proactive Push — 「データが自ら語りかけてくる DB」

Architecture:
  知識推薦の3つのトリガー:
    1. Context-Triggered: ユーザー文脈からベクトル近傍を推薦
    2. Graph-Triggered:   リンクグラフ上のバックリンク・ブリッジノードを推薦
    3. Time-Triggered:    定期的に未読/高関連知識をプッシュ

  Source:
    - NotebookLM の Source Grounding + Studio Mode
    - Obsidian の Bidirectional Links + Graph View
    - Mem0 の自動関連付け
    - 既存 Proactive Recall (handoff_search.py) の LanceDB 統合版

  Ingestion:
    - /boot 時: boot_recommendations() で「今日の推薦」を 3 件表示
    - チャット中: context_recommendations() でリアルタイム推薦
"""

import re
import time
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Paths
_MNEME_ROOT = Path.home() / "oikos" / "mneme" / ".hegemonikon"
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
LINK_GRAPH_PATH = _MNEME_ROOT / "indices" / "link_graph.json"


@dataclass
class Recommendation:
    """ユーザーへの知識推薦 1 件."""

    title: str
    source_type: str  # papers / knowledge / session / handoff
    relevance: float  # 0.0 - 1.0
    trigger: str  # context / graph / time
    benefit: str  # ユーザーへのベネフィット説明
    content_snippet: str  # 先頭 300 文字
    url: str = ""
    primary_key: str = ""
    distance: float = 0.0
    actions: list[str] = field(default_factory=lambda: ["/eat", "/jukudoku"])


@dataclass
class PushResult:
    """推薦結果の集約."""

    recommendations: list[Recommendation]
    trigger_type: str  # boot / context / time
    query_used: str
    retrieval_time: float
    total_candidates: int


class ProactivePush:
    """「データが自ら語りかけてくる DB」の核心実装.

    3 つのトリガーを統合:
      1. Context-Triggered: チャット文脈からベクトル近傍を推薦
      2. Graph-Triggered: リンクグラフ上の関連ノードを推薦 (Phase 2 で実装)
      3. Time-Triggered: 定期プッシュ (n8n 連携で実装)

    Layer 構成:
      GnosisIndex (LanceDB) → Bi-encoder 検索
      → Reranker (Cross-encoder) → 精度向上
      → Benefit Generator → ベネフィット説明生成
      → 推薦フォーマット出力
    """

    # 推薦閾値 (LanceDB L2 distance, normalized)
    # 0 = identical, ~1.0 = unrelated
    DISTANCE_THRESHOLD = 0.85

    # Papers は cross-language gap を考慮して緩和
    PAPERS_DISTANCE_THRESHOLD = 0.95

    # 重複除去: 推薦済みのキーを記録 (セッション内のみ)
    _seen_keys: set[str] = set()

    def __init__(
        self,
        max_recommendations: int = 3,
        use_reranker: bool = True,
        include_papers: bool = True,
        include_knowledge: bool = True,
    ):
        self.max_recommendations = max_recommendations
        self.use_reranker = use_reranker
        self.include_papers = include_papers
        self.include_knowledge = include_knowledge

        self._index = None
        self._reranker = None
        self._seen_keys: set[str] = set()

    def _load_index(self):
        """GnosisIndex をロード."""
        if self._index is not None:
            return
        from mekhane.anamnesis.index import GnosisIndex

        self._index = GnosisIndex()
        logger.info("[ProactivePush] Index loaded")

    def _load_reranker(self):
        """Reranker をロード (optional)."""
        if not self.use_reranker or self._reranker is not None:
            return
        from mekhane.anamnesis.gnosis_chat import Reranker

        self._reranker = Reranker()
        logger.info("[ProactivePush] Reranker loaded")

    def _retrieve(self, query: str, k: int = 10) -> list[dict]:
        """LanceDB からセマンティック検索 + 閾値フィルタ + Rerank.

        GnosisChat._retrieve() と同等のロジックだが、
        推薦用に独立させる（GnosisChat と結合度を下げる）。
        """
        self._load_index()
        from mekhane.anamnesis.lancedb_compat import get_table_names

        results = []
        fetch_k = k * 3 if self.use_reranker else k

        # Papers table
        if self.include_papers:
            try:
                paper_results = self._index.search(query, k=fetch_k)
                for r in paper_results:
                    r["_source_table"] = "papers"
                results.extend(paper_results)
            except Exception as e:
                logger.warning(f"[ProactivePush] Papers search failed: {e}")

        # Knowledge table
        if self.include_knowledge:
            try:
                if "knowledge" in get_table_names(self._index.db):
                    embedder = self._index._get_embedder()
                    table = self._index.db.open_table("knowledge")

                    from mekhane.anamnesis.index import _get_vector_dimension

                    table_dim = _get_vector_dimension(table)
                    embedder_dim = getattr(embedder, "_dimension", 0)

                    if table_dim and embedder_dim and table_dim != embedder_dim:
                        logger.warning(
                            f"[ProactivePush] Dimension mismatch: "
                            f"table={table_dim}, embedder={embedder_dim}. "
                            f"Skipping knowledge."
                        )
                    else:
                        qvec = embedder.embed(query)
                        k_results = table.search(qvec).limit(fetch_k).to_list()
                        for r in k_results:
                            r["_source_table"] = "knowledge"
                        results.extend(k_results)
            except Exception as e:
                logger.warning(f"[ProactivePush] Knowledge search failed: {e}")

        # Layer 1: Bi-encoder 距離閾値フィルタ
        results = [
            r
            for r in results
            if r.get("_distance", 999)
            < (
                self.PAPERS_DISTANCE_THRESHOLD
                if r.get("_source_table") == "papers"
                else self.DISTANCE_THRESHOLD
            )
        ]

        results.sort(key=lambda r: r.get("_distance", 999))

        # Layer 2: Reranker
        if self.use_reranker and results:
            self._load_reranker()
            if self._reranker:
                results = self._reranker.rerank(query, results, top_k=k)
        else:
            results = results[:k]

        return results

    def _generate_benefit(self, result: dict, query: str) -> str:
        """検索結果からベネフィット説明を生成.

        LLM を使わず、ルールベースで生成（軽量化のため）。
        Phase 4 で LLM 生成に切り替え可能。
        """
        title = result.get("title", "Untitled")
        source = result.get("source", result.get("_source_table", "unknown"))
        distance = result.get("_distance", 1.0)
        relevance = 1 - distance

        # ソースタイプ別のベネフィット
        benefit_templates = {
            "papers": f"論文 '{title}' が現在のコンテキストに {relevance:.0%} の関連性",
            "arxiv": f"論文 '{title}' が現在のコンテキストに {relevance:.0%} の関連性",
            "handoff": f"過去の引継書 '{title}' に類似のコンテキストあり",
            "session": f"過去のセッション '{title}' に関連する議論あり",
            "ki": f"知識項目 '{title}' がこの文脈に適用可能",
            "kernel": f"カーネル定義 '{title}' がこの設計に関連",
            "doxa": f"信念記録 '{title}' がこの判断に影響",
            "workflow": f"ワークフロー '{title}' がこのタスクに有用",
            "research": f"研究ノート '{title}' に関連知見あり",
        }

        return benefit_templates.get(
            source,
            f"'{title}' が現在のコンテキストに {relevance:.0%} の関連性",
        )

    def _to_recommendation(
        self, result: dict, query: str, trigger: str
    ) -> Recommendation:
        """検索結果を Recommendation に変換."""
        distance = result.get("_distance", 1.0)
        source_table = result.get("_source_table", "unknown")

        # content or abstract
        if source_table == "knowledge":
            snippet = result.get("content", result.get("abstract", ""))[:300]
        else:
            snippet = result.get("abstract", "")[:300]

        actions = ["/eat", "/jukudoku"]
        if source_table == "papers":
            actions = ["/eat", "/sop"]

        return Recommendation(
            title=result.get("title", "Untitled")[:100],
            source_type=result.get("source", source_table),
            relevance=round(1 - distance, 4),
            trigger=trigger,
            benefit=self._generate_benefit(result, query),
            content_snippet=snippet,
            url=result.get("url", ""),
            primary_key=result.get("primary_key", ""),
            distance=round(distance, 4),
            actions=actions,
        )

    def _deduplicate(self, recs: list[Recommendation]) -> list[Recommendation]:
        """セッション内の重複除去."""
        unique = []
        for rec in recs:
            key = rec.primary_key or rec.title
            if key not in self._seen_keys:
                self._seen_keys.add(key)
                unique.append(rec)
        return unique

    # ==========================================================
    # Public API
    # ==========================================================

    def boot_recommendations(
        self, context: Optional[str] = None
    ) -> PushResult:
        """/boot 時の推薦 — 「今日の推薦」.

        Args:
            context: 直近の Handoff の primary_task や目的テキスト。
                     None の場合、直近 Handoff から自動抽出を試みる。

        Returns:
            PushResult: 推薦結果
        """
        t0 = time.time()

        # コンテキスト自動抽出: 直近の Handoff を読む
        if context is None:
            context = self._extract_latest_context()

        if not context:
            return PushResult(
                recommendations=[],
                trigger_type="boot",
                query_used="",
                retrieval_time=0,
                total_candidates=0,
            )

        # 検索実行
        results = self._retrieve(context, k=self.max_recommendations * 2)
        retrieval_time = time.time() - t0

        # Recommendation に変換
        recs = [
            self._to_recommendation(r, context, trigger="context")
            for r in results
        ]

        # 重複除去 + 上限適用
        recs = self._deduplicate(recs)[: self.max_recommendations]

        return PushResult(
            recommendations=recs,
            trigger_type="boot",
            query_used=context[:100],
            retrieval_time=round(retrieval_time, 3),
            total_candidates=len(results),
        )

    def context_recommendations(
        self, user_message: str, max_recs: int = 2
    ) -> PushResult:
        """チャット中のリアルタイム推薦.

        ユーザーのメッセージからベクトル近傍を検索し、
        関連知識を「データが語りかける」形式で推薦する。

        Args:
            user_message: ユーザーの直近メッセージ
            max_recs: 推薦上限（チャット中は控えめに）

        Returns:
            PushResult: 推薦結果
        """
        t0 = time.time()

        # 短すぎるメッセージは推薦しない
        if len(user_message.strip()) < 20:
            return PushResult(
                recommendations=[],
                trigger_type="context",
                query_used=user_message,
                retrieval_time=0,
                total_candidates=0,
            )

        results = self._retrieve(user_message, k=max_recs * 2)
        retrieval_time = time.time() - t0

        recs = [
            self._to_recommendation(r, user_message, trigger="context")
            for r in results
        ]

        recs = self._deduplicate(recs)[:max_recs]

        return PushResult(
            recommendations=recs,
            trigger_type="context",
            query_used=user_message[:100],
            retrieval_time=round(retrieval_time, 3),
            total_candidates=len(results),
        )

    def _extract_latest_context(self) -> str:
        """直近の Handoff から primary_task を抽出."""
        sessions_dir = _MNEME_ROOT / "sessions"
        if not sessions_dir.exists():
            return ""

        handoffs = sorted(sessions_dir.glob("handoff_*.md"), reverse=True)
        if not handoffs:
            return ""

        latest = handoffs[0]
        try:
            content = latest.read_text(encoding="utf-8")

            # YAML フロントマターから primary_task を抽出
            match = re.search(r"primary_task:\s*[\"']?(.+?)[\"']?\s*$", content, re.M)
            if match:
                return match.group(1)

            # フォールバック: 主題行を探す
            match = re.search(r"\*\*主題\*\*:\s*(.+)", content)
            if match:
                return match.group(1)

            # さらにフォールバック: 先頭 200 文字
            return content[:200]
        except Exception as e:
            logger.warning(f"[ProactivePush] Failed to read handoff: {e}")
            return ""

    def reset_session(self):
        """セッション内の重複除去キャッシュをリセット."""
        self._seen_keys.clear()

    # ==========================================================
    # Format
    # ==========================================================

    @staticmethod
    def format_recommendations(result: PushResult) -> str:
        """推薦結果を人間向けフォーマットに変換.

        /boot 時やチャット中に表示する形式。
        """
        if not result.recommendations:
            return ""

        header = {
            "boot": "🧠 この知識があなたに語りかけています",
            "context": "💡 関連する知識を発見",
            "time": "📬 定期推薦",
        }.get(result.trigger_type, "💡 推薦")

        lines = [f"\n{'=' * 50}", f"  {header}", f"{'=' * 50}"]

        for i, rec in enumerate(result.recommendations, 1):
            icon = {
                "papers": "📄",
                "arxiv": "📄",
                "knowledge": "🧠",
                "session": "💬",
                "handoff": "📋",
                "ki": "💎",
                "kernel": "⚙️",
                "doxa": "🏛️",
                "workflow": "🔧",
                "research": "🔬",
            }.get(rec.source_type, "📁")

            lines.append(f"\n  [{i}] {icon} {rec.title}")
            lines.append(f"      関連度: {rec.relevance:.0%}")
            lines.append(f"      → {rec.benefit}")
            if rec.content_snippet:
                snippet = rec.content_snippet[:120].replace("\n", " ")
                lines.append(f"      概要: {snippet}...")
            actions_str = " | ".join(rec.actions + ["無視"])
            lines.append(f"      アクション: {actions_str}")

        lines.append(f"\n  検索時間: {result.retrieval_time:.2f}s")
        lines.append(f"  候補数: {result.total_candidates}")
        lines.append(f"{'=' * 50}\n")

        return "\n".join(lines)

    @staticmethod
    def format_compact(result: PushResult) -> str:
        """チャット中の控えめなフォーマット.

        リアルタイム推薦は邪魔にならないよう短く。
        """
        if not result.recommendations:
            return ""

        lines = ["💡 **関連知識**:"]
        for rec in result.recommendations:
            lines.append(
                f"  - [{rec.source_type}] {rec.title} "
                f"(関連度 {rec.relevance:.0%})"
            )
        return "\n".join(lines)


# ==========================================================
# Convenience functions
# ==========================================================

_push_instance: Optional[ProactivePush] = None


def get_push() -> ProactivePush:
    """シングルトン ProactivePush インスタンスを取得."""
    global _push_instance
    if _push_instance is None:
        _push_instance = ProactivePush()
    return _push_instance


def boot_push(context: Optional[str] = None) -> str:
    """/boot 時の推薦を実行し、フォーマット済み文字列を返す.

    Usage:
        from mekhane.anamnesis.proactive_push import boot_push
        print(boot_push())
    """
    push = get_push()
    result = push.boot_recommendations(context)
    return ProactivePush.format_recommendations(result)


def context_push(user_message: str) -> str:
    """チャット中のリアルタイム推薦を実行し、コンパクト文字列を返す.

    Usage:
        from mekhane.anamnesis.proactive_push import context_push
        print(context_push("FEP の数学的定式化について"))
    """
    push = get_push()
    result = push.context_recommendations(user_message)
    return ProactivePush.format_compact(result)


# ==========================================================
# CLI
# ==========================================================

def main():
    """CLI エントリーポイント."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Proactive Push — データが自ら語りかけてくる DB"
    )
    subparsers = parser.add_subparsers(dest="command")

    # boot
    boot_parser = subparsers.add_parser("boot", help="/boot 時の推薦")
    boot_parser.add_argument(
        "--context", "-c", default=None, help="コンテキスト（省略時: 直近 Handoff）"
    )
    boot_parser.add_argument(
        "--max", "-n", type=int, default=3, help="推薦上限"
    )

    # context
    ctx_parser = subparsers.add_parser("context", help="リアルタイム推薦")
    ctx_parser.add_argument("message", help="ユーザーメッセージ")
    ctx_parser.add_argument(
        "--max", "-n", type=int, default=2, help="推薦上限"
    )

    args = parser.parse_args()

    if args.command == "boot":
        push = ProactivePush(max_recommendations=args.max)
        result = push.boot_recommendations(args.context)
        print(ProactivePush.format_recommendations(result))
    elif args.command == "context":
        push = ProactivePush(max_recommendations=args.max)
        result = push.context_recommendations(args.message, max_recs=args.max)
        print(ProactivePush.format_recommendations(result))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
