# PROOF: [L2/インフラ] 検証履歴永続化 (Audit Trail)
"""
Hermēneus Audit — 検証履歴の記録と追跡

すべての検証結果を SQLite に永続化し、
監査証跡 (Audit Trail) を提供する。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager


# =============================================================================
# Audit Types
# =============================================================================

@dataclass
class AuditRecord:
    """監査レコード"""
    record_id: str
    ccl_expression: str
    execution_result: str
    debate_summary: str
    consensus_accepted: bool
    confidence: float
    dissent_reasons: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditStats:
    """監査統計"""
    total_records: int
    accepted_count: int
    rejected_count: int
    avg_confidence: float
    period_start: datetime
    period_end: datetime


# =============================================================================
# Audit Store
# =============================================================================

class AuditStore:
    """監査ストア
    
    検証履歴を SQLite に永続化する。
    """
    
    DEFAULT_PATH = Path.home() / ".hermeneus" / "audit" / "audit.db"
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or self.DEFAULT_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """データベースを初期化"""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audits (
                    record_id TEXT PRIMARY KEY,
                    ccl_expression TEXT NOT NULL,
                    execution_result TEXT NOT NULL,
                    debate_summary TEXT,
                    consensus_accepted INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    dissent_reasons TEXT,
                    metadata TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON audits(timestamp DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ccl 
                ON audits(ccl_expression)
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
        return f"audit_{uuid.uuid4().hex[:12]}"
    
    def record(self, audit: AuditRecord) -> str:
        """監査レコードを記録"""
        if not audit.record_id:
            audit.record_id = self._generate_id()
        
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO audits 
                (record_id, ccl_expression, execution_result, debate_summary,
                 consensus_accepted, confidence, dissent_reasons, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit.record_id,
                audit.ccl_expression,
                audit.execution_result,
                audit.debate_summary,
                1 if audit.consensus_accepted else 0,
                audit.confidence,
                json.dumps(audit.dissent_reasons, ensure_ascii=False),
                json.dumps(audit.metadata, ensure_ascii=False) if audit.metadata else None,
                audit.timestamp.isoformat()
            ))
            conn.commit()
        
        return audit.record_id
    
    async def record_async(self, audit: AuditRecord) -> str:
        """監査レコードを非同期に記録"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.record, audit)

    def get(self, record_id: str) -> Optional[AuditRecord]:
        """レコードを取得"""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM audits WHERE record_id = ?",
                (record_id,)
            ).fetchone()
            
            if row:
                return self._row_to_record(row)
            return None
    
    def query(
        self,
        ccl_pattern: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        accepted_only: Optional[bool] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditRecord]:
        """レコードをクエリ"""
        conditions = []
        params = []
        
        if ccl_pattern:
            conditions.append("ccl_expression LIKE ?")
            params.append(f"%{ccl_pattern}%")
        
        if min_confidence is not None:
            conditions.append("confidence >= ?")
            params.append(min_confidence)
        
        if max_confidence is not None:
            conditions.append("confidence <= ?")
            params.append(max_confidence)
        
        if accepted_only is not None:
            conditions.append("consensus_accepted = ?")
            params.append(1 if accepted_only else 0)
        
        if since:
            conditions.append("timestamp >= ?")
            params.append(since.isoformat())
        
        if until:
            conditions.append("timestamp <= ?")
            params.append(until.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._connect() as conn:
            rows = conn.execute(f"""
                SELECT * FROM audits 
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """, (*params, limit)).fetchall()
            
            return [self._row_to_record(row) for row in rows]
    
    def get_stats(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> AuditStats:
        """統計を取得"""
        conditions = []
        params = []
        
        if since:
            conditions.append("timestamp >= ?")
            params.append(since.isoformat())
        else:
            since = datetime.min
        
        if until:
            conditions.append("timestamp <= ?")
            params.append(until.isoformat())
        else:
            until = datetime.now()
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        with self._connect() as conn:
            row = conn.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN consensus_accepted = 1 THEN 1 ELSE 0 END) as accepted,
                    SUM(CASE WHEN consensus_accepted = 0 THEN 1 ELSE 0 END) as rejected,
                    AVG(confidence) as avg_conf
                FROM audits
                WHERE {where_clause}
            """, params).fetchone()
            
            return AuditStats(
                total_records=row["total"] or 0,
                accepted_count=row["accepted"] or 0,
                rejected_count=row["rejected"] or 0,
                avg_confidence=row["avg_conf"] or 0.0,
                period_start=since,
                period_end=until
            )
    
    def delete(self, record_id: str):
        """レコードを削除"""
        with self._connect() as conn:
            conn.execute("DELETE FROM audits WHERE record_id = ?", (record_id,))
            conn.commit()
    
    def clear_before(self, before: datetime):
        """指定日時より前のレコードを削除"""
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM audits WHERE timestamp < ?",
                (before.isoformat(),)
            )
            conn.commit()
    
    def _row_to_record(self, row) -> AuditRecord:
        """行をレコードに変換"""
        return AuditRecord(
            record_id=row["record_id"],
            ccl_expression=row["ccl_expression"],
            execution_result=row["execution_result"],
            debate_summary=row["debate_summary"] or "",
            consensus_accepted=bool(row["consensus_accepted"]),
            confidence=row["confidence"],
            dissent_reasons=json.loads(row["dissent_reasons"]) if row["dissent_reasons"] else [],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {}
        )


# =============================================================================
# Report Generator
# =============================================================================

class AuditReporter:
    """監査レポート生成器"""
    
    def __init__(self, store: AuditStore):
        self.store = store
    
    def generate_summary(
        self,
        period: str = "last_7_days"
    ) -> str:
        """サマリーレポートを生成"""
        since = self._parse_period(period)
        stats = self.store.get_stats(since=since)
        
        if stats.total_records == 0:
            return f"期間 ({period}) に監査レコードがありません。"
        
        acceptance_rate = stats.accepted_count / stats.total_records * 100
        
        report = f"""
# 監査サマリーレポート

**期間**: {stats.period_start.strftime('%Y-%m-%d')} ～ {stats.period_end.strftime('%Y-%m-%d')}

## 統計

| 指標 | 値 |
|:-----|:---|
| 総レコード数 | {stats.total_records} |
| 受理件数 | {stats.accepted_count} |
| 拒否件数 | {stats.rejected_count} |
| 受理率 | {acceptance_rate:.1f}% |
| 平均確信度 | {stats.avg_confidence:.2%} |
"""
        return report.strip()
    
    def generate_detail(
        self,
        limit: int = 10,
        period: str = "last_7_days"
    ) -> str:
        """詳細レポートを生成"""
        since = self._parse_period(period)
        records = self.store.query(since=since, limit=limit)
        
        if not records:
            return "レコードがありません。"
        
        lines = ["# 監査詳細レポート\n"]
        
        for i, rec in enumerate(records, 1):
            status = "✅ ACCEPT" if rec.consensus_accepted else "❌ REJECT"
            lines.append(f"""
## {i}. {rec.record_id}

- **CCL**: `{rec.ccl_expression}`
- **判定**: {status}
- **確信度**: {rec.confidence:.2%}
- **時刻**: {rec.timestamp.strftime('%Y-%m-%d %H:%M')}
""")
            if rec.dissent_reasons:
                lines.append("- **反対意見**:")
                for reason in rec.dissent_reasons:
                    lines.append(f"  - {reason}")
        
        return "\n".join(lines)
    
    def _parse_period(self, period: str) -> datetime:
        """期間文字列をパース"""
        now = datetime.now()
        
        if period == "today":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "last_24h":
            return now - timedelta(hours=24)
        elif period == "last_7_days":
            return now - timedelta(days=7)
        elif period == "last_30_days":
            return now - timedelta(days=30)
        elif period == "all":
            return datetime.min
        else:
            return now - timedelta(days=7)


# =============================================================================
# Integration with Verifier
# =============================================================================

def record_verification(
    ccl: str,
    execution_result: str,
    consensus_result: Any,  # ConsensusResult from verifier
    db_path: Optional[Path] = None
) -> str:
    """検証結果を記録 (便利関数)
    
    Example:
        >>> from hermeneus.src import verify_execution, record_verification
        >>> result = verify_execution("/noe+", "分析結果")
        >>> audit_id = record_verification("/noe+", "分析結果", result)
    """
    store = AuditStore(db_path)
    
    # ディベートサマリーを作成
    debate_summary = f"ラウンド数: {len(consensus_result.rounds)}, "
    debate_summary += f"多数派比率: {consensus_result.majority_ratio:.2%}"
    
    record = AuditRecord(
        record_id="",  # 自動生成
        ccl_expression=ccl,
        execution_result=execution_result[:500],  # 切り詰め
        debate_summary=debate_summary,
        consensus_accepted=consensus_result.accepted,
        confidence=consensus_result.confidence,
        dissent_reasons=consensus_result.dissent_reasons[:5],
        metadata={
            "verdict_type": consensus_result.verdict.type.value,
            "verdict_reasoning": consensus_result.verdict.reasoning[:200]
        }
    )
    
    return store.record(record)


async def record_verification_async(
    ccl: str,
    execution_result: str,
    consensus_result: Any,  # ConsensusResult from verifier
    db_path: Optional[Path] = None
) -> str:
    """検証結果を非同期に記録 (便利関数)"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        record_verification,
        ccl,
        execution_result,
        consensus_result,
        db_path
    )


def query_audits(
    ccl_pattern: Optional[str] = None,
    min_confidence: Optional[float] = None,
    period: str = "last_7_days",
    limit: int = 100,
    db_path: Optional[Path] = None
) -> List[AuditRecord]:
    """監査レコードをクエリ (便利関数)"""
    store = AuditStore(db_path)
    reporter = AuditReporter(store)
    since = reporter._parse_period(period)
    
    return store.query(
        ccl_pattern=ccl_pattern,
        min_confidence=min_confidence,
        since=since,
        limit=limit
    )


def get_audit_report(
    period: str = "last_7_days",
    db_path: Optional[Path] = None
) -> str:
    """監査レポートを取得 (便利関数)"""
    store = AuditStore(db_path)
    reporter = AuditReporter(store)
    return reporter.generate_summary(period)
