# PROOF: [L2/Ochema] <- mekhane/ochema/ A0→コンテキスト収集→スクリプト
# PURPOSE: Cortex Capture — Antigravity Context を収集するスクリプト
"""Cortex Capture — Collect Antigravity Context.

Usage:
    python -m mekhane.ochema.scripts.cortex_capture <cascade_id>
"""

import argparse
import json
import sys

from mekhane.ochema.antigravity_client import AntigravityClient


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Capture Cortex Context")
    parser.add_argument("cascade_id", help="Cascade ID")
    args = parser.parse_args()

    client = AntigravityClient()

    # Get session info
    info = client.session_info(args.cascade_id)
    if "error" in info:
        print(f"Error: {info['error']}", file=sys.stderr)
        sys.exit(1)

    # Get conversation
    conv = client.session_read(args.cascade_id, full=True)

    result = {
        "info": info,
        "conversation": conv
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
