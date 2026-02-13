# PROOF: [L2/インフラ] <- hermeneus/src/ Constrained Decoding
"""
Hermēneus Constraints — 構造化出力の強制

Outlines/vLLM による Grammar-Constrained Decoding (GCD) を提供。
JSON Schema に従った出力を保証する。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints
from enum import Enum


# =============================================================================
# Output Schema Definitions
# =============================================================================

# PURPOSE: [L2-auto] CCL 出力スキーマ
@dataclass
class CCLOutputSchema:
    """CCL 出力スキーマ"""
    result: str                              # 主要な出力
    confidence: float                        # 確信度 (0.0-1.0)
    reasoning: Optional[str] = None          # 推論過程
    alternatives: Optional[List[str]] = None # 代替案
    metadata: Optional[Dict[str, Any]] = None


# PURPOSE: [L2-auto] 収束ループ出力スキーマ
@dataclass
class ConvergenceOutputSchema:
    """収束ループ出力スキーマ"""
    final_result: str
    iterations: int
    converged: bool
    uncertainty: float
    intermediate_steps: List[str]


# PURPOSE: [L2-auto] シーケンス出力スキーマ
@dataclass
class SequenceOutputSchema:
    """シーケンス出力スキーマ"""
    steps: List[Dict[str, str]]
    final_result: str
    success: bool


# =============================================================================
# JSON Schema Generator
# =============================================================================

# PURPOSE: [L2-auto] Python dataclass から JSON Schema を生成
class SchemaGenerator:
    """Python dataclass から JSON Schema を生成"""
    
    TYPE_MAP = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        type(None): {"type": "null"},
    }
    
    # PURPOSE: dataclass から JSON Schema を生成
    @classmethod
    def from_dataclass(cls, dataclass_type: Type) -> Dict[str, Any]:
        """dataclass から JSON Schema を生成"""
        hints = get_type_hints(dataclass_type)
        
        properties = {}
        required = []
        
        for field_name, field_type in hints.items():
            # Optional 型の処理
            is_optional = False
            origin = getattr(field_type, "__origin__", None)
            
            if origin is Union:
                args = field_type.__args__
                if type(None) in args:
                    is_optional = True
                    # None 以外の型を取得
                    field_type = [a for a in args if a is not type(None)][0]
            
            # 型変換
            schema = cls._type_to_schema(field_type)
            properties[field_name] = schema
            
            if not is_optional:
                required.append(field_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False
        }
    
    # PURPOSE: Python 型を JSON Schema に変換
    @classmethod
    def _type_to_schema(cls, python_type: Type) -> Dict[str, Any]:
        """Python 型を JSON Schema に変換"""
        # 基本型
        if python_type in cls.TYPE_MAP:
            return cls.TYPE_MAP[python_type]
        
        # List
        origin = getattr(python_type, "__origin__", None)
        if origin is list:
            item_type = python_type.__args__[0] if python_type.__args__ else str
            return {
                "type": "array",
                "items": cls._type_to_schema(item_type)
            }
        
        # Dict
        if origin is dict:
            return {
                "type": "object",
                "additionalProperties": True
            }
        
        # Enum
        if isinstance(python_type, type) and issubclass(python_type, Enum):
            return {
                "type": "string",
                "enum": [e.value for e in python_type]
            }
        
        # デフォルト
        return {"type": "string"}


# =============================================================================
# Constrained Decoder
# =============================================================================

# PURPOSE: [L2-auto] Constrained Decoding を使用した出力生成
class ConstrainedDecoder:
    """Constrained Decoding を使用した出力生成
    
    Outlines がインストールされている場合は使用し、
    なければ正規表現ベースのフォールバックを使用。
    """
    
    # PURPOSE: Initialize instance
    def __init__(self, model: str = "openai/gpt-4o"):
        self.model = model
        self._outlines_available = self._check_outlines()
    
    # PURPOSE: Outlines がインストールされているか確認
    def _check_outlines(self) -> bool:
        """Outlines がインストールされているか確認"""
        try:
            import outlines  # noqa: F401
            return True
        except ImportError:
            return False
    
    # PURPOSE: JSON Schema に従った出力を生成
    def generate_with_schema(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """JSON Schema に従った出力を生成"""
        if self._outlines_available:
            return self._generate_with_outlines(prompt, schema, **kwargs)
        else:
            return self._generate_with_fallback(prompt, schema, **kwargs)
    
    # PURPOSE: dataclass 型に従った出力を生成
    def generate_with_dataclass(
        self,
        prompt: str,
        dataclass_type: Type,
        **kwargs
    ) -> Any:
        """dataclass 型に従った出力を生成"""
        schema = SchemaGenerator.from_dataclass(dataclass_type)
        result = self.generate_with_schema(prompt, schema, **kwargs)
        return dataclass_type(**result)
    
    # PURPOSE: Outlines を使用して生成
    def _generate_with_outlines(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Outlines を使用して生成"""
        from outlines import generate, models
        
        # モデルをロード
        model = models.openai(self.model.replace("openai/", ""))
        
        # JSON 生成器を作成
        generator = generate.json(model, schema)
        
        # 生成
        result = generator(prompt)
        return result
    
    # PURPOSE: フォールバック: プロンプトに Schema を含めて生成
    def _generate_with_fallback(
        self,
        prompt: str,
        schema: Dict[str, Any],
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """フォールバック: プロンプトに Schema を含めて生成"""
        import os
        
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("OpenAI SDK not installed. Run: pip install openai")
        
        api_key = kwargs.get("api_key") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        client = OpenAI(api_key=api_key)
        
        # Schema をプロンプトに含める
        schema_prompt = f"""
以下の JSON Schema に厳密に従った JSON のみを出力してください。
コードブロックや説明は不要です。純粋な JSON のみ出力してください。

JSON Schema:
```json
{json.dumps(schema, indent=2, ensure_ascii=False)}
```

タスク:
{prompt}

JSON 出力:
"""
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model.replace("openai/", ""),
                    messages=[{"role": "user", "content": schema_prompt}],
                    temperature=0.3,  # 低めの温度で一貫性を高める
                )
                
                content = response.choices[0].message.content
                
                # JSON を抽出してパース
                result = self._extract_and_parse_json(content)
                
                # スキーマ検証
                if self._validate_against_schema(result, schema):
                    return result
                
            except json.JSONDecodeError:
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse JSON after {max_retries} attempts")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
        
        raise ValueError("Failed to generate valid JSON output")
    
    # PURPOSE: 出力から JSON を抽出してパース
    def _extract_and_parse_json(self, content: str) -> Dict[str, Any]:
        """出力から JSON を抽出してパース"""
        # コードブロックを除去
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        # JSON パース
        return json.loads(content)
    
    # PURPOSE: 簡易スキーマ検証
    def _validate_against_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> bool:
        """簡易スキーマ検証"""
        # 必須フィールドの確認
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False
        
        # プロパティの型確認
        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get("type")
                actual_value = data[field]
                
                if expected_type == "string" and not isinstance(actual_value, str):
                    return False
                elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                    return False
                elif expected_type == "integer" and not isinstance(actual_value, int):
                    return False
                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    return False
                elif expected_type == "array" and not isinstance(actual_value, list):
                    return False
                elif expected_type == "object" and not isinstance(actual_value, dict):
                    return False
        
        return True


# =============================================================================
# Convenience Functions
# =============================================================================

# PURPOSE: 型安全な出力生成 (便利関数)
def generate_constrained(
    prompt: str,
    output_type: Type,
    model: str = "openai/gpt-4o",
    **kwargs
) -> Any:
    """型安全な出力生成 (便利関数)
    
    Args:
        prompt: 入力プロンプト
        output_type: 出力の dataclass 型
        model: 使用する LLM モデル
        
    Returns:
        output_type のインスタンス
        
    Example:
        >>> result = generate_constrained(
        ...     "プロジェクトを分析して",
        ...     CCLOutputSchema
        ... )
        >>> print(result.confidence)
    """
    decoder = ConstrainedDecoder(model=model)
    return decoder.generate_with_dataclass(prompt, output_type, **kwargs)


# PURPOSE: JSON Schema に従った出力生成 (便利関数)
def generate_json(
    prompt: str,
    schema: Dict[str, Any],
    model: str = "openai/gpt-4o",
    **kwargs
) -> Dict[str, Any]:
    """JSON Schema に従った出力生成 (便利関数)"""
    decoder = ConstrainedDecoder(model=model)
    return decoder.generate_with_schema(prompt, schema, **kwargs)
