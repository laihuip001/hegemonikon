# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
cleanup-datefix.py
Fix files in 0000/00 by re-fetching metadata and moving to correct YYYY/MM folder.
"""

import requests
import json
import datetime
import os
import re
import shutil
from bs4 import BeautifulSoup

ROOT_DIR = os.path.join("Raw", "aidb")
PROBLEM_DIR = os.path.join(ROOT_DIR, "0000", "00")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def parse_date(date_str):
    if not date_str:
        return None, None, None

    # Try ISO format
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if match:
        return (
            f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
            match.group(1),
            match.group(2),
        )

    # Try YYYY.MM.DD
    match = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date_str)
    if match:
        return (
            f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
            match.group(1),
            match.group(2),
        )

    return None, None, None


def get_article_date(post_id):
    url = f"https://ai-data-base.com/archives/{post_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        # Try meta tag first
        pub_time = soup.find("meta", property="article:published_time")
        if pub_time and pub_time.get("content"):
            return parse_date(pub_time["content"])

        # Try visible date element
        date_el = soup.select_one(".p-entry__date, .entry-date, .date")
        if date_el:
            return parse_date(date_el.get_text().strip())

        return None, None, None
    except Exception as e:
        print(f"Error fetching {post_id}: {e}")
        return None, None, None


def fix_file(filepath):
    filename = os.path.basename(filepath)
    post_id = filename.replace(".md", "")

    print(f"Processing {post_id}...", end=" ")

    formatted_date, year, month = get_article_date(post_id)

    if not year or not month:
        print("SKIP (no date found)")
        return False

    # Read existing content
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Update frontmatter
    content = re.sub(r"publish_date:.*\n", f"publish_date: {formatted_date}\n", content)

    # Create new directory
    new_dir = os.path.join(ROOT_DIR, year, month)
    os.makedirs(new_dir, exist_ok=True)

    new_path = os.path.join(new_dir, filename)

    # Write to new location
    with open(new_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Remove old file
    os.remove(filepath)

    print(f"MOVED to {year}/{month}")
    return True


def main():
    if not os.path.exists(PROBLEM_DIR):
        print("No 0000/00 directory found.")
        return

    files = [f for f in os.listdir(PROBLEM_DIR) if f.endswith(".md")]
    print(f"Found {len(files)} files to fix.\n")

    fixed = 0
    for filename in files:
        filepath = os.path.join(PROBLEM_DIR, filename)
        if fix_file(filepath):
            fixed += 1

    print(f"\nFixed: {fixed}/{len(files)}")

    # Remove empty 0000/00 if possible
    try:
        os.rmdir(PROBLEM_DIR)
        print(f"Removed empty directory: {PROBLEM_DIR}")
        os.rmdir(os.path.join(ROOT_DIR, "0000"))
        print(f"Removed empty directory: {os.path.join(ROOT_DIR, '0000')}")
    except OSError as e:
        print(f"Could not remove directory: {e}")


if __name__ == "__main__":
    main()
