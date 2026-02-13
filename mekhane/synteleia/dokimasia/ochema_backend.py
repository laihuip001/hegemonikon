# PROOF: [L2/Infra] <- mekhane/synteleia/dokimasia/ Backend Integration
"""Ochēma Backend Integration.

Bridge between the Ochēma client and the Synteleia Dokimasia framework.
"""

from typing import Any, Dict
from mekhane.ochema.antigravity_client import AntigravityClient

class OchemaBackend:
    """Ochema Backend for Dokimasia tests."""

    def __init__(self):
        self.client = AntigravityClient()

    def execute_prompt(self, prompt: str) -> Dict[str, Any]:
        """Execute a prompt via Antigravity."""
        resp = self.client.ask(prompt)
        return {"text": resp.text, "model": resp.model}
