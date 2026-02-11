#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- synergeia/ Jules API Client
"""
Jules API Client for Synergeia
==============================

Jules を使用して非同期コード生成タスクを実行。
6アカウント、最大3同時使用、ラウンドロビン。

Usage:
    # CLI モード
    python jules_api.py new "テスト追加"
    python jules_api.py status <session_id>
    python jules_api.py list
    
    # API モード (import)
    from jules_api import JulesPool
    pool = JulesPool()
    result = pool.create_session("テスト追加", repo="user/repo")
"""

import os
import sys
import json
import yaml
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from threading import Lock
import shutil

CONFIG_FILE = Path(__file__).parent / "jules_accounts.yaml"
POOL_STATE_FILE = Path(__file__).parent / "jules_pool_state.json"
POOL_DB_FILE = Path(__file__).parent / "jules_pool_state.db"
JULES_CLI = "jules"


@dataclass
class JulesAccount:
    """Jules アカウント"""
    id: str
    email: str
    status: str  # active, inactive, busy, cooldown
    config_dir: Path
    current_session: Optional[str] = None
    last_used: Optional[datetime] = None
    sessions_count: int = 0


@dataclass
class JulesSession:
    """Jules セッション"""
    session_id: str
    account_id: str
    task: str
    repo: Optional[str]
    status: str  # pending, running, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None


class JulesPool:
    """
    Jules アカウントプール管理。
    6アカウント、最大3同時、ラウンドロビン。
    """
    
    def __init__(self, config_path: Path = CONFIG_FILE):
        self.config_path = config_path
        self.config = self._load_config()
        self.accounts: List[JulesAccount] = []
        self.sessions: Dict[str, JulesSession] = {}
        self.lock = Lock()
        self.conn = None
        self._init_accounts()
        self._init_db()
        self._load_state()
    
    def _init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(POOL_DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                status TEXT,
                sessions_count INTEGER DEFAULT 0,
                last_used TEXT
            )
        """)
        self.conn.commit()

    def _load_config(self) -> dict:
        """設定ファイル読み込み"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        return yaml.safe_load(self.config_path.read_text())
    
    def _init_accounts(self):
        """アカウント初期化"""
        for acc in self.config.get("accounts", []):
            config_dir = Path(acc["config_dir"]).expanduser()
            config_dir.mkdir(parents=True, exist_ok=True)
            
            self.accounts.append(JulesAccount(
                id=acc["id"],
                email=acc.get("email", ""),
                status=acc.get("status", "inactive"),
                config_dir=config_dir,
            ))
    
    def _migrate_from_json(self):
        """JSONからDBへ移行"""
        if not POOL_STATE_FILE.exists():
            return

        # Check if table is empty
        cursor = self.conn.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] > 0:
            return  # Already migrated or populated

        try:
            state = json.loads(POOL_STATE_FILE.read_text())
            accounts = state.get("accounts", {})
            for acc_id, acc_data in accounts.items():
                self.conn.execute("""
                    INSERT OR REPLACE INTO accounts (id, status, sessions_count, last_used)
                    VALUES (?, ?, ?, ?)
                """, (
                    acc_id,
                    acc_data.get("status", "inactive"),
                    acc_data.get("sessions_count", 0),
                    acc_data.get("last_used")
                ))
            self.conn.commit()
            print(f"[JulesPool] Migrated {len(accounts)} accounts from JSON to DB.")

            # Backup JSON file
            backup_path = POOL_STATE_FILE.with_suffix(".json.bak")
            shutil.move(POOL_STATE_FILE, backup_path)
            print(f"[JulesPool] Backed up JSON state to {backup_path.name}")

        except Exception as e:
            print(f"[JulesPool] Migration failed: {e}")

    def _load_state(self):
        """プール状態を読み込み"""
        # Try migration first
        self._migrate_from_json()

        cursor = self.conn.execute("SELECT * FROM accounts")
        rows = {row["id"]: row for row in cursor.fetchall()}

        for acc in self.accounts:
            if acc.id in rows:
                row = rows[acc.id]
                acc.status = row["status"]
                acc.sessions_count = row["sessions_count"]
                if row["last_used"]:
                    acc.last_used = datetime.fromisoformat(row["last_used"])
    
    def _update_account_state(self, account: JulesAccount):
        """
        特定アカウントの状態をDBに保存。
        JSON保存と異なり、該当レコードのみ更新する。
        """
        self.conn.execute("""
            INSERT OR REPLACE INTO accounts (id, status, sessions_count, last_used)
            VALUES (?, ?, ?, ?)
        """, (
            account.id,
            account.status,
            account.sessions_count,
            account.last_used.isoformat() if account.last_used else None
        ))
        self.conn.commit()
    
    def get_available_account(self) -> Optional[JulesAccount]:
        """
        利用可能なアカウントを取得（ラウンドロビン）。
        最大同時使用数を考慮。
        """
        with self.lock:
            max_concurrent = self.config.get("max_concurrent", 3)
            cooldown_minutes = self.config.get("rotation", {}).get("cooldown_minutes", 5)
            
            # 現在ビジーなアカウント数
            busy_count = sum(1 for acc in self.accounts if acc.status == "busy")
            if busy_count >= max_concurrent:
                return None
            
            # クールダウンチェック
            now = datetime.now()
            for acc in self.accounts:
                if acc.status == "cooldown" and acc.last_used:
                    if now - acc.last_used > timedelta(minutes=cooldown_minutes):
                        acc.status = "active"
            
            # ラウンドロビン: 最も古く使われたアクティブアカウント
            available = [acc for acc in self.accounts if acc.status == "active"]
            if not available:
                # inactive から1つをアクティブ化（初回）
                inactive = [acc for acc in self.accounts if acc.status == "inactive"]
                if inactive:
                    return inactive[0]
                return None
            
            # 最も古く使われたものを選択
            available.sort(key=lambda a: a.last_used or datetime.min)
            return available[0]
    
    def _run_jules_cli(self, account: JulesAccount, args: List[str]) -> Dict[str, Any]:
        """
        特定のアカウントでJules CLIを実行。
        """
        env = os.environ.copy()
        env["JULES_CONFIG_DIR"] = str(account.config_dir)
        
        try:
            result = subprocess.run(
                [JULES_CLI] + args,
                capture_output=True,
                text=True,
                env=env,
                timeout=600,  # 10分
            )
            
            if result.returncode != 0:
                return {"error": result.stderr, "returncode": result.returncode}
            
            return {"output": result.stdout, "returncode": 0}
            
        except subprocess.TimeoutExpired:
            return {"error": "Timeout (600s)", "returncode": -1}
        except Exception as e:
            return {"error": str(e), "returncode": -1}
    
    def login_account(self, account_id: str) -> Dict[str, Any]:
        """
        指定アカウントでログイン。
        ブラウザが開くので対話的に実行。
        """
        account = next((acc for acc in self.accounts if acc.id == account_id), None)
        if not account:
            return {"error": f"Account not found: {account_id}"}
        
        print(f"[JulesPool] ログイン: {account_id}")
        print(f"[JulesPool] Config dir: {account.config_dir}")
        print("[JulesPool] ブラウザでログインしてください...")
        
        # 対話的にログイン
        env = os.environ.copy()
        env["JULES_CONFIG_DIR"] = str(account.config_dir)
        
        result = subprocess.run(
            [JULES_CLI, "login"],
            env=env,
        )
        
        if result.returncode == 0:
            account.status = "active"
            self._update_account_state(account)
            return {"status": "success", "account_id": account_id}
        
        return {"error": "Login failed", "returncode": result.returncode}
    
    def create_session(
        self,
        task: str,
        repo: Optional[str] = None,
        parallel: int = 1,
    ) -> Dict[str, Any]:
        """
        新しいセッションを作成。
        `jules remote new --session` で非対話的に実行。
        """
        account = self.get_available_account()
        if not account:
            return {"error": "No available account (all busy or at max concurrent)"}
        
        with self.lock:
            account.status = "busy"
            account.last_used = datetime.now()
            account.sessions_count += 1
            self._update_account_state(account)
        
        try:
            # `jules remote new` は非対話的（APIベース）
            args = ["remote", "new", "--session", task]
            if repo:
                args.extend(["--repo", repo])
            if parallel > 1:
                args.extend(["--parallel", str(parallel)])
            
            result = self._run_jules_cli(account, args)
            
            if "error" in result:
                account.status = "active"
                self._update_account_state(account)
                return result
            
            # セッションIDを出力から抽出
            output = result.get("output", "")
            session_id = self._extract_session_id(output, account.id)
            
            session = JulesSession(
                session_id=session_id,
                account_id=account.id,
                task=task,
                repo=repo,
                status="running",
                created_at=datetime.now(),
            )
            self.sessions[session_id] = session
            
            # クールダウンに移行
            account.status = "cooldown"
            self._update_account_state(account)
            
            return {
                "status": "success",
                "session_id": session_id,
                "account_id": account.id,
                "output": output,
            }
            
        except Exception as e:
            account.status = "active"
            self._update_account_state(account)
            return {"error": str(e)}
    
    @staticmethod
    def _extract_session_id(output: str, account_id: str) -> str:
        """出力からセッションIDを抽出。見つからなければタイムスタンプで生成。"""
        import re
        # 典型的な出力: "Session created: 1234567" or URL with session ID
        match = re.search(r'(?:session[:\s]+|/sessions?/)(\d+)', output, re.IGNORECASE)
        if match:
            return match.group(1)
        return f"{account_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def list_sessions(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        セッション一覧を取得。
        """
        if account_id:
            accounts = [acc for acc in self.accounts if acc.id == account_id]
        else:
            accounts = [acc for acc in self.accounts if acc.status in ("active", "busy", "cooldown")]
        
        all_sessions = []
        for account in accounts:
            result = self._run_jules_cli(account, ["remote", "list", "--session"])
            if "output" in result:
                all_sessions.append({
                    "account_id": account.id,
                    "sessions": result["output"],
                })
        
        return {"sessions": all_sessions}
    
    def get_status(self) -> Dict[str, Any]:
        """
        プール状態を取得。
        """
        return {
            "accounts": [
                {
                    "id": acc.id,
                    "email": acc.email,
                    "status": acc.status,
                    "sessions_count": acc.sessions_count,
                    "last_used": acc.last_used.isoformat() if acc.last_used else None,
                }
                for acc in self.accounts
            ],
            "max_concurrent": self.config.get("max_concurrent", 3),
            "active_count": sum(1 for acc in self.accounts if acc.status == "busy"),
        }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    pool = JulesPool()
    command = sys.argv[1]
    
    if command == "status":
        result = pool.get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "login":
        if len(sys.argv) < 3:
            print("Usage: jules_api.py login <account_id>")
            return
        result = pool.login_account(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "new":
        if len(sys.argv) < 3:
            print("Usage: jules_api.py new <task> [--repo <repo>]")
            return
        task = sys.argv[2]
        repo = None
        if "--repo" in sys.argv:
            idx = sys.argv.index("--repo")
            if idx + 1 < len(sys.argv):
                repo = sys.argv[idx + 1]
        result = pool.create_session(task, repo)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "list":
        result = pool.list_sessions()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
