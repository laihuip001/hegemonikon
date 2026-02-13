# PROOF: [L2/Infra] <- mekhane/anamnesis/ Session Monitoring
"""Session Monitor.

Watches for new Antigravity sessions and triggers indexing.
"""

import time
import logging
from mekhane.ochema.antigravity_client import AntigravityClient

# PURPOSE: [L2-auto] Monitor for new sessions.
def monitor_sessions(interval: int = 60):
    """Monitor for new sessions."""
    client = AntigravityClient()
    seen = set()
    while True:
        info = client.session_info()
        sessions = info.get("sessions", [])
        for s in sessions:
            cid = s.get("cascade_id")
            if cid and cid not in seen:
                logging.info(f"New session detected: {cid}")
                seen.add(cid)
        time.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor_sessions()
