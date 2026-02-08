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

# パッケージパス追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def format_ast_tree(node, indent=0) -> str:
    """AST をインデント付きで木構造表示"""
    from hermeneus.src.ast import (
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
            from hermeneus.src.ast import OpType
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


def extract_workflows(node) -> list:
    """AST から全ワークフロー ID を再帰的に抽出"""
    from hermeneus.src.ast import (
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


def dispatch(ccl_expr: str) -> dict:
    """CCL 式をディスパッチ: パース → 構造表示 → 実行計画テンプレート

    Returns:
        dict with keys: success, ast, tree, workflows, wf_paths,
                        plan_template, error
    """
    from hermeneus.src.parser import CCLParser as _Parser

    parser = _Parser()
    result = {
        "success": False,
        "ccl": ccl_expr,
        "ast": None,
        "tree": "",
        "workflows": [],
        "wf_paths": {},
        "plan_template": "",
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

    # Step 2: ワークフロー抽出 + パス解決
    result["workflows"] = extract_workflows(ast)
    result["wf_paths"] = resolve_wf_paths(result["workflows"])

    # Step 3: 実行計画テンプレート
    wf_list = ", ".join(result["workflows"])

    # view_file コマンド一覧 (Agent がコピペで開ける)
    view_cmds = "\n".join(
        f"  view_file {p}" for p in result["wf_paths"].values()
    )
    if not view_cmds:
        view_cmds = "  (WF 定義ファイルが見つかりません)"

    tmpl = f"""【CCL】{ccl_expr}
【構造】
{result['tree']}
【関連WF】{wf_list}
【WF定義】以下を view_file で開くこと:
{view_cmds}
【実行計画】(AI が AST 構造に基づいて記入)
【/dia 反論】(AI が最低1つの懸念を提示)
→ これで進めてよいですか？"""
    result["plan_template"] = tmpl

    return result


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

