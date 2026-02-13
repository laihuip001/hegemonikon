# PROOF: [L2/Antigravity] <- mekhane/ochema/ CLI Interface
# PURPOSE: コマンドラインから Antigravity LS を操作する
"""Antigravity CLI Module."""

import sys
import json
import argparse
import time
from typing import Dict, Any

from .antigravity_client import AntigravityClient

def main():
    """CLI メインエントリポイント"""
    parser = argparse.ArgumentParser(description="Antigravity LS CLI")
    subparsers = parser.add_subparsers(dest="command")

    # query コマンド
    cmd_query = subparsers.add_parser("query", help="LLM に質問する")
    cmd_query.add_argument("message", help="質問内容")
    cmd_query.add_argument("--model", "-m", default="default", help="使用するモデル")

    # status コマンド
    subparsers.add_parser("status", help="LS のステータスを確認")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = AntigravityClient()

        if args.command == "query":
            print(f"Asking ({args.model}): {args.message}")
            response = client.ask(args.message, model=args.model)
            print("-" * 40)
            print(f"Model: {response.model}")
            print(f"Text: {response.text}")
            print("-" * 40)

        elif args.command == "status":
            print("Checking status...")
            status = client.get_status()
            print(json.dumps(status, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
