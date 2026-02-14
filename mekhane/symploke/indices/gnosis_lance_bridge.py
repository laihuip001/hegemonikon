#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/indices/ A0→LanceDB Gnōsis への直接アクセスが必要
"""
Gnōsis LanceDB Bridge — Anamnesis LanceDB を Symplokē DomainIndex として公開

27,432件の論文データを持つ LanceDB を、再エンベッドせずに
Symplokē SearchEngine の gnosis ソースとして使う。

Usage:
    bridge = GnosisLanceBridge()
    engine.register(bridge)  # SearchEngine に登録
    results = engine.search("active inference", sources=["gnosis"])
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

from .base import DomainIndex, SourceType, IndexedResult, Document

# Anamnesis のパス解決
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # hegemonikon/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# PURPOSE: LanceDB Gnōsis を Symplokē DomainIndex として公開するブリッジ
class GnosisLanceBridge(DomainIndex):
    """LanceDB Gnōsis を Symplokē DomainIndex として公開するブリッジ

    Anamnesis の GnosisIndex (LanceDB) を内部で使い、
    Symplokē の DomainIndex インターフェースに変換する。

    特徴:
    - 再エンベッド不要 (LanceDB の既存ベクトルを直接使用)
    - 27,432件の論文データに即座にアクセス
    - adapter は使わず、LanceDB の search API を直接呼ぶ
    """

    # PURPOSE: LanceDB Gnōsis ブリッジの初期化
    def __init__(self, lance_dir: Optional[Path] = None):
        """
        Args:
            lance_dir: LanceDB ディレクトリ (None = デフォルト)
        """
        # DomainIndex.__init__ には adapter が必要だが、
        # このブリッジは adapter を使わないので None を渡す
        super().__init__(adapter=None, name="gnosis", dimension=1024)
        self._lance_dir = lance_dir
        self._lance_index = None
        self._initialized = True  # LanceDB は initialize 不要

    # PURPOSE: [L2-auto] source_type
    @property
    def source_type(self) -> SourceType:
        return SourceType.GNOSIS

    # PURPOSE: LanceDB GnosisIndex を遅延初期化
    def _get_lance_index(self):
        """LanceDB GnosisIndex を遅延初期化"""
        if self._lance_index is None:
            # プロキシ回避
            for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
                os.environ.pop(key, None)
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"

            from mekhane.anamnesis.index import GnosisIndex as AnamnesisGnosisIndex
            self._lance_index = AnamnesisGnosisIndex(lance_dir=self._lance_dir)
        return self._lance_index

    # PURPOSE: LanceDB 検索 → Symplokē IndexedResult 変換
    def search(self, query: str, k: int = 10, **kwargs) -> List[IndexedResult]:
        """LanceDB 検索 → Symplokē IndexedResult 変換"""
        try:
            lance = self._get_lance_index()
            raw_results = lance.search(query, k=k)
        except Exception as e:
            print(f"[GnosisLanceBridge] Search error: {e}", file=sys.stderr)
            return []

        results = []
        for r in raw_results:
            # LanceDB の _distance を 0-1 スコアに変換
            distance = r.get("_distance", float("inf"))
            score = max(0.0, 1.0 - (distance / 2.0))

            results.append(
                IndexedResult(
                    doc_id=r.get("doi", r.get("arxiv_id", str(hash(r.get("title", ""))))),
                    score=score,
                    source=SourceType.GNOSIS,
                    content=r.get("abstract", ""),
                    metadata={
                        "title": r.get("title", "Untitled"),
                        "authors": r.get("authors", ""),
                        "source": r.get("source", "unknown"),
                        "url": r.get("url", ""),
                        "citations": r.get("citations", 0),
                    },
                )
            )

        return results

    # PURPOSE: LanceDB の論文数を返す
    def count(self) -> int:
        """LanceDB の論文数を返す"""
        try:
            lance = self._get_lance_index()
            return lance.stats().get("total_papers", 0)
        except Exception:
            return 0

    # PURPOSE: ブリッジは ingest をサポートしない
    def ingest(self, documents: List[Document]) -> int:
        """ブリッジは ingest をサポートしない (Anamnesis 経由で追加)"""
        raise NotImplementedError(
            "GnosisLanceBridge does not support ingest. "
            "Use Anamnesis GnosisIndex directly."
        )

    # PURPOSE: ブリッジは initialize 不要
    def initialize(self) -> None:
        """ブリッジは initialize 不要 (LanceDB は自己管理)"""
        self._initialized = True

    # PURPOSE: ブリッジは save/load 不要
    def save(self, path: str) -> None:
        pass

    # PURPOSE: [L2-auto] load
    def load(self, path: str) -> None:
        self._initialized = True
