#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Chat API — Gemini API SSE プロキシ + Cortex generateChat (2MB コンテキスト)
"""
Chat Router — LLM Chat の REST API エンドポイント

エンドポイント:
  POST /chat/send    — メッセージ送信 (SSE ストリーミング)
  POST /chat/cortex  — Cortex generateChat (無課金 Gemini 2MB)
  GET  /chat/models  — 利用可能なモデル一覧
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

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


class CortexChatMessage(BaseModel):
    """Cortex generateChat history message."""
    author: int  # 1 = USER, 2 = MODEL
    content: str


class CortexChatRequest(BaseModel):
    """Cortex generateChat request."""
    user_message: str
    history: list[CortexChatMessage] = []
    tier_id: str = ""  # empty = Gemini default
    include_thinking_summaries: bool = False


AVAILABLE_MODELS: dict[str, str] = {
    "gemini-3-pro-preview": "Gemini 3 Pro Preview",
    "gemini-3-flash-preview": "Gemini 3 Flash Preview",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini-2.0-flash": "Gemini 2.0 Flash",
    "cortex-gemini": "Cortex Gemini (無課金 2MB)",
}

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
CORTEX_CHAT_URL = "https://cloudcode-pa.googleapis.com/v1internal:generateChat"
CORTEX_STREAM_URL = "https://cloudcode-pa.googleapis.com/v1internal:streamGenerateChat"


def _get_api_key() -> str:
    """Gemini API キーを環境変数から取得する。"""
    key = os.getenv("HGK_GEMINI_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    if not key:
        key = os.getenv("VITE_GOOGLE_API_KEY", "")
    return key


def _get_cortex_token() -> Optional[str]:
    """CortexClient の _get_token ロジックを再利用してアクセストークンを取得する。"""
    try:
        from mekhane.ochema.cortex_client import CortexClient
        client = CortexClient()
        return client._get_token()
    except Exception as e:
        logger.error("Cortex token acquisition failed: %s", e)
        return None


def _get_cortex_project(token: str) -> Optional[str]:
    """CortexClient の _get_project ロジックを再利用してプロジェクト ID を取得する。"""
    try:
        from mekhane.ochema.cortex_client import CortexClient
        client = CortexClient()
        return client._get_project(token)
    except Exception as e:
        logger.error("Cortex project retrieval failed: %s", e)
        return None


# --- Endpoints ---


@router.post("/chat/send")
async def chat_send(req: ChatRequest):
    """Gemini API にプロキシし、SSE をそのままフロントに流す。"""
    # Cortex モデルの場合は Cortex ルートにリダイレクト
    if req.model == "cortex-gemini":
        return await _cortex_chat_from_gemini_format(req)

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


async def _cortex_chat_from_gemini_format(req: ChatRequest):
    """Gemini 形式の ChatRequest を Cortex generateChat 形式に変換して実行する。"""
    # Gemini contents → Cortex history + user_message に変換
    history: list[dict[str, Any]] = []
    user_message = ""

    for content in req.contents:
        text = content.parts[0].get("text", "") if content.parts else ""
        if content.role == "user":
            # 最後の user メッセージは user_message に
            if user_message:
                history.append({"author": 1, "content": user_message})
            user_message = text
        elif content.role == "model":
            history.append({"author": 2, "content": text})

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    cortex_req = CortexChatRequest(
        user_message=user_message,
        history=[CortexChatMessage(**h) for h in history],
    )
    return await cortex_chat(cortex_req)


@router.post("/chat/cortex")
async def cortex_chat(req: CortexChatRequest):
    """Cortex generateChat — 無課金 Gemini 2MB コンテキスト。"""
    token = _get_cortex_token()
    if not token:
        raise HTTPException(
            status_code=500,
            detail="Cortex OAuth トークンが取得できません。gemini-cli 認証を実行してください。",
        )

    project = _get_cortex_project(token)
    if not project:
        raise HTTPException(
            status_code=500,
            detail="Cortex プロジェクトIDが取得できません。",
        )

    body: dict[str, Any] = {
        "project": project,
        "user_message": req.user_message,
        "history": [h.model_dump() for h in req.history],
        "metadata": {"ideType": "IDE_UNSPECIFIED"},
    }

    if req.tier_id:
        body["tier_id"] = req.tier_id
    if req.include_thinking_summaries:
        body["include_thinking_summaries"] = True

    logger.info(
        "Cortex Chat request: history=%d, msg_len=%d",
        len(req.history), len(req.user_message),
    )

    async def stream_cortex():
        """Cortex generateChat を呼び、Gemini SSE 互換形式に変換して yield する。"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    CORTEX_CHAT_URL,
                    json=body,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code != 200:
                    error_text = response.text[:500]
                    logger.error("Cortex API error %d: %s", response.status_code, error_text)
                    yield f"data: {{\"error\": {{\"message\": \"Cortex API Error {response.status_code}\", \"code\": {response.status_code}}}}}\n\n"
                    return

                data = response.json()
                markdown_text = data.get("markdown", "")

                if not markdown_text:
                    yield 'data: {"error": {"message": "Empty response from Cortex", "code": 0}}\n\n'
                    return

                # Cortex の markdown レスポンスを Gemini SSE 互換形式で返す
                # Frontend の readSSEStream は candidates[0].content.parts[0].text を期待
                gemini_compat = {
                    "candidates": [{
                        "content": {
                            "parts": [{"text": markdown_text}],
                            "role": "model",
                        },
                        "finishReason": "STOP",
                    }]
                }
                yield f"data: {json.dumps(gemini_compat)}\n\n"

            except httpx.TimeoutException:
                yield 'data: {"error": {"message": "Cortex API timeout", "code": 408}}\n\n'
            except Exception as e:
                logger.error("Cortex chat error: %s", e)
                yield f'data: {{"error": {{"message": "Cortex error: {str(e)}", "code": 500}}}}\n\n'

    return StreamingResponse(
        stream_cortex(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/models")
async def chat_models() -> dict[str, Any]:
    """利用可能なモデル一覧を返す。Cortex の認証状態も含む。"""
    cortex_available = False
    try:
        token = _get_cortex_token()
        cortex_available = token is not None
    except Exception:
        pass

    return {
        "models": AVAILABLE_MODELS,
        "default": "gemini-3-pro-preview",
        "cortex_available": cortex_available,
    }
