# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/pks/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 予測誤差最小化には能動的知識表面化が必要
→ Pull型検索の逆転 → Push型で知識がコンテキストに語りかける
→ pks_engine.py が担う

# PURPOSE: Proactive Knowledge Surface エンジン
# 従来の「検索してから結果を得る」を「データが自ら語りかけてくる」に逆転する。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path resolution
_PKS_DIR = Path(__file__).resolve().parent
_MEKHANE_DIR = _PKS_DIR.parent
_HEGEMONIKON_ROOT = _MEKHANE_DIR.parent

if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

# --- Data Models ---


@dataclass
# PURPOSE: 知識の最小単位 — PKS がプッシュする情報の粒
class KnowledgeNugget:
    """知識の最小単位 — PKS がプッシュする情報の粒"""

    title: str
    abstract: str
    source: str
    relevance_score: float
    url: Optional[str] = None
    authors: Optional[str] = None
    push_reason: str = ""  # なぜこの知識を今プッシュするのか

    # PURPOSE: Markdown 形式で出力
    def to_markdown(self) -> str:
        """Markdown 形式で出力"""
        lines = [
            f"### 📡 {self.title}",
            f"",
            f"**関連度**: {self.relevance_score:.2f} | **ソース**: {self.source}",
        ]
        if self.push_reason:
            lines.append(f"**プッシュ理由**: {self.push_reason}")
        lines.append(f"")
        if self.abstract:
            lines.append(f"> {self.abstract[:300]}...")
        if self.authors:
            lines.append(f"")
            lines.append(f"*Authors: {self.authors[:100]}*")
        if self.url:
            lines.append(f"")
            lines.append(f"[論文リンク]({self.url})")
        return "\n".join(lines)


# PURPOSE: セッションの作業コンテキスト
@dataclass
class SessionContext:
    """セッションの作業コンテキスト"""

    topics: list[str] = field(default_factory=list)
    recent_queries: list[str] = field(default_factory=list)
    active_workflows: list[str] = field(default_factory=list)
    handoff_keywords: list[str] = field(default_factory=list)
    timestamp: str = ""

    # PURPOSE: コンテキストを埋め込み用テキストに変換
    def to_embedding_text(self) -> str:
        """コンテキストを埋め込み用テキストに変換"""
        parts = []
        if self.topics:
            parts.append(f"Topics: {', '.join(self.topics)}")
        if self.recent_queries:
            parts.append(f"Recent queries: {', '.join(self.recent_queries[-5:])}")
        if self.active_workflows:
            parts.append(f"Active workflows: {', '.join(self.active_workflows)}")
        if self.handoff_keywords:
            parts.append(f"Handoff context: {', '.join(self.handoff_keywords)}")
        return " | ".join(parts) if parts else "general knowledge"


# --- Core Engine ---
# PURPOSE: 作業コンテキストのベクトル化保持


class ContextTracker:
    """作業コンテキストのベクトル化保持"""

    # PURPOSE: 内部処理: init__
    def __init__(self):
        self._context = SessionContext()

    @property
    # PURPOSE: 関数: context
    def context(self) -> SessionContext:
        return self._context

    # PURPOSE: トピック更新
    def update_topics(self, topics: list[str]) -> None:
        """トピック更新"""
        self._context.topics = topics
        self._context.timestamp = datetime.now().isoformat()

    # PURPOSE: 検索クエリを履歴に追加
    def add_query(self, query: str) -> None:
        """検索クエリを履歴に追加"""
        self._context.recent_queries.append(query)
        # 直近 20 件のみ保持
        if len(self._context.recent_queries) > 20:
            self._context.recent_queries = self._context.recent_queries[-20:]

    # PURPOSE: アクティブなワークフローを設定
    def set_workflows(self, workflows: list[str]) -> None:
        """アクティブなワークフローを設定"""
        self._context.active_workflows = workflows

    # PURPOSE: 最新 Handoff からキーワードを抽出
    def load_from_handoff(self, handoff_path: Path) -> None:
        """最新 Handoff からキーワードを抽出"""
        if not handoff_path.exists():
            return

        text = handoff_path.read_text(encoding="utf-8", errors="replace")

        # YAML frontmatter からキーワード抽出
        keywords = []
        for line in text.split("\n"):
# PURPOSE: コンテキスト × 未消化データの関連度スコアリング
            line = line.strip()
            if line.startswith("primary_task:"):
                keywords.append(line.split(":", 1)[1].strip().strip('"'))
            elif line.startswith("- \"") and line.endswith("✓\""):
                keywords.append(line.strip("- \"✓"))
        self._context.handoff_keywords = keywords[:10]


class RelevanceDetector:
    """コンテキスト × 未消化データの関連度スコアリング

    GnosisIndex のセマンティック検索を利用し、
    現在のコンテキストに対する各知識の関連度を算出する。
    """

    # PURPOSE: 内部処理: init__
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

    # PURPOSE: 検索結果をコンテキストとの関連度でスコアリング
    def score(
        self,
        context: SessionContext,
        search_results: list[dict],
    ) -> list[KnowledgeNugget]:
        """検索結果をコンテキストとの関連度でスコアリング

        LanceDB の距離スコアを正規化し、閾値以上のものを KnowledgeNugget に変換。
        """
        nuggets = []

        for result in search_results:
            # LanceDB の _distance は低いほど類似度が高い
            distance = result.get("_distance", float("inf"))

            # 距離を 0-1 のスコアに正規化 (低距離 = 高スコア)
            # BGE-small の cosine distance は通常 0〜2 の範囲
            score = max(0.0, 1.0 - (distance / 2.0))

            if score >= self.threshold:
                nugget = KnowledgeNugget(
                    title=result.get("title", "Untitled"),
                    abstract=result.get("abstract", ""),
                    source=result.get("source", "unknown"),
                    relevance_score=score,
                    url=result.get("url"),
                    authors=result.get("authors", ""),
                    push_reason=self._generate_push_reason(context, result, score),
                )
                nuggets.append(nugget)

        # スコア降順でソート
        nuggets.sort(key=lambda n: n.relevance_score, reverse=True)
        return nuggets

    # PURPOSE: プッシュ理由を生成
    def _generate_push_reason(
        self, context: SessionContext, result: dict, score: float
    ) -> str:
        """プッシュ理由を生成"""
        reasons = []
        title = result.get("title", "").lower()
        abstract = result.get("abstract", "").lower()
# PURPOSE: 閾値超過時に知識を能動的にプッシュ

        for topic in context.topics:
            if topic.lower() in title or topic.lower() in abstract:
                reasons.append(f"現在のトピック '{topic}' に直接関連")

        if not reasons:
            reasons.append(f"セマンティック類似度 {score:.2f} でコンテキストに適合")

        return " / ".join(reasons)


class PushController:
    """閾値超過時に知識を能動的にプッシュ

    RelevanceDetector のスコアリング結果を受け取り、
    プッシュ対象の制御（最大件数、重複排除等）を行う。
    """

    # PURPOSE: 内部処理: init__
    def __init__(self, max_push: int = 5, cooldown_hours: float = 24.0):
        self.max_push = max_push
        self.cooldown_hours = cooldown_hours
        self._push_history: dict[str, str] = {}  # title -> last_pushed_at ISO

    # PURPOSE: プッシュ対象をフィルタリング
    def filter_pushable(self, nuggets: list[KnowledgeNugget]) -> list[KnowledgeNugget]:
        """プッシュ対象をフィルタリング"""
        now = datetime.now()
        pushable = []

        for nugget in nuggets:
            # クールダウンチェック
            last_pushed = self._push_history.get(nugget.title)
            if last_pushed:
                elapsed = (now - datetime.fromisoformat(last_pushed)).total_seconds()
                if elapsed < self.cooldown_hours * 3600:
                    continue

            pushable.append(nugget)

            if len(pushable) >= self.max_push:
                break

        return pushable

    # PURPOSE: プッシュ履歴を記録
    def record_push(self, nuggets: list[KnowledgeNugget]) -> None:
        """プッシュ履歴を記録"""
        now_iso = datetime.now().isoformat()
        for nugget in nuggets:
            self._push_history[nugget.title] = now_iso

    # PURPOSE: プッシュ履歴をファイルに保存
    def save_history(self, path: Path) -> None:
# PURPOSE: Proactive Knowledge Surface — メインオーケストレータ
        """プッシュ履歴をファイルに保存"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._push_history, f, ensure_ascii=False, indent=2)

    # PURPOSE: プッシュ履歴をファイルから読み込み
    def load_history(self, path: Path) -> None:
        """プッシュ履歴をファイルから読み込み"""
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self._push_history = json.load(f)


# --- Orchestrator ---


class PKSEngine:
    """Proactive Knowledge Surface — メインオーケストレータ

    使い方:
        engine = PKSEngine()
        engine.set_context(topics=["FEP", "CCL"])
        nuggets = engine.proactive_push()
        for n in nuggets:
            print(n.to_markdown())
    """

    # Push 履歴の保存先
    HISTORY_FILE = "pks_push_history.json"

    # PURPOSE: 内部処理: init__
    def __init__(
        self,
        threshold: float = 0.65,
        max_push: int = 5,
        lance_dir: Optional[Path] = None,
    ):
        self.tracker = ContextTracker()
        self.detector = RelevanceDetector(threshold=threshold)
        self.controller = PushController(max_push=max_push)

        # 遅延インポート (GnosisIndex は重い)
        self._index = None
        self._lance_dir = lance_dir

        # 履歴読み込み
        history_path = _PKS_DIR / self.HISTORY_FILE
        self.controller.load_history(history_path)

    # PURPOSE: GnosisIndex を遅延初期化
    def _get_index(self):
        """GnosisIndex を遅延初期化"""
        if self._index is None:
            from mekhane.anamnesis.index import GnosisIndex

            self._index = GnosisIndex(lance_dir=self._lance_dir)
        return self._index

    # PURPOSE: セッションコンテキストを設定
    def set_context(
        self,
        topics: Optional[list[str]] = None,
        workflows: Optional[list[str]] = None,
        handoff_path: Optional[Path] = None,
    ) -> None:
        """セッションコンテキストを設定"""
        if topics:
            self.tracker.update_topics(topics)
        if workflows:
            self.tracker.set_workflows(workflows)
        if handoff_path:
            self.tracker.load_from_handoff(handoff_path)

    # PURPOSE: 能動的プッシュ: コンテキストに基づいて知識を表面化
    def proactive_push(self, k: int = 20) -> list[KnowledgeNugget]:
        """能動的プッシュ: コンテキストに基づいて知識を表面化

        1. コンテキストをクエリに変換
        2. GnosisIndex でセマンティック検索
        3. RelevanceDetector でスコアリング
        4. PushController でフィルタリング
        5. プッシュ履歴を記録

        Returns:
            プッシュ対象の KnowledgeNugget リスト
        """
        context = self.tracker.context
        query_text = context.to_embedding_text()

        if query_text == "general knowledge":
            print("[PKS] コンテキスト未設定。topics を指定してください。")
            return []

        # Gnōsis 検索
        self.tracker.add_query(query_text)
        index = self._get_index()
        results = index.search(query_text, k=k)

        if not results:
            print("[PKS] 検索結果なし")
            return []

        # スコアリング + フィルタリング
        nuggets = self.detector.score(context, results)
        pushable = self.controller.filter_pushable(nuggets)

        # 履歴記録
        if pushable:
            self.controller.record_push(pushable)
            self.controller.save_history(_PKS_DIR / self.HISTORY_FILE)

        return pushable

    # PURPOSE: 明示的クエリでプッシュ: 通常検索 + PKS フィルタリング
    def search_and_push(self, query: str, k: int = 10) -> list[KnowledgeNugget]:
        """明示的クエリでプッシュ: 通常検索 + PKS フィルタリング

        cli.py の `proactive` サブコマンドから呼ばれる。
        """
        self.tracker.add_query(query)
        index = self._get_index()
        results = index.search(query, k=k)

        if not results:
            return []

        nuggets = self.detector.score(self.tracker.context, results)
        return nuggets  # 明示的検索ではクールダウンなし

    # PURPOSE: プッシュ結果を Markdown レポートに整形
    def format_push_report(self, nuggets: list[KnowledgeNugget]) -> str:
        """プッシュ結果を Markdown レポートに整形"""
        if not nuggets:
            return "📭 プッシュ対象の知識はありません。"

        lines = [
            "## 📡 PKS — 知識が語りかけています",
            "",
            f"_コンテキスト: {', '.join(self.tracker.context.topics) if self.tracker.context.topics else '(未設定)'}_",
            f"_検出数: {len(nuggets)} 件_",
            "",
            "---",
        ]

        for nugget in nuggets:
            lines.append("")
            lines.append(nugget.to_markdown())
            lines.append("")
            lines.append("---")

        return "\n".join(lines)
