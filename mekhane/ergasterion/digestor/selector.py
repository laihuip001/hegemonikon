# PROOF: [L2/インフラ] <- mekhane/ergasterion/digestor/ A0→消化処理が必要→selector が担う
"""
Digestor Selector - 消化候補選定ロジック

Gnosis から収集した論文を、消化すべき候補として選定する。
- SemanticMatcher: ベクトル類似度によるトピックマッチング (A 改善)
- TemplateClassifier: 消化テンプレート T1-T4 の自動推奨 (C 改善)
- DigestorSelector: 統合セレクター
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import yaml
import numpy as np

# Paper モデルのインポート
try:
    from mekhane.anamnesis.models.paper import Paper
except ImportError:
    # フォールバック: 簡易 Paper dataclass
    @dataclass
    # PURPOSE: クラス: Paper
    class Paper:
        id: str
        title: str
        abstract: str = ""
        source: str = ""
        categories: list[str] = field(default_factory=list)
        published: Optional[str] = None
        url: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# DigestCandidate — 消化候補データクラス
# ═══════════════════════════════════════════════════════════

# PURPOSE: 消化候補
@dataclass
class DigestCandidate:
    """消化候補"""

    paper: Paper
    score: float  # 優先度スコア (0.0 - 1.0)
    matched_topics: list[str]  # マッチしたトピック
    rationale: str  # 選定理由
    # C 改善: 推奨テンプレート (スコア付き Top-2)
    suggested_templates: list[tuple[str, float]] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SemanticMatcher — ベクトル類似度によるトピックマッチング (A)
# ═══════════════════════════════════════════════════════════

# PURPOSE: ベクトル類似度によるトピックマッチング
class SemanticMatcher:
    """ベクトル類似度によるトピックマッチング

    EmbeddingAdapter を使い、論文と topic query のコサイン類似度で
    マッチングを行う。キーワードマッチよりも同義語・上位概念を捉えられる。

    "Free Energy Principle" と "variational inference" がマッチしない
    キーワードマッチの問題を解決する。
    """

    # コサイン類似度の閾値: この値以上ならトピックマッチとみなす
    SIMILARITY_THRESHOLD = 0.3

    def __init__(self):
        self._adapter = None
        self._topic_vectors: dict[str, np.ndarray] = {}

    def _get_adapter(self):
        """EmbeddingAdapter を GPU 上でロード"""
        if self._adapter is None:
            from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
            self._adapter = EmbeddingAdapter()
        return self._adapter

    # PURPOSE: トピックのクエリをベクトル化してキャッシュ
    def _ensure_topic_vectors(self, topics: list[dict]) -> None:
        """トピックのクエリをベクトル化してキャッシュ

        初回呼び出し時のみ計算。2回目以降はキャッシュを返す。
        """
        # 未キャッシュのトピックのみ処理
        uncached = [
            t for t in topics
            if t.get("id", "") and t["id"] not in self._topic_vectors
        ]
        if not uncached:
            return

        adapter = self._get_adapter()
        queries = [t.get("query", "") for t in uncached]
        vectors = adapter.encode(queries)

        # 正規化してキャッシュ
        for i, topic in enumerate(uncached):
            vec = vectors[i]
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self._topic_vectors[topic["id"]] = vec

    # PURPOSE: 論文がマッチするトピックをセマンティック検索で検出
    def match_topics(
        self, paper, topics: list[dict], threshold: Optional[float] = None
    ) -> list[tuple[str, float]]:
        """論文がマッチするトピックをセマンティック検索で検出

        Args:
            paper: Paper オブジェクト
            topics: トピック定義リスト
            threshold: 類似度閾値 (None = デフォルト 0.3)

        Returns:
            (topic_id, similarity_score) のリスト（スコア降順）
        """
        if not topics:
            return []

        threshold = threshold or self.SIMILARITY_THRESHOLD

        # トピックベクトルの準備
        self._ensure_topic_vectors(topics)

        # 論文テキストのベクトル化
        adapter = self._get_adapter()
        text = f"{paper.title} {paper.abstract[:1000]}"
        paper_vec = adapter.encode([text])[0]
        norm = np.linalg.norm(paper_vec)
        if norm > 0:
            paper_vec = paper_vec / norm

        # コサイン類似度を計算
        matches = []
        for topic in topics:
            topic_id = topic.get("id", "")
            if topic_id not in self._topic_vectors:
                continue
            similarity = float(np.dot(paper_vec, self._topic_vectors[topic_id]))
            if similarity >= threshold:
                matches.append((topic_id, similarity))

        # スコア降順でソート
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches


# ═══════════════════════════════════════════════════════════
# TemplateClassifier — 消化テンプレート T1-T4 分類 (C)
# ═══════════════════════════════════════════════════════════

# Pythōsis digestion_templates.md から忠実に転写した prototype descriptions
# これらは「理想的な論文像」— 各テンプレートが最もよくマッチする論文の特徴
TEMPLATE_PROTOTYPES: dict[str, str] = {
    "T1_mapping": (
        "A systematic survey, comparison, or taxonomy of frameworks, architectures, and systems. "
        "Cross-referencing existing approaches, establishing correspondence tables between concepts "
        "from different domains. Literature review mapping one theory to another. "
        "Classification systems, ontology alignment, structural comparison."
    ),
    "T2_extraction": (
        "Design philosophy, foundational principles, ethics, and cognitive models. "
        "Theoretical work exploring why systems behave as they do, not how to build them. "
        "Philosophical foundations of computation. Value systems and normative frameworks. "
        "Epistemological inquiry, phenomenological analysis, first-principles reasoning."
    ),
    "T3_absorption": (
        "Algorithm implementation, practical tools, libraries, and engineering techniques. "
        "How to build and optimize systems. Benchmarks, performance evaluation, practical methodology. "
        "Software engineering patterns, API design, concrete code-level solutions. "
        "Reproducible experiments with artifacts and measurable outcomes."
    ),
    "T4_import": (
        "Meta-level architecture, design patterns, type theory, and category-theoretic structures. "
        "Abstract frameworks that organize other frameworks. Higher-order design that shapes "
        "how systems are structured rather than what they do. "
        "Compositionality, modularity, interface design, meta-programming patterns."
    ),
}


# PURPOSE: 消化テンプレート T1-T4 のセマンティック分類
class TemplateClassifier:
    """消化テンプレート T1-T4 のセマンティック分類

    Pythōsis の消化テンプレートを prototype description としてベクトル化し、
    論文の abstract との類似度で最適なテンプレートを推奨する。

    キーワードヒューリスティクスではなくセマンティック分類なので、
    "neural architecture" が T4 (概念輸入) ではなく T3 (機能消化) に
    正しく分類される。
    """

    def __init__(self):
        self._adapter = None
        self._prototype_vectors: dict[str, np.ndarray] = {}

    def _get_adapter(self):
        """EmbeddingAdapter を GPU 上でロード"""
        if self._adapter is None:
            from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
            self._adapter = EmbeddingAdapter()
        return self._adapter

    # PURPOSE: Prototype のベクトルを計算してキャッシュ
    def _ensure_prototype_vectors(self) -> None:
        """Prototype のベクトルを計算してキャッシュ"""
        if self._prototype_vectors:
            return

        adapter = self._get_adapter()
        template_ids = list(TEMPLATE_PROTOTYPES.keys())
        descriptions = [TEMPLATE_PROTOTYPES[tid] for tid in template_ids]
        vectors = adapter.encode(descriptions)

        for i, tid in enumerate(template_ids):
            vec = vectors[i]
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self._prototype_vectors[tid] = vec

    # PURPOSE: 論文に最適な消化テンプレートを Top-2 で推奨
    def classify(self, paper) -> list[tuple[str, float]]:
        """論文に最適な消化テンプレートを Top-2 で推奨

        Args:
            paper: Paper オブジェクト

        Returns:
            [(template_id, score), ...] — Top-2、スコア降順
            例: [("T3_absorption", 0.72), ("T2_extraction", 0.58)]
        """
        self._ensure_prototype_vectors()

        adapter = self._get_adapter()
        text = f"{paper.title} {paper.abstract[:1000]}"
        paper_vec = adapter.encode([text])[0]
        norm = np.linalg.norm(paper_vec)
        if norm > 0:
            paper_vec = paper_vec / norm

        # 全テンプレートとの類似度を計算
        scores = []
        for tid, proto_vec in self._prototype_vectors.items():
            similarity = float(np.dot(paper_vec, proto_vec))
            scores.append((tid, similarity))

        # スコア降順でソート → Top-2
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:2]


# ═══════════════════════════════════════════════════════════
# DigestorSelector — 統合セレクター
# ═══════════════════════════════════════════════════════════

# PURPOSE: 消化候補選定ロジック
class DigestorSelector:
    """消化候補選定ロジック

    セマンティック検索 (SemanticMatcher) + テンプレート分類 (TemplateClassifier)
    を統合し、候補の選定と消化戦略の提案を行う。
    """

    def __init__(
        self,
        topics_file: Optional[Path] = None,
        mode: str = "semantic",
    ):
        """
        Args:
            topics_file: トピック定義 YAML ファイルのパス
            mode: マッチングモード ("semantic" or "keyword")
        """
        self.topics_file = topics_file or self._default_topics_file()
        self.topics = self._load_topics()
        self.mode = mode

        # A: セマンティックマッチャー
        self._semantic_matcher: Optional[SemanticMatcher] = None
        # C: テンプレート分類器
        self._template_classifier: Optional[TemplateClassifier] = None

        # セマンティックモード: 起動時にマッチャーを初期化
        if mode == "semantic":
            try:
                self._semantic_matcher = SemanticMatcher()
                self._template_classifier = TemplateClassifier()
            except Exception as e:
                print(f"[Digestor] Semantic mode init failed, falling back to keyword: {e}")
                self.mode = "keyword"

    # PURPOSE: デフォルトのトピックファイルパス
    def _default_topics_file(self) -> Path:
        """デフォルトのトピックファイルパス"""
        return Path(__file__).parent / "topics.yaml"

    # PURPOSE: トピック定義を読み込む
    def _load_topics(self) -> dict:
        """トピック定義を読み込む"""
        if self.topics_file.exists():
            with open(self.topics_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    # PURPOSE: キーワードマッチでトピックを検出 (フォールバック)
    def _match_topics_keyword(self, paper) -> list[str]:
        """キーワードマッチでトピックを検出 (フォールバック)

        従来のロジック: クエリ内の単語が title/abstract に含まれるか。
        60% 以上マッチでトピックマッチとみなす。
        """
        matched = []
        topics_list = self.topics.get("topics", [])
        text_to_match = f"{paper.title} {paper.abstract}".lower()

        for topic in topics_list:
            query = topic.get("query", "").lower()
            topic_id = topic.get("id", "")
            query_words = query.split()
            match_count = sum(1 for w in query_words if w in text_to_match)

            if len(query_words) > 0 and match_count / len(query_words) >= 0.6:
                matched.append(topic_id)

        return matched

    # PURPOSE: トピックマッチング (セマンティック or キーワード)
    def _match_topics(self, paper) -> list[str]:
        """トピックマッチング (セマンティック or キーワード)

        mode="semantic": SemanticMatcher でベクトル類似度マッチ
        mode="keyword": 従来の 60% キーワードマッチ
        """
        if self.mode == "semantic" and self._semantic_matcher is not None:
            try:
                topics_list = self.topics.get("topics", [])
                matches = self._semantic_matcher.match_topics(paper, topics_list)
                return [topic_id for topic_id, _ in matches]
            except Exception as e:
                print(f"[Digestor] Semantic match failed, falling back to keyword: {e}")
                self.mode = "keyword"
                return self._match_topics_keyword(paper)
        else:
            return self._match_topics_keyword(paper)

    # PURPOSE: テンプレート分類 (セマンティック)
    def _classify_template(self, paper) -> list[tuple[str, float]]:
        """テンプレート分類"""
        if self._template_classifier is not None:
            try:
                return self._template_classifier.classify(paper)
            except Exception as e:
                print(f"[Digestor] Template classification failed: {e}")
                self._template_classifier = None
        return []

    # PURPOSE: 優先度スコアを計算
    def _calculate_score(self, paper, matched_topics: list[str]) -> float:
        """優先度スコアを計算

        スコア要素:
        - トピックマッチ数
        - 新鮮さ（published date）
        - 将来: citation count, relevance to Hegemonikón
        """
        score = 0.0

        # トピックマッチ (0.0 - 0.6)
        max_topics = len(self.topics.get("topics", []))
        if max_topics > 0:
            score += min(len(matched_topics) / max_topics, 1.0) * 0.6

        # Abstract 長さボーナス (長い = 消化しやすい)
        if paper.abstract and len(paper.abstract) > 500:
            score += 0.2
        elif paper.abstract and len(paper.abstract) > 200:
            score += 0.1

        # ソースボーナス
        if paper.source == "arxiv":
            score += 0.1  # arXiv は最新プレプリント
        elif paper.source == "semantic_scholar":
            score += 0.1  # 被引用情報あり

        return min(score, 1.0)

    # PURPOSE: 消化候補を選定
    def select_candidates(
        self,
        papers: list,
        max_candidates: int = 10,
        min_score: float = 0.3,
        topic_filter: Optional[list[str]] = None,
    ) -> list[DigestCandidate]:
        """消化候補を選定

        Args:
            papers: Gnosis から収集した論文リスト
            max_candidates: 最大候補数
            min_score: 最小スコア閾値
            topic_filter: 特定トピックのみ選定（None = 全トピック）

        Returns:
            DigestCandidate のリスト（スコア降順）
        """
        candidates = []

        for paper in papers:
            # トピックマッチング (semantic or keyword)
            matched_topics = self._match_topics(paper)

            # トピックフィルタリング
            if topic_filter:
                matched_topics = [t for t in matched_topics if t in topic_filter]

            # マッチなしはスキップ
            if not matched_topics:
                continue

            # スコア計算
            score = self._calculate_score(paper, matched_topics)

            # 閾値チェック
            if score < min_score:
                continue

            # C: テンプレート分類
            templates = self._classify_template(paper)

            # 選定理由生成
            mode_label = f"[{self.mode}]"
            template_label = ""
            if templates:
                template_label = f" | Template: {templates[0][0]} ({templates[0][1]:.2f})"
            rationale = f"{mode_label} Topics: {', '.join(matched_topics)} | Score: {score:.2f}{template_label}"

            candidates.append(
                DigestCandidate(
                    paper=paper,
                    score=score,
                    matched_topics=matched_topics,
                    rationale=rationale,
                    suggested_templates=templates,
                )
            )

        # スコア降順でソート
        candidates.sort(key=lambda c: c.score, reverse=True)

        return candidates[:max_candidates]

    # PURPOSE: 定義済みトピックを取得
    def get_topics(self) -> list[dict]:
        """定義済みトピックを取得"""
        return self.topics.get("topics", [])
