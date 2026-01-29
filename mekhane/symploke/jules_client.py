#!/usr/bin/env python3
"""
Jules API Client - Hegemonikón H3 Symplokē Layer

Async client for Google Jules API with:
- Session creation and polling
- Batch execution with semaphore control
- Exponential backoff for rate limiting

Usage:
    client = JulesClient(api_key="YOUR_KEY")
    result = await client.create_and_poll("Fix the bug in utils.py", "sources/github/owner/repo")
"""

import asyncio
import aiohttp
import contextlib
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SessionState(Enum):
    """Jules session states."""
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    IMPLEMENTING = "IMPLEMENTING"
    TESTING = "TESTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"  # Fallback for new/unknown states


def parse_state(state_str: str) -> SessionState:
    """Parse state string, returning UNKNOWN for unrecognized states."""
    try:
        return SessionState(state_str)
    except ValueError:
        return SessionState.UNKNOWN


@dataclass
class JulesSession:
    """Represents a Jules API session."""
    id: str
    name: str
    state: SessionState
    prompt: str
    source: str
    pull_request_url: Optional[str] = None
    error: Optional[str] = None


class JulesClient:
    """
    Async client for Jules API.
    
    Attributes:
        BASE_URL: Jules API base URL
        DEFAULT_TIMEOUT: Default timeout for polling (5 minutes)
        POLL_INTERVAL: Seconds between poll requests
        MAX_CONCURRENT: Maximum concurrent sessions (per Ultra account)
    """
    
    BASE_URL = "https://jules.googleapis.com/v1alpha"
    DEFAULT_TIMEOUT = 300  # 5 minutes
    POLL_INTERVAL = 5  # seconds
    MAX_CONCURRENT = 60  # Ultra plan limit
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Jules client.
        
        Args:
            api_key: Jules API key. If None, reads from JULES_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("JULES_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set JULES_API_KEY or pass api_key.")
        
        self._headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def create_session(
        self,
        prompt: str,
        source: str,
        branch: str = "main",
        auto_approve: bool = True
    ) -> JulesSession:
        """
        Create a new Jules session.
        
        Args:
            prompt: Task description
            source: Repository source (e.g., "sources/github/owner/repo")
            branch: Starting branch (default: main)
            auto_approve: Skip plan approval step
            
        Returns:
            JulesSession with session ID and initial state
        """
        payload = {
            "prompt": prompt,
            "sourceContext": {
                "source": source,
                "githubRepoContext": {
                    "startingBranch": branch
                }
            },
            "automationMode": "AUTO_CREATE_PR",
            "requirePlanApproval": not auto_approve
        }
        
        session_ctx = contextlib.nullcontext(self._session) if (self._session and not self._session.closed) else aiohttp.ClientSession()

        async with session_ctx as session:
            async with session.post(
                f"{self.BASE_URL}/sessions",
                headers=self._headers,
                json=payload
            ) as resp:
                if resp.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                resp.raise_for_status()
                data = await resp.json()
                
                return JulesSession(
                    id=data["id"],
                    name=data["name"],
                    state=parse_state(data.get("state", "PLANNING")),
                    prompt=prompt,
                    source=source
                )
    
    async def get_session(self, session_id: str) -> JulesSession:
        """
        Get session status.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            Updated JulesSession
        """
        session_ctx = contextlib.nullcontext(self._session) if (self._session and not self._session.closed) else aiohttp.ClientSession()

        async with session_ctx as session:
            async with session.get(
                f"{self.BASE_URL}/sessions/{session_id}",
                headers=self._headers
            ) as resp:
                if resp.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                resp.raise_for_status()
                data = await resp.json()
                
                # Extract PR URL if available
                pr_url = None
                outputs = data.get("outputs", [])
                if outputs:
                    pr = outputs[0].get("pullRequest", {})
                    pr_url = pr.get("url")
                
                return JulesSession(
                    id=data["id"],
                    name=data["name"],
                    state=parse_state(data.get("state", "PLANNING")),
                    prompt=data.get("prompt", ""),
                    source=data.get("sourceContext", {}).get("source", ""),
                    pull_request_url=pr_url,
                    error=data.get("error")
                )
    
    async def poll_session(
        self,
        session_id: str,
        timeout: int = DEFAULT_TIMEOUT,
        poll_interval: int = POLL_INTERVAL
    ) -> JulesSession:
        """
        Poll session until completion or timeout.
        
        Args:
            session_id: Session ID to poll
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between polls
            
        Returns:
            Final JulesSession state
            
        Raises:
            TimeoutError: If session doesn't complete within timeout
        """
        start_time = time.time()
        backoff = poll_interval
        
        while time.time() - start_time < timeout:
            try:
                session = await self.get_session(session_id)
                
                if session.state == SessionState.UNKNOWN:
                    print(f"Warning: Unknown session state encountered for {session_id}")

                elif session.state in (SessionState.COMPLETED, SessionState.FAILED):
                    return session
                
                # Reset backoff on success before sleeping
                backoff = poll_interval
                await asyncio.sleep(backoff)
                
            except (RateLimitError, aiohttp.ClientError, asyncio.TimeoutError):
                # Exponential backoff on rate limit or network error
                backoff = min(backoff * 2, 60)
                await asyncio.sleep(backoff)
        
        raise TimeoutError(f"Session {session_id} did not complete within {timeout}s")
    
    async def create_and_poll(
        self,
        prompt: str,
        source: str,
        branch: str = "main",
        timeout: int = DEFAULT_TIMEOUT
    ) -> JulesSession:
        """
        Create session and poll until completion.
        
        Convenience method combining create_session and poll_session.
        
        Args:
            prompt: Task description
            source: Repository source
            branch: Starting branch
            timeout: Maximum wait time
            
        Returns:
            Completed JulesSession
        """
        session = await self.create_session(prompt, source, branch)
        return await self.poll_session(session.id, timeout)
    
    async def batch_execute(
        self,
        tasks: list[dict],
        max_concurrent: int = 30
    ) -> list[JulesSession]:
        """
        Execute multiple tasks in parallel with concurrency control.
        
        Args:
            tasks: List of dicts with 'prompt', 'source', optional 'branch'
            max_concurrent: Maximum concurrent sessions (default: 30)
            
        Returns:
            List of JulesSession results (may include failed sessions)
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_execute(task: dict) -> JulesSession:
            async with semaphore:
                try:
                    return await self.create_and_poll(
                        prompt=task["prompt"],
                        source=task["source"],
                        branch=task.get("branch", "main")
                    )
                except Exception as e:
                    # Return failed session instead of raising
                    return JulesSession(
                        id="",
                        name="",
                        state=SessionState.FAILED,
                        prompt=task["prompt"],
                        source=task["source"],
                        error=str(e)
                    )
        
        results = await asyncio.gather(*[
            bounded_execute(task) for task in tasks
        ])
        
        return list(results)


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


# ============ CLI for testing ============
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Jules API Client")
    parser.add_argument("--test", action="store_true", help="Run connection test")
    parser.add_argument("--key", help="API key (or set JULES_API_KEY)")
    args = parser.parse_args()
    
    if args.test:
        print("Jules Client Test")
        print("-" * 40)
        
        api_key = args.key or os.environ.get("JULES_API_KEY")
        if not api_key:
            print("❌ No API key provided. Set JULES_API_KEY or use --key")
            exit(1)
        
        try:
            client = JulesClient(api_key)
            print(f"✅ Client initialized")
            masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
            print(f"   API Key: {masked_key}")
            print(f"   Base URL: {client.BASE_URL}")
            print(f"   Max Concurrent: {client.MAX_CONCURRENT}")
        except Exception as e:
            print(f"❌ Error: {e}")
            exit(1)
