#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- synergeia/ Jules Usage Dashboard
"""
Jules Usage Dashboard & PR Retrieval
====================================

6アカウントの使用量トラッキングと完了タスクのPR取得。

Usage:
    # 使用量確認
    python jules_dashboard.py status
    
    # 完了タスクのPR一覧
    python jules_dashboard.py prs
    
    # セッション詳細
    python jules_dashboard.py session <session_id>
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

# Add hegemonikon to path
HEGEMONIKON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HEGEMONIKON_ROOT))

try:
    from termcolor import colored, cprint
    TERMCOLOR_AVAILABLE = True
except ImportError:
    TERMCOLOR_AVAILABLE = False
    def colored(text, color=None, on_color=None, attrs=None):
        return text
    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)

try:
    from mekhane.symploke.jules_client import JulesClient, JulesSession, SessionState
    JULES_CLIENT_AVAILABLE = True
except ImportError:
    JULES_CLIENT_AVAILABLE = False
    print("[Warning] jules_client not available")


# ============ Constants ============
USAGE_FILE = Path(__file__).parent / "jules_usage.json"
DAILY_LIMIT = 300  # Ultra tier
ACCOUNTS_COUNT = 6


# ============ Account Mapping ============
# 18 API Keys are distributed across 6 accounts (3 keys each)
ACCOUNT_KEY_MAPPING = {
    "account_01": ["JULES_API_KEY_01", "JULES_API_KEY_02", "JULES_API_KEY_03"],
    "account_02": ["JULES_API_KEY_04", "JULES_API_KEY_05", "JULES_API_KEY_06"],
    "account_03": ["JULES_API_KEY_07", "JULES_API_KEY_08", "JULES_API_KEY_09"],
    "account_04": ["JULES_API_KEY_10", "JULES_API_KEY_11", "JULES_API_KEY_12"],
    "account_05": ["JULES_API_KEY_13", "JULES_API_KEY_14", "JULES_API_KEY_15"],
    "account_06": ["JULES_API_KEY_16", "JULES_API_KEY_17", "JULES_API_KEY_18"],
}


@dataclass
class AccountUsage:
    """アカウント使用状況"""
    account_id: str
    used_today: int
    remaining: int
    last_reset: str
    sessions: List[str]


@dataclass
class PRInfo:
    """PR情報"""
    session_id: str
    pr_url: str
    prompt: str
    state: str
    created_at: str


class JulesDashboard:
    """
    Jules 使用量ダッシュボード。
    """
    
    def __init__(self):
        self.usage_data = self._load_usage()
    
    def _load_usage(self) -> dict:
        """使用データを読み込み"""
        if USAGE_FILE.exists():
            data = json.loads(USAGE_FILE.read_text())
            # 日付リセット確認
            today = datetime.now().strftime("%Y-%m-%d")
            if data.get("date") != today:
                # 新しい日 → リセット
                return self._create_empty_usage()
            return data
        return self._create_empty_usage()
    
    def _create_empty_usage(self) -> dict:
        """空の使用データを作成"""
        today = datetime.now().strftime("%Y-%m-%d")
        return {
            "date": today,
            "accounts": {
                f"account_{i:02d}": {
                    "used": 0,
                    "sessions": [],
                }
                for i in range(1, ACCOUNTS_COUNT + 1)
            },
            "total_used": 0,
            "prs": [],
        }
    
    def _save_usage(self):
        """使用データを保存"""
        USAGE_FILE.write_text(json.dumps(self.usage_data, indent=2, ensure_ascii=False))
    
    def get_account_for_key(self, key_index: int) -> str:
        """API Key インデックスからアカウントIDを取得"""
        # 1-18 → account_01-06
        account_num = ((key_index - 1) // 3) + 1
        return f"account_{account_num:02d}"
    
    def record_usage(self, key_index: int, session_id: str):
        """使用を記録"""
        account_id = self.get_account_for_key(key_index)
        self.usage_data["accounts"][account_id]["used"] += 1
        self.usage_data["accounts"][account_id]["sessions"].append(session_id)
        self.usage_data["total_used"] += 1
        self._save_usage()
    
    def record_pr(self, session_id: str, pr_url: str, prompt: str, state: str):
        """PR情報を記録"""
        self.usage_data["prs"].append({
            "session_id": session_id,
            "pr_url": pr_url,
            "prompt": prompt[:100],
            "state": state,
            "created_at": datetime.now().isoformat(),
        })
        self._save_usage()
    
    def get_status(self) -> Dict[str, Any]:
        """使用状況を取得"""
        accounts = []
        for i in range(1, ACCOUNTS_COUNT + 1):
            account_id = f"account_{i:02d}"
            used = self.usage_data["accounts"][account_id]["used"]
            accounts.append({
                "account_id": account_id,
                "used": used,
                "remaining": DAILY_LIMIT - used,
                "sessions_count": len(self.usage_data["accounts"][account_id]["sessions"]),
            })
        
        return {
            "date": self.usage_data["date"],
            "accounts": accounts,
            "total_used": self.usage_data["total_used"],
            "total_remaining": (DAILY_LIMIT * ACCOUNTS_COUNT) - self.usage_data["total_used"],
            "prs_count": len(self.usage_data.get("prs", [])),
        }
    
    def get_prs(self) -> List[Dict]:
        """PR一覧を取得"""
        return self.usage_data.get("prs", [])
    
    def get_best_account(self) -> tuple[str, int]:
        """
        最も残り回数が多いアカウントを取得。
        Returns: (account_id, key_index)
        """
        best_account = None
        min_used = float("inf")
        
        for i in range(1, ACCOUNTS_COUNT + 1):
            account_id = f"account_{i:02d}"
            used = self.usage_data["accounts"][account_id]["used"]
            if used < min_used:
                min_used = used
                best_account = account_id
        
        if best_account:
            # アカウント番号から最初のキーインデックスを計算
            account_num = int(best_account.split("_")[1])
            first_key_index = (account_num - 1) * 3 + 1
            return best_account, first_key_index
        
        return "account_01", 1


async def fetch_session_pr(session_id: str, api_key: str) -> Optional[PRInfo]:
    """セッションからPR情報を取得"""
    if not JULES_CLIENT_AVAILABLE:
        return None
    
    try:
        async with JulesClient(api_key) as client:
            session = await client.get_session(session_id)
            if session.pull_request_url:
                return PRInfo(
                    session_id=session.id,
                    pr_url=session.pull_request_url,
                    prompt=session.prompt,
                    state=session.state.value,
                    created_at=datetime.now().isoformat(),
                )
    except Exception as e:
        print(f"Error fetching session {session_id}: {e}")
    
    return None


def print_status(dashboard: JulesDashboard):
    """使用状況を表示"""
    status = dashboard.get_status()
    
    cprint(f"\n{'='*60}", "cyan")
    cprint(f"Jules Usage Dashboard - {status['date']}", "cyan", attrs=["bold"])
    cprint(f"{'='*60}\n", "cyan")
    
    header = f"{'Account':<12} {'Used':<8} {'Remaining':<10} {'Sessions':<10}"
    cprint(header, attrs=["bold"])
    print("-" * 40)
    
    for acc in status["accounts"]:
        remaining = acc["remaining"]
        bar_len = int(remaining / DAILY_LIMIT * 20)
        if bar_len < 0: bar_len = 0
        if bar_len > 20: bar_len = 20

        # Determine color based on remaining usage
        ratio = remaining / DAILY_LIMIT
        if ratio > 0.5:
            color = "green"
        elif ratio > 0.2:
            color = "yellow"
        else:
            color = "red"

        bar_filled = colored("█" * bar_len, color)
        bar_empty = colored("░" * (20 - bar_len), "grey")

        rem_str = colored(f"{remaining:<10}", color, attrs=["bold"])

        print(f"{acc['account_id']:<12} {acc['used']:<8} {rem_str} {acc['sessions_count']:<10}")
        print(f"  [{bar_filled}{bar_empty}] {remaining}/{DAILY_LIMIT}")
    
    print("-" * 40)

    total_remaining = status['total_remaining']
    total_ratio = total_remaining / (DAILY_LIMIT * ACCOUNTS_COUNT)
    if total_ratio > 0.5:
        total_color = "green"
    elif total_ratio > 0.2:
        total_color = "yellow"
    else:
        total_color = "red"

    cprint(f"{'TOTAL':<12} {status['total_used']:<8} {colored(str(total_remaining), total_color, attrs=['bold'])}")
    print(f"\nPRs created today: {status['prs_count']}")
    cprint(f"{'='*60}\n", "cyan")


def print_prs(dashboard: JulesDashboard):
    """PR一覧を表示"""
    prs = dashboard.get_prs()
    
    cprint(f"\n{'='*60}", "cyan")
    cprint("Jules PRs", "cyan", attrs=["bold"])
    cprint(f"{'='*60}\n", "cyan")
    
    if not prs:
        print("No PRs recorded today.")
        return
    
    for i, pr in enumerate(prs, 1):
        print(f"[{i}] {pr['state']}")
        print(f"    Session: {pr['session_id']}")
        print(f"    PR: {pr['pr_url']}")
        print(f"    Task: {pr['prompt'][:60]}...")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    dashboard = JulesDashboard()
    command = sys.argv[1]
    
    if command == "status":
        print_status(dashboard)
    
    elif command == "prs":
        print_prs(dashboard)
    
    elif command == "best":
        account, key_index = dashboard.get_best_account()
        print(f"Best account: {account} (key index: {key_index})")
    
    elif command == "session":
        if len(sys.argv) < 3:
            print("Usage: jules_dashboard.py session <session_id>")
            return
        session_id = sys.argv[2]
        # 最初のキーを使用
        api_key = os.environ.get("JULES_API_KEY_01")
        if api_key:
            pr_info = asyncio.run(fetch_session_pr(session_id, api_key))
            if pr_info:
                print(json.dumps(asdict(pr_info), indent=2, ensure_ascii=False))
            else:
                print("No PR found or session not found")
        else:
            print("No API key available")
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
