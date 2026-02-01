# PROOF: [L3/ユーティリティ] O4→実験スクリプトが必要
import os
import json
import csv
import datetime
import re

import os
import json
import csv
import datetime
import re
import sys

# Read from temp file (or stdin if needed, but file is safer for large data in Antigravity)
TEMP_JSON_FILE = 'temp_batch_data.json'

try:
    if os.path.exists(TEMP_JSON_FILE):
        with open(TEMP_JSON_FILE, 'r', encoding='utf-8') as f:
            DATA_JSON = f.read()
    else:
        # Fallback for testing or empty run
        DATA_JSON = "[]"
        print(f"Warning: {TEMP_JSON_FILE} not found.")
except Exception as e:
    print(f"Error reading input: {e}")
    sys.exit(1)


ROOT_DIR = os.path.join('Raw', 'aidb')
MANIFEST_FILE = os.path.join(ROOT_DIR, '_index', 'manifest.jsonl')
LOG_FILE = os.path.join(ROOT_DIR, '_index', 'capture_log.csv')

def parse_date(date_str):
    if not date_str: return datetime.date.today(), "0000", "00"
    try:
        # Expected format: 2026.01.18 or similar
        d = datetime.datetime.strptime(date_str, "%Y.%m.%d")
        return d, d.strftime("%Y"), d.strftime("%m")
    except Exception:
        return datetime.date.today(), "0000", "00"

def save_article(article):
    url = article['url']
    post_id = url.split('/')[-1]
    title = article['title']
    date_str = article['date']
    tags = article['metadata'].get('tags', [])
    content = article['markdown']

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
conversion_method: browser_subagent_v1
is_premium: unknown
---

"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)
    
    # Update manifest
    manifest_entry = {
        "id": post_id,
        "url": url,
        "title": title,
        "file_path": filepath,
        "captured_at": datetime.datetime.now().isoformat(),
        "status": "success"
    }
    
    with open(MANIFEST_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(manifest_entry, ensure_ascii=False) + '\n')
        
    print(f"Saved: {filepath}")

def main():
    articles = json.loads(DATA_JSON)
    for art in articles:
        save_article(art)

if __name__ == "__main__":
    main()
