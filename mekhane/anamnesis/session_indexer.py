# PROOF: [L2/インフラ] <- mekhane/anamnesis/ Session Indexing Logic
"""
Session Indexing Logic
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class SessionIndexer:
    """Index sessions for fast retrieval."""

    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    data TEXT
                )
            """)

    def index_session(self, session_id: str, data: Dict[str, Any]):
        """Index a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (id, data) VALUES (?, ?)",
                (session_id, json.dumps(data))
            )

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
