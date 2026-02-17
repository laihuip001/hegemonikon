# PROOF: [L2/インフラ] <- mekhane/anamnesis/ A0→記憶永続化→セッション履歴のインデックス化
# PURPOSE: セッション履歴を GnosisIndex (LanceDB) にインデックスする
"""
PROOF: [L2/インフラ] <- mekhane/anamnesis/

P3 → 記憶の永続化が必要
   → セッション履歴のセマンティック検索が必要
   → session_indexer.py が担う

Q.E.D.

---

Session Indexer — セッション履歴ベクトル検索

Language Server API から取得したセッション履歴、または agq-sessions.sh --dump で取得した
JSON を Paper モデルに変換し、GnosisIndex に source="session" として投入する。

Usage:
    python -m mekhane.anamnesis.session_indexer <json_path>
    python -m mekhane.anamnesis.session_indexer --from-api
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("session_indexer")

# Constants
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent

# Default paths via environment variables
MNEME_HOME = Path(os.environ.get("MNEME_HOME", Path.home() / "oikos" / "mneme"))
_HANDOFF_DIR = MNEME_HOME / ".hegemonikon" / "sessions"
_ROM_DIR = MNEME_HOME / ".hegemonikon" / "rom"
_EXPORT_DIR = MNEME_HOME / ".hegemonikon" / "sessions"
_BRAIN_DIR = Path(
    os.environ.get("BRAIN_DIR", Path.home() / ".gemini" / "antigravity" / "brain")
)


# --- Type Definitions ---

class SessionInfo(TypedDict):
    conversation_id: str
    title: str
    step_count: int
    status: str
    created: str
    modified: str
    workspaces: List[str]


class HandoffRecord(TypedDict):
    title: str
    date: str
    session_id: str
    sections: List[str]
    text: str
    filename: str


class StepInfo(TypedDict):
    conversation_id: str
    step_number: str
    content: str
    size: int


class ExportRecord(TypedDict):
    title: str
    conv_id: str
    exported_at: str
    user_count: int
    assistant_count: int
    content: str
    filename: str


class ConversationInfo(TypedDict):
    cascade_id: str
    title: str
    step_count: int
    total_turns: int
    user_text: str
    assistant_text: str
    full_text: str
    created: str
    modified: str


class RomRecord(TypedDict):
    title: str
    date: str
    derivative: str
    topics: List[str]
    exec_summary: str
    reliability: str
    semantic_tags: List[str]
    sections: List[str]
    text: str
    filename: str


# --- Functions ---

# PURPOSE: LS API の trajectorySummaries JSON からセッション情報を構造化 dict に抽出する
def parse_sessions_from_json(data: Dict[str, Any]) -> List[SessionInfo]:
    """PURPOSE: LS API の trajectorySummaries JSON からセッション情報を構造化 dict に抽出する"""
    summaries = data.get("trajectorySummaries", {})
    sessions: List[SessionInfo] = []

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

        session: SessionInfo = {
            "conversation_id": conv_id,
            "title": title,
            "step_count": info.get("stepCount", 0),
            "status": info.get("status", "unknown"),
            "created": info.get("createdTime", ""),
            "modified": info.get("lastModifiedTime", ""),
            "workspaces": workspaces,
        }
        sessions.append(session)

    return sessions


# PURPOSE: セッション情報を LanceDB レコード (既存スキーマ準拠) に変換する
def sessions_to_records(sessions: List[SessionInfo]) -> List[Dict[str, Any]]:
    """PURPOSE: セッション情報を LanceDB レコード (既存スキーマ準拠) に変換する"""
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
                logger.warning(f"Failed to parse timestamps for session {conv_id}")

        # Build abstract
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

        # Content
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

        authors = ", ".join(workspaces) if workspaces else ""
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
        }
        records.append(record)

    return records


# ==============================================================
# Handoff Indexer
# ==============================================================

# Regex patterns for Handoff parsing
_RE_TITLE = re.compile(r"^#\s+(?:🔄\s*)?(?:Handoff:\s*)?(.+)$", re.MULTILINE)
_RE_DATE = re.compile(
    r"\*\*日時\*\*:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", re.MULTILINE
)
_RE_SESSION_ID = re.compile(
    r"\*Session:\s*([0-9a-f-]{36})\*", re.MULTILINE
)
_RE_SECTION = re.compile(r"^##\s+(.+)$", re.MULTILINE)


# PURPOSE: Handoff マークダウンファイルをパースし構造化 dict に変換する
def parse_handoff_md(path: Path) -> HandoffRecord:
    """PURPOSE: Handoff マークダウンファイルをパースし構造化 dict に変換する"""
    text = path.read_text(encoding="utf-8", errors="replace")

    title_match = _RE_TITLE.search(text)
    title = title_match.group(1).strip() if title_match else path.stem

    date_match = _RE_DATE.search(text)
    date_str = date_match.group(1).strip() if date_match else ""

    if not date_str:
        fname_match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})", path.stem)
        if fname_match:
            date_str = f"{fname_match.group(1)} {fname_match.group(2)}:{fname_match.group(3)}"

    session_match = _RE_SESSION_ID.search(text)
    session_id = session_match.group(1) if session_match else ""

    sections = _RE_SECTION.findall(text)
    sections = [re.sub(r"^[^\w]+", "", s).strip() for s in sections]

    return {
        "title": title,
        "date": date_str,
        "session_id": session_id,
        "sections": sections,
        "text": text,
        "filename": path.name,
    }


# PURPOSE: パース済み Handoff dict を LanceDB 互換レコードに変換する
def handoffs_to_records(handoffs: List[HandoffRecord]) -> List[Dict[str, Any]]:
    """PURPOSE: パース済み Handoff dict を LanceDB 互換レコードに変換する"""
    records = []
    for h in handoffs:
        abstract_parts = [h["title"]]
        if h["date"]:
            abstract_parts.append(f"({h['date']})")
        if h["sections"]:
            abstract_parts.append("— " + ", ".join(h["sections"][:6]))
        abstract = " ".join(abstract_parts)

        content = h["text"][:4000]
        primary_key = f"handoff:{h['filename']}"
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


# PURPOSE: handoff_*.md ファイル群を LanceDB にセマンティックインデックスする
def index_handoffs(handoff_dir: Optional[str] = None) -> int:
    """PURPOSE: handoff_*.md ファイル群を LanceDB にセマンティックインデックスする"""
    directory = Path(handoff_dir) if handoff_dir else _HANDOFF_DIR

    if not directory.exists():
        logger.error(f"Handoff directory not found: {directory}")
        return 1

    md_files = sorted(directory.glob("handoff_*.md"))
    if not md_files:
        logger.info("No handoff_*.md files found")
        return 1

    logger.info(f"Found {len(md_files)} handoff files")

    handoffs = [parse_handoff_md(f) for f in md_files]
    records = handoffs_to_records(handoffs)

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    # Dedupe
    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates (table might be empty or schema mismatch)", exc_info=True)

    if not records:
        logger.info("No new handoffs to add (all duplicates)")
        return 0

    texts = [f"{r['title']} {r['abstract']}" for r in records]
    vectors = embedder.embed_batch(texts)

    data_with_vectors = []
    for rec, vec in zip(records, vectors):
        rec["vector"] = vec
        data_with_vectors.append(rec)

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            schema_fields = {f.name for f in table.schema}
            filtered_data = [
                {k: v for k, v in record.items() if k in schema_fields}
                for record in data_with_vectors
            ]
            table.add(filtered_data)
        except Exception:
            logger.error("Failed to add records to existing table", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} handoffs")
    return 0


# PURPOSE: AntigravityClient 経由で LS API から全セッション会話データを取得する
def fetch_all_conversations(max_sessions: int = 100) -> List[ConversationInfo]:
    """PURPOSE: AntigravityClient 経由で LS API から全セッション会話データを取得する"""
    from mekhane.ochema.antigravity_client import AntigravityClient

    client = AntigravityClient()

    try:
        all_data = client._rpc(
            "exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories", {}
        )
    except Exception:
        logger.error("Failed to fetch cascade trajectories from Language Server", exc_info=True)
        return []

    summaries = all_data.get("trajectorySummaries", {})
    conversations: List[ConversationInfo] = []
    processed = 0

    for cid, meta in summaries.items():
        if processed >= max_sessions:
            break

        step_count = meta.get("stepCount", 0)
        trajectory_id = meta.get("trajectoryId", "")

        if not trajectory_id or step_count == 0:
            continue

        try:
            conv_data = client.session_read(cid, full=True)
            if "error" in conv_data:
                logger.warning(f"Error reading session {cid[:8]}: {conv_data['error']}")
                continue

            conversation = conv_data.get("conversation", [])
            if not conversation:
                continue

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
                "title": meta.get("summary", "").strip() or f"Session {cid[:8]}",
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
                logger.info(f"Fetched {processed} conversations...")

        except Exception:
            logger.error(f"Failed to read {cid[:8]}", exc_info=True)
            continue

    logger.info(f"Fetched {len(conversations)} conversations")
    return conversations


# PURPOSE: 会話データを LanceDB セマンティック検索用レコードに変換する
def conversations_to_records(conversations: List[ConversationInfo]) -> List[Dict[str, Any]]:
    """PURPOSE: 会話データを LanceDB セマンティック検索用レコードに変換する"""
    records = []

    for conv in conversations:
        cascade_id = conv["cascade_id"]
        title = conv["title"]
        full_text = conv.get("full_text", "")

        user_preview = conv.get("user_text", "")[:200]
        abstract = f"{title} ({conv.get('total_turns', 0)} turns) — {user_preview}"
        content = full_text[:4000] if full_text else abstract

        created = conv.get("created", "")
        year = ""
        if created:
            try:
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
            "citations": conv.get("step_count", 0),
        })

    return records


# PURPOSE: 全セッション会話を取得し LanceDB にセマンティックインデックスする
def index_conversations(max_sessions: int = 100) -> int:
    """PURPOSE: 全セッション会話を取得し LanceDB にセマンティックインデックスする"""
    conversations = fetch_all_conversations(max_sessions)
    if not conversations:
        logger.info("No conversations to index")
        return 1

    records = conversations_to_records(conversations)

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates", exc_info=True)

    if not records:
        logger.info("No new conversations to add (all duplicates)")
        return 0

    BATCH_SIZE = 16
    data_with_vectors = []

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)

        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)

        logger.info(f"Embedded {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            schema_fields = {f.name for f in table.schema}
            filtered_data = [
                {k: v for k, v in record.items() if k in schema_fields}
                for record in data_with_vectors
            ]
            table.add(filtered_data)
        except Exception:
            logger.error("Failed to add records", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} conversations")
    return 0


# ==============================================================
# Steps Indexer
# ==============================================================

# PURPOSE: .system_generated/steps/ 配下の output.txt をパースしレコード化する
def parse_step_outputs(brain_dir: Optional[str] = None, max_per_session: int = 20) -> List[StepInfo]:
    """PURPOSE: .system_generated/steps/ 配下の output.txt をパースしレコード化する"""
    directory = Path(brain_dir) if brain_dir else _BRAIN_DIR
    if not directory.exists():
        return []

    steps: List[StepInfo] = []
    for conv_dir in directory.iterdir():
        if not conv_dir.is_dir():
            continue
        conv_id = conv_dir.name
        steps_dir = conv_dir / ".system_generated" / "steps"
        if not steps_dir.exists():
            continue

        output_files = sorted(
            steps_dir.glob("*/output.txt"),
            key=lambda p: int(p.parent.name) if p.parent.name.isdigit() else 0,
            reverse=True,
        )

        for i, out_file in enumerate(output_files[:max_per_session]):
            step_num = out_file.parent.name
            try:
                text = out_file.read_text(encoding="utf-8", errors="replace")[:4000]
            except Exception:
                continue

            if not text.strip():
                continue

            steps.append({
                "conversation_id": conv_id,
                "step_number": step_num,
                "content": text,
                "size": out_file.stat().st_size,
            })

    return steps


# PURPOSE: ステップ出力データを LanceDB 互換レコードに変換する
def steps_to_records(steps: List[StepInfo]) -> List[Dict[str, Any]]:
    """PURPOSE: ステップ出力データを LanceDB 互換レコードに変換する"""
    records = []
    for s in steps:
        conv_id = s["conversation_id"]
        step_num = s["step_number"]
        content = s["content"]

        first_line = content.split("\n", 1)[0][:120].strip()
        title = f"[Step {step_num}] {first_line}" if first_line else f"Step {step_num}"

        abstract = f"Step {step_num} in session {conv_id[:8]}. Size: {s['size']} bytes. {first_line}"

        records.append({
            "primary_key": f"step:{conv_id}:{step_num}",
            "title": title,
            "source": "step",
            "abstract": abstract[:500],
            "content": content,
            "authors": "IDE Step Output",
            "doi": "",
            "arxiv_id": "",
            "url": f"session://{conv_id}#step-{step_num}",
            "citations": 0,
        })

    return records


# PURPOSE: .system_generated/steps/ の出力ファイルを LanceDB にインデックスする
def index_steps(brain_dir: Optional[str] = None, max_per_session: int = 20) -> int:
    """PURPOSE: .system_generated/steps/ の出力ファイルを LanceDB にインデックスする"""
    steps = parse_step_outputs(brain_dir, max_per_session)
    if not steps:
        logger.info("No step outputs found")
        return 1

    logger.info(f"Found {len(steps)} step outputs")
    records = steps_to_records(steps)

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates", exc_info=True)

    if not records:
        logger.info("No new steps to add (all duplicates)")
        return 0

    BATCH_SIZE = 16
    data_with_vectors = []

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)

        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)

        logger.info(f"Embedded {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            schema_fields = {f.name for f in table.schema}
            filtered_data = [
                {k: v for k, v in record.items() if k in schema_fields}
                for record in data_with_vectors
            ]
            table.add(filtered_data)
        except Exception:
            logger.error("Failed to add records", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} steps")
    return 0


# ==============================================================
# Export MD Indexer
# ==============================================================

_RE_EXPORT_ID = re.compile(r"\*\*ID\*\*:\s*`([^`]+)`")
_RE_EXPORT_DATE = re.compile(r"\*\*エクスポート日時\*\*:\s*(.+)")


# PURPOSE: export_chats.py 出力の MD ファイルを構造化 dict にパースする
def parse_export_md(path: Path) -> ExportRecord:
    """PURPOSE: export_chats.py 出力の MD ファイルを構造化 dict にパースする"""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    title = path.stem
    for line in lines[:5]:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    id_match = _RE_EXPORT_ID.search(text)
    conv_id = id_match.group(1) if id_match else ""

    date_match = _RE_EXPORT_DATE.search(text)
    exported_at = date_match.group(1).strip() if date_match else ""

    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            body_start = i + 1
            break

    user_count = len(re.findall(r"^## 👤 User", text, re.MULTILINE))
    assistant_count = len(re.findall(r"^## 🤖 Claude", text, re.MULTILINE))

    body = "\n".join(lines[body_start:])
    body = re.sub(r"Thought for \d+s\s*", "", body)
    body = re.sub(r"Thought for <\d+s\s*", "", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    return {
        "title": title,
        "conv_id": conv_id,
        "exported_at": exported_at,
        "user_count": user_count,
        "assistant_count": assistant_count,
        "content": body[:4000],
        "filename": path.name,
    }


# PURPOSE: パース済みエクスポート dict を LanceDB 互換レコードに変換する
def exports_to_records(exports: List[ExportRecord]) -> List[Dict[str, Any]]:
    """PURPOSE: パース済みエクスポート dict を LanceDB 互換レコードに変換する"""
    records = []
    for e in exports:
        abstract = f"{e['title']} ({e['user_count']} user, {e['assistant_count']} assistant messages)"
        if e["exported_at"]:
            abstract += f" — exported {e['exported_at'][:10]}"

        records.append({
            "primary_key": f"export:{e['filename']}",
            "title": e["title"],
            "source": "export",
            "abstract": abstract[:500],
            "content": e["content"],
            "authors": "IDE Export",
            "doi": "",
            "arxiv_id": "",
            "url": f"session://{e['conv_id']}" if e["conv_id"] else "",
            "citations": e["user_count"] + e["assistant_count"],
        })
    return records


# PURPOSE: export_chats.py 出力 MD を LanceDB にセマンティックインデックスする
def index_exports(export_dir: Optional[str] = None) -> int:
    """PURPOSE: export_chats.py 出力 MD を LanceDB にセマンティックインデックスする"""
    directory = Path(export_dir) if export_dir else _EXPORT_DIR
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return 1

    md_files = sorted(directory.glob("*_conv_*.md"))
    if not md_files:
        logger.info("No export MD files found")
        return 1

    logger.info(f"Found {len(md_files)} export files")

    exports = [parse_export_md(f) for f in md_files]
    records = exports_to_records(exports)

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates", exc_info=True)

    if not records:
        logger.info("No new exports to add (all duplicates)")
        return 0

    BATCH_SIZE = 16
    data_with_vectors = []
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)
        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)
        logger.info(f"Embedded {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            schema_fields = {f.name for f in table.schema}
            filtered_data = [
                {k: v for k, v in record.items() if k in schema_fields}
                for record in data_with_vectors
            ]
            table.add(filtered_data)
        except Exception:
            logger.error("Failed to add records", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} exports")
    return 0


# ==============================================================
# ROM Indexer
# ==============================================================

_RE_ROM_TITLE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_RE_ROM_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_RE_ROM_SEMANTIC_TAG = re.compile(
    r">\s*\*\*\[(DEF|FACT|RULE|CONFLICT|OPINION)\]\*\*", re.MULTILINE
)


# PURPOSE: ROM マークダウンファイルをパースし構造化 dict に変換する
def parse_rom_md(path: Path) -> RomRecord:
    """PURPOSE: ROM マークダウンファイルをパースし構造化 dict に変換する"""
    text = path.read_text(encoding="utf-8", errors="replace")

    title_match = _RE_ROM_TITLE.search(text)
    title = title_match.group(1).strip() if title_match else path.stem

    topics = []
    exec_summary = ""
    reliability = ""
    source_date = ""
    fm_match = _RE_ROM_FRONTMATTER.match(text)
    if fm_match:
        try:
            import yaml
            fm = yaml.safe_load(fm_match.group(1))
            if isinstance(fm, dict):
                topics = fm.get("topics", [])
                exec_summary = fm.get("exec_summary", "")
                reliability = fm.get("reliability", "")
                source_date = fm.get("source_date", "")
        except Exception:
            pass

    date_str = ""
    fname_match = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})", path.stem)
    if fname_match:
        date_str = f"{fname_match.group(1)} {fname_match.group(2)}:{fname_match.group(3)}"
    elif source_date and source_date != "Unknown":
        date_str = source_date

    derivative = "standard"
    if "_snapshot_" in path.stem or path.stem.endswith("_snapshot"):
        derivative = "rom-"
    elif "_rag_" in path.stem or path.stem.endswith("_rag"):
        derivative = "rom+"

    semantic_tags = _RE_ROM_SEMANTIC_TAG.findall(text)
    sections = _RE_SECTION.findall(text)
    sections = [re.sub(r"^[^\w]+", "", s).strip() for s in sections]

    return {
        "title": title,
        "date": date_str,
        "derivative": derivative,
        "topics": topics,
        "exec_summary": exec_summary,
        "reliability": reliability,
        "semantic_tags": semantic_tags,
        "sections": sections,
        "text": text,
        "filename": path.name,
    }


# PURPOSE: パース済み ROM dict を LanceDB 互換レコードに変換する
def roms_to_records(roms: List[RomRecord]) -> List[Dict[str, Any]]:
    """PURPOSE: パース済み ROM dict を LanceDB 互換レコードに変換する"""
    records = []
    for r in roms:
        abstract_parts = [f"[ROM/{r['derivative']}] {r['title']}"]
        if r["date"]:
            abstract_parts.append(f"({r['date']})")
        if r["exec_summary"]:
            abstract_parts.append(f"— {r['exec_summary'][:200]}")
        elif r["sections"]:
            abstract_parts.append("— " + ", ".join(r["sections"][:6]))
        if r["topics"]:
            abstract_parts.append(f"Topics: {', '.join(r['topics'][:5])}")
        abstract = " ".join(abstract_parts)

        content = r["text"][:4000]
        primary_key = f"rom:{r['filename']}"
        url = str(_ROM_DIR / r["filename"])

        record = {
            "primary_key": primary_key,
            "title": f"[ROM] {r['title']}",
            "source": "rom",
            "abstract": abstract[:500],
            "content": content,
            "authors": f"derivative:{r['derivative']}",
            "doi": "",
            "arxiv_id": "",
            "url": url,
            "citations": len(r.get("semantic_tags", [])),
        }
        records.append(record)

    return records


# PURPOSE: ROM ファイル群を LanceDB にセマンティックインデックスする
def index_roms(rom_dir: Optional[str] = None) -> int:
    """PURPOSE: ROM ファイル群を LanceDB にセマンティックインデックスする"""
    directory = Path(rom_dir) if rom_dir else _ROM_DIR

    if not directory.exists():
        logger.error(f"ROM directory not found: {directory}")
        logger.info("Run /rom to generate ROM files first")
        return 1

    md_files = sorted(directory.glob("rom_*.md"))
    if not md_files:
        logger.info("No rom_*.md files found")
        return 1

    logger.info(f"Found {len(md_files)} ROM files")

    roms = [parse_rom_md(f) for f in md_files]
    records = roms_to_records(roms)

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates", exc_info=True)

    if not records:
        logger.info("No new ROMs to add (all duplicates)")
        return 0

    texts = [f"{r['title']} {r['abstract']}" for r in records]
    vectors = embedder.embed_batch(texts)

    data_with_vectors = []
    for rec, vec in zip(records, vectors):
        rec["vector"] = vec
        data_with_vectors.append(rec)

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            schema_fields = {f.name for f in table.schema}
            filtered_data = [
                {k: v for k, v in record.items() if k in schema_fields}
                for record in data_with_vectors
            ]
            table.add(filtered_data)
        except Exception:
            logger.error("Failed to add records", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} ROMs")
    return 0


# PURPOSE: trajectorySummaries JSON からセッション情報を LanceDB にインデックスする
def index_from_json(json_path: str) -> int:
    """PURPOSE: trajectorySummaries JSON からセッション情報を LanceDB にインデックスする"""
    path = Path(json_path)
    if not path.exists():
        logger.error(f"File not found: {json_path}")
        return 1

    with open(path) as f:
        data = json.load(f)

    sessions = parse_sessions_from_json(data)
    if not sessions:
        logger.error("No sessions found in JSON")
        return 1

    logger.info(f"Parsed {len(sessions)} sessions")
    records = sessions_to_records(sessions)

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates", exc_info=True)

    if not records:
        logger.info("No new sessions to add (all duplicates)")
        return 0

    BATCH_SIZE = 32
    data_with_vectors = []

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)

        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)

        logger.info(f"Processed {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            table.add(data_with_vectors)
        except Exception:
            logger.error("Failed to add records", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} sessions")
    return 0


# PURPOSE: LS API から直接セッション情報を取得し LanceDB にインデックスする
def index_from_api() -> int:
    """PURPOSE: LS API から直接セッション情報を取得し LanceDB にインデックスする"""
    from mekhane.ochema.antigravity_client import AntigravityClient

    try:
        client = AntigravityClient()
        data = client._rpc(
            "exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories", {}
        )
    except Exception:
        logger.error("Failed to fetch trajectories from API", exc_info=True)
        return 1

    # In-memory processing without writing to file
    sessions = parse_sessions_from_json(data)
    if not sessions:
        logger.info("No sessions found from API")
        return 0

    logger.info(f"Fetched {len(sessions)} sessions from API")
    records = sessions_to_records(sessions)

    # Re-use logic: index_from_json's logic is duplicated here, better refactor?
    # For now, let's keep it inline to avoid further complexity, similar to index_from_json
    # but strictly speaking, we could extract `index_records(records)` function.
    # To minimize changes, I will duplicate the indexing logic block or call a helper if I made one.
    # Since I didn't plan a helper extraction, I will duplicate the block but with logger fixes.

    from mekhane.anamnesis.index import Embedder, GnosisIndex

    index = GnosisIndex()
    embedder = Embedder()

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            existing = table.to_pandas()
            if not existing.empty:
                existing_keys = set(existing["primary_key"].tolist())
                before = len(records)
                records = [r for r in records if r["primary_key"] not in existing_keys]
                skipped = before - len(records)
                if skipped:
                    logger.info(f"Skipped {skipped} duplicates")
        except Exception:
            logger.warning("Failed to check duplicates", exc_info=True)

    if not records:
        logger.info("No new sessions to add (all duplicates)")
        return 0

    BATCH_SIZE = 32
    data_with_vectors = []
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [f"{r['title']} {r['abstract']}" for r in batch]
        vectors = embedder.embed_batch(texts)
        for record, vector in zip(batch, vectors):
            record["vector"] = vector
            data_with_vectors.append(record)
        logger.info(f"Processed {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    if index._table_exists():
        try:
            table = index.db.open_table(index.TABLE_NAME)
            table.add(data_with_vectors)
        except Exception:
            logger.error("Failed to add records", exc_info=True)
            return 1
    else:
        try:
            index.db.create_table(index.TABLE_NAME, data=data_with_vectors)
        except Exception:
            logger.error("Failed to create table", exc_info=True)
            return 1

    logger.info(f"✅ Indexed {len(data_with_vectors)} sessions from API")
    return 0


# PURPOSE: [L2-auto] 関数: main
def main() -> int:  # PURPOSE: CLI エントリポイント — サブコマンド (sessions/handoffs/conversations/steps/exports) をディスパッチする
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
        help="Custom handoff directory",
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
    parser.add_argument(
        "--steps",
        action="store_true",
        help="Index .system_generated/steps/ output files from brain dirs",
    )
    parser.add_argument(
        "--max-steps-per-session",
        type=int,
        default=20,
        help="Max step outputs per session to index (default: 20)",
    )
    parser.add_argument(
        "--exports",
        action="store_true",
        help="Index export_chats.py output MD files",
    )
    parser.add_argument(
        "--export-dir",
        default=None,
        help="Custom export directory",
    )
    parser.add_argument(
        "--roms",
        action="store_true",
        help="Index rom_*.md files from mneme ROM directory",
    )
    parser.add_argument(
        "--rom-dir",
        default=None,
        help="Custom ROM directory",
    )

    args = parser.parse_args()

    if args.exports:
        return index_exports(args.export_dir)
    elif args.roms:
        return index_roms(args.rom_dir)
    elif args.steps:
        return index_steps(max_per_session=args.max_steps_per_session)
    elif args.conversations:
        return index_conversations(args.max_sessions)
    elif args.handoffs:
        return index_handoffs(args.handoff_dir)
    elif args.from_api:
        return index_from_api()
    elif args.json_path:
        return index_from_json(args.json_path)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    if str(_HEGEMONIKON_ROOT) not in sys.path:
        sys.path.insert(0, str(_HEGEMONIKON_ROOT))
    sys.exit(main())
