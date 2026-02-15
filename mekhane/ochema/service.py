#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/ochema/ A0→LLMアクセス統合サービス
# PURPOSE: OchemaService — 統一 LLM サービス層。全消費者の唯一のエントリポイント
"""
OchemaService — Unified LLM Service Layer

3つの消費者 (Desktop API / MCP Server / CLI) が
同一インターフェースで LLM にアクセスするためのサービス層。

内部で AntigravityClient (LS経由) と CortexClient (Cortex API 直叩き) を
モデル名に基づいてルーティングする。

Usage:
    from mekhane.ochema.service import OchemaService

    svc = OchemaService.get()
    resp = svc.ask("Hello", model="gemini-2.0-flash")
    print(resp.text)
"""

from __future__ import annotations

import logging
from typing import Any, Generator, Optional

logger = logging.getLogger(__name__)


# --- Constants ---

# PURPOSE: デフォルトモデル (CortexClient 用)
DEFAULT_MODEL = "gemini-2.0-flash"

# PURPOSE: 全プロバイダの利用可能モデル (モデルID → 表示名)
AVAILABLE_MODELS: dict[str, str] = {
    # Gemini (Cortex API 経由)
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gemini-3-flash-preview": "Gemini 3 Flash Preview",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini-2.0-flash": "Gemini 2.0 Flash",
    # Cortex generateChat (無課金枠)
    "cortex-gemini": "Cortex Gemini (無課金 2MB)",
    # Claude (LS 経由)
    "claude-sonnet": "Claude Sonnet 4.5 (LS経由)",
    "claude-opus": "Claude Opus 4.6 (LS経由)",
}

# PURPOSE: Claude モデルのフレンドリー名 → proto enum マッピング
CLAUDE_MODEL_MAP: dict[str, str] = {
    "claude-sonnet": "MODEL_CLAUDE_4_5_SONNET_THINKING",
    "claude-opus": "MODEL_PLACEHOLDER_M26",
}

# PURPOSE: LS proto 形式のモデル名セット (ルーティング判定用)
_LS_PROTO_MODELS = {
    "MODEL_CLAUDE_4_5_SONNET_THINKING",
    "MODEL_PLACEHOLDER_M26",
    "MODEL_GEMINI_2_5_PRO",
    "MODEL_GEMINI_2_5_FLASH",
    "MODEL_GPT_4_1",
}


# --- Service ---


# PURPOSE: 統一 LLM サービス。モデル名に基づくルーティング + シングルトン管理
class OchemaService:
    """Unified LLM Service — routes to AntigravityClient or CortexClient.

    Singleton pattern: use OchemaService.get() to obtain the shared instance.
    """

    _instance: Optional["OchemaService"] = None

    def __init__(self) -> None:
        """Initialize service (use get() for singleton access)."""
        self._ls_client: Any = None
        self._cortex_client: Any = None
        self._ls_init_attempted = False
        self._cortex_init_attempted = False

    @classmethod
    def get(cls) -> "OchemaService":
        """Get the singleton service instance."""
        if cls._instance is None:
            cls._instance = cls()
            logger.info("OchemaService initialized")
        assert cls._instance is not None  # satisfy type checker
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        cls._instance = None

    # --- Client Access (lazy) ---

    def _get_ls_client(self) -> Any:
        """Get AntigravityClient (lazy, cached). Returns None if LS unavailable."""
        if self._ls_client is not None:
            # Quick health check
            try:
                self._ls_client.get_status()
                return self._ls_client
            except Exception:
                self._ls_client = None

        if self._ls_init_attempted:
            return None

        try:
            from mekhane.ochema.antigravity_client import AntigravityClient
            self._ls_client = AntigravityClient()
            logger.info(
                "LS client connected: PID=%s Port=%s",
                self._ls_client.pid, self._ls_client.port,
            )
            return self._ls_client
        except Exception as e:
            logger.debug("LS client unavailable: %s", e)
            self._ls_init_attempted = True
            return None

    def _get_cortex_client(self) -> Any:
        """Get CortexClient (lazy, cached). Raises on auth failure."""
        if self._cortex_client is not None:
            return self._cortex_client

        from mekhane.ochema.cortex_client import CortexClient
        self._cortex_client = CortexClient(model=DEFAULT_MODEL)
        logger.info("CortexClient initialized")
        return self._cortex_client

    # --- Routing ---

    def _is_claude_model(self, model: str) -> bool:
        """Check if model should route to LS (Claude/GPT)."""
        return model in CLAUDE_MODEL_MAP or model in _LS_PROTO_MODELS

    def _resolve_claude_model(self, model: str) -> str:
        """Resolve friendly name to proto enum."""
        return CLAUDE_MODEL_MAP.get(model, model)

    # --- Core API ---

    def ask(
        self,
        message: str,
        model: str = DEFAULT_MODEL,
        *,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
        timeout: float = 120.0,
    ) -> "LLMResponse":
        """Send a prompt and get a response.

        Routes to the appropriate client based on model name:
        - claude-*, MODEL_* → AntigravityClient (LS)
        - gemini-*, cortex-* → CortexClient (Cortex API)

        Args:
            message: The prompt text
            model: Model name (see AVAILABLE_MODELS)
            system_instruction: Optional system prompt (Cortex only)
            temperature: Generation temperature
            max_tokens: Max output tokens
            thinking_budget: Thinking budget (Cortex only)
            timeout: Request timeout in seconds

        Returns:
            LLMResponse with text, thinking, model, token_usage
        """
        from mekhane.ochema.antigravity_client import LLMResponse

        if self._is_claude_model(model):
            return self._ask_ls(message, model, timeout=timeout)
        else:
            return self._ask_cortex(
                message, model,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                thinking_budget=thinking_budget,
                timeout=timeout,
            )

    async def ask_async(
        self,
        message: str,
        model: str = DEFAULT_MODEL,
        **kwargs: Any,
    ) -> "LLMResponse":
        """Async version of ask(). Runs sync code in thread pool."""
        import asyncio
        return await asyncio.to_thread(self.ask, message, model, **kwargs)

    def stream(
        self,
        message: str,
        model: str = DEFAULT_MODEL,
        *,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
        timeout: float = 120.0,
    ) -> Generator[str, None, None]:
        """Stream a response token by token (Cortex only).

        Yields text chunks as they arrive via SSE.

        Raises:
            ValueError: If model routes to LS (streaming not supported)
        """
        if self._is_claude_model(model):
            raise ValueError(
                f"Streaming not supported for LS models ({model}). "
                "Use ask() instead."
            )

        client = self._get_cortex_client()
        yield from client.ask_stream(
            message,
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,
            timeout=timeout,
        )

    # --- Info API ---

    def models(self) -> dict[str, Any]:
        """Return all available models with provider status.

        Returns:
            {
                "models": {model_id: display_name, ...},
                "default": str,
                "ls_available": bool,
                "cortex_available": bool,
            }
        """
        return {
            "models": AVAILABLE_MODELS,
            "default": DEFAULT_MODEL,
            "ls_available": self.ls_available,
            "cortex_available": self.cortex_available,
        }

    def status(self) -> dict[str, Any]:
        """Return connection status for all providers."""
        result: dict[str, Any] = {
            "ls_available": self.ls_available,
            "cortex_available": self.cortex_available,
        }

        ls = self._get_ls_client()
        if ls:
            try:
                status = ls.get_status()
                user_status = status.get("userStatus", {})
                result["ls"] = {
                    "pid": ls.pid,
                    "port": ls.port,
                    "workspace": ls.workspace,
                    "name": user_status.get("name", "N/A"),
                }
            except Exception as e:
                result["ls_error"] = str(e)

        return result

    def quota(self) -> dict[str, Any]:
        """Return unified quota info from LS and Cortex.

        Returns:
            {
                "ls": {...} or None,
                "cortex": {...} or None,
            }
        """
        result: dict[str, Any] = {"ls": None, "cortex": None}

        # LS quota
        ls = self._get_ls_client()
        if ls:
            try:
                result["ls"] = ls.quota_status()
            except Exception as e:
                logger.debug("LS quota error: %s", e)

        # Cortex quota
        try:
            cortex = self._get_cortex_client()
            result["cortex"] = cortex.retrieve_quota()
        except Exception as e:
            logger.debug("Cortex quota error: %s", e)

        return result

    def ls_models(self) -> list[dict[str, Any]]:
        """Return LS model list with quota info. Empty list if unavailable."""
        ls = self._get_ls_client()
        if not ls:
            return []
        try:
            return ls.list_models()
        except Exception:
            return []

    # --- Session API (LS only) ---

    def session_info(self, cascade_id: Optional[str] = None) -> dict[str, Any]:
        """Get session info from LS. Raises if LS unavailable."""
        ls = self._get_ls_client()
        if not ls:
            raise RuntimeError("Language Server is not available")
        return ls.session_info(cascade_id)

    def context_health(self, cascade_id: Optional[str] = None) -> dict[str, Any]:
        """Get context health from LS. Raises if LS unavailable."""
        ls = self._get_ls_client()
        if not ls:
            raise RuntimeError("Language Server is not available")
        return ls.context_health(cascade_id)

    # --- Properties ---

    @property
    def ls_available(self) -> bool:
        """Check if Language Server is reachable."""
        return self._get_ls_client() is not None

    @property
    def cortex_available(self) -> bool:
        """Check if Cortex API is authenticated."""
        try:
            client = self._get_cortex_client()
            client._get_token()
            return True
        except Exception:
            return False

    # --- Internal ---

    def _ask_ls(
        self,
        message: str,
        model: str,
        timeout: float = 120.0,
    ) -> "LLMResponse":
        """Send via AntigravityClient (LS)."""
        from mekhane.ochema.antigravity_client import LLMResponse

        ls = self._get_ls_client()
        if not ls:
            raise RuntimeError(
                "Language Server が起動していません。"
                "IDE を開いてから再試行してください。"
            )

        proto_model = self._resolve_claude_model(model)
        logger.info("LS ask: model=%s proto=%s", model, proto_model)
        return ls.ask(message, model=proto_model, timeout=timeout)

    def _ask_cortex(
        self,
        message: str,
        model: str = DEFAULT_MODEL,
        *,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
        timeout: float = 120.0,
    ) -> "LLMResponse":
        """Send via CortexClient (Cortex API direct)."""
        client = self._get_cortex_client()
        logger.info("Cortex ask: model=%s", model)
        return client.ask(
            message,
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,
            timeout=timeout,
        )

    def __repr__(self) -> str:
        return (
            f"OchemaService("
            f"ls={'✓' if self._ls_client else '✗'}, "
            f"cortex={'✓' if self._cortex_client else '✗'})"
        )
