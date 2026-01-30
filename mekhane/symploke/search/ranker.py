"""
# PROOF: [L2/インフラ] A0→検索機能が必要→ranker が担う
Symplokē Ranker

Hegemonikón H3: 検索結果のリランキング
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from ..indices.base import IndexedResult


@dataclass
class RankingConfig:
    """リランキング設定"""
    score_normalize: bool = True  # スコアを正規化するか
    min_score: float = 0.0        # 最低スコア閾値


class Ranker:
    """
    検索結果リランキング
    
    複数ソースからの検索結果を統合し、
    重み付けスコアで再順位付けする。
    
    Features:
        - ソース別重み付け
        - スコア正規化
        - 重複排除 (同一 doc_id)
    """
    
    def __init__(self, config: Optional[RankingConfig] = None):
        self._config = config or RankingConfig()
    
    def rank(
        self,
        source_results: Dict[str, List[IndexedResult]],
        weights: Dict[str, float],
        backlink_boost: Optional[Dict[str, float]] = None,
    ) -> List[IndexedResult]:
        """
        ソース別結果を統合ランキング (HybridSearch 対応)
        
        Args:
            source_results: {ソース名: 結果リスト} の辞書
            weights: {ソース名: 重み} の辞書
            backlink_boost: {doc_id: ブースト係数} の辞書 (オプション)
                           バックリンク数に応じたスコアブースト
        
        Returns:
            統合・ソート済み IndexedResult のリスト
        """
        # 全結果を収集
        all_results: List[tuple[float, IndexedResult]] = []
        seen_doc_ids: set = set()
        
        for source_name, results in source_results.items():
            weight = weights.get(source_name, 1.0)
            
            # ソース内でのスコア正規化
            if results and self._config.score_normalize:
                max_score = max(r.score for r in results)
                min_score = min(r.score for r in results)
                score_range = max_score - min_score if max_score != min_score else 1.0
            else:
                score_range = 1.0
                min_score = 0.0
            
            for result in results:
                # 重複排除
                if result.doc_id in seen_doc_ids:
                    continue
                seen_doc_ids.add(result.doc_id)
                
                # 正規化 & 重み付けスコア
                if self._config.score_normalize and score_range > 0:
                    normalized_score = (result.score - min_score) / score_range
                else:
                    normalized_score = result.score
                
                weighted_score = normalized_score * weight
                
                # HybridSearch: バックリンクブースト適用
                if backlink_boost and result.doc_id in backlink_boost:
                    boost = backlink_boost[result.doc_id]
                    # ブースト係数を 0.0-0.5 に制限して過剰ブースト防止
                    boost = min(max(boost, 0.0), 0.5)
                    weighted_score *= (1.0 + boost)
                
                # 最低スコアフィルタ
                if weighted_score >= self._config.min_score:
                    all_results.append((weighted_score, result))
        
        # スコア降順でソート
        all_results.sort(key=lambda x: x[0], reverse=True)
        
        # IndexedResult のみを返す
        return [result for _, result in all_results]
