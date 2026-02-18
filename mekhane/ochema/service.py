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
    # Cortex generateChat (LS不要、全モデル直接アクセス)
    "cortex-chat": "Cortex Chat (LS不要 全モデル直接)",
    # Claude (Cortex chat() 直接 / LS フォールバック)
    "claude-sonnet": "Claude Sonnet 4.5",
    "claude-sonnet-4-5": "Claude Sonnet 4.5",
    "claude-opus": "Claude Opus 4.6",
}

# PURPOSE: Claude モデルのフレンドリー名 → model_config_id マッピング
# generateChat API の model_config_id として使用
CLAUDE_MODEL_MAP: dict[str, str] = {
    "claude-sonnet": "claude-sonnet-4-5",
    "claude-sonnet-4-5": "claude-sonnet-4-5",
    "claude-opus": "claude-opus-4-6",
    # LS proto enum → model_config_id (互換性維持)
    "MODEL_CLAUDE_4_5_SONNET_THINKING": "claude-sonnet-4-5",
    "MODEL_PLACEHOLDER_M26": "claude-opus-4-6",
}

# PURPOSE: LS proto 形式のモデル名セット (LS フォールバック用)
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
        self._cortex_clients: dict[str, Any] = {}  # account -> CortexClient
        self._ls_init_attempted = False

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

    def _get_cortex_client(self, account: str = "default") -> Any:
        """Get CortexClient for account (lazy, cached per account)."""
        if account in self._cortex_clients:
            return self._cortex_clients[account]

        from mekhane.ochema.cortex_client import CortexClient
        client = CortexClient(model=DEFAULT_MODEL, account=account)
        self._cortex_clients[account] = client
        logger.info("CortexClient initialized (account=%s)", account)
        return client

    # --- Routing ---

    def _is_claude_model(self, model: str) -> bool:
        """Check if model is a Claude/GPT model."""
        return model in CLAUDE_MODEL_MAP or model in _LS_PROTO_MODELS

    def _resolve_model_config_id(self, model: str) -> str:
        """Resolve friendly name to model_config_id for generateChat."""
        return CLAUDE_MODEL_MAP.get(model, model)

    def _resolve_ls_proto_model(self, model: str) -> str:
        """Resolve friendly name to LS proto enum (fallback)."""
        # Reverse map: model_config_id → proto enum
        _REVERSE_MAP = {
            "claude-sonnet-4-5": "MODEL_CLAUDE_4_5_SONNET_THINKING",
            "claude-opus-4-6": "MODEL_PLACEHOLDER_M26",
        }
        config_id = CLAUDE_MODEL_MAP.get(model, model)
        return _REVERSE_MAP.get(config_id, model)

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
        account: str = "default",
    ) -> "LLMResponse":
        """Send a prompt and get a response.

        Routes to the appropriate client based on model name:
        - claude-*, MODEL_* → Cortex chat() 直接 (LS フォールバック)
        - gemini-*, cortex-* → CortexClient generateContent

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
        if self._is_claude_model(model):
            # Primary: Cortex chat() 直接 (LS不要)
            try:
                config_id = self._resolve_model_config_id(model)
                return self._ask_cortex_chat(
                    message, model=config_id, timeout=timeout,
                    account=account,
                )
            except Exception as e:
                logger.warning(
                    "Cortex chat() failed for %s, trying LS: %s", model, e,
                )
                # Fallback: LS 経由
                return self._ask_ls(message, model, timeout=timeout)
        else:
            return self._ask_cortex(
                message, model,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                thinking_budget=thinking_budget,
                timeout=timeout,
                account=account,
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
        account: str = "default",
    ) -> Generator[str, None, None]:
        """Stream a response token by token.

        Routes to:
        - Cortex ask_stream (Gemini models with system_instruction support)
        - Cortex chat_stream (Claude or any generateChat model)

        Yields text chunks as they arrive.
        """
        client = self._get_cortex_client(account)

        if self._is_claude_model(model):
            raise ValueError(
                f"Streaming not supported for Claude models (got '{model}'). "
                "Use ask() instead."
            )
        else:
            # Gemini → Cortex streaming (supports system_instruction etc.)
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

    def models(self, account: str = "default") -> dict[str, Any]:
        """Return all available models with provider status.

        Merges hardcoded AVAILABLE_MODELS with dynamically fetched models (F6).

        Returns:
            {
                "models": {model_id: display_name, ...},
                "default": str,
                "ls_available": bool,
                "cortex_available": bool,
                "dynamic_models": list,
            }
        """
        # Start with hardcoded models
        merged = dict(AVAILABLE_MODELS)

        # Attempt dynamic model discovery (F6)
        dynamic: list[dict[str, Any]] = []
        try:
            client = self._get_cortex_client(account)
            dynamic = client.fetch_available_models()
            for m in dynamic:
                mid = m.get("id", m.get("modelId", ""))
                name = m.get("displayName", mid)
                if mid and mid not in merged:
                    merged[mid] = name
        except Exception as e:
            logger.debug("Dynamic model fetch failed: %s", e)

        return {
            "models": merged,
            "default": DEFAULT_MODEL,
            "ls_available": self.ls_available,
            "cortex_available": self.cortex_available,
            "dynamic_models": dynamic,
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

        # Token cache info (F3)
        from mekhane.ochema.cortex_client import _TOKEN_CACHE, _TOKEN_TTL
        if _TOKEN_CACHE.exists():
            import time
            age = time.time() - _TOKEN_CACHE.stat().st_mtime
            remaining = max(0, _TOKEN_TTL - age)
            result["token_cache"] = {
                "remaining_seconds": int(remaining),
                "remaining_human": f"{int(remaining // 60)}m{int(remaining % 60)}s",
                "expired": remaining <= 0,
            }

        return result

    def quota(self, account: str = "default") -> dict[str, Any]:
        """Return unified quota info from LS and Cortex.

        Includes token health from TokenVault.
        """
        result: dict[str, Any] = {"ls": None, "cortex": None, "token_health": None}

        # LS quota
        ls = self._get_ls_client()
        if ls:
            try:
                result["ls"] = ls.quota_status()
            except Exception as e:
                logger.debug("LS quota error: %s", e)

        # Cortex quota
        try:
            cortex = self._get_cortex_client(account)
            result["cortex"] = cortex.retrieve_quota()
        except Exception as e:
            logger.debug("Cortex quota error: %s", e)

        # Token health (F5)
        try:
            result["token_health"] = cortex.vault.status()  # type: ignore[possibly-undefined]
        except Exception as e:
            logger.debug("Token health error: %s", e)

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
        """Send via AntigravityClient (LS). Fallback for Claude models."""
        from mekhane.ochema.types import LLMResponse

        ls = self._get_ls_client()
        if not ls:
            raise RuntimeError(
                "Language Server が起動していません。"
                "IDE を開いてから再試行してください。"
            )

        proto_model = self._resolve_ls_proto_model(model)
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
        account: str = "default",
    ) -> "LLMResponse":
        """Send via CortexClient (Cortex API direct)."""
        client = self._get_cortex_client(account)
        logger.info("Cortex ask: model=%s account=%s", model, account)
        return client.ask(
            message,
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,
            timeout=timeout,
        )

    # --- Chat API (generateChat) ---

    def chat(
        self,
        message: str,
        model: str = "",
        history: list[dict] | None = None,
        tier_id: str = "",
        include_thinking: bool = True,
        timeout: float = 120.0,
        account: str = "default",
    ) -> "LLMResponse":
        """generateChat API でチャット応答を取得。"""
        client = self._get_cortex_client(account)
        resolved_model = self._resolve_model_config_id(model) if model else model
        logger.info("Cortex chat: model=%s account=%s", resolved_model or "default", account)
        return client.chat(
            message=message,
            model=resolved_model,
            history=history,
            tier_id=tier_id,
            include_thinking=include_thinking,
            timeout=timeout,
        )

    def _ask_cortex_chat(
        self,
        message: str,
        model: str = "",
        timeout: float = 120.0,
        account: str = "default",
    ) -> "LLMResponse":
        """Send via CortexClient.chat() (generateChat API direct)."""
        client = self._get_cortex_client(account)
        logger.info("Cortex chat direct: model=%s account=%s", model or "default", account)
        return client.chat(
            message=message,
            model=model,
            timeout=timeout,
        )

    def start_chat(
        self,
        model: str = "",
        tier_id: str = "",
        include_thinking: bool = True,
        account: str = "default",
    ) -> Any:
        """マルチターン generateChat 会話を開始する。"""
        client = self._get_cortex_client(account)
        resolved_model = self._resolve_model_config_id(model) if model else model
        return client.start_chat(
            model=resolved_model,
            tier_id=tier_id,
            include_thinking=include_thinking,
        )

    def __repr__(self) -> str:
        return (
            f"OchemaService("
            f"ls={'✓' if self._ls_client else '✗'}, "
            f"cortex={'✓' if self._cortex_clients else '✗'})"
        )
