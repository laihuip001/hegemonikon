# PROOF: [L2/インフラ] <- mekhane/ochema/ A0→外部LLM接続→Cortex API 直叩きクライアント
# PURPOSE: Cortex API (cloudcode-pa v1internal) を LS 非経由で呼び出す Python クライアント
"""CortexClient — Gemini API direct access via cloudcode-pa v1internal.

Bypasses the Language Server to call Gemini models directly.
Returns the same LLMResponse type as AntigravityClient for unified interface.

Reference: kernel/doxa/DX-010_ide_hack_cortex_direct_access.md

Usage:
    from mekhane.ochema import CortexClient

    client = CortexClient()
    response = client.ask("Hello")
    print(response.text)

    # Batch for CCL pipeline
    results = client.ask_batch([
        {"prompt": "Analyze...", "model": "gemini-2.5-pro"},
        {"prompt": "Review...", "model": "gemini-3-pro-preview"},
    ])

    # Quota check
    quota = client.retrieve_quota()
"""

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Generator, Optional

from mekhane.ochema.antigravity_client import LLMResponse

logger = logging.getLogger(__name__)

# --- Constants ---

# OAuth credentials loaded from external config (not in source)
# Setup: ~/.config/cortex/oauth.json with client_id + client_secret
# Source of values: gemini-cli oauth2.ts L70-86
_OAUTH_CONFIG = Path.home() / ".config" / "cortex" / "oauth.json"
_CREDS_FILE = Path.home() / ".gemini" / "oauth_creds.json"


def _load_oauth_config() -> tuple[str, str]:
    """Load OAuth client_id and client_secret from external config."""
    if not _OAUTH_CONFIG.exists():
        raise FileNotFoundError(
            f"OAuth 設定ファイルが見つかりません: {_OAUTH_CONFIG}\n"
            "作成方法: mkdir -p ~/.config/cortex && "
            'echo \'{"client_id":"...","client_secret":"..."}\' > ~/.config/cortex/oauth.json'
        )
    data = json.loads(_OAUTH_CONFIG.read_text())
    return data["client_id"], data["client_secret"]
_TOKEN_CACHE = Path("/tmp/.cortex_token_cache")
_TOKEN_TTL = 3300  # 55 minutes (access_token expires in 60 min)

_BASE_URL = "https://cloudcode-pa.googleapis.com/v1internal"
_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Defaults
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 8192
MAX_RETRIES = 3
BACKOFF_BASE = 1.0  # seconds


# --- Exceptions ---


# PURPOSE: Cortex API 固有のエラーを他の例外と区別する
class CortexError(Exception):
    """Cortex API error."""

    pass


# PURPOSE: OAuth 認証の未完了を検出し、ユーザーに gemini-cli 認証を促す
class CortexAuthError(CortexError):
    """Authentication error — gemini-cli OAuth required."""

    pass


# PURPOSE: API レート制限や一時的エラーを区別し、リトライ戦略を適用する
class CortexAPIError(CortexError):
    """API call error with status code."""

    def __init__(self, message: str, status_code: int = 0, response_body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


# --- Client ---


# PURPOSE: Cortex API (cloudcode-pa v1internal) を LS 非経由で呼び出し、
#   AntigravityClient と同一の LLMResponse を返す統一インターフェースを提供する
class CortexClient:
    """Cortex API direct client — bypasses Language Server.

    Provides the same ask() → LLMResponse interface as AntigravityClient,
    enabling transparent model switching between LS-proxied and direct access.

    Key features:
        - Token caching (55 min TTL, shared with cortex.sh)
        - Auto project ID retrieval via loadCodeAssist
        - Retry with exponential backoff
        - Zero external dependencies (urllib.request only)
        - CCL pipeline support via ask_batch()
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        """Initialize with default generation parameters.

        Args:
            model: Default model (gemini-2.0-flash, gemini-2.5-pro,
                   gemini-3-pro-preview, etc.)
            temperature: Default temperature (0.0-2.0)
            max_tokens: Default max output tokens
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._token: Optional[str] = None
        self._project: Optional[str] = None

        # Unset proxy env vars (mitmproxy remnant avoidance)
        for var in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
            os.environ.pop(var, None)

    # --- Public API ---

    # PURPOSE: AntigravityClient.ask() と同一シグネチャで LLM を呼び出し、
    #   呼び出し側が LS 経由か直叩きかを意識しない統一 IF を実現する
    def ask(
        self,
        message: str,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
        timeout: float = 120.0,
    ) -> LLMResponse:
        """Send a prompt and get a response.

        Args:
            message: The prompt text
            model: Model override (default: instance model)
            system_instruction: Optional system prompt
            temperature: Temperature override
            max_tokens: Max output tokens override
            thinking_budget: Thinking budget for extended thinking models
            timeout: Request timeout in seconds

        Returns:
            LLMResponse with text, model, token_usage fields populated
        """
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        request_body = self._build_request(
            contents=[{"role": "user", "parts": [{"text": message}]}],
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,
        )

        response = self._call_api(
            f"{_BASE_URL}:generateContent",
            request_body,
            timeout=timeout,
        )

        return self._parse_response(response)

    # PURPOSE: CCL パイプラインや Specialist Reviews で複数プロンプトを
    #   順次処理し、一括で結果を返す
    def ask_batch(
        self,
        tasks: list[dict[str, Any]],
        default_model: Optional[str] = None,
        default_system_instruction: Optional[str] = None,
        delay: float = 0.5,
    ) -> list[LLMResponse]:
        """Process multiple prompts sequentially.

        Args:
            tasks: List of dicts with 'prompt' (required) and optional
                   'model', 'system_instruction', 'temperature',
                   'max_tokens', 'thinking_budget'
            default_model: Default model for all tasks
            default_system_instruction: Default system instruction
            delay: Delay between requests (rate limit safety)

        Returns:
            List of LLMResponse, one per task
        """
        results: list[LLMResponse] = []
        model = default_model or self.model

        for i, task in enumerate(tasks):
            if i > 0 and delay > 0:
                time.sleep(delay)

            try:
                response = self.ask(
                    message=task["prompt"],
                    model=task.get("model", model),
                    system_instruction=task.get(
                        "system_instruction", default_system_instruction
                    ),
                    temperature=task.get("temperature"),
                    max_tokens=task.get("max_tokens"),
                    thinking_budget=task.get("thinking_budget"),
                )
                results.append(response)
            except CortexError as e:
                logger.error("Batch task %d/%d failed: %s", i + 1, len(tasks), e)
                results.append(
                    LLMResponse(
                        text=f"[ERROR] {e}",
                        model=task.get("model", model),
                    )
                )

        return results

    # PURPOSE: 非同期版の ask() — asyncio イベントループから呼び出し可能
    async def ask_async(
        self,
        message: str,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
        timeout: float = 120.0,
    ) -> LLMResponse:
        """Async version of ask() — runs sync code in thread pool.

        Thread-safe: each call runs in its own thread via ThreadPoolExecutor.

        Args:
            (same as ask())

        Returns:
            LLMResponse
        """
        import asyncio
        import concurrent.futures

        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return await loop.run_in_executor(
                pool,
                lambda: self.ask(
                    message=message,
                    model=model,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    thinking_budget=thinking_budget,
                    timeout=timeout,
                ),
            )

    # PURPOSE: 複数プロンプトを並行処理し、逐次版 ask_batch() 比で大幅高速化する
    async def ask_batch_async(
        self,
        tasks: list[dict[str, Any]],
        default_model: Optional[str] = None,
        default_system_instruction: Optional[str] = None,
        max_concurrency: int = 5,
    ) -> list[LLMResponse]:
        """Process multiple prompts concurrently.

        Uses asyncio.Semaphore for rate-limit-safe concurrency control.
        Default max_concurrency=5 keeps well within Cortex rate limits.

        Args:
            tasks: List of dicts with 'prompt' (required) and optional
                   'model', 'system_instruction', 'temperature',
                   'max_tokens', 'thinking_budget'
            default_model: Default model for all tasks
            default_system_instruction: Default system instruction
            max_concurrency: Max concurrent requests (default: 5)

        Returns:
            List of LLMResponse in same order as tasks
        """
        import asyncio

        model = default_model or self.model
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _run_one(task: dict[str, Any]) -> LLMResponse:
            async with semaphore:
                try:
                    return await self.ask_async(
                        message=task["prompt"],
                        model=task.get("model", model),
                        system_instruction=task.get(
                            "system_instruction", default_system_instruction
                        ),
                        temperature=task.get("temperature"),
                        max_tokens=task.get("max_tokens"),
                        thinking_budget=task.get("thinking_budget"),
                    )
                except CortexError as e:
                    logger.error("Async batch task failed: %s", e)
                    return LLMResponse(
                        text=f"[ERROR] {e}",
                        model=task.get("model", model),
                    )

        return list(await asyncio.gather(*[_run_one(t) for t in tasks]))

    # PURPOSE: ストリーミング応答を yield で返し、対話的 CLI やリアルタイム表示に対応する
    def ask_stream(
        self,
        message: str,
        model: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
        timeout: float = 120.0,
    ) -> Generator[str, None, None]:
        """Stream a response token by token.

        Yields text chunks as they arrive via SSE.

        Args:
            (same as ask())

        Yields:
            str: Text chunks from the response
        """
        model = model or self.model
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens

        request_body = self._build_request(
            contents=[{"role": "user", "parts": [{"text": message}]}],
            model=model,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,
        )

        token = self._get_token()
        project = self._get_project(token)
        request_body["project"] = project

        url = f"{_BASE_URL}:streamGenerateContent?alt=sse"
        data = json.dumps(request_body, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                for line_bytes in resp:
                    line = line_bytes.decode("utf-8").strip()
                    if line.startswith("data: "):
                        try:
                            d = json.loads(line[6:])
                            candidates = (
                                d.get("response", {}).get("candidates", [{}])
                            )
                            for candidate in candidates:
                                parts = (
                                    candidate.get("content", {}).get("parts", [])
                                )
                                for part in parts:
                                    if "text" in part:
                                        yield part["text"]
                        except json.JSONDecodeError:
                            continue
        except urllib.error.HTTPError as e:
            raise CortexAPIError(
                f"Stream failed: {e.code} {e.reason}",
                status_code=e.code,
                response_body=e.read().decode("utf-8", errors="replace"),
            )

    # PURPOSE: プロジェクト情報 (tier, プロジェクト ID) を取得し、
    #   接続確認と設定把握に使う
    def load_code_assist(self) -> dict:
        """Get loadCodeAssist info (project, tier, settings).

        Returns:
            dict with cloudaicompanionProject, currentTier, paidTier, etc.
        """
        token = self._get_token()
        return self._call_api(
            f"{_BASE_URL}:loadCodeAssist",
            {
                "metadata": {
                    "ideType": "IDE_UNSPECIFIED",
                    "platform": "PLATFORM_UNSPECIFIED",
                    "pluginType": "GEMINI",
                }
            },
            token_override=token,
        )

    # PURPOSE: 全モデルの Quota 残量を取得し、モデルルーティング判断の入力とする
    def retrieve_quota(self) -> dict:
        """Get quota info for all model buckets.

        Returns:
            dict with model quotas (12 buckets expected)
        """
        token = self._get_token()
        project = self._get_project(token)
        return self._call_api(
            f"{_BASE_URL}:retrieveUserQuota",
            {"project": project},
            token_override=token,
        )

    # --- Private Methods ---

    # PURPOSE: refresh_token から access_token を取得し、55分 TTL でキャッシュする
    def _get_token(self) -> str:
        """Get access token (cached for 55 min, shared with cortex.sh)."""
        # Check instance cache
        if self._token:
            if _TOKEN_CACHE.exists():
                age = time.time() - _TOKEN_CACHE.stat().st_mtime
                if age < _TOKEN_TTL:
                    return self._token

        # Check file cache
        if _TOKEN_CACHE.exists():
            age = time.time() - _TOKEN_CACHE.stat().st_mtime
            if age < _TOKEN_TTL:
                self._token = _TOKEN_CACHE.read_text().strip()
                return self._token

        # Refresh
        if not _CREDS_FILE.exists():
            raise CortexAuthError(
                "OAuth 認証が必要です。先に: npx @google/gemini-cli --prompt 'hello'"
            )

        try:
            creds = json.loads(_CREDS_FILE.read_text())
            refresh_token = creds["refresh_token"]
        except (json.JSONDecodeError, KeyError) as e:
            raise CortexAuthError(f"oauth_creds.json の解析に失敗: {e}")

        client_id, client_secret = _load_oauth_config()
        data = urllib.parse.urlencode(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
        ).encode("utf-8")

        try:
            req = urllib.request.Request(_TOKEN_URL, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                self._token = result["access_token"]
        except (urllib.error.HTTPError, KeyError, json.JSONDecodeError) as e:
            raise CortexAuthError(f"Token refresh 失敗: {e}")

        # Save cache (shared with cortex.sh)
        _TOKEN_CACHE.write_text(self._token)
        _TOKEN_CACHE.chmod(0o600)
        return self._token

    # PURPOSE: loadCodeAssist で動的にプロジェクト ID を取得・キャッシュし、
    #   generateContent の必須パラメータを自動解決する
    def _get_project(self, token: str) -> str:
        """Get project ID via loadCodeAssist (cached)."""
        if self._project:
            return self._project

        # Check env override
        env_project = os.environ.get("CORTEX_PROJECT")
        if env_project:
            self._project = env_project
            return self._project

        result = self._call_api(
            f"{_BASE_URL}:loadCodeAssist",
            {
                "metadata": {
                    "ideType": "IDE_UNSPECIFIED",
                    "platform": "PLATFORM_UNSPECIFIED",
                    "pluginType": "GEMINI",
                }
            },
            token_override=token,
        )

        project = result.get("cloudaicompanionProject")
        if not project:
            raise CortexError(
                f"loadCodeAssist がプロジェクト ID を返しませんでした: {result}"
            )

        self._project = project
        logger.info("Cortex project: %s", project)
        return self._project

    # PURPOSE: リクエスト JSON を組み立て、オプション (system instruction, thinking) を条件付きで含める
    def _build_request(
        self,
        contents: list[dict],
        model: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        thinking_budget: Optional[int] = None,
    ) -> dict:
        """Build the generateContent request payload."""
        request_inner: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        if system_instruction:
            request_inner["systemInstruction"] = {
                "role": "user",
                "parts": [{"text": system_instruction}],
            }

        if thinking_budget is not None:
            request_inner["generationConfig"]["thinkingConfig"] = {
                "thinkingBudget": thinking_budget
            }

        return {
            "model": model,
            "request": request_inner,
        }

    # PURPOSE: API 呼び出しにリトライ (指数バックオフ) を適用し、一時的エラーに耐性を持たせる
    def _call_api(
        self,
        url: str,
        payload: dict,
        timeout: float = 120.0,
        token_override: Optional[str] = None,
    ) -> dict:
        """Make an API call with retry and error handling.

        Args:
            url: Full API URL
            payload: JSON request body
            timeout: Request timeout
            token_override: Use specific token (skip auto-refresh)

        Returns:
            Parsed JSON response dict
        """
        token = token_override or self._get_token()

        # Inject project if not present and not a loadCodeAssist call
        if "project" not in payload and ":loadCodeAssist" not in url:
            payload["project"] = self._get_project(token)

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                sleep_time = BACKOFF_BASE * (2 ** (attempt - 1))
                logger.info("Retry %d/%d after %.1fs", attempt + 1, MAX_RETRIES, sleep_time)
                time.sleep(sleep_time)

            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                # Check for API-level errors in response body
                if "error" in result:
                    err = result["error"]
                    raise CortexAPIError(
                        f"API error: {json.dumps(err)}",
                        status_code=err.get("code", 0),
                        response_body=json.dumps(result),
                    )

                return result

            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                last_error = CortexAPIError(
                    f"HTTP {e.code}: {e.reason}",
                    status_code=e.code,
                    response_body=body,
                )
                # Don't retry auth errors
                if e.code in (401, 403):
                    # Token might be expired — clear cache and retry once
                    if attempt == 0:
                        self._token = None
                        if _TOKEN_CACHE.exists():
                            _TOKEN_CACHE.unlink()
                        token = self._get_token()
                        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                        continue
                    raise last_error
                # Don't retry 4xx (except 429)
                if 400 <= e.code < 500 and e.code != 429:
                    raise last_error
                logger.warning("API error (attempt %d): %s", attempt + 1, last_error)

            except urllib.error.URLError as e:
                last_error = CortexError(f"Network error: {e.reason}")
                logger.warning("Network error (attempt %d): %s", attempt + 1, e.reason)

        raise last_error or CortexError("All retries exhausted")

    # PURPOSE: Cortex API のレスポンスを LLMResponse に変換し、
    #   AntigravityClient と同一のインターフェースを提供する
    def _parse_response(self, response: dict) -> LLMResponse:
        """Parse Cortex API response into LLMResponse.

        Handles both thinking and non-thinking response formats.
        """
        r = response.get("response", response)

        text_parts: list[str] = []
        thinking_parts: list[str] = []
        model_version = r.get("modelVersion", "")

        for candidate in r.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "text" in part:
                    # Thinking models put thought in a separate part with "thought": true
                    if part.get("thought"):
                        thinking_parts.append(part["text"])
                    else:
                        text_parts.append(part["text"])

        usage = r.get("usageMetadata", {})
        token_usage = {}
        if usage:
            token_usage = {
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
            }

        return LLMResponse(
            text="\n".join(text_parts),
            thinking="\n".join(thinking_parts),
            model=model_version,
            token_usage=token_usage,
        )

    def __repr__(self) -> str:
        return f"CortexClient(model={self.model!r}, project={self._project!r})"


# --- Convenience Functions ---


# PURPOSE: ワンライナーで Gemini API を呼べるヘルパー関数。
#   スクリプトや n8n 統合などの簡易利用向け
def cortex_ask(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_instruction: Optional[str] = None,
    thinking_budget: Optional[int] = None,
) -> str:
    """One-liner convenience function.

    Args:
        prompt: The prompt text
        model: Model name
        system_instruction: Optional system prompt
        thinking_budget: Optional thinking budget

    Returns:
        Response text (string only)
    """
    client = CortexClient(model=model)
    response = client.ask(
        prompt,
        system_instruction=system_instruction,
        thinking_budget=thinking_budget,
    )
    return response.text


# --- CLI ---

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cortex_client.py <prompt>")
        print("       python cortex_client.py --quota")
        print("       python cortex_client.py --info")
        sys.exit(1)

    arg = sys.argv[1]

    client = CortexClient()

    if arg == "--quota":
        import pprint

        pprint.pprint(client.retrieve_quota())
    elif arg == "--info":
        import pprint

        pprint.pprint(client.load_code_assist())
    else:
        prompt = " ".join(sys.argv[1:])
        resp = client.ask(prompt)
        print(resp.text)
        if resp.token_usage:
            print(
                f"\n---\n📊 {resp.token_usage.get('prompt_tokens', '?')} in → "
                f"{resp.token_usage.get('completion_tokens', '?')} out = "
                f"{resp.token_usage.get('total_tokens', '?')} total"
            )
            print(f"📍 model: {resp.model}")
