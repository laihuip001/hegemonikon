# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
AIDB Knowledge Base - LanceDB + ONNX Runtime Edition
=====================================================

Based on Perplexity research (2026-01-19):
- LanceDB: Python 3.14 compatible, wheel distribution
- ONNX Runtime: Direct embedding without fastEmbed

Usage:
    python aidb-kb.py setup             # Download ONNX model
    python aidb-kb.py index             # Build/rebuild the index
    python aidb-kb.py search "query"    # Semantic search
    python aidb-kb.py show <id>         # Show article content
    python aidb-kb.py stats             # Show KB statistics

Requirements:
    pip install lancedb onnxruntime tokenizers numpy
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from mekhane.anamnesis.lancedb_compat import get_table_names

# Paths
ROOT_DIR = Path(__file__).parent.parent / "Raw" / "aidb"
LANCE_DIR = ROOT_DIR / "_index" / "lancedb"
MANIFEST_FILE = ROOT_DIR / "_index" / "manifest.jsonl"
MODELS_DIR = Path(__file__).parent.parent / "models" / "bge-small"

# Embedding config
EMBEDDING_DIM = 384  # BGE-small dimension


# PURPOSE: Check if required packages are installed.
def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        import lancedb
    except ImportError:
        missing.append("lancedb")
    try:
        import onnxruntime
    except ImportError:
        missing.append("onnxruntime")
    try:
        from tokenizers import Tokenizer
    except ImportError:
        missing.append("tokenizers")
    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        return False
    return True


# PURPOSE: Download ONNX embedding model.
def setup_model():
    """Download ONNX embedding model."""
    import urllib.request

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    if (MODELS_DIR / "model.onnx").exists() and (
        MODELS_DIR / "tokenizer.json"
    ).exists():
        print("Model already exists.")
        return

    print("Downloading BGE-small ONNX model...")

    # Correct HuggingFace paths for Xenova/bge-small-en-v1.5
    files = {
        "model.onnx": "https://huggingface.co/Xenova/bge-small-en-v1.5/resolve/main/onnx/model.onnx",
        "tokenizer.json": "https://huggingface.co/Xenova/bge-small-en-v1.5/resolve/main/tokenizer.json",
    }

    for filename, url in files.items():
        dest = MODELS_DIR / filename
        if dest.exists():
            print(f"  {filename} already exists, skipping.")
            continue
        print(f"  Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  [OK] {filename} downloaded.")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Please manually download from: {url}")
            return

    print("[OK] Model downloaded successfully!")


# PURPOSE: ONNX-based text embedding.
class Embedder:
    """ONNX-based text embedding."""

    # PURPOSE: Embedder の構成と依存関係の初期化
    def __init__(self):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        import numpy as np

        self.np = np

        model_path = MODELS_DIR / "model.onnx"
        tokenizer_path = MODELS_DIR / "tokenizer.json"

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n" "Run: python aidb-kb.py setup"
            )

        self.session = ort.InferenceSession(str(model_path))
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(length=512)

    # PURPOSE: Generate embedding for text.
    def embed(self, text: str) -> list:
        """Generate embedding for text."""
        # Tokenize
        encoded = self.tokenizer.encode(text)

        # Prepare inputs
        input_ids = self.np.array([encoded.ids], dtype=self.np.int64)
        attention_mask = self.np.array([encoded.attention_mask], dtype=self.np.int64)
        token_type_ids = self.np.zeros_like(input_ids)

        # Run inference
        outputs = self.session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        # Mean pooling over tokens
        embeddings = outputs[0]  # (1, seq_len, hidden_dim)
        mask = attention_mask[:, :, None]
        pooled = (embeddings * mask).sum(axis=1) / mask.sum(axis=1)

        # Normalize
        norm = self.np.linalg.norm(pooled, axis=1, keepdims=True)
        normalized = pooled / norm

        return normalized[0].tolist()

    # PURPOSE: Embed multiple texts.
    def embed_batch(self, texts: list[str]) -> list[list]:
        """Embed multiple texts."""
# PURPOSE: Extract frontmatter and body from markdown.
        return [self.embed(t) for t in texts]


# PURPOSE: frontmatter を解析する
def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract frontmatter and body from markdown."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"')

# PURPOSE: Split article into semantic chunks.
    return frontmatter, parts[2].strip()


# PURPOSE: aidb-kb の chunk article 処理を実行する
def chunk_article(article_id: str, content: str, meta: dict) -> list[dict]:
    """Split article into semantic chunks."""
    _, body = parse_frontmatter(content)

    # Split by H2 headers
    sections = re.split(r"\n## ", body)
    chunks = []

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        if i == 0:
            chunk_text = section.strip()
            chunk_title = meta.get("title", article_id)
        else:
            lines = section.split("\n", 1)
            chunk_title = lines[0].strip()
            chunk_text = lines[1].strip() if len(lines) > 1 else ""

        if len(chunk_text) < 50:
            continue

        chunk_id = f"{article_id}_{i}"
        chunks.append(
            {
                "id": chunk_id,
                "article_id": article_id,
                "title": meta.get("title", "")[:200],
                "section": chunk_title[:100],
                "text": chunk_text[:1500],
                "url": meta.get("source_url", ""),
                "date": meta.get("publish_date", ""),
            }
        )

# PURPOSE: Build LanceDB index from markdown files.
    return chunks


# PURPOSE: index を構築する
def build_index():
    """Build LanceDB index from markdown files."""
    if not check_dependencies():
        return

    import lancedb
    import pyarrow as pa

    print("Initializing embedder...")
    embedder = Embedder()

    print("Connecting to LanceDB...")
    LANCE_DIR.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(LANCE_DIR))

    # Find markdown files
    md_files = list(ROOT_DIR.glob("**/*.md"))
    md_files = [f for f in md_files if "_index" not in str(f)]

    print(f"Found {len(md_files)} markdown files.")

    all_data = []

    for i, md_file in enumerate(md_files):
        article_id = md_file.stem

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        meta, _ = parse_frontmatter(content)
        chunks = chunk_article(article_id, content, meta)

        for chunk in chunks:
            # Generate embedding
            embed_text = f"{chunk['title']} {chunk['section']} {chunk['text']}"
            vector = embedder.embed(embed_text)

            all_data.append(
                {
                    "id": chunk["id"],
                    "article_id": chunk["article_id"],
                    "title": chunk["title"],
                    "section": chunk["section"],
                    "text": chunk["text"],
                    "url": chunk["url"],
                    "date": chunk["date"],
                    "vector": vector,
                }
            )

        if (i + 1) % 50 == 0:
            print(
                f"Processed {i + 1}/{len(md_files)} files ({len(all_data)} chunks)..."
            )

    print(f"\nTotal chunks: {len(all_data)}")
    print("Writing to LanceDB...")

    # Create/overwrite table
    if "aidb" in get_table_names(db):
        db.drop_table("aidb")

    table = db.create_table("aidb", data=all_data)

    print(f"\n[OK] Index built successfully!")
    print(f"  Location: {LANCE_DIR}")
    print(f"  Articles: {len(md_files)}")
# PURPOSE: Semantic search.
    print(f"  Chunks: {len(all_data)}")


# PURPOSE: aidb-kb の search 処理を実行する
def search(query: str, n_results: int = 5):
    """Semantic search."""
    if not check_dependencies():
        return

    import lancedb

    if not LANCE_DIR.exists():
        print("Error: Index not found. Run 'python aidb-kb.py index' first.")
        return

    embedder = Embedder()
    query_vector = embedder.embed(query)

    db = lancedb.connect(str(LANCE_DIR))
    table = db.open_table("aidb")

    results = table.search(query_vector).limit(n_results * 2).to_list()

    print(f'\n[SEARCH] Query: "{query}"\n')
    print("-" * 60)

    seen_articles = set()
    count = 0

    for r in results:
        article_id = r["article_id"]
        if article_id in seen_articles:
            continue
        seen_articles.add(article_id)
        count += 1

        if count > n_results:
            break

        print(f"\n[{count}] {r['title'][:70]}")
        print(f"    ID: {article_id} | Date: {r['date']}")
        print(f"    Section: {r['section'][:50]}")
        print(f"    URL: {r['url']}")
        print(f"    Snippet: {r['text'][:150]}...")

# PURPOSE: Show full article content.
    print("\n" + "-" * 60)


# PURPOSE: aidb-kb の show article 処理を実行する
def show_article(article_id: str):
    """Show full article content."""
    matches = list(ROOT_DIR.glob(f"**/{article_id}.md"))

    if not matches:
        print(f"Error: Article '{article_id}' not found.")
        return

    with open(matches[0], "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = parse_frontmatter(content)

    print(f"\n{'='*60}")
    print(f"Title: {meta.get('title', 'Unknown')}")
    print(f"Date: {meta.get('publish_date', 'Unknown')}")
    print(f"URL: {meta.get('source_url', 'Unknown')}")
    print(f"{'='*60}\n")
    print(body[:3000])
    if len(body) > 3000:
# PURPOSE: Show KB statistics.
        print(f"\n... (truncated, {len(body)} chars total)")


# PURPOSE: aidb-kb の show stats 処理を実行する
def show_stats():
    """Show KB statistics."""
    # Count files
    md_files = list(ROOT_DIR.glob("**/*.md"))
    md_files = [f for f in md_files if "_index" not in str(f)]

    # Year distribution
    years = {}
    for f in md_files:
        parts = str(f.relative_to(ROOT_DIR)).split(os.sep)
        if len(parts) >= 2 and parts[0].isdigit():
            year = parts[0]
            years[year] = years.get(year, 0) + 1

    print(f"\n[STATS] AIDB Knowledge Base Statistics")
    print("=" * 40)
    print(f"Total Articles: {len(md_files)}")
    print(f"\nBy Year:")
    for year in sorted(years.keys()):
        print(f"  {year}: {years[year]} articles")

    # Check index status
    if LANCE_DIR.exists():
        try:
            import lancedb

            db = lancedb.connect(str(LANCE_DIR))
            if "aidb" in get_table_names(db):
                table = db.open_table("aidb")
                print(f"\nIndex Status: [OK] Active")
                print(f"Indexed Chunks: {len(table.to_pandas())}")
            else:
                print(f"\nIndex Status: [X] Table not found")
        except Exception as e:
            print(f"\nIndex Status: [X] Error: {e}")
    else:
        print(f"\nIndex Status: [X] Not built")

    # Model status
    if (MODELS_DIR / "model.onnx").exists():
        print(f"\nModel Status: [OK] Downloaded")
        print(f"Model Path: {MODELS_DIR}")
    else:
        print(f"\nModel Status: [X] Not downloaded")
        print(f"Run: python aidb-kb.py setup")

# PURPOSE: CLI エントリポイント — データパイプラインの直接実行
    print("=" * 40)


# PURPOSE: aidb-kb の main 処理を実行する
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    # Windows console UTF-8 fix
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    if command == "setup":
        setup_model()
    elif command == "index":
        build_index()
    elif command == "search":
        if len(sys.argv) < 3:
            print('Usage: python aidb-kb.py search "query"')
            return
        search(" ".join(sys.argv[2:]))
    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: python aidb-kb.py show <article_id>")
            return
        show_article(sys.argv[2])
    elif command == "stats":
        show_stats()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
