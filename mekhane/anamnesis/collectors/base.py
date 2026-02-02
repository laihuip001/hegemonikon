# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/anamnesis/collectors/
"""
PROOF: [L2/インフラ]

P3 → 知識収集が必要
   → 複数ソースへの共通インタフェース
   → BaseCollector が担う

Q.E.D.

---

Gnōsis Base Collector - コレクター共通インタフェース
"""

from abc import ABC, abstractmethod
from typing import Optional
import time
import asyncio

from mekhane.anamnesis.models.paper import Paper


class BaseCollector(ABC):
    """論文コレクター基底クラス"""

    name: str = "base"
    rate_limit: float = 1.0  # requests per second

    def __init__(self):
        self._last_request_time: float = 0

    def _calculate_wait_time(self) -> float:
        """待機時間を計算"""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                return min_interval - elapsed
        return 0.0

    def _rate_limit_wait(self):
        """レート制限準拠のための待機"""
        wait_time = self._calculate_wait_time()
        if wait_time > 0:
            time.sleep(wait_time)
        self._last_request_time = time.time()

    async def _rate_limit_wait_async(self):
        """レート制限準拠のための待機 (非同期)"""
        wait_time = self._calculate_wait_time()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._last_request_time = time.time()

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[list[str]] = None,
    ) -> list[Paper]:
        """
        クエリで論文検索

        Args:
            query: 検索クエリ
            max_results: 最大取得件数
            categories: カテゴリフィルタ（オプション）

        Returns:
            Paper オブジェクトのリスト
        """
        pass

    @abstractmethod
    def fetch_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        IDで論文取得

        Args:
            paper_id: ソース固有ID

        Returns:
            Paper オブジェクト or None
        """
        pass

    def collect(
        self,
        query: str,
        max_results: int = 10,
        **kwargs,
    ) -> list[Paper]:
        """
        論文収集（レート制限付き）

        標準的な収集フロー。サブクラスでオーバーライド可能。
        """
        self._rate_limit_wait()
        return self.search(query, max_results, **kwargs)
