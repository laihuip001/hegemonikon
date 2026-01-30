#!/usr/bin/env python3
"""
PROOF: このファイルは存在しなければならない

P3 → 記憶の永続化が必要
   → セッション内のログ記録が必要
   → logger.py が担う

Q.E.D.

---

SessionLogger for Hegemonikón
=============================
エージェントの会話ログを自律的かつリアルタイムに保存する。
Anti-Fragile設計: WAL (Write-Ahead Logging) パターン採用。

Usage:
    python logger.py log "role" "content" --session "ID"
    python logger.py dump --session "ID"
"""

import json
import os
import sys
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class SessionLogger:
    def __init__(self, session_id: Optional[str] = None, base_dir: str = "vault/logs/raw"):
        self.session_id = session_id or datetime.now().strftime("%Y-%m-%d_Session")
        
        # M:\Hegemonikon root resolution
        # Assuming script is in forge/gnosis/ or forge/scripts/
        # Need to find 'Hegemonikon' root or use env var
        # Fallback to current dir if not found
        self.root_dir = self._find_root()
        self.log_dir = self.root_dir / base_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_path = self.log_dir / f"{self.session_id}.jsonl"
        self.temp_path = self.log_dir / f"{self.session_id}.tmp"

    def _find_root(self) -> Path:
        # Try to find M:\Hegemonikon
        # Check current working directory parents
        cwd = Path.cwd()
        for parent in [cwd] + list(cwd.parents):
            if (parent / "Hegemonikon").exists(): # Subdir check
                return parent / "Hegemonikon"
            if parent.name == "Hegemonikon": # Inside root
                return parent
                
        # Fallback: specific absolute path M:\Hegemonikon
        abs_path = Path("M:/Hegemonikon")
        if abs_path.exists():
            return abs_path
            
        return cwd

    def append(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        メッセージを追記する (Write-Ahead Logging Pattern)
        1. 既存ログ + 新規エントリ -> Tempファイル
        2. Tempファイル -> 実ファイル (Atomic Rename)
        ※ JSONL追記なら単に open('a') で良いが、堅牢性重視ならアトミック性が欲しい。
        ただしWindowsでのrenameはatomicでない場合があるため、
        ここでは単純なAppend + Flushを採用し、ロック競合を避ける。
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno()) # Force write to disk
            return True
        except Exception as e:
            print(f"Error logging message: {e}")
            return False

    def read_logs(self) -> list:
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    
    if cmd == "log":
        # python logger.py log "user" "hello" --session "test"
        role = sys.argv[2]
        content = sys.argv[3]
        
        session_id = None
        if "--session" in sys.argv:
            idx = sys.argv.index("--session")
            session_id = sys.argv[idx+1]
            
        logger = SessionLogger(session_id)
        if logger.append(role, content):
            print(f"Logged to {logger.log_path}")
        else:
            sys.exit(1)
            
    elif cmd == "dump":
        session_id = None
        if "--session" in sys.argv:
            idx = sys.argv.index("--session")
            session_id = sys.argv[idx+1]
        
        logger = SessionLogger(session_id)
        logs = logger.read_logs()
        print(json.dumps(logs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
