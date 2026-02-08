# PROOF: [L2/インフラ] <- mekhane/anamnesis/models/
"""
PROOF: [L2/インフラ]

P3 → 知識収集が必要
   → 異なるソースの統一スキーマ
   → Paper model が担う

Q.E.D.

---

Gnōsis Paper Model - 統一論文スキーマ

全コレクターはこのスキーマに正規化する。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
# PURPOSE: 統一論文スキーマ
class Paper:
    """統一論文スキーマ"""
    
    # Identity
    id: str                          # gnosis_{source}_{source_id}
    source: str                      # arxiv, semantic_scholar, openalex
    source_id: str                   # ソース固有ID
    
    # Deduplication keys
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    
    # Core metadata
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    published: Optional[str] = None  # ISO 8601
    
    # URLs
    url: str = ""
    pdf_url: Optional[str] = None
    
    # Extended metadata
    citations: Optional[int] = None
    categories: list[str] = field(default_factory=list)
    venue: Optional[str] = None
    
    # Gnōsis metadata
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    # PURPOSE: 重複排除用プライマリキー (DOI > arXiv ID > source:id)
    def primary_key(self) -> str:
        """重複排除用プライマリキー (DOI > arXiv ID > source:id)"""
        if self.doi:
            return f"doi:{self.doi}"
        if self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        return f"{self.source}:{self.source_id}"
    
    @property
    # PURPOSE: 埋め込み生成用テキスト
    def embedding_text(self) -> str:
        """埋め込み生成用テキスト"""
        return f"{self.title} {self.abstract[:1000]}"
    
    # PURPOSE: LanceDB保存用辞書
    def to_dict(self) -> dict:
        """LanceDB保存用辞書"""
        return {
            "id": self.id,
            "primary_key": self.primary_key,
            "source": self.source,
            "source_id": self.source_id,
            "doi": self.doi or "",
            "arxiv_id": self.arxiv_id or "",
            "title": self.title,
            "authors": ", ".join(self.authors[:10]),
            "abstract": self.abstract[:2000],
            "published": self.published or "",
            "url": self.url,
            "pdf_url": self.pdf_url or "",
            "citations": self.citations or 0,
            "categories": ", ".join(self.categories),
            "venue": self.venue or "",
            "collected_at": self.collected_at,
        }
    
    @classmethod
    # PURPOSE: 辞書から復元
    def from_dict(cls, data: dict) -> "Paper":
        """辞書から復元"""
        return cls(
            id=data["id"],
            source=data["source"],
            source_id=data["source_id"],
            doi=data.get("doi") or None,
            arxiv_id=data.get("arxiv_id") or None,
            title=data["title"],
            authors=data.get("authors", "").split(", ") if data.get("authors") else [],
            abstract=data.get("abstract", ""),
            published=data.get("published") or None,
            url=data.get("url", ""),
            pdf_url=data.get("pdf_url") or None,
            citations=data.get("citations") or None,
            categories=data.get("categories", "").split(", ") if data.get("categories") else [],
            venue=data.get("venue") or None,
# PURPOSE: 同一primary_keyの論文をマージ。
            collected_at=data.get("collected_at", datetime.now().isoformat()),
        )


def merge_papers(existing: Paper, new: Paper) -> Paper:
    """
    同一primary_keyの論文をマージ。
    新しい情報で既存を更新（citations等）。
    """
    return Paper(
        id=existing.id,  # 既存IDを維持
        source=existing.source,
        source_id=existing.source_id,
        doi=existing.doi or new.doi,
        arxiv_id=existing.arxiv_id or new.arxiv_id,
        title=existing.title or new.title,
        authors=existing.authors or new.authors,
        abstract=existing.abstract or new.abstract,
        published=existing.published or new.published,
        url=existing.url or new.url,
        pdf_url=existing.pdf_url or new.pdf_url,
        citations=new.citations if new.citations else existing.citations,  # 新しい方を優先
        categories=list(set(existing.categories + new.categories)),
        venue=existing.venue or new.venue,
        collected_at=existing.collected_at,  # 最初の収集日時を維持
    )
