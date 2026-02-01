#!/usr/bin/env python3
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

# Import Perplexity API
PERPLEXITY_SCRIPT = Path("/home/laihuip001/oikos/hegemonikon/mekhane/peira/scripts")
sys.path.insert(0, str(PERPLEXITY_SCRIPT))

from perplexity_api import search as perplexity_search

EXPERIMENTS_DIR = Path(__file__).parent / "experiments"


# =============================================================================
# Thread Definitions
# =============================================================================

THREAD_REGISTRY = {
    "antigravity": {
        "name": "Antigravity",
        "supported_ccl": ["/noe", "/dia", "/u", "/bou"],
        "executor": "manual",  # 手動実行
    },
    "perplexity": {
        "name": "Perplexity",
        "supported_ccl": ["/sop", "/zet"],
        "executor": "api",
    },
    "claude": {
        "name": "Claude CLI",
        "supported_ccl": ["/s", "/ene", "/mek"],
        "executor": "cli",
    },
    "gemini": {
        "name": "Gemini CLI",
        "supported_ccl": ["/tek", "/sta"],
        "executor": "cli",
    },
}


def select_thread(ccl: str) -> str:
    """CCL要素から最適なスレッドを選択。"""
    # 修飾子を除去してベースを取得
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
            timeout=120,
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
    
    prompt = f"{context}\n\nExecute CCL: {ccl}\n\nProvide a detailed response."
    
    try:
        result = subprocess.run(
            ["node", "/home/laihuip001/oikos/.npm/_npx/38c708f8d73fe4c9/node_modules/@google/gemini-cli/bundle/gemini.js", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
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


def execute_manual(ccl: str, context: str) -> Dict[str, Any]:
    """手動実行 (Antigravity)。"""
    return {
        "status": "manual",
        "ccl": ccl,
        "thread": "antigravity",
        "note": "Antigravityが手動で実行。結果は統合時に入力してください。",
    }


def execute_ccl(ccl: str, context: str) -> Dict[str, Any]:
    """CCL要素を適切なスレッドで実行。"""
    thread = select_thread(ccl)
    
    print(f"[Coordinator] {ccl} -> {thread}")
    
    if thread == "perplexity":
        return execute_perplexity(ccl, context)
    elif thread == "claude":
        return execute_claude(ccl, context)
    elif thread == "gemini":
        return execute_gemini(ccl, context)
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
