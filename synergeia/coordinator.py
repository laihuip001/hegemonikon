#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- synergeia/ Synergeia Coordinator
"""
Synergeia Coordinator (簡易版)
==============================

CCL式を解析し、適切なスレッドに分配する簡易Coordinator。

Usage:
    python coordinator.py "/noe+ || /sop+"
    python coordinator.py "/noe+ |> /dia+ |> /ene+"

Supported:
    - || (並列): 複数スレッドで同時実行
    - |> (パイプライン): 順次実行
    - @thread[agent]{CCL}: スレッド指定
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Add hegemonikon to path for Hermeneus import
HEGEMONIKON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HEGEMONIKON_ROOT))

# Import Perplexity API
PERPLEXITY_SCRIPT = Path("/home/laihuip001/oikos/hegemonikon/mekhane/peira/scripts")
sys.path.insert(0, str(PERPLEXITY_SCRIPT))

from perplexity_api import search as perplexity_search

# Import Hermeneus CCL Compiler
try:
    from hermeneus.src import compile_ccl, expand_ccl
    from hermeneus.src import execute_ccl as hermeneus_execute
    from hermeneus.src import parse_ccl as hermeneus_parse
    from hermeneus.src.macros import get_all_macros
    HERMENEUS_AVAILABLE = True
    STANDARD_MACROS = get_all_macros()
except ImportError:
    HERMENEUS_AVAILABLE = False
    STANDARD_MACROS = {}
    hermeneus_execute = None
    print("[Warning] Hermeneus not available, falling back to manual execution")

# Import FEP Selector
try:
    from synergeia.fep_selector import select_thread_by_fep, ThreadRecommendation
    FEP_SELECTOR_AVAILABLE = True
except ImportError:
    FEP_SELECTOR_AVAILABLE = False

EXPERIMENTS_DIR = Path(__file__).parent / "experiments"


# =============================================================================
# Thread Definitions
# =============================================================================

THREAD_REGISTRY = {
    "hermeneus": {
        "name": "Hermeneus CCL Compiler",
        "supported_ccl": ["*"],  # すべての CCL をコンパイル可能
        "executor": "lmql",
        "priority": 0,  # 最優先
    },
    "antigravity": {
        "name": "Antigravity",
        "supported_ccl": ["/noe", "/dia", "/u", "/bou"],
        "executor": "manual",  # 手動実行
        "priority": 10,
    },
    "perplexity": {
        "name": "Perplexity",
        "supported_ccl": ["/sop", "/zet"],
        "executor": "api",
        "priority": 5,
    },
    "claude": {
        "name": "Claude CLI",
        "supported_ccl": ["/s", "/mek"],
        "executor": "cli",
        "priority": 5,
    },
    "gemini": {
        "name": "Gemini CLI",
        "supported_ccl": ["/tek", "/sta"],
        "executor": "cli",
        "priority": 5,
    },
    "codex": {
        "name": "OpenAI Codex",
        "supported_ccl": ["/ene", "/pra"],  # 実行系
        "executor": "cli",
        "priority": 5,
    },
}


def select_thread(ccl: str, use_fep: bool = True) -> str:
    """
    CCL要素から最適なスレッドを選択。
    
    Args:
        ccl: CCL 式
        use_fep: True の場合 FEP ベースの複雑度分析を使用
    
    Returns:
        スレッド ID
    """
    # FEP ベース選択 (複雑度に基づく)
    if use_fep and FEP_SELECTOR_AVAILABLE:
        try:
            recommendation = select_thread_by_fep(ccl)
            print(f"[FEP] {ccl} -> {recommendation.thread} (complexity: {recommendation.complexity_score:.2f})")
            return recommendation.thread
        except Exception as e:
            print(f"[FEP] Error: {e}, falling back to rule-based selection")
    
    # ルールベース選択 (フォールバック)
    base = re.match(r"(/\w+)", ccl)
    if not base:
        return "antigravity"
    
    base_ccl = base.group(1)
    
    for thread_id, config in THREAD_REGISTRY.items():
        if base_ccl in config["supported_ccl"]:
            return thread_id

    return "antigravity"  # デフォルト


# =============================================================================
# CLI Paths
# =============================================================================

CLAUDE_CLI = "/home/laihuip001/oikos/.local/bin/claude"
GEMINI_CLI = "node /home/laihuip001/oikos/.npm/_npx/38c708f8d73fe4c9/node_modules/@google/gemini-cli/bundle/gemini.js"
CODEX_CLI = "/home/laihuip001/oikos/hegemonikon/synergeia/node_modules/.bin/codex"


# =============================================================================
# Executors
# =============================================================================

def execute_perplexity(ccl: str, context: str) -> Dict[str, Any]:
    """Perplexity API でCCLを実行。"""
    # CCLを検索クエリに変換
    query = f"{context} {ccl.replace('/', ' ').replace('+', ' deep').replace('-', ' brief')}"
    
    result = perplexity_search(query)
    
    if "error" in result:
        return {"status": "error", "error": result["error"], "ccl": ccl}
    
    return {
        "status": "success",
        "ccl": ccl,
        "thread": "perplexity",
        "answer": result["answer"],
        "citations": result.get("citations", []),
        "cost": result["cost"],
    }


def execute_claude(ccl: str, context: str) -> Dict[str, Any]:
    """Claude CLI でCCLを実行。"""
    import subprocess
    
    prompt = f"{context}\n\nExecute CCL: {ccl}\n\nProvide a detailed response."
    
    try:
        result = subprocess.run(
            [CLAUDE_CLI, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=600,  # 最大10分
            cwd="/home/laihuip001/oikos/hegemonikon"
        )
        answer = result.stdout.strip()
        if result.returncode != 0:
            return {"status": "error", "error": result.stderr, "ccl": ccl}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout (120s)", "ccl": ccl}
    except Exception as e:
        return {"status": "error", "error": str(e), "ccl": ccl}
    
    return {
        "status": "success",
        "ccl": ccl,
        "thread": "claude",
        "answer": answer,
    }


def execute_gemini(ccl: str, context: str) -> Dict[str, Any]:
    """Gemini CLI でCCLを実行。"""
    import subprocess
    
    # ツール操作を避けるプロンプト
    prompt = f"""You are a Hegemonikon CCL interpreter.
Do NOT use any file system tools. Just analyze and respond in text.

{context}

Analyze and explain the CCL command: {ccl}

Provide a detailed conceptual response without executing any tools."""
    
    try:
        result = subprocess.run(
            [
                "node", 
                "/home/laihuip001/oikos/.npm/_npx/38c708f8d73fe4c9/node_modules/@google/gemini-cli/bundle/gemini.js", 
                "-p", prompt
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 最大10分
            cwd="/home/laihuip001/oikos/hegemonikon"
        )
        # Geminiは最初の2行がログなので除去
        lines = result.stdout.strip().split("\n")
        answer = "\n".join(lines[2:]) if len(lines) > 2 else result.stdout.strip()
        if result.returncode != 0:
            return {"status": "error", "error": result.stderr, "ccl": ccl}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout (120s)", "ccl": ccl}
    except Exception as e:
        return {"status": "error", "error": str(e), "ccl": ccl}
    
    return {
        "status": "success",
        "ccl": ccl,
        "thread": "gemini",
        "answer": answer,
    }


def execute_codex(ccl: str, context: str) -> Dict[str, Any]:
    """OpenAI Codex CLI でCCLを実行。"""
    import subprocess
    
    prompt = f"{context}\n\nExecute CCL: {ccl}\n\nProvide a detailed response."
    
    try:
        result = subprocess.run(
            [CODEX_CLI, "exec", prompt],
            capture_output=True,
            text=True,
            timeout=600,  # 最大10分
            cwd="/home/laihuip001/oikos/hegemonikon"
        )
        # Codex は最初と最後にメタデータがあるので整理
        lines = result.stdout.strip().split("\n")
        # "Hello from Codex" のような実際の出力を抽出
        answer = "\n".join([l for l in lines if not l.startswith("OpenAI Codex") and not l.startswith("---") and not l.startswith("workdir:") and not l.startswith("model:") and not l.startswith("provider:") and not l.startswith("approval:") and not l.startswith("sandbox:") and not l.startswith("reasoning") and not l.startswith("session id:") and not l.startswith("user") and not l.startswith("mcp startup:") and not l.startswith("codex") and not l.startswith("tokens used")])
        if result.returncode != 0:
            return {"status": "error", "error": result.stderr, "ccl": ccl}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout (600s)", "ccl": ccl}
    except Exception as e:
        return {"status": "error", "error": str(e), "ccl": ccl}
    
    return {
        "status": "success",
        "ccl": ccl,
        "thread": "codex",
        "answer": answer.strip(),
    }


def execute_manual(ccl: str, context: str) -> Dict[str, Any]:
    """手動実行 (Antigravity)。"""
    return {
        "status": "manual",
        "ccl": ccl,
        "thread": "antigravity",
        "note": "Antigravityが手動で実行。結果は統合時に入力してください。",
    }


def execute_hermeneus(ccl: str, context: str, compile_only: bool = False) -> Dict[str, Any]:
    """
    Hermeneus CCL Compiler で実行。
    
    Args:
        ccl: CCL 式
        context: 実行コンテキスト
        compile_only: True の場合は LMQL コードを返すだけ（実行しない）
    """
    if not HERMENEUS_AVAILABLE:
        return execute_manual(ccl, context)
    
    try:
        # Step 1: CCL をコンパイル (標準マクロを使用)
        lmql_code = compile_ccl(ccl, macros=STANDARD_MACROS)
        
        if compile_only:
            return {
                "status": "compiled",
                "ccl": ccl,
                "thread": "hermeneus",
                "lmql": lmql_code,
                "macros_available": list(STANDARD_MACROS.keys()),
                "note": "LMQL code generated (not executed)",
            }
        
        # Step 2: 展開情報を取得
        expansion = expand_ccl(ccl, macros=STANDARD_MACROS)
        
        # Step 3: AST を取得
        ast = hermeneus_parse(expansion.expanded)
        
        # Step 4: Synteleia Monitor - コンテキストに監査情報を自動追加
        enriched_context = context
        synteleia_report = None
        
        try:
            from synteleia import SynteleiaOrchestrator, AuditTarget, AuditTargetType
            
            # コンテキストに Synteleia 監査を実行
            if context and len(context) > 100:
                orch = SynteleiaOrchestrator()
                target = AuditTarget(
                    content=context,
                    target_type=AuditTargetType.THOUGHT,
                    source="user_context"
                )
                audit_result = orch.audit(target)
                
                if audit_result.all_issues:
                    issue_lines = []
                    for issue in audit_result.all_issues:
                        issue_lines.append(f"- [{issue.severity.value.upper()}] {issue.code}: {issue.message}")
                        if issue.suggestion:
                            issue_lines.append(f"  - 提案: {issue.suggestion}")
                    
                    synteleia_report = f"""
## Synteleia 監査結果 (自動追加)
Issues: {len(audit_result.all_issues)}
{chr(10).join(issue_lines)}
"""
                    enriched_context = f"{context}\n{synteleia_report}"
        except ImportError:
            pass  # Synteleia 未インストール
        except Exception:
            pass  # 監査エラーは無視 (LLM 実行を優先)
        
        # Step 5: LLM で実行 (hermeneus_execute が利用可能な場合)
        llm_output = None
        if hermeneus_execute is not None:
            exec_result = hermeneus_execute(ccl, enriched_context)
            if exec_result.status.value == "success":
                llm_output = exec_result.output
        
        return {
            "status": "success",
            "ccl": ccl,
            "thread": "hermeneus",
            "expansion": {
                "original": expansion.original,
                "expanded": expansion.expanded,
                "formal": expansion.formal,
            },
            "ast_type": type(ast).__name__,
            "lmql": lmql_code,
            "llm_output": llm_output,
            "macros_used": len(STANDARD_MACROS),
            "note": "Compiled and executed by Hermeneus.",
        }
        
    except Exception as e:
        return {
            "status": "error",
            "ccl": ccl,
            "thread": "hermeneus",
            "error": str(e),
        }


def execute_ccl(ccl: str, context: str, use_hermeneus: bool = True) -> Dict[str, Any]:
    """
    CCL要素を適切なスレッドで実行。
    
    Args:
        ccl: CCL 式
        context: 実行コンテキスト
        use_hermeneus: True の場合は Hermeneus で構造化コンパイル
    """
    # Hermeneus モード: 構造化 LMQL コンパイル
    if use_hermeneus and HERMENEUS_AVAILABLE:
        hermeneus_result = execute_hermeneus(ccl, context)
        if hermeneus_result["status"] != "error":
            return hermeneus_result
        # エラー時はフォールバック
        print(f"[Coordinator] Hermeneus failed, falling back to thread selection")
    
    thread = select_thread(ccl)
    
    print(f"[Coordinator] {ccl} -> {thread}")
    
    if thread == "perplexity":
        return execute_perplexity(ccl, context)
    elif thread == "claude":
        return execute_claude(ccl, context)
    elif thread == "gemini":
        return execute_gemini(ccl, context)
    elif thread == "codex":
        return execute_codex(ccl, context)
    else:
        return execute_manual(ccl, context)


# =============================================================================
# CCL Parser
# =============================================================================

def parse_ccl(ccl_expr: str) -> Dict[str, Any]:
    """
    CCL式をパースして実行計画を生成。
    
    Returns:
        {
            "type": "parallel" | "pipeline" | "single",
            "elements": [...]
        }
    """
    ccl_expr = ccl_expr.strip()
    
    # 並列 (||)
    if "||" in ccl_expr:
        elements = [e.strip() for e in ccl_expr.split("||")]
        return {"type": "parallel", "elements": elements}
    
    # パイプライン (|>)
    if "|>" in ccl_expr:
        elements = [e.strip() for e in ccl_expr.split("|>")]
        return {"type": "pipeline", "elements": elements}
    
    # 単一
    return {"type": "single", "elements": [ccl_expr]}


# =============================================================================
# Coordinator
# =============================================================================

def coordinate(ccl_expr: str, context: str = "") -> Dict[str, Any]:
    """
    CCL式を解析し、分散実行を調整。
    """
    plan = parse_ccl(ccl_expr)
    results = []
    
    print(f"\n{'='*60}")
    print(f"[Coordinator] CCL: {ccl_expr}")
    print(f"[Coordinator] Type: {plan['type']}")
    print(f"[Coordinator] Elements: {plan['elements']}")
    print(f"{'='*60}\n")
    
    if plan["type"] == "parallel":
        # 並列実行
        with ThreadPoolExecutor(max_workers=len(plan["elements"])) as executor:
            futures = {
                executor.submit(execute_ccl, elem, context): elem
                for elem in plan["elements"]
            }
            for future in as_completed(futures):
                results.append(future.result())
    
    elif plan["type"] == "pipeline":
        # パイプライン実行
        prev_result = None
        for elem in plan["elements"]:
            ctx = context
            if prev_result and prev_result.get("answer"):
                ctx = f"{context} Previous: {prev_result['answer'][:200]}"
            result = execute_ccl(elem, ctx)
            results.append(result)
            prev_result = result
    
    else:
        # 単一実行
        results.append(execute_ccl(plan["elements"][0], context))
    
    return {
        "ccl": ccl_expr,
        "plan": plan,
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


def save_result(result: Dict[str, Any]):
    """結果を保存。"""
    EXPERIMENTS_DIR.mkdir(exist_ok=True)
    
    exp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = EXPERIMENTS_DIR / f"coord_{exp_id}.json"
    log_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n[Coordinator] Result saved: {log_file}")
    return log_file


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    ccl_expr = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else "Hegemonikon CCL execution"
    
    result = coordinate(ccl_expr, context)
    log_file = save_result(result)
    
    # サマリ出力
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in result["results"]:
        status = r.get("status", "unknown")
        thread = r.get("thread", "unknown")
        ccl = r.get("ccl", "unknown")
        print(f"  [{status}] {ccl} -> {thread}")
        if status == "success" and "answer" in r:
            print(f"    Answer: {r['answer'][:100]}...")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
