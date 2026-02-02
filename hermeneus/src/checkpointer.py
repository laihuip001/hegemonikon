# PROOF: [L2/インフラ] <- hermeneus/src/ 状態永続化 (Checkpointer)
"""
Hermēneus Checkpointer — 実行状態の永続化と復元

SQLite ベースの状態保存により、
長時間実行や HITL ワークフローを可能にする。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager


# =============================================================================
# Checkpoint Types
# =============================================================================

@dataclass
class Checkpoint:
    """チェックポイント"""
    checkpoint_id: str
    thread_id: str
    state: Dict[str, Any]
    created_at: datetime
    parent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CheckpointWrite:
    """チェックポイント書き込みリクエスト"""
    thread_id: str
    state: Dict[str, Any]
    parent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# =============================================================================
# SQLite Checkpointer
# =============================================================================

class CCLCheckpointer:
    """SQLite ベースのチェックポインター
    
    LangGraph の BaseCheckpointSaver 互換インターフェース。
    """
    
    DEFAULT_PATH = Path.home() / ".hermeneus" / "checkpoints" / "state.db"
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or self.DEFAULT_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """データベースを初期化"""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    parent_id TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (parent_id) REFERENCES checkpoints(checkpoint_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_thread_id 
                ON checkpoints(thread_id, created_at DESC)
            """)
            conn.commit()
    
    @contextmanager
    def _connect(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _generate_id(self) -> str:
        """一意の ID を生成"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _serialize_state(self, state: Dict[str, Any]) -> str:
        """状態を JSON にシリアライズ"""
        def default_serializer(obj):
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            elif hasattr(obj, "value"):  # Enum
                return obj.value
            else:
                return str(obj)
        
        return json.dumps(state, default=default_serializer, ensure_ascii=False)
    
    def _deserialize_state(self, state_json: str) -> Dict[str, Any]:
        """JSON から状態をデシリアライズ"""
        return json.loads(state_json)
    
    def put(self, write: CheckpointWrite) -> Checkpoint:
        """チェックポイントを保存"""
        checkpoint_id = self._generate_id()
        created_at = datetime.now()
        
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO checkpoints 
                (checkpoint_id, thread_id, state, parent_id, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                checkpoint_id,
                write.thread_id,
                self._serialize_state(write.state),
                write.parent_id,
                json.dumps(write.metadata) if write.metadata else None,
                created_at.isoformat()
            ))
            conn.commit()
        
        return Checkpoint(
            checkpoint_id=checkpoint_id,
            thread_id=write.thread_id,
            state=write.state,
            created_at=created_at,
            parent_id=write.parent_id,
            metadata=write.metadata
        )
    
    def get(self, thread_id: str, checkpoint_id: Optional[str] = None) -> Optional[Checkpoint]:
        """チェックポイントを取得"""
        with self._connect() as conn:
            if checkpoint_id:
                row = conn.execute("""
                    SELECT * FROM checkpoints 
                    WHERE thread_id = ? AND checkpoint_id = ?
                """, (thread_id, checkpoint_id)).fetchone()
            else:
                # 最新のチェックポイントを取得
                row = conn.execute("""
                    SELECT * FROM checkpoints 
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (thread_id,)).fetchone()
            
            if row:
                return Checkpoint(
                    checkpoint_id=row["checkpoint_id"],
                    thread_id=row["thread_id"],
                    state=self._deserialize_state(row["state"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    parent_id=row["parent_id"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
            return None
    
    def list(
        self,
        thread_id: str,
        limit: int = 10,
        before: Optional[str] = None
    ) -> List[Checkpoint]:
        """チェックポイント履歴を取得"""
        with self._connect() as conn:
            if before:
                rows = conn.execute("""
                    SELECT * FROM checkpoints 
                    WHERE thread_id = ? AND created_at < (
                        SELECT created_at FROM checkpoints WHERE checkpoint_id = ?
                    )
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (thread_id, before, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM checkpoints 
                    WHERE thread_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (thread_id, limit)).fetchall()
            
            return [
                Checkpoint(
                    checkpoint_id=row["checkpoint_id"],
                    thread_id=row["thread_id"],
                    state=self._deserialize_state(row["state"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    parent_id=row["parent_id"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]
    
    def delete(self, thread_id: str, checkpoint_id: Optional[str] = None):
        """チェックポイントを削除"""
        with self._connect() as conn:
            if checkpoint_id:
                conn.execute("""
                    DELETE FROM checkpoints 
                    WHERE thread_id = ? AND checkpoint_id = ?
                """, (thread_id, checkpoint_id))
            else:
                # スレッドの全チェックポイントを削除
                conn.execute("""
                    DELETE FROM checkpoints WHERE thread_id = ?
                """, (thread_id,))
            conn.commit()
    
    def get_tuple(self, config: Dict[str, Any]) -> Optional[Tuple]:
        """LangGraph 互換: チェックポイントをタプルで取得"""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None
        
        checkpoint = self.get(thread_id)
        if checkpoint:
            return (checkpoint.state, {"checkpoint_id": checkpoint.checkpoint_id})
        return None
    
    def put_tuple(self, config: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph 互換: チェックポイントを保存"""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id is required in config")
        
        parent_id = config.get("configurable", {}).get("checkpoint_id")
        
        checkpoint = self.put(CheckpointWrite(
            thread_id=thread_id,
            state=state,
            parent_id=parent_id
        ))
        
        return {"checkpoint_id": checkpoint.checkpoint_id}


# =============================================================================
# Memory Checkpointer (テスト用)
# =============================================================================

class MemoryCheckpointer:
    """メモリベースのチェックポインター (テスト用)"""
    
    def __init__(self):
        self._storage: Dict[str, List[Checkpoint]] = {}
        self._counter = 0
    
    def _generate_id(self) -> str:
        self._counter += 1
        return f"mem_{self._counter:04d}"
    
    def put(self, write: CheckpointWrite) -> Checkpoint:
        checkpoint_id = self._generate_id()
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            thread_id=write.thread_id,
            state=write.state.copy(),
            created_at=datetime.now(),
            parent_id=write.parent_id,
            metadata=write.metadata
        )
        
        if write.thread_id not in self._storage:
            self._storage[write.thread_id] = []
        self._storage[write.thread_id].append(checkpoint)
        
        return checkpoint
    
    def get(self, thread_id: str, checkpoint_id: Optional[str] = None) -> Optional[Checkpoint]:
        if thread_id not in self._storage:
            return None
        
        checkpoints = self._storage[thread_id]
        if not checkpoints:
            return None
        
        if checkpoint_id:
            for cp in checkpoints:
                if cp.checkpoint_id == checkpoint_id:
                    return cp
            return None
        
        return checkpoints[-1]  # 最新
    
    def list(self, thread_id: str, limit: int = 10, before: Optional[str] = None) -> List[Checkpoint]:
        if thread_id not in self._storage:
            return []
        
        checkpoints = self._storage[thread_id][::-1]  # 新しい順
        
        if before:
            idx = next((i for i, cp in enumerate(checkpoints) if cp.checkpoint_id == before), -1)
            if idx >= 0:
                checkpoints = checkpoints[idx + 1:]
        
        return checkpoints[:limit]
    
    def delete(self, thread_id: str, checkpoint_id: Optional[str] = None):
        if thread_id not in self._storage:
            return
        
        if checkpoint_id:
            self._storage[thread_id] = [
                cp for cp in self._storage[thread_id]
                if cp.checkpoint_id != checkpoint_id
            ]
        else:
            del self._storage[thread_id]


# =============================================================================
# Convenience Functions
# =============================================================================

def save_state(
    thread_id: str,
    state: Dict[str, Any],
    db_path: Optional[Path] = None
) -> Checkpoint:
    """状態を保存 (便利関数)
    
    Example:
        >>> save_state("session-001", {"context": "分析中", "results": []})
    """
    checkpointer = CCLCheckpointer(db_path)
    return checkpointer.put(CheckpointWrite(thread_id=thread_id, state=state))


def load_state(
    thread_id: str,
    checkpoint_id: Optional[str] = None,
    db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """状態を読み込み (便利関数)
    
    Example:
        >>> state = load_state("session-001")
    """
    checkpointer = CCLCheckpointer(db_path)
    checkpoint = checkpointer.get(thread_id, checkpoint_id)
    return checkpoint.state if checkpoint else None


def list_checkpoints(
    thread_id: str,
    limit: int = 10,
    db_path: Optional[Path] = None
) -> List[Checkpoint]:
    """チェックポイント履歴を取得 (便利関数)"""
    checkpointer = CCLCheckpointer(db_path)
    return checkpointer.list(thread_id, limit)
