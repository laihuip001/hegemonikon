# PROOF: [L1/定理] CCL→CCLパーサーが必要→semantic_matcher が担う
"""
Semantic Macro Matcher

Uses vector embeddings to match Japanese natural language to CCL macros.
Integrates with Symplokē for semantic search.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from .macro_registry import MacroRegistry, Macro, BUILTIN_MACROS

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False


@dataclass
class MacroMatch:
    """A matched macro with similarity score."""

    macro: Macro
    score: float
    matched_term: str


# Japanese semantic mappings for macros
MACRO_DESCRIPTIONS_JP = {
    # === Original Macros ===
    "dig": [
        "深く考える",
        "掘り下げる",
        "分析する",
        "熟考する",
        "じっくり考える",
        "深掘りする",
        "検討する",
    ],
    "go": ["実行する", "やる", "進める", "行動する", "走らせる", "動かす", "開始する"],
    "osc": ["往復する", "振動する", "行き来する", "揺れる", "交互に考える", "反復する"],
    "fix": [
        "直す",
        "修正する",
        "改善する",
        "治す",
        "手直しする",
        "修復する",
        "フィックスする",
    ],
    "plan": [
        "計画する",
        "企画する",
        "立案する",
        "設計する",
        "プランを立てる",
        "構想する",
    ],
    "learn": ["学ぶ", "学習する", "覚える", "習得する", "理解する", "勉強する"],
    "nous": ["問う", "尋ねる", "自問する", "探求する", "問いかける", "深く問う"],
    # === H-Series (Hormē) ===
    "h": [
        "動機を確認",
        "衝動を感じる",
        "やる気",
        "モチベーション",
        "傾向と欲求",
        "なぜやりたいか",
    ],
    "pro": [
        "直感",
        "第一印象",
        "初期傾向",
        "ファーストインプレッション",
        "最初に感じたこと",
    ],
    "pis": ["確信度", "信頼度", "どれくらい確か", "自信", "信じる度合い"],
    "ore": ["欲求", "何が欲しいか", "願望", "望み", "本当に欲しいもの"],
    "dox": ["信念", "信じていること", "価値観", "持論", "記録しておきたい"],
    # === P-Series (Perigraphē) ===
    "p": ["環境", "コンテキスト", "場", "状況", "どこで", "空間を考える"],
    "kho": ["スコープ", "範囲", "領域", "境界", "どこまでやるか"],
    "hod": ["道筋", "経路", "ルート", "パス", "どう進むか"],
    "tro": ["軌道", "サイクル", "適用範囲", "イテレーション", "繰り返し範囲"],
    "tek": ["技法", "テクニック", "手法", "やり方", "どうやるか"],
    # === K-Series (Kairos) ===
    "k": ["タイミング", "文脈", "いつ", "状況判断", "機を見る"],
    "euk": ["好機", "チャンス", "今がベスト", "適切なタイミング", "今やるべきか"],
    "chr": ["時間制約", "期限", "デッドライン", "締め切り", "いつまでに"],
    "tel": ["目的", "なぜ", "ゴール", "最終目標", "何のために"],
    "sop": ["知恵", "調査", "リサーチ", "情報収集", "調べる"],
    # === A-Series (Axiōma) ===
    "a": ["評価", "判断", "価値判断", "アセスメント", "良し悪し"],
    "pat": ["感情", "情念", "気持ち", "フィーリング", "どう感じるか"],
    "dia": ["批評", "判定", "レビュー", "クリティーク", "検証する"],
    "gno": ["格言", "教訓", "原則", "ルール", "学んだこと"],
    "epi": ["知識", "確定知", "確かなこと", "事実", "知識化する"],
}


class SemanticMacroMatcher:
    """Matches natural language to macros using embeddings."""

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self, registry: Optional[MacroRegistry] = None):
        """
        Initialize the semantic matcher.

        Args:
            registry: Macro registry to use
        """
        self.registry = registry or MacroRegistry()
        self.model = None
        self.embeddings = {}
        self.term_to_macro = {}

        if HAS_EMBEDDINGS:
            try:
                self.model = SentenceTransformer(self.MODEL_NAME)
                self._build_index()
            except Exception:
                pass  # TODO: Add proper error handling

    def _build_index(self):
        """Build embedding index for all macro descriptions."""
        if not self.model:
            return

        all_terms = []
        for macro_name, terms in MACRO_DESCRIPTIONS_JP.items():
            for term in terms:
                all_terms.append(term)
                self.term_to_macro[term] = macro_name

        if all_terms:
            embeddings = self.model.encode(all_terms)
            for i, term in enumerate(all_terms):
                self.embeddings[term] = embeddings[i]

    def is_available(self) -> bool:
        """Check if semantic matching is available."""
        return self.model is not None and len(self.embeddings) > 0

    def match(self, query: str, top_k: int = 3) -> List[MacroMatch]:
        """
        Find macros that semantically match the query.

        Args:
            query: Japanese natural language query
            top_k: Number of top matches to return

        Returns:
            List of MacroMatch sorted by score
        """
        if not self.is_available():
            return []

        # Encode query
        query_embedding = self.model.encode([query])[0]

        # Calculate similarities
        scores = []
        for term, embedding in self.embeddings.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            macro_name = self.term_to_macro[term]
            macro = self.registry.get(macro_name) or BUILTIN_MACROS.get(macro_name)
            if macro:
                scores.append(
                    MacroMatch(macro=macro, score=float(similarity), matched_term=term)
                )

        # Sort by score, deduplicate by macro name
        scores.sort(key=lambda x: x.score, reverse=True)
        seen = set()
        results = []
        for match in scores:
            if match.macro.name not in seen:
                seen.add(match.macro.name)
                results.append(match)
                if len(results) >= top_k:
                    break

        return results

    def suggest(self, query: str, threshold: float = 0.6) -> Optional[Macro]:
        """
        Suggest the best macro for a query if confidence is high enough.

        Args:
            query: Japanese natural language query
            threshold: Minimum similarity score

        Returns:
            Best matching Macro or None
        """
        matches = self.match(query, top_k=1)
        if matches and matches[0].score >= threshold:
            return matches[0].macro
        return None
