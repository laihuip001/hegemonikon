# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→知識管理が必要→chronos_ingest が担う
"""
Chronos Ingest - 会話履歴を Chronos インデックスに自動投入
"""
import re
from pathlib import Path
from datetime import datetime
from mekhane.symploke.indices.base import Document
from mekhane.symploke.indices.chronos import ChronosIndex

# Use the same default session dir as pks_cli.py
DEFAULT_SESSIONS_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "sessions"

# PURPOSE: Parse handoff file chunks into Documents
def parse_handoff_for_chronos(file_path: Path) -> list[Document]:
    """Parse a handoff file into conversation chunks for Chronos."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    session_id = file_path.stem

    match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
    timestamp_str = match.group(1) if match else datetime.now().strftime("%Y-%m-%d")
    timestamp = f"{timestamp_str}T00:00:00"

    docs = []
    sections = re.split(r'\n(?=## )', content)
    for i, section in enumerate(sections):
        section = section.strip()
        if len(section) < 50:
            continue
        if len(section) > 2000:
            section = section[:2000]

        docs.append(Document(
            id=f"{session_id}_s{i}",
            content=section,
            metadata={
                "timestamp": timestamp,
                "session_id": session_id,
                "chunk": i,
                "type": "conversation_chunk"
            }
        ))
    return docs

# PURPOSE: Get all handoff files for chronos ingest
def get_chronos_files() -> list[Path]:
    """Get all handoff files that contain conversation history."""
    if not DEFAULT_SESSIONS_DIR.exists():
        return []
    files = list(DEFAULT_SESSIONS_DIR.glob("handoff_20??-??-??_????.md"))
    return sorted(files, reverse=True)

# PURPOSE: Ingest documents to Chronos index
def ingest_to_chronos(docs: list[Document], save_path: str = None) -> int:
    """Ingest documents to Chronos index using real embeddings."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    sample_vec = adapter.encode(["test"])
    dim = sample_vec.shape[1] if sample_vec.ndim == 2 else len(sample_vec[0])
    index = ChronosIndex(adapter, "chronos", dimension=dim)
    index.initialize()

    count = index.ingest(docs)
    print(f"Ingested {count} documents to Chronos (real embeddings)")

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        adapter.save(save_path)
        print(f"💾 Saved index to: {save_path}")

    return count

# PURPOSE: Load a previously saved Chronos index
def load_chronos_index(load_path: str):
    """Load a previously saved Chronos index."""
    from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter

    adapter = EmbeddingAdapter()
    adapter.load(load_path)
    return adapter
