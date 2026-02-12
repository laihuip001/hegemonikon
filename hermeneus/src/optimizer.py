# PROOF: [L2/インフラ] <- hermeneus/src/ Hermēneus DSPy Optimizer
"""
Hermēneus Optimizer — 自動プロンプト最適化

DSPy の Teleprompter (BootstrapFewShot 等) を使用して、
CCL ワークフローのプロンプトを自動最適化する。

Usage:
    from hermeneus.src.optimizer import CCLOptimizer, optimize_ccl
    
    # 最適化実行
    result = optimize_ccl("/noe+", examples, metric)
    print(result.optimized_prompt)

Origin: 2026-02-01 Synergeia Distributed Execution / Phase 4
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
import os

# DSPy import (lazy)
try:
    import dspy
    from dspy.teleprompt import BootstrapFewShot
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None
    BootstrapFewShot = None


# =============================================================================
# Types
# =============================================================================

class OptimizerType(Enum):
    """最適化手法"""
    BOOTSTRAP_FEWSHOT = "bootstrap_fewshot"
    MIPRO = "mipro"
    COPRO = "copro"
    RANDOM_SEARCH = "random_search"


@dataclass
class OptimizationConfig:
    """最適化設定"""
    optimizer_type: OptimizerType = OptimizerType.BOOTSTRAP_FEWSHOT
    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 4
    num_trials: int = 10
    metric_threshold: float = 0.8
    model: str = "openai/gpt-4o-mini"
    api_key: Optional[str] = None


@dataclass
class OptimizationResult:
    """最適化結果"""
    success: bool
    optimized_prompt: str
    accuracy: float
    num_demos: int
    config: OptimizationConfig
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class CCLExample:
    """CCL 最適化用の例"""
    ccl: str
    context: str
    expected_output: str
    
    # PURPOSE: DSPy Example に変換
    def to_dspy_example(self) -> Any:
        """DSPy Example に変換"""
        if not DSPY_AVAILABLE:
            raise RuntimeError("DSPy not installed")
        return dspy.Example(
            ccl=self.ccl,
            context=self.context,
            output=self.expected_output
        ).with_inputs("ccl", "context")


# =============================================================================
# CCL Signature (DSPy)
# =============================================================================

# PURPOSE: CCL 実行用の DSPy Signature を生成
def create_ccl_signature():
    """CCL 実行用の DSPy Signature を生成"""
    if not DSPY_AVAILABLE:
        return None
    
    class CCLExecutionSignature(dspy.Signature):
        """CCL ワークフローを実行して結果を生成"""
        ccl: str = dspy.InputField(desc="CCL expression (e.g., /noe+)")
        context: str = dspy.InputField(desc="Execution context")
        output: str = dspy.OutputField(desc="Execution result")
    
    return CCLExecutionSignature


# =============================================================================
# CCL Module (DSPy)
# =============================================================================

class CCLModule:
    """CCL 実行モジュール (DSPy Module ラッパー)"""
    
    # PURPOSE: Initialize instance
    def __init__(self, signature=None, model: str = "openai/gpt-4o-mini"):
        if not DSPY_AVAILABLE:
            raise RuntimeError("DSPy not installed. Run: pip install dspy-ai")
        
        self.signature = signature or create_ccl_signature()
        self.model = model
        self._configure_lm()
        self._build_module()
    
    # PURPOSE: LM を設定
    def _configure_lm(self):
        """LM を設定"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        
        # DSPy 3.x では dspy.LM を使用
        lm = dspy.LM(self.model, api_key=api_key)
        dspy.configure(lm=lm)
    
    # PURPOSE: モジュールを構築
    def _build_module(self):
        """モジュールを構築"""
        # ChainOfThought で推論を強化
        self.predictor = dspy.ChainOfThought(self.signature)
    
    # PURPOSE: CCL を実行
    def forward(self, ccl: str, context: str) -> str:
        """CCL を実行"""
        result = self.predictor(ccl=ccl, context=context)
        return result.output
    
    # PURPOSE: Call  
    def __call__(self, ccl: str, context: str) -> str:
        return self.forward(ccl, context)


# =============================================================================
# CCL Optimizer
# =============================================================================

class CCLOptimizer:
    """CCL ワークフロー最適化器"""
    
    # PURPOSE: Initialize instance
    def __init__(self, config: Optional[OptimizationConfig] = None):
        if not DSPY_AVAILABLE:
            raise RuntimeError("DSPy not installed. Run: pip install dspy-ai")
        
        self.config = config or OptimizationConfig()
        self._compiled_module = None
    
    # PURPOSE: CCL ワークフローを最適化
    def optimize(
        self,
        ccl: str,
        examples: List[CCLExample],
        metric: Optional[Callable] = None,
    ) -> OptimizationResult:
        """CCL ワークフローを最適化
        
        Args:
            ccl: 最適化対象の CCL 式
            examples: トレーニング例
            metric: 評価メトリクス (デフォルト: 完全一致)
            
        Returns:
            OptimizationResult
        """
        try:
            # モジュール作成
            module = CCLModule(model=self.config.model)
            
            # 例を DSPy 形式に変換
            trainset = [ex.to_dspy_example() for ex in examples]
            
            # メトリクス (デフォルト: 出力の類似度)
            if metric is None:
                metric = self._default_metric
            
            # オプティマイザ選択
            optimizer = self._create_optimizer()
            
            # 最適化実行
            compiled = optimizer.compile(
                module.predictor,
                trainset=trainset,
            )
            
            self._compiled_module = compiled
            
            # 精度評価
            accuracy = self._evaluate(compiled, examples, metric)
            
            # 最適化されたプロンプトを抽出
            optimized_prompt = self._extract_optimized_prompt(compiled)
            
            return OptimizationResult(
                success=True,
                optimized_prompt=optimized_prompt,
                accuracy=accuracy,
                num_demos=len(trainset),
                config=self.config,
                metadata={"ccl": ccl, "num_examples": len(examples)}
            )
            
        except Exception as e:
            return OptimizationResult(
                success=False,
                optimized_prompt="",
                accuracy=0.0,
                num_demos=0,
                config=self.config,
                error=str(e)
            )
    
    # PURPOSE: オプティマイザを作成
    def _create_optimizer(self):
        """オプティマイザを作成"""
        opt_type = self.config.optimizer_type
        
        if opt_type == OptimizerType.BOOTSTRAP_FEWSHOT:
            return BootstrapFewShot(
                max_bootstrapped_demos=self.config.max_bootstrapped_demos,
                max_labeled_demos=self.config.max_labeled_demos,
            )
        else:
            # フォールバック
            return BootstrapFewShot(
                max_bootstrapped_demos=self.config.max_bootstrapped_demos,
            )
    
    # PURPOSE: デフォルトメトリクス: 出力の類似度
    def _default_metric(self, example, prediction, trace=None) -> float:
        """デフォルトメトリクス: 出力の類似度"""
        expected = getattr(example, 'output', '')
        predicted = getattr(prediction, 'output', '')
        
        if not expected or not predicted:
            return 0.0
        
        # 簡易類似度 (完全一致 or 部分一致)
        if expected.lower() == predicted.lower():
            return 1.0
        elif expected.lower() in predicted.lower():
            return 0.8
        elif predicted.lower() in expected.lower():
            return 0.6
        else:
            # 単語オーバーラップ
            expected_words = set(expected.lower().split())
            predicted_words = set(predicted.lower().split())
            overlap = len(expected_words & predicted_words)
            total = len(expected_words | predicted_words)
            return overlap / total if total > 0 else 0.0
    
    # PURPOSE: 最適化結果を評価
    def _evaluate(
        self,
        compiled,
        examples: List[CCLExample],
        metric: Callable
    ) -> float:
        """最適化結果を評価"""
        if not examples:
            return 0.0
        
        scores = []
        for ex in examples:
            try:
                prediction = compiled(ccl=ex.ccl, context=ex.context)
                dspy_example = ex.to_dspy_example()
                score = metric(dspy_example, prediction)
                scores.append(score)
            except Exception:
                scores.append(0.0)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    # PURPOSE: 最適化されたプロンプトを抽出
    def _extract_optimized_prompt(self, compiled) -> str:
        """最適化されたプロンプトを抽出"""
        try:
            # デモを文字列化
            demos = getattr(compiled, 'demos', [])
            if demos:
                demo_strs = []
                for d in demos[:3]:  # 最大3件
                    ccl = getattr(d, 'ccl', '')
                    ctx = getattr(d, 'context', '')[:50]
                    out = getattr(d, 'output', '')[:100]
                    demo_strs.append(f"CCL: {ccl}, Context: {ctx}... -> {out}...")
                return "Optimized with demos:\n" + "\n".join(demo_strs)
            return "Optimized (no demos extracted)"
        except Exception:
            return "Optimized"


# =============================================================================
# Convenience Functions
# =============================================================================

# PURPOSE: DSPy が利用可能か
def is_dspy_available() -> bool:
    """DSPy が利用可能か"""
    return DSPY_AVAILABLE


# PURPOSE: CCL を最適化 (便利関数)
def optimize_ccl(
    ccl: str,
    examples: List[CCLExample],
    metric: Optional[Callable] = None,
    config: Optional[OptimizationConfig] = None,
) -> OptimizationResult:
    """CCL を最適化 (便利関数)"""
    optimizer = CCLOptimizer(config)
    return optimizer.optimize(ccl, examples, metric)


# =============================================================================
# Mock Optimizer (for testing)
# =============================================================================

class MockOptimizer:
    """テスト用モック最適化器"""
    
    # PURPOSE: Initialize instance
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
    
    # PURPOSE: モック最適化
    def optimize(
        self,
        ccl: str,
        examples: List[CCLExample],
        metric: Optional[Callable] = None,
    ) -> OptimizationResult:
        """モック最適化"""
        return OptimizationResult(
            success=True,
            optimized_prompt=f"[MOCK] Optimized: {ccl}",
            accuracy=0.85,
            num_demos=len(examples),
            config=self.config,
            metadata={"mock": True}
        )


# PURPOSE: オプティマイザを取得
def get_optimizer(use_mock: bool = False) -> Union[CCLOptimizer, MockOptimizer]:
    """オプティマイザを取得"""
    if use_mock or not DSPY_AVAILABLE:
        return MockOptimizer()
    return CCLOptimizer()
