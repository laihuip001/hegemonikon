# PROOF: [L2/インフラ] <- mekhane/dendron/
"""
Dendron Models — データ型・定数・パターン

checker.py から分離したモデル層。
Enum, Dataclass, 検証パターン, 定数をここに集約する。
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict
import re


# PURPOSE: チェック結果の分類と後続処理の分岐を可能にする
class ProofStatus(Enum):
    """PROOF 状態"""

    OK = "ok"
    MISSING = "missing"
    INVALID = "invalid"
    EXEMPT = "exempt"
    ORPHAN = "orphan"  # v2: 親参照なし
    WEAK = "weak"  # v2.6: 弱い Purpose


# PURPOSE: 検証対象の粒度 (ディレクトリ/ファイル/関数/変数) を識別し、統計分類を可能にする
class ProofLevel(Enum):
    """PROOF レベル (Depth Layer)

    マトリクス構造の「深さ」軸:
    - L0: ディレクトリ (Kairos - 文脈)
    - L1: ファイル (Ousia/Schema - 本質)
    - L2: 関数・クラス (Hormē/Perigraphē - 動機)
    - L3: 変数・字句 (Akribeia - 精密)
    """

    L0 = "L0"  # ディレクトリ / 文脈
    L1 = "L1"  # 定理 / 本質
    L2 = "L2"  # インフラ / 動機
    L3 = "L3"  # 変数・字句 / 精密
    UNKNOWN = "unknown"


# PURPOSE: ファイル単位のチェック結果を統一的に扱い、レポート生成とCI判定に渡す
@dataclass
class FileProof:
    """ファイルの存在証明情報"""

    path: Path
    status: ProofStatus
    level: Optional[ProofLevel] = None
    parent: Optional[str] = None
    reason: Optional[str] = None
    line_number: Optional[int] = None


# PURPOSE: 関数単位のチェック結果を統一的に扱い、品質評価を可能にする
@dataclass
class FunctionProof:
    """関数の存在証明情報 (L2 Purpose)"""

    name: str
    path: Path
    line_number: int
    status: ProofStatus
    purpose_text: Optional[str] = None
    reason: Optional[str] = None
    is_private: bool = False
    is_dunder: bool = False
    quality_issue: Optional[str] = None  # v2.6: WEAK の理由


# PURPOSE: 変数・字句レベル (L3) のチェック結果を統一的に扱い、精密性の表層検証を行う
@dataclass
class VariableProof:
    """変数・字句の存在証明情報 (L3 Akribeia)"""

    name: str
    path: Path
    line_number: int
    status: ProofStatus  # OK / MISSING / WEAK
    check_type: str  # "type_hint" / "short_name"
    reason: Optional[str] = None


# PURPOSE: ディレクトリ単位のチェック結果を統一的に扱い、PROOF.md の有無を判定する
@dataclass
class DirProof:
    """ディレクトリの存在証明情報"""

    path: Path
    status: ProofStatus
    has_proof_md: bool = False
    reason: Optional[str] = None


# PURPOSE: ディレクトリツリー全体のチェック結果を集計するデータクラス
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

    # v2.5 L2 Purpose 統計
    total_functions: int = 0
    functions_with_purpose: int = 0
    functions_missing_purpose: int = 0
    functions_weak_purpose: int = 0  # v2.6: WEAK 品質の Purpose 数
    function_proofs: List[FunctionProof] = field(default_factory=list)

    # v3.0 L3 Variable 統計
    total_checked_signatures: int = 0
    signatures_with_hints: int = 0
    signatures_missing_hints: int = 0
    short_name_violations: int = 0
    variable_proofs: List[VariableProof] = field(default_factory=list)

    level_stats: Dict[str, int] = field(default_factory=dict)  # L1/L2/L3 統計

    # PURPOSE: チェック対象ファイル全体に対する証明カバレッジ率を計算する
    @property
    def coverage(self) -> float:
        """カバレッジ率 (v2: ORPHAN も OK 扱い)"""
        checkable = self.total_files - self.files_exempt
        if checkable == 0:
            return 100.0
        # v2: ORPHAN は PROOF あり扱い
        with_proof = self.files_with_proof + self.files_orphan
        return (with_proof / checkable) * 100

    # PURPOSE: CI パイプラインでの合否判定を行う (Phase 1: 警告のみ)
    @property
    def is_passing(self) -> bool:
        """CI で PASS するか (v2: ORPHAN は警告のみ)"""
        # Phase 1: Function Purpose missing はまだエラーにしない
        return self.files_missing_proof == 0 and self.files_invalid_proof == 0


# ─── 定数・パターン ──────────────────────────────

# 除外パターン
EXEMPT_PATTERNS = [
    r"__pycache__",
    r"\.pyc$",
    r"\.git",
    r"\.egg-info",
    r"\.venv",  # 仮想環境を除外
    r"tests/",  # テストコードは Purpose 対象外
    r"test_",  # テストファイル
    r"\.codex/",  # Codex 自動生成スクリプト
    r"\.agent/scripts/",  # エージェント補助スクリプト
    r"experiments/",  # 実験コード (PROOF 不要)
]

# PROOF ヘッダーパターン (v2: 親参照付き、任意の後続テキスト許容)
# 形式: # PROOF: [レベル] または # PROOF: [レベル] <- 親
PROOF_PATTERN_V2 = re.compile(r"#\s*PROOF:\s*\[([^\]]+)\](?:\s*<-\s*([^\s#]+))?")

# PURPOSE ヘッダーパターン (v2.5: 関数直前コメント)
# 形式: # PURPOSE: 目的の説明
PURPOSE_PATTERN = re.compile(r"#\s*PURPOSE:\s*(.+)")

# v2.6: 弱い Purpose パターン (WHAT であり WHY ではない)
WEAK_PURPOSE_PATTERNS = [
    (re.compile(r"を表す"), "WHAT: 'を表す' → 'を可能にする' etc."),
    (re.compile(r"を保持する"), "WHAT: 'を保持する' → 'を統一的に扱う' etc."),
    (re.compile(r"を提供する"), "WHAT: 'を提供する' → 'を生成する' etc."),
    (re.compile(r"を定義する$"), "WHAT: 'を定義する' → 'を可能にする' etc."),
    (re.compile(r"^データクラス$"), "WHAT: 具体的な目的がない"),
    (re.compile(r"^列挙型$"), "WHAT: 具体的な目的がない"),
    # v3.0: 英語 WEAK パターン (/dia+ レビューで追加)
    (
        re.compile(r"^Represents?\b", re.IGNORECASE),
        "WHAT: 'Represents' → state WHY it exists",
    ),
    (re.compile(r"^Holds?\b", re.IGNORECASE), "WHAT: 'Holds' → state WHY it's needed"),
    (
        re.compile(r"^Provides?\b", re.IGNORECASE),
        "WHAT: 'Provides' → state WHY it matters",
    ),
    (
        re.compile(r"^Defines?\b", re.IGNORECASE),
        "WHAT: 'Defines' → state WHY it enables",
    ),
]

# 特殊親参照 (バリデーションをスキップ)
SPECIAL_PARENTS = {"FEP", "external", "legacy"}

# 有効なレベルプレフィックス (v2.2: 厳密検証, v3.0: L0追加)
VALID_LEVEL_PREFIXES = {"L0", "L1", "L2", "L3"}

# 最大ファイルサイズ (v2.2: リソース枯渇防止)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# PROOF.md パターン
PROOF_MD_PATTERN = re.compile(r"^PROOF\.md$", re.IGNORECASE)
