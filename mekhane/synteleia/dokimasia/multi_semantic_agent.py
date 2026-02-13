# PROOF: [L2/Stathmos] <- mekhane/synteleia/dokimasia/multi_semantic_agent.py
# PURPOSE: マルチエージェントによる意味論的検証 (Dokimasia)
"""
Dokimasia Multi-Semantic Agent — 意味論的検証エージェント

複数の LLM エージェント (Prover, Devil's Advocate, Judge) を協調させ、
命題やコードの意味論的正確性を検証する。
"""

from dataclasses import dataclass
from typing import List, Optional

from mekhane.ochema.antigravity_client import AntigravityClient


# PURPOSE: [L2-auto] 検証リクエスト
@dataclass
class VerificationRequest:
    """検証リクエスト"""
    proposition: str
    context: str = ""
    depth: int = 1


# PURPOSE: [L2-auto] 検証結果
@dataclass
class VerificationResult:
    """検証結果"""
    verified: bool
    confidence: float
    reasoning: str
    dissent: Optional[str] = None


# PURPOSE: [L2-auto] マルチエージェント検証を実行する
class MultiSemanticAgent:
    """マルチエージェント検証を実行する"""

    def __init__(self):
        self.client = AntigravityClient()

    # PURPOSE: [L2-auto] 命題を検証する
    def verify(self, request: VerificationRequest) -> VerificationResult:
        """命題を検証する

        1. Prover: 命題を支持する論証を構築
        2. Advocate: 反証を試みる
        3. Judge: 両者を比較し判定する
        """
        # Step 1: Prover
        prover_prompt = f"""
        PROPOSITION: {request.proposition}
        CONTEXT: {request.context}

        As a Prover, construct a rigorous proof or argument supporting this proposition.
        Focus on logical consistency and evidence.
        """
        proof = self.client.ask(prover_prompt).text

        # Step 2: Devil's Advocate
        advocate_prompt = f"""
        PROPOSITION: {request.proposition}
        PROOF: {proof}

        As a Devil's Advocate, identify weaknesses, edge cases, or counter-arguments to the proof.
        If the proof is solid, acknowledge it but search for subtle flaws.
        """
        dissent = self.client.ask(advocate_prompt).text

        # Step 3: Judge
        judge_prompt = f"""
        PROPOSITION: {request.proposition}
        PROOF: {proof}
        DISSENT: {dissent}

        As an impartial Judge, evaluate the proposition based on the proof and dissent.
        Return a JSON object with:
        - verified: boolean
        - confidence: float (0.0 to 1.0)
        - reasoning: string (summary of the verdict)
        """
        verdict_text = self.client.ask(judge_prompt).text

        # Parse JSON (naive)
        import json
        import re

        try:
            match = re.search(r"\{.*\}", verdict_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return VerificationResult(
                    verified=data.get("verified", False),
                    confidence=data.get("confidence", 0.0),
                    reasoning=data.get("reasoning", "No reasoning provided"),
                    dissent=dissent
                )
        except Exception:
            pass

        return VerificationResult(
            verified=False,
            confidence=0.0,
            reasoning=f"Failed to parse verdict: {verdict_text}",
            dissent=dissent
        )
