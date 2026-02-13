# PROOF: [L3/Synteleia] <- mekhane/synteleia/dokimasia/ochema_backend.py Ochema Backend
"""
Ochema Backend for Dokimasia

Ochema (L2) を利用して、Dokimasia (L3) のエージェント機能を提供する。
"""
# PURPOSE: mekhane/synteleia/dokimasia/ochema_backend.py
import logging
from typing import Dict, List, Optional

from mekhane.ochema.antigravity_client import AntigravityClient

logger = logging.getLogger(__name__)


# PURPOSE: Ochema Backend Class
class OchemaBackend:
    """Backend utilizing AntigravityClient."""

    def __init__(self):
        self.client = AntigravityClient()

    # PURPOSE: Execute completion
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o"
    ) -> str:
        """Execute simple completion."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat_completion(
            messages=messages,
            model=model
        )

        return response.content

    # PURPOSE: Check logic
    async def check_logic(self, claim: str, context: str) -> bool:
        """Check logical consistency."""
        prompt = f"""
        Context: {context}
        Claim: {claim}

        Is the claim logically consistent with the context?
        Reply with only 'YES' or 'NO'.
        """

        response = await self.complete(prompt, model="gpt-4o")
        return "YES" in response.upper()
