#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ O4→結果統合が必要→jules_results_loader が担う
"""
Jules 結果読み込みモジュール

/boot ワークフローで使用。
docs/specialist_run_*.json から発見事項を抽出し、優先度付きで表示。

Usage:
    from jules_results_loader import load_latest_results, summarize_findings
    
    results = load_latest_results()
    summary = summarize_findings(results)
    print(summary)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


# ============ Constants ============
RESULTS_DIR = Path(__file__).parent.parent.parent / "docs"
RESULTS_PATTERN = "specialist_run_*.json"


@dataclass
class Finding:
    """発見事項"""
    specialist_id: str
    specialist_name: str
    severity: str  # critical, high, medium, low, none
    description: str
    file_path: Optional[str] = None


@dataclass
class JulesRunResults:
    """Julesバッチ実行結果"""
    timestamp: str
    target_file: str
    category: str
    total_specialists: int
    started: int
    failed: int
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)


def load_latest_results() -> Optional[JulesRunResults]:
    """最新のJules実行結果を読み込み"""
    result_files = sorted(RESULTS_DIR.glob(RESULTS_PATTERN), reverse=True)
    
    if not result_files:
        return None
    
    latest_file = result_files[0]
    
    try:
        data = json.loads(latest_file.read_text())
        
        results = data.get("results", [])
        started = sum(1 for r in results if "session_id" in r)
        failed = sum(1 for r in results if "error" in r)
        
        return JulesRunResults(
            timestamp=data.get("timestamp", "unknown"),
            target_file=data.get("target_file", "unknown"),
            category=data.get("category", "all"),
            total_specialists=data.get("total_specialists", len(results)),
            started=started,
            failed=failed,
            sessions=results,
        )
    except Exception as e:
        print(f"Error loading {latest_file}: {e}")
        return None


def load_all_recent_results(days: int = 7) -> List[JulesRunResults]:
    """最近N日分の結果を読み込み"""
    result_files = sorted(RESULTS_DIR.glob(RESULTS_PATTERN), reverse=True)
    results = []
    
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for file_path in result_files:
        try:
            # ファイル名から日付抽出を試みる
            mtime = file_path.stat().st_mtime
            if mtime < cutoff:
                break
            
            data = json.loads(file_path.read_text())
            session_results = data.get("results", [])
            started = sum(1 for r in session_results if "session_id" in r)
            failed = sum(1 for r in session_results if "error" in r)
            
            results.append(JulesRunResults(
                timestamp=data.get("timestamp", "unknown"),
                target_file=data.get("target_file", "unknown"),
                category=data.get("category", "all"),
                total_specialists=data.get("total_specialists", len(session_results)),
                started=started,
                failed=failed,
                sessions=session_results,
            ))
        except Exception:
            continue
    
    return results


def summarize_findings(results: Optional[JulesRunResults]) -> str:
    """発見事項のサマリーを生成"""
    if not results:
        return "📭 Jules 実行結果なし"
    
    lines = [
        f"## 🔍 Jules 専門家レビュー結果",
        f"",
        f"| 項目 | 値 |",
        f"|:-----|:---|",
        f"| 日時 | {results.timestamp} |",
        f"| 対象 | `{results.target_file}` |",
        f"| カテゴリ | {results.category} |",
        f"| 専門家数 | {results.total_specialists} |",
        f"| 開始済み | {results.started} |",
        f"| 失敗 | {results.failed} |",
        f"",
    ]
    
    # セッション状態の集計
    if results.sessions:
        states = {}
        for session in results.sessions:
            state = session.get("status", "unknown")
            states[state] = states.get(state, 0) + 1
        
        lines.append("### セッション状態")
        lines.append("")
        for state, count in sorted(states.items()):
            lines.append(f"- {state}: {count}")
        lines.append("")
    
    return "\n".join(lines)


def get_session_urls(results: Optional[JulesRunResults]) -> List[str]:
    """セッションURLのリストを取得"""
    if not results:
        return []
    
    urls = []
    for session in results.sessions:
        url = session.get("url")
        if url:
            urls.append(url)
    return urls


def print_summary():
    """サマリーを標準出力に表示（CLI用）"""
    results = load_latest_results()
    print(summarize_findings(results))
    
    if results and results.sessions:
        print("\n### 直近のセッション（最大10件）")
        for session in results.sessions[:10]:
            sid = session.get("session_id", "N/A")[:8] if session.get("session_id") else "N/A"
            name = session.get("name", "unknown")[:30]
            status = session.get("status", "unknown")
            print(f"- {sid}... | {name} | {status}")


if __name__ == "__main__":
    print_summary()
