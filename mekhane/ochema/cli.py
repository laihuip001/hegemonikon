#!/usr/bin/env python3
# PROOF: [L2/Ochema] <- mekhane/ochema/cli.py Ochema CLI
"""
Ochema CLI

LLM API への直接アクセスを提供するCLIツール。
...
"""
# PURPOSE: mekhane/ochema/cli.py
import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Optional

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse

# Configure logger
logger = logging.getLogger(__name__)


# PURPOSE: Parse arguments
def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ochema CLI")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # status command
    status_parser = subparsers.add_parser("status", help="Check API status")

    # models command
    models_parser = subparsers.add_parser("models", help="List available models")

    # ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question (single turn)")
    ask_parser.add_argument("prompt", help="Prompt text")
    ask_parser.add_argument("--model", "-m", help="Model name")
    ask_parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature")

    # chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    chat_parser.add_argument("--model", "-m", help="Model name")
    chat_parser.add_argument("--system", "-s", help="System prompt")

    # quota command
    quota_parser = subparsers.add_parser("quota", help="Check quota usage")

    # sessions command
    sessions_parser = subparsers.add_parser("sessions", help="List sessions")

    # episodes command
    episodes_parser = subparsers.add_parser("episodes", help="List episodes")
    episodes_parser.add_argument("--session", "-s", help="Session ID")

    return parser.parse_args()


# PURPOSE: Check API status
async def cmd_status(client: AntigravityClient):
    """Check API status."""
    print("Checking API status...")
    # TODO: Implement actual status check
    print("OK (Mock)")


# PURPOSE: List models
async def cmd_models(client: AntigravityClient):
    """List available models."""
    print("Available models:")
    # TODO: Implement actual models list
    print("- gpt-4o")
    print("- o1")
    print("- o3-mini")
    print("- claude-3-5-sonnet-20241022")
    print("- gemini-2.0-flash-lite")


# PURPOSE: Ask a question
async def cmd_ask(client: AntigravityClient, args):
    """Ask a question."""
    model = args.model or "gpt-4o"
    print(f"Asking {model}...")

    try:
        response = await client.chat_completion(
            messages=[{"role": "user", "content": args.prompt}],
            model=model,
            temperature=args.temperature
        )
        print(f"\nResponse:\n{response.content}")
        print(f"\nUsage: {response.usage}")
    except Exception as e:
        print(f"Error: {e}")


# PURPOSE: Interactive chat
async def cmd_chat(client: AntigravityClient, args):
    """Start interactive chat."""
    model = args.model or "gpt-4o"
    system_prompt = args.system or "You are a helpful AI assistant."

    print(f"Starting chat with {model} (Ctrl+C to exit)")
    print(f"System: {system_prompt}")

    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ("exit", "quit"):
                break

            messages.append({"role": "user", "content": user_input})

            print("AI: ", end="", flush=True)
            response_content = ""

            # Simple non-streaming implementation for now
            response = await client.chat_completion(
                messages=messages,
                model=model
            )
            print(response.content)
            messages.append({"role": "assistant", "content": response.content})

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


# PURPOSE: Check quota
async def cmd_quota(client: AntigravityClient):
    """Check quota usage."""
    print("Quota usage:")
    # TODO: Implement actual quota check
    print("Unknown")


# PURPOSE: List sessions
async def cmd_sessions(client: AntigravityClient):
    """List sessions."""
    print("Sessions:")
    # TODO: Implement actual sessions list
    print("No sessions found.")


# PURPOSE: List episodes
async def cmd_episodes(client: AntigravityClient, args):
    """List episodes."""
    print(f"Episodes for session {args.session}:")
    # TODO: Implement actual episodes list
    print("No episodes found.")


# PURPOSE: Main entry point
async def main():
    """Main entry point."""
    args = parse_args()

    # Initialize client
    # Note: API keys should be in environment variables
    client = AntigravityClient()

    if args.command == "status":
        await cmd_status(client)
    elif args.command == "models":
        await cmd_models(client)
    elif args.command == "ask":
        await cmd_ask(client, args)
    elif args.command == "chat":
        await cmd_chat(client, args)
    elif args.command == "quota":
        await cmd_quota(client)
    elif args.command == "sessions":
        await cmd_sessions(client)
    elif args.command == "episodes":
        await cmd_episodes(client, args)
    else:
        print("No command specified. Use --help for usage.")


if __name__ == "__main__":
    asyncio.run(main())
