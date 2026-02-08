# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
Perplexity API Client (パプ君)
==============================

AI自律使用のためのPerplexity API クライアント。

Usage:
    python perplexity_api.py search "質問"
    python perplexity_api.py search "質問" --model sonar-pro

Environment:
    PERPLEXITY_API_KEY: API キー（必須）

Budget:
    月$5まで自由使用可。使用状況は usage.json に記録。
"""

import os
import sys
import json
import httpx
from pathlib import Path
from datetime import datetime, date

# Configuration
API_URL = "https://api.perplexity.ai/chat/completions"
DEFAULT_MODEL = "sonar-pro"  # sonar: $0.002/1K, sonar-pro: $0.005/1K
USAGE_FILE = Path(__file__).parent / "perplexity_usage.json"
MONTHLY_BUDGET = 5.00  # USD


# PURPOSE: Get API key from environment.
def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("PERPLEXITY_API_KEY")
    if not key:
        # Try reading from common locations
        for path in [
            Path(__file__).parent / ".env.local",  # Script directory first
            Path.home() / ".gemini" / ".env.local",
            Path.home() / ".perplexity_api_key",
            Path(__file__).parent / ".perplexity_api_key",
        ]:
            if path.exists():
                content = path.read_text().strip()
                # Parse .env format
                for line in content.split("\n"):
                    if line.startswith("PERPLEXITY_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip("\"'")
                        break
                if not key and not "=" in content:
                    key = content  # Plain key file
                if key:
                    break

    if not key:
        raise ValueError(
            "PERPLEXITY_API_KEY not found. Set environment variable or create "
            "~/.perplexity_api_key file."
        )
    return key


# PURPOSE: Load usage data.
def load_usage() -> dict:
    """Load usage data."""
    if USAGE_FILE.exists():
        return json.loads(USAGE_FILE.read_text())
    return {
        "month": date.today().strftime("%Y-%m"),
        "total_cost": 0.0,
        "calls": 0,
        "history": [],
    }


# PURPOSE: Save usage data.
def save_usage(usage: dict):
    """Save usage data."""
    USAGE_FILE.write_text(json.dumps(usage, indent=2, ensure_ascii=False))


# PURPOSE: Estimate cost based on token usage.
def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate cost based on token usage."""
    # Pricing: sonar $0.002/1K, sonar-pro $0.005/1K
    rate = 0.005 if "pro" in model else 0.002
    return (input_tokens + output_tokens) / 1000 * rate


# PURPOSE: Execute search query via Perplexity API.
def search(query: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Execute search query via Perplexity API.

    Returns:
        {
            "answer": str,
            "citations": list[str],
            "cost": float,
            "budget_remaining": float
        }
    """
    # Check budget
    usage = load_usage()
    current_month = date.today().strftime("%Y-%m")

    if usage["month"] != current_month:
        # Reset for new month
        usage = {"month": current_month, "total_cost": 0.0, "calls": 0, "history": []}

    if usage["total_cost"] >= MONTHLY_BUDGET:
        return {
            "error": f"Monthly budget exhausted (${MONTHLY_BUDGET:.2f})",
            "budget_remaining": 0.0,
        }

    # Make API call
    api_key = get_api_key()

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {"model": model, "messages": [{"role": "user", "content": query}]}

    try:
        # タイムアウト設定: 全体5分、読み取り3分
        timeout = httpx.Timeout(300.0, read=180.0, connect=30.0)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException as e:
        return {"error": f"Timeout: {e}"}
    except httpx.HTTPError as e:
        return {"error": f"API error: {e}"}

    # Extract answer and citations
    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    citations = data.get("citations", [])

    # Calculate cost
    input_tokens = data.get("usage", {}).get("prompt_tokens", 0)
    output_tokens = data.get("usage", {}).get("completion_tokens", 0)
    cost = estimate_cost(input_tokens, output_tokens, model)

    # Update usage
    usage["total_cost"] += cost
    usage["calls"] += 1
    usage["history"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],  # Truncate for storage
            "cost": cost,
            "tokens": {"input": input_tokens, "output": output_tokens},
        }
    )
    save_usage(usage)

    return {
        "answer": answer,
        "citations": citations,
        "cost": cost,
        "budget_remaining": MONTHLY_BUDGET - usage["total_cost"],
        "total_spent": usage["total_cost"],
        "calls_this_month": usage["calls"],
    }


# PURPOSE: Show current usage statistics.
def show_usage() -> dict:
    """Show current usage statistics."""
    usage = load_usage()
    return {
        "month": usage["month"],
        "total_spent": usage["total_cost"],
        "budget_remaining": MONTHLY_BUDGET - usage["total_cost"],
        "calls": usage["calls"],
        "recent_calls": usage["history"][-5:] if usage["history"] else [],
    }


# PURPOSE: CLI エントリポイント — データパイプラインの直接実行
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "search":
        if len(sys.argv) < 3:
            print('Usage: perplexity_api.py search "query"')
            sys.exit(1)

        query = sys.argv[2]
        model = DEFAULT_MODEL

        if "--model" in sys.argv:
            idx = sys.argv.index("--model")
            if idx + 1 < len(sys.argv):
                model = sys.argv[idx + 1]

        result = search(query, model)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "usage":
        result = show_usage()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
