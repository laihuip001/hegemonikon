# PROOF: [L2/インフラ]  # noqa: AI-022
"""
Dendron Checker — PROOF 検証ロジック

L0 (ディレクトリ) と L1 (ファイル) の存在証明を検証する。
"""

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Set
import re


class ProofStatus(Enum):
    """PROOF 状態"""

    OK = "ok"  # 存在証明あり (親参照付き)
    MISSING = "missing"  # 存在証明なし
    INVALID = "invalid"  # 形式不正
    EXEMPT = "exempt"  # 除外対象
    ORPHAN = "orphan"  # 親参照なし (v2 警告)


class ProofLevel(Enum):
    """PROOF レベル"""

    L1 = "L1"  # 定理
    L2 = "L2"  # インフラ
    L3 = "L3"  # テスト
    UNKNOWN = "unknown"


@dataclass
class FileProof:
    """ファイルの存在証明情報"""

    path: Path
    status: ProofStatus
    level: Optional[ProofLevel] = None
    parent: Optional[str] = None  # v2: 親参照
    reason: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class DirProof:
    """ディレクトリの存在証明情報"""

    path: Path
    status: ProofStatus
    has_proof_md: bool = False
    reason: Optional[str] = None


@dataclass
class CheckResult:
    """チェック結果"""

    total_files: int
    files_with_proof: int
    files_missing_proof: int
    files_invalid_proof: int
    files_exempt: int
    files_orphan: int  # v2: 親参照なし
    file_proofs: List[FileProof]
    dir_proofs: List[DirProof]
    level_stats: Dict[str, int] = field(default_factory=dict)  # L1/L2/L3 統計

    @property
    def coverage(self) -> float:
        """カバレッジ率 (v2: ORPHAN も OK 扱い)"""
        checkable = self.total_files - self.files_exempt
        if checkable == 0:
            return 100.0
        # v2: ORPHAN は PROOF あり扱い
        with_proof = self.files_with_proof + self.files_orphan
        return (with_proof / checkable) * 100

    @property
    def is_passing(self) -> bool:
        """CI で PASS するか (v2: ORPHAN は警告のみ)"""
        return self.files_missing_proof == 0 and self.files_invalid_proof == 0


# 除外パターン
EXEMPT_PATTERNS = [
    r"__pycache__",
    r"\.pyc$",
    r"\.git",
    r"\.egg-info",
    r"\.venv",  # 仮想環境を除外
]

# PROOF ヘッダーパターン (v1)
PROOF_PATTERN = re.compile(r"#\s*PROOF:\s*\[([^\]]+)\]")

# PROOF ヘッダーパターン (v2: 親参照付き、任意の後続テキスト許容)
# 形式: # PROOF: [レベル] または # PROOF: [レベル] <- 親
PROOF_PATTERN_V2 = re.compile(r"#\s*PROOF:\s*\[([^\]]+)\](?:\s*<-\s*([^\s#]+))?")

# 特殊親参照
SPECIAL_PARENTS = {"FEP", "external", "legacy"}

# PROOF.md パターン
PROOF_MD_PATTERN = re.compile(r"^PROOF\.md$", re.IGNORECASE)


class DendronChecker:  # noqa: AI-007
    """Dendron PROOF チェッカー"""

    def __init__(
        self,
        exempt_patterns: List[str] = None,
        check_dirs: bool = True,
        check_files: bool = True,
    ):
        self.exempt_patterns = [re.compile(p) for p in (exempt_patterns or EXEMPT_PATTERNS)]
        self.check_dirs = check_dirs
        self.check_files = check_files

    def is_exempt(self, path: Path) -> bool:
        """除外対象かどうか"""
        path_str = str(path)
        return any(p.search(path_str) for p in self.exempt_patterns)

    def check_file_proof(self, path: Path) -> FileProof:
        """ファイルの PROOF ヘッダーをチェック (v2: 親参照対応)"""
        if self.is_exempt(path):
            return FileProof(path=path, status=ProofStatus.EXEMPT)

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return FileProof(path=path, status=ProofStatus.INVALID, reason=f"読み込みエラー: {e}")

        # 最初の 10 行を検索
        lines = content.split("\n")[:10]
        for i, line in enumerate(lines, 1):
            # v2 パターン (親参照付き) を優先
            match_v2 = PROOF_PATTERN_V2.search(line)
            if match_v2:
                level_str = match_v2.group(1)
                parent = match_v2.group(2)
                level = self._parse_level(level_str)
                
                if parent:
                    # 親参照あり → OK
                    parent = parent.strip()
                    return FileProof(
                        path=path, status=ProofStatus.OK, 
                        level=level, parent=parent, line_number=i
                    )
                else:
                    # 親参照なし → ORPHAN (v2 警告)
                    return FileProof(
                        path=path, status=ProofStatus.ORPHAN, 
                        level=level, line_number=i,
                        reason="親参照なし (v2: <- parent 必須)"
                    )

        return FileProof(path=path, status=ProofStatus.MISSING, reason="PROOF ヘッダーなし")

    def check_dir_proof(self, path: Path) -> DirProof:
        """ディレクトリの PROOF.md をチェック"""
        if self.is_exempt(path):
            return DirProof(path=path, status=ProofStatus.EXEMPT)

        proof_md = path / "PROOF.md"
        if proof_md.exists():
            return DirProof(path=path, status=ProofStatus.OK, has_proof_md=True)

        return DirProof(
            path=path, status=ProofStatus.MISSING, has_proof_md=False, reason="PROOF.md なし"
        )

    def _parse_level(self, level_str: str) -> ProofLevel:  # noqa: AI-007
        """レベル文字列をパース"""
        level_str = level_str.upper()
        if "L1" in level_str:
            return ProofLevel.L1
        elif "L2" in level_str:
            return ProofLevel.L2
        elif "L3" in level_str:
            return ProofLevel.L3
        return ProofLevel.UNKNOWN

    def check(self, root: Path) -> CheckResult:  # noqa: AI-007
        """ディレクトリツリーをチェック"""
        root = Path(root)

        file_proofs: List[FileProof] = []
        dir_proofs: List[DirProof] = []

        # ディレクトリをチェック
        if self.check_dirs:
            for path in root.rglob("*"):
                if path.is_dir() and not self.is_exempt(path):
                    dir_proofs.append(self.check_dir_proof(path))

        # ファイルをチェック
        if self.check_files:
            for path in root.rglob("*.py"):
                if path.is_file():
                    file_proofs.append(self.check_file_proof(path))

        # 集計
        total = len(file_proofs)
        ok = sum(1 for f in file_proofs if f.status == ProofStatus.OK)
        missing = sum(1 for f in file_proofs if f.status == ProofStatus.MISSING)
        invalid = sum(1 for f in file_proofs if f.status == ProofStatus.INVALID)
        exempt = sum(1 for f in file_proofs if f.status == ProofStatus.EXEMPT)
        orphan = sum(1 for f in file_proofs if f.status == ProofStatus.ORPHAN)  # v2

        # レベル統計 (OK + ORPHAN を含む)
        level_counter: Counter = Counter()
        for fp in file_proofs:
            if fp.status in (ProofStatus.OK, ProofStatus.ORPHAN) and fp.level:
                level_counter[fp.level.value] += 1
        level_stats = dict(level_counter)

        return CheckResult(
            total_files=total,
            files_with_proof=ok,
            files_missing_proof=missing,
            files_invalid_proof=invalid,
            files_exempt=exempt,
            files_orphan=orphan,
            file_proofs=file_proofs,
            dir_proofs=dir_proofs,
            level_stats=level_stats,
        )


# テスト用
if __name__ == "__main__":
    from pathlib import Path

    checker = DendronChecker()
    result = checker.check(Path("."))

    print(f"Total files: {result.total_files}")
    print(f"With proof: {result.files_with_proof}")
    print(f"Missing: {result.files_missing_proof}")
    print(f"Coverage: {result.coverage:.1f}%")
    print(f"Passing: {result.is_passing}")
