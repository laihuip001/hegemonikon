# PROOF: [L3/ユーティリティ] O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
phase3-fast-collect.py
High-speed AIDB article collection using aiohttp + BeautifulSoup + html2text.
Optimized for concurrency.

Usage:
  python scripts/phase3-fast-collect.py <start_index> <end_index> [batch_id]

Example:
  python scripts/phase3-fast-collect.py 31 150 1
"""

import asyncio
import aiohttp
import html2text
from bs4 import BeautifulSoup
import json
import datetime
import os
import sys
import time

# Configuration
ROOT_DIR = os.path.join("Raw", "aidb")
URL_LIST_FILE = os.path.join(ROOT_DIR, "_index", "url_list.txt")
COOKIE_FILE = os.path.join(ROOT_DIR, "_index", "session_cookies.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
}

# Concurrency limit
MAX_CONCURRENT_REQUESTS = 10


def load_cookies():
    """Load session cookies from file."""
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookie_str = f.read().strip()
            return {"Cookie": cookie_str}
    return {}


def parse_date(date_str):
    """Parse various date formats to YYYY.MM.DD."""
    if not date_str:
        return "0000.00.00", "0000", "00"

    formats = [
        ("%Y-%m-%dT%H:%M:%S%z", lambda d: d),
        ("%Y-%m-%dT%H:%M:%S+09:00", lambda d: d),
        ("%Y.%m.%d", lambda d: d),
    ]

    for fmt, _ in formats:
        try:
            d = datetime.datetime.strptime(date_str[:19], fmt[: len(date_str)])
            return d.strftime("%Y.%m.%d"), d.strftime("%Y"), d.strftime("%m")
        except Exception:
            continue

    # Fallback: try to extract YYYY-MM-DD pattern
    import re

    match = re.search(r"(\d{4})[.-](\d{2})[.-](\d{2})", date_str)
    if match:
        return f"{match.group(1)}.{match.group(2)}.{match.group(3)}", match.group(1), match.group(2)

    return "0000.00.00", "0000", "00"


async def fetch_html_async(url, session):
    """Fetch HTML content asynchronously."""
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get(url, timeout=timeout) as response:
            if response.status == 404:
                return {"url": url, "status": "error", "error": "404 Not Found"}
            response.raise_for_status()
            text = await response.text(encoding="utf-8")
            return {"url": url, "status": "success", "content": text}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}


def parse_article_content(html_content, url):
    """Parse HTML content and extract metadata/markdown (CPU bound)."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Check for critical error
        if "重大なエラー" in html_content or "Critical Error" in html_content:
            return {"url": url, "status": "error", "error": "WordPress Critical Error"}

        # Extract Metadata
        og_title = soup.find("meta", property="og:title")
        title = (
            og_title["content"]
            if og_title
            else (soup.find("h1").get_text().strip() if soup.find("h1") else "No Title")
        )
        title = title.replace(" - AIDB", "").strip()

        pub_time = soup.find("meta", property="article:published_time")
        date_str = pub_time["content"] if pub_time else ""
        formatted_date, year, month = parse_date(date_str)

        # Tags
        tag_els = soup.select(
            'a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"]'
        )
        tags = list(set([t.get_text().strip() for t in tag_els if t.get_text().strip()]))

        # Content
        content_el = soup.select_one(".p-entry__content, .c-entry__content, .p-entry-content")
        if not content_el:
            content_el = soup.select_one("article")

        html_content_filtered = ""
        if content_el:
            for bad in content_el.select(
                "script, style, .sharedaddy, .related-posts, nav, .wpp-list, .c-share"
            ):
                bad.decompose()
            html_content_filtered = str(content_el)

        # Convert to Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        markdown = h.handle(html_content_filtered)

        return {
            "url": url,
            "title": title,
            "date": formatted_date,
            "year": year,
            "month": month,
            "tags": tags,
            "markdown": markdown,
            "status": "success",
        }
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}


def save_markdown_file(article, batch_id):
    """Save article markdown to disk."""
    post_id = article["url"].split("/")[-1]
    year = article.get("year", "0000")
    month = article.get("month", "00")

    save_dir = os.path.join(ROOT_DIR, year, month)
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, f"{post_id}.md")

    frontmatter = f"""---
source_url: {article['url']}
captured_at: {datetime.datetime.now().isoformat()}
title: "{article['title']}"
publish_date: {article['date']}
tags: {json.dumps(article.get('tags', []), ensure_ascii=False)}
conversion_method: fast_collect_v1
batch_id: {batch_id}
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + article.get("markdown", ""))

    return filepath


def append_to_manifest(article, filepath, batch_id):
    """Append article entry to manifest file."""
    post_id = article["url"].split("/")[-1]
    manifest_file = os.path.join(ROOT_DIR, "_index", f"manifest_fast_{batch_id}.jsonl")
    manifest_entry = {
        "id": post_id,
        "url": article["url"],
        "title": article["title"],
        "file_path": filepath,
        "captured_at": datetime.datetime.now().isoformat(),
        "batch_id": batch_id,
        "status": "success",
    }

    with open(manifest_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(manifest_entry, ensure_ascii=False) + "\n")


async def process_single_url(url, session, semaphore, batch_id):
    """Process a single URL: fetch, parse, save markdown."""
    async with semaphore:
        fetch_result = await fetch_html_async(url, session)

    if fetch_result["status"] != "success":
        return fetch_result

    # Run CPU-bound parsing in executor
    loop = asyncio.get_running_loop()
    article = await loop.run_in_executor(None, parse_article_content, fetch_result["content"], url)

    if article["status"] != "success":
        return article

    # Save markdown in executor (File I/O)
    filepath = await loop.run_in_executor(None, save_markdown_file, article, batch_id)
    article["filepath"] = filepath

    return article


async def process_urls_async(target_urls, batch_id):
    """Main async processing loop."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    cookie_headers = load_cookies()

    print(
        f"[Fast Collect] Processing {len(target_urls)} URLs with concurrency {MAX_CONCURRENT_REQUESTS}"
    )

    # Prepare headers
    final_headers = HEADERS.copy()
    if cookie_headers:
        final_headers.update(cookie_headers)
        print("[Fast Collect] Session cookies loaded.")
    else:
        print(
            "[Fast Collect] WARNING: No session cookies found. Premium content may not be accessible."
        )

    success_count = 0
    error_count = 0

    async with aiohttp.ClientSession(headers=final_headers) as session:
        tasks = []
        for url in target_urls:
            task = asyncio.create_task(process_single_url(url, session, semaphore, batch_id))
            tasks.append(task)

        # Use as_completed to process results as they come in
        for i, future in enumerate(asyncio.as_completed(tasks)):
            result = await future

            if result["status"] == "success":
                # Append to manifest sequentially (safe in main loop)
                append_to_manifest(result, result["filepath"], batch_id)
                print(f"[{i+1}/{len(target_urls)}] OK: {result['title'][:40]}...")
                success_count += 1
            else:
                print(
                    f"[{i+1}/{len(target_urls)}] SKIP: {result['url']} - {result.get('error', 'Unknown')}"
                )
                error_count += 1

                # Log skip
                skip_file = os.path.join(ROOT_DIR, "_index", f"skipped_fast_{batch_id}.txt")
                # Append to skip file sequentially
                with open(skip_file, "a", encoding="utf-8") as f:
                    f.write(f"{result['url']}\t{result.get('error', 'Unknown')}\n")

    print(f"\n[Fast Collect] Completed: {success_count} success, {error_count} errors")


def main():
    if len(sys.argv) < 3:
        print("Usage: python phase3-fast-collect.py <start_index> <end_index> [batch_id]")
        sys.exit(1)

    start_idx = int(sys.argv[1])
    end_idx = int(sys.argv[2])
    batch_id = sys.argv[3] if len(sys.argv) > 3 else "fast"

    # Load URLs
    if not os.path.exists(URL_LIST_FILE):
        print(f"Error: URL list file not found at {URL_LIST_FILE}")
        sys.exit(1)

    with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    target_urls = urls[start_idx:end_idx]

    # Run async loop
    asyncio.run(process_urls_async(target_urls, batch_id))


if __name__ == "__main__":
    main()
