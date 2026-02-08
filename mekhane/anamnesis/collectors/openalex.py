# PROOF: [L2/インフラ] <- mekhane/anamnesis/collectors/
"""
PROOF: [L2/インフラ]

P3 → 知識収集が必要
   → OpenAlex からの論文収集
   → OpenAlexCollector が担う

Q.E.D.

---

Gnōsis OpenAlex Collector - OpenAlex API経由で論文収集
"""

from typing import Optional

try:
    import requests
except ImportError:
    requests = None

from mekhane.anamnesis.collectors.base import BaseCollector
from mekhane.anamnesis.models.paper import Paper


# PURPOSE: OpenAlex論文コレクター
class OpenAlexCollector(BaseCollector):
    """OpenAlex論文コレクター"""

    name = "openalex"
    rate_limit = 10.0  # 10 requests per second (polite pool)

    BASE_URL = "https://api.openalex.org"

    # PURPOSE: Args:
    def __init__(self, email: Optional[str] = None):
        """
        Args:
            email: メールアドレス（polite poolに入るため推奨）
        """
        super().__init__()
        if requests is None:
            raise ImportError("requests package required: pip install requests")

        self.session = requests.Session()
        self.session.headers["User-Agent"] = (
            "Gnosis/0.1 (Hegemonikon Knowledge Foundation)"
        )

        # メール指定でpolite poolに入る（レート制限緩和）
        self.email = email
        if email:
            self.session.params = {"mailto": email}

    # PURPOSE: API応答 -> Paper 変換
    def _to_paper(self, data: dict) -> Paper:
        """API応答 -> Paper 変換"""
        # IDs
        ids = data.get("ids", {}) or {}
        doi = (
            ids.get("doi", "").replace("https://doi.org/", "")
            if ids.get("doi")
            else None
        )

        # arXiv ID抽出（openalex_idから）
        arxiv_id = None
        openalex_id = data.get("id", "")

        # Authors
        authors = []
        for authorship in data.get("authorships", [])[:10]:
            author = authorship.get("author", {})
            if author.get("display_name"):
                authors.append(author["display_name"])

        # Categories (concepts)
        categories = []
        for concept in data.get("concepts", [])[:5]:
            if concept.get("display_name"):
                categories.append(concept["display_name"])

        # PDF URL (best OA location)
        pdf_url = None
        best_oa = data.get("best_oa_location") or {}
        if best_oa.get("pdf_url"):
            pdf_url = best_oa["pdf_url"]

        # OpenAlex ID
        oa_id = openalex_id.replace("https://openalex.org/", "")

        return Paper(
            id=f"gnosis_openalex_{oa_id}",
            source="openalex",
            source_id=oa_id,
            doi=doi,
            arxiv_id=arxiv_id,
            title=data.get("title") or "",
            authors=authors,
            abstract=self._get_abstract(data),
            published=(
                str(data.get("publication_year"))
                if data.get("publication_year")
                else None
            ),
            url=data.get("id") or "",
            pdf_url=pdf_url,
            citations=data.get("cited_by_count"),
            categories=categories,
            venue=self._get_venue(data),
        )

    # PURPOSE: Abstract inverted index を復元
    def _get_abstract(self, data: dict) -> str:
        """Abstract inverted index を復元"""
        abstract_inverted = data.get("abstract_inverted_index")
        if not abstract_inverted:
            return ""

        # {word: [positions]} -> reconstructed text
        try:
            words = {}
            for word, positions in abstract_inverted.items():
                for pos in positions:
                    words[pos] = word

            return " ".join(words[i] for i in sorted(words.keys()))
        except Exception:
            return ""

    # PURPOSE: Venue/Journal名を取得
    def _get_venue(self, data: dict) -> Optional[str]:
        """Venue/Journal名を取得"""
        primary_location = data.get("primary_location") or {}
        source = primary_location.get("source") or {}
        return source.get("display_name")

    # PURPOSE: OpenAlexで論文検索
    def search(
        self,
        query: str,
        max_results: int = 10,
        categories: Optional[list[str]] = None,
    ) -> list[Paper]:
        """OpenAlexで論文検索"""

        url = f"{self.BASE_URL}/works"
        params = {
            "search": query,
            "per_page": min(max_results, 200),  # API上限200
            "sort": "publication_date:desc",
        }

        # カテゴリフィルタ（OpenAlex concepts使用）
        if categories:
            # concepts.display_name でフィルタ
            params["filter"] = ",".join(
                [f"concepts.display_name:{cat}" for cat in categories]
            )

        self._rate_limit_wait()

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[OpenAlex] Search error: {e}")
            return []

        papers = []
        for item in data.get("results", []):
            try:
                papers.append(self._to_paper(item))
            except Exception:
                continue

        return papers

    # PURPOSE: IDで論文取得
    def fetch_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        IDで論文取得

        paper_id: OpenAlex ID (W...) or DOI
        """
        # DOIの場合はフォーマット
        if paper_id.startswith("10."):
            paper_id = f"https://doi.org/{paper_id}"

        url = f"{self.BASE_URL}/works/{paper_id}"

        self._rate_limit_wait()

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return self._to_paper(response.json())
        except Exception as e:
            print(f"[OpenAlex] Fetch error: {e}")
            return None

    # PURPOSE: 著者IDで論文一覧取得
    def get_works_by_author(self, author_id: str, max_results: int = 50) -> list[Paper]:
        """著者IDで論文一覧取得"""
        url = f"{self.BASE_URL}/works"
        params = {
            "filter": f"author.id:{author_id}",
            "per_page": min(max_results, 200),
            "sort": "publication_date:desc",
        }

        self._rate_limit_wait()

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception:
            return []

        return [self._to_paper(item) for item in data.get("results", [])]
