"""
Prompt Literacy — Pattern Database

改善パターンと技法推奨のデータベース
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Pattern:
    """改善パターン定義"""
    regex: str
    context_check: Optional[str]
    suggestion: str
    reason: str
    mechanism: str


@dataclass
class Technique:
    """技法定義"""
    name: str
    detection_pattern: str
    situation: str
    example: str
    mechanism: str


# ============================================================
# 改善パターン
# ============================================================

IMPROVEMENT_PATTERNS: List[Pattern] = [
    # --- Tell系 → Think系 への変換 ---
    Pattern(
        regex=r"(.+)(を|について)(教えて|説明して)",
        context_check="推論が必要な文脈",
        suggestion="「考えて」「分析して」への変更を検討",
        reason="推論が必要な文脈では Think 系動詞が効果的",
        mechanism="LLMを推論モードに設定し、ステップバイステップの論証を誘発",
    ),
    
    # --- CoT トリガー欠如 ---
    Pattern(
        regex=r"^(?!.*(?:ステップ|段階|step|順番)).*(?:複雑|難しい|分析|設計|考え).*(?:して|ください)$",
        context_check="複雑なタスク",
        suggestion="「ステップバイステップで」を追加",
        reason="複雑なタスクには明示的な CoT トリガーが効果的",
        mechanism="Chain-of-Thought を誘発し、推論精度を向上",
    ),
    
    # --- 曖昧な指示 ---
    Pattern(
        regex=r"(?:いい感じ|うまく|適当|なんとなく|とりあえず)",
        context_check=None,
        suggestion="具体的な基準や条件を明示",
        reason="曖昧な指示は出力のばらつきを増やす",
        mechanism="LLMは具体的な制約がないと「平均的」な出力に収束する",
    ),
    
    # --- 目標後出し ---
    Pattern(
        regex=r"^(?!.*(?:目標|ゴール|目的|goal)).*(?:して|ください).*(?:ため|ように)$",
        context_check=None,
        suggestion="Goal-First: 目標を先に明示",
        reason="目標が後出しになると LLM の注意が分散",
        mechanism="Goal-First で LLM の注意を目標に固定",
    ),
    
    # --- 問いかけ形式 ---
    Pattern(
        regex=r"(?:もらえる|いただける|できる)\?$",
        context_check=None,
        suggestion="命令形に変更",
        reason="問いかけ形式は「可能性の確認」と解釈されることがある",
        mechanism="命令形は意図を明確にし、期待する行動を直接指示",
    ),
    
    # --- 長すぎる単一指示 ---
    Pattern(
        regex=r".{200,}(?:して|ください)$",
        context_check=None,
        suggestion="複数の指示に分割、または構造化",
        reason="長い単一指示は情報過負荷を招く",
        mechanism="構造化された入力は LLM のパース精度を向上",
    ),
]


# ============================================================
# 技法推奨
# ============================================================

TECHNIQUE_RECOMMENDATIONS = {
    "goal_first": Technique(
        name="Goal-First Declaration",
        detection_pattern=r"(?:目標|ゴール|目的|goal)\s*[:：]",
        situation="目標が後出しになっている発話",
        example="目標: 〜を達成する。そのために〜",
        mechanism="LLMの注意を目標に固定し、関連性の高い出力を誘発",
    ),
    
    "constraint_enum": Technique(
        name="Constraint Enumeration",
        detection_pattern=r"(?:【条件】|【制約】|【要件】|\[条件\]|条件[:：])",
        situation="条件が散在している発話",
        example="【条件】1. 型安全 2. エラーハンドリング 3. テスト容易性",
        mechanism="制約をチェックリスト化し、漏れを防止",
    ),
    
    "cot_trigger": Technique(
        name="CoT Trigger",
        detection_pattern=r"(?:ステップ|段階|step|順番|let's think)",
        situation="複雑な推論を要するタスク",
        example="ステップバイステップで考えてください",
        mechanism="Chain-of-Thought を明示的に誘発",
    ),
    
    "output_format": Technique(
        name="Output Format Specification",
        detection_pattern=r"(?:形式|フォーマット|format)[:：]|\|.*\|",
        situation="構造化された出力が必要な場合",
        example="以下の形式で出力: | 項目 | 評価 | 理由 |",
        mechanism="出力形式を事前に制約し、パース可能性を向上",
    ),
    
    "role_assignment": Technique(
        name="Role Assignment",
        detection_pattern=r"(?:あなたは|として|role|persona)",
        situation="特定の専門性や視点が必要な場合",
        example="あなたはセキュリティ専門家として評価してください",
        mechanism="特定のロールを付与し、関連知識の活性化を促進",
    ),
    
    "few_shot": Technique(
        name="Few-Shot Examples",
        detection_pattern=r"(?:例[:：]|例えば|example|e\.g\.)",
        situation="期待するパターンを示したい場合",
        example="例: 入力「X」→ 出力「Y」",
        mechanism="具体例から出力パターンを学習させる",
    ),
}


# ============================================================
# 拡張用フック
# ============================================================

def register_pattern(pattern: Pattern) -> None:
    """新しい改善パターンを登録"""
    IMPROVEMENT_PATTERNS.append(pattern)


def register_technique(key: str, technique: Technique) -> None:
    """新しい技法推奨を登録"""
    TECHNIQUE_RECOMMENDATIONS[key] = technique
