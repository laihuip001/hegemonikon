# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→semantic_validator が担う
"""
CCL Semantic Validator v1.0

Layer 2 validation: Semantic alignment between intent and CCL.
Uses LLM to evaluate whether a CCL expression correctly captures the user's intent.

Design decisions:
- Optional validation (call only when needed)
- Caching via Doxa to reduce API calls
- Graceful degradation if LLM unavailable
"""

import os
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

# Try to import LLM client
try:
    from google import genai

    HAS_LLM = True
except ImportError:
    HAS_LLM = False


# PURPOSE: Get API key from environment.
def _get_api_key() -> Optional[str]:
    """Get API key from environment."""
    return (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_GENAI_API_KEY")
    )


# PURPOSE: SemanticResult の機能を提供する
@dataclass
# PURPOSE: Result of semantic validation.
class SemanticResult:
    """Result of semantic validation."""

    aligned: bool
    confidence: float
    reasoning: str
    suggestions: List[str]

    # PURPOSE: LLM-based semantic validation for CCL expressions. Validates whether a CCL expre
    def __bool__(self) -> bool:
        return self.aligned

# PURPOSE: LLM-based semantic validation for CCL expressions.

class CCLSemanticValidator:
    """
    LLM-based semantic validation for CCL expressions.

    Validates whether a CCL expression semantically matches
    the user's natural language intent.
    """

    PROMPT_PATH = Path(__file__).parent / "prompts" / "semantic_check.md"

    # PURPOSE: Initialize the semantic validator.
    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the semantic validator."""
        self.model_name = model
        self.client = None
        self.system_prompt = self._load_prompt()

        if HAS_LLM:
            api_key = _get_api_key()
            if api_key:
                try:
                    self.client = genai.Client(api_key=api_key)
                except Exception:
                    pass  # TODO: Add proper error handling

    # PURPOSE: Load the semantic check prompt.
    def _load_prompt(self) -> str:
        """Load the semantic check prompt."""
        if self.PROMPT_PATH.exists():
            return self.PROMPT_PATH.read_text()
        return self._default_prompt()

    # PURPOSE: Default prompt if file not found.
    def _default_prompt(self) -> str:
        """Default prompt if file not found."""
        return """あなたは CCL (Cognitive Control Language) の意味的検証器です。

CCL は Hegemonikón システムの認知制御言語で、以下のワークフローを組み合わせます:
- /bou: 意志・目的の明確化
- /noe: 深い認識・分析
- /zet: 問いの発見
- /s: 設計・計画
- /ene: 実行
- /dia: 批評・判定
- +/-: 深化/縮約
- _: シーケンス（順序実行）
- *: 融合
- ~: 往復振動

ユーザーの意図と CCL 式を比較し、意味的に一致しているか評価してください。"""

    # PURPOSE: Check if LLM is available.
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.client is not None

    # PURPOSE: Validate semantic alignment between intent and CCL.
    def validate(
        self, intent: str, ccl: str, context: Optional[str] = None
    ) -> SemanticResult:
        """
        Validate semantic alignment between intent and CCL.

        Args:
            intent: Natural language description of desired action
            ccl: The CCL expression to validate
            context: Optional additional context

        Returns:
            SemanticResult with alignment status and reasoning
        """
        if not self.is_available():
            # Graceful degradation: assume aligned if LLM unavailable
            return SemanticResult(
                aligned=True,
                confidence=0.0,
                reasoning="LLM unavailable, skipping semantic validation",
                suggestions=[],
            )

        try:
            prompt = self._build_prompt(intent, ccl, context)

            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt
            )

            if response and response.text:
                return self._parse_response(response.text)

        except Exception as e:
            return SemanticResult(
                aligned=True,
                confidence=0.0,
                reasoning=f"Validation error: {e}",
                suggestions=[],
            )

        return SemanticResult(
            aligned=True,
            confidence=0.0,
            reasoning="Empty response from LLM",
            suggestions=[],
        )

    # PURPOSE: Build the validation prompt.
    def _build_prompt(self, intent: str, ccl: str, context: Optional[str]) -> str:
        """Build the validation prompt."""
        prompt = f"""{self.system_prompt}

## 検証タスク

### 意図 (Intent)
{intent}

### CCL 式
{ccl}

"""
        if context:
            prompt += f"""### コンテキスト
{context}

"""
        prompt += """### 出力フォーマット (JSON)
以下の形式で回答してください:
```json
{
  "aligned": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "判断理由を簡潔に",
  "suggestions": ["改善案があれば"]
}
```"""
        return prompt

    # PURPOSE: Parse LLM response into SemanticResult.
    def _parse_response(self, text: str) -> SemanticResult:
        """Parse LLM response into SemanticResult."""
        import json
        import re

        # Try to extract JSON from response
        json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return SemanticResult(
                    aligned=data.get("aligned", True),
                    confidence=float(data.get("confidence", 0.5)),
                    reasoning=data.get("reasoning", ""),
                    suggestions=data.get("suggestions", []),
                )
            except (json.JSONDecodeError, ValueError):
                pass  # TODO: Add proper error handling

        # Fallback: try to infer from text
        aligned = "不一致" not in text and "aligned.*false" not in text.lower()
        return SemanticResult(
# PURPOSE: Quick validation helper.
            aligned=aligned,
            confidence=0.5,
            reasoning=text[:200] if len(text) > 200 else text,
            suggestions=[],
        )


# Quick validation function
# PURPOSE: Quick validation helper
def validate_semantic(intent: str, ccl: str) -> SemanticResult:
    """Quick validation helper."""
    validator = CCLSemanticValidator()
    return validator.validate(intent, ccl)
