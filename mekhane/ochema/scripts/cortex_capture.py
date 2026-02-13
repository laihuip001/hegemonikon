# PROOF: [L2/Infra] <- mekhane/ochema/ Cortex Capture Script
"""Cortex Capture Script.

Script to capture LLM reasoning steps from Antigravity logs.
"""

import sys
from mekhane.ochema.antigravity_client import AntigravityClient

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.ochema.scripts.cortex_capture <cascade_id>")
        sys.exit(1)

    cascade_id = sys.argv[1]
    client = AntigravityClient()
    info = client.session_info(cascade_id=cascade_id)
    if "error" in info:
        print(f"Error: {info['error']}")
        sys.exit(1)

    print(f"Cortex Steps for {cascade_id}:")
    print(info.get("step_types", {}))

if __name__ == "__main__":
    main()
