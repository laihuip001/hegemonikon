# PROOF: [L2/インフラ] <- synergeia/ FEP ベーススレッド選択
"""
Synergeia FEP Selector — 不確実性に基づく最適スレッド選択

FEP (Free Energy Principle) を使って、CCL 式の認知的複雑さを推定し、
最適な実行スレッドを選択する。

Usage:
    from synergeia.fep_selector import select_thread_by_fep
    
    thread = select_thread_by_fep("/noe+ >> V[] < 0.3")
    # → 高複雑度 → "antigravity" (深い思考が必要)
    # → 低複雑度 → "perplexity" (検索で十分)
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# FEP Bridge を遅延インポート (循環参照回避)
FEP_AVAILABLE = False
try:
    from mekhane.fep.fep_bridge import noesis_analyze, NoesisResult
    FEP_AVAILABLE = True
except ImportError:
    pass


@dataclass
class ThreadRecommendation:
    """スレッド推奨結果"""
    thread: str
    confidence: float  # 推奨確信度 (0-1)
    reason: str
    complexity_score: float  # CCL 複雑度 (0-1)


# 複雑度スコアに基づくスレッドマッピング
COMPLEXITY_THREAD_MAP = {
    # 高複雑度 (0.7-1.0): 深い思考が必要
    "high": {
        "thread": "antigravity",
        "reason": "高度な認知処理が必要。手動/深層思考モード推奨。",
    },
    # 中複雑度 (0.4-0.7): 構造化処理
    "medium": {
        "thread": "claude",
        "reason": "構造化処理が適切。Claude CLI 推奨。",
    },
    # 低複雑度 (0-0.4): 検索・単純処理
    "low": {
        "thread": "perplexity",
        "reason": "情報検索で十分。Perplexity API 推奨。",
    },
}


def estimate_ccl_complexity(ccl: str) -> float:
    """
    CCL 式の認知的複雑度を推定 (0-1)
    
    複雑度要因:
    - 演算子の数と種類
    - 収束ループの存在
    - 制御構造 (F:/I:/W:) の存在
    - ネストの深さ
    """
    score = 0.0
    
    # 基本ワークフローの複雑度
    wf_weights = {
        "noe": 0.8,   # 深い認識
        "bou": 0.7,   # 意志決定
        "dia": 0.6,   # 批判的分析
        "zet": 0.5,   # 探求
        "s": 0.4,     # 設計
        "sop": 0.2,   # 検索
        "ene": 0.5,   # 実行
    }
    
    for wf, weight in wf_weights.items():
        if f"/{wf}" in ccl:
            score = max(score, weight)
    
    # 演算子加算
    if "+" in ccl:
        score += 0.1  # 深化
    if ">>" in ccl or "lim" in ccl:
        score += 0.2  # 収束ループ
    if "_" in ccl:
        score += 0.05 * ccl.count("_")  # シーケンス
    if "*" in ccl or "~" in ccl:
        score += 0.1  # 融合/振動
    if "!" in ccl:
        score += 0.15  # 全展開
    
    # 制御構造
    if re.search(r"[FIWL]:\[", ccl):
        score += 0.2
    
    return min(score, 1.0)


def select_thread_by_fep(ccl: str) -> ThreadRecommendation:
    """
    FEP ベースで最適なスレッドを選択
    
    Args:
        ccl: CCL 式
        
    Returns:
        ThreadRecommendation with thread, confidence, and reason
    """
    # CCL 複雑度を推定
    complexity = estimate_ccl_complexity(ccl)
    
    # 複雑度レベルを決定
    if complexity >= 0.7:
        level = "high"
    elif complexity >= 0.4:
        level = "medium"
    else:
        level = "low"
    
    mapping = COMPLEXITY_THREAD_MAP[level]
    
    # オプション: FEP による確信度調整
    fep_confidence = 0.8  # デフォルト
    if FEP_AVAILABLE:
        try:
            # コンテキスト明確度を複雑度から推定
            clarity = 2 if complexity < 0.3 else (1 if complexity < 0.6 else 0)
            result = noesis_analyze(context_clarity=clarity)
            fep_confidence = result.confidence
        except Exception:
            pass
    
    return ThreadRecommendation(
        thread=mapping["thread"],
        confidence=fep_confidence,
        reason=mapping["reason"],
        complexity_score=complexity,
    )


def get_optimal_thread(ccl: str, fallback: str = "antigravity") -> str:
    """シンプルなスレッド選択 (文字列のみ返す)"""
    try:
        result = select_thread_by_fep(ccl)
        return result.thread
    except Exception:
        return fallback


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    test_cases = [
        "/sop+",
        "/noe+",
        "/noe+ >> V[] < 0.3",
        "/s+ _ /ene",
        "/noe! * /dia!",
        "F:[×3]{/dia+}",
    ]
    
    print("=== FEP Thread Selector ===\n")
    for ccl in test_cases:
        result = select_thread_by_fep(ccl)
        print(f"CCL: {ccl}")
        print(f"  Thread: {result.thread}")
        print(f"  Complexity: {result.complexity_score:.2f}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reason: {result.reason}")
        print()
