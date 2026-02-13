#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- synergeia/ Synergeia v2 Bridge — n8n WF Coordinator への薄いラッパー
"""
Synergeia v2 Bridge
====================

n8n の WF-17 (Synergeia Coordinator) に CCL 式を送信し、
分散実行結果を取得する薄い Python wrapper。

Architecture:
    bridge.py → HTTP POST → n8n webhook → (Jules MCP / Ochēma / Perplexity / Hermēneus)

Usage:
    # Python
    from synergeia.bridge import dispatch
    result = dispatch("/noe+ || /sop+", context="my analysis")

    # CLI
    python -m synergeia.bridge "/noe+ || /sop+"
    python -m synergeia.bridge "/noe+ |> /dia+" --context "review this"
"""

import json
import sys
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict

import requests

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
SYNERGEIA_WEBHOOK = f"{N8N_BASE_URL}/webhook/synergeia"
EXPERIMENTS_DIR = Path(__file__).parent / "experiments"
DEFAULT_TIMEOUT = 120  # seconds


@dataclass
class SynergeiaResult:
    """Synergeia の実行結果"""
    ccl: str
    status: str  # "success" | "error" | "manual" | "timeout"
    results: list = field(default_factory=list)
    plan: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    error: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# Core API
# =============================================================================

def dispatch(
    ccl: str,
    context: str = "",
    timeout: int = DEFAULT_TIMEOUT,
    save: bool = True,
) -> SynergeiaResult:
    """
    n8n Synergeia webhook に CCL 式を送信し、分散実行結果を取得。

    Args:
        ccl: CCL 式 (e.g. "/noe+ || /sop+")
        context: 実行コンテキスト
        timeout: タイムアウト (秒)
        save: True の場合は experiments/ に結果を保存

    Returns:
        SynergeiaResult
    """
    payload = {
        "ccl": ccl,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        logger.info(f"[Synergeia] Dispatching: {ccl}")
        resp = requests.post(
            SYNERGEIA_WEBHOOK,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

        result = SynergeiaResult(
            ccl=ccl,
            status=data.get("status", "success"),
            results=data.get("results", []),
            plan=data.get("plan", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )

    except requests.exceptions.Timeout:
        result = SynergeiaResult(
            ccl=ccl,
            status="timeout",
            error=f"Timed out after {timeout}s",
        )
    except requests.exceptions.ConnectionError:
        result = SynergeiaResult(
            ccl=ccl,
            status="error",
            error=f"Cannot connect to n8n at {SYNERGEIA_WEBHOOK}. Is n8n running?",
        )
    except Exception as e:
        result = SynergeiaResult(
            ccl=ccl,
            status="error",
            error=str(e),
        )

    if save:
        _save_result(result)

    return result


def dispatch_compile_only(ccl: str) -> SynergeiaResult:
    """CCL をコンパイルのみ (Hermēneus 経由、実行しない)"""
    payload = {
        "ccl": ccl,
        "mode": "compile_only",
        "timestamp": datetime.now().isoformat(),
    }

    try:
        resp = requests.post(
            SYNERGEIA_WEBHOOK,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

        return SynergeiaResult(
            ccl=ccl,
            status="compiled",
            results=[data],
        )
    except Exception as e:
        return SynergeiaResult(
            ccl=ccl,
            status="error",
            error=str(e),
        )


# =============================================================================
# Utilities
# =============================================================================

def _save_result(result: SynergeiaResult) -> Optional[Path]:
    """結果を experiments/ に保存"""
    try:
        EXPERIMENTS_DIR.mkdir(exist_ok=True)
        exp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = EXPERIMENTS_DIR / f"v2_{exp_id}.json"
        log_file.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        )
        logger.info(f"[Synergeia] Result saved: {log_file}")
        return log_file
    except Exception as e:
        logger.warning(f"[Synergeia] Failed to save result: {e}")
        return None


def health_check() -> Dict[str, Any]:
    """n8n Synergeia webhook の疎通確認"""
    try:
        resp = requests.post(
            SYNERGEIA_WEBHOOK,
            json={"ccl": "/health", "mode": "ping"},
            timeout=5,
        )
        return {
            "status": "ok" if resp.ok else "error",
            "code": resp.status_code,
            "url": SYNERGEIA_WEBHOOK,
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "unreachable",
            "url": SYNERGEIA_WEBHOOK,
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI エントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Synergeia v2 — n8n Distributed CCL Executor"
    )
    parser.add_argument("ccl", help="CCL expression (e.g. '/noe+ || /sop+')")
    parser.add_argument("--context", "-c", default="", help="Execution context")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--no-save", action="store_true", help="Don't save result")
    parser.add_argument("--compile-only", action="store_true", help="Compile only")
    parser.add_argument("--health", action="store_true", help="Health check")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.health:
        result = health_check()
        print(json.dumps(result, indent=2))
        return

    if args.compile_only:
        result = dispatch_compile_only(args.ccl)
    else:
        result = dispatch(
            args.ccl,
            context=args.context,
            timeout=args.timeout,
            save=not args.no_save,
        )

    # Output
    print(f"\n{'='*60}")
    print(f"[Synergeia v2] CCL: {result.ccl}")
    print(f"[Synergeia v2] Status: {result.status}")
    print(f"{'='*60}")

    if result.error:
        print(f"  Error: {result.error}")
    elif result.results:
        for i, r in enumerate(result.results, 1):
            thread = r.get("thread", "unknown") if isinstance(r, dict) else "unknown"
            status = r.get("status", "unknown") if isinstance(r, dict) else "unknown"
            print(f"  [{i}] {status} -> {thread}")
            if isinstance(r, dict) and "answer" in r:
                print(f"      {r['answer'][:200]}...")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
