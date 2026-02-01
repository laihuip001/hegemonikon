#!/usr/bin/env python3
# PROOF: [L2/インフラ]
"""
Claude API Client for Synergeia
================================

Claude API を使用して CCL を実行するクライアント。
Structured Output (output_config.format) をサポート。

Usage:
    python claude_api.py "質問"
    python claude_api.py "質問" --structured

Environment:
    ANTHROPIC_API_KEY: API キー (必須)

Note:
    Structured Output は 2026-01-12 より GA (Claude Sonnet 4.5+)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Type

try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from pydantic import BaseModel
except ImportError:
    print("Error: pydantic package not installed. Run: pip install pydantic")
    sys.exit(1)

USAGE_FILE = Path(__file__).parent / "claude_usage.json"
DEFAULT_MODEL = "claude-sonnet-4-20250514"


def get_api_key() -> str:
    """Get API key from environment or config file."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        for path in [
            Path(__file__).parent / ".env.local",
            Path.home() / ".anthropic" / ".env.local",
            Path("/home/laihuip001/oikos/.claude") / ".env.local",
        ]:
            if path.exists():
                content = path.read_text().strip()
                for line in content.split("\n"):
                    if line.startswith("ANTHROPIC_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip("\"'")
                        break
                if key:
                    break
    
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not found")
    return key


def load_usage() -> dict:
    """Load usage data."""
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {"calls": 0, "history": []}


def save_usage(usage: dict):
    """Save usage data."""
    USAGE_FILE.write_text(json.dumps(usage, indent=2, ensure_ascii=False))


def query(
    prompt: str,
    model: str = DEFAULT_MODEL,
    response_schema: Optional[Type[BaseModel]] = None,
    max_tokens: int = 4096,
    system: str = None,
) -> dict:
    """
    Execute query via Claude API.
    
    Args:
        prompt: The prompt to send
        model: Model name (default: claude-sonnet-4)
        response_schema: Optional Pydantic model for structured output
        max_tokens: Maximum tokens in response
        system: Optional system prompt
    
    Returns:
        dict with answer, model, timestamp, and optionally structured_output
    """
    api_key = get_api_key()
    client = Anthropic(api_key=api_key)
    
    # Build request
    request_params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    
    if system:
        request_params["system"] = system
    
    # Configure structured output if schema provided
    if response_schema:
        schema = response_schema.model_json_schema()
        request_params["output_config"] = {
            "format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_schema.__name__,
                    "schema": schema,
                    "strict": True,
                }
            }
        }
    
    try:
        response = client.messages.create(**request_params)
        
        # Extract text content
        answer = ""
        for block in response.content:
            if hasattr(block, "text"):
                answer = block.text
                break
        
        # Parse structured output if schema was provided
        structured_output = None
        if response_schema and answer:
            try:
                structured_output = json.loads(answer)
            except json.JSONDecodeError:
                pass  # Fall back to raw text
                
    except Exception as e:
        return {"error": str(e)}
    
    # Update usage
    usage = load_usage()
    usage["calls"] += 1
    usage["history"].append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:100],
        "model": model,
        "has_schema": response_schema is not None,
        "input_tokens": getattr(response.usage, "input_tokens", 0),
        "output_tokens": getattr(response.usage, "output_tokens", 0),
    })
    save_usage(usage)
    
    result = {
        "answer": answer,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "usage": {
            "input_tokens": getattr(response.usage, "input_tokens", 0),
            "output_tokens": getattr(response.usage, "output_tokens", 0),
        }
    }
    
    if structured_output:
        result["structured_output"] = structured_output
    
    return result


def query_with_tools(
    prompt: str,
    tools: list[dict],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
    system: str = None,
) -> dict:
    """
    Execute query with tool use (strict mode).
    
    Args:
        prompt: The prompt to send
        tools: List of tool definitions with strict: true
        model: Model name
        max_tokens: Maximum tokens
        system: Optional system prompt
    
    Returns:
        dict with answer, tool_calls, and metadata
    """
    api_key = get_api_key()
    client = Anthropic(api_key=api_key)
    
    request_params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "tools": tools,
    }
    
    if system:
        request_params["system"] = system
    
    try:
        response = client.messages.create(**request_params)
        
        # Extract content
        answer = ""
        tool_calls = []
        
        for block in response.content:
            if hasattr(block, "text"):
                answer = block.text
            elif hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
                
    except Exception as e:
        return {"error": str(e)}
    
    # Update usage
    usage = load_usage()
    usage["calls"] += 1
    usage["history"].append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:100],
        "model": model,
        "has_tools": True,
        "tool_count": len(tool_calls),
    })
    save_usage(usage)
    
    return {
        "answer": answer,
        "tool_calls": tool_calls,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "stop_reason": response.stop_reason,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    prompt = sys.argv[1]
    model = DEFAULT_MODEL
    structured = "--structured" in sys.argv
    
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]
    
    if structured:
        # Simple test schema
        class SimpleResponse(BaseModel):
            answer: str
            confidence: float
            reasoning: str
        
        result = query(prompt, model, response_schema=SimpleResponse)
    else:
        result = query(prompt, model)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
