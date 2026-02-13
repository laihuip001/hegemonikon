# PROOF: [L2/Anamnesis] <- mekhane/anamnesis/ A0→記憶の索引化→セッションインデクサ
# PURPOSE: Session Indexer — チャットログのベクトル化と検索
"""Session Indexer — Indexing and retrieval of chat logs.

Uses SentenceTransformers for embedding and LanceDB for vector storage.
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

import lancedb
import pandas as pd
from sentence_transformers import SentenceTransformer

# Index storage path
MNEME_DIR = os.path.expanduser("~/oikos/mneme")
DB_PATH = os.path.join(MNEME_DIR, "lancedb")
TABLE_NAME = "chat_logs"

# Embedding model
MODEL_NAME = "all-MiniLM-L6-v2"


class SessionIndexer:
    """Session Indexer."""

    def __init__(self, db_path: str = DB_PATH):
        """Initialize indexer."""
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        self.model = SentenceTransformer(MODEL_NAME)
        self._init_table()

    def _init_table(self):
        """Initialize LanceDB table."""
        # Check if table exists
        if TABLE_NAME not in self.db.table_names():
            # Create dummy data to infer schema
            # schema: vector(384), text, role, timestamp, session_id
            data = [{
                "vector": self.model.encode("hello world").tolist(),
                "text": "hello world",
                "role": "user",
                "timestamp": datetime.now().isoformat(),
                "session_id": "init_session"
            }]
            self.db.create_table(TABLE_NAME, data)
            # Clear dummy data
            self.db.open_table(TABLE_NAME).delete("session_id = 'init_session'")

    def index_session(self, session_id: str, logs: List[dict]):
        """Index a chat session."""
        table = self.db.open_table(TABLE_NAME)

        # Prepare data
        data = []
        for log in logs:
            text = log.get("content", "")
            if not text:
                continue

            vector = self.model.encode(text).tolist()
            data.append({
                "vector": vector,
                "text": text,
                "role": log.get("role", "unknown"),
                "timestamp": log.get("timestamp", datetime.now().isoformat()),
                "session_id": session_id
            })

        if data:
            table.add(data)

    def search(self, query: str, limit: int = 5) -> List[dict]:
        """Search chat logs."""
        table = self.db.open_table(TABLE_NAME)
        vector = self.model.encode(query).tolist()

        results = table.search(vector).limit(limit).to_pandas()
        return results.to_dict(orient="records")

    def get_stats(self) -> dict:
        """Get index statistics."""
        table = self.db.open_table(TABLE_NAME)
        return {
            "count": len(table),
            "columns": table.schema.names
        }
