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
# PURPOSE: [L2-auto] Synergeia の実行結果
class SynergeiaResult:
    # PURPOSE: n8n Synergeia webhook の実行結果を構造化して保持する
    """Synergeia の実行結果"""
    ccl: str
    status: str  # "success" | "error" | "manual" | "timeout"
    results: list = field(default_factory=list)
    plan: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    error: Optional[str] = None

    # PURPOSE: [L2-auto] __post_init__
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @property
    # PURPOSE: [L2-auto] is_success
    def is_success(self) -> bool:
        # PURPOSE: 結果が成功かどうかを判定する
        return self.status == "success"

    def to_dict(self) -> Dict[str, Any]:
        # PURPOSE: dataclass を辞書に変換して JSON シリアライズ可能にする
        return asdict(self)


# =============================================================================
# Core API
# =============================================================================

# PURPOSE: [L2-auto] Synergeia v2 — 2段階分散 CCL 実行。
def dispatch(
    # PURPOSE: n8n CCL ルーターでパース後、bridge.py 側でバックエンドを実行する 2段階アーキテクチャ
    ccl: str,
    context: str = "",
    timeout: int = DEFAULT_TIMEOUT,
    save: bool = True,
    execute: bool = True,
) -> SynergeiaResult:
    """
    Synergeia v2 — 2段階分散 CCL 実行。

    Stage 1: n8n WF-17 → CCL パース + ルーティング判定
    Stage 2: bridge.py → バックエンド呼出し (ochema/hermeneus/jules/perplexity)

    Args:
        ccl: CCL 式 (e.g. "/noe+ || /sop+")
        context: 実行コンテキスト
        timeout: タイムアウト (秒)
        save: True の場合は experiments/ に結果を保存
        execute: True の場合はバックエンドも実行 (False=ルーティングのみ)

    Returns:
        SynergeiaResult
    """
    payload = {
        "ccl": ccl,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # ── Stage 1: n8n CCL Router ──
        logger.info(f"[Synergeia] Stage 1 — Routing: {ccl}")
        resp = requests.post(
            SYNERGEIA_WEBHOOK,
            json=payload,
            timeout=min(timeout, 10),  # ルーティングは軽い
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

        # ルーティングのみの場合はここで終了
        if not execute or data.get("status") == "ok":
            return SynergeiaResult(
                ccl=ccl,
                status=data.get("status", "routed"),
                results=data.get("tasks", []),
                plan=data.get("plan", {}),
                timestamp=data.get("timestamp", datetime.now().isoformat()),
            )

        # ── Stage 2: バックエンド実行 ──
        logger.info(f"[Synergeia] Stage 2 — Executing threads")
        tasks = data.get("tasks", [])
        results = []

        for task in tasks:
            thread = task.get("thread", "hermeneus")
            task_ccl = task.get("ccl", ccl)
            try:
                result = _execute_thread(thread, task_ccl, context, timeout)
                results.append(result)
            except Exception as e:
                results.append({
                    "thread": thread,
                    "ccl": task_ccl,
                    "status": "error",
                    "error": str(e),
                })

        result = SynergeiaResult(
            ccl=ccl,
            status="success" if all(
                r.get("status") == "success" for r in results
            ) else "partial",
            results=results,
            plan=data.get("plan", {}),
            timestamp=datetime.now().isoformat(),
        )

    except requests.exceptions.ConnectionError:
        # n8n 不通時: ローカルフォールバック
        logger.warning("[Synergeia] n8n unreachable, using local fallback")
        result = _local_fallback(ccl, context, timeout)

    except requests.exceptions.Timeout:
        result = SynergeiaResult(
            ccl=ccl,
            status="timeout",
            error=f"Timed out after {timeout}s",
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


# =============================================================================
# Stage 2: Thread Execution
# =============================================================================

# PURPOSE: [L2-auto] スレッドに応じたバックエンドを呼び出す
def _execute_thread(
    # PURPOSE: CCL のスレッド種別に応じて対応するバックエンドを呼び出す
    thread: str,
    ccl: str,
    context: str,
    timeout: int,
) -> Dict[str, Any]:
    """スレッドに応じたバックエンドを呼び出す"""
    logger.info(f"[Synergeia] Executing {ccl} → {thread}")

    if thread == "ochema":
        return _exec_ochema(ccl, context, timeout)
    elif thread == "jules":
        return _exec_jules(ccl, context)
    elif thread == "perplexity":
        return _exec_perplexity(ccl, context)
    else:  # hermeneus (default)
        return _exec_hermeneus(ccl, context)


# PURPOSE: [L2-auto] Ochēma → Antigravity LS → LLM
def _exec_ochema(ccl: str, context: str, timeout: int) -> Dict[str, Any]:
    # PURPOSE: Ochēma MCP 経由で LLM を呼び出す
    """Ochēma → Antigravity LS → LLM"""
    try:
        from mekhane.ochema.antigravity_client import AntigravityClient
        client = AntigravityClient()
        msg = f"{context}\nCCL: {ccl}" if context else f"CCL: {ccl}"
        response = client.ask(msg, timeout=float(timeout))
        return {
            "thread": "ochema",
            "ccl": ccl,
            "status": "success",
            "answer": response.text[:3000],
            "model": response.model,
        }
    except Exception as e:
        return {"thread": "ochema", "ccl": ccl, "status": "error", "error": str(e)}


# PURPOSE: [L2-auto] Hermēneus → CCL dispatch
def _exec_hermeneus(ccl: str, context: str) -> Dict[str, Any]:
    # PURPOSE: Hermēneus CCL パーサーで構造解析する
    """Hermēneus → CCL dispatch"""
    try:
        from hermeneus.src.dispatch import dispatch as herm_dispatch
        result = herm_dispatch(ccl)
        return {
            "thread": "hermeneus",
            "ccl": ccl,
            "status": "success",
            "answer": json.dumps(result, ensure_ascii=False, default=str)[:3000],
        }
    except Exception as e:
        return {"thread": "hermeneus", "ccl": ccl, "status": "error", "error": str(e)}


# PURPOSE: [L2-auto] Jules → タスク作成 (非同期)
def _exec_jules(ccl: str, context: str) -> Dict[str, Any]:
    # PURPOSE: Jules MCP でコーディングタスクを作成する (非同期)
    """Jules → タスク作成 (非同期)"""
    return {
        "thread": "jules",
        "ccl": ccl,
        "status": "deferred",
        "answer": f"Jules タスク '{ccl}' — jules MCP create_task を使用してください",
        "note": "Jules は非同期実行。jules_create_task MCP ツールで直接投入推奨",
    }


# PURPOSE: [L2-auto] /sop → 調査依頼書生成
def _exec_perplexity(ccl: str, context: str) -> Dict[str, Any]:
    # PURPOSE: /sop 調査を HGK Gateway の SOP 生成経由で実行する
    """/sop → 調査依頼書生成"""
    try:
        # HGK Gateway の hgk_sop_generate を直接呼ぶ
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from mekhane.mcp.hgk_gateway import hgk_sop_generate
        result = hgk_sop_generate(context or ccl)
        return {
            "thread": "perplexity",
            "ccl": ccl,
            "status": "success",
            "answer": str(result)[:3000],
        }
    except Exception as e:
        return {"thread": "perplexity", "ccl": ccl, "status": "error", "error": str(e)}


# PURPOSE: [L2-auto] n8n 不通時のローカルフォールバック
def _local_fallback(ccl: str, context: str, timeout: int) -> SynergeiaResult:
    # PURPOSE: n8n 不通時にローカルで CCL をパースし実行するフォールバック
    """n8n 不通時のローカルフォールバック"""
    import re

    # 簡易 CCL パーサー (n8n の JS ロジックの Python 版)
    THREAD_MAP = {
        "/noe": "ochema", "/dia": "ochema", "/bou": "ochema",
        "/zet": "ochema", "/u": "ochema",
        "/sop": "perplexity",
        "/s": "jules", "/mek": "jules", "/ene": "jules", "/pra": "jules",
    }

    match = re.match(r"^/([a-z]+)", ccl)
    prefix = f"/{match.group(1)}" if match else ""
    thread = THREAD_MAP.get(prefix, "hermeneus")

    try:
        result_data = _execute_thread(thread, ccl, context, timeout)
        return SynergeiaResult(
            ccl=ccl,
            status=result_data.get("status", "error"),
            results=[result_data],
            plan={"type": "single", "elements": [ccl], "fallback": True},
        )
    except Exception as e:
        return SynergeiaResult(
            ccl=ccl,
            status="error",
            error=f"Local fallback failed: {e}",
        )


# PURPOSE: [L2-auto] CCL をコンパイルのみ (Hermēneus 経由、実行しない)
def dispatch_compile_only(ccl: str) -> SynergeiaResult:
    # PURPOSE: CCL をコンパイルのみ行い、実行せずに LMQL コードを取得する
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

# PURPOSE: [L2-auto] 結果を experiments/ に保存
def _save_result(result: SynergeiaResult) -> Optional[Path]:
    # PURPOSE: 実行結果を experiments/ ディレクトリに JSON として永続化する
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


# PURPOSE: [L2-auto] n8n Synergeia webhook の疎通確認
def health_check() -> Dict[str, Any]:
    # PURPOSE: n8n Synergeia webhook の疎通を確認して稼働状態を返す
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

# PURPOSE: [L2-auto] CLI エントリーポイント
def main():
    # PURPOSE: Synergeia v2 の CLI エントリーポイント
    """CLI エントリーポイント"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Synergeia v2 — n8n Distributed CCL Executor"
    )
    parser.add_argument("ccl", nargs="?", default=None, help="CCL expression (e.g. '/noe+ || /sop+')")
    parser.add_argument("--context", "-c", default="", help="Execution context")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--no-save", action="store_true", help="Don't save result")
    parser.add_argument("--compile-only", action="store_true", help="Compile only")
    parser.add_argument("--health", action="store_true", help="Health check")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.health:
        result = health_check()
        print(json.dumps(result, indent=2))
        return

    if not args.ccl:
        parser.error("CCL expression is required (unless --health is used)")

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
