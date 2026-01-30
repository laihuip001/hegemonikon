"""
Cognitive Axioms — パッシブ認知公理

全ワークフローに暗黙的に適用される認知的規則
"""
from dataclasses import dataclass, field
from typing import Any, Callable
from functools import wraps


@dataclass
class GroundedItem:
    """6W3H で具体化されたアイテム"""
    what: str = ""       # 何を？
    why: str = ""        # なぜ？
    who: str = ""        # 誰が？
    whom: str = ""       # 誰と？
    where: str = ""      # どこで？
    when: str = ""       # いつ？
    how: str = ""        # どうやって？
    how_much: str = ""   # いくらで？
    how_many: str = ""   # どれだけ？
    
    def completeness(self) -> float:
        """具体化の完全性 (0-1)"""
        fields = [self.what, self.why, self.who, self.whom, 
                  self.where, self.when, self.how, self.how_much, self.how_many]
        filled = sum(1 for f in fields if f)
        return filled / len(fields)


@dataclass
class Gap:
    """不足情報"""
    category: str  # SCOPE, TECHNICAL, RESOURCE, DEADLINE, DEPENDENCY
    question: str
    auto_collectible: bool = False


@dataclass
class ActionableOutput:
    """行動可能な出力"""
    next_action: str
    deadline: str = ""
    success_criteria: str = ""
    priority: str = "SHOULD"


# === A1: 接地原則 (Grounding Principle) ===

def apply_grounding(text: str) -> GroundedItem:
    """
    A1: 曖昧な入力を 6W3H で具体化
    
    現在の実装: キーワードベースの抽出
    将来: LLM による自動補完
    """
    grounded = GroundedItem()
    
    # What の抽出
    grounded.what = text[:100] if text else ""
    
    # When の検出
    time_keywords = ["今日", "明日", "今週", "来週", "今月"]
    for kw in time_keywords:
        if kw in text:
            grounded.when = kw
            break
    
    return grounded


# === A2: 分解原則 (Decomposition Principle) ===

def apply_decomposition(items: list[str], max_size: int = 10) -> list[list[str]]:
    """
    A2: 大きなものを小さなものに分解
    
    Args:
        items: 入力アイテムリスト
        max_size: 1バッチの最大サイズ
        
    Returns:
        分割されたバッチのリスト
    """
    if len(items) <= max_size:
        return [items]
    
    # 等分割
    batches = []
    for i in range(0, len(items), max_size):
        batches.append(items[i:i + max_size])
    
    return batches


# === A3: 不足検出原則 (Gap Detection Principle) ===

def detect_gaps(grounded: GroundedItem) -> list[Gap]:
    """
    A3: 不足情報を検出
    """
    gaps = []
    
    if not grounded.what:
        gaps.append(Gap("SCOPE", "何を実現したいですか？"))
    
    if not grounded.when:
        gaps.append(Gap("DEADLINE", "いつまでに完了させますか？"))
    
    if not grounded.how:
        gaps.append(Gap("TECHNICAL", "どのような手段で実現しますか？"))
    
    return gaps


# === A4: 行動可能性原則 (Actionability Principle) ===

def ensure_actionable(output: Any, context: dict = None) -> ActionableOutput:
    """
    A4: 出力を行動可能形式に変換
    """
    if isinstance(output, ActionableOutput):
        return output
    
    # 文字列の場合
    if isinstance(output, str):
        return ActionableOutput(
            next_action=output,
            priority="SHOULD",
        )
    
    # その他の場合
    return ActionableOutput(
        next_action=str(output),
        priority="SHOULD",
    )


# === 統合デコレータ ===

def apply_axioms(func: Callable) -> Callable:
    """
    全公理を適用するデコレータ
    
    Usage:
        @apply_axioms
        def my_workflow(input):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 前処理: A2 分解 + A1 接地
        # (入力がある場合のみ)
        
        # 本体処理
        result = func(*args, **kwargs)
        
        # 後処理: A3 不足検出 + A4 行動可能化
        # (結果がある場合のみ)
        
        return result
    
    return wrapper
