# PROOF: [L3/ユーティリティ] O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
arXiv論文コレクター - AIDB記事からarXivリンクを抽出し、論文DBを構築

Usage:
    python arxiv-collector.py extract       # AIDB記事からarXivリンク抽出
    python arxiv-collector.py fetch         # arXiv APIでメタデータ取得
    python arxiv-collector.py index         # LanceDBへ追加
    python arxiv-collector.py search "query"  # 論文検索
    python arxiv-collector.py stats         # 統計表示

Requires:
    pip install arxiv lancedb onnxruntime tokenizers numpy
"""

import os
import sys
import re
import json
import time
from pathlib import Path
from datetime import datetime

# Paths
ROOT_DIR = Path(__file__).parent.parent / "Raw" / "aidb"
INDEX_DIR = ROOT_DIR / "_index"
ARXIV_LINKS_FILE = INDEX_DIR / "arxiv_links.json"
PAPERS_METADATA_FILE = INDEX_DIR / "papers_metadata.jsonl"
LANCE_DIR = INDEX_DIR / "lancedb"
MODELS_DIR = Path(__file__).parent.parent / "models" / "bge-small"

# arXiv ID pattern: e.g. 2307.12981, 2401.13481v1
ARXIV_PATTERN = re.compile(r'arxiv\.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)', re.IGNORECASE)

# Windows UTF-8 fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class Embedder:
    """ONNX-based text embedding (Self-contained)."""
    
    def __init__(self):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        import numpy as np
        
        self.np = np
        
        model_path = MODELS_DIR / "model.onnx"
        tokenizer_path = MODELS_DIR / "tokenizer.json"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                "Run: python aidb-kb.py setup"
            )
        
        self.session = ort.InferenceSession(str(model_path))
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(length=512)
    
    def embed(self, text: str) -> list:
        encoded = self.tokenizer.encode(text)
        input_ids = self.np.array([encoded.ids], dtype=self.np.int64)
        attention_mask = self.np.array([encoded.attention_mask], dtype=self.np.int64)
        token_type_ids = self.np.zeros_like(input_ids)
        
        outputs = self.session.run(None, {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        })
        
        embeddings = outputs[0]
        mask = attention_mask[:, :, None]
        pooled = (embeddings * mask).sum(axis=1) / mask.sum(axis=1)
        norm = self.np.linalg.norm(pooled, axis=1, keepdims=True)
        normalized = pooled / norm
        
        return normalized[0].tolist()


def extract_arxiv_links():
    """Extract arXiv links from all AIDB markdown files."""
    print("Extracting arXiv links from AIDB articles...")
    
    md_files = list(ROOT_DIR.glob("**/*.md"))
    md_files = [f for f in md_files if "_index" not in str(f)]
    
    links = {}  # arxiv_id -> {source_articles: [], first_seen: ...}
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        matches = ARXIV_PATTERN.findall(content)
        article_id = md_file.stem
        
        for arxiv_id in matches:
            # Normalize: remove version suffix for deduplication
            base_id = arxiv_id.split('v')[0]
            
            if base_id not in links:
                links[base_id] = {
                    "arxiv_id": base_id,
                    "full_id": arxiv_id,
                    "source_articles": [],
                    "first_seen": str(md_file.relative_to(ROOT_DIR))
                }
            
            if article_id not in links[base_id]["source_articles"]:
                links[base_id]["source_articles"].append(article_id)
    
    # Save
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARXIV_LINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Extracted {len(links)} unique arXiv IDs from {len(md_files)} articles")
    print(f"    Saved to: {ARXIV_LINKS_FILE}")
    
    # Show top sources
    top_sources = sorted(links.values(), key=lambda x: len(x["source_articles"]), reverse=True)[:5]
    print("\nTop referenced papers:")
    for p in top_sources:
        print(f"  {p['arxiv_id']}: {len(p['source_articles'])} articles")


def fetch_metadata():
    """Fetch paper metadata from arXiv API."""
    import arxiv
    
    if not ARXIV_LINKS_FILE.exists():
        print("Error: Run 'extract' first to generate arxiv_links.json")
        return
    
    with open(ARXIV_LINKS_FILE, 'r', encoding='utf-8') as f:
        links = json.load(f)
    
    print(f"Fetching metadata for {len(links)} papers...")
    print("(Rate limit: 1 request per 3 seconds)")
    
    client = arxiv.Client()
    papers = []
    
    for i, (arxiv_id, info) in enumerate(links.items()):
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(client.results(search), None)
            
            if result:
                paper = {
                    "arxiv_id": arxiv_id,
                    "title": result.title,
                    "authors": [a.name for a in result.authors],
                    "summary": result.summary.replace('\n', ' '),
                    "categories": list(result.categories),
                    "published": result.published.isoformat() if result.published else None,
                    "updated": result.updated.isoformat() if result.updated else None,
                    "pdf_url": result.pdf_url,
                    "source_articles": info["source_articles"],
                    "fetched_at": datetime.now().isoformat()
                }
                papers.append(paper)
                print(f"[{i+1}/{len(links)}] {arxiv_id}: {result.title[:50]}...")
            else:
                print(f"[{i+1}/{len(links)}] {arxiv_id}: Not found")
        except Exception as e:
            print(f"[{i+1}/{len(links)}] {arxiv_id}: Error - {e}")
        
        # Rate limit: 3 seconds between requests
        if i < len(links) - 1:
            time.sleep(3)
    
    # Save
    with open(PAPERS_METADATA_FILE, 'w', encoding='utf-8') as f:
        for paper in papers:
            f.write(json.dumps(paper, ensure_ascii=False) + '\n')
    
    print(f"\n[OK] Fetched {len(papers)} papers")
    print(f"    Saved to: {PAPERS_METADATA_FILE}")


def build_index():
    """Build LanceDB index from paper metadata."""
    import lancedb
    
    if not PAPERS_METADATA_FILE.exists():
        print("Error: Run 'fetch' first to generate papers_metadata.jsonl")
        return
    
    print("Initializing embedder...")
    embedder = Embedder()
    
    print("Loading paper metadata...")
    papers = []
    with open(PAPERS_METADATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            papers.append(json.loads(line.strip()))
    
    print(f"Generating embeddings for {len(papers)} papers...")
    
    all_data = []
    for i, paper in enumerate(papers):
        # Create embedding text
        embed_text = f"{paper['title']} {paper['summary'][:500]}"
        vector = embedder.embed(embed_text)
        
        all_data.append({
            "id": f"arxiv_{paper['arxiv_id']}",
            "arxiv_id": paper["arxiv_id"],
            "title": paper["title"],
            "authors": ", ".join(paper["authors"][:5]),
            "summary": paper["summary"][:1000],
            "categories": ", ".join(paper["categories"]),
            "published": paper.get("published", ""),
            "pdf_url": paper.get("pdf_url", ""),
            "source_articles": ", ".join(paper.get("source_articles", [])),
            "vector": vector
        })
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(papers)}...")
    
    print("Writing to LanceDB...")
    LANCE_DIR.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(LANCE_DIR))
    
    # Create/overwrite table
    if "arxiv_papers" in db.table_names():
        db.drop_table("arxiv_papers")
    
    table = db.create_table("arxiv_papers", data=all_data)
    
    print(f"\n[OK] Index built successfully!")
    print(f"  Location: {LANCE_DIR}")
    print(f"  Papers: {len(all_data)}")


def search_papers(query: str, n_results: int = 5):
    """Search papers by semantic similarity."""
    import lancedb
    
    if not LANCE_DIR.exists():
        print("Error: Run 'index' first to build the search index")
        return
    
    embedder = Embedder()
    query_vector = embedder.embed(query)
    
    db = lancedb.connect(str(LANCE_DIR))
    
    if "arxiv_papers" not in db.table_names():
        print("Error: Paper index not found. Run 'index' first.")
        return
    
    table = db.open_table("arxiv_papers")
    results = table.search(query_vector).limit(n_results).to_list()
    
    print(f"\n[SEARCH] Query: \"{query}\"\n")
    print("-" * 70)
    
    for i, r in enumerate(results):
        print(f"\n[{i+1}] {r['title'][:70]}")
        print(f"    arXiv: {r['arxiv_id']} | Categories: {r['categories']}")
        print(f"    Authors: {r['authors'][:60]}...")
        print(f"    Summary: {r['summary'][:150]}...")
        print(f"    PDF: {r['pdf_url']}")
    
    print("\n" + "-" * 70)


def show_stats():
    """Show paper database statistics."""
    print("\n[STATS] arXiv Paper Collection")
    print("=" * 40)
    
    # Links
    if ARXIV_LINKS_FILE.exists():
        with open(ARXIV_LINKS_FILE, 'r', encoding='utf-8') as f:
            links = json.load(f)
        print(f"Extracted Links: {len(links)}")
    else:
        print("Extracted Links: (not yet extracted)")
    
    # Metadata
    if PAPERS_METADATA_FILE.exists():
        count = sum(1 for _ in open(PAPERS_METADATA_FILE, 'r', encoding='utf-8'))
        print(f"Fetched Metadata: {count} papers")
    else:
        print("Fetched Metadata: (not yet fetched)")
    
    # Index
    if LANCE_DIR.exists():
        try:
            import lancedb
            db = lancedb.connect(str(LANCE_DIR))
            if "arxiv_papers" in db.table_names():
                table = db.open_table("arxiv_papers")
                print(f"Indexed Papers: {len(table.to_pandas())}")
            else:
                print("Indexed Papers: (not yet indexed)")
        except Exception as e:
            print(f"Index Status: Error - {e}")
    else:
        print("Indexed Papers: (not yet indexed)")
    
    print("=" * 40)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "extract":
        extract_arxiv_links()
    elif command == "fetch":
        fetch_metadata()
    elif command == "index":
        build_index()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python arxiv-collector.py search \"query\"")
            return
        search_papers(" ".join(sys.argv[2:]))
    elif command == "stats":
        show_stats()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
