# PROOF: [L2/Ochema] <- mekhane/ochema/ A0→Ochema CLI
"""
Ochema CLI

Command line interface for Ochema flight systems.
"""

import argparse
from .antigravity_client import AntigravityClient

# PURPOSE: Main CLI entry point
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Ochema Flight Control")
    parser.add_argument("--lift", help="Object ID to lift")
    args = parser.parse_args()

    if args.lift:
        client = AntigravityClient(api_key="demo")
        print(f"Lifting {args.lift}...")

if __name__ == "__main__":
    main()
