# PROOF: [L2/Mekhane] <- mekhane/api/routes/ A0->Auto->AddedByCI
#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Chat API — OchemaService 経由の統合 LLM Chat プロキシ
"""
Chat Router — LLM Chat の REST API エンドポイント

エンドポイント:
  POST /chat/send    — メッセージ送信 (SSE ストリーミング)
  POST /chat/cortex  — Cortex generateChat (無課金 Gemini 2MB)
  GET  /chat/models  — 利用可能なモデル一覧 (LS 接続状態含む)

消費者として OchemaService に委譲し、SSE フォーマット変換のみ担う。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from mekhane.ochema.service import (
    AVAILABLE_MODELS,
    CLAUDE_MODEL_MAP,
    OchemaService,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


# --- Models ---


class ChatContent(BaseModel):
    """Single message content."""
    role: str
    parts: list[dict[str, str]]


class ChatRequest(BaseModel):
    """Chat send request."""
    model: str = "gemini-3.1-pro-preview"
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
    model_config_id: str = ""  # empty = server default (Gemini), e.g. "claude-sonnet-4-5"
    tier_id: str = ""  # empty = Gemini default
    include_thinking_summaries: bool = False


GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
CORTEX_CHAT_URL = "https://cloudcode-pa.googleapis.com/v1internal:generateChat"
CORTEX_STREAM_URL = "https://cloudcode-pa.googleapis.com/v1internal:streamGenerateChat"


def _get_api_key() -> str:
    """Gemini API キーを環境変数から取得する。"""
    key = os.getenv("HGK_GEMINI_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    if not key:
        key = os.getenv("VITE_GOOGLE_API_KEY", "")
    return key


# --- Endpoints ---


@router.post("/chat/send")
async def chat_send(req: ChatRequest):
    """Gemini API にプロキシし、SSE をそのままフロントに流す。"""
    # Claude モデルの場合も Cortex generateChat 経由に統合
    if req.model in CLAUDE_MODEL_MAP:
        return await _cortex_chat_from_gemini_format(
            req, model_config_id=CLAUDE_MODEL_MAP[req.model],
        )

    # Cortex モデルの場合は Cortex ルートにリダイレクト
    if req.model == "cortex-chat":
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


async def _claude_chat_from_gemini_format(req: ChatRequest):
    """Gemini 形式の ChatRequest を OchemaService 経由で Claude に送信する。"""
    svc = OchemaService.get()

    if not svc.ls_available:
        raise HTTPException(
            status_code=503,
            detail="Language Server が起動していません。IDE を開いてから再試行してください。",
        )

    # 最後の user メッセージだけを送信 (会話履歴は LS 側で管理)
    user_message = ""
    for content in reversed(req.contents):
        if content.role == "user":
            text = content.parts[0].get("text", "") if content.parts else ""
            user_message = text
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    # システムプロンプトがあれば先頭に付与
    if req.system_instruction:
        sys_parts = req.system_instruction.get("parts", [])
        if sys_parts:
            sys_text = sys_parts[0].get("text", "")
            if sys_text:
                user_message = f"[System] {sys_text}\n\n{user_message}"

    logger.info(
        "Claude Chat request: model=%s msg_len=%d",
        req.model, len(user_message),
    )

    async def stream_claude():
        """OchemaService.ask_async() で Gemini SSE 互換レスポンスを返す。"""
        try:
            response = await svc.ask_async(user_message, model=req.model)

            if not response.text:
                yield 'data: {"error": {"message": "Empty response from Claude", "code": 0}}\n\n'
                return

            # Gemini SSE 互換形式で返す
            gemini_compat = {
                "candidates": [{
                    "content": {
                        "parts": [{"text": response.text}],
                        "role": "model",
                    },
                    "finishReason": "STOP",
                }]
            }
            yield f"data: {json.dumps(gemini_compat)}\n\n"

        except Exception as e:
            logger.error("Claude chat error: %s", e)
            yield f'data: {{"error": {{"message": "Claude error: {str(e)}", "code": 500}}}}\n\n'

    return StreamingResponse(
        stream_claude(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _cortex_chat_from_gemini_format(
    req: ChatRequest,
    model_config_id: str = "",
):
    """Gemini 形式の ChatRequest を Cortex generateChat 形式に変換して実行する。"""
    history: list[dict[str, Any]] = []
    user_message = ""

    for content in req.contents:
        text = content.parts[0].get("text", "") if content.parts else ""
        if content.role == "user":
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
        model_config_id=model_config_id,
    )
    return await cortex_chat(cortex_req)


@router.post("/chat/cortex")
async def cortex_chat(req: CortexChatRequest):
    """Cortex generateChat — 無課金 Gemini 2MB コンテキスト。

    OchemaService の CortexClient を使って認証を委譲。
    """
    svc = OchemaService.get()

    try:
        cortex = svc._get_cortex_client()
        token = cortex._get_token()
        project = cortex._get_project(token)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cortex 認証エラー: {e}",
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
    if req.model_config_id:
        body["model_config_id"] = req.model_config_id

    logger.info(
        "Cortex Chat request: model=%s history=%d, msg_len=%d",
        req.model_config_id or "default", len(req.history), len(req.user_message),
    )

    async def stream_cortex():
        """Cortex streamGenerateChat → Gemini SSE 互換形式に変換して yield。

        streamGenerateChat は JSON 配列 [{markdown: "..."}, ...] を返す。
        各要素を SSE チャンクとしてフロントエンドに送出する。
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    CORTEX_STREAM_URL,
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

                raw = response.text

                # streamGenerateChat returns JSON array or single object
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    yield 'data: {"error": {"message": "Invalid JSON from Cortex", "code": 0}}\n\n'
                    return

                # Normalize to list
                items = data if isinstance(data, list) else [data]
                has_content = False

                for item in items:
                    markdown_text = item.get("markdown", "")
                    if not markdown_text:
                        continue
                    has_content = True
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

                if not has_content:
                    yield 'data: {"error": {"message": "Empty response from Cortex", "code": 0}}\n\n'

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
    """利用可能なモデル一覧を返す。OchemaService に委譲。"""
    svc = OchemaService.get()
    return svc.models()
