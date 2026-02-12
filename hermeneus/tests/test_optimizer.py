# PROOF: [L2/テスト] <- hermeneus/tests/ Optimizer テスト
"""テスト: Hermeneus Phase 4 Optimizer"""

import pytest
from hermeneus.src.optimizer import (
    OptimizerType, OptimizationConfig, OptimizationResult,
    CCLExample, MockOptimizer,
    is_dspy_available, get_optimizer
)


class TestOptimizationConfig:
    """OptimizationConfig のテスト"""
    
    # PURPOSE: デフォルト設定
    def test_default_config(self):
        """デフォルト設定"""
        config = OptimizationConfig()
        assert config.optimizer_type == OptimizerType.BOOTSTRAP_FEWSHOT
        assert config.max_bootstrapped_demos == 4
        assert config.metric_threshold == 0.8
    
    # PURPOSE: カスタム設定
    def test_custom_config(self):
        """カスタム設定"""
        config = OptimizationConfig(
            optimizer_type=OptimizerType.MIPRO,
            num_trials=20,
            metric_threshold=0.9
        )
        assert config.optimizer_type == OptimizerType.MIPRO
        assert config.num_trials == 20


class TestCCLExample:
    """CCLExample のテスト"""
    
    # PURPOSE: 例の作成
    def test_example_creation(self):
        """例の作成"""
        ex = CCLExample(
            ccl="/noe+",
            context="テスト",
            expected_output="分析結果"
        )
        assert ex.ccl == "/noe+"
        assert ex.context == "テスト"


class TestMockOptimizer:
    """MockOptimizer のテスト"""
    
    # PURPOSE: モック最適化
    def test_mock_optimize(self):
        """モック最適化"""
        opt = MockOptimizer()
        examples = [
            CCLExample("/noe+", "ctx1", "out1"),
            CCLExample("/dia+", "ctx2", "out2"),
        ]
        result = opt.optimize("/noe+", examples)
        
        assert result.success is True
        assert result.accuracy == 0.85
        assert "[MOCK]" in result.optimized_prompt
        assert result.num_demos == 2


class TestGetOptimizer:
    """get_optimizer のテスト"""
    
    # PURPOSE: モックオプティマイザ取得
    def test_get_mock_optimizer(self):
        """モックオプティマイザ取得"""
        opt = get_optimizer(use_mock=True)
        assert isinstance(opt, MockOptimizer)


class TestDSPyAvailability:
    """DSPy 利用可能性のテスト"""
    
    # PURPOSE: DSPy 利用可能性チェック
    def test_is_dspy_available(self):
        """DSPy 利用可能性チェック"""
        # DSPy インストール済みなら True
        available = is_dspy_available()
        assert isinstance(available, bool)


class TestOptimizationResult:
    """OptimizationResult のテスト"""
    
    # PURPOSE: 成功結果
    def test_success_result(self):
        """成功結果"""
        config = OptimizationConfig()
        result = OptimizationResult(
            success=True,
            optimized_prompt="Optimized",
            accuracy=0.9,
            num_demos=5,
            config=config,
        )
        assert result.success is True
        assert result.accuracy == 0.9
        assert result.error is None
    
    # PURPOSE: エラー結果
    def test_error_result(self):
        """エラー結果"""
        config = OptimizationConfig()
        result = OptimizationResult(
            success=False,
            optimized_prompt="",
            accuracy=0.0,
            num_demos=0,
            config=config,
            error="Test error"
        )
        assert result.success is False
        assert result.error == "Test error"
