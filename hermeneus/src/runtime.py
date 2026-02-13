# PROOF: [L2/インフラ] <- hermeneus/src/ LMQL 実行ランタイム
"""
Hermēneus Runtime — LMQL プログラムを実行

compile_ccl() の出力を実際の LLM で実行し、
結果を構造化して返す。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
Updated: 2026-02-11 Vertex AI Multi-Model Integration
"""

import os
import re
import json
import time
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pathlib import Path

# .env ファイルから環境変数を読み込む
# PURPOSE: hermeneus/.env から API キーを読み込む
def _load_env():
    """hermeneus/.env から API キーを読み込む"""
    env_paths = [
        Path(__file__).parent.parent / ".env",  # hermeneus/.env
        Path(__file__).parent.parent.parent / ".env",  # hegemonikon/.env
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key not in os.environ:  # 既存の環境変数は上書きしない
                            os.environ[key] = value.strip()

_load_env()


# PURPOSE: [L2-auto] Secret アクセスの一元化 (W08 Secret Sprawl 対策)
def _get_secret(key: str) -> Optional[str]:
    """Secret アクセスの一元化 (W08 Secret Sprawl 対策)
    
    全ての API キー・認証情報はこの関数経由で取得する。
    散在する os.environ.get を排除し、将来的な Secret Manager
    統合のフックポイントとする。
    """
    # TODO: Secret Manager (GCP/AWS) 統合時はここを変更
    return os.environ.get(key)


# PURPOSE: [L2-auto] メモリ内 Circuit Breaker (W06 Cascade Failure 対策)
class _ProviderCircuitBreaker:
    """メモリ内 Circuit Breaker (W06 Cascade Failure 対策)
    
    プロバイダーの連続失敗を追跡し、閾値を超えたら
    一定期間スキップする。全プロバイダー不調時の
    3連試行の無駄を排除。
    """
    
    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self._failures: Dict[str, int] = {}
        self._open_until: Dict[str, float] = {}
        self._threshold = failure_threshold
        self._cooldown = cooldown_seconds
    
    # PURPOSE: [L2-auto] Circuit が開いている (= スキップすべき) か
    def is_open(self, provider: str) -> bool:
        """Circuit が開いている (= スキップすべき) か"""
        until = self._open_until.get(provider, 0)
        if time.time() < until:
            return True
        # cooldown 経過 → リセット
        if provider in self._open_until and time.time() >= until:
            self._failures[provider] = 0
            self._open_until.pop(provider, None)
        return False
    
    # PURPOSE: [L2-auto] 失敗を記録。閾値超過で Circuit を開く
    def record_failure(self, provider: str) -> None:
        """失敗を記録。閾値超過で Circuit を開く"""
        self._failures[provider] = self._failures.get(provider, 0) + 1
        if self._failures[provider] >= self._threshold:
            self._open_until[provider] = time.time() + self._cooldown
    
    # PURPOSE: [L2-auto] 成功で Circuit をリセット
    def record_success(self, provider: str) -> None:
        """成功で Circuit をリセット"""
        self._failures[provider] = 0
        self._open_until.pop(provider, None)


# Module-level circuit breaker instance
_circuit_breaker = _ProviderCircuitBreaker()


# =============================================================================
# Model Registry — 設定駆動のモデルカタログ
# =============================================================================

MODEL_REGISTRY: Dict[str, Dict[str, str]] = {
    # --- Google Gemini (google-genai SDK, API key) ---
    "gemini-3-pro": {
        "provider": "google",
        "model_id": "gemini-3-pro-preview",
    },
    "gemini-2.5-pro": {
        "provider": "google",
        "model_id": "gemini-2.5-pro",
    },
    "gemini-2.5-flash": {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
    },
    "gemini-2.5-flash-lite": {
        "provider": "google",
        "model_id": "gemini-2.5-flash-lite",
    },
    # --- Anthropic Direct (anthropic SDK, API key) ---
    "claude-sonnet-4": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-20250514",
    },
    # --- Vertex AI Anthropic (AnthropicVertex SDK, ADC) ---
    "vertex/claude-opus-4.6": {
        "provider": "vertex-anthropic",
        "model_id": "claude-opus-4-6@latest",
        "region": "us-east5",
    },
    "vertex/claude-sonnet-4.5": {
        "provider": "vertex-anthropic",
        "model_id": "claude-sonnet-4-5@latest",
        "region": "us-east5",
    },
    "vertex/claude-haiku-4.5": {
        "provider": "vertex-anthropic",
        "model_id": "claude-haiku-4-5@latest",
        "region": "us-east5",
    },
    # --- Vertex AI Open Models (OpenAI-compatible SDK, ADC) ---
    "vertex/deepseek-v3.1": {
        "provider": "vertex-openai",
        "model_id": "deepseek-v3.1-maas",
        "publisher": "deepseek",
        "region": "us-east5",
    },
    "vertex/deepseek-r1": {
        "provider": "vertex-openai",
        "model_id": "deepseek-r1-maas",
        "publisher": "deepseek",
        "region": "us-east5",
    },
    "vertex/mistral-medium-3": {
        "provider": "vertex-openai",
        "model_id": "mistral-medium-3@latest",
        "publisher": "mistralai",
        "region": "us-east5",
    },
    "vertex/codestral-2": {
        "provider": "vertex-openai",
        "model_id": "codestral-2@latest",
        "publisher": "mistralai",
        "region": "us-east5",
    },
    "vertex/llama-4-maverick": {
        "provider": "vertex-openai",
        "model_id": "llama-4-maverick-17b-128e-instruct-maas",
        "publisher": "meta",
        "region": "us-east5",
    },
    # --- Antigravity LS (ローカル LS 経由、API key 不要) ---
    "agq/claude-sonnet": {
        "provider": "antigravity",
        "model_id": "MODEL_CLAUDE_4_5_SONNET_THINKING",
    },
    "agq/gemini-pro": {
        "provider": "antigravity",
        "model_id": "MODEL_GEMINI_2_5_PRO",
    },
    "agq/gemini-flash": {
        "provider": "antigravity",
        "model_id": "MODEL_GEMINI_2_5_FLASH",
    },
    "agq/gpt-4.1": {
        "provider": "antigravity",
        "model_id": "MODEL_GPT_4_1",
    },
}


# PURPOSE: [L2-auto] 実行ステータス
# =============================================================================
# Execution Result Types
# =============================================================================

class ExecutionStatus(Enum):
    """実行ステータス"""
    SUCCESS = "success"
    PARTIAL = "partial"       # 一部成功
    TIMEOUT = "timeout"
    ERROR = "error"
# PURPOSE: [L2-auto] CCL 実行結果
    RATE_LIMITED = "rate_limited"


@dataclass
class ExecutionResult:
    """CCL 実行結果"""
    status: ExecutionStatus
    output: str                              # 最終出力
    iterations: int = 0                      # 反復回数 (収束ループの場合)
    confidence: float = 1.0                  # 確信度 (0.0-1.0)
    intermediate_results: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
# PURPOSE: [L2-auto] 実行設定
    error: Optional[str] = None


@dataclass
class ExecutionConfig:
    """実行設定"""
    model: str = "auto"                      # MODEL_REGISTRY のキー or "auto"
    provider: str = "auto"                   # auto | antigravity | anthropic | google | vertex-anthropic | vertex-openai | openai
    timeout: int = 300                       # 秒
    max_retries: int = 3
    max_iterations: int = 5                  # 収束ループの最大反復
    temperature: float = 0.7
    api_key: Optional[str] = None


# PURPOSE: [L2-auto] LMQL プログラム実行器
# =============================================================================
# LMQL Executor
# =============================================================================

class LMQLExecutor:
    """LMQL プログラム実行器
    
    LMQL がインストールされていない場合は、
    フォールバック実行 (直接 LLM API) を使用。
    
    対応プロバイダー:
    - anthropic: Anthropic API (ANTHROPIC_API_KEY)
    - google: Google Gemini (GOOGLE_API_KEY)
    - openai: OpenAI (OPENAI_API_KEY)
    - vertex-anthropic: Vertex AI 経由 Claude (ADC)
    - vertex-openai: Vertex AI 経由 Open Models (ADC + OpenAI互換)
    """
    
    # ADC token キャッシュ (クラス変数)
    _adc_token: Optional[str] = None
    _adc_token_expiry: float = 0.0
    
    # PURPOSE: Initialize instance
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self._lmql_available = self._check_lmql()
    
    # PURPOSE: LMQL がインストールされているか確認
    def _check_lmql(self) -> bool:
        """LMQL がインストールされているか確認"""
        try:
            import lmql  # noqa: F401
            return True
        except ImportError:
            return False
    
    # PURPOSE: LMQL プログラムを非同期実行
    async def execute_async(
        self,
        lmql_code: str,
        context: str = "",
        variables: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """LMQL プログラムを非同期実行"""
        variables = variables or {}
        
        try:
            if self._lmql_available:
                result = await self._execute_with_lmql(lmql_code, context, variables)
                # LMQL exec() が失敗した場合は Fallback へ
                if result.status == ExecutionStatus.ERROR and "exec" in str(result.error).lower():
                    return await self._execute_fallback(lmql_code, context, variables)
                return result
            else:
                return await self._execute_fallback(lmql_code, context, variables)
        except asyncio.TimeoutError:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                output="",
                error=f"Execution timed out after {self.config.timeout} seconds"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=str(e)
            )
    
    # PURPOSE: LMQL プログラムを同期実行
    def execute(
        self,
        lmql_code: str,
        context: str = "",
        variables: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """LMQL プログラムを同期実行"""
        return asyncio.run(self.execute_async(lmql_code, context, variables))
    
    # PURPOSE: LMQL ライブラリを使用して実行
    async def _execute_with_lmql(
        self,
        lmql_code: str,
        context: str,
        variables: Dict[str, Any]
    ) -> ExecutionResult:
        """LMQL ライブラリを使用して実行
        
        G07 安全化: exec() を compile() + 制限された名前空間で実行。
        __builtins__ を制限し、危険な操作 (os, subprocess, sys) を
        名前空間から排除する。
        """
        import lmql
        
        # 制限された名前空間 — 必要最小限のみ許可
        _SAFE_BUILTINS = {
            "True": True, "False": False, "None": None,
            "str": str, "int": int, "float": float, "bool": bool,
            "list": list, "dict": dict, "tuple": tuple, "set": set,
            "len": len, "range": range, "enumerate": enumerate,
            "zip": zip, "map": map, "filter": filter,
            "isinstance": isinstance, "print": print,
            "min": min, "max": max, "sum": sum, "abs": abs,
        }
        
        safe_globals = {
            "__builtins__": _SAFE_BUILTINS,
            "lmql": lmql,
            "context": context,
        }
        safe_locals = {**variables}
        
        try:
            # compile() で構文チェック → 制限された名前空間で実行
            compiled = compile(lmql_code, "<ccl_lmql>", "exec")
            exec(compiled, safe_globals, safe_locals)  # noqa: S102
            
            # 関数を探して実行
            for name, obj in safe_locals.items():
                if callable(obj) and name.startswith("ccl_"):
                    result = await obj(context)
                    return ExecutionResult(
                        status=ExecutionStatus.SUCCESS,
                        output=str(result),
                        metadata={"function": name, "sandbox": True}
                    )
            
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="No executable CCL function found in LMQL code"
            )
        except SyntaxError as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=f"LMQL syntax error: {e}"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=f"LMQL execution error: {e}"
            )
    
    # PURPOSE: config.model を MODEL_REGISTRY で解決する
    def _resolve_model(self) -> Dict[str, str]:
        """config.model を MODEL_REGISTRY で解決する"""
        model = self.config.model
        if model in MODEL_REGISTRY:
            return MODEL_REGISTRY[model]
        # レジストリ未登録 → provider/model_id を推測
        if model.startswith("agq/"):
            return {"provider": "antigravity", "model_id": model.replace("agq/", "")}
        if "/" in model and model.startswith("vertex/"):
            return {"provider": "vertex-anthropic", "model_id": model.replace("vertex/", "")}
        if model.startswith("claude"):
            return {"provider": "anthropic", "model_id": model}
        if model.startswith("gemini"):
            return {"provider": "google", "model_id": model}
        # デフォルト: openai
        return {"provider": "openai", "model_id": model.replace("openai/", "")}
    
    # PURPOSE: ADC トークンを取得 (キャッシュ付き、有効期限 50分)
    @classmethod
    def _get_adc_token(cls) -> Optional[str]:
        """ADC トークンを取得 (キャッシュ付き、有効期限 50分)"""
        if cls._adc_token and time.time() < cls._adc_token_expiry:
            return cls._adc_token
        try:
            import google.auth
            import google.auth.transport.requests
            creds, _ = google.auth.default()
            creds.refresh(google.auth.transport.requests.Request())
            cls._adc_token = creds.token
            cls._adc_token_expiry = time.time() + 3000  # 50分キャッシュ
            return cls._adc_token
        except Exception:
            cls._adc_token = None
            return None
    
    # PURPOSE: フォールバック: 複数プロバイダー対応の LLM 呼び出し
    async def _execute_fallback(
        self,
        lmql_code: str,
        context: str,
        variables: Dict[str, Any]
    ) -> ExecutionResult:
        """フォールバック: 複数プロバイダー対応の LLM 呼び出し
        
        provider 指定モード:
          config.model が MODEL_REGISTRY にある → そのプロバイダーを使用
        
        auto モード (デフォルト):
          優先順位 (順に試行、失敗時は次へ):
          1. Anthropic (Claude) - ANTHROPIC_API_KEY
          2. Google (Gemini) - GOOGLE_API_KEY  
          3. OpenAI - OPENAI_API_KEY
        """
        # LMQL コードからプロンプトを抽出
        prompt = self._extract_prompt_from_lmql(lmql_code)
        if not prompt:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="Could not extract prompt from LMQL code"
            )
        
        # コンテキストを明示的にプロンプトに追加
        if context and context.strip():
            full_prompt = f"""## コンテキスト
{context}

## タスク
{prompt}

上記のコンテキストに基づいて、タスクを実行してください。"""
        else:
            full_prompt = prompt
        
        # --- モデル指定モード: MODEL_REGISTRY から解決 ---
        if self.config.model != "auto":
            model_info = self._resolve_model()
            provider = model_info["provider"]
            
            if provider == "antigravity":
                return await self._execute_antigravity(full_prompt, model_info.get("model_id"))
            elif provider == "vertex-anthropic":
                return await self._execute_vertex_anthropic(full_prompt, model_info)
            elif provider == "vertex-openai":
                return await self._execute_vertex_openai(full_prompt, model_info)
            elif provider == "anthropic":
                key = _get_secret("ANTHROPIC_API_KEY")
                if key:
                    return await self._execute_anthropic(full_prompt, key, model_info.get("model_id"))
            elif provider == "google":
                key = _get_secret("GOOGLE_API_KEY")
                if key:
                    return await self._execute_google(full_prompt, key, model_info.get("model_id"))
            elif provider == "openai":
                key = self.config.api_key or _get_secret("OPENAI_API_KEY")
                if key:
                    return await self._execute_openai(full_prompt, key, model_info.get("model_id"))
            # 指定プロバイダー失敗 → auto フォールバックへ
        
        # --- Auto モード: 順に試行 ---
        providers = []
        
        # Antigravity LS を最優先 (API key 不要、コスト 0)
        if self._is_antigravity_available():
            providers.append(("antigravity", None, self._execute_antigravity_auto))
        
        anthropic_key = _get_secret("ANTHROPIC_API_KEY")
        google_key = _get_secret("GOOGLE_API_KEY")
        openai_key = self.config.api_key or _get_secret("OPENAI_API_KEY")
        
        if anthropic_key:
            providers.append(("anthropic", anthropic_key, self._execute_anthropic))
        if google_key:
            providers.append(("google", google_key, self._execute_google))
        if openai_key:
            providers.append(("openai", openai_key, self._execute_openai))
        
        if not providers:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="No API key found. Set ANTHROPIC_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY"
            )
        
        errors = []
        for provider_name, key, executor_fn in providers:
            # W06: Circuit Breaker — 連続失敗中のプロバイダーをスキップ
            if _circuit_breaker.is_open(provider_name):
                errors.append(f"{provider_name}: circuit open (cooldown)")
                continue
            
            result = await executor_fn(full_prompt, key)
            if result.status == ExecutionStatus.SUCCESS:
                _circuit_breaker.record_success(provider_name)
                return result
            _circuit_breaker.record_failure(provider_name)
            errors.append(f"{provider_name}: {result.error}")
        
        # 全プロバイダー失敗
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error=f"All providers failed: {'; '.join(errors)}"
        )
    
    # PURPOSE: Anthropic Claude API 呼び出し (直接 API key)
    async def _execute_anthropic(
        self, prompt: str, api_key: str, model_id: Optional[str] = None
    ) -> ExecutionResult:
        """Anthropic Claude API 呼び出し (直接 API key)"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="anthropic not installed. Run: pip install anthropic"
            )
        
        model_name = model_id or "claude-sonnet-4-20250514"
        client = AsyncAnthropic(api_key=api_key)
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    client.messages.create(
                        model=model_name,
                        max_tokens=4096,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                    timeout=self.config.timeout
                )
                
                output = response.content[0].text
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=output,
                    metadata={
                        "provider": "anthropic",
                        "model": model_name,
                        "attempt": attempt + 1,
                        "fallback": self.config.model == "auto"
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error="Anthropic API call timed out"
                    )
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"Anthropic error: {str(e)[:200]}"
                )
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Anthropic API call failed after retries"
        )
    
    # PURPOSE: Google Gemini API 呼び出し (google.genai SDK)
    async def _execute_google(
        self, prompt: str, api_key: str, model_id: Optional[str] = None
    ) -> ExecutionResult:
        """Google Gemini API 呼び出し (google.genai SDK)"""
        try:
            from google import genai
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="google-genai not installed. Run: pip install google-genai"
            )
        
        client = genai.Client(api_key=api_key)
        model_name = model_id or "gemini-2.5-flash"
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=model_name,
                        contents=prompt
                    ),
                    timeout=self.config.timeout
                )
                
                output = response.text
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=output,
                    metadata={
                        "provider": "google",
                        "model": model_name,
                        "attempt": attempt + 1,
                        "fallback": self.config.model == "auto"
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error="Google API call timed out"
                    )
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"Google error: {str(e)[:200]}"
                )
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Google API call failed after retries"
        )
    
    # PURPOSE: OpenAI API 呼び出し
    async def _execute_openai(
        self, prompt: str, api_key: str, model_id: Optional[str] = None
    ) -> ExecutionResult:
        """OpenAI API 呼び出し"""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="openai not installed. Run: pip install openai"
            )
        
        model_name = model_id or self.config.model.replace("openai/", "")
        if model_name == "auto":
            model_name = "gpt-4o"
        client = AsyncOpenAI(api_key=api_key)
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.config.temperature,
                    ),
                    timeout=self.config.timeout
                )
                
                output = response.choices[0].message.content
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=output,
                    metadata={
                        "provider": "openai",
                        "model": model_name,
                        "attempt": attempt + 1,
                        "fallback": self.config.model == "auto"
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error="OpenAI API call timed out"
                    )
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"OpenAI error: {str(e)[:200]}"
                )
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Max retries exceeded"
        )
    
    # PURPOSE: Vertex AI 経由 Claude 呼び出し (AnthropicVertex SDK, ADC 認証)
    async def _execute_vertex_anthropic(
        self, prompt: str, model_info: Dict[str, str]
    ) -> ExecutionResult:
        """Vertex AI 経由 Claude 呼び出し (AnthropicVertex SDK, ADC 認証)"""
        try:
            from anthropic import AnthropicVertex
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="anthropic[vertex] not installed. Run: pip install 'anthropic[vertex]'"
            )
        
        project_id = _get_secret("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="GOOGLE_CLOUD_PROJECT not set in environment"
            )
        
        region = model_info.get("region", "us-east5")
        model_name = model_info.get("model_id", "claude-sonnet-4-5@latest")
        
        try:
            client = AnthropicVertex(project_id=project_id, region=region)
        except Exception as e:
            # ADC 未設定時のグレースフルフォールバック
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
            if anthropic_key:
                # 直接 API に降格
                fallback_model = model_name.split("@")[0]  # @latest を除去
                return await self._execute_anthropic(prompt, anthropic_key, fallback_model)
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=f"Vertex ADC failed and no ANTHROPIC_API_KEY fallback: {str(e)[:200]}"
            )
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.messages.create,
                        model=model_name,
                        max_tokens=4096,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                    timeout=self.config.timeout
                )
                
                output = response.content[0].text
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=output,
                    metadata={
                        "provider": "vertex-anthropic",
                        "model": model_name,
                        "region": region,
                        "project": project_id,
                        "attempt": attempt + 1,
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error=f"Vertex Anthropic API call timed out (region={region})"
                    )
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"Vertex Anthropic error: {str(e)[:200]}"
                )
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Vertex Anthropic API call failed after retries"
        )
    
    # PURPOSE: Vertex AI 経由 Open Models (OpenAI互換 SDK, ADC 認証)
    async def _execute_vertex_openai(
        self, prompt: str, model_info: Dict[str, str]
    ) -> ExecutionResult:
        """Vertex AI 経由 Open Models (OpenAI互換 SDK, ADC 認証)
        
        DeepSeek, Mistral, Llama 4 等のオープンモデルを
        Vertex AI の OpenAI 互換エンドポイント経由で呼び出す。
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="openai not installed. Run: pip install openai"
            )
        
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="GOOGLE_CLOUD_PROJECT not set in environment"
            )
        
        # ADC token 取得
        token = self._get_adc_token()
        if not token:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="Failed to get ADC token. Run: gcloud auth application-default login"
            )
        
        region = model_info.get("region", "us-east5")
        model_id = model_info.get("model_id", "")
        publisher = model_info.get("publisher", "google")
        
        base_url = (
            f"https://{region}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{project_id}/locations/{region}/"
            f"endpoints/openapi"
        )
        
        # OpenAI互換の model 名: publishers/{publisher}/models/{model_id}
        oai_model_name = f"google/{model_id}" if publisher == "google" else f"{publisher}/{model_id}"
        
        client = AsyncOpenAI(base_url=base_url, api_key=token)
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=oai_model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.config.temperature,
                    ),
                    timeout=self.config.timeout
                )
                
                output = response.choices[0].message.content
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=output,
                    metadata={
                        "provider": "vertex-openai",
                        "model": model_id,
                        "publisher": publisher,
                        "region": region,
                        "attempt": attempt + 1,
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error=f"Vertex OpenAI-compat API timed out (region={region})"
                    )
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                error_msg = str(e)[:200]
                # token 期限切れ → リフレッシュ試行
                if "401" in error_msg or "403" in error_msg:
                    LMQLExecutor._adc_token = None  # キャッシュ無効化
                    new_token = self._get_adc_token()
                    if new_token and attempt < self.config.max_retries - 1:
                        client = AsyncOpenAI(base_url=base_url, api_key=new_token)
                        await asyncio.sleep(1)
                        continue
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"Vertex OpenAI-compat error: {error_msg}"
                )
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Vertex OpenAI-compat API call failed after retries"
        )
    
    # PURPOSE: Antigravity LS が利用可能か確認
    def _is_antigravity_available(self) -> bool:
        """Antigravity LS が起動しているか確認 (軽量チェック)"""
        try:
            from mekhane.ochema.antigravity_client import AntigravityClient
            client = AntigravityClient()
            # _detect_ls() は PID/CSRF/Port を検出。失敗時は RuntimeError
            client._detect_ls()
            return True
        except Exception:
            return False
    
    # PURPOSE: Antigravity LS 経由の LLM 呼び出し (モデル指定)
    async def _execute_antigravity(
        self, prompt: str, model_id: Optional[str] = None
    ) -> ExecutionResult:
        """Antigravity LS 経由の LLM 呼び出し
        
        ローカルの Language Server API を経由して LLM を呼び出す。
        API key 不要、追加コスト 0。
        """
        try:
            from mekhane.ochema.antigravity_client import AntigravityClient
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="mekhane.ochema.antigravity_client not found"
            )
        
        agq_model = model_id or "MODEL_CLAUDE_4_5_SONNET_THINKING"
        
        try:
            client = AntigravityClient()
            # asyncio.to_thread で同期の client.ask() をラップ
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    client.ask,
                    prompt,
                    model=agq_model,
                    timeout=float(self.config.timeout),
                ),
                timeout=self.config.timeout
            )
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output=result.text,
                metadata={
                    "provider": "antigravity",
                    "model": result.model or agq_model,
                    "cascade_id": result.cascade_id,
                    "thinking": result.thinking,
                }
            )
        except TimeoutError:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                output="",
                error=f"Antigravity LS timed out after {self.config.timeout}s"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=f"Antigravity error: {str(e)[:200]}"
            )
    
    # PURPOSE: Auto モード用 Antigravity LS 呼び出し (キーなしアダプター)
    async def _execute_antigravity_auto(
        self, prompt: str, _key: Optional[str] = None, model_id: Optional[str] = None
    ) -> ExecutionResult:
        """Auto モード用アダプター (provider チェーンの署名に合わせる)"""
        return await self._execute_antigravity(prompt, model_id)
    
    # PURPOSE: プレーンテキストプロンプトから直接 LLM を呼び出す (LMQL 不使用)
    async def generate_text_async(
        self,
        prompt: str,
        context: str = "",
    ) -> ExecutionResult:
        """プレーンテキストプロンプトを直接 LLM に送信
        
        LMQL パーサーを迂回し、プロバイダーチェーンの自動フォールバックを直接使用。
        verifier の Multi-Agent Debate 等、LMQL 不要の LLM 呼び出し用。
        
        Args:
            prompt: プレーンテキストプロンプト
            context: 追加コンテキスト (オプション)
            
        Returns:
            ExecutionResult
        """
        # コンテキストをプロンプトに統合
        if context and context.strip():
            full_prompt = f"""## コンテキスト
{context}

## タスク
{prompt}

上記のコンテキストに基づいて、タスクを実行してください。"""
        else:
            full_prompt = prompt
        
        # --- モデル指定モード ---
        if self.config.model != "auto":
            model_info = self._resolve_model()
            provider = model_info["provider"]
            
            if provider == "antigravity":
                return await self._execute_antigravity(full_prompt, model_info.get("model_id"))
            elif provider == "vertex-anthropic":
                return await self._execute_vertex_anthropic(full_prompt, model_info)
            elif provider == "vertex-openai":
                return await self._execute_vertex_openai(full_prompt, model_info)
            elif provider == "anthropic":
                key = _get_secret("ANTHROPIC_API_KEY")
                if key:
                    return await self._execute_anthropic(full_prompt, key, model_info.get("model_id"))
            elif provider == "google":
                key = _get_secret("GOOGLE_API_KEY")
                if key:
                    return await self._execute_google(full_prompt, key, model_info.get("model_id"))
            elif provider == "openai":
                key = self.config.api_key or _get_secret("OPENAI_API_KEY")
                if key:
                    return await self._execute_openai(full_prompt, key, model_info.get("model_id"))
        
        # --- Auto モード: 順に試行 ---
        providers = []
        
        if self._is_antigravity_available():
            providers.append(("antigravity", None, self._execute_antigravity_auto))
        
        anthropic_key = _get_secret("ANTHROPIC_API_KEY")
        google_key = _get_secret("GOOGLE_API_KEY")
        openai_key = self.config.api_key or _get_secret("OPENAI_API_KEY")
        
        if anthropic_key:
            providers.append(("anthropic", anthropic_key, self._execute_anthropic))
        if google_key:
            providers.append(("google", google_key, self._execute_google))
        if openai_key:
            providers.append(("openai", openai_key, self._execute_openai))
        
        if not providers:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="No LLM provider available (no API keys, no Antigravity LS)"
            )
        
        errors = []
        for provider_name, key, executor_fn in providers:
            if _circuit_breaker.is_open(provider_name):
                errors.append(f"{provider_name}: circuit open (cooldown)")
                continue
            
            result = await executor_fn(full_prompt, key)
            if result.status == ExecutionStatus.SUCCESS:
                _circuit_breaker.record_success(provider_name)
                return result
            _circuit_breaker.record_failure(provider_name)
            errors.append(f"{provider_name}: {result.error}")
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error=f"All providers failed: {'; '.join(errors)}"
        )
    
    # PURPOSE: generate_text の同期版
    def generate_text(
        self,
        prompt: str,
        context: str = "",
    ) -> ExecutionResult:
        """generate_text_async の同期ラッパー"""
        return asyncio.run(self.generate_text_async(prompt, context))
    
    # PURPOSE: LMQL コードからプロンプト部分を抽出
    def _extract_prompt_from_lmql(self, lmql_code: str) -> Optional[str]:
        """LMQL コードからプロンプト部分を抽出"""
        # 文字列リテラルを探す
        prompts = []
        
        # "..." パターンを抽出
        for match in re.finditer(r'"([^"]+)"', lmql_code):
            text = match.group(1)
            # コード的な文字列は除外
            if not text.startswith("@") and not "import" in text:
                prompts.append(text)
        
        if prompts:
            return "\n".join(prompts)
        return None


# PURPOSE: [L2-auto] 収束ループ実行器
# =============================================================================
# Convergence Loop Executor
# =============================================================================

class ConvergenceExecutor:
    """収束ループ実行器
    
    CCL の >> (収束) 演算子を実行し、
    条件を満たすまで反復する。
    """
    
    # PURPOSE: Initialize instance
    def __init__(self, executor: LMQLExecutor):
        self.executor = executor
    
    # PURPOSE: 収束ループを実行
    async def execute_convergence(
        self,
        lmql_code: str,
        context: str,
        condition_var: str = "V",
        condition_op: str = "<",
        condition_value: float = 0.3,
        max_iterations: int = 5
    ) -> ExecutionResult:
        """収束ループを実行"""
        results = []
        current_value = 1.0  # 初期不確実性
        
        for i in range(max_iterations):
            # ワークフロー実行
            result = await self.executor.execute_async(lmql_code, context)
            results.append(result.output)
            
            if result.status != ExecutionStatus.SUCCESS:
                return ExecutionResult(
                    status=result.status,
                    output=result.output,
                    iterations=i + 1,
                    intermediate_results=results,
                    error=result.error
                )
            
            # 不確実性を評価 (簡易ヒューリスティック)
            current_value = self._estimate_uncertainty(result.output)
            
            # 収束条件チェック
            if self._check_condition(current_value, condition_op, condition_value):
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=results[-1],
                    iterations=i + 1,
                    confidence=1.0 - current_value,
                    intermediate_results=results,
                    metadata={"converged": True, "final_uncertainty": current_value}
                )
            
            # 次の反復のためにコンテキストを更新
            context = f"{context}\n\n前回の分析:\n{result.output}"
        
        # 最大反復に達した
        return ExecutionResult(
            status=ExecutionStatus.PARTIAL,
            output=results[-1] if results else "",
            iterations=max_iterations,
            confidence=1.0 - current_value,
            intermediate_results=results,
            metadata={"converged": False, "final_uncertainty": current_value}
        )
    
    # PURPOSE: 出力から不確実性を推定 (簡易ヒューリスティック)
    def _estimate_uncertainty(self, output: str) -> float:
        """出力から不確実性を推定 (簡易ヒューリスティック)"""
        uncertainty_indicators = [
            "かもしれない", "おそらく", "might", "maybe", "perhaps",
            "不明", "unclear", "uncertain", "possible",
            "?", "推測", "guess", "assume"
        ]
        
        certainty_indicators = [
            "確実", "definitely", "certainly", "明確",
            "結論", "conclusion", "therefore", "したがって"
        ]
        
        output_lower = output.lower()
        
        uncertainty_count = sum(1 for ind in uncertainty_indicators if ind in output_lower)
        certainty_count = sum(1 for ind in certainty_indicators if ind in output_lower)
        
        # 簡易スコア計算
        if certainty_count > uncertainty_count:
            return max(0.1, 0.5 - (certainty_count * 0.1))
        elif uncertainty_count > 0:
            return min(0.9, 0.5 + (uncertainty_count * 0.1))
        else:
            return 0.4  # デフォルト
    
    # PURPOSE: 条件をチェック
    def _check_condition(self, value: float, op: str, threshold: float) -> bool:
        """条件をチェック"""
        if op == "<":
            return value < threshold
        elif op == "<=":
            return value <= threshold
        elif op == ">":
            return value > threshold
        elif op == ">=":
            return value >= threshold
        elif op == "=":
            return abs(value - threshold) < 0.01
        return False


# =============================================================================
# High-Level API
# =============================================================================

# PURPOSE: CCL 式をコンパイルして実行
def execute_ccl(
    ccl: str,
    context: str = "",
    model: str = "auto",
    macros: Optional[Dict[str, str]] = None,
    **kwargs
) -> ExecutionResult:
    """CCL 式をコンパイルして実行
    
    Args:
        ccl: CCL 式 (例: "/noe+ >> V[] < 0.3")
        context: 入力コンテキスト
        model: 使用する LLM モデル
        macros: マクロ定義
        **kwargs: ExecutionConfig に渡す追加設定
        
    Returns:
        ExecutionResult
        
    Example:
        >>> result = execute_ccl("/noe+", "プロジェクト設計を分析")
        >>> print(result.output)
    """
    # 遅延インポート (循環参照回避)
    from . import compile_ccl
    from .parser import parse_ccl
    from .ccl_ast import ConvergenceLoop
    
    # コンパイル
    lmql_code = compile_ccl(ccl, macros=macros, model=model)
    
    # 設定
    config = ExecutionConfig(model=model, **kwargs)
    executor = LMQLExecutor(config)
    
    # 収束ループかどうかを判定
    try:
        ast = parse_ccl(ccl)
        if isinstance(ast, ConvergenceLoop):
            conv_executor = ConvergenceExecutor(executor)
            return asyncio.run(conv_executor.execute_convergence(
                lmql_code,
                context,
                condition_var=ast.condition.var,
                condition_op=ast.condition.op,
                condition_value=ast.condition.value,
                max_iterations=config.max_iterations
            ))
    except Exception:
        pass  # パース失敗時は通常実行
    
    # 通常実行
    return executor.execute(lmql_code, context)
