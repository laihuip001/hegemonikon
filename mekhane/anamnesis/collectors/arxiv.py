"""
Gnōsis arXiv Collector - arXiv API経由で論文収集
"""

import re
from typing import Optional
from datetime import datetime

try:
    import arxiv
except ImportError:
    arxiv = None

from mekhane.anamnesis.collectors.base import BaseCollector
from mekhane.anamnesis.models.paper import Paper


class ArxivCollector(BaseCollector):
    """arXiv論文コレクター"""
    
    name = "arxiv"
    rate_limit = 3.0  # 3 requests per second
    
    # arXiv ID pattern
    ARXIV_PATTERN = re.compile(r'(\d{4}\.\d{4,5})(v\d+)?')
    
    def __init__(self):
        super().__init__()
        if arxiv is None:
            raise ImportError("arxiv package required: pip install arxiv")
        self.client = arxiv.Client()
    
    def _parse_arxiv_id(self, entry_id: str) -> str:
        """arXiv URLからIDを抽出"""
        # http://arxiv.org/abs/2401.12345v1 -> 2401.12345
        match = self.ARXIV_PATTERN.search(entry_id)
        if match:
            return match.group(1)
        return entry_id.split("/")[-1]
    
    def _to_paper(self, result: "arxiv.Result") -> Paper:
        """arxiv.Result -> Paper 変換"""
        arxiv_id = self._parse_arxiv_id(result.entry_id)
        
        return Paper(
            id=f"gnosis_arxiv_{arxiv_id}",
            source="arxiv",
            source_id=arxiv_id,
            arxiv_id=arxiv_id,
            doi=result.doi,
            title=result.title.replace("\n", " "),
            authors=[a.name for a in result.authors],
            abstract=result.summary.replace("\n", " "),
            published=result.published.isoformat() if result.published else None,
            url=result.entry_id,
            pdf_url=result.pdf_url,
            categories=list(result.categories),
        )
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[list[str]] = None,
    ) -> list[Paper]:
        """arXivで論文検索"""
        
        # カテゴリ指定があればクエリに追加
        search_query = query
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            search_query = f"({query}) AND ({cat_query})"
        
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        papers = []
        for result in self.client.results(search):
            self._rate_limit_wait()
            papers.append(self._to_paper(result))
        
        return papers
    
    def fetch_by_id(self, paper_id: str) -> Optional[Paper]:
        """arXiv IDで論文取得"""
        # IDの正規化（versionを除去）
        base_id = paper_id.split("v")[0]
        
        search = arxiv.Search(id_list=[base_id])
        
        try:
            result = next(self.client.results(search), None)
            if result:
                return self._to_paper(result)
        except Exception:
            pass
        
        return None
    
    def search_recent(
        self,
        categories: list[str],
        days: int = 7,
        max_results: int = 100,
    ) -> list[Paper]:
        """指定カテゴリの最新論文を取得"""
        # 日付範囲クエリ
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        
        search = arxiv.Search(
            query=cat_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        papers = []
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for result in self.client.results(search):
            self._rate_limit_wait()
            if result.published and result.published.timestamp() < cutoff:
                break
            papers.append(self._to_paper(result))
        
        return papers
