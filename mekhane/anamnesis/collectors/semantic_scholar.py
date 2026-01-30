"""
PROOF: [L2/インフラ]

P3 → 知識収集が必要
   → Semantic Scholar からの論文収集
   → SemanticScholarCollector が担う

Q.E.D.

---

Gnōsis Semantic Scholar Collector - S2 API経由で論文収集
"""

import os
from typing import Optional
import time

try:
    import requests
except ImportError:
    requests = None

from mekhane.anamnesis.collectors.base import BaseCollector
from mekhane.anamnesis.models.paper import Paper


class SemanticScholarCollector(BaseCollector):
    """Semantic Scholar論文コレクター"""
    
    name = "semantic_scholar"
    rate_limit = 1.0  # 1 request per second (認証なしの制限)
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    PAPER_FIELDS = "paperId,externalIds,title,authors,abstract,year,citationCount,venue,url,openAccessPdf"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        if requests is None:
            raise ImportError("requests package required: pip install requests")
        
        # APIキー取得: 引数 > 環境変数
        self.api_key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["x-api-key"] = self.api_key
            self.rate_limit = 10.0  # 認証済みは10 req/sec
    
    def _to_paper(self, data: dict) -> Paper:
        """API応答 -> Paper 変換"""
        external_ids = data.get("externalIds", {}) or {}
        
        # PDF URL取得
        pdf_url = None
        oa_pdf = data.get("openAccessPdf")
        if oa_pdf and isinstance(oa_pdf, dict):
            pdf_url = oa_pdf.get("url")
        
        return Paper(
            id=f"gnosis_s2_{data['paperId']}",
            source="semantic_scholar",
            source_id=data["paperId"],
            doi=external_ids.get("DOI"),
            arxiv_id=external_ids.get("ArXiv"),
            title=data.get("title", ""),
            authors=[a.get("name", "") for a in data.get("authors", [])],
            abstract=data.get("abstract") or "",
            published=str(data.get("year")) if data.get("year") else None,
            url=data.get("url") or f"https://www.semanticscholar.org/paper/{data['paperId']}",
            pdf_url=pdf_url,
            citations=data.get("citationCount"),
            venue=data.get("venue"),
        )
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[list[str]] = None,  # S2では使用しない
    ) -> list[Paper]:
        """Semantic Scholarで論文検索"""
        
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": min(max_results, 100),  # API上限100
            "fields": self.PAPER_FIELDS,
        }
        
        # 429 リトライ設定
        max_retries = 3
        retry_delay = 2.0  # 初回遅延（秒）
        
        for attempt in range(max_retries + 1):
            self._rate_limit_wait()
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                # 429 の場合はリトライ
                if response.status_code == 429:
                    if attempt < max_retries:
                        wait_time = retry_delay * (2 ** attempt)  # 指数バックオフ
                        print(f"[SemanticScholar] Rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[SemanticScholar] Rate limit exceeded after {max_retries} retries")
                        return []
                
                response.raise_for_status()
                data = response.json()
                break
                
            except Exception as e:
                print(f"[SemanticScholar] Search error: {e}")
                return []
        
        papers = []
        for item in data.get("data", []):
            try:
                papers.append(self._to_paper(item))
            except Exception:
                continue
        
        return papers
    
    def fetch_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        IDで論文取得
        
        paper_id: S2 Paper ID, DOI, arXiv ID など
        """
        url = f"{self.BASE_URL}/paper/{paper_id}"
        params = {"fields": self.PAPER_FIELDS}
        
        self._rate_limit_wait()
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return self._to_paper(response.json())
        except Exception as e:
            print(f"[SemanticScholar] Fetch error: {e}")
            return None
    
    def get_citations(self, paper_id: str, limit: int = 10) -> list[Paper]:
        """論文の被引用論文を取得"""
        url = f"{self.BASE_URL}/paper/{paper_id}/citations"
        params = {
            "limit": limit,
            "fields": self.PAPER_FIELDS,
        }
        
        self._rate_limit_wait()
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception:
            return []
        
        papers = []
        for item in data.get("data", []):
            citing = item.get("citingPaper", {})
            if citing.get("paperId"):
                try:
                    papers.append(self._to_paper(citing))
                except Exception:
                    continue
        
        return papers
