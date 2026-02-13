# PROOF: [L2/Transport] <- mekhane/ochema/scripts/ Cortex Capture
# PURPOSE: 現在の LLM (Ochema) の状態をキャプチャし、デバッグログを保存する
"""
Cortex Capture — LLM Debugging Tool

Usage:
    python -m mekhane.ochema.scripts.cortex_capture [--out path]
"""

import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime
from mekhane.ochema.antigravity_client import AntigravityClient


# PURPOSE: Cortex Capture Main
async def main():
    """Cortex Capture Main"""
    parser = argparse.ArgumentParser(description="Capture LLM State")
    parser.add_argument("--out", type=str, default="cortex_dump.json", help="Output file")

    args = parser.parse_args()

    client = AntigravityClient()

    # 状態取得
    print("Capturing Cortex state...")
    status = client.get_status()

    # ダミーチャットで疎通確認
    print("Checking connectivity...")
    try:
        response = client.completion(
            model="ping",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=10
        )
        latency_check = "OK"
    except Exception as e:
        latency_check = f"Error: {e}"

    dump = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "connectivity": latency_check,
        "client_config": {
            "base_url": client.base_url,
            "workspace": client.workspace,
        }
    }

    out_path = Path(args.out)
    with out_path.open("w") as f:
        json.dump(dump, f, indent=2)

    print(f"✅ Cortex state captured to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
