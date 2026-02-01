#!/usr/bin/env python3
"""
Synergeia Interactive Coordinator
==================================

手動スレッド (Antigravity) の結果を対話的に入力し、
分散実行結果を統合するインタラクティブモード。

Usage:
    python interactive.py "/noe+ || /sop+"
    
Flow:
    1. CCLをパース
    2. 自動スレッド (Perplexity等) を実行
    3. 手動スレッド (Antigravity) の結果入力を待つ
    4. 全結果を統合して保存
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Import coordinator
sys.path.insert(0, str(Path(__file__).parent))
from coordinator import (
    parse_ccl, 
    execute_perplexity, 
    select_thread,
    EXPERIMENTS_DIR,
    THREAD_REGISTRY
)


def prompt_manual_input(ccl: str, context: str) -> Dict[str, Any]:
    """手動スレッドの結果を対話的に入力。"""
    print(f"\n{'='*60}")
    print(f"[MANUAL INPUT REQUIRED]")
    print(f"{'='*60}")
    print(f"CCL: {ccl}")
    print(f"Context: {context[:100]}..." if len(context) > 100 else f"Context: {context}")
    print(f"{'='*60}")
    print("Antigravityとして、このCCLを実行してください。")
    print("結果を入力 (複数行可、空行で終了):")
    print(f"{'='*60}\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError:
            break
    
    answer = "\n".join(lines)
    
    return {
        "status": "success",
        "ccl": ccl,
        "thread": "antigravity",
        "answer": answer,
        "input_method": "interactive",
        "timestamp": datetime.now().isoformat(),
    }


def execute_ccl_interactive(ccl: str, context: str) -> Dict[str, Any]:
    """CCLを実行 (自動または対話的手動)。"""
    thread = select_thread(ccl)
    
    print(f"[Coordinator] {ccl} -> {thread}")
    
    if thread == "perplexity":
        return execute_perplexity(ccl, context)
    elif thread == "antigravity":
        return prompt_manual_input(ccl, context)
    else:
        # 未実装スレッドは手動にフォールバック
        print(f"[Warning] Thread '{thread}' not implemented, falling back to manual")
        return prompt_manual_input(ccl, context)


def coordinate_interactive(ccl_expr: str, context: str = "") -> Dict[str, Any]:
    """対話的にCCLを分散実行。"""
    plan = parse_ccl(ccl_expr)
    results = []
    
    print(f"\n{'='*60}")
    print(f"[Interactive Coordinator] CCL: {ccl_expr}")
    print(f"[Interactive Coordinator] Type: {plan['type']}")
    print(f"[Interactive Coordinator] Elements: {plan['elements']}")
    print(f"{'='*60}\n")
    
    # 自動スレッドを先に実行
    auto_results = {}
    manual_ccls = []
    
    for elem in plan["elements"]:
        thread = select_thread(elem)
        if thread == "perplexity":
            print(f"[Auto] Executing {elem} via {thread}...")
            auto_results[elem] = execute_perplexity(elem, context)
        else:
            manual_ccls.append(elem)
    
    # 手動スレッドを対話的に入力
    for elem in manual_ccls:
        # パイプラインの場合、前の結果をコンテキストに
        ctx = context
        if plan["type"] == "pipeline":
            idx = plan["elements"].index(elem)
            if idx > 0:
                prev_elem = plan["elements"][idx - 1]
                if prev_elem in auto_results:
                    prev_answer = auto_results[prev_elem].get("answer", "")[:300]
                    ctx = f"{context}\n\nPrevious result ({prev_elem}):\n{prev_answer}"
        
        result = prompt_manual_input(elem, ctx)
        auto_results[elem] = result
    
    # 結果を順序どおりに整理
    for elem in plan["elements"]:
        results.append(auto_results.get(elem, {"status": "missing", "ccl": elem}))
    
    return {
        "ccl": ccl_expr,
        "plan": plan,
        "results": results,
        "mode": "interactive",
        "timestamp": datetime.now().isoformat(),
    }


def save_result(result: Dict[str, Any]) -> Path:
    """結果を保存。"""
    EXPERIMENTS_DIR.mkdir(exist_ok=True)
    
    exp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = EXPERIMENTS_DIR / f"interactive_{exp_id}.json"
    log_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n[Coordinator] Result saved: {log_file}")
    return log_file


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    ccl_expr = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else "Hegemonikon CCL execution"
    
    result = coordinate_interactive(ccl_expr, context)
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
            answer = r["answer"]
            print(f"    Answer: {answer[:100]}..." if len(answer) > 100 else f"    Answer: {answer}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
