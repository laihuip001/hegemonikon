# PROOF: [L2/インフラ] LMQL 実行ランタイム
"""
Hermēneus Runtime — LMQL プログラムを実行

compile_ccl() の出力を実際の LLM で実行し、
結果を構造化して返す。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import os
import re
import json
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pathlib import Path

# .env ファイルから環境変数を読み込む
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


# =============================================================================
# Execution Result Types
# =============================================================================

class ExecutionStatus(Enum):
    """実行ステータス"""
    SUCCESS = "success"
    PARTIAL = "partial"       # 一部成功
    TIMEOUT = "timeout"
    ERROR = "error"
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
    error: Optional[str] = None


@dataclass
class ExecutionConfig:
    """実行設定"""
    model: str = "openai/gpt-4o"
    timeout: int = 300                       # 秒
    max_retries: int = 3
    max_iterations: int = 5                  # 収束ループの最大反復
    temperature: float = 0.7
    api_key: Optional[str] = None


# =============================================================================
# LMQL Executor
# =============================================================================

class LMQLExecutor:
    """LMQL プログラム実行器
    
    LMQL がインストールされていない場合は、
    フォールバック実行 (直接 OpenAI API) を使用。
    """
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self._lmql_available = self._check_lmql()
    
    def _check_lmql(self) -> bool:
        """LMQL がインストールされているか確認"""
        try:
            import lmql  # noqa: F401
            return True
        except ImportError:
            return False
    
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
    
    def execute(
        self,
        lmql_code: str,
        context: str = "",
        variables: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """LMQL プログラムを同期実行"""
        return asyncio.run(self.execute_async(lmql_code, context, variables))
    
    async def _execute_with_lmql(
        self,
        lmql_code: str,
        context: str,
        variables: Dict[str, Any]
    ) -> ExecutionResult:
        """LMQL ライブラリを使用して実行"""
        import lmql
        
        # LMQL コードを実行可能な形式に変換
        # (compile_ccl の出力は文字列なので、exec で実行)
        local_vars = {"lmql": lmql, "context": context, **variables}
        
        try:
            exec(lmql_code, local_vars)
            
            # 関数を探して実行
            for name, obj in local_vars.items():
                if callable(obj) and name.startswith("ccl_"):
                    result = await obj(context)
                    return ExecutionResult(
                        status=ExecutionStatus.SUCCESS,
                        output=str(result),
                        metadata={"function": name}
                    )
            
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="No executable CCL function found in LMQL code"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error=f"LMQL execution error: {e}"
            )
    
    async def _execute_fallback(
        self,
        lmql_code: str,
        context: str,
        variables: Dict[str, Any]
    ) -> ExecutionResult:
        """フォールバック: 複数プロバイダー対応の LLM 呼び出し
        
        優先順位:
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
        
        # コンテキストを挿入
        full_prompt = prompt.replace("{context}", context)
        
        # プロバイダー検出と実行
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        google_key = os.environ.get("GOOGLE_API_KEY")
        openai_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        
        if anthropic_key:
            return await self._execute_anthropic(full_prompt, anthropic_key)
        elif google_key:
            return await self._execute_google(full_prompt, google_key)
        elif openai_key:
            return await self._execute_openai(full_prompt, openai_key)
        else:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="No API key found. Set ANTHROPIC_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY"
            )
    
    async def _execute_anthropic(self, prompt: str, api_key: str) -> ExecutionResult:
        """Anthropic Claude API 呼び出し"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="anthropic not installed. Run: pip install anthropic"
            )
        
        client = AsyncAnthropic(api_key=api_key)
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    client.messages.create(
                        model="claude-sonnet-4-20250514",
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
                        "model": "claude-sonnet-4-20250514",
                        "attempt": attempt + 1,
                        "fallback": True
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Anthropic API call failed after retries"
        )
    
    async def _execute_google(self, prompt: str, api_key: str) -> ExecutionResult:
        """Google Gemini API 呼び出し"""
        try:
            import google.generativeai as genai
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="google-generativeai not installed. Run: pip install google-generativeai"
            )
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-pro")
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, prompt),
                    timeout=self.config.timeout
                )
                
                output = response.text
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=output,
                    metadata={
                        "provider": "google",
                        "model": "gemini-2.5-pro",
                        "attempt": attempt + 1,
                        "fallback": True
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Google API call failed after retries"
        )
    
    async def _execute_openai(self, prompt: str, api_key: str) -> ExecutionResult:
        """OpenAI API 呼び出し"""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                output="",
                error="openai not installed. Run: pip install openai"
            )
        
        client = AsyncOpenAI(api_key=api_key)
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=self.config.model.replace("openai/", ""),
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
                        "model": self.config.model,
                        "attempt": attempt + 1,
                        "fallback": True
                    }
                )
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            output="",
            error="Max retries exceeded"
        )
    
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


# =============================================================================
# Convergence Loop Executor
# =============================================================================

class ConvergenceExecutor:
    """収束ループ実行器
    
    CCL の >> (収束) 演算子を実行し、
    条件を満たすまで反復する。
    """
    
    def __init__(self, executor: LMQLExecutor):
        self.executor = executor
    
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

async def execute_ccl_async(
    ccl: str,
    context: str = "",
    model: str = "openai/gpt-4o",
    macros: Optional[Dict[str, str]] = None,
    **kwargs
) -> ExecutionResult:
    """CCL 式をコンパイルして非同期実行
    
    Args:
        ccl: CCL 式 (例: "/noe+ >> V[] < 0.3")
        context: 入力コンテキスト
        model: 使用する LLM モデル
        macros: マクロ定義
        **kwargs: ExecutionConfig に渡す追加設定
        
    Returns:
        ExecutionResult
    """
    # 遅延インポート (循環参照回避)
    from . import compile_ccl
    from .parser import parse_ccl
    from .ast import ConvergenceLoop
    
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
            return await conv_executor.execute_convergence(
                lmql_code,
                context,
                condition_var=ast.condition.var,
                condition_op=ast.condition.op,
                condition_value=ast.condition.value,
                max_iterations=config.max_iterations
            )
    except Exception:
        pass  # パース失敗時は通常実行
    
    # 通常実行
    return await executor.execute_async(lmql_code, context)


def execute_ccl(
    ccl: str,
    context: str = "",
    model: str = "openai/gpt-4o",
    macros: Optional[Dict[str, str]] = None,
    **kwargs
) -> ExecutionResult:
    """CCL 式をコンパイルして実行 (同期)

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
    return asyncio.run(execute_ccl_async(
        ccl=ccl,
        context=context,
        model=model,
        macros=macros,
        **kwargs
    ))
