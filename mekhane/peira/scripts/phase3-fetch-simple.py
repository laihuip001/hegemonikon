# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
phase3-fetch-simple.py
Simple HTTP-based article fetcher for AIDB.
Uses requests + BeautifulSoup instead of browser automation.

Usage:
  python scripts/phase3-fetch-simple.py <batch_id> <start_line> <end_line>

Example:
  python scripts/phase3-fetch-simple.py 4 391 510
"""

import os
import sys
import json
import re
import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from html2text import HTML2Text

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Configuration
URL_LIST_FILE = os.path.join("Raw", "aidb", "_index", "url_list.txt")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# PURPOSE: get_args プロパティの取得
def get_args():
    if len(sys.argv) < 4:
        print("Usage: python phase3-fetch-simple.py <batch_id> <start_line> <end_line>")
        print("Example: python phase3-fetch-simple.py 4 391 510")
        sys.exit(1)
    return sys.argv[1], int(sys.argv[2]), int(sys.argv[3])


# PURPOSE: Load URLs from the list file (1-indexed lines).
def load_urls(start_line, end_line):
    """Load URLs from the list file (1-indexed lines)."""
    with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Convert to 0-indexed
    return [line.strip() for line in lines[start_line - 1 : end_line] if line.strip()]


# PURPOSE: Extract metadata from parsed HTML.
def extract_metadata(soup, url):
    """Extract metadata from parsed HTML."""
    result = {"url": url}

    # Title
    h1 = soup.find("h1")
    result["title"] = h1.get_text(strip=True) if h1 else ""

    # Date
    date_el = soup.select_one(".p-article__date") or soup.select_one(".entry-date")
    if date_el:
        result["date"] = date_el.get_text(strip=True)
    else:
        # Fallback: search for date pattern in body
        body_text = soup.get_text()
        match = re.search(r"\d{4}\.\d{2}\.\d{2}", body_text)
        result["date"] = match.group(0) if match else ""

    # Tags
    tag_selectors = [
        'a[href*="/archives/type-tag/"]',
        'a[href*="/archives/tech-tag/"]',
        'a[href*="/archives/app-tag/"]',
        ".post_tag a",
    ]
    tags = set()
    for selector in tag_selectors:
        for tag_el in soup.select(selector):
            tag_text = tag_el.get_text(strip=True)
            if tag_text:
                tags.add(tag_text)

    result["metadata"] = {"tags": list(tags)}
    return result


# PURPOSE: Convert article content to Markdown.
def extract_markdown(soup):
    """Convert article content to Markdown."""
    # Find main article content
    article = (
        soup.select_one("article")
        or soup.select_one(".entry-content")
        or soup.select_one(".post-content")
        or soup.select_one("main")
    )

    if not article:
        # Fallback: use body
        article = soup.find("body")

    if not article:
        return ""

    # Remove unwanted elements
    for unwanted in article.select(
        "script, style, nav, header, footer, .sidebar, .ads, .related-posts, .share-buttons"
    ):
        unwanted.decompose()

    # Convert to Markdown
    h2t = HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = False
    h2t.body_width = 0  # No wrapping

    return h2t.handle(str(article))


# PURPOSE: Fetch and parse a single article.
async def fetch_article(session, url, semaphore):
    """Fetch and parse a single article asynchronously."""
    async with semaphore:
        try:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status == 404:
                    return None, "404 Not Found"

                response.raise_for_status()
                text = await response.text(encoding="utf-8", errors="replace")

                soup = BeautifulSoup(text, "html.parser")

                metadata = extract_metadata(soup, url)
                markdown = extract_markdown(soup)

                return {
                    "url": metadata["url"],
                    "title": metadata["title"],
                    "date": metadata["date"],
                    "metadata": metadata["metadata"],
                    "markdown": markdown,
                }, None

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return None, str(e)


# PURPOSE: Fetch article wrapper to return original URL for logging
async def fetch_article_with_url(session, url, semaphore):
    article, error = await fetch_article(session, url, semaphore)
    return url, article, error


# PURPOSE: CLI エントリポイントの非同期ラッパー — データパイプラインの直接実行
async def main_async():
    batch_id, start_line, end_line = get_args()
    output_file = f"temp_batch_data_{batch_id}.json"
    skip_log_file = os.path.join("Raw", "aidb", "_index", f"skipped_{batch_id}.txt")

    print(f"[Batch {batch_id}] Loading URLs from lines {start_line}-{end_line}...")
    urls = load_urls(start_line, end_line)
    print(f"[Batch {batch_id}] Found {len(urls)} URLs to process.")

    articles = []
    skipped = []
    semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_article_with_url(session, url, semaphore) for url in urls]

        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            url, article, error = await coro

            print(f"[Batch {batch_id}] [{i}/{len(urls)}] Fetching: {url}")

            if error:
                print(f"  -> SKIPPED: {error}")
                skipped.append(f"{url}\t{error}")
            else:
                print(f"  -> OK: {article['title'][:50]}...")
                articles.append(article)

    # Save results
    print(f"\n[Batch {batch_id}] Saving {len(articles)} articles to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    if skipped:
        print(
            f"[Batch {batch_id}] Logging {len(skipped)} skipped URLs to {skip_log_file}..."
        )
        os.makedirs(os.path.dirname(skip_log_file), exist_ok=True)
        with open(skip_log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(skipped))

    print(
        f"\n[Batch {batch_id}] COMPLETE: {len(articles)} success, {len(skipped)} skipped."
    )
    print(f"Next step: python scripts/phase3-save-batch-parallel.py {batch_id}")


# PURPOSE: CLI エントリポイント
def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
