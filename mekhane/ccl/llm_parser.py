"""
LLM Parser for CCL v2.0

Layer 1 of the 4-layer fallback system.
Uses Gemini API to convert natural language intent into CCL expressions.
"""

from typing import Optional
from pathlib import Path

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class LLMParser:
    """LLM-based CCL intent parser (Layer 1)."""
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        """
        Initialize the LLM parser.
        
        Args:
            model: Gemini model name
        """
        self.model_name = model
        self.model = None
        self.system_prompt = self._load_system_prompt()
        
        if HAS_GENAI:
            try:
                self.model = genai.GenerativeModel(model)
            except Exception:
                pass
    
    def _load_system_prompt(self) -> str:
        """Load the CCL compiler prompt."""
        prompt_path = Path(__file__).parent / "prompts" / "ccl_compiler.md"
        if prompt_path.exists():
            return prompt_path.read_text()
        return ""
    
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.model is not None
    
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
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Clean up the response
                ccl = response.text.strip()
                # Remove markdown code blocks if present
                if ccl.startswith("```"):
                    lines = ccl.split("\n")
                    ccl = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
                return ccl.strip()
        except Exception:
            pass
            
        return None
