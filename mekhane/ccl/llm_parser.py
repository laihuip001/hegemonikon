# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→llm_parser が担う
"""
LLM Parser for CCL v2.0

Layer 1 of the 4-layer fallback system.
Uses Gemini API (google.genai SDK) to convert natural language intent into CCL expressions.

Migration: google.generativeai -> google.genai (deprecated Nov 2025)
"""

import logging
import os
from typing import Optional
from pathlib import Path

# Configure module logger
logger = logging.getLogger(__name__)

# Try new SDK first, fall back to legacy
try:
    from google import genai
    from google.genai.types import GenerateContentConfig

    HAS_GENAI = True
    USE_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai_legacy

        HAS_GENAI = True
        USE_NEW_SDK = False
    except ImportError:
        HAS_GENAI = False
        USE_NEW_SDK = False


def _get_api_key() -> Optional[str]:
    """Get API key from environment, trying multiple variable names."""
    return (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_GENAI_API_KEY")
    )


class LLMParser:
    """LLM-based CCL intent parser (Layer 1)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """
        Initialize the LLM parser.

        Args:
            model: Gemini model name
        """
        self.model_name = model
        self.client = None
        self.model = None
        self.system_prompt = self._load_system_prompt()

        if HAS_GENAI:
            try:
                if USE_NEW_SDK:
                    # New SDK: google.genai
                    # Try multiple env var names for API key
                    api_key = _get_api_key()
                    if api_key:
                        self.client = genai.Client(api_key=api_key)
                    else:
                        # Fallback: try default auth (ADC/Vertex)
                        self.client = genai.Client()
                else:
                    # Legacy SDK: google.generativeai
                    self.model = genai_legacy.GenerativeModel(model)
            except Exception as e:
                logger.error(f"Failed to initialize LLM client: {e}", exc_info=True)

    def _load_system_prompt(self) -> str:
        """Load the CCL compiler prompt."""
        prompt_path = Path(__file__).parent / "prompts" / "ccl_compiler.md"
        if prompt_path.exists():
            return prompt_path.read_text()
        return ""

    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.client is not None or self.model is not None

    def parse(self, intent: str) -> Optional[str]:
        """
        Convert natural language intent to CCL expression.

        Args:
            intent: Natural language description of desired action

        Returns:
            CCL expression or None if parsing fails
        """
        if not self.is_available():
            return None

        try:
            prompt = f"{self.system_prompt}\n\n## Intent\n{intent}\n\n## Output\nCCL expression only:"

            if USE_NEW_SDK and self.client:
                # New SDK: google.genai
                response = self.client.models.generate_content(
                    model=self.model_name, contents=prompt
                )
                text = response.text if response else None
            elif self.model:
                # Legacy SDK: google.generativeai
                response = self.model.generate_content(prompt)
                text = response.text if response else None
            else:
                return None

            if text:
                # Clean up the response
                ccl = text.strip()
                # Remove markdown code blocks if present
                if ccl.startswith("```"):
                    lines = ccl.split("\n")
                    ccl = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
                return ccl.strip()
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}", exc_info=True)

        return None
