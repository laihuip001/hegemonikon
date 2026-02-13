# PROOF: [L2/Transport] <- mekhane/ochema/ Ochema CLI
# PURPOSE: Antigravity LS への直接コマンドラインインターフェース
"""
Ochema CLI — Low-level LLM Client

Usage:
    python -m mekhane.ochema.cli [status|chat]
"""

import sys
import argparse
import asyncio
from .antigravity_client import AntigravityClient


# PURPOSE: Ochema メインエントリポイント
async def main():
    """Ochema メインエントリポイント"""
    parser = argparse.ArgumentParser(description="Ochema LLM Client")
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Get LS status")

    # chat
    chat_parser = subparsers.add_parser("chat", help="Chat with LS")
    chat_parser.add_argument("--message", "-m", type=str, required=True, help="Input message")

    args = parser.parse_args()

    client = AntigravityClient()

    if args.command == "status":
        status = client.get_status()
        print(f"Status: {status}")

    elif args.command == "chat":
        print(f"User: {args.message}")
        print("AI: ", end="", flush=True)
        response = client.completion(
            model="antigravity",
            messages=[{"role": "user", "content": args.message}]
        )
        print(response.choices[0]["message"]["content"])

    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
