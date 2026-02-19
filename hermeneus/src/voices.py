# PROOF: [L2/MoT] <- hermeneus/src/ dynamic_voices 閾値制御
"""
Voices — MoT (Mixture-of-Thought) 動的 Voice 選択

確信度に応じて Internal Council の Voice 数を制御する。
SKILL.md の dynamic_voices 定義 (L278-303) のコード実装。

Usage:
    from hermeneus.src.voices import select_voices, format_voices_prompt
    
    voices = select_voices(confidence=45)
    prompt = format_voices_prompt(voices, hypothesis="仮説A")
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Voice:
    """MoT の Individual Voice."""
    name: str
    focus: str
    question: str


# Base voices (常駐 3)
LOGIC = Voice("LOGIC", "論理的整合性・因果推論", "論理には飛躍がないか？ 前提は正しいか？")
EMOTION = Voice("EMOTION", "感情的影響・直感の声", "これは人をどう感じさせるか？ 直感は何を言っているか？")
HISTORY = Voice("HISTORY", "過去のパターン・失敗事例", "以前これを試した時、何が起きたか？")

# Optional voices (条件付き追加)
DOMAIN_EXPERT = Voice(
    "DOMAIN_EXPERT",
    "ドメイン固有知識・先行事例",
    "この分野の専門知識に照らして妥当か？ ベストプラクティスは？",
)
DEVILS_ADVOCATE = Voice(
    "DEVILS_ADVOCATE",
    "意図的反論・見落とし発掘",
    "この結論が間違っているとしたら、なぜか？ 何を見逃しているか？",
)

# Voice registry
ALL_VOICES = {v.name: v for v in [LOGIC, EMOTION, HISTORY, DOMAIN_EXPERT, DEVILS_ADVOCATE]}
BASE_VOICES = [LOGIC, EMOTION, HISTORY]
MAX_VOICES = 5


def select_voices(
    confidence: float,
    all_agree: bool = False,
) -> list[Voice]:
    """確信度とグループ合意に基づいて Voice セットを選択。

    Selection rule (SKILL.md L291-296):
        - 確信度 80%+: base_voices のみ (3)
        - 確信度 50-79%: + DOMAIN_EXPERT (4)
        - 確信度 < 50%: + DOMAIN_EXPERT + DEVILS_ADVOCATE (5)
        - 全 Voice 同意: DEVILS_ADVOCATE 強制追加

    Args:
        confidence: 確信度 (0-100)
        all_agree: 全 base_voices が同意したか (groupthink 検出)

    Returns:
        選択された Voice のリスト (最大 5)
    """
    voices = list(BASE_VOICES)

    if confidence < 80:
        voices.append(DOMAIN_EXPERT)
    if confidence < 50:
        voices.append(DEVILS_ADVOCATE)

    # Groupthink detection: 全員同意 → DEVILS_ADVOCATE 強制
    if all_agree and DEVILS_ADVOCATE not in voices:
        voices.append(DEVILS_ADVOCATE)

    return voices[:MAX_VOICES]


def format_voices_prompt(voices: list[Voice], hypothesis: str = "") -> str:
    """Voice セットを LLM プロンプト用にフォーマット。

    Args:
        voices: 選択された Voice リスト
        hypothesis: 検証対象の仮説 (空なら省略)

    Returns:
        Multi-persona critique 用プロンプト文字列
    """
    lines = ["## Internal Council — Multi-Voice Critique\n"]

    if hypothesis:
        lines.append(f"**検証対象**: {hypothesis}\n")

    lines.append(f"以下の {len(voices)} 名の視点から評価してください:\n")

    for i, v in enumerate(voices, 1):
        lines.append(f"### Voice {i}: {v.name}")
        lines.append(f"**視点**: {v.focus}")
        lines.append(f"**問い**: {v.question}\n")

    lines.append("---")
    lines.append("各 Voice の評価を述べた後、統合的な判断を提示してください。")
    lines.append("Voice 間の対立がある場合は、その対立を明示してください。")

    return "\n".join(lines)
