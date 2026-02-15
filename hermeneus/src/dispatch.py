# PROOF: [L2/インフラ] <- hermeneus/src/ CCL ディスパッチャ
"""
CCL Dispatch — CCL 式の検知・パース・構造表示を環境強制するエントリポイント

新セッションの AI が CCL 式を受け取ったとき:
  python hermeneus/src/dispatch.py '{CCL式}'

Step 0: Hermēneus パース (環境強制)
Step 1: AST 構造表示
Step 2: 実行計画の提案テンプレート出力

Usage:
    python hermeneus/src/dispatch.py '/dia+~*/noe'
    python hermeneus/src/dispatch.py '{(/dia+~*/noe)~*/pan+}~*{(/dia+~*/noe)~*\\pan+}'
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# パッケージパス追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


# PURPOSE: G2 — dispatch() 戻り値の型定義
class RouteContext(TypedDict, total=False):
    """Aristos L3 ルーティング文脈。"""
    source: str
    target: str
    route: List[str]
    depth_level: int
    wf_count: int


class DispatchResult(TypedDict, total=False):
    """dispatch() 関数の戻り値型。

    total=False にすることで、全キーがオプショナルになる。
    これにより段階的にキーを設定する dispatch() のパターンと整合する。
    """
    success: bool
    ccl: str
    ast: Any                            # CCLParser の AST ノード
    tree: str                           # AST 木構造のテキスト表示
    workflows: List[str]                # 抽出された WF ID (e.g. ["/noe", "/dia"])
    wf_paths: Dict[str, str]            # WF ID → 絶対パス
    wf_submodules: Dict[str, List[str]] # WF ID → サブモジュールパスのリスト
    wf_summaries: Dict[str, Dict[str, Any]]  # WF ID → 要約情報
    plan_template: str                  # 実行計画テンプレート
    macro_plan: Optional[Dict[str, Any]]     # マクロ実行計画
    error: Optional[str]                     # エラーメッセージ
    exhaustive_warnings: List[str]      # 網羅性チェック警告
    parallel_warnings: List[str]        # 並列安全性チェック警告
    route_context: RouteContext         # Aristos ルーティング文脈


# PURPOSE: AST をインデント付きで木構造表示
def format_ast_tree(node, indent=0) -> str:
    """AST をインデント付きで木構造表示"""
    from hermeneus.src.ccl_ast import (
        Workflow, Oscillation, Fusion, Sequence, ConvergenceLoop,
        ColimitExpansion, ForLoop, IfCondition, WhileLoop
    )
    
    prefix = "  " * indent
    lines = []
    
    if isinstance(node, Oscillation):
        mode = "~*" if node.convergent else ("~!" if node.divergent else "~")
        lines.append(f"{prefix}Oscillation ({mode})")
        lines.append(f"{prefix}  left:")
        lines.append(format_ast_tree(node.left, indent + 2))
        lines.append(f"{prefix}  right:")
        lines.append(format_ast_tree(node.right, indent + 2))
    elif isinstance(node, ColimitExpansion):
        lines.append(f"{prefix}ColimitExpansion (\\)")
        lines.append(f"{prefix}  body:")
        lines.append(format_ast_tree(node.body, indent + 2))
    elif isinstance(node, Fusion):
        lines.append(f"{prefix}Fusion (*)")
        lines.append(f"{prefix}  left:")
        lines.append(format_ast_tree(node.left, indent + 2))
        lines.append(f"{prefix}  right:")
        lines.append(format_ast_tree(node.right, indent + 2))
    elif isinstance(node, Sequence):
        lines.append(f"{prefix}Sequence (_)")
        for i, step in enumerate(node.steps):
            lines.append(f"{prefix}  step {i+1}:")
            lines.append(format_ast_tree(step, indent + 2))
    elif isinstance(node, ConvergenceLoop):
        lines.append(f"{prefix}ConvergenceLoop (>>)")
        lines.append(f"{prefix}  body:")
        lines.append(format_ast_tree(node.body, indent + 2))
        lines.append(f"{prefix}  cond: {node.condition.var} {node.condition.op} {node.condition.value}")
    elif isinstance(node, Workflow):
        ops = ""
        if node.operators:
            from hermeneus.src.ccl_ast import OpType
            ops_map = {
                OpType.DEEPEN: "+", OpType.CONDENSE: "-",
                OpType.ASCEND: "^", OpType.EXPAND: "!",
                OpType.QUERY: "?", OpType.INVERT: "\\",
                OpType.DIFF: "'",
            }
            ops = "".join(ops_map.get(op, "") for op in node.operators)
        lines.append(f"{prefix}Workflow: /{node.id}{ops}")
    else:
        lines.append(f"{prefix}{type(node).__name__}: {node}")
    
    return "\n".join(lines)


# PURPOSE: AST から全ワークフロー ID を再帰的に抽出
def extract_workflows(node) -> list:
    """AST から全ワークフロー ID を再帰的に抽出"""
    from hermeneus.src.ccl_ast import (
        Workflow, Oscillation, Fusion, Sequence, ConvergenceLoop,
        ColimitExpansion
    )
    wfs = []
    if isinstance(node, Workflow):
        wfs.append(f"/{node.id}")
    elif isinstance(node, Oscillation):
        wfs.extend(extract_workflows(node.left))
        wfs.extend(extract_workflows(node.right))
    elif isinstance(node, ColimitExpansion):
        wfs.extend(extract_workflows(node.body))
    elif isinstance(node, Fusion):
        wfs.extend(extract_workflows(node.left))
        wfs.extend(extract_workflows(node.right))
    elif isinstance(node, Sequence):
        for step in node.steps:
            wfs.extend(extract_workflows(step))
    elif isinstance(node, ConvergenceLoop):
        wfs.extend(extract_workflows(node.body))
    return wfs


# PURPOSE: AST 内の条件分岐の網羅性をチェック (Pepsis Rust Phase 2 — exhaustive_check.md)
def exhaustive_check(node, depth=0) -> list[str]:
    """AST を再帰走査し、/dia+ を含む式で条件分岐の網羅性を検証。

    Rust の exhaustive pattern matching に着想を得た設計。
    I: があれば E: (else) が必須。EI: チェーンも E: で終端すべき。

    Returns:
        list of warning strings (空なら問題なし)
    """
    from hermeneus.src.ccl_ast import (
        Workflow, Oscillation, Fusion, Sequence, ConvergenceLoop,
        ColimitExpansion, ForLoop, IfCondition, WhileLoop,
        TaggedBlock, Pipeline, Parallel, OpType
    )

    warnings = []

    if isinstance(node, IfCondition):
        # I: があるが E: がない → 非網羅的
        if node.else_branch is None:
            cond_str = f"{node.condition.var} {node.condition.op} {node.condition.value}"
            warnings.append(
                f"⚠️ [exhaustive] I:[{cond_str}] に E:{{}} (else) がありません。"
                f" 全ケースを網羅していない可能性があります。"
            )
        else:
            # else_branch も再帰チェック
            warnings.extend(exhaustive_check(node.else_branch, depth + 1))
        # then_branch も再帰チェック
        warnings.extend(exhaustive_check(node.then_branch, depth + 1))

    elif isinstance(node, Sequence):
        for step in node.steps:
            warnings.extend(exhaustive_check(step, depth + 1))
    elif isinstance(node, Oscillation):
        warnings.extend(exhaustive_check(node.left, depth + 1))
        warnings.extend(exhaustive_check(node.right, depth + 1))
    elif isinstance(node, Fusion):
        warnings.extend(exhaustive_check(node.left, depth + 1))
        warnings.extend(exhaustive_check(node.right, depth + 1))
    elif isinstance(node, ColimitExpansion):
        warnings.extend(exhaustive_check(node.body, depth + 1))
    elif isinstance(node, ConvergenceLoop):
        warnings.extend(exhaustive_check(node.body, depth + 1))
    elif isinstance(node, ForLoop):
        warnings.extend(exhaustive_check(node.body, depth + 1))
    elif isinstance(node, WhileLoop):
        warnings.extend(exhaustive_check(node.body, depth + 1))
    elif isinstance(node, TaggedBlock):
        warnings.extend(exhaustive_check(node.body, depth + 1))
    elif isinstance(node, Pipeline):
        for step in node.steps:
            warnings.extend(exhaustive_check(step, depth + 1))
    elif isinstance(node, Parallel):
        for branch in node.branches:
            warnings.extend(exhaustive_check(branch, depth + 1))

    return warnings


# PURPOSE: 並列実行 (||) ノードの安全性チェック (Pepsis Rust Phase 2 — parallel_model.md)
def parallel_safety_check(node, depth=0) -> list[str]:
    """AST を再帰走査し、|| ノードの安全性を検証。

    Rust の Send/Sync 特性に着想を得た設計。
    同一 WF が複数ブランチに出現する場合、データ競合の可能性を警告。

    Returns:
        list of warning strings (空なら問題なし)
    """
    from hermeneus.src.ccl_ast import (
        Workflow, Oscillation, Fusion, Sequence, ConvergenceLoop,
        ColimitExpansion, ForLoop, IfCondition, WhileLoop,
        TaggedBlock, Pipeline, Parallel, OpType
    )

    warnings = []

    if isinstance(node, Parallel):
        # 各ブランチから WF ID を収集
        branch_wfs = []
        for branch in node.branches:
            wfs = set(extract_workflows(branch))
            branch_wfs.append(wfs)

        # ブランチ間の重複 WF を検出
        for i in range(len(branch_wfs)):
            for j in range(i + 1, len(branch_wfs)):
                shared = branch_wfs[i] & branch_wfs[j]
                if shared:
                    shared_str = ", ".join(sorted(shared))
                    warnings.append(
                        f"⚠️ [parallel] || ブランチ {i+1} と {j+1} で同一 WF ({shared_str}) が重複。"
                        f" データ競合の可能性があります。`*` で共有参照にするか、独立した WF に分割してください。"
                    )

        # 各ブランチも再帰チェック
        for branch in node.branches:
            warnings.extend(parallel_safety_check(branch, depth + 1))

    elif isinstance(node, Sequence):
        for step in node.steps:
            warnings.extend(parallel_safety_check(step, depth + 1))
    elif isinstance(node, Oscillation):
        warnings.extend(parallel_safety_check(node.left, depth + 1))
        warnings.extend(parallel_safety_check(node.right, depth + 1))
    elif isinstance(node, Fusion):
        warnings.extend(parallel_safety_check(node.left, depth + 1))
        warnings.extend(parallel_safety_check(node.right, depth + 1))
    elif isinstance(node, ColimitExpansion):
        warnings.extend(parallel_safety_check(node.body, depth + 1))
    elif isinstance(node, ConvergenceLoop):
        warnings.extend(parallel_safety_check(node.body, depth + 1))
    elif isinstance(node, ForLoop):
        warnings.extend(parallel_safety_check(node.body, depth + 1))
    elif isinstance(node, WhileLoop):
        warnings.extend(parallel_safety_check(node.body, depth + 1))
    elif isinstance(node, TaggedBlock):
        warnings.extend(parallel_safety_check(node.body, depth + 1))
    elif isinstance(node, Pipeline):
        for step in node.steps:
            warnings.extend(parallel_safety_check(step, depth + 1))
    elif isinstance(node, IfCondition):
        warnings.extend(parallel_safety_check(node.then_branch, depth + 1))
        if node.else_branch:
            warnings.extend(parallel_safety_check(node.else_branch, depth + 1))

    return warnings


# PURPOSE: WF ID → .agent/workflows/*.md の絶対パスに解決。
def resolve_wf_paths(wf_ids: list[str]) -> dict[str, str]:
    """WF ID → .agent/workflows/*.md の絶対パスに解決。

    /dia → dia.md, /noe → noe.md のように対応。
    存在しないファイルは除外。

    Returns:
        {"/dia": "/absolute/path/.agent/workflows/dia.md", ...}
    """
    project_root = Path(__file__).parent.parent.parent
    wf_dir = project_root / ".agent" / "workflows"
    paths = {}
    for wf_id in wf_ids:
        clean = wf_id.lstrip("/")
        wf_path = wf_dir / f"{clean}.md"
        if wf_path.exists():
            paths[wf_id] = str(wf_path.resolve())
        else:
            # エイリアス検索: boot+ → boot, dia+ → dia など
            # (演算子付きの場合、ベース名で検索)
            base = clean.rstrip("+-^!?'")
            base_path = wf_dir / f"{base}.md"
            if base_path.exists():
                paths[wf_id] = str(base_path.resolve())
    return paths


# PURPOSE: WF 定義ファイルから構造的要約を自動抽出 (L1 テンプレート自動充填)
def resolve_wf_summaries(wf_paths: dict[str, str]) -> dict[str, dict]:
    """WF 定義ファイルから purpose / phases / output_hint を抽出。

    抽出元:
      - YAML frontmatter の description: → purpose (fallback)
      - blockquote `> **目的**:` → purpose (優先)
      - `## 処理フロー` or `PHASE N` 見出し → phases
      - `## 出力形式` → output_hint

    Returns:
        {"/noe": {"purpose": "...", "phases": [...], "output_hint": "..."}, ...}
    """
    import re
    import yaml as _yaml

    summaries: dict[str, dict] = {}

    for wf_id, wf_path_str in wf_paths.items():
        summary: dict = {"purpose": "", "phases": [], "output_hint": ""}

        try:
            content = Path(wf_path_str).read_text(encoding="utf-8")
        except Exception:
            summaries[wf_id] = summary
            continue

        # --- 1. YAML frontmatter から description を抽出 ---
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            try:
                fm = _yaml.safe_load(fm_match.group(1))
                if isinstance(fm, dict) and fm.get("description"):
                    summary["purpose"] = fm["description"]
            except Exception:
                pass

        # --- 2. blockquote `> **目的**:` で上書き (より具体的) ---
        # frontmatter 直後 〜 最初の ## セクション見出しまでに限定
        # (各 STEP/PHASE 内の局所的な `> **目的**:` を拾わない)
        body = content[fm_match.end():] if fm_match else content
        # 最初の "## " 見出しの前までを冒頭定義ブロックとする
        intro_lines = []
        for line in body.split("\n"):
            if line.startswith("## "):
                break
            intro_lines.append(line)
        intro_block = "\n".join(intro_lines)
        purpose_match = re.search(
            r">\s*\*\*目的\*\*\s*[:：]\s*(.+)", intro_block
        )
        if purpose_match:
            summary["purpose"] = purpose_match.group(1).strip()

        # --- 3. PHASE / STEP 行を抽出 ---
        # パターン: "N. **PHASE N" or "N. **STEP N" (numbered list items)
        phase_pattern = re.compile(
            r"^\d+\.\s+\*\*(?:PHASE|STEP)\s+[\d.]+[\w]*\s*(?:—|:|-)\s*(.+?)\*\*",
            re.MULTILINE,
        )
        phases = phase_pattern.findall(content)
        if phases:
            summary["phases"] = [p.strip().rstrip("*") for p in phases]

        # fallback: `## PHASE N` 見出し
        if not summary["phases"]:
            heading_pattern = re.compile(
                r"^##\s+PHASE\s+\d+\s*(?:—|:|-)\s*(.+)", re.MULTILINE
            )
            summary["phases"] = [
                h.strip() for h in heading_pattern.findall(content)
            ]

        # --- 4. 出力形式セクションの冒頭を取得 ---
        output_match = re.search(
            r"##\s*出力形式\s*\n((?:.*\n){1,5})", content
        )
        if output_match:
            hint = output_match.group(1).strip()
            # コードフェンス (```) や空行を除外
            hint_lines = [
                l for l in hint.split("\n")
                if l.strip()
                and not l.strip().startswith("```")
                and "---" not in l
            ]
            if hint_lines:
                # テーブルヘッダーがあればそれだけ、なければ最初の行
                table_lines = [l for l in hint_lines if l.strip().startswith("|")]
                hint = table_lines[0] if table_lines else hint_lines[0]
                summary["output_hint"] = hint.strip()[:120]

        summaries[wf_id] = summary

    return summaries


# PURPOSE: WF 定義ファイルからサブモジュールのパスを抽出。
def resolve_submodules(wf_paths: dict[str, str]) -> dict[str, list[str]]:
    """WF 定義ファイルからサブモジュールのパスを抽出。

    WF の md ファイルを読み、## サブモジュール テーブル内の
    Markdown リンク [name](../path) を検出して絶対パスに解決する。

    Returns:
        {"/bye": ["/abs/path/value-pitch.md", "/abs/path/pitch_gallery.md"], ...}
    """
    import re
    submodules: dict[str, list[str]] = {}

    # Markdown リンクパターン: [text](relative/path.md)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)')

    for wf_id, wf_path_str in wf_paths.items():
        wf_path = Path(wf_path_str)
        subs: list[str] = []

        try:
            content = wf_path.read_text(encoding='utf-8')
        except Exception:
            continue

        # サブモジュールセクションを探す
        in_submodule_section = False
        for line in content.split('\n'):
            if line.strip().startswith('## サブモジュール') or line.strip().startswith('## Sub'):
                in_submodule_section = True
                continue
            if in_submodule_section and line.strip().startswith('## '):
                break  # 次のセクションに入った
            if in_submodule_section:
                for match in link_pattern.finditer(line):
                    rel_path = match.group(2)
                    # 相対パスを絶対パスに解決
                    abs_path = (wf_path.parent / rel_path).resolve()
                    if abs_path.exists():
                        subs.append(str(abs_path))

        if subs:
            submodules[wf_id] = subs

    return submodules


# PURPOSE: CCL 式をディスパッチ: パース → 構造表示 → 実行計画テンプレート
def dispatch(ccl_expr: str) -> DispatchResult:
    """CCL 式をディスパッチ: パース → 構造表示 → 実行計画テンプレート

    v3.0: @macro 検出時に MacroExecutor を自動実行し、
    エントロピー計測 + 逆伝播の結果を plan_template に埋め込む。
    これにより「意志より環境」(第零原則) が達成される。

    Returns:
        DispatchResult: TypedDict — success, ast, tree, workflows,
                        wf_paths, wf_submodules, plan_template, macro_plan, error 等
    """
    from hermeneus.src.parser import CCLParser as _Parser

    parser = _Parser()
    result: DispatchResult = {  # type: ignore[typeddict-item]
        "success": False,
        "ccl": ccl_expr,
        "ast": None,
        "tree": "",
        "workflows": [],
        "wf_paths": {},
        "wf_submodules": {},
        "wf_summaries": {},
        "plan_template": "",
        "macro_plan": None,
        "error": None,
    }


    # Step 0: パース
    try:
        ast = parser.parse(ccl_expr)
        result["ast"] = ast
        result["success"] = True
    except Exception as e:
        result["error"] = str(e)
        return result

    # Step 1: 木構造表示
    result["tree"] = format_ast_tree(ast)

    # Step 2: ワークフロー抽出 + パス解決 + 要約抽出
    result["workflows"] = extract_workflows(ast)
    result["wf_paths"] = resolve_wf_paths(result["workflows"])
    result["wf_submodules"] = resolve_submodules(result["wf_paths"])
    result["wf_summaries"] = resolve_wf_summaries(result["wf_paths"])

    # Step 2.3: 網羅性チェック (Pepsis Rust — exhaustive_check)
    exhaustive_warnings = exhaustive_check(ast)
    result["exhaustive_warnings"] = exhaustive_warnings

    # Step 2.4: 並列安全性チェック (Pepsis Rust — parallel_safety_check)
    parallel_warnings = parallel_safety_check(ast)
    result["parallel_warnings"] = parallel_warnings

    # Step 2.5: マクロ自動実行計画 (L1 環境制約)
    macro_section = ""
    if ccl_expr.strip().startswith("@"):
        try:
            from hermeneus.src.macro_executor import MacroExecutor
            executor = MacroExecutor()
            macro_result = executor.execute(ccl_expr)
            result["macro_plan"] = macro_result

            # マクロ実行計画セクションを生成
            lines = [
                f"【マクロ実行計画】@macro → AST walk (自動生成)",
                f"  展開: {macro_result.expanded_ccl}",
                f"  ステップ数: {len(macro_result.steps)}",
                f"  確信度: {macro_result.final_confidence:.0%}",
            ]
            if macro_result.bottleneck_step:
                lines.append(
                    f"  ⚠️ ボトルネック: {macro_result.bottleneck_step} "
                    f"(gradient={macro_result.gradient_map.get(macro_result.bottleneck_step, 0):.2f})"
                )
            lines.append("  実行順序:")
            for i, step in enumerate(macro_result.steps, 1):
                lines.append(f"    {i}. {step.node_id} (Δε={step.entropy_reduction:+.2f})")
            lines.append("  → 上記順序で各 WF 定義を view_file し、順次実行せよ")

            macro_section = "\n".join(lines)
        except Exception as e:
            macro_section = f"【マクロ実行計画】⚠️ MacroExecutor エラー: {e}"

    # Step 3: 射提案の自動生成 (BC-8 引力化)
    morphism_section = ""
    try:
        from mekhane.taxis.morphism_proposer import parse_trigonon, format_proposal
        for wf_id, wf_path in result["wf_paths"].items():
            trigonon = parse_trigonon(Path(wf_path))
            if trigonon:
                proposal = format_proposal(
                    wf_id.lstrip("/"), trigonon, confidence=None
                )
                morphism_section += f"\n{proposal}\n"
    except Exception:
        morphism_section = "\n  (射提案の自動生成に失敗 — 手動で trigonon を確認)\n"

    # Step 4: 実行計画テンプレート
    wf_list = ", ".join(result["workflows"])

    # view_file コマンド一覧 (Agent がコピペで開ける)
    view_lines = []
    for wf_id, wf_path in result["wf_paths"].items():
        view_lines.append(f"  view_file {wf_path}")
        # サブモジュールがあれば階層表示
        subs = result["wf_submodules"].get(wf_id, [])
        for i, sub_path in enumerate(subs):
            prefix = "└──" if i == len(subs) - 1 else "├──"
            sub_name = Path(sub_path).name
            view_lines.append(f"    {prefix} view_file {sub_path}  ({sub_name})")
    view_cmds = "\n".join(view_lines)
    if not view_cmds:
        view_cmds = "  (WF 定義ファイルが見つかりません)"

    # マクロセクションがあれば plan_template の先頭に挿入
    macro_block = f"\n{macro_section}\n" if macro_section else ""

    # Step 5: 実行計画の自動充填 (L1 テンプレート自動充填)
    execution_plan_lines = []
    wf_summaries = result["wf_summaries"]
    for i, wf_id in enumerate(result["workflows"], 1):
        summary = wf_summaries.get(wf_id, {})
        purpose = summary.get("purpose", "")
        phases = summary.get("phases", [])
        output_hint = summary.get("output_hint", "")

        line = f"  Step {i}: {wf_id}"
        if purpose:
            line += f"\n    目的: {purpose}"
        if phases:
            phase_str = " → ".join(phases[:5])  # 最大5フェーズ
            line += f"\n    フェーズ: {phase_str}"
        if output_hint:
            line += f"\n    出力: {output_hint}"
        execution_plan_lines.append(line)

    if execution_plan_lines:
        execution_plan = "\n".join(execution_plan_lines)
    else:
        execution_plan = "  (WF 要約を抽出できませんでした — view_file で確認してください)"

    # Step 6: 深度レベル判定 (CCL 派生から推定)
    # "+" → L3, 無印 → L2, "-" → L1
    has_plus = "+" in ccl_expr
    has_minus = "-" in ccl_expr and ">" not in ccl_expr  # >> は除外
    if has_plus:
        depth_level = 3
    elif has_minus:
        depth_level = 1
    else:
        depth_level = 2
    result["depth_level"] = depth_level

    # Step 6.1: Adaptive Depth トリガー (BC-18 v3.5)
    result["adaptive_depth"] = {
        "current_level": depth_level,
        "triggers": [
            {"condition": "BC-14 FaR confidence <50% x2", "action": "propose L+1"},
            {"condition": "AMP loop Stage 3→1 x2", "action": "force L+1"},
            {"condition": "Creator explicit request", "action": "immediate L+1"},
        ],
    }

    # UML セクション: L2+ のみ
    if depth_level >= 2:
        uml_pre = """【UML Pre-check】(WF 実行前に回答)
  S1 [O1]: 入力を正しく理解したか？ → (回答)
  S2 [A1]: 第一印象・直感はどうか？ → (回答)"""
        uml_post = """【UML Post-check】(WF 実行後に回答)
  S3 [A2]: 批判的に再評価したか？ → (回答)
  S4 [O4]: 決定は妥当か？ 説明できるか？ → (回答)
  S5 [A4]: 確信度は適切か？ 過信していないか？ (FP 32.5%) → (回答)"""
    else:
        uml_pre = ""
        uml_post = ""

    # 射提案セクション: L2+ のみ、かつ改善版フォーマット
    if depth_level >= 2 and morphism_section.strip():
        morphism_block = f"""【射提案 @complete】(WF 完了時に以下を出力すること)
{morphism_section}"""
    else:
        morphism_block = ""

    # Step 7: 演算子警告の生成 (spec_injector + failure_db 連携)
    warnings_block = ""
    quiz_block = ""
    try:
        from mekhane.ccl.spec_injector import (
            get_warnings_for_expr, get_warned_operators, SpecInjector
        )
        # 7a: 既知の危険パターン警告
        op_warnings = get_warnings_for_expr(ccl_expr)
        already_warned = get_warned_operators(ccl_expr)

        # 7b: failure_db からの過去失敗パターン警告 (演算子ベース重複排除)
        try:
            from mekhane.ccl.learning.failure_db import get_failure_db
            db = get_failure_db()
            db_warnings = db.get_warnings(ccl_expr)
            for w in db_warnings:
                if w.operator not in already_warned:
                    op_warnings.append(f"⚠️ [{w.severity}] {w.operator}: {w.message}")
                    already_warned.add(w.operator)
        except (ImportError, Exception):
            pass

        if op_warnings:
            warnings_block = "【⚠️ 演算子注意】\n" + "\n".join(f"  {w}" for w in op_warnings)

        # 7c: 危険演算子含有時のみ理解確認クイズを注入
        dangerous_ops = {'!', '*^', '\\'}
        injector = SpecInjector()
        detected_ops = injector.parse_operators(ccl_expr)
        # parse_operators が複合演算子も検出するため、直接 & で判定
        quiz_target = detected_ops & dangerous_ops
        if quiz_target:
            quiz_block = injector.generate_quiz(quiz_target)
            # G4: クイズ効果ログ — 生成を記録
            try:
                from mekhane.ccl.learning.quiz_logger import get_quiz_logger
                ql = get_quiz_logger()
                result["quiz_entry_id"] = ql.log_quiz_generated(  # type: ignore[typeddict-unknown-key]
                    ccl_expr=ccl_expr,
                    operators=quiz_target,
                )
            except (ImportError, Exception):
                pass
    except ImportError:
        pass  # spec_injector が利用不可の場合はスキップ

    # テンプレート構築 (空セクションを除外して組み立て)
    sections = [
        f"【CCL】{ccl_expr}",
    ]
    if warnings_block:
        sections.append(warnings_block)
    sections += [
        f"【構造】\n{result['tree']}",
        f"【関連WF】{wf_list}",
    ]

    # 網羅性 + 並列安全性の警告を注入
    safety_warnings = result.get("exhaustive_warnings", []) + result.get("parallel_warnings", [])
    if safety_warnings:
        safety_block = "【🦀 Pepsis Safety Check】\n" + "\n".join(f"  {w}" for w in safety_warnings)
        sections.append(safety_block)

    sections += [
        f"【WF定義】以下を view_file で開くこと:\n{view_cmds}{macro_block}",
    ]
    if uml_pre:
        sections.append(uml_pre)
    sections.append(f"【実行計画】(AST 順序に基づく自動生成)\n{execution_plan}")
    if quiz_block:
        sections.append(f"【理解確認】\n{quiz_block}")
    sections.append("【/dia 反論】(AI が最低1つの懸念を提示)")
    if uml_post:
        sections.append(uml_post)
    if morphism_block:
        sections.append(morphism_block)
    # Adaptive Depth: L1 以下のとき深度上昇トリガーを表示
    if depth_level <= 1:
        ad_section = """【📈 Adaptive Depth】(実行中に以下を検知したら深度を上げよ)
  ・BC-14 FaR 確信度 <50% が 2 回連続 → L+1 を提案
  ・AMP ループ Stage 3→1 が 2 回発動 → L+1 を強制
  ・Creator が「もっと深く」と指示 → 即座に L+1"""
        sections.append(ad_section)
    # Step 8: ルーティングフィードバック収集の環境強制 (Aristos L3)
    if len(result["workflows"]) >= 2:
        fb_section = """【📊 Aristos Feedback】(WF 完了後に実行)
  以下を実行してルーティング品質を記録せよ:
  ```python
  from aristos.route_feedback import log_from_dispatch
  log_from_dispatch(dispatch_result, actual_time_min=X, had_errors=False)
  ```
  → フィードバックは PT 最適化 (L3 GA) の学習データになる"""
        sections.append(fb_section)

        # route_context を result に付加
        result["route_context"] = {
            "source": result["workflows"][0].lstrip("/"),
            "target": result["workflows"][-1].lstrip("/"),
            "route": [w.lstrip("/") for w in result["workflows"]],
            "depth_level": depth_level,
            "wf_count": len(result["workflows"]),
        }

    sections.append("→ これで進めてよいですか？")

    tmpl = "\n".join(sections)
    result["plan_template"] = tmpl

    return result


# PURPOSE: CLI エントリポイント
def main():
    """CLI エントリポイント"""
    if len(sys.argv) < 2:
        print("Usage: python hermeneus/src/dispatch.py '<CCL式>'")
        print("Example: python hermeneus/src/dispatch.py '/dia+~/noe'")
        print("Example: python hermeneus/src/dispatch.py '(/dia+~/noe)~/pan+'")
        sys.exit(1)

    ccl_expr = sys.argv[1]

    print(f"{'='*60}")
    print(f"  Hermēneus CCL Dispatch")
    print(f"  入力: {ccl_expr}")
    print(f"{'='*60}")
    print()

    # 循環インポート回避: dispatch() 内でパーサーを遅延インポート
    result = dispatch(ccl_expr)

    if not result["success"]:
        print(f"❌ Parse Error: {result['error']}")
        print()
        print("パーサー拡張が必要か、式の修正が必要です。")
        print("Creator に報告してください。")
        sys.exit(1)

    print("✅ パース成功")
    print()
    print("── AST 構造 ──────────────────────────────")
    print(result["tree"])
    print()
    print(f"── 関連 WF: {', '.join(result['workflows'])} ──")
    print()

    # WF 定義ファイルパス
    if result["wf_paths"]:
        print("── WF 定義ファイル (view_file で開け) ────")
        for wf_id, path in result["wf_paths"].items():
            print(f"  {wf_id} → {path}")
        print()

    print("── 実行計画テンプレート ──────────────────")
    print(result["plan_template"])
    print()
    print("─" * 60)
    print("↑ この出力を基に AST 順序で WF を実行せよ。")


if __name__ == "__main__":
    main()

