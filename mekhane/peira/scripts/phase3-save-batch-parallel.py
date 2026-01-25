#!/usr/bin/env python3
"""
phase3-save-batch-parallel.py
Parallel-safe version of the batch save script.

Usage:
  python scripts/phase3-save-batch-parallel.py <batch_id>

This script reads from temp_batch_data_<batch_id>.json and writes to:
  - Raw/aidb/YYYY/MM/<post_id>.md (article files)
  - Raw/aidb/_index/manifest_<batch_id>.jsonl (batch-specific manifest)

After all batches complete, run merge-manifests.py to combine them.
"""

import os
import json
import datetime
import sys

def get_batch_id():
    if len(sys.argv) < 2:
        print("Usage: python phase3-save-batch-parallel.py <batch_id>")
        print("Example: python phase3-save-batch-parallel.py 1")
        sys.exit(1)
    return sys.argv[1]

BATCH_ID = get_batch_id()
TEMP_JSON_FILE = f'temp_batch_data_{BATCH_ID}.json'
ROOT_DIR = os.path.join('Raw', 'aidb')
MANIFEST_FILE = os.path.join(ROOT_DIR, '_index', f'manifest_{BATCH_ID}.jsonl')
SKIP_LOG_FILE = os.path.join(ROOT_DIR, '_index', f'skipped_{BATCH_ID}.txt')

def parse_date(date_str):
    if not date_str:
        return datetime.date.today(), "0000", "00"
    try:
        d = datetime.datetime.strptime(date_str, "%Y.%m.%d")
        return d, d.strftime("%Y"), d.strftime("%m")
    except:
        return datetime.date.today(), "0000", "00"

def save_article(article, manifest_file):
    url = article['url']
    post_id = url.split('/')[-1]
    title = article.get('title', '')
    date_str = article.get('date', '')
    tags = article.get('metadata', {}).get('tags', [])
    content = article.get('markdown', '')

    date_obj, year, month = parse_date(date_str)
    
    # Directory structure: Raw/aidb/YYYY/MM/
    save_dir = os.path.join(ROOT_DIR, year, month)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    filename = f"{post_id}.md"
    filepath = os.path.join(save_dir, filename)

    # Frontmatter construction
    frontmatter = f"""---
source_url: {url}
captured_at: {datetime.datetime.now().isoformat()}
title: "{title}"
publish_date: {date_str}
tags: {json.dumps(tags, ensure_ascii=False)}
conversion_method: browser_subagent_v1_parallel
batch_id: {BATCH_ID}
is_premium: unknown
---

"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    # Update batch-specific manifest
    manifest_entry = {
        "id": post_id,
        "url": url,
        "title": title,
        "file_path": filepath,
        "captured_at": datetime.datetime.now().isoformat(),
        "batch_id": BATCH_ID,
        "status": "success"
    }
    
    manifest_file.write(json.dumps(manifest_entry, ensure_ascii=False) + '\n')
        
    print(f"[Batch {BATCH_ID}] Saved: {filepath}")
    return True

def main():
    if not os.path.exists(TEMP_JSON_FILE):
        print(f"Error: {TEMP_JSON_FILE} not found.")
        sys.exit(1)
    
    with open(TEMP_JSON_FILE, 'r', encoding='utf-8') as f:
        data = f.read()
    
    articles = json.loads(data)
    success_count = 0
    
    # Ensure manifest directory exists
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)

    with open(MANIFEST_FILE, 'a', encoding='utf-8') as manifest_file:
        for art in articles:
            try:
                if save_article(art, manifest_file):
                    success_count += 1
            except Exception as e:
                print(f"[Batch {BATCH_ID}] Error saving {art.get('url', 'unknown')}: {e}")
                with open(SKIP_LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{art.get('url', 'unknown')}\t{str(e)}\n")
    
    print(f"[Batch {BATCH_ID}] Completed: {success_count}/{len(articles)} articles saved.")

if __name__ == "__main__":
    main()
