#!/usr/bin/env python3
# PROOF: [L2/SessionIndex] <- mekhane/anamnesis/ A0→Session Indexing
"""
Session Indexer - mekhane.anamnesis

Indexes Jules sessions for fast retrieval and semantic search.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logger
logger = logging.getLogger(__name__)


# PURPOSE: Index Jules sessions
class SessionIndexer:
    """Indexes Jules sessions for fast retrieval and semantic search."""

    # PURPOSE: Initialize indexer
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize indexer."""
        self.db_path = db_path or Path.home() / ".mekhane" / "sessions.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # PURPOSE: Initialize database schema
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    prompt TEXT,
                    state TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                )
            """)
            conn.commit()

    # PURPOSE: Index a session
    def index_session(self, session: Dict[str, Any]):
        """Index a session."""
        import json

        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().isoformat()
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                (id, prompt, state, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.get("id"),
                session.get("prompt"),
                session.get("state"),
                session.get("created_at", now),
                now,
                json.dumps(session.get("metadata", {}))
            ))
            conn.commit()

        logger.info(f"Indexed session {session.get('id')}")

    # PURPOSE: Search sessions
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search sessions (simple text match for now)."""
        import json

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM sessions
                WHERE prompt LIKE ? OR id LIKE ?
            """, (f"%{query}%", f"%{query}%"))

            results = []
            for row in cursor:
                item = dict(row)
                if item["metadata"]:
                    item["metadata"] = json.loads(item["metadata"])
                results.append(item)

            return results
