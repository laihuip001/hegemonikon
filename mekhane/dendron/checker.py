# PROOF: [L2/インフラ] <- mekhane/dendron/  # noqa: AI-022
"""
Dendron Checker — PROOF 検証ロジック

L0 (ディレクトリ) と L1 (ファイル) の存在証明を検証する。
v2.5: L2 (関数/クラス) の # PURPOSE: 検証を追加
v3.0: データモデルを models.py に分離
"""

from collections import Counter
from pathlib import Path
from typing import List, Optional, Dict, Set
import re
import ast

# モデル・定数を models.py から import (後方互換性のため re-export)
from .models import (  # noqa: F401
    ProofStatus,
    ProofLevel,
    MetaLayer,
    FileProof,
    FunctionProof,
    VariableProof,
    DirProof,
    StructureProof,
    FunctionNFProof,
    VerificationProof,
    CheckResult,
    EXEMPT_PATTERNS,
    PROOF_PATTERN_V2,
    PURPOSE_PATTERN,
    WEAK_PURPOSE_PATTERNS,
    SPECIAL_PARENTS,
    VALID_LEVEL_PREFIXES,
    MAX_FILE_SIZE,
    PROOF_MD_PATTERN,
    REASON_PATTERN,
)


# L3: ループ変数として許容される 1 文字名 (/dia+ レビューで d/v/t 削除)
_LOOP_VAR_NAMES = frozenset("i j k n m x y z _ e f".split())


# PURPOSE: コードベースの存在証明を検証し、CI判定とレポートの判定結果を生成する
class DendronChecker:  # noqa: AI-007
    """Dendron PROOF チェッカー v3.0 (L3 Surface 対応)"""

    # PURPOSE: チェッカーを初期化し、除外パターンと検証オプションを設定する
    def __init__(
        self,
        exempt_patterns: Optional[List[str]] = None,
        check_dirs: bool = True,
        check_files: bool = True,
        check_functions: bool = True,  # v2.5
        check_variables: bool = True,  # v3.0 L3
        check_structure: bool = False,  # v3.1 NF2
        check_function_nf: bool = False,  # v3.2 NF3
        check_verification: bool = False,  # v3.3 BCNF
        root: Optional[Path] = None,  # v2.1: 親パス検証用ルート
        validate_parents: bool = True,  # v2.1: 親パス存在検証
    ):
        self.exempt_patterns = [re.compile(p) for p in (EXEMPT_PATTERNS if exempt_patterns is None else exempt_patterns)]
        self.check_dirs = check_dirs
        self.check_files = check_files
        self.check_functions = check_functions  # v2.5
        self.check_variables = check_variables  # v3.0 L3
        self.check_structure = check_structure  # v3.1 NF2
        self.check_function_nf = check_function_nf  # v3.2 NF3
        self.check_verification = check_verification  # v3.3 BCNF
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
        except (OSError, UnicodeDecodeError) as e:
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
        except (SyntaxError, UnicodeDecodeError):
            return []
        
        return self._check_functions_from_tree(path, tree, content)

    # PURPOSE: パース済み AST から関数の PURPOSE コメント有無を検証する (内部用)
    def _check_functions_from_tree(self, path: Path, tree: ast.Module, content: str) -> List[FunctionProof]:
        """AST から関数・クラスの Purpose をチェック (内部用)"""
        results: List[FunctionProof] = []
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
                    
                # node.lineno は def 行。デコレータがある場合は node.decorator_list[0].lineno が開始行
                start_scan_line = line_no
                if getattr(node, 'decorator_list', []):
                    start_scan_line = node.decorator_list[0].lineno
                
                # 直前行から遡って検索 (0-indexed に変換)
                found_purpose = None
                scan_idx = start_scan_line - 2  # 1行上 (0-indexed)
                
                while scan_idx >= 0 and scan_idx >= start_scan_line - 10:
                    line = lines[scan_idx].strip()
                    if not line:
                        scan_idx -= 1
                        continue
                    
                    if line.startswith("#"):
                        match = PURPOSE_PATTERN.search(line)
                        if match:
                            found_purpose = match.group(1).strip()
                            break
                        scan_idx -= 1
                    else:
                        break
                
                if found_purpose:
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
                    status = ProofStatus.EXEMPT if is_private else ProofStatus.MISSING
                    reason = "Private method" if is_private else "No # PURPOSE comment found"
                    results.append(FunctionProof(
                        name=name, path=path, line_number=line_no,
                        status=status, purpose_text=None, reason=reason,
                        is_private=is_private, is_dunder=is_dunder
                    ))
                    
        return results

    # PURPOSE: ファイル内の public 関数の型ヒント有無と 1文字変数を検出する (L3 Akribeia)
    def check_variables_in_file(self, path: Path) -> List[VariableProof]:
        """ファイル内の変数・字句を精密検証 (v3.0 L3 Surface)"""
        if self.is_exempt(path):
            return []

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            return []

        return self._check_variables_from_tree(path, tree)

    # PURPOSE: パース済み AST から型ヒントと 1文字変数を検出する (内部用)
    def _check_variables_from_tree(self, path: Path, tree: ast.Module) -> List[VariableProof]:
        """AST から変数・字句を精密検証 (内部用)"""
        results: List[VariableProof] = []

        for node in ast.walk(tree):
            # --- 型ヒント検査: public 関数の引数と戻り値 ---
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = node.name
                if name.startswith("_"):
                    continue

                if node.returns is None:
                    results.append(VariableProof(
                        name=f"{name}() -> ???", path=path,
                        line_number=node.lineno, status=ProofStatus.MISSING,
                        check_type="type_hint",
                        reason="戻り値の型ヒントなし",
                    ))
                else:
                    results.append(VariableProof(
                        name=f"{name}() -> ...", path=path,
                        line_number=node.lineno, status=ProofStatus.OK,
                        check_type="type_hint",
                    ))

                # 全引数種別を検査 (args + kwonlyargs + posonlyargs)
                all_args = list(node.args.args) + list(node.args.kwonlyargs) + list(node.args.posonlyargs)
                for arg in all_args:
                    if arg.arg in ("self", "cls"):
                        continue
                    if arg.annotation is None:
                        results.append(VariableProof(
                            name=f"{name}({arg.arg})", path=path,
                            line_number=node.lineno, status=ProofStatus.MISSING,
                            check_type="type_hint",
                            reason=f"引数 '{arg.arg}' に型ヒントなし",
                        ))
                    else:
                        results.append(VariableProof(
                            name=f"{name}({arg.arg})", path=path,
                            line_number=node.lineno, status=ProofStatus.OK,
                            check_type="type_hint",
                        ))

                # *args の型ヒント検査
                if node.args.vararg:
                    vararg = node.args.vararg
                    if vararg.annotation is None:
                        results.append(VariableProof(
                            name=f"{name}(*{vararg.arg})", path=path,
                            line_number=node.lineno, status=ProofStatus.MISSING,
                            check_type="type_hint",
                            reason=f"*{vararg.arg} に型ヒントなし",
                        ))
                    else:
                        results.append(VariableProof(
                            name=f"{name}(*{vararg.arg})", path=path,
                            line_number=node.lineno, status=ProofStatus.OK,
                            check_type="type_hint",
                        ))

                # **kwargs の型ヒント検査
                if node.args.kwarg:
                    kwarg = node.args.kwarg
                    if kwarg.annotation is None:
                        results.append(VariableProof(
                            name=f"{name}(**{kwarg.arg})", path=path,
                            line_number=node.lineno, status=ProofStatus.MISSING,
                            check_type="type_hint",
                            reason=f"**{kwarg.arg} に型ヒントなし",
                        ))
                    else:
                        results.append(VariableProof(
                            name=f"{name}(**{kwarg.arg})", path=path,
                            line_number=node.lineno, status=ProofStatus.OK,
                            check_type="type_hint",
                        ))

            # --- 1文字変数検出 ---
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and len(target.id) == 1:
                        if target.id not in _LOOP_VAR_NAMES:
                            results.append(VariableProof(
                                name=target.id, path=path,
                                line_number=target.lineno, status=ProofStatus.WEAK,
                                check_type="short_name",
                                reason=f"1文字変数 '{target.id}' は可読性が低い",
                            ))

        return results

    # PURPOSE: ディレクトリ内の PROOF.md の存在を検証する
    def check_dir_proof(self, path: Path) -> DirProof:
        """ディレクトリの PROOF.md をチェック"""
        if self.is_exempt(path):
            return DirProof(path=path, status=ProofStatus.EXEMPT)

        proof_md = path / "PROOF.md"
        if proof_md.exists():
            try:
                content = proof_md.read_text(encoding="utf-8").strip()
                if not content:
                    return DirProof(path=path, status=ProofStatus.WEAK, has_proof_md=True,
                                    reason="PROOF.md が空")
            except (OSError, UnicodeDecodeError):
                return DirProof(path=path, status=ProofStatus.OK, has_proof_md=True)
            
            # PURPOSE: と REASON: を検出 (PROOF.md 内は # 接頭辞なし)
            _md_purpose = re.compile(r"(?:#\s*)?PURPOSE:\s*(.+)")
            purpose_text: Optional[str] = None
            reason_text: Optional[str] = None
            for line in content.splitlines():
                pm = _md_purpose.match(line.strip())
                if pm and not purpose_text:
                    purpose_text = pm.group(1).strip()
                rm = REASON_PATTERN.match(line.strip())
                if rm and not reason_text:
                    reason_text = rm.group(1).strip()
            
            return DirProof(
                path=path, status=ProofStatus.OK, has_proof_md=True,
                has_reason=reason_text is not None,
                purpose_text=purpose_text,
                reason_text=reason_text,
            )

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

    # ── NF2: Structure Layer (依存関係検証) ─────────────────

    # PURPOSE: import 文の参照先が実在するかを検証し、壊れた依存を検出する (P11)
    def _check_imports_from_tree(self, path: Path, tree: ast.Module) -> List[StructureProof]:
        """ファイル内の import 文を検証 (NF2 P11)"""
        results: List[StructureProof] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    results.append(StructureProof(
                        name=module_name, path=path,
                        line_number=node.lineno, status=ProofStatus.OK,
                        check_type="import", target=module_name,
                    ))
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                if node.level > 0:  # 相対 import
                    # 相対 import はパス解決を試みる
                    parts = path.parent.parts
                    level_up = node.level - 1
                    if level_up < len(parts):
                        base = Path(*parts[:len(parts) - level_up]) if level_up > 0 else path.parent
                        if module_name:
                            target_path = base / module_name.replace(".", "/")
                            if not (target_path.exists() or target_path.with_suffix(".py").exists()):
                                results.append(StructureProof(
                                    name=f"from {'.' * node.level}{module_name}",
                                    path=path, line_number=node.lineno,
                                    status=ProofStatus.MISSING,
                                    check_type="import", target=str(target_path),
                                    reason=f"相対 import 先が存在しない: {target_path}",
                                ))
                            else:
                                results.append(StructureProof(
                                    name=f"from {'.' * node.level}{module_name}",
                                    path=path, line_number=node.lineno,
                                    status=ProofStatus.OK,
                                    check_type="import", target=str(target_path),
                                ))
                        else:
                            results.append(StructureProof(
                                name=f"from {'.' * node.level} import ...",
                                path=path, line_number=node.lineno,
                                status=ProofStatus.OK,
                                check_type="import", target=str(base),
                            ))
                else:  # 絶対 import
                    results.append(StructureProof(
                        name=f"from {module_name}", path=path,
                        line_number=node.lineno, status=ProofStatus.OK,
                        check_type="import", target=module_name,
                    ))
        
        return results

    # PURPOSE: 関数内の呼出先が同モジュール内で解決可能か検証する (P21)
    def _check_calls_from_tree(self, path: Path, tree: ast.Module) -> List[StructureProof]:
        """関数呼出の解決可能性を検証 (NF2 P21)"""
        results: List[StructureProof] = []
        
        # モジュール内の定義名を収集
        defined_names: Set[str] = set()
        imported_names: Set[str] = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined_names.add(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
        
        known_names = defined_names | imported_names | {"print", "len", "range", "int", "str",
            "list", "dict", "set", "tuple", "bool", "float", "type", "super", "isinstance",
            "issubclass", "hasattr", "getattr", "setattr", "enumerate", "zip", "map",
            "filter", "sorted", "reversed", "any", "all", "min", "max", "sum", "abs",
            "open", "repr", "id", "hash", "vars", "dir", "iter", "next", "property",
            "staticmethod", "classmethod", "dataclass", "field",
        }
        
        # public 関数内の呼出を検査
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        call_name = self._extract_call_name(child)
                        if call_name and call_name not in known_names:
                            results.append(StructureProof(
                                name=f"{node.name}() -> {call_name}()",
                                path=path, line_number=child.lineno,
                                status=ProofStatus.WEAK,
                                check_type="call",
                                target=call_name,
                                reason=f"呼出先 '{call_name}' がモジュール内で未解決",
                            ))
        
        return results

    # PURPOSE: 型アノテーションが import されているか検証する (P31)
    def _check_type_refs_from_tree(self, path: Path, tree: ast.Module) -> List[StructureProof]:
        """型参照の import 照合を検証 (NF2 P31)"""
        results: List[StructureProof] = []
        
        # import された名前を収集
        imported_names: Set[str] = set()
        # 同ファイル内の定義 (class/function) も型として有効
        defined_names: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_names.add(node.name)
        
        # 組込型 + 特殊型
        builtin_types = {"str", "int", "float", "bool", "bytes", "None", "list",
            "dict", "set", "tuple", "type", "object", "Any", "Callable",
        }
        known_types = imported_names | builtin_types | defined_names
        
        # 関数の型アノテーションから型名を抽出
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                annotations = []
                if node.returns:
                    annotations.append(("return", node.returns))
                for arg in node.args.args + node.args.kwonlyargs + node.args.posonlyargs:
                    if arg.annotation:
                        annotations.append((arg.arg, arg.annotation))
                
                for label, ann in annotations:
                    type_names = self._extract_type_names(ann)
                    for tn in type_names:
                        if tn not in known_types:
                            results.append(StructureProof(
                                name=f"{node.name}({label}: {tn})",
                                path=path, line_number=node.lineno,
                                status=ProofStatus.WEAK,
                                check_type="type_ref",
                                target=tn,
                                reason=f"型 '{tn}' が import されていない",
                            ))
        
        return results

    # PURPOSE: ast.Call ノードから呼出先の名前を抽出する
    def _extract_call_name(self, node: ast.Call) -> Optional[str]:
        """呼出先名を抽出"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # self.method() / module.func() は解決済みとみなす
            return None
        return None

    # PURPOSE: 型アノテーション AST から型名文字列を再帰的に抽出する
    def _extract_type_names(self, node: ast.expr) -> List[str]:
        """型アノテーションから型名を抽出"""
        names: List[str] = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            # module.Type → module は import で解決済み
            pass
        elif isinstance(node, ast.Subscript):
            # List[X], Dict[K, V] など
            names.extend(self._extract_type_names(node.value))
            if isinstance(node.slice, ast.Tuple):
                for elt in node.slice.elts:
                    names.extend(self._extract_type_names(elt))
            else:
                names.extend(self._extract_type_names(node.slice))
        elif isinstance(node, ast.BinOp):  # X | Y (union)
            names.extend(self._extract_type_names(node.left))
            names.extend(self._extract_type_names(node.right))
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                names.append(node.value)  # 文字列アノテーション (forward ref)
        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                names.extend(self._extract_type_names(elt))
        return names

    # PURPOSE: PROOF.md 内の親参照が実在するか検証する (P01)
    def check_dir_structure(self, path: Path) -> List[StructureProof]:
        """ディレクトリの PROOF.md 内の親参照を検証 (NF2 P01)"""
        results: List[StructureProof] = []
        proof_md = path / "PROOF.md"
        if not proof_md.exists():
            return results
        
        try:
            content = proof_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return results
        
        # PROOF.md 内の <- 参照を検索
        match = PROOF_PATTERN_V2.search(content)
        if match and match.group(2):
            parent = match.group(2).strip()
            is_valid, reason = self.validate_parent(parent)
            results.append(StructureProof(
                name=f"PROOF.md <- {parent}",
                path=proof_md, line_number=1,
                status=ProofStatus.OK if is_valid else ProofStatus.MISSING,
                check_type="dir_ref",
                target=parent,
                reason=None if is_valid else reason,
            ))
        
        return results

    # ── NF3: Function Layer (機能的冗長性) ────────────────

    # --- 閾値定数 ---
    _SRP_MAX_LINES = 50
    _SRP_MAX_BRANCHES = 10
    _SRP_MAX_PARAMS = 5
    _SIMILARITY_THRESHOLD = 0.8  # 80% 以上で類似判定

    # PURPOSE: 関数の複雑度メトリクスを計算し SRP 違反を検出する (P22)
    def _check_complexity_from_tree(self, path: Path, tree: ast.Module) -> List[FunctionNFProof]:
        """関数の SRP 検証 (NF3 P22)"""
        results: List[FunctionNFProof] = []
        
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            
            # 行数
            lines = (node.end_lineno or node.lineno) - node.lineno + 1
            if lines > self._SRP_MAX_LINES:
                results.append(FunctionNFProof(
                    name=node.name, path=path, line_number=node.lineno,
                    status=ProofStatus.WEAK, check_type="complexity",
                    metric_value=lines, threshold=self._SRP_MAX_LINES,
                    reason=f"関数が長すぎる: {lines}行 (閾値: {self._SRP_MAX_LINES})",
                ))
            
            # 分岐数 (cyclomatic complexity 近似)
            branches = sum(1 for child in ast.walk(node)
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                                      ast.With, ast.Assert)))
            # BoolOp の and/or もカウント
            branches += sum(1 for child in ast.walk(node)
                if isinstance(child, ast.BoolOp))
            
            if branches > self._SRP_MAX_BRANCHES:
                results.append(FunctionNFProof(
                    name=node.name, path=path, line_number=node.lineno,
                    status=ProofStatus.WEAK, check_type="complexity",
                    metric_value=branches, threshold=self._SRP_MAX_BRANCHES,
                    reason=f"分岐が多すぎる: {branches} (閾値: {self._SRP_MAX_BRANCHES})",
                ))
            
            # パラメータ数
            all_params = [a for a in node.args.args if a.arg not in ("self", "cls")]
            all_params += node.args.kwonlyargs + node.args.posonlyargs
            param_count = len(all_params)
            if node.args.vararg:
                param_count += 1
            if node.args.kwarg:
                param_count += 1
            
            if param_count > self._SRP_MAX_PARAMS:
                results.append(FunctionNFProof(
                    name=node.name, path=path, line_number=node.lineno,
                    status=ProofStatus.WEAK, check_type="complexity",
                    metric_value=param_count, threshold=self._SRP_MAX_PARAMS,
                    reason=f"引数が多すぎる: {param_count} (閾値: {self._SRP_MAX_PARAMS})",
                ))
            
            # 全 OK の場合
            if lines <= self._SRP_MAX_LINES and branches <= self._SRP_MAX_BRANCHES and param_count <= self._SRP_MAX_PARAMS:
                results.append(FunctionNFProof(
                    name=node.name, path=path, line_number=node.lineno,
                    status=ProofStatus.OK, check_type="complexity",
                    metric_value=lines,
                ))
        
        return results

    # PURPOSE: 同ファイル内の類似関数を AST 構造比較で検出する (P12)
    def _check_similarity_from_tree(self, path: Path, tree: ast.Module) -> List[FunctionNFProof]:
        """関数の類似性検証 (NF3 P12)"""
        results: List[FunctionNFProof] = []
        
        # public 関数の AST 構造を抽出
        func_signatures: List[tuple] = []  # (name, lineno, node_type_seq)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                # AST ノード型のシーケンスとして構造を表現
                type_seq = tuple(type(child).__name__ for child in ast.walk(node))
                func_signatures.append((node.name, node.lineno, type_seq))
        
        # ペア比較
        reported_pairs: set = set()
        for i, (name_a, line_a, seq_a) in enumerate(func_signatures):
            for j, (name_b, line_b, seq_b) in enumerate(func_signatures):
                if i >= j:
                    continue
                pair_key = (name_a, name_b)
                if pair_key in reported_pairs:
                    continue
                
                # Jaccard 類似度 (型シーケンスの集合比較)
                set_a = set(enumerate(seq_a))
                set_b = set(enumerate(seq_b))
                if not set_a or not set_b:
                    continue
                intersection = len(set_a & set_b)
                union = len(set_a | set_b)
                similarity = intersection / union if union > 0 else 0
                
                if similarity > self._SIMILARITY_THRESHOLD:
                    reported_pairs.add(pair_key)
                    sim_pct = int(similarity * 100)
                    results.append(FunctionNFProof(
                        name=f"{name_a} ≈ {name_b}", path=path,
                        line_number=line_a,
                        status=ProofStatus.WEAK, check_type="similarity",
                        metric_value=sim_pct, threshold=int(self._SIMILARITY_THRESHOLD * 100),
                        reason=f"関数 '{name_a}' と '{name_b}' が {sim_pct}% 類似",
                    ))
        
        return results

    # PURPOSE: 同一スコープ内で変数が複数回代入されていないか検出する (P32)
    def _check_reassignment_from_tree(self, path: Path, tree: ast.Module) -> List[FunctionNFProof]:
        """変数の再代入検出 (NF3 P32)"""
        results: List[FunctionNFProof] = []
        
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            
            # 関数直下の代入先を収集 (ネストされたスコープは除外)
            assignments: Dict[str, List[int]] = {}
            for child in ast.iter_child_nodes(node):
                self._collect_assignments(child, assignments)
            
            # 3回以上の代入は WEAK (ループ変数・累積パターンを考慮)
            for var_name, lines in assignments.items():
                if len(lines) >= 3 and var_name not in _LOOP_VAR_NAMES:
                    results.append(FunctionNFProof(
                        name=f"{node.name}.{var_name}", path=path,
                        line_number=lines[0],
                        status=ProofStatus.WEAK, check_type="reassign",
                        metric_value=len(lines),
                        reason=f"変数 '{var_name}' が {len(lines)} 回代入 (関数 {node.name} 内)",
                    ))
        
        return results

    # PURPOSE: AST ノードから代入先変数名を再帰的に収集する (NF3 P32 補助)
    def _collect_assignments(self, node: ast.AST, assignments: Dict[str, List[int]]) -> None:
        """代入先を収集 (ネストされた関数/クラスはスキップ)"""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return  # ネストされたスコープはスキップ
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.setdefault(target.id, []).append(target.lineno)
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                assignments.setdefault(node.target.id, []).append(node.target.lineno)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value is not None:
                assignments.setdefault(node.target.id, []).append(node.target.lineno)
        # 再帰
        for child in ast.iter_child_nodes(node):
            self._collect_assignments(child, assignments)

    # ── BCNF: Verification Layer (不可欠性) ───────────────

    # PURPOSE: プロジェクト全体で関数/変数の不可欠性を検証する (P23, P33)
    def _check_verification_global(
        self, root: Path, file_trees: Dict[Path, ast.Module],
    ) -> List[VerificationProof]:
        """プロジェクト横断の不可欠性検証 (BCNF)"""
        results: List[VerificationProof] = []
        
        # P13: ファイルの被 import カウント
        # 全ファイルの相対パス (拡張子なし) を正規化
        file_stems: Dict[str, Path] = {}
        for fp in file_trees:
            rel = fp.relative_to(root) if fp.is_relative_to(root) else fp
            stem = str(rel).replace(".py", "").replace("/", ".")
            file_stems[stem] = fp
        
        # 全 import 先を収集
        imported_modules: set = set()
        for tree in file_trees.values():
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported_modules.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.add(alias.name)
        
        for stem, fp in file_stems.items():
            is_imported = any(stem.endswith(m) or m.endswith(stem) for m in imported_modules)
            # __init__.py と __main__.py はエントリポイントなので除外
            if fp.name in ("__init__.py", "__main__.py"):
                continue
            results.append(VerificationProof(
                name=fp.name, path=fp, line_number=1,
                status=ProofStatus.OK if is_imported else ProofStatus.WEAK,
                check_type="file_import_count",
                ref_count=1 if is_imported else 0,
                reason=None if is_imported else f"ファイル '{fp.name}' が他ファイルから import されていない",
            ))
        
        # P23: dead function 検出
        # 全定義を収集
        all_definitions: Dict[str, tuple] = {}  # name -> (path, lineno)
        all_calls: set = set()
        
        _SKIP_DECORATORS = {"property", "staticmethod", "classmethod", "abstractmethod"}
        
        for fp, tree in file_trees.items():
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        # @property 等はアトリビュートアクセスなので除外
                        dec_names = set()
                        for d in node.decorator_list:
                            if isinstance(d, ast.Name):
                                dec_names.add(d.id)
                            elif isinstance(d, ast.Attribute):
                                dec_names.add(d.attr)
                        if not dec_names & _SKIP_DECORATORS:
                            all_definitions[f"{fp}:{node.name}"] = (fp, node.lineno, node.name)
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        all_calls.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        all_calls.add(node.func.attr)
        
        for key, (fp, lineno, fname) in all_definitions.items():
            is_called = fname in all_calls
            results.append(VerificationProof(
                name=fname, path=fp, line_number=lineno,
                status=ProofStatus.OK if is_called else ProofStatus.WEAK,
                check_type="dead_func",
                ref_count=1 if is_called else 0,
                reason=None if is_called else f"関数 '{fname}' がプロジェクト内で呼ばれていない",
            ))
        
        # P33: unused variable (関数内の Store のみで Load なし)
        for fp, tree in file_trees.items():
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name.startswith("_"):
                    continue
                
                stores: set = set()
                loads: set = set()
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Store):
                            stores.add(child.id)
                        elif isinstance(child.ctx, (ast.Load, ast.Del)):
                            loads.add(child.id)
                
                # パラメータ名は loads に含める
                for arg in node.args.args + node.args.kwonlyargs:
                    loads.add(arg.arg)
                
                unused = stores - loads - {"_"} - _LOOP_VAR_NAMES
                for var in unused:
                    results.append(VerificationProof(
                        name=f"{node.name}.{var}", path=fp, line_number=node.lineno,
                        status=ProofStatus.WEAK,
                        check_type="unused_var",
                        ref_count=0,
                        reason=f"変数 '{var}' が関数 '{node.name}' 内で未使用",
                    ))
        
        return results

    # PURPOSE: 指定ルート以下のディレクトリツリー全体を再帰的にチェックする
    def check(self, root: Path) -> CheckResult:  # noqa: AI-007
        """ディレクトリツリーをチェック"""
        root = Path(root)

        file_proofs: List[FileProof] = []
        dir_proofs: List[DirProof] = []
        function_proofs: List[FunctionProof] = []
        variable_proofs: List[VariableProof] = []
        structure_proofs: List[StructureProof] = []
        function_nf_proofs: List[FunctionNFProof] = []
        verification_proofs: List[VerificationProof] = []
        file_trees: Dict[Path, ast.Module] = {}

        # ディレクトリをチェック
        if self.check_dirs:
            for path in root.rglob("*"):
                if path.is_dir() and not self.is_exempt(path):
                    dir_proofs.append(self.check_dir_proof(path))
                    if self.check_structure:
                        structure_proofs.extend(self.check_dir_structure(path))

        # ファイルをチェック
        if self.check_files:
            for path in root.rglob("*.py"):
                if path.is_file():
                    file_proofs.append(self.check_file_proof(path))
                    self._check_file_ast(
                        path, function_proofs, variable_proofs,
                        structure_proofs, function_nf_proofs, file_trees,
                    )

        # BCNF: プロジェクト横断解析
        if self.check_verification and file_trees:
            verification_proofs.extend(
                self._check_verification_global(root, file_trees)
            )

        return self._aggregate_results(
            file_proofs, dir_proofs, function_proofs,
            variable_proofs, structure_proofs,
            function_nf_proofs, verification_proofs,
        )

    # PURPOSE: 1ファイルの AST を解析し、各レイヤーのチェックを分配する
    def _check_file_ast(
        self, path: Path,
        function_proofs: List[FunctionProof],
        variable_proofs: List[VariableProof],
        structure_proofs: List[StructureProof],
        function_nf_proofs: List[FunctionNFProof],
        file_trees: Dict[Path, ast.Module],
    ) -> None:
        """AST ベースのチェックを1ファイルに対して実行"""
        needs_ast = (
            self.check_functions or self.check_variables
            or self.check_structure or self.check_function_nf
            or self.check_verification
        )
        if not needs_ast or self.is_exempt(path):
            return

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            return

        if self.check_functions:
            function_proofs.extend(self._check_functions_from_tree(path, tree, content))
        if self.check_variables:
            variable_proofs.extend(self._check_variables_from_tree(path, tree))
        if self.check_structure:
            structure_proofs.extend(self._check_imports_from_tree(path, tree))
            structure_proofs.extend(self._check_calls_from_tree(path, tree))
            structure_proofs.extend(self._check_type_refs_from_tree(path, tree))
        if self.check_function_nf:
            function_nf_proofs.extend(self._check_complexity_from_tree(path, tree))
            function_nf_proofs.extend(self._check_similarity_from_tree(path, tree))
            function_nf_proofs.extend(self._check_reassignment_from_tree(path, tree))
        if self.check_verification:
            file_trees[path] = tree

    # PURPOSE: 収集した各 proof リストから統計を集計し CheckResult を構築する
    def _aggregate_results(
        self,
        file_proofs: List[FileProof],
        dir_proofs: List[DirProof],
        function_proofs: List[FunctionProof],
        variable_proofs: List[VariableProof],
        structure_proofs: List[StructureProof],
        function_nf_proofs: List[FunctionNFProof],
        verification_proofs: List[VerificationProof],
    ) -> CheckResult:
        """全 proof から CheckResult を構築"""
        # ファイル集計
        total_files = len(file_proofs)
        ok = sum(1 for f in file_proofs if f.status == ProofStatus.OK)
        missing = sum(1 for f in file_proofs if f.status == ProofStatus.MISSING)
        invalid = sum(1 for f in file_proofs if f.status == ProofStatus.INVALID)
        exempt = sum(1 for f in file_proofs if f.status == ProofStatus.EXEMPT)
        orphan = sum(1 for f in file_proofs if f.status == ProofStatus.ORPHAN)

        # 関数集計
        total_functions = sum(1 for f in function_proofs if not f.is_dunder)
        funcs_ok = sum(1 for f in function_proofs if f.status == ProofStatus.OK)
        funcs_missing = sum(1 for f in function_proofs if f.status == ProofStatus.MISSING)
        funcs_weak = sum(1 for f in function_proofs if f.status == ProofStatus.WEAK)

        # L3 変数集計
        hint_proofs = [v for v in variable_proofs if v.check_type == "type_hint"]
        total_sigs = len(hint_proofs)
        sigs_ok = sum(1 for v in hint_proofs if v.status == ProofStatus.OK)
        sigs_missing = sum(1 for v in hint_proofs if v.status == ProofStatus.MISSING)
        short_violations = sum(1 for v in variable_proofs if v.check_type == "short_name")

        # レベル統計
        level_counter: Counter = Counter()
        for fp in file_proofs:
            if fp.status in (ProofStatus.OK, ProofStatus.ORPHAN) and fp.level:
                level_counter[fp.level.value] += 1

        return CheckResult(
            total_files=total_files,
            files_with_proof=ok,
            files_missing_proof=missing,
            files_invalid_proof=invalid,
            files_exempt=exempt,
            files_orphan=orphan,
            file_proofs=file_proofs,
            dir_proofs=dir_proofs,
            total_functions=total_functions,
            functions_with_purpose=funcs_ok,
            functions_missing_purpose=funcs_missing,
            functions_weak_purpose=funcs_weak,
            function_proofs=function_proofs,
            total_checked_signatures=total_sigs,
            signatures_with_hints=sigs_ok,
            signatures_missing_hints=sigs_missing,
            short_name_violations=short_violations,
            variable_proofs=variable_proofs,
            level_stats=dict(level_counter),
            total_structure_checks=len(structure_proofs),
            structure_ok=sum(1 for s in structure_proofs if s.status == ProofStatus.OK),
            structure_missing=sum(1 for s in structure_proofs if s.status in (ProofStatus.MISSING, ProofStatus.WEAK)),
            structure_proofs=structure_proofs,
            total_function_nf_checks=len(function_nf_proofs),
            function_nf_ok=sum(1 for f in function_nf_proofs if f.status == ProofStatus.OK),
            function_nf_weak=sum(1 for f in function_nf_proofs if f.status == ProofStatus.WEAK),
            function_nf_proofs=function_nf_proofs,
            total_verification_checks=len(verification_proofs),
            verification_ok=sum(1 for v in verification_proofs if v.status == ProofStatus.OK),
            verification_weak=sum(1 for v in verification_proofs if v.status == ProofStatus.WEAK),
            verification_proofs=verification_proofs,
        )

