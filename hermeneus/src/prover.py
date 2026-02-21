# PROOF: [L2/インフラ] <- hermeneus/src/ Formal Prover Interface
"""
Hermēneus Prover — 形式的正確性検証

Python 型チェック (mypy) と形式証明 (Lean4) による
コード/出力の正確性保証。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import hashlib
import json
import sqlite3
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager


# =============================================================================
# Types
# =============================================================================

# PURPOSE: [L2-auto] 証明タイプ
class ProofType(Enum):
    """証明タイプ"""
    TYPE = "type"       # 型チェック (mypy)
    SCHEMA = "schema"   # スキーマ検証 (JSON)
    FORMAL = "formal"   # 形式証明 (Lean4)


# PURPOSE: [L2-auto] 証明ステータス
class ProofStatus(Enum):
    """証明ステータス"""
    VERIFIED = "verified"     # 検証成功
    FAILED = "failed"         # 検証失敗
    ERROR = "error"           # 検証エラー
    SKIPPED = "skipped"       # スキップ
    CACHED = "cached"         # キャッシュヒット


# PURPOSE: [L2-auto] 証明結果
@dataclass
class ProofResult:
    """証明結果"""
    verified: bool
    proof_type: ProofType
    status: ProofStatus
    confidence: float = 1.0
    details: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    cached: bool = False
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Prover Interface
# =============================================================================

# PURPOSE: [L2-auto] Prover 抽象インターフェース
class ProverInterface(ABC):
    """Prover 抽象インターフェース"""
    
    # PURPOSE: 証明タイプ
    @property
    # PURPOSE: [L2-auto] 証明タイプ
    @abstractmethod
    def proof_type(self) -> ProofType:
        """証明タイプ"""
        pass
    
    # PURPOSE: コード/主張を検証
    @abstractmethod
    def verify(
        self,
        code: str,
        claim: Optional[str] = None,
        **kwargs
    ) -> ProofResult:
        """コード/主張を検証"""
        pass
    
    # PURPOSE: Prover が利用可能か
    def is_available(self) -> bool:
        """Prover が利用可能か"""
        return True


# =============================================================================
# Mypy Prover
# =============================================================================
# PURPOSE: [L2-auto] Mypy 型チェッカー

class MypyProver(ProverInterface):
    """Mypy 型チェッカー
    
    Python コードの型安全性を検証する。
    """
    
    # PURPOSE: Initialize instance
    def __init__(
        self,
        strict: bool = True,
        python_version: str = "3.11",
        ignore_missing_imports: bool = True
    ):
        self.strict = strict
        self.python_version = python_version
        self.ignore_missing_imports = ignore_missing_imports
        self._mypy_available = self._check_mypy()
    
    # PURPOSE: Proof type
    @property
    def proof_type(self) -> ProofType:
        return ProofType.TYPE
    
    # PURPOSE: mypy が利用可能か確認
    def _check_mypy(self) -> bool:
        """mypy が利用可能か確認"""
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    # PURPOSE: Is available
    def is_available(self) -> bool:
        return self._mypy_available
    
    # PURPOSE: Python コードの型チェック
    def verify(
        self,
        code: str,
        claim: Optional[str] = None,
        **kwargs
    ) -> ProofResult:
        """Python コードの型チェック"""
        import time
        start = time.time()
        
        if not self._mypy_available:
            return ProofResult(
                verified=False,
                proof_type=ProofType.TYPE,
                status=ProofStatus.SKIPPED,
                details="mypy is not available",
                confidence=0.0
            )
        
        # 一時ファイルに書き込み
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            returncode, stdout, stderr = self._run_mypy(temp_path)
            errors, warnings = self._parse_output(stdout + stderr)
            
            execution_time = (time.time() - start) * 1000
            
            if returncode == 0 and not errors:
                return ProofResult(
                    verified=True,
                    proof_type=ProofType.TYPE,
                    status=ProofStatus.VERIFIED,
                    confidence=1.0,
                    details="Type check passed",
                    warnings=warnings,
                    execution_time_ms=execution_time
                )
            else:
                return ProofResult(
                    verified=False,
                    proof_type=ProofType.TYPE,
                    status=ProofStatus.FAILED,
                    confidence=0.0,
                    details=f"Type check failed with {len(errors)} errors",
                    errors=errors,
                    warnings=warnings,
                    execution_time_ms=execution_time
                )
        finally:
            temp_path.unlink(missing_ok=True)
    
    # PURPOSE: mypy を実行
    def _run_mypy(self, path: Path) -> Tuple[int, str, str]:
        """mypy を実行"""
        cmd = ["python", "-m", "mypy"]
        
        if self.strict:
            cmd.append("--strict")
        
        cmd.extend(["--python-version", self.python_version])
        
        if self.ignore_missing_imports:
            cmd.append("--ignore-missing-imports")
        
        cmd.append(str(path))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "mypy timed out"
    
    # PURPOSE: 出力をパース
    def _parse_output(self, output: str) -> Tuple[List[str], List[str]]:
        """出力をパース"""
        errors = []
        warnings = []
        
        for line in output.strip().split("\n"):
            if not line:
                continue
            if ": error:" in line:
                # ファイル名を除去
                parts = line.split(": error:", 1)
                if len(parts) == 2:
                    errors.append(parts[1].strip())
                else:
                    errors.append(line)
            elif ": warning:" in line or ": note:" in line:
                warnings.append(line)
        
        return errors, warnings


# =============================================================================
# Schema Prover
# =============================================================================
# PURPOSE: [L2-auto] スキーマ検証

class SchemaProver(ProverInterface):
    """スキーマ検証
    
    JSON 出力がスキーマに準拠しているか検証する。
    """
    
    # PURPOSE: Initialize instance
    def __init__(self):
        self._jsonschema_available = self._check_jsonschema()
    
    # PURPOSE: Proof type
    @property
    def proof_type(self) -> ProofType:
        return ProofType.SCHEMA
    
    # PURPOSE: jsonschema が利用可能か確認
    def _check_jsonschema(self) -> bool:
        """jsonschema が利用可能か確認"""
        try:
            import jsonschema  # noqa: F401
            return True
        except ImportError:
            return False
    
    # PURPOSE: Is available
    def is_available(self) -> bool:
        return self._jsonschema_available
    
    # PURPOSE: JSON をスキーマで検証
    def verify(
        self,
        code: str,
        claim: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ProofResult:
        """JSON をスキーマで検証"""
        import time
        start = time.time()
        
        if not schema:
            return ProofResult(
                verified=False,
                proof_type=ProofType.SCHEMA,
                status=ProofStatus.ERROR,
                details="No schema provided",
                confidence=0.0
            )
        
        try:
            data = json.loads(code)
        except json.JSONDecodeError as e:
            return ProofResult(
                verified=False,
                proof_type=ProofType.SCHEMA,
                status=ProofStatus.FAILED,
                details=f"Invalid JSON: {e}",
                errors=[str(e)],
                execution_time_ms=(time.time() - start) * 1000
            )
        
        if not self._jsonschema_available:
            # フォールバック: 必須フィールドのみチェック
            return self._fallback_validate(data, schema, start)
        
        import jsonschema
        
        try:
            jsonschema.validate(data, schema)
            return ProofResult(
                verified=True,
                proof_type=ProofType.SCHEMA,
                status=ProofStatus.VERIFIED,
                confidence=1.0,
                details="Schema validation passed",
                execution_time_ms=(time.time() - start) * 1000
            )
        except jsonschema.ValidationError as e:
            return ProofResult(
                verified=False,
                proof_type=ProofType.SCHEMA,
                status=ProofStatus.FAILED,
                details=f"Schema validation failed: {e.message}",
                errors=[e.message],
                execution_time_ms=(time.time() - start) * 1000
            )
    
    # PURPOSE: フォールバック検証
    def _fallback_validate(
        self,
        data: Dict,
        schema: Dict,
        start: float
    ) -> ProofResult:
        """フォールバック検証"""
        required = schema.get("required", [])
        missing = [f for f in required if f not in data]
        
        if missing:
            return ProofResult(
                verified=False,
                proof_type=ProofType.SCHEMA,
                status=ProofStatus.FAILED,
                details=f"Missing required fields: {missing}",
                errors=[f"Missing: {f}" for f in missing],
                execution_time_ms=(time.time() - start) * 1000
            )
        
        return ProofResult(
            verified=True,
            proof_type=ProofType.SCHEMA,
            status=ProofStatus.VERIFIED,
            confidence=0.8,  # フォールバックは確信度低め
            details="Fallback validation passed (required fields only)",
            execution_time_ms=(time.time() - start) * 1000
        )


# =============================================================================
# Lean4 Prover (オプション)
# =============================================================================
# PURPOSE: [L2-auto] Lean 4 形式証明

class Lean4Prover(ProverInterface):
    """Lean 4 形式証明
    
    数学的主張の形式証明を行う。
    """
    
    DEFAULT_LEAN_PATH = Path.home() / ".elan" / "bin" / "lean"
    
    # PURPOSE: Initialize instance
    def __init__(self, lean_path: Optional[Path] = None):
        self.lean_path = lean_path or self.DEFAULT_LEAN_PATH
        self._lean_available = self._check_lean()
    
    # PURPOSE: Proof type
    @property
    def proof_type(self) -> ProofType:
        return ProofType.FORMAL
    
    # PURPOSE: Lean 4 が利用可能か確認
    def _check_lean(self) -> bool:
        """Lean 4 が利用可能か確認"""
        if not self.lean_path.exists():
            return False
        
        try:
            result = subprocess.run(
                [str(self.lean_path), "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    # PURPOSE: Is available
    def is_available(self) -> bool:
        return self._lean_available
    
    # PURPOSE: 形式証明
    def verify(
        self,
        code: str,
        claim: Optional[str] = None,
        **kwargs
    ) -> ProofResult:
        """形式証明"""
        import time
        start = time.time()
        
        if not self._lean_available:
            return ProofResult(
                verified=False,
                proof_type=ProofType.FORMAL,
                status=ProofStatus.SKIPPED,
                details="Lean 4 is not available",
                confidence=0.0
            )
        
        # Lean 4 コードとして直接検証
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".lean",
            delete=False
        ) as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            result = subprocess.run(
                [str(self.lean_path), temp_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            execution_time = (time.time() - start) * 1000
            
            if result.returncode == 0:
                return ProofResult(
                    verified=True,
                    proof_type=ProofType.FORMAL,
                    status=ProofStatus.VERIFIED,
                    confidence=1.0,
                    details="Formal proof verified",
                    execution_time_ms=execution_time
                )
            else:
                errors = [
                    line for line in result.stderr.split("\n")
                    if "error" in line.lower()
                ]
                return ProofResult(
                    verified=False,
                    proof_type=ProofType.FORMAL,
                    status=ProofStatus.FAILED,
                    details="Formal proof failed",
                    errors=errors[:5],  # 最大5件
                    execution_time_ms=execution_time
                )
        except subprocess.TimeoutExpired:
            return ProofResult(
                verified=False,
                proof_type=ProofType.FORMAL,
                status=ProofStatus.ERROR,
                details="Lean 4 timed out",
                execution_time_ms=(time.time() - start) * 1000
            )
        finally:
            temp_path.unlink(missing_ok=True)


# =============================================================================
# Proof Cache
# =============================================================================
# PURPOSE: [L2-auto] 証明結果キャッシュ

class ProofCache:
    """証明結果キャッシュ"""
    
    DEFAULT_PATH = Path.home() / ".hermeneus" / "proof_cache.db"
    DEFAULT_TTL = 86400  # 24時間
    
    # PURPOSE: Initialize instance
    def __init__(
        self,
        db_path: Optional[Path] = None,
        ttl_seconds: int = DEFAULT_TTL
    ):
        self.db_path = db_path or self.DEFAULT_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self._init_db()
    
    # PURPOSE: データベースを初期化
    def _init_db(self):
        """データベースを初期化"""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proof_cache (
                    code_hash TEXT NOT NULL,
                    proof_type TEXT NOT NULL,
                    verified INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    details TEXT,
                    errors TEXT,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (code_hash, proof_type)
                )
            """)
            conn.commit()
    
    # PURPOSE: データベース接続
    @contextmanager
    def _connect(self):
        """データベース接続"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # PURPOSE: コードのハッシュ
    def _hash_code(self, code: str) -> str:
        """コードのハッシュ"""
        return hashlib.sha256(code.encode()).hexdigest()[:16]
    
    # PURPOSE: キャッシュから取得
    def get(
        self,
        code: str,
        proof_type: ProofType
    ) -> Optional[ProofResult]:
        """キャッシュから取得"""
        code_hash = self._hash_code(code)
        
        with self._connect() as conn:
            row = conn.execute("""
                SELECT * FROM proof_cache
                WHERE code_hash = ? AND proof_type = ?
            """, (code_hash, proof_type.value)).fetchone()
            
            if not row:
                return None
            
            # TTL チェック
            created = datetime.fromisoformat(row["created_at"])
            if datetime.now() - created > timedelta(seconds=self.ttl_seconds):
                self.invalidate(code, proof_type)
                return None
            
            return ProofResult(
                verified=bool(row["verified"]),
                proof_type=proof_type,
                status=ProofStatus.CACHED,
                confidence=row["confidence"],
                details=row["details"] or "",
                errors=json.loads(row["errors"]) if row["errors"] else [],
                cached=True
            )
    
    # PURPOSE: キャッシュに保存
    def put(self, code: str, result: ProofResult):
        """キャッシュに保存"""
        code_hash = self._hash_code(code)
        
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO proof_cache
                (code_hash, proof_type, verified, confidence, details, errors, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                code_hash,
                result.proof_type.value,
                1 if result.verified else 0,
                result.confidence,
                result.details,
                json.dumps(result.errors),
                datetime.now().isoformat()
            ))
            conn.commit()
    
    # PURPOSE: キャッシュを無効化
    def invalidate(self, code: str, proof_type: Optional[ProofType] = None):
        """キャッシュを無効化"""
        code_hash = self._hash_code(code)
        
        with self._connect() as conn:
            if proof_type:
                conn.execute("""
                    DELETE FROM proof_cache
                    WHERE code_hash = ? AND proof_type = ?
                """, (code_hash, proof_type.value))
            else:
                conn.execute("""
                    DELETE FROM proof_cache WHERE code_hash = ?
                """, (code_hash,))
            conn.commit()
    
    # PURPOSE: 期限切れを削除
    def clean_expired(self):
        """期限切れを削除"""
        threshold = datetime.now() - timedelta(seconds=self.ttl_seconds)
        
        with self._connect() as conn:
            conn.execute("""
                DELETE FROM proof_cache WHERE created_at < ?
            """, (threshold.isoformat(),))
            conn.commit()


# =============================================================================
# Convenience Functions
# =============================================================================

# PURPOSE: コードを検証 (便利関数)
def verify_code(
    code: str,
    prover: Optional[ProverInterface] = None,
    use_cache: bool = True,
    **kwargs
) -> ProofResult:
    """コードを検証 (便利関数)
    
    Args:
        code: 検証対象のコード
        prover: 使用するProver (デフォルト: MypyProver)
        use_cache: キャッシュを使用するか
        
    Returns:
        ProofResult
        
    Example:
        >>> result = verify_code("def add(x: int, y: int) -> int: return x + y")
        >>> print(result.verified)
    """
    if prover is None:
        prover = MypyProver()
    
    cache = ProofCache() if use_cache else None
    
    # キャッシュチェック
    if cache:
        cached_result = cache.get(code, prover.proof_type)
        if cached_result:
            return cached_result
    
    # 検証実行
    result = prover.verify(code, **kwargs)
    
    # キャッシュ保存
    if cache and result.status in (ProofStatus.VERIFIED, ProofStatus.FAILED):
        cache.put(code, result)
    
    return result


# PURPOSE: スキーマ検証 (便利関数)
def verify_schema(
    data: str,
    schema: Dict[str, Any],
    use_cache: bool = True
) -> ProofResult:
    """スキーマ検証 (便利関数)"""
    prover = SchemaProver()
    return verify_code(data, prover=prover, use_cache=use_cache, schema=schema)


# PURPOSE: Prover を取得
def get_prover(proof_type: ProofType) -> ProverInterface:
    """Prover を取得"""
    if proof_type == ProofType.TYPE:
        return MypyProver()
    elif proof_type == ProofType.SCHEMA:
        return SchemaProver()
    elif proof_type == ProofType.FORMAL:
        return Lean4Prover()
    else:
        raise ValueError(f"Unknown proof type: {proof_type}")
