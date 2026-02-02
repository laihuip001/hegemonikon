# PROOF: [L2/インフラ] <- mekhane/poiema/flow/ O4→創造機能が必要
"""
Noēsis Client — O1 Noēsis Instantiation (API Layer)

Philosophical Reference:
    O1 Noēsis (認識): 深い理解、本質把握

Design Principle:
    外部AI (Gemini) との接続層
    = Hegemonikón の認識能力を外部AIに委譲

Original: Flow AI v5.0 GeminiClient
Recast: Hegemonikón O1 Noēsis vocabulary
"""

import os
import logging
from typing import Dict, Optional, Generator

logger = logging.getLogger("noesis_client")


class NoesisClient:
    """
    O1 Noēsis の外部接続層: AI認識の委譲

    Philosophical Reference:
        Noēsis (νόησις) = 「純粋思考」「直観的認識」
        外部AIの認識能力を借りて処理を行う

    Design Principle:
        Hegemonikón 自身は認識を持たず、
        外部AI（Gemini等）に認識を委譲する
    """

    def __init__(self, settings: Dict = None):
        """
        Initialize NoesisClient

        Args:
            settings: Configuration with GEMINI_API_KEY, MODEL_FAST, MODEL_SMART
        """
        self.settings = settings or {
            "GEMINI_API_KEY": "",
            "MODEL_FAST": "gemini-2.0-flash-exp",
            "MODEL_SMART": "gemini-2.0-pro-exp",
        }
        self.client = None
        self._configure()

    def _configure(self):
        """
        API設定

        Philosophical Reference:
            外部認識源との接続を確立
        """
        env_key = os.environ.get("GEMINI_API_KEY", "").strip()
        conf_key = self.settings.get("GEMINI_API_KEY", "").strip()

        api_key = env_key or conf_key

        if api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=api_key)
                logger.info("O1 Noēsis: External cognition source configured")
            except ImportError:
                logger.warning("O1 Noēsis: google-genai not installed")
        else:
            logger.warning("O1 Noēsis: API Key not configured")

    @property
    def is_configured(self) -> bool:
        """外部認識源が利用可能か"""
        return self.client is not None

    async def generate_content(
        self, text: str, config: Dict, model: Optional[str] = None
    ) -> Dict:
        """
        O1 Noēsis 核心機能: 外部認識の取得

        Philosophical Reference:
            外部AIに「認識」を委譲し、結果を受け取る

        Args:
            text: 入力テキスト
            config: システムプロンプト等の設定
            model: 使用するモデル

        Returns:
            Dict with success, result, error, blocked_reason
        """
        if not self.is_configured:
            return {
                "success": False,
                "result": "",
                "error": "noesis_not_configured",
                "blocked_reason": "外部認識源（API）が設定されていません",
            }

        try:
            from google.genai import types

            target_model = model or self.settings.get(
                "MODEL_FAST", "gemini-2.0-flash-exp"
            )
            prompt = f"{config.get('system', '')}\n\n[Input]\n{text}"

            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=config.get("params", {}).get("temperature", 0.3)
                ),
            )

            # Safety Check (A2 Epochē 連携)
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, "finish_reason"):
                    if candidate.finish_reason == "SAFETY":
                        blocked_categories = []
                        if hasattr(candidate, "safety_ratings"):
                            for rating in candidate.safety_ratings:
                                if rating.blocked:
                                    blocked_categories.append(rating.category)
                        return {
                            "success": False,
                            "result": "",
                            "error": "noesis_safety_blocked",
                            "blocked_reason": f"Safety filter: {blocked_categories}",
                        }

            result_text = response.text.strip() if response.text else ""
            return {
                "success": True,
                "result": result_text,
                "error": None,
                "blocked_reason": None,
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"O1 Noēsis Error: {error_msg}")
            return {
                "success": False,
                "result": "",
                "error": "noesis_error",
                "blocked_reason": error_msg,
            }

    def generate_content_stream(
        self, text: str, config: Dict
    ) -> Generator[str, None, None]:
        """
        ストリーミング生成

        Philosophical Reference:
            認識の段階的な顕現
        """
        if not self.is_configured:
            yield "Error: 外部認識源が設定されていません"
            return

        try:
            from google.genai import types

            model = self.settings.get("MODEL_FAST", "gemini-2.0-flash-exp")
            prompt = f"{config.get('system', '')}\n\n[Input]\n{text}"

            for chunk in self.client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=config.get("params", {}).get("temperature", 0.3)
                ),
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            yield f"Error: {str(e)}"


# Backward compatibility aliases
GeminiClient = NoesisClient

# Singleton instance
_default_client = None


def _get_client() -> NoesisClient:
    global _default_client
    if _default_client is None:
        _default_client = NoesisClient()
    return _default_client


def is_api_configured() -> bool:
    return _get_client().is_configured


async def execute_gemini(text: str, config: Dict, model: str = None) -> Dict:
    """Backward compatibility function"""
    return await _get_client().generate_content(text, config, model)


def execute_gemini_stream(text: str, config: Dict) -> Generator[str, None, None]:
    """Backward compatibility function"""
    return _get_client().generate_content_stream(text, config)
