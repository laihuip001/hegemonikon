#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Chat API — Gemini API への SSE プロキシ
"""
Chat Router — LLM Chat の REST API エンドポイント

エンドポイント:
  POST /chat/send    — メッセージ送信 (SSE ストリーミング)
  GET  /chat/models  — 利用可能なモデル一覧
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


# --- Models ---


class ChatContent(BaseModel):
    """Single message content."""
    role: str
    parts: list[dict[str, str]]


class ChatRequest(BaseModel):
    """Chat send request."""
    model: str = "gemini-3-pro-preview"
    contents: list[ChatContent]
    system_instruction: dict[str, Any] | None = None
    generation_config: dict[str, Any] = Field(
        default_factory=lambda: {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        }
    )


AVAILABLE_MODELS: dict[str, str] = {
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gemini-3-flash-preview": "Gemini 3 Flash Preview",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini-2.0-flash": "Gemini 2.0 Flash",
}

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _get_api_key() -> str:
    """Gemini API キーを環境変数から取得する。"""
    key = os.getenv("HGK_GEMINI_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    if not key:
        # .env.local fallback: VITE_GOOGLE_API_KEY
        key = os.getenv("VITE_GOOGLE_API_KEY", "")
    return key


# --- Endpoints ---


@router.post("/chat/send")
async def chat_send(req: ChatRequest):
    """Gemini API にプロキシし、SSE をそのままフロントに流す。"""
    key = _get_api_key()
    if not key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API キーが設定されていません。HGK_GEMINI_KEY 環境変数を設定してください。",
        )

    if req.model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {req.model}. Available: {list(AVAILABLE_MODELS.keys())}",
        )

    url = f"{GEMINI_API_BASE}/{req.model}:streamGenerateContent?alt=sse&key={key}"

    body: dict[str, Any] = {
        "contents": [c.model_dump() for c in req.contents],
        "generationConfig": req.generation_config,
    }

    if req.system_instruction:
        body["systemInstruction"] = req.system_instruction

    logger.info("Chat request: model=%s, messages=%d", req.model, len(req.contents))

    async def stream_proxy():
        """httpx で Gemini API に接続し、SSE チャンクをそのまま yield する。"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                url,
                json=body,
                headers={"Content-Type": "application/json"},
            ) as resp:
                if resp.status_code != 200:
                    error_text = ""
                    async for chunk in resp.aiter_text():
                        error_text += chunk
                    logger.error("Gemini API error %d: %s", resp.status_code, error_text[:500])
                    # Send error as SSE event
                    yield f"data: {{\"error\": {{\"message\": \"Gemini API Error {resp.status_code}\", \"code\": {resp.status_code}}}}}\n\n"
                    return

                async for chunk in resp.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        stream_proxy(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/models")
async def chat_models() -> dict[str, Any]:
    """利用可能なモデル一覧を返す。"""
    return {
        "models": AVAILABLE_MODELS,
        "default": "gemini-3-pro-preview",
    }
