"""
Jules API Client

Google Jules (Cognitive Agent) API Client.
Based on docs/guides/jules_setup_guide.md
"""

import os
import aiohttp
from typing import Optional, Dict, Any

class JulesClient:
    """Client for interacting with Google Jules API."""

    BASE_URL = "https://julius.googleapis.com/v1alpha"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client.

        Args:
            api_key: Google Jules API Key. If None, reads from JULIUS_API_KEY env var.

        Raises:
            ValueError: If API key is not found.
        """
        self.api_key = api_key or os.environ.get("JULIUS_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in JULIUS_API_KEY environment variable.")

        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def create_session(
        self,
        prompt: str,
        source_context: Optional[Dict[str, Any]] = None,
        automation_mode: str = "AUTO_CREATE_PR"
    ) -> Dict[str, Any]:
        """
        Create a new Jules session.

        Args:
            prompt: The instruction for Jules.
            source_context: Context dictionary (e.g. repo info).
            automation_mode: Mode of operation.

        Returns:
            JSON response from the API.

        Raises:
            aiohttp.ClientError: For network or HTTP errors.
        """
        url = f"{self.BASE_URL}/sessions"
        payload = {
            "prompt": prompt,
            "automationMode": automation_mode
        }
        if source_context:
            payload["sourceContext"] = source_context

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()

    async def list_sessions(self) -> Dict[str, Any]:
        """
        List active sessions.

        Returns:
            JSON response containing session list.

        Raises:
            aiohttp.ClientError: For network or HTTP errors.
        """
        url = f"{self.BASE_URL}/sessions"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
