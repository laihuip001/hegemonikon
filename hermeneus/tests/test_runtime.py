# PROOF: [L3/テスト] <- hermeneus/tests/ Hermēneus ランタイムテスト
"""
Hermēneus Runtime Unit Tests

Phase 2: LMQL ランタイム統合のテスト
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src import compile_ccl
from hermeneus.src.constraints import CCLOutputSchema, SchemaGenerator, ConstrainedDecoder
from hermeneus.src.runtime import ExecutionStatus, ExecutionResult, ExecutionConfig, LMQLExecutor, ConvergenceExecutor


class TestExecutionConfig:
    """ExecutionConfig のテスト"""
    
    def test_default_config(self):
        """デフォルト設定"""
        config = ExecutionConfig()
        assert config.model == "openai/gpt-4o"
        assert config.timeout == 300
        assert config.max_retries == 3
    
    def test_custom_config(self):
        """カスタム設定"""
        config = ExecutionConfig(
            model="openai/gpt-3.5-turbo",
            timeout=60,
            max_retries=5
        )
        assert config.model == "openai/gpt-3.5-turbo"
        assert config.timeout == 60


class TestLMQLExecutor:
    """LMQLExecutor のテスト"""
    
    def test_executor_creation(self):
        """Executor 作成"""
        executor = LMQLExecutor()
        assert executor.config.model == "openai/gpt-4o"
    
    def test_executor_with_config(self):
        """カスタム設定で Executor 作成"""
        config = ExecutionConfig(model="openai/gpt-3.5-turbo")
        executor = LMQLExecutor(config)
        assert executor.config.model == "openai/gpt-3.5-turbo"
    
    def test_extract_prompt_from_lmql(self):
        """LMQL からプロンプト抽出"""
        executor = LMQLExecutor()
        lmql_code = '''
@lmql.query
def ccl_noe(context: str):
    argmax
        "深い認識を実行"
        "コンテキスト: {context}"
'''
        prompt = executor._extract_prompt_from_lmql(lmql_code)
        assert prompt is not None
        assert "深い認識" in prompt


class TestConvergenceExecutor:
    """ConvergenceExecutor のテスト"""
    
    def test_estimate_uncertainty_high(self):
        """高不確実性の推定"""
        executor = LMQLExecutor()
        conv_executor = ConvergenceExecutor(executor)
        
        output = "これは推測ですが、おそらく正しいかもしれません。不明な点もあります。"
        uncertainty = conv_executor._estimate_uncertainty(output)
        assert uncertainty > 0.5
    
    def test_estimate_uncertainty_low(self):
        """低不確実性の推定"""
        executor = LMQLExecutor()
        conv_executor = ConvergenceExecutor(executor)
        
        output = "結論として、この分析は確実に正しい。したがって、definitively 成功です。"
        uncertainty = conv_executor._estimate_uncertainty(output)
        assert uncertainty < 0.5
    
    def test_check_condition_less_than(self):
        """条件チェック: <"""
        executor = LMQLExecutor()
        conv_executor = ConvergenceExecutor(executor)
        
        assert conv_executor._check_condition(0.2, "<", 0.3) is True
        assert conv_executor._check_condition(0.4, "<", 0.3) is False
    
    def test_check_condition_greater_than(self):
        """条件チェック: >"""
        executor = LMQLExecutor()
        conv_executor = ConvergenceExecutor(executor)
        
        assert conv_executor._check_condition(0.5, ">", 0.3) is True
        assert conv_executor._check_condition(0.2, ">", 0.3) is False


class TestSchemaGenerator:
    """SchemaGenerator のテスト"""
    
    def test_generate_from_ccl_output_schema(self):
        """CCLOutputSchema から JSON Schema 生成"""
        schema = SchemaGenerator.from_dataclass(CCLOutputSchema)
        
        assert schema["type"] == "object"
        assert "result" in schema["properties"]
        assert "confidence" in schema["properties"]
        assert "result" in schema["required"]
        assert "confidence" in schema["required"]
    
    def test_optional_fields_not_required(self):
        """Optional フィールドは required に含まれない"""
        schema = SchemaGenerator.from_dataclass(CCLOutputSchema)
        
        # reasoning は Optional なので required に含まれない
        assert "reasoning" not in schema["required"]


class TestConstrainedDecoder:
    """ConstrainedDecoder のテスト"""
    
    def test_decoder_creation(self):
        """Decoder 作成"""
        decoder = ConstrainedDecoder()
        assert decoder.model == "openai/gpt-4o"
    
    def test_validate_against_schema_valid(self):
        """スキーマ検証: 有効"""
        decoder = ConstrainedDecoder()
        
        schema = {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["result", "confidence"]
        }
        
        data = {"result": "test", "confidence": 0.9}
        assert decoder._validate_against_schema(data, schema) is True
    
    def test_validate_against_schema_missing_required(self):
        """スキーマ検証: 必須フィールド欠落"""
        decoder = ConstrainedDecoder()
        
        schema = {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["result", "confidence"]
        }
        
        data = {"result": "test"}  # confidence が欠落
        assert decoder._validate_against_schema(data, schema) is False
    
    def test_extract_and_parse_json(self):
        """JSON 抽出とパース"""
        decoder = ConstrainedDecoder()
        
        content = '```json\n{"result": "test"}\n```'
        result = decoder._extract_and_parse_json(content)
        assert result == {"result": "test"}


class TestIntegration:
    """統合テスト"""
    
    def test_compile_and_structure(self):
        """コンパイル結果の構造"""
        lmql_code = compile_ccl("/noe+")
        
        assert "@lmql.query" in lmql_code
        assert "ccl_noe" in lmql_code
        assert "argmax" in lmql_code


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
