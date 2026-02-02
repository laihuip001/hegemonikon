#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→会話履歴管理が必要→chronos_ingest が担う
"""
Chronos Ingest - Conversation History を LanceDB にインデックス

Usage:
    python chronos_ingest.py                    # 全セッションを投入
"""

import re
import sys
from pathlib import Path
from typing import List, Optional

try:
    import lancedb
    from pydantic import BaseModel
except ImportError:
    lancedb = None
    BaseModel = object
    print("[Chronos] Warning: lancedb or pydantic not found. Indexing disabled.")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Settings (aligned with mneme environment)
# Use relative paths to make it portable and testable
REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
SESSIONS_DIR = REPO_ROOT / ".hegemonikon" / "sessions"
DB_PATH = REPO_ROOT / ".hegemonikon" / "lancedb"
TABLE_NAME = "sessions"


class SessionDocument(BaseModel):
    """Session document schema."""
    filename: str
    title: str
    exported_at: str
    message_count: int
    content: str  # Full content
    content_preview: str  # For search results


def parse_session_file(filepath: Path) -> Optional[SessionDocument]:
    """Parse a session markdown file into a document."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Title extraction (# start)
        title = "Untitled"
        for line in lines[:5]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Exported at
        exported_at = ""
        for line in lines[:10]:
            if "**Exported**" in line or "エクスポート日時" in line:
                match = re.search(r"\d{4}[-/]\d{2}[-/]\d{2}.*?[\d:.]+", line)
                if match:
                    exported_at = match.group()
                break

        # Message count
        message_count = 0
        for line in lines[:10]:
            if "**Messages**" in line or "**メッセージ数**" in line:
                match = re.search(r"(\d+)", line)
                if match:
                    message_count = int(match.group(1))
                break

        # Body extraction (after ---)
        body_start = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                body_start = i + 1
                break

        body_lines = []
        for line in lines[body_start:]:
            # Skip headers and separators
            if line.startswith("## 🤖") or line.startswith("## 👤") or line.startswith("### "):
                continue
            if line.strip() == "---":
                continue
            if line.strip():
                body_lines.append(line.strip())

        full_content = "\n".join(body_lines)

        # Remove CSS noise
        full_content = re.sub(r"/\*.*?\*/", "", full_content, flags=re.DOTALL)
        full_content = re.sub(r"@media\s*\([^)]*\)\s*\{[^}]*\}", "", full_content)
        full_content = re.sub(r"\.markdown[-\w]*\s*\{[^}]*\}", "", full_content)
        full_content = re.sub(r"Thought for \d+s\s*", "", full_content)
        full_content = re.sub(r"Thought for <\d+s\s*", "", full_content)
        full_content = re.sub(r"\n{3,}", "\n\n", full_content).strip()

        preview = full_content[:500].replace("\n", " ")

        return SessionDocument(
            filename=filepath.name,
            title=title,
            exported_at=exported_at,
            message_count=message_count,
            content=full_content[:10000],  # Max 10KB
            content_preview=preview,
        )

    except Exception as e:
        print(f"[Chronos] Error parsing {filepath.name}: {e}")
        return None


def ingest_to_chronos(docs: Optional[List[SessionDocument]] = None) -> int:
    """Ingest session documents to LanceDB."""
    if lancedb is None:
        return 0

    print("[Chronos] Ingesting to LanceDB")
    print(f"    Sessions: {SESSIONS_DIR}")
    print(f"    Database: {DB_PATH}")

    DB_PATH.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(DB_PATH))

    # If docs not provided, scan SESSIONS_DIR
    if docs is None:
        if not SESSIONS_DIR.exists():
            print(f"[Chronos] Session directory not found: {SESSIONS_DIR}")
            return 0

        session_files = list(SESSIONS_DIR.glob("*.md"))
        print(f"[Chronos] Found {len(session_files)} session files")

        docs = []
        for filepath in session_files:
            doc = parse_session_file(filepath)
            if doc and len(doc.content) > 50:
                docs.append(doc)

    if not docs:
        print("[Chronos] No valid documents to index")
        return 0

    # Drop existing table to rebuild (simple strategy)
    if TABLE_NAME in db.table_names():
        db.drop_table(TABLE_NAME)

    # Create table
    data = [doc.model_dump() for doc in docs]
    table = db.create_table(TABLE_NAME, data)

    # Create FTS index
    try:
        table.create_fts_index("content", replace=True)
        print(f"[Chronos] Created FTS index on 'content'")
    except Exception as e:
        print(f"[Chronos] FTS index creation failed (might need tantivy-py): {e}")

    count = len(docs)
    print(f"[Chronos] Indexed {count} documents")
    return count


def get_chronos_count() -> int:
    """Get the number of indexed documents."""
    if lancedb is None or not DB_PATH.exists():
        return 0

    try:
        db = lancedb.connect(str(DB_PATH))
        if TABLE_NAME not in db.table_names():
            return 0
        table = db.open_table(TABLE_NAME)
        return table.count_rows()
    except Exception:
        return 0

def search_chronos(query: str, limit: int = 5) -> List[dict]:
    """Search sessions."""
    if lancedb is None or not DB_PATH.exists():
        return []

    try:
        db = lancedb.connect(str(DB_PATH))
        if TABLE_NAME not in db.table_names():
            return []

        table = db.open_table(TABLE_NAME)
        results = table.search(query, query_type="fts").limit(limit).to_list()
        return results
    except Exception as e:
        print(f"[Chronos] Search error: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "search":
         query = " ".join(sys.argv[2:])
         results = search_chronos(query)
         for r in results:
             print(f"- {r['title']} ({r['filename']})")
    else:
        ingest_to_chronos()
