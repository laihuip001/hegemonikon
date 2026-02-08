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
import math
import os
import re
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
    suggested_questions: list[str] = field(default_factory=list)  # v2: 聞くべき質問
    serendipity_score: float = 0.0  # v2: 意外性スコア

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
        """検索クエリを履歴に追加（重複時は末尾に移動）"""
        # 重複排除: 既存なら除去して末尾に再追加
        if query in self._context.recent_queries:
            self._context.recent_queries.remove(query)
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


# --- v2: Autophōnos コンポーネント ---


# PURPOSE: Handoff テキストからトピックを自動抽出する
class AutoTopicExtractor:
    """Handoff テキストからトピックを自動抽出する (Mem 風)

    Handoff の構造（YAML frontmatter + Markdown）を解析し、
    重要なトピックを正規表現ベースで抽出する。
    LLM 不要の軽量実装。
    """

    # キーワード抽出の正規表現パターン
    _YAML_KEYS = re.compile(
        r"(?:primary_task|decision|pattern|topic|recommendation):\s*[\"']?(.+?)[\"']?\s*$",
        re.MULTILINE,
    )
    _COMPLETED_TASKS = re.compile(r"-\s*\[x\]\s*(.+?)(?:\s*✓|$)", re.MULTILINE)
    _NEXT_TASKS = re.compile(r"-\s*\[\s\]\s*(.+?)$", re.MULTILINE)
    _HEADERS = re.compile(r"^#{1,3}\s+(.+)$", re.MULTILINE)
    # SBAR 形式: 太字キーワード (**keyword**)
    _BOLD_KEYWORDS = re.compile(r"\*\*([^*]{3,60})\*\*", re.MULTILINE)
    # Situation セクションの冒頭文 (SBAR format)
    _SITUATION_LINE = re.compile(
        r"^##\s*Situation\s*\n+(.+?)$", re.MULTILINE
    )

    # PURPOSE: Handoff テキストからトピックを自動抽出
    def extract(self, text: str, max_topics: int = 8) -> list[str]:
        """Handoff テキストからトピックを自動抽出

        抽出戦略 (優先度順):
        1. YAML frontmatter のキー値 (primary_task, decision 等)
        2. 完了タスクの名前 ([x])
        3. 未完了タスクの名前 ([ ])
        4. SBAR: Situation セクションの冒頭文
        5. SBAR: 太字キーワード (**keyword**)

        Returns:
            重複排除されたトピックリスト (最大 max_topics 件)
        """
        topics: list[str] = []

        # 1. YAML キー値
        for m in self._YAML_KEYS.finditer(text):
            val = m.group(1).strip()
            if len(val) > 3:  # ノイズ除去
                topics.append(val)

        # 2. 完了タスク名
        for m in self._COMPLETED_TASKS.finditer(text):
            task_name = m.group(1).strip()
            if len(task_name) > 5:
                topics.append(task_name)

        # 3. 未完了タスク名 (次回の文脈として重要)
        for m in self._NEXT_TASKS.finditer(text):
            task_name = m.group(1).strip()
            if len(task_name) > 5:
                topics.append(task_name)

        # 4. SBAR: Situation セクションの冒頭文
        for m in self._SITUATION_LINE.finditer(text):
            situation = m.group(1).strip()
            if len(situation) > 10:
                # 長文は最初の句点で切る
                first_sentence = situation.split("。")[0]
                if len(first_sentence) > 5:
                    topics.append(first_sentence)

        # 5. SBAR: 太字キーワード (上限 5 件)
        bold_count = 0
        noise_words = {
            "前セッション", "本セッション開始地点", "終了地点",
            "セッション時間", "Handoff", "注意",
        }
        for m in self._BOLD_KEYWORDS.finditer(text):
            kw = m.group(1).strip()
            if kw in noise_words or kw.startswith("V["):
                continue
            if len(kw) > 3 and bold_count < 5:
                topics.append(kw)
                bold_count += 1

        # 重複排除 (順序保持)
        seen: set[str] = set()
        unique: list[str] = []
        for t in topics:
            key = t.lower()
            if key not in seen:
                seen.add(key)
                unique.append(t)

        return unique[:max_topics]


# PURPOSE: 「関連するが意外」な情報を優先するスコアリング
class SerendipityScorer:
    """Serendipity Score — 意外だが有用な情報を発見する (Glean/Obsidian 風)

    通常の関連度スコアは「完全一致」を最高としてランク付けするが、
    セレンディピティスコアは「関連するが予想外」な情報を優先する。

    情報理論: Serendipity ≈ Relevance × Surprise
    - Relevance: 既存の関連度スコア
    - Surprise: コンテキストからの「距離」(近すぎず遠すぎずの情報量)
    """

    # PURPOSE: セレンディピティスコアを算出
    def score(
        self,
        relevance: float,
        distance: float,
        sweet_spot: float = 0.45,
        spread: float = 0.15,
    ) -> float:
        """セレンディピティスコアを算出

        Relevance × Gaussian(distance, sweet_spot, spread)

        sweet_spot: 「ちょうどいい意外性」の距離
        spread: sweet_spot 周りの許容幅

        Returns:
            0.0〜1.0 のセレンディピティスコア
        """
        # ガウシアン: sweet_spot 付近で最大、離れるほど減衰
        surprise = math.exp(
            -((distance - sweet_spot) ** 2) / (2 * spread**2)
        )
        return relevance * surprise

    # PURPOSE: KnowledgeNugget リストにセレンディピティスコアを付与
    def enrich(
        self, nuggets: list[KnowledgeNugget], raw_distances: list[float]
    ) -> list[KnowledgeNugget]:
        """KnowledgeNugget リストにセレンディピティスコアを付与

        Args:
            nuggets: スコア付きナゲット
            raw_distances: 各ナゲットの元のベクトル距離
        """
        for nugget, dist in zip(nuggets, raw_distances):
            nugget.serendipity_score = self.score(nugget.relevance_score, dist)
        return nuggets


# PURPOSE: プッシュされた知識から「聞くべき質問」を LLM 生成する
class SuggestedQuestionGenerator:
    """Suggested Questions — NotebookLM の「聞くべき質問」機能の再現

    プッシュされた KnowledgeNugget を分析し、
    Creator が深掘りすべき質問を 3 つ自動生成する。

    Gemini API (google.genai SDK) を使用。
    API 不可時はテンプレートベースのフォールバック。
    """

    _PROMPT_TEMPLATE = (
        "以下の知識について、この知識を活用して洞察を得るために"
        "最も重要な質問を3つ生成してください。\n\n"
        "質問は具体的で、単なる要約の繰り返しではなく、\n"
        "- 応用可能性\n"
        "- 既存知識との接続点\n"
        "- 隠れた前提や限界\n"
        "を問うものにしてください。\n\n"
        "タイトル: {title}\n"
        "要約: {abstract}\n"
        "ソース: {source}\n\n"
        "出力形式: 各質問を1行ずつ、番号なしで出力してください。"
    )

    # PURPOSE: Gemini クライアントを初期化
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model_name = model
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        """Gemini クライアントを遅延初期化"""
        try:
            from google import genai

            api_key = (
                os.environ.get("GOOGLE_API_KEY")
                or os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_GENAI_API_KEY")
            )
            if api_key:
                self._client = genai.Client(api_key=api_key)
            else:
                self._client = genai.Client()
        except (ImportError, Exception):
            self._client = None

    @property
    def is_available(self) -> bool:
        return self._client is not None

    # PURPOSE: KnowledgeNugget から「聞くべき質問」を生成
    def generate(
        self, nugget: KnowledgeNugget, num_questions: int = 3
    ) -> list[str]:
        """KnowledgeNugget から「聞くべき質問」を生成

        LLM 可用時は Gemini で生成。不可時はテンプレートフォールバック。

        Returns:
            質問文字列のリスト (最大 num_questions 件)
        """
        if self.is_available:
            return self._generate_llm(nugget, num_questions)
        return self._generate_fallback(nugget, num_questions)

    def _generate_llm(
        self, nugget: KnowledgeNugget, num_questions: int
    ) -> list[str]:
        """Gemini API で質問を生成"""
        prompt = self._PROMPT_TEMPLATE.format(
            title=nugget.title,
            abstract=nugget.abstract[:500] if nugget.abstract else "(なし)",
            source=nugget.source,
        )

        try:
            response = self._client.models.generate_content(
                model=self.model_name, contents=prompt
            )
            text = response.text if response else ""
            if text:
                lines = [
                    line.strip()
                    for line in text.strip().split("\n")
                    if line.strip() and not line.strip().startswith("#")
                ]
                # 番号プレフィックスを除去
                cleaned = []
                for line in lines:
                    cleaned_line = re.sub(r"^\d+[.\)]\s*", "", line)
                    if cleaned_line:
                        cleaned.append(cleaned_line)
                return cleaned[:num_questions]
        except Exception as e:
            print(f"[PKS] SuggestedQuestion LLM error: {e}")

        return self._generate_fallback(nugget, num_questions)

    def _generate_fallback(
        self, nugget: KnowledgeNugget, num_questions: int
    ) -> list[str]:
        """テンプレートベースのフォールバック生成"""
        title = nugget.title
        questions = [
            f"『{title}』の知見は、現在の作業にどう応用できるか？",
            f"『{title}』が前提としている仮定は何か？その仮定は妥当か？",
            f"『{title}』と矛盾する既知の知識はあるか？",
        ]
        return questions[:num_questions]

    # PURPOSE: 複数ナゲットに一括で質問を付与
    def enrich_batch(self, nuggets: list[KnowledgeNugget]) -> list[KnowledgeNugget]:
        """複数ナゲットに一括で質問を付与"""
        for nugget in nuggets:
            nugget.suggested_questions = self.generate(nugget)
        return nuggets


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
        enable_questions: bool = True,
        enable_serendipity: bool = True,
    ):
        self.tracker = ContextTracker()
        self.detector = RelevanceDetector(threshold=threshold)
        self.controller = PushController(max_push=max_push)
        self.topic_extractor = AutoTopicExtractor()
        self.serendipity_scorer = SerendipityScorer() if enable_serendipity else None
        self.question_gen = SuggestedQuestionGenerator() if enable_questions else None

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

    # PURPOSE: v2: Handoff から自動的にコンテキストを設定
    def auto_context_from_handoff(self, handoff_path: Optional[Path] = None) -> list[str]:
        """Handoff テキストからトピックを自動抽出してコンテキストに設定

        Args:
            handoff_path: Handoff ファイルパス。None の場合は最新を自動検出。

        Returns:
            抽出されたトピックのリスト
        """
        if handoff_path is None:
            # 最新の Handoff を自動検出
            handoff_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "sessions"
            if handoff_dir.exists():
                # handoff_YYYY-MM-DD_HHMM.md パターンのみ対象 (handoff_final 等を除外)
                handoffs = list(handoff_dir.glob("handoff_20??-??-??_????.md"))
                if handoffs:
                    # mtime でソート (最新優先)
                    handoffs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    handoff_path = handoffs[0]

        if handoff_path is None or not handoff_path.exists():
            print("[PKS] Handoff ファイルが見つかりません")
            return []

        text = handoff_path.read_text(encoding="utf-8", errors="replace")
        topics = self.topic_extractor.extract(text)

        if topics:
            self.tracker.update_topics(topics)
            self.tracker.load_from_handoff(handoff_path)
            print(f"[PKS] 自動トピック抽出: {topics}")

        return topics

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

    # PURPOSE: v2: プッシュされた知識に対する「聞くべき質問」を生成
    def suggest_questions(
        self, nuggets: list[KnowledgeNugget]
    ) -> list[KnowledgeNugget]:
        """プッシュされたナゲットに「聞くべき質問」を付与

        Returns:
            suggested_questions が付与された KnowledgeNugget リスト
        """
        if self.question_gen:
            return self.question_gen.enrich_batch(nuggets)
        return nuggets

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

            # v2: 聞くべき質問を表示
            if nugget.suggested_questions:
                lines.append("")
                lines.append("**💡 聞くべき質問:**")
                for q in nugget.suggested_questions:
                    lines.append(f"- {q}")

            # v2: セレンディピティスコアを表示
            if nugget.serendipity_score > 0:
                lines.append(f"")
                lines.append(f"_🎲 意外性: {nugget.serendipity_score:.2f}_")

            lines.append("")
            lines.append("---")

        return "\n".join(lines)
