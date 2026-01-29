#!/usr/bin/env python3
"""
Jules API Client - Hegemonikón H3 Symplokē Layer

Async client for Google Jules API with:
- Session creation and polling
- Batch execution with semaphore control
- Exponential backoff for rate limiting
- Unified HTTP layer with retry support

Refactored based on 58 Jules Synedrion reviews.

Usage:
    client = JulesClient(api_key="YOUR_KEY")
    result = await client.create_and_poll("Fix the bug in utils.py", "sources/github/owner/repo")
"""

import asyncio
import aiohttp
import functools
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# Optional OpenTelemetry support for distributed tracing
try:
    from opentelemetry import trace
    from opentelemetry.propagate import inject
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Configure module logger
logger = logging.getLogger(__name__)


# ============ Exceptions ============

class JulesError(Exception):
    """Base exception for Jules client errors."""
    pass


class RateLimitError(JulesError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class UnknownStateError(JulesError):
    """Raised when API returns an unknown session state."""
    def __init__(self, state: str, session_id: str):
        super().__init__(f"Unknown session state '{state}' for session {session_id}")
        self.state = state
        self.session_id = session_id


# ============ Enums ============

class SessionState(Enum):
    """Jules session states."""
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    IMPLEMENTING = "IMPLEMENTING"
    TESTING = "TESTING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"  # Human approval required
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"  # User or system cancelled
    UNKNOWN = "UNKNOWN"  # Fallback for new/unknown states
    
    @classmethod
    def from_string(cls, state_str: str) -> "SessionState":
        """Parse state string, returning UNKNOWN for unrecognized states.
        
        Warning: Unknown states may indicate new terminal states (e.g., CANCELLED)
        that should stop polling. Check logs for unknown state occurrences.
        """
        try:
            return cls(state_str)
        except ValueError:
            # Log unknown states for monitoring - may be new terminal states
            logger.warning(
                f"Unknown Jules API state encountered: '{state_str}'. "
                f"This may indicate a new terminal state requiring code update."
            )
            return cls.UNKNOWN


# Legacy alias for backwards compatibility
def parse_state(state_str: str) -> SessionState:
    """Deprecated: Use SessionState.from_string() instead."""
    return SessionState.from_string(state_str)


# ============ Data Types ============

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
    error_type: Optional[str] = None  # Preserves exception type for debugging


@dataclass
class JulesResult:
    """
    Result wrapper for batch operations.
    
    Provides explicit success/failure representation instead of
    using empty IDs for failed sessions. See cl-003 review.
    """
    session: JulesSession | None = None
    error: Exception | None = None
    task: dict = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        return self.error is None and self.session is not None
    
    @property
    def is_failed(self) -> bool:
        return not self.is_success


# ============ Retry Decorator ============

def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple = (RateLimitError, aiohttp.ClientError),
):
    """
    Decorator for async functions with exponential backoff retry.
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Multiplier for delay between retries
        initial_delay: Starting delay in seconds
        max_delay: Maximum delay cap
        retryable_exceptions: Tuple of exceptions to retry on
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise
                    
                    # Use retry_after if available
                    if isinstance(e, RateLimitError) and e.retry_after:
                        wait_time = e.retry_after
                    else:
                        wait_time = min(delay, max_delay)
                    
                    logger.warning(
                        f"Retry {attempt + 1}/{max_attempts} for {func.__name__}: "
                        f"{e}. Waiting {wait_time:.1f}s"
                    )
                    await asyncio.sleep(wait_time)
                    delay *= backoff_factor
            
            raise last_exception  # Should not reach here
        return wrapper
    return decorator


# ============ Client ============

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
    
    # Terminal states that stop polling (task finished)
    TERMINAL_STATES = frozenset({SessionState.COMPLETED, SessionState.FAILED, SessionState.CANCELLED})
    
    # Pause states that stop polling (awaiting external action)
    PAUSE_STATES = frozenset({SessionState.WAITING_FOR_APPROVAL})
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        max_concurrent: Optional[int] = None,
    ):
        """
        Initialize Jules client.
        
        Args:
            api_key: Jules API key. If None, reads from JULES_API_KEY env var.
            session: Optional shared aiohttp session for connection reuse.
            max_concurrent: Global concurrency limit. Defaults to MAX_CONCURRENT.
        """
        self.api_key = api_key or os.environ.get("JULES_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set JULES_API_KEY or pass api_key.")
        
        self._headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self._shared_session = session
        self._owned_session: Optional[aiohttp.ClientSession] = None
        
        # Global semaphore for cross-batch rate limiting (th-003 fix)
        self._global_semaphore = asyncio.Semaphore(
            max_concurrent if max_concurrent is not None else self.MAX_CONCURRENT
        )
    
    async def __aenter__(self):
        """Context manager entry - creates pooled session for connection reuse."""
        if self._shared_session is None:
            # Connection pooling: reuse TCP connections (cl-004, as-008 fix)
            connector = aiohttp.TCPConnector(
                limit=self.MAX_CONCURRENT,  # Max concurrent connections
                keepalive_timeout=30,  # Keep connections alive for reuse
                enable_cleanup_closed=True,  # Clean up closed connections
            )
            self._owned_session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes owned session."""
        if self._owned_session:
            await self._owned_session.close()
            self._owned_session = None
    
    @property
    def _session(self) -> aiohttp.ClientSession:
        """Get the active session (shared or owned)."""
        return self._shared_session or self._owned_session or aiohttp.ClientSession()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict | None = None,
    ) -> dict:
        """
        Unified HTTP request handler.
        
        Centralizes error handling and rate limit detection.
        DRY fix per ai-006 review.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: Optional JSON payload
            
        Returns:
            Parsed JSON response
            
        Raises:
            RateLimitError: If rate limited
            aiohttp.ClientResponseError: For other HTTP errors
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Create session if not in context manager
        session = self._shared_session or self._owned_session
        close_after = False
        if session is None:
            session = aiohttp.ClientSession()
            close_after = True
        
        try:
            # Prepare headers with optional trace context
            request_headers = dict(self._headers)
            if OTEL_AVAILABLE:
                # Inject W3C trace context into headers
                inject(request_headers)
            
            async with session.request(
                method, url,
                headers=request_headers,
                json=json
            ) as resp:
                if resp.status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    raise RateLimitError(
                        f"Rate limit exceeded for {endpoint}",
                        retry_after=int(retry_after) if retry_after else None
                    )
                
                # Include response body in error for debugging
                if not resp.ok:
                    body = await resp.text()
                    logger.error(f"API error {resp.status}: {body[:200]}")
                
                resp.raise_for_status()
                return await resp.json()
        finally:
            if close_after:
                await session.close()
    
    @with_retry(max_attempts=3, retryable_exceptions=(RateLimitError, aiohttp.ClientError))
    async def create_session(
        self,
        prompt: str,
        source: str,
        branch: str = "main",
        auto_approve: bool = True,
        automation_mode: str = "AUTO_CREATE_PR",
    ) -> JulesSession:
        """
        Create a new Jules session.
        
        Args:
            prompt: Task description
            source: Repository source (e.g., "sources/github/owner/repo")
            branch: Starting branch (default: main)
            auto_approve: Skip plan approval step
            automation_mode: Automation mode (default: AUTO_CREATE_PR)
            
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
            "automationMode": automation_mode,
            "requirePlanApproval": not auto_approve
        }
        
        data = await self._request("POST", "sessions", json=payload)
        
        return JulesSession(
            id=data["id"],
            name=data["name"],
            state=parse_state(data.get("state", "PLANNING")),
            prompt=prompt,
            source=source
        )
    
    @with_retry(max_attempts=3, retryable_exceptions=(RateLimitError, aiohttp.ClientError))
    async def get_session(self, session_id: str) -> JulesSession:
        """
        Get session status.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            Updated JulesSession
        """
        data = await self._request("GET", f"sessions/{session_id}")
        
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
        poll_interval: int = POLL_INTERVAL,
        fail_on_unknown: bool = True,
    ) -> JulesSession:
        """
        Poll session until completion or timeout.
        
        Args:
            session_id: Session ID to poll
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between polls
            fail_on_unknown: If True, raise on UNKNOWN state (fail-fast)
            
        Returns:
            Final JulesSession state
            
        Raises:
            TimeoutError: If session doesn't complete within timeout
            UnknownStateError: If API returns unknown state (when fail_on_unknown=True)
        """
        start_time = time.time()
        consecutive_unknown = 0
        current_interval = poll_interval  # Backoff reset: track current interval
        
        while time.time() - start_time < timeout:
            try:
                session = await self.get_session(session_id)
                
                # Reset interval on successful request (ai-004 backoff reset fix)
                current_interval = poll_interval
                
                # Terminal state - return immediately
                if session.state in self.TERMINAL_STATES:
                    return session
                
                # Pause state - requires external action (e.g., human approval)
                if session.state in self.PAUSE_STATES:
                    logger.info(
                        f"Session {session_id} paused: {session.state.value}. "
                        f"External action required."
                    )
                    return session
                
                # Unknown state handling (th-001 fix)
                if session.state == SessionState.UNKNOWN:
                    consecutive_unknown += 1
                    logger.warning(f"Session {session_id} in UNKNOWN state ({consecutive_unknown}x)")
                    
                    if consecutive_unknown >= 3 and fail_on_unknown:
                        raise UnknownStateError(
                            state=session.state.value,
                            session_id=session_id
                        )
                else:
                    consecutive_unknown = 0
                    
            except RateLimitError as e:
                # Exponential backoff on rate limit (ai-004 fix)
                if e.retry_after:
                    current_interval = e.retry_after
                else:
                    current_interval = min(current_interval * 2, 60)
                logger.warning(
                    f"Rate limited during poll for {session_id}, "
                    f"backing off to {current_interval}s"
                )
            
            await asyncio.sleep(current_interval)
        
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
        max_concurrent: Optional[int] = None,
        use_global_semaphore: bool = True,
    ) -> list[JulesResult]:
        """
        Execute multiple tasks in parallel with concurrency control.
        
        Returns JulesResult objects with explicit success/failure representation
        instead of using empty IDs (cl-003 fix).
        
        Args:
            tasks: List of dicts with 'prompt', 'source', optional 'branch'
            max_concurrent: Maximum concurrent sessions. If None, uses MAX_CONCURRENT.
                           Ignored if use_global_semaphore=True.
            use_global_semaphore: If True, uses instance-level semaphore for
                                  cross-batch rate limiting (th-003 fix).
            
        Returns:
            List of JulesResult objects
        """
        # Use global semaphore for consistent rate limiting across batches
        if use_global_semaphore:
            semaphore = self._global_semaphore
        else:
            limit = max_concurrent if max_concurrent is not None else self.MAX_CONCURRENT
            semaphore = asyncio.Semaphore(limit)
        
        async def bounded_execute(task: dict) -> JulesResult:
            async with semaphore:
                try:
                    session = await self.create_and_poll(
                        prompt=task["prompt"],
                        source=task["source"],
                        branch=task.get("branch", "main")
                    )
                    return JulesResult(session=session, task=task)
                except Exception as e:
                    # Note: Python 3.8+ handles CancelledError as BaseException,
                    # so it properly propagates and allows cancellation (as-003 review)
                    # Return failed session with traceable ID and error type
                    error_id = f"error-{uuid.uuid4().hex[:8]}"
                    logger.error(f"Task failed [{error_id}]: {type(e).__name__}: {e}")
                    return JulesResult(
                        session=JulesSession(
                            id=error_id,
                            name="",
                            state=SessionState.FAILED,
                            prompt=task["prompt"],
                            source=task["source"],
                            error=str(e),
                            error_type=type(e).__name__
                        ),
                        error=e,
                        task=task
                    )
        
        results = await asyncio.gather(*[
            bounded_execute(task) for task in tasks
        ])
        
        return list(results)
    
    async def synedrion_review(
        self,
        source: str,
        branch: str = "main",
        domains: list[str] | None = None,
        axes: list[str] | None = None,
        progress_callback: Optional[callable] = None,
    ) -> list["JulesResult"]:
        """
        Execute Synedrion v2.1 review with 480 orthogonal perspectives.
        
        Uses the Hegemonikón theorem grid (20 domains × 24 axes) to generate
        structurally orthogonal review perspectives, eliminating redundancy.
        
        Args:
            source: Repository source (e.g., "sources/github/owner/repo")
            branch: Branch to review (default: "main")
            domains: Optional list of domains to filter (e.g., ["Security", "Error"])
            axes: Optional list of axes to filter (e.g., ["O1", "A2"])
            progress_callback: Optional callback(batch_num, total_batches, completed)
        
        Returns:
            List of JulesResult objects from all perspectives
            
        Example:
            # Full 480-perspective review (8 batches)
            results = await client.synedrion_review(
                source="sources/github/owner/repo"
            )
            
            # Filtered review (Security domain, O-series axes = 4 perspectives)
            results = await client.synedrion_review(
                source="sources/github/owner/repo",
                domains=["Security"],
                axes=["O1", "O2", "O3", "O4"]
            )
        """
        # Import perspective matrix
        try:
            from mekhane.ergasterion.synedrion import PerspectiveMatrix
        except ImportError:
            raise ImportError(
                "Synedrion module not found. Ensure mekhane.ergasterion.synedrion is installed."
            )
        
        # Load perspective matrix
        matrix = PerspectiveMatrix.load()
        perspectives = matrix.all_perspectives()
        
        # Apply domain filter
        if domains:
            perspectives = [p for p in perspectives if p.domain_id in domains]
            logger.info(f"Filtered to domains: {domains} ({len(perspectives)} perspectives)")
        
        # Apply axis filter
        if axes:
            perspectives = [p for p in perspectives if p.axis_id in axes]
            logger.info(f"Filtered to axes: {axes} ({len(perspectives)} perspectives)")
        
        if not perspectives:
            logger.warning("No perspectives match the filters. Returning empty results.")
            return []
        
        # Generate tasks from perspectives
        tasks = [
            {
                "prompt": matrix.generate_prompt(p),
                "source": source,
                "branch": branch,
                "perspective_id": p.id,
                "perspective_name": p.name,
                "theorem": p.theorem,
            }
            for p in perspectives
        ]
        
        # Calculate batches
        batch_size = self.MAX_CONCURRENT
        total_batches = (len(tasks) + batch_size - 1) // batch_size
        
        logger.info(
            f"Starting Synedrion v2.1 review: "
            f"{len(tasks)} perspectives, {total_batches} batches"
        )
        
        # Execute and track progress
        all_results = []
        for batch_num, i in enumerate(range(0, len(tasks), batch_size), 1):
            batch_tasks = tasks[i:i + batch_size]
            
            logger.info(f"Batch {batch_num}/{total_batches}: {len(batch_tasks)} perspectives")
            
            batch_results = await self.batch_execute(batch_tasks)
            all_results.extend(batch_results)
            
            # Progress callback if provided
            if progress_callback:
                progress_callback(batch_num, total_batches, len(all_results))
        
        # Log summary
        succeeded = sum(1 for r in all_results if r.is_success)
        failed = len(all_results) - succeeded
        silent = sum(1 for r in all_results if r.is_success and "SILENCE" in str(r.session))
        
        logger.info(
            f"Synedrion review complete: "
            f"{succeeded} succeeded, {failed} failed, {silent} silent (no issues)"
        )
        
        return all_results


# ============ Utilities ============

def mask_api_key(key: str, visible_chars: int = 4) -> str:
    """
    Safely mask API key for display.
    
    Prevents information leakage with short keys (ai-009, th-010 fix).
    
    Args:
        key: API key to mask
        visible_chars: Number of chars to show at start and end
        
    Returns:
        Masked key string
    """
    min_length = visible_chars * 2 + 4  # Need enough chars to mask
    if len(key) < min_length:
        return "***"  # Fully mask short keys
    return f"{key[:visible_chars]}...{key[-visible_chars:]}"


# ============ CLI for testing ============

def main():
    """CLI entry point for testing."""
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
            print("✅ Client initialized")
            print(f"   API Key: {mask_api_key(api_key)}")
            print(f"   Base URL: {client.BASE_URL}")
            print(f"   Max Concurrent: {client.MAX_CONCURRENT}")
            print(f"   Connection Pooling: Enabled (TCPConnector)")
        except Exception as e:
            print(f"❌ Error: {e}")
            exit(1)


if __name__ == "__main__":
    main()
