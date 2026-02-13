# PROOF: [L2/Anamnesis] <- mekhane/anamnesis/session_indexer.py Session Indexer
"""
Session Indexer

Session ログ (.jsonl) を解析し、検索用インデックスを構築する。
"""
# PURPOSE: mekhane/anamnesis/session_indexer.py
import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# PURPOSE: Session Indexer Class
class SessionIndexer:
    """Indexer for session logs."""

    def __init__(self, db_path: str = "session.db"):
        self.db_path = db_path
        self._init_db()

    # PURPOSE: Initialize DB
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Sessions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                model TEXT,
                summary TEXT
            )
        ''')

        # Messages table (Full Text Search)
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')

        # FTS table
        c.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                content,
                session_id UNINDEXED
            )
        ''')

        conn.commit()
        conn.close()

    # PURPOSE: Index a session file
    def index_file(self, file_path: Path):
        """Index a .jsonl session file."""
        logger.info(f"Indexing {file_path}")

        session_id = file_path.stem
        messages = []
        metadata = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if "role" in entry and "content" in entry:
                        messages.append(entry)
                    elif "metadata" in entry:
                        metadata = entry["metadata"]
                except json.JSONDecodeError:
                    continue

        self._save_session(session_id, messages, metadata)

    # PURPOSE: Save session to DB
    def _save_session(self, session_id: str, messages: List[Dict], metadata: Dict):
        """Save session data to database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Upsert session
        c.execute('''
            INSERT OR REPLACE INTO sessions (id, start_time, end_time, model, summary)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            metadata.get("start_time"),
            metadata.get("end_time"),
            metadata.get("model"),
            metadata.get("summary")
        ))

        # Insert messages
        for msg in messages:
            c.execute('''
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                session_id,
                msg.get("role"),
                msg.get("content"),
                msg.get("timestamp")
            ))

            # Index for FTS
            c.execute('''
                INSERT INTO messages_fts (content, session_id)
                VALUES (?, ?)
            ''', (msg.get("content"), session_id))

        conn.commit()
        conn.close()

    # PURPOSE: Search
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search messages."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute('''
            SELECT m.session_id, m.role, m.content, snippet(messages_fts, 0, '<b>', '</b>', '...', 64) as snippet
            FROM messages_fts f
            JOIN messages m ON f.rowid = m.id
            WHERE messages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))

        results = [dict(row) for row in c.fetchall()]
        conn.close()

        return results
