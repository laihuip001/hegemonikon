#!/usr/bin/env python3
# PROOF: [L3/実験] <- synergeia/ Parallel CCL Experiment
"""
Synergeia Experiment 001: 並列CCL実行
======================================

CCL: /noe+ || /sop+

- Thread A (Antigravity): /noe+ を実行 (このスクリプト外で)
- Thread B (Perplexity): /sop+ を実行

このスクリプトは Thread B (Perplexity) を担当し、
結果を experiments/ に記録する。
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent path for perplexity_api import
PERPLEXITY_SCRIPT = Path("/home/makaron8426/oikos/hegemonikon/mekhane/peira/scripts")
sys.path.insert(0, str(PERPLEXITY_SCRIPT))

from perplexity_api import search

EXPERIMENTS_DIR = Path(__file__).parent / "experiments"


def run_sop_thread(query: str) -> dict:
    """
    /sop+ スレッドを実行。
    Perplexity API を使用して調査を行う。
    """
    print(f"[Thread B: /sop+] Starting with query: {query}")
    
    result = search(query)
    
    if "error" in result:
        print(f"[Thread B: /sop+] Error: {result['error']}")
        return {"status": "error", "error": result["error"]}
    
    print(f"[Thread B: /sop+] Completed. Cost: ${result['cost']:.4f}")
    
    return {
        "status": "success",
        "thread": "sop+",
        "agent": "perplexity",
        "query": query,
        "answer": result["answer"],
        "citations": result.get("citations", []),
        "cost": result["cost"],
        "timestamp": datetime.now().isoformat()
    }


def save_experiment_log(experiment_id: str, results: dict):
    """実験結果をログに保存。"""
    EXPERIMENTS_DIR.mkdir(exist_ok=True)
    
    log_file = EXPERIMENTS_DIR / f"exp_{experiment_id}.json"
    log_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    
    print(f"[Synergeia] Experiment log saved: {log_file}")


def main():
    """
    Experiment 001: 並列実行テスト
    
    - Thread A: Antigravity が /noe+ を実行 (手動)
    - Thread B: このスクリプトが /sop+ を実行
    """
    
    # 実験クエリ
    sop_query = "CCL (Cognitive Control Language) distributed execution multi-agent architecture 2025 2026"
    
    # Thread B: /sop+ 実行
    sop_result = run_sop_thread(sop_query)
    
    # 実験結果
    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = {
        "id": experiment_id,
        "ccl": "/noe+ || /sop+",
        "description": "Synergeia Experiment 001: 並列CCL実行テスト",
        "threads": {
            "thread_a": {
                "ccl": "/noe+",
                "agent": "antigravity",
                "status": "manual",
                "note": "Antigravityが手動で実行"
            },
            "thread_b": sop_result
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # ログ保存
    save_experiment_log(experiment_id, experiment)
    
    # 結果出力
    print("\n" + "="*60)
    print("Synergeia Experiment 001 Results")
    print("="*60)
    print(f"CCL: {experiment['ccl']}")
    print(f"Thread B (/sop+) Status: {sop_result['status']}")
    if sop_result['status'] == 'success':
        print(f"\n--- Answer (truncated) ---")
        print(sop_result['answer'][:500] + "..." if len(sop_result['answer']) > 500 else sop_result['answer'])
    print("="*60)


if __name__ == "__main__":
    main()
