# PROOF: [L2/Ochema] <- mekhane/ochema/antigravity_client.py Antigravity Client
"""
Antigravity Client - Unified LLM Interface

サポート:
- OpenAI (GPT-4o, o1, o3-mini)
- Anthropic (Claude 3.5 Sonnet)
- Google (Gemini 2.0 Flash Lite)
- Ollama (Local)

Usage:
    client = AntigravityClient()
    response = await client.chat_completion(...)
"""
# PURPOSE: mekhane/ochema/antigravity_client.py
import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

# Optional dependencies
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configure logger
logger = logging.getLogger(__name__)


# PURPOSE: LLM Response
@dataclass
class LLMResponse:
    """Unified LLM Response."""
    content: str
    role: str = "assistant"
    model: str = "unknown"
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    raw_response: Any = None


# PURPOSE: LS Info
@dataclass
class LSInfo:
    """Latent Space Information."""
    embedding: List[float]
    model: str


# PURPOSE: Antigravity Client
class AntigravityClient:
    """Unified Client for multiple LLM providers."""

    # Default models
    DEFAULT_OPENAI_MODEL = "gpt-4o"
    DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_GOOGLE_MODEL = "gemini-2.0-flash-lite"

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
    ):
        """Initialize client with API keys."""
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.google_api_key = google_api_key or os.environ.get("GOOGLE_API_KEY")

        self._openai_client = None
        self._anthropic_client = None
        # Google client is module-level

    @property
    def openai_client(self):
        """Lazy load OpenAI client."""
        if not self._openai_client and self.openai_api_key:
            if openai:
                self._openai_client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            else:
                logger.warning("openai package not installed")
        return self._openai_client

    @property
    def anthropic_client(self):
        """Lazy load Anthropic client."""
        if not self._anthropic_client and self.anthropic_api_key:
            if anthropic:
                self._anthropic_client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
            else:
                logger.warning("anthropic package not installed")
        return self._anthropic_client

    # PURPOSE: Chat Completion
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute chat completion.

        Args:
            messages: List of message dicts {"role": "...", "content": "..."}
            model: Model name (auto-detect provider)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            LLMResponse
        """
        model = model or self.DEFAULT_OPENAI_MODEL

        if "gpt" in model or "o1" in model or "o3" in model:
            return await self._call_openai(messages, model, temperature, max_tokens, **kwargs)
        elif "claude" in model:
            return await self._call_anthropic(messages, model, temperature, max_tokens, **kwargs)
        elif "gemini" in model:
            return await self._call_google(messages, model, temperature, max_tokens, **kwargs)
        else:
            # Fallback to OpenAI (e.g. for Ollama via compatible API)
            return await self._call_openai(messages, model, temperature, max_tokens, **kwargs)

    # PURPOSE: Call OpenAI
    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Call OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        # o1/o3-mini models don't support temperature
        if "o1" in model or "o3" in model:
            kwargs.pop("temperature", None)
            temperature = 1.0 # Default dummy
        else:
            kwargs["temperature"] = temperature

        if max_tokens:
            kwargs["max_completion_tokens"] = max_tokens

        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

        choice = response.choices[0]
        content = choice.message.content or ""

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

        return LLMResponse(
            content=content,
            role=choice.message.role,
            model=response.model,
            usage=usage,
            finish_reason=choice.finish_reason,
            raw_response=response
        )

    # PURPOSE: Call Anthropic
    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Call Anthropic API."""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        # Extract system message
        system_prompt = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        kwargs["temperature"] = temperature
        kwargs["max_tokens"] = max_tokens or 4096

        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self.anthropic_client.messages.create(
            model=model,
            messages=filtered_messages,
            **kwargs
        )

        content = response.content[0].text

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }

        return LLMResponse(
            content=content,
            role=response.role,
            model=response.model,
            usage=usage,
            finish_reason=response.stop_reason,
            raw_response=response
        )

    # PURPOSE: Call Google
    async def _call_google(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Call Google Gemini API."""
        if not self.google_api_key:
            raise ValueError("Google API key not configured")

        if not genai:
            raise ImportError("google-generativeai package not installed")

        genai.configure(api_key=self.google_api_key)
        gemini = genai.GenerativeModel(model)

        # Convert messages format
        # TODO: Better conversion logic
        history = []
        last_message = ""

        for msg in messages[:-1]:
            role = "user" if msg["role"] in ("user", "system") else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        last_message = messages[-1]["content"]

        chat = gemini.start_chat(history=history)

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )

        response = await chat.send_message_async(
            last_message,
            generation_config=generation_config
        )

        content = response.text

        # Usage info not easily available in standard response object
        usage = {}

        return LLMResponse(
            content=content,
            role="assistant",
            model=model,
            usage=usage,
            finish_reason="stop",
            raw_response=response
        )
