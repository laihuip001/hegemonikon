# PROOF: [L2/Session] <- mekhane/anamnesis/ Session Indexer Implementation
# PURPOSE: セッションインデックスの作成・検索を行う
"""Session Indexer Module."""

from typing import List, Dict, Any, Optional
import os
import json
import re
import time
from pathlib import Path
from dataclasses import dataclass, field

# 内部使用するが外部依存を減らすためローカル定義
@dataclass
class IndexEntry:
    """インデックスエントリ"""
    session_id: str
    timestamp: float
    summary: str
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

class SessionIndexer:
    """セッションインデクサ"""

    def __init__(self, index_dir: str):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, IndexEntry] = {}

    def index_session(self, session_id: str, content: str) -> bool:
        """セッションをインデックスに追加"""
        # 単純な実装: ファイルに保存するだけ
        # 実際には embedding 計算などが入る
        entry = IndexEntry(
            session_id=session_id,
            timestamp=time.time(),
            summary=content[:100] + "...",
            tags=self._extract_tags(content)
        )
        self._cache[session_id] = entry

        # 永続化
        self._save_entry(entry)
        return True

    def search(self, query: str) -> List[Dict[str, Any]]:
        """セッションを検索"""
        results = []
        query_lower = query.lower()

        # メモリ内キャッシュから検索 (単純なキーワードマッチ)
        for entry in self._cache.values():
            if query_lower in entry.summary.lower() or query_lower in str(entry.tags).lower():
                results.append({
                    "id": entry.session_id,
                    "summary": entry.summary,
                    "score": 1.0  # ダミー
                })

        return results

    def _extract_tags(self, content: str) -> List[str]:
        """コンテンツからタグを抽出 (簡易版)"""
        # #tag 形式を抽出
        _RE_TAG = re.compile(r"#(\w+)")
        return _RE_TAG.findall(content)

    def _save_entry(self, entry: IndexEntry):
        """エントリをファイルに保存"""
        path = self.index_dir / f"{entry.session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            data = {
                "session_id": entry.session_id,
                "timestamp": entry.timestamp,
                "summary": entry.summary,
                "tags": entry.tags
            }
            json.dump(data, f, ensure_ascii=False)

    def load_all(self):
        """全インデックスをロード"""
        if not self.index_dir.exists():
            return

        for path in self.index_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    entry = IndexEntry(
                        session_id=data.get("session_id", path.stem),
                        timestamp=data.get("timestamp", 0.0),
                        summary=data.get("summary", ""),
                        tags=data.get("tags", [])
                    )
                    self._cache[entry.session_id] = entry
            except Exception:
                pass  # 壊れたファイルは無視
