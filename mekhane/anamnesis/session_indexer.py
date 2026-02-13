# PURPOSE: セッション履歴を GnosisIndex (LanceDB) にインデックスする
"""
PROOF: [L2/インフラ] <- mekhane/anamnesis/

P3 → 記憶の永続化が必要
   → セッション履歴のセマンティック検索が必要
   → session_indexer.py が担う

Q.E.D.

---

Session Indexer — セッション履歴ベクトル検索

agq-sessions.sh --dump で取得した JSON を Paper モデルに変換し、
GnosisIndex に source="session" として投入する。

Usage:
    python mekhane/anamnesis/session_indexer.py <json_path>
    python mekhane/anamnesis/session_indexer.py --from-api
"""

import json
import re
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure hegemonikon root is in path
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))


def parse_sessions_from_json(data: dict) -> list[dict]:
    """trajectorySummaries JSON からセッション情報を抽出"""
    summaries = data.get("trajectorySummaries", {})
    sessions = []

    for conv_id, info in summaries.items():
        if not isinstance(info, dict):
            continue

        title = info.get("summary", "").strip()
        if not title:
            title = f"Session {conv_id[:8]}"

        # Workspace extraction
        workspaces = []
        for ws in info.get("workspaces", []):
            if isinstance(ws, dict):
                path = ws.get("workspacePath", "")
                if path:
                    workspaces.append(Path(path).name)

        sessions.append({
            "conversation_id": conv_id,
            "title": title,
            "step_count": info.get("stepCount", 0),
            "status": info.get("status", "unknown"),
            "created": info.get("createdTime", ""),
            "modified": info.get("lastModifiedTime", ""),
            "workspaces": workspaces,
        })

    return sessions


def sessions_to_records(sessions: list[dict]) -> list[dict]:
    """セッション情報を LanceDB レコード (既存スキーマ準拠) に変換

    既存テーブルスキーマ:
      primary_key, title, source, abstract, content,
      authors, doi, arxiv_id, url, citations, vector

    P3 フィールド拡充 (v2):
      content  → 構造化メタデータ (timestamps, status, duration)
      authors  → ワークスペース名 (プロジェクト文脈)
      url      → セッション conversation_id (逆引き用)
    """
    records = []

    for s in sessions:
        conv_id = s["conversation_id"]
        title = s["title"]
        workspaces = s.get("workspaces", [])
        step_count = s.get("step_count", 0)
        status = s.get("status", "unknown")
        created = s.get("created", "")
        modified = s.get("modified", "")

        # Duration calculation (if timestamps available)
        duration_str = ""
        if created and modified:
            try:
                from datetime import datetime as _dt
                # Parse ISO 8601 timestamps
                t_created = _dt.fromisoformat(created.replace("Z", "+00:00"))
                t_modified = _dt.fromisoformat(modified.replace("Z", "+00:00"))
                delta = t_modified - t_created
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes = remainder // 60
                duration_str = f"{hours}h{minutes:02d}m"
            except (ValueError, TypeError):
                pass

        # Build abstract: rich context for embedding quality
        abstract_parts = [
            f"Session: {title}",
            f"Steps: {step_count}",
            f"Status: {status}",
        ]
        if workspaces:
            abstract_parts.append(f"Workspaces: {', '.join(workspaces)}")
        if duration_str:
            abstract_parts.append(f"Duration: {duration_str}")

        abstract = ". ".join(abstract_parts)

        # P3: content — 構造化メタデータ (検索対象 + 情報保持)
        content_parts = []
        if created:
            content_parts.append(f"Created: {created}")
        if modified:
            content_parts.append(f"Modified: {modified}")
        if duration_str:
            content_parts.append(f"Duration: {duration_str}")
        content_parts.append(f"Status: {status}")
        content_parts.append(f"Steps: {step_count}")
        if workspaces:
            content_parts.append(f"Workspaces: {', '.join(workspaces)}")
        content = " | ".join(content_parts)

        # P3: authors — ワークスペース名 (プロジェクト文脈として活用)
        authors = ", ".join(workspaces) if workspaces else ""

        # P3: url — conversation_id (逆引き・リンク用)
        url = f"session://{conv_id}"

        record = {
            "primary_key": f"session:{conv_id}",
            "title": title,
            "source": "session",
            "abstract": abstract,
            "content": content,
            "authors": authors,
            "doi": "",
            "arxiv_id": "",
            "url": url,
            "citations": step_count,
            # vector will be added by indexer
        }
        records.append(record)

    return records


# ==============================================================
# Handoff Indexer — handoff_*.md を source="handoff" でインデックス
# ==============================================================

_HANDOFF_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "sessions"

# Regex patterns for Handoff parsing
_RE_TITLE = re.compile(r"^#\s+(?:🔄\s*)?(?:Handoff:\s*)?(.+)$", re.MULTILINE)
_RE_DATE = re.compile(
    r"\*\*日時\*\*:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", re.MULTILINE
)
_RE_SESSION_ID = re.compile(
    r"\*Session:\s*([0-9a-f-]{36})\*", re.MULTILINE
)
_RE_SECTION = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def parse_handoff_md(path: Path) -> dict:
    """Single handoff .md file -> structured dict"""
    text = path.read_text(encoding="utf-8", errors="replace")

    # Title: first H1 line
    title_match = _RE_TITLE.search(text)
    title = title_match.group(1).strip() if title_match else path.stem

    # Date from metadata blockquote
    date_match = _RE_DATE.search(text)
    date_str = date_match.group(1).strip() if date_match else ""

    # Fallback: extract date from filename  handoff_YYYY-MM-DD_HHMM.md
    if not date_str:
        fname_match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})", path.stem)
        if fname_match:
            date_str = f"{fname_match.group(1)} {fname_match.group(2)}:{fname_match.group(3)}"

    # Session ID (if present at bottom)
    session_match = _RE_SESSION_ID.search(text)
    session_id = session_match.group(1) if session_match else ""

    # Section headers for content summary
    sections = _RE_SECTION.findall(text)
    # Clean emoji prefixes
    sections = [re.sub(r"^[^\w]+", "", s).strip() for s in sections]

    return {
        "title": title,
        "date": date_str,
        "session_id": session_id,
        "sections": sections,
        "text": text,
        "filename": path.name,
    }


def handoffs_to_records(handoffs: list[dict]) -> list[dict]:
    """Parsed handoff dicts -> LanceDB-compatible records"""
    records = []
    for h in handoffs:
        # Build abstract from title + date + section list
        abstract_parts = [h["title"]]
        if h["date"]:
            abstract_parts.append(f"({h['date']})")
        if h["sections"]:
            abstract_parts.append("— " + ", ".join(h["sections"][:6]))
        abstract = " ".join(abstract_parts)

        # Content: full text truncated to ~4000 chars for embedding
        content = h["text"][:4000]

        # Primary key from filename for dedup
        primary_key = f"handoff:{h['filename']}"

        # URL: link to session if available
        url = f"session://{h['session_id']}" if h["session_id"] else ""

        record = {
            "primary_key": primary_key,
            "title": f"[Handoff] {h['title']}",
            "source": "handoff",
            "abstract": abstract,
            "content": content,
            "authors": "",
            "doi": "",
            "arxiv_id": "",
            "url": url,
            "citations": 0,
        }
        records.append(record)

    return records


def index_handoffs(handoff_dir: Optional[str] = None) -> int:
    """handoff_*.md を LanceDB にインデックス"""
    directory = Path(handoff_dir) if handoff_dir else _HANDOFF_DIR

    if not directory.exists():
        print(f"[Error] Handoff directory not found: {directory}")
        return 1

    md_files = sorted(directory.glob("handoff_*.md"))
    if not md_files:
        print("[Error] No handoff_*.md files found")
        return 1

    print(f"[HandoffIndexer] Found {len(md_files)} handoff files")

    # Parse all
    handoffs = [parse_handoff_md(f) for f in md_files]
    records = handoffs_to_records(handoffs)

    # Embed and add to LanceDB
    from mekhane.anamnesis.index import GnosisIndex, Embedder

    index = GnosisIndex()
    embedder = Embedder()

    # Dedupe against existing records
    if index._table_exists():
        table = index.db.open_table(index.TABLE_NAME)
        try:
            existing = table.to_pandas()
            existing_keys = set(existing["primary_key"].tolist())
            before = len(records)
            records = [r for r in records if r["primary_key"] not in existing_keys]
            skipped = before - len(records)
            if skipped:
                print(f"[HandoffIndexer] Skipped {skipped} duplicates")
        except Exception:
            pass  # Intentional: table may be empty or have incompatible schema

    if not records:
        print("[HandoffIndexer] No new handoffs to add (all duplicates)")
        return 0

    # Generate embeddings (title + abstract for embedding text)
    texts = [f"{r['title']} {r['abstract']}" for r in records]
    vectors = embedder.embed_batch(texts)

    # Attach vectors
    data_with_vectors = []
    for rec, vec in zip(records, vectors):
        rec["vector"] = vec
        data_with_vectors.append(rec)

    # Add to LanceDB
    if index._table_exists():
        table = index.db.open_table(index.TABLE_NAME)
        # Schema filtering (P4 pattern)
        schema_fields = {f.name for f in table.schema}
        filtered_data = [
            {k: v for k, v in record.items() if k in schema_fields}
            for record in data_with_vectors
        ]
        table.add(filtered_data)
    else:
        index.db.create_table(index.TABLE_NAME, data=data_with_vectors)

    print(f"[HandoffIndexer] ✅ Indexed {len(data_with_vectors)} handoffs")
    return 0


def fetch_all_conversations(max_sessions: int = 100) -> list[dict]:
    """AntigravityClient で全セッションの会話を取得"""
    from mekhane.ochema.antigravity_client import AntigravityClient

    client = AntigravityClient()

    # 全セッション一覧を取得 (session_info は内部で RPC_GET_TRAJECTORIES を使う)
    all_data = client._rpc(
        "exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories", {}
    )
    summaries = all_data.get("trajectorySummaries", {})

    conversations = []
    processed = 0

    for cid, meta in summaries.items():
        if processed >= max_sessions:
            break

        summary_text = meta.get("summary", "").strip()
        step_count = meta.get("stepCount", 0)
        trajectory_id = meta.get("trajectoryId", "")

        if not trajectory_id or step_count == 0:
            continue

        try:
            conv_data = client.session_read(cid, full=True)
            if "error" in conv_data:
                continue

            conversation = conv_data.get("conversation", [])
            if not conversation:
                continue

            # user + assistant のテキストを結合
            user_texts = []
            assistant_texts = []
            for turn in conversation:
                if turn.get("role") == "user":
                    user_texts.append(turn.get("content", ""))
                elif turn.get("role") == "assistant":
                    assistant_texts.append(turn.get("content", ""))

            full_text = "\n\n".join(user_texts + assistant_texts)

            conversations.append({
                "cascade_id": cid,
                "title": summary_text or f"Session {cid[:8]}",
                "step_count": step_count,
                "total_turns": conv_data.get("total_turns", 0),
                "user_text": "\n\n".join(user_texts),
                "assistant_text": "\n\n".join(assistant_texts),
                "full_text": full_text,
                "created": meta.get("createdTime", ""),
                "modified": meta.get("lastModifiedTime", ""),
            })
            processed += 1

            if processed % 10 == 0:
                print(f"  Fetched {processed} conversations...")

        except Exception as e:
            print(f"  [Warn] Failed to read {cid[:8]}: {e}")
            continue

    print(f"[ConvIndexer] Fetched {len(conversations)} conversations")
    return conversations


def conversations_to_records(conversations: list[dict]) -> list[dict]:
    """会話データを LanceDB レコードに変換"""
    records = []

    for conv in conversations:
        cascade_id = conv["cascade_id"]
        title = conv["title"]
        full_text = conv.get("full_text", "")

        # abstract: タイトル + ターン数 + 最初のユーザー入力の先頭200文字
        user_preview = conv.get("user_text", "")[:200]
        abstract = f"{title} ({conv.get('total_turns', 0)} turns) — {user_preview}"

        # content: 検索用テキスト (先頭 4000 文字)
        content = full_text[:4000] if full_text else abstract

        # 日付のパース
        created = conv.get("created", "")
        year = ""
        if created:
            try:
                # ISO format or timestamp
                if "T" in created:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    year = str(dt.year)
            except Exception:
                pass

        records.append({
            "primary_key": f"conv:{cascade_id}",
            "source": "conversation",
            "title": title,
            "abstract": abstract[:500],
            "content": content,
            "authors": "IDE Session",
            "year": year,
            "url": f"conversation://{cascade_id}",
            "citations": conv.get("step_count", 0),  # step count as proxy
        })

    return records


def index_conversations(max_sessions: int = 100) -> int:
    """全セッション会話を LanceDB にインデックス"""
    conversations = fetch_all_conversations(max_sessions)
    if not conversations:
        print("[ConvIndexer] No conversations to index")
        return 1

    records = conversations_to_records(conversations)

    from mekhane.anamnesis.index import GnosisIndex, Embedder

    index = GnosisIndex()
    embedder = Embedder()

    # Dedupe against existing records
    if index._table_exists():
        table = index.db.open_table(index.TABLE_NAME)
        try:
            existing = table.to_pandas()
            existing_keys = set(existing["primary_key"].tolist())
            before = len(records)
            records = [r for r in records if r["primary_key"] not in existing_keys]
            skipped = before - len(records)
            if skipped:
                print(f"[ConvIndexer] Skipped {skipped} duplicates")
        except Exception:
            pass  # Intentional: table may be empty or have incompatible schema

    if not records:
        print("[ConvIndexer] No new conversations to add (all duplicates)")
        return 0

    # Generate embeddings in batches
    BATCH_SIZE = 16
    data_with_vectors = []

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)

        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)

        print(f"  Embedded {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    # Add to LanceDB
    if index._table_exists():
        table = index.db.open_table(index.TABLE_NAME)
        schema_fields = {f.name for f in table.schema}
        filtered_data = [
            {k: v for k, v in record.items() if k in schema_fields}
            for record in data_with_vectors
        ]
        table.add(filtered_data)
    else:
        index.db.create_table(index.TABLE_NAME, data=data_with_vectors)

    print(f"[ConvIndexer] ✅ Indexed {len(data_with_vectors)} conversations")
    return 0


def index_from_json(json_path: str) -> int:
    """JSON ファイルからセッションをインデックス"""
    path = Path(json_path)
    if not path.exists():
        print(f"[Error] File not found: {json_path}")
        return 1

    with open(path) as f:
        data = json.load(f)

    sessions = parse_sessions_from_json(data)
    if not sessions:
        print("[Error] No sessions found in JSON")
        return 1

    print(f"[SessionIndexer] Parsed {len(sessions)} sessions")

    records = sessions_to_records(sessions)

    # Embed and add to LanceDB
    from mekhane.anamnesis.index import GnosisIndex, Embedder

    index = GnosisIndex()
    embedder = Embedder()

    # Dedupe: check existing primary_keys
    if index._table_exists():
        table = index.db.open_table(index.TABLE_NAME)
        try:
            existing = table.to_pandas()
            existing_keys = set(existing["primary_key"].tolist())
            before = len(records)
            records = [r for r in records if r["primary_key"] not in existing_keys]
            skipped = before - len(records)
            if skipped:
                print(f"[SessionIndexer] Skipped {skipped} duplicates")
        except Exception:
            pass  # Intentional: table may be empty or have incompatible schema

    if not records:
        print("[SessionIndexer] No new sessions to add (all duplicates)")
        return 0

    # Generate embeddings
    BATCH_SIZE = 32
    data_with_vectors = []

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)

        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)

        print(f"  Processed {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    # Add to LanceDB
    if index._table_exists():
        table = index.db.open_table(index.TABLE_NAME)
        table.add(data_with_vectors)
    else:
        index.db.create_table(index.TABLE_NAME, data=data_with_vectors)

    print(f"[SessionIndexer] ✅ Indexed {len(data_with_vectors)} sessions")
    return 0


def index_from_api() -> int:
    """API から直接取得してインデックス"""
    script = _HEGEMONIKON_ROOT / "scripts" / "agq-sessions.sh"
    if not script.exists():
        print(f"[Error] Script not found: {script}")
        return 1

    with tempfile.TemporaryDirectory(prefix="agq_sessions_") as tmpdir:
        dump_dir = Path(tmpdir)
        result = subprocess.run(
            ["bash", str(script), "--dump", str(dump_dir)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"[Error] agq-sessions.sh failed: {result.stderr}")
            return 1

        json_path = dump_dir / "trajectories_raw.json"
        if not json_path.exists():
            print("[Error] trajectories_raw.json not generated")
            return 1

        return index_from_json(str(json_path))


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Index session history into GnosisIndex (LanceDB)"
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        help="Path to trajectories_raw.json (from agq-sessions.sh --dump)",
    )
    parser.add_argument(
        "--from-api",
        action="store_true",
        help="Fetch from Language Server API directly",
    )
    parser.add_argument(
        "--handoffs",
        action="store_true",
        help="Index handoff_*.md files from mneme sessions directory",
    )
    parser.add_argument(
        "--handoff-dir",
        default=None,
        help="Custom handoff directory (default: ~/oikos/mneme/.hegemonikon/sessions)",
    )
    parser.add_argument(
        "--conversations",
        action="store_true",
        help="Index full conversation content from Language Server API",
    )
    parser.add_argument(
        "--max-sessions",
        type=int,
        default=100,
        help="Max sessions to index for --conversations (default: 100)",
    )

    args = parser.parse_args()

    if args.conversations:
        return index_conversations(args.max_sessions)
    elif args.handoffs:
        return index_handoffs(args.handoff_dir)
    elif args.from_api:
        return index_from_api()
    elif args.json_path:
        return index_from_json(args.json_path)
    else:
        print("Usage: session_indexer.py <json_path> | --from-api | --handoffs")
        return 1


if __name__ == "__main__":
    sys.exit(main())
