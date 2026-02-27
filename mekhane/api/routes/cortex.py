# PROOF: [L2/Impl] <- mekhane/api/routes/ Automated fix for CI
from typing import Any, AsyncGenerator

import asyncio
import json
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from mekhane.ochema.cortex_client import CortexClient

logger = logging.getLogger("hegemonikon.api.cortex")

router = APIRouter(prefix="/api/cortex", tags=["Cortex"])

# Singleton client
_client: CortexClient | None = None

def _get_client() -> CortexClient:
    global _client
    if _client is None:
        _client = CortexClient()
    return _client


@router.get("/health")
async def health():
    """Health check for Cortex Proxy."""
    return {"status": "ok", "service": "hgk-desktop-api-cortex"}


@router.post("/ask")
async def ask(request: Request):
    """Simple ask endpoint — non-streaming."""
    body = await request.json()
    message = body.get("message", "")
    model = body.get("model", "gemini-2.5-flash")

    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)

    try:
        client = _get_client()
        result = await asyncio.to_thread(
            client.generate, prompt=message, model=model
        )
        return {"text": result.text, "model": result.model}
    except Exception as e:
        logger.error("Cortex API error (ask): %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/ask/stream")
async def ask_stream(request: Request):
    """SSE streaming endpoint — full parameter control."""
    body = await request.json()
    message = body.get("message", "")
    model = body.get("model", "gemini-2.5-flash")
    system_instruction = body.get("system_instruction")
    temperature = body.get("temperature")
    max_tokens = body.get("max_tokens")
    thinking_budget = body.get("thinking_budget")

    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)

    async def event_generator() -> AsyncGenerator[str, Any]:
        try:
            client = _get_client()
            kwargs = dict(prompt=message, model=model)
            if system_instruction: kwargs["system_instruction"] = system_instruction
            if temperature is not None: kwargs["temperature"] = float(temperature)
            if max_tokens is not None: kwargs["max_tokens"] = int(max_tokens)
            if thinking_budget is not None: kwargs["thinking_budget"] = int(thinking_budget)

            result = await asyncio.to_thread(client.generate, **kwargs)
            # Simulate streaming by chunking the response
            text = result.text or ""
            chunk_size = 20
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                yield f"data: {json.dumps({'text': chunk, 'done': False})}\n\n"
                await asyncio.sleep(0.02)
            yield f"data: {json.dumps({'text': '', 'done': True, 'model': result.model})}\n\n"
        except Exception as e:
            logger.error("Cortex API error (stream): %s", e)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
