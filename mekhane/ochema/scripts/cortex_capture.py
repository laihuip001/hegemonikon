# PROOF: [L2/Antigravity] <- mekhane/ochema/ Cortex Capture Script
# PURPOSE: Cortex ステップ情報のキャプチャ
"""Capture Cortex Step Data."""

import argparse
import json
import sys
import time
from typing import Dict, Any, List

from mekhane.ochema.antigravity_client import AntigravityClient

def main():
    """ステップキャプチャメイン処理"""
    parser = argparse.ArgumentParser(description="Capture cortex steps")
    parser.add_argument("cascade_id", help="Cascade ID")
    parser.add_argument("trajectory_id", help="Trajectory ID")
    parser.add_argument("--output", "-o", help="Output JSON file")

    args = parser.parse_args()

    client = AntigravityClient()

    try:
        steps = client._rpc(
            "cortex.v1.CortexService/GetCascadeTrajectorySteps",
            {
                "cascadeId": args.cascade_id,
                "trajectoryId": args.trajectory_id
            }
        )

        output = json.dumps(steps, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Captured {len(steps.get('steps', []))} steps to {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error capturing steps: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
