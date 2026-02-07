# PROOF: [L2/インフラ] <- mekhane/dendron/  # noqa: AI-022
"""
Dendron Checker — PROOF 検証ロジック

L0 (ディレクトリ) と L1 (ファイル) の存在証明を検証する。
v2.5: L2 (関数/クラス) の # PURPOSE: 検証を追加
"""

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Set
import re
import ast


# PURPOSE: チェック結果の分類と後続処理の分岐を可能にする
class ProofStatus(Enum):
    """PROOF 状態"""

    OK = "ok"  # 存在証明あり (親参照付き)
    MISSING = "missing"  # 存在証明なし
    INVALID = "invalid"  # 形式不正
    EXEMPT = "exempt"  # 除外対象
    ORPHAN = "orphan"  # 親参照なし (v2 警告)
    WEAK = "weak"  # v2.6: Purpose あるが品質が低い


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
    L3 = "L3"  # テスト / 精密
    UNKNOWN = "unknown"


# PURPOSE: 将来的な多軸検証 (表層→構造→機能→実証) の拡張ポイントを確保する
class MetaLayer(Enum):
    """Meta Layer (検証の種類)
    
    マトリクス構造の「検証」軸:
    - SURFACE: 表層 - 何があるか（PROOF ヘッダー）
    - STRUCTURE: 構造層 - どう繋がるか（import graph）
    - FUNCTION: 機能層 - 何が同じか（類似度）
    - VERIFICATION: 実証層 - 本当に必要か（削除テスト）
    """

    SURFACE = "surface"          # 表層
    STRUCTURE = "structure"      # 構造層
    FUNCTION = "function"        # 機能層  
    VERIFICATION = "verification"  # 実証層


# PURPOSE: ファイル単位のチェック結果を統一的に扱い、レポート生成とCI判定に渡す
@dataclass
class FileProof:
    """ファイルの存在証明情報"""

    path: Path
    status: ProofStatus
    level: Optional[ProofLevel] = None
    parent: Optional[str] = None  # v2: 親参照
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
    is_private: bool = False  # _foo
    is_dunder: bool = False   # __init__
    quality_issue: Optional[str] = None  # v2.6: 品質問題の記述


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
        
        # TODO: L2 coverage を統合するか検討 (現在はファイル単位のみ)
        
        return (with_proof / checkable) * 100

    # PURPOSE: CI パイプラインでの合否判定を行う (Phase 1: 警告のみ)
    @property
    def is_passing(self) -> bool:
        """CI で PASS するか (v2: ORPHAN は警告のみ)"""
        # Phase 1: Function Purpose missing はまだエラーにしない
        return self.files_missing_proof == 0 and self.files_invalid_proof == 0


# 除外パターン
EXEMPT_PATTERNS = [
    r"__pycache__",
    r"\.pyc$",
    r"\.git",
    r"\.egg-info",
    r"\.venv",  # 仮想環境を除外
    r"tests/",  # テストコードは Purpose 対象外
    r"test_",   # テストファイル
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
]

# 特殊親参照 (バリデーションをスキップ)
SPECIAL_PARENTS = {"FEP", "external", "legacy"}

# 有効なレベルプレフィックス (v2.2: 厳密検証, v3.0: L0追加)
VALID_LEVEL_PREFIXES = {"L0", "L1", "L2", "L3"}

# 最大ファイルサイズ (v2.2: リソース枯渇防止)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# PROOF.md パターン
PROOF_MD_PATTERN = re.compile(r"^PROOF\.md$", re.IGNORECASE)


# PURPOSE: コードベースの存在証明を検証し、CI判定とレポートの判定結果を生成する
class DendronChecker:  # noqa: AI-007
    """Dendron PROOF チェッカー v2.1 (親パス検証付き)"""

    # PURPOSE: チェッカーを初期化し、除外パターンと検証オプションを設定する
    def __init__(
        self,
        exempt_patterns: List[str] = None,
        check_dirs: bool = True,
        check_files: bool = True,
        check_functions: bool = True,  # v2.5
        root: Path = None,  # v2.1: 親パス検証用ルート
        validate_parents: bool = True,  # v2.1: 親パス存在検証
    ):
        self.exempt_patterns = [re.compile(p) for p in (exempt_patterns or EXEMPT_PATTERNS)]
        self.check_dirs = check_dirs
        self.check_files = check_files
        self.check_functions = check_functions  # v2.5
        self.root = root
        self.validate_parents = validate_parents

    # PURPOSE: 指定されたパスが除外対象かどうかを判定する
    def is_exempt(self, path: Path) -> bool:
        """除外対象かどうか"""
        path_str = str(path)
        return any(p.search(path_str) for p in self.exempt_patterns)

    # PURPOSE: 親参照パスの妥当性 (長さ, 存在, 安全性) を検証する
    def validate_parent(self, parent: str) -> tuple[bool, str]:
        """親参照を検証 (v2.4: パス長制限追加)
        
        Returns:
            (is_valid, reason)
        """
        # 特殊親参照はスキップ
        if parent in SPECIAL_PARENTS:
            return True, "特殊親参照"
        
        # v2.4: パス長制限 (255 bytes = Linux ファイル名上限)
        if len(parent.encode('utf-8')) > 255:
            return False, f"親パスが長すぎる: {len(parent)} chars"
        
        # パストラバーサル防止: .. を含むパスを拒否
        if ".." in parent:
            return False, f"パストラバーサル検出: {parent}"
        
        # 絶対パス拒否
        if parent.startswith("/"):
            return False, f"絶対パスは禁止: {parent}"
        
        # 存在チェック (root が設定されている場合のみ)
        if self.root and self.validate_parents:
            try:
                parent_path = self.root / parent.rstrip("/")
                if not parent_path.exists():
                    return False, f"親パスが存在しない: {parent}"
            except OSError as e:
                return False, f"パス検証エラー: {e}"
        
        return True, "OK"

    # PURPOSE: ファイル内の PROOF ヘッダーを検出し、その妥当性を検証する
    def check_file_proof(self, path: Path) -> FileProof:
        """ファイルの PROOF ヘッダーをチェック (v2.2: 強化版)"""
        if self.is_exempt(path):
            return FileProof(path=path, status=ProofStatus.EXEMPT)

        # v2.2: ファイルサイズチェック (リソース枯渇防止)
        try:
            file_size = path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                return FileProof(
                    path=path, status=ProofStatus.INVALID,
                    reason=f"ファイルサイズ超過: {file_size // (1024*1024)}MB > 10MB"
                )
        except OSError as e:
            return FileProof(path=path, status=ProofStatus.INVALID, reason=f"ファイルアクセスエラー: {e}")

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return FileProof(path=path, status=ProofStatus.INVALID, reason=f"読み込みエラー: {e}")

        # v2.3: バイナリファイル検出 (NULL バイトチェック)
        if "\x00" in content:
            return FileProof(
                path=path, status=ProofStatus.INVALID,
                reason="バイナリファイル検出 (NULL バイト含む)"
            )

        # 最初の 10 行を検索
        lines = content.split("\n")[:10]
        for i, line in enumerate(lines, 1):
            # v2.2: コードコメント行のみをチェック (docstring内を除外)
            if not self._is_code_comment(line):
                continue
            
            # v2 パターン (親参照付き) を優先
            match_v2 = PROOF_PATTERN_V2.search(line)
            if match_v2:
                level_str = match_v2.group(1)
                parent = match_v2.group(2)
                level = self._parse_level(level_str)
                
                # v2.2: レベル検証 (UNKNOWN を拒否)
                is_valid_level, level_reason = self._validate_level(level)
                if not is_valid_level:
                    return FileProof(
                        path=path, status=ProofStatus.INVALID,
                        level=level, line_number=i,
                        reason=f"{level_reason} (入力: {level_str})"
                    )
                
                if parent:
                    parent = parent.strip()
                    
                    # v2.1: 親参照を検証
                    is_valid, reason = self.validate_parent(parent)
                    if not is_valid:
                        return FileProof(
                            path=path, status=ProofStatus.INVALID, 
                            level=level, parent=parent, line_number=i,
                            reason=reason
                        )
                    
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
    
    # PURPOSE: ファイル内の関数・クラス定義から Purpose コメントを抽出・検証する
    def check_functions_in_file(self, path: Path) -> List[FunctionProof]:
        """ファイル内の関数・クラスの Purpose をチェック (v2.5)"""
        if self.is_exempt(path):
            return []
            
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
            results = []
            
            # コメントの取得 (各行へのマッピング)
            # AST だけではコメントを取得できないため、別途処理が必要だが
            # 簡易的に行番号で直前を検索するアプローチを取る
            lines = content.splitlines()
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = node.name
                    line_no = node.lineno
                    
                    # 除外判定
                    is_private = name.startswith("_") and not name.startswith("__")
                    is_dunder = name.startswith("__") and name.endswith("__")
                    
                    # dunder は完全除外 (v2.5)
                    if is_dunder:
                        continue
                        
                    # 直前のコメントを検索 (最大 5行遡る)
                    # デコレータがある場合はそれをスキップする必要がある
                    # ast.FunctionDef.decorator_list を使う手もあるが
                    # 行番号ベースで遡るのが確実
                    
                    # node.lineno は def 行。デコレータがある場合は node.decorator_list[0].lineno が開始行
                    start_scan_line = line_no
                    if getattr(node, 'decorator_list', []):
                        # 一番上のデコレータの開始行
                        start_scan_line = node.decorator_list[0].lineno
                    
                    # 直前行から遡って検索 (0-indexed に変換)
                    found_purpose = None
                    scan_idx = start_scan_line - 2  # 1行上 (0-indexed)
                    
                    # 空行やデコレータ以外の要素をスキップしつつ、コメントを探す
                    while scan_idx >= 0 and scan_idx >= start_scan_line - 10:  # 最大10行見る
                        line = lines[scan_idx].strip()
                        if not line:
                            scan_idx -= 1
                            continue
                        
                        if line.startswith("#"):
                            match = PURPOSE_PATTERN.search(line)
                            if match:
                                found_purpose = match.group(1).strip()
                                break
                            # 他のコメントなら更に上を見る
                            scan_idx -= 1
                        else:
                            # コード行なら探索終了
                            break
                    
                    if found_purpose:
                        # v2.6: Purpose 品質チェック
                        quality_issue = self._validate_purpose_quality(found_purpose)
                        if quality_issue:
                            results.append(FunctionProof(
                                name=name, path=path, line_number=line_no,
                                status=ProofStatus.WEAK, purpose_text=found_purpose,
                                is_private=is_private, is_dunder=is_dunder,
                                quality_issue=quality_issue
                            ))
                        else:
                            results.append(FunctionProof(
                                name=name, path=path, line_number=line_no,
                                status=ProofStatus.OK, purpose_text=found_purpose,
                                is_private=is_private, is_dunder=is_dunder
                            ))
                    else:
                        # Private は EXEMPT 扱いだが警告として記録も可能
                        status = ProofStatus.EXEMPT if is_private else ProofStatus.MISSING
                        reason = "Private method" if is_private else "No # PURPOSE comment found"
                        results.append(FunctionProof(
                            name=name, path=path, line_number=line_no,
                            status=status, purpose_text=None, reason=reason,
                            is_private=is_private, is_dunder=is_dunder
                        ))
                        
            return results
            
        except Exception:
            # パースエラー等は無視 (コードとしては無効でもテキストとしては読める場合など)
            return []

    # PURPOSE: ディレクトリ内の PROOF.md の存在を検証する
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

    # PURPOSE: レベル文字列 (L0-L3) を解析して Enum に変換する
    def _parse_level(self, level_str: str) -> ProofLevel:  # noqa: AI-007
        """レベル文字列をパース (v3.0: L0追加)"""
        level_str_upper = level_str.upper()
        
        # 厳密検証: L0/L1/L2/L3 で始まる必要がある
        if level_str_upper.startswith("L0"):
            return ProofLevel.L0
        elif level_str_upper.startswith("L1"):
            return ProofLevel.L1
        elif level_str_upper.startswith("L2"):
            return ProofLevel.L2
        elif level_str_upper.startswith("L3"):
            return ProofLevel.L3
        return ProofLevel.UNKNOWN
    
    # PURPOSE: 指定行が有効なコードコメントかどうかを判定する (docstring 除外)
    def _is_code_comment(self, line: str) -> bool:
        """行がコードコメントかどうか (docstring内を除外)
        
        v2.2: docstring 内の PROOF を無視するため、
        行が # で始まるかチェック (前後の空白は許容)
        """
        stripped = line.strip()
        return stripped.startswith("#")
    
    # PURPOSE: 解析されたレベルが有効範囲内であることを検証する
    def _validate_level(self, level: ProofLevel) -> tuple[bool, str]:
        """レベルを検証 (v3.0: L0追加)"""
        if level == ProofLevel.UNKNOWN:
            return False, "無効なレベル: L0/L1/L2/L3 のいずれかで始まる必要があります"
        return True, "OK"

    # PURPOSE: Purpose コメントが WHAT ではなく WHY を述べているか検証する
    def _validate_purpose_quality(self, purpose_text: str) -> Optional[str]:
        """Purpose の品質を検証 (v2.6)
        
        Returns:
            品質問題がある場合はその説明、なければ None
        """
        for pattern, issue_desc in WEAK_PURPOSE_PATTERNS:
            if pattern.search(purpose_text):
                return issue_desc
        return None

    # PURPOSE: 指定ルート以下のディレクトリツリー全体を再帰的にチェックする
    def check(self, root: Path) -> CheckResult:  # noqa: AI-007
        """ディレクトリツリーをチェック"""
        root = Path(root)

        file_proofs: List[FileProof] = []
        dir_proofs: List[DirProof] = []
        function_proofs: List[FunctionProof] = []

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
                    
                    # 関数をチェック (v2.5)
                    if self.check_functions:
                        fps = self.check_functions_in_file(path)
                        function_proofs.extend(fps)

        # 集計
        total_files = len(file_proofs)
        ok = sum(1 for f in file_proofs if f.status == ProofStatus.OK)
        missing = sum(1 for f in file_proofs if f.status == ProofStatus.MISSING)
        invalid = sum(1 for f in file_proofs if f.status == ProofStatus.INVALID)
        exempt = sum(1 for f in file_proofs if f.status == ProofStatus.EXEMPT)
        orphan = sum(1 for f in file_proofs if f.status == ProofStatus.ORPHAN)  # v2
        
        # 関数集計 (v2.5, v2.6: WEAK追加)
        # Private (EXEMPT) は母数に含めるが、OK/MISSING には含めないのが理想
        # ここでは単純に OK と MISSING の数を数える (EXEMPT除く)
        total_functions = sum(1 for f in function_proofs if not f.is_dunder)
        funcs_ok = sum(1 for f in function_proofs if f.status == ProofStatus.OK)
        funcs_missing = sum(1 for f in function_proofs if f.status == ProofStatus.MISSING)
        funcs_weak = sum(1 for f in function_proofs if f.status == ProofStatus.WEAK)

        # レベル統計 (OK + ORPHAN を含む)
        level_counter: Counter = Counter()
        for fp in file_proofs:
            if fp.status in (ProofStatus.OK, ProofStatus.ORPHAN) and fp.level:
                level_counter[fp.level.value] += 1
        level_stats = dict(level_counter)

        return CheckResult(
            total_files=total_files,
            files_with_proof=ok,
            files_missing_proof=missing,
            files_invalid_proof=invalid,
            files_exempt=exempt,
            files_orphan=orphan,
            file_proofs=file_proofs,
            dir_proofs=dir_proofs,
            
            # v2.5, v2.6
            total_functions=total_functions,
            functions_with_purpose=funcs_ok,
            functions_missing_purpose=funcs_missing,
            functions_weak_purpose=funcs_weak,
            function_proofs=function_proofs,
            
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
    print("-" * 20)
    print(f"Total functions (L2): {result.total_functions}")
    print(f"With Purpose: {result.functions_with_purpose}")
    print(f"Missing Purpose: {result.functions_missing_purpose}")
    
    # v2.6: WEAK Purpose の表示
    weak_funcs = [f for f in result.function_proofs if f.status == ProofStatus.WEAK]
    if weak_funcs:
        print(f"Weak Purpose: {len(weak_funcs)}")
        print("-" * 20)
        print("⚠️ WEAK Purposes (WHAT not WHY):")
        for f in weak_funcs[:10]:  # 最大10件
            print(f"  {f.path}:{f.line_number} {f.name}")
            print(f"    Purpose: {f.purpose_text}")
            print(f"    Issue: {f.quality_issue}")

