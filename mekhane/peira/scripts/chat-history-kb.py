# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
Chat History Knowledge Base - LanceDB Edition
==============================================

Antigravityチャット履歴をDB化し、M8 Anamnēsisの長期記憶として活用。
AIDB機構（aidb-kb.py）をベースに改修。

Usage:
    python chat-history-kb.py setup             # モデルダウンロード
    python chat-history-kb.py index             # 全件インデックス
    python chat-history-kb.py sync              # 差分同期
    python chat-history-kb.py search "query"    # 意味検索
    python chat-history-kb.py stats             # 統計表示

Requirements:
    pip install lancedb onnxruntime tokenizers numpy
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Paths
BRAIN_DIR = Path(r"C:\Users\makar\.gemini\antigravity\brain")
KB_DIR = Path(r"M:\Hegemonikon\forge\knowledge_base")
LANCE_DIR = KB_DIR / "_index" / "lancedb"
SYNC_STATE_FILE = KB_DIR / "_index" / "sync_state.json"
MODELS_DIR = Path(r"M:\Hegemonikon\forge\models\bge-small")

# Embedding config
EMBEDDING_DIM = 384  # BGE-small


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        import lancedb
    except ImportError:
        missing.append("lancedb")
    try:
        import onnxruntime
    except ImportError:
        missing.append("onnxruntime")
    try:
        from tokenizers import Tokenizer
    except ImportError:
        missing.append("tokenizers")
    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        return False
    return True


class Embedder:
    """ONNX-based text embedding (reused from aidb-kb.py)."""

    def __init__(self):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        import numpy as np

        self.np = np

        model_path = MODELS_DIR / "model.onnx"
        tokenizer_path = MODELS_DIR / "tokenizer.json"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n" "Run: python aidb-kb.py setup"
            )

        self.session = ort.InferenceSession(str(model_path))
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(length=512)

    def embed(self, text: str) -> list:
        """Generate embedding for text."""
        encoded = self.tokenizer.encode(text)

        input_ids = self.np.array([encoded.ids], dtype=self.np.int64)
        attention_mask = self.np.array([encoded.attention_mask], dtype=self.np.int64)
        token_type_ids = self.np.zeros_like(input_ids)

        outputs = self.session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        embeddings = outputs[0]
        mask = attention_mask[:, :, None]
        pooled = (embeddings * mask).sum(axis=1) / mask.sum(axis=1)

        norm = self.np.linalg.norm(pooled, axis=1, keepdims=True)
        normalized = pooled / norm

        return normalized[0].tolist()


def get_sessions() -> list[dict]:
    """Get all sessions from brain directory."""
    sessions = []

    for session_dir in BRAIN_DIR.iterdir():
        if not session_dir.is_dir():
            continue
        if session_dir.name.startswith("_"):
            continue

        session_id = session_dir.name
        artifacts = []

        for md_file in session_dir.glob("*.md"):
            meta_file = session_dir / f"{md_file.name}.metadata.json"

            if not meta_file.exists():
                continue

            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)

            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            artifacts.append(
                {
                    "session_id": session_id,
                    "artifact_type": meta.get("artifactType", "unknown"),
                    "summary": meta.get("summary", ""),
                    "content": content[:3000],
                    "updated_at": meta.get("updatedAt", ""),
                    "file_path": str(md_file),
                }
            )

        if artifacts:
            sessions.append(
                {
                    "session_id": session_id,
                    "artifacts": artifacts,
                }
            )

    return sessions


def load_sync_state() -> Optional[datetime]:
    """Load last sync timestamp."""
    if not SYNC_STATE_FILE.exists():
        return None

    with open(SYNC_STATE_FILE, "r") as f:
        data = json.load(f)

    ts = data.get("last_sync")
    if ts:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return None


def save_sync_state():
    """Save current sync timestamp."""
    SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    from datetime import timezone

    with open(SYNC_STATE_FILE, "w") as f:
        # Use timezone-aware UTC
        json.dump({"last_sync": datetime.now(timezone.utc).isoformat()}, f)


def build_index(incremental: bool = False, report_mode: bool = False):
    """Build LanceDB index."""
    if not check_dependencies():
        return

    import lancedb

    if not report_mode:
        print("Initializing embedder...")

    try:
        embedder = Embedder()
    except Exception as e:
        if report_mode:
            print(
                f"[Hegemonikon] M8 Anamnēsis\n  Sync Phase: Error\n  Reason: Embedder init failed ({e})"
            )
        else:
            print(f"Error initializing embedder: {e}")
        return

    if not report_mode:
        print("Connecting to LanceDB...")

    try:
        LANCE_DIR.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(str(LANCE_DIR))
    except Exception as e:
        if report_mode:
            print(
                f"[Hegemonikon] M8 Anamnēsis\n  Sync Phase: Error\n  Reason: DB connection failed ({e})"
            )
        else:
            print(f"Error connecting to DB: {e}")
        return

    last_sync = load_sync_state() if incremental else None
    sessions = get_sessions()

    if not report_mode:
        print(f"Found {len(sessions)} sessions.")

    all_data = []

    for session in sessions:
        for artifact in session["artifacts"]:
            # Check if needs processing
            if incremental and last_sync:
                artifact_time = artifact.get("updated_at", "")
                if artifact_time:
                    try:
                        at = datetime.fromisoformat(
                            artifact_time.replace("Z", "+00:00")
                        )
                        if at <= last_sync:
                            continue
                    except Exception as e:
                        s_id = artifact.get("session_id", "unknown")
                        a_type = artifact.get("artifact_type", "unknown")
                        msg = f"Failed to parse timestamp for artifact {s_id}/{a_type}: {e}"
                        if report_mode:
                            print(
                                f"[Hegemonikon] M8 Anamnēsis\n  Sync Phase: Warning\n  Reason: {msg}"
                            )
                        else:
                            print(f"Warning: {msg}. Skipping.")
                        continue

            # Generate ID
            art_type = (
                artifact.get("artifact_type", "unknown")
                .replace("ARTIFACT_TYPE_", "")
                .lower()
            )
            doc_id = f"{artifact['session_id']}_{art_type}"

            # Robust embedding
            try:
                summary = artifact.get("summary", "") or ""
                content = artifact.get("content", "") or ""
                embed_text = f"{summary} {content[:1000]}"
                vector = embedder.embed(embed_text)

                all_data.append(
                    {
                        "id": doc_id,
                        "session_id": artifact["session_id"],
                        "artifact_type": art_type,
                        "summary": summary[:500],
                        "content": content[:3000],
                        "updated_at": artifact.get("updated_at", ""),
                        "vector": vector,
                    }
                )
            except Exception as e:
                if not report_mode:
                    print(f"Skipping artifact {doc_id}: {e}")
                continue

    if not all_data:
        if report_mode:
            print(
                f"[Hegemonikon] M8 Anamnēsis\n  Sync Phase: Skipped\n  Reason: No new data"
            )
        else:
            print("No new data to index.")
        save_sync_state()
        return

    if not report_mode:
        print(f"Indexing {len(all_data)} artifacts...")

    # Create/update table
    try:
        existing_tables = db.list_tables()
        table_names = (
            existing_tables.tables
            if hasattr(existing_tables, "tables")
            else list(existing_tables)
        )
        if "chat_history" in table_names:
            if incremental:
                table = db.open_table("chat_history")
                # Delete existing records that match the new data IDs
                new_ids = [item["id"] for item in all_data]
                if new_ids:
                    # Batch delete to avoid query length limits
                    batch_size = 100
                    for i in range(0, len(new_ids), batch_size):
                        batch = new_ids[i : i + batch_size]
                        ids_str = ", ".join([f"'{bid}'" for bid in batch])
                        table.delete(f"id IN ({ids_str})")
                table.add(all_data)
            else:
                db.drop_table("chat_history")
                table = db.create_table("chat_history", data=all_data)
        else:
            table = db.create_table("chat_history", data=all_data)

        save_sync_state()

        if report_mode:
            print(
                f"[Hegemonikon] M8 Anamnēsis\n  Sync Phase: Complete\n  Processed: {len(sessions)} sessions\n  New Index: {len(all_data)} chunks"
            )
        else:
            print(f"\n[OK] Index built successfully!")
            print(f"  Location: {LANCE_DIR}")
            print(f"  Artifacts: {len(all_data)}")

    except Exception as e:
        if report_mode:
            print(
                f"[Hegemonikon] M8 Anamnēsis\n  Sync Phase: Error\n  Reason: DB write failed ({e})"
            )
        else:
            print(f"Error writing to DB: {e}")


def search(query: str, n_results: int = 5):
    """Semantic search."""
    if not check_dependencies():
        return

    import lancedb

    if not LANCE_DIR.exists():
        print("Error: Index not found. Run 'python chat-history-kb.py index' first.")
        return

    embedder = Embedder()
    query_vector = embedder.embed(query)

    db = lancedb.connect(str(LANCE_DIR))
    table = db.open_table("chat_history")

    results = table.search(query_vector).limit(n_results).to_list()

    print(f'\n[SEARCH] Query: "{query}"\n')
    print("-" * 60)

    for i, r in enumerate(results):
        print(f"\n[{i+1}] Session: {r['session_id'][:8]}...")
        print(f"    Type: {r['artifact_type']}")
        print(f"    Summary: {r['summary'][:100]}...")
        print(f"    Updated: {r['updated_at']}")

    print("\n" + "-" * 60)


def show_stats():
    """Show statistics."""
    sessions = get_sessions()

    print(f"\n[STATS] Chat History Knowledge Base")
    print("=" * 40)
    print(f"Total Sessions: {len(sessions)}")

    artifact_counts = {}
    for s in sessions:
        for a in s["artifacts"]:
            t = a["artifact_type"]
            artifact_counts[t] = artifact_counts.get(t, 0) + 1

    print(f"\nBy Artifact Type:")
    for t, c in sorted(artifact_counts.items()):
        print(f"  {t}: {c}")

    # Check index status
    if LANCE_DIR.exists():
        try:
            import lancedb

            db = lancedb.connect(str(LANCE_DIR))
            existing_tables = db.list_tables()
            table_names = (
                existing_tables.tables
                if hasattr(existing_tables, "tables")
                else list(existing_tables)
            )
            if "chat_history" in table_names:
                table = db.open_table("chat_history")
                print(f"\nIndex Status: [OK] Active")
                print(f"Indexed: {len(table.to_pandas())}")
        except Exception as e:
            print(f"\nIndex Status: [X] Error: {e}")
    else:
        print(f"\nIndex Status: [X] Not built")

    # Sync state
    last_sync = load_sync_state()
    if last_sync:
        print(f"\nLast Sync: {last_sync.isoformat()}")
    else:
        print(f"\nLast Sync: Never")

    print("=" * 40)


def setup_model():
    """Download ONNX embedding model."""
    import urllib.request

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if (MODELS_DIR / "model.onnx").exists() and (
        MODELS_DIR / "tokenizer.json"
    ).exists():
        print("Model already exists.")
        return

    print("Downloading BGE-small ONNX model...")

    files = {
        "model.onnx": "https://huggingface.co/Xenova/bge-small-en-v1.5/resolve/main/onnx/model.onnx",
        "tokenizer.json": "https://huggingface.co/Xenova/bge-small-en-v1.5/resolve/main/tokenizer.json",
    }

    for filename, url in files.items():
        dest = MODELS_DIR / filename
        if dest.exists():
            print(f"  {filename} already exists, skipping.")
            continue
        print(f"  Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  [OK] {filename} downloaded.")
        except Exception as e:
            print(f"  Error: {e}")
            return

    print("[OK] Model downloaded successfully!")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    if command == "setup":
        setup_model()
    elif command == "index":
        build_index(incremental=False)

    elif command == "sync":
        report_mode = "--report" in sys.argv
        # NOTE: LanceDB append-only logic creates duplicates on update.
        # Using incremental=True with delete-before-insert to ensure data consistency.
        build_index(incremental=True, report_mode=report_mode)
    elif command == "search":
        if len(sys.argv) < 3:
            print('Usage: python chat-history-kb.py search "query"')
            return
        search(" ".join(sys.argv[2:]))
    elif command == "stats":
        show_stats()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
