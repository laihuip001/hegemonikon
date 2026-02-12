# PROOF: [L3/テスト] <- hermeneus/tests/ Hermēneus Prover テスト
"""
Hermēneus Prover Unit Tests

Phase 4b: Formal Prover のテスト
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.prover import ProofType, ProofStatus, ProofResult, MypyProver, SchemaProver, Lean4Prover, ProofCache, verify_code, verify_schema


class TestProofType:
    """ProofType のテスト"""
    
    # PURPOSE: タイプ列挙
    def test_types(self):
        """タイプ列挙"""
        assert ProofType.TYPE.value == "type"
        assert ProofType.SCHEMA.value == "schema"
        assert ProofType.FORMAL.value == "formal"


class TestProofStatus:
    """ProofStatus のテスト"""
    
    # PURPOSE: ステータス列挙
    def test_statuses(self):
        """ステータス列挙"""
        assert ProofStatus.VERIFIED.value == "verified"
        assert ProofStatus.FAILED.value == "failed"
        assert ProofStatus.CACHED.value == "cached"


class TestProofResult:
    """ProofResult のテスト"""
    
    # PURPOSE: 結果作成
    def test_create_result(self):
        """結果作成"""
        result = ProofResult(
            verified=True,
            proof_type=ProofType.TYPE,
            status=ProofStatus.VERIFIED,
            confidence=1.0
        )
        assert result.verified is True
        assert result.confidence == 1.0


class TestMypyProver:
    """MypyProver のテスト"""
    
    # PURPOSE: Prover 作成
    def test_create_prover(self):
        """Prover 作成"""
        prover = MypyProver()
        assert prover.proof_type == ProofType.TYPE
    
    # PURPOSE: 有効なコードの検証
    def test_verify_valid_code(self):
        """有効なコードの検証"""
        prover = MypyProver(strict=False)
        
        if not prover.is_available():
            pytest.skip("mypy not available")
        
        code = '''
def add(x: int, y: int) -> int:
    return x + y
'''
        result = prover.verify(code)
        assert result.verified is True
        assert result.proof_type == ProofType.TYPE
    
    # PURPOSE: 無効なコードの検証
    def test_verify_invalid_code(self):
        """無効なコードの検証"""
        prover = MypyProver(strict=True)
        
        if not prover.is_available():
            pytest.skip("mypy not available")
        
        code = '''
def add(x: int, y: int) -> int:
    return "not an int"  # type error
'''
        result = prover.verify(code)
        assert result.verified is False
        assert len(result.errors) > 0


class TestSchemaProver:
    """SchemaProver のテスト"""
    
    # PURPOSE: Prover 作成
    def test_create_prover(self):
        """Prover 作成"""
        prover = SchemaProver()
        assert prover.proof_type == ProofType.SCHEMA
    
    # PURPOSE: 有効な JSON の検証
    def test_verify_valid_json(self):
        """有効な JSON の検証"""
        prover = SchemaProver()
        
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        
        data = json.dumps({"name": "Alice", "age": 30})
        result = prover.verify(data, schema=schema)
        
        assert result.verified is True
    
    # PURPOSE: 無効な JSON の検証
    def test_verify_invalid_json(self):
        """無効な JSON の検証"""
        prover = SchemaProver()
        
        schema = {"type": "object"}
        result = prover.verify("not valid json", schema=schema)
        assert result.verified is False
        assert "Invalid JSON" in result.details
    
    # PURPOSE: 必須フィールド欠落
    def test_verify_missing_required(self):
        """必須フィールド欠落"""
        prover = SchemaProver()
        
        schema = {
            "type": "object",
            "required": ["name", "age"]
        }
        
        data = json.dumps({"name": "Alice"})  # age missing
        result = prover.verify(data, schema=schema)
        
        # jsonschema がない場合はフォールバック検証
        if prover.is_available():
            assert result.verified is False


class TestLean4Prover:
    """Lean4Prover のテスト"""
    
    # PURPOSE: Prover 作成
    def test_create_prover(self):
        """Prover 作成"""
        prover = Lean4Prover()
        assert prover.proof_type == ProofType.FORMAL
    
    # PURPOSE: Lean4 が利用不可の場合
    def test_not_available(self):
        """Lean4 が利用不可の場合"""
        prover = Lean4Prover(lean_path=Path("/nonexistent/lean"))
        assert prover.is_available() is False
        
        result = prover.verify("theorem test : 1 + 1 = 2 := rfl")
        assert result.status == ProofStatus.SKIPPED


class TestProofCache:
    """ProofCache のテスト"""
    
    # PURPOSE: 一時キャッシュ
    @pytest.fixture
    def temp_cache(self, tmp_path):
        """一時キャッシュ"""
        db_path = tmp_path / "test_proof.db"
        return ProofCache(db_path=db_path)
    
    # PURPOSE: 保存と取得
    def test_put_and_get(self, temp_cache):
        """保存と取得"""
        code = "def test(): pass"
        result = ProofResult(
            verified=True,
            proof_type=ProofType.TYPE,
            status=ProofStatus.VERIFIED,
            confidence=1.0,
            details="test"
        )
        
        temp_cache.put(code, result)
        
        cached = temp_cache.get(code, ProofType.TYPE)
        assert cached is not None
        assert cached.verified is True
        assert cached.cached is True
    
    # PURPOSE: キャッシュミス
    def test_cache_miss(self, temp_cache):
        """キャッシュミス"""
        cached = temp_cache.get("unknown code", ProofType.TYPE)
        assert cached is None
    
    # PURPOSE: 無効化
    def test_invalidate(self, temp_cache):
        """無効化"""
        code = "def test(): pass"
        result = ProofResult(
            verified=True,
            proof_type=ProofType.TYPE,
            status=ProofStatus.VERIFIED
        )
        
        temp_cache.put(code, result)
        temp_cache.invalidate(code, ProofType.TYPE)
        
        cached = temp_cache.get(code, ProofType.TYPE)
        assert cached is None


class TestVerifyCode:
    """verify_code 関数のテスト"""
    
    # PURPOSE: デフォルト Prover で検証
    def test_verify_with_default_prover(self):
        """デフォルト Prover で検証"""
        code = '''
def greet(name: str) -> str:
    return f"Hello, {name}"
'''
        result = verify_code(code, use_cache=False)
        
        # mypy があれば検証、なければスキップ
        assert result.proof_type == ProofType.TYPE


class TestVerifySchema:
    """verify_schema 関数のテスト"""
    
    # PURPOSE: 有効なスキーマで検証
    def test_verify_valid_schema(self):
        """有効なスキーマで検証"""
        data = json.dumps({"id": 1, "name": "test"})
        schema = {
            "type": "object",
            "required": ["id", "name"]
        }
        
        result = verify_schema(data, schema, use_cache=False)
        assert result.proof_type == ProofType.SCHEMA


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
