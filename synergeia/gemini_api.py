#!/usr/bin/env python3
"""
Gemini API Client for Synergeia
================================

Gemini API を使用して CCL を実行するクライアント。

Usage:
    python gemini_api.py "質問"
    python gemini_api.py "質問" --model gemini-2.0-flash

Environment:
    GOOGLE_API_KEY: API キー
    または ~/.gemini/.env.local に記載
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add venv to path
VENV_PATH = Path("/home/laihuip001/oikos/hegemonikon/.venv/lib/python3.11/site-packages")
sys.path.insert(0, str(VENV_PATH))

import google.generativeai as genai

USAGE_FILE = Path(__file__).parent / "gemini_usage.json"
DEFAULT_MODEL = "gemini-2.0-flash-exp"


def get_api_key() -> str:
    """Get API key from environment or config file."""
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        for path in [
            Path(__file__).parent / ".env.local",
            Path.home() / ".gemini" / ".env.local",
            Path("/home/laihuip001/oikos/.gemini") / ".env.local",
        ]:
            if path.exists():
                content = path.read_text().strip()
                for line in content.split("\n"):
                    if line.startswith("GOOGLE_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"\'')
                        break
                if key:
                    break
    
    if not key:
        raise ValueError("GOOGLE_API_KEY not found")
    return key


def load_usage() -> dict:
    """Load usage data."""
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {"calls": 0, "history": []}


def save_usage(usage: dict):
    """Save usage data."""
    USAGE_FILE.write_text(json.dumps(usage, indent=2, ensure_ascii=False))


def query(prompt: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Execute query via Gemini API.
    """
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    model_instance = genai.GenerativeModel(model)
    
    try:
        response = model_instance.generate_content(prompt)
        answer = response.text
    except Exception as e:
        return {"error": str(e)}
    
    # Update usage
    usage = load_usage()
    usage["calls"] += 1
    usage["history"].append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:100],
        "model": model,
    })
    save_usage(usage)
    
    return {
        "answer": answer,
        "model": model,
        "timestamp": datetime.now().isoformat(),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    prompt = sys.argv[1]
    model = DEFAULT_MODEL
    
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]
    
    result = query(prompt, model)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
