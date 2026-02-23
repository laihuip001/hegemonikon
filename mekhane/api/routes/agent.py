#!/usr/bin/env python3
# PROOF: [L2/PoC] <- mekhane/api/routes/agent.py
# PURPOSE: Phase 5 Self-Modification PoC Agent API
"""
Agent Routes — Self-Modification PoC

Endpoints:
  POST /agent/ask     — Agent に変更を依頼 (Proposal 生成)
  POST /agent/approve — Proposal を承認して適用
"""

from __future__ import annotations

import logging
import uuid
import json
from typing import Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from mekhane.ochema.cortex_client import CortexClient
from mekhane.ochema.tools import execute_tool as exec_std_tool

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])

# --- In-Memory Storage ---
PROPOSALS: dict[str, dict[str, Any]] = {}

# --- Models ---

class AskRequest(BaseModel):
    prompt: str
    dry_run: bool = True

class ApproveRequest(BaseModel):
    proposal_id: str

class AskResponse(BaseModel):
    text: str
    proposal_id: Optional[str] = None
    diff: Optional[str] = None

# --- Tool Definitions ---

PROPOSE_TOOL = {
    "name": "propose_edit",
    "description": "Propose a modification to a file. Returns a proposal ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target file path"},
            "content": {"type": "string", "description": "New file content"},
            "diff_summary": {"type": "string", "description": "Description of changes"}
        },
        "required": ["path", "content"]
    },
}

READ_FILE_TOOL = {
    "name": "read_file",
    "description": "Read file content.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {"type": "string"}
        },
        "required": ["path"]
    }
}

# --- Helper ---

def _execute_agent_loop(client: CortexClient, prompt: str) -> tuple[str, Optional[str]]:
    """Custom agent loop handling propose_edit."""
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    tools = [PROPOSE_TOOL, READ_FILE_TOOL]

    proposal_id = None
    final_text = ""

    for _ in range(5): # Max 5 turns
        # 1. Call LLM
        req = client._build_request(
            contents=messages,
            model=client.model,
            tools=tools
        )
        # Note: _call_api is internal, but we need raw access or use ask_with_tools logic
        # We'll use _call_api for full control
        # _BASE_URL is module-level private in cortex_client, so we hardcode or import. Hardcoding for PoC.
        base_url = "https://cloudcode-pa.googleapis.com/v1internal"
        resp = client._call_api(f"{base_url}:generateContent", req)

        # 2. Parse response
        llm_resp = client._parse_response(resp)
        final_text = llm_resp.text

        # 3. Check tool calls
        fn_calls = getattr(llm_resp, "function_calls", [])
        if not fn_calls:
            break

        # 4. Execute tools
        tool_outputs = []
        for fc in fn_calls:
            name = fc["name"]
            args = fc["args"]

            if name == "propose_edit":
                pid = str(uuid.uuid4())[:8]
                PROPOSALS[pid] = {
                    "path": args["path"],
                    "content": args["content"],
                    "summary": args.get("diff_summary", "No summary")
                }
                proposal_id = pid
                tool_outputs.append({
                    "functionResponse": {
                        "name": name,
                        "response": {"output": f"Proposal stored. ID: {pid}"}
                    }
                })
            elif name == "read_file":
                # Delegate to standard tool
                res = exec_std_tool(name, args)
                tool_outputs.append({
                    "functionResponse": {
                        "name": name,
                        "response": res
                    }
                })
            else:
                tool_outputs.append({
                    "functionResponse": {
                        "name": name,
                        "response": {"error": f"Unknown tool: {name}"}
                    }
                })

        # 5. Append history
        # Add model response
        if getattr(llm_resp, "raw_model_parts", []):
             messages.append({"role": "model", "parts": llm_resp.raw_model_parts})
        else:
             # Fallback
             messages.append({"role": "model", "parts": [{"functionCall": fc} for fc in fn_calls]})

        # Add tool outputs
        messages.append({"role": "user", "parts": tool_outputs})

    return final_text, proposal_id

# --- Endpoints ---

@router.post("/ask/agent", response_model=AskResponse)
async def ask_agent(req: AskRequest):
    """Ask agent to modify code."""
    try:
        client = CortexClient()
        # Ensure we can use client (mocked in tests)
    except Exception as e:
        raise HTTPException(500, f"Agent init failed: {e}")

    text, pid = _execute_agent_loop(client, req.prompt)

    diff = None
    if pid and pid in PROPOSALS:
        diff = f"Modification for {PROPOSALS[pid]['path']}"

    return AskResponse(
        text=text,
        proposal_id=pid,
        diff=diff
    )

@router.post("/ask/agent/approve")
async def approve_proposal(req: ApproveRequest):
    """Approve and apply a proposal."""
    pid = req.proposal_id
    if pid not in PROPOSALS:
        raise HTTPException(404, f"Proposal {pid} not found")

    prop = PROPOSALS[pid]
    path = Path(prop["path"]).resolve()

    # Security check (simple)
    if "serve.py" not in str(path): # Limit scope for PoC
        raise HTTPException(403, "Access denied: Can only modify serve.py in PoC")

    try:
        path.write_text(prop["content"], encoding="utf-8")
        del PROPOSALS[pid]
        return {"status": "applied", "path": str(path)}
    except Exception as e:
        raise HTTPException(500, f"Apply failed: {e}")
