# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
import json
import os
import requests
import datetime
import html2text
from bs4 import BeautifulSoup

ROOT_DIR = os.path.join("Raw", "aidb")
MANIFEST_FILE = os.path.join(ROOT_DIR, "_index", "manifest.jsonl")
RESTORED_MANIFEST = os.path.join(ROOT_DIR, "_index", "manifest_restored.jsonl")
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_session_cookies():
    cookie_file = os.path.join(ROOT_DIR, "_index", "session_cookies.txt")
    cookies = {}
    if os.path.exists(cookie_file):
        with open(cookie_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        cookies[parts[5]] = parts[6]
    return cookies


COOKIES = get_session_cookies()


def fetch_article(url):
    try:
        resp = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=15)
        if resp.status_code != 200:
            return None
        resp.encoding = "utf-8"
        return resp.text
    except Exception:
        return None


def parse_date(date_str):
    # Same date parser as before
    import re

    match = re.search(r"(\d{4})[.-](\d{2})[.-](\d{2})", str(date_str))
    if match:
        return (
            f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
            match.group(1),
            match.group(2),
        )
    return datetime.date.today().strftime("%Y.%m.%d"), "2026", "01"


def restore_entry(entry):
    url = entry.get("url")
    if not url:
        return entry

    post_id = url.split("/")[-1]
    title = entry.get("title", "")

    # 1. Fetch content
    html = fetch_article(url)
    if not html:
        print(f"Failed to fetch {url}")
        return entry

    soup = BeautifulSoup(html, "html.parser")

    # Extract meta
    date_el = soup.select_one(".p-entry__date, .entry-date, .date")
    date_str = date_el.get_text().strip() if date_el else ""
    formatted_date, year, month = parse_date(date_str)

    tags = [t.get_text() for t in soup.select(".post_tags a")]

    # Convert to MD
    h = html2text.HTML2Text()
    h.ignore_links = False
    article_body = (
        soup.select_one(".post_content")
        or soup.select_one("article")
        or soup.find("body")
    )
    markdown = h.handle(str(article_body)) if article_body else ""

    # 2. Save file (Standardized Name)
    save_dir = os.path.join(ROOT_DIR, year, month)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{post_id}.md"
    filepath = os.path.join(save_dir, filename)

    frontmatter = f"""---
source_url: {url}
captured_at: {datetime.datetime.now().isoformat()}
title: "{title}"
publish_date: {formatted_date}
tags: {json.dumps(tags, ensure_ascii=False)}
conversion_method: restoration_script
is_premium: unknown
---

"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + markdown)

    # 3. Update Entry
    entry["file_path"] = filepath
    entry["status"] = "restored"
    entry["captured_at"] = datetime.datetime.now().isoformat()
    return entry


def main():
    if not os.path.exists(MANIFEST_FILE):
        print("Manifest not found")
        return

    restored_count = 0
    new_manifest_lines = []

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"Checking {len(lines)} entries...")

    for i, line in enumerate(lines):
        entry = json.loads(line.strip())
        path = entry.get("file_path", "")

        # Check if file exists
        if not os.path.exists(path):
            print(f"[{i+1}/{len(lines)}] Restoring {entry['url']} ...")
            new_entry = restore_entry(entry)
            new_manifest_lines.append(json.dumps(new_entry, ensure_ascii=False))
            restored_count += 1
        else:
            new_manifest_lines.append(line.strip())

    # Write new manifest
    with open(RESTORED_MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(new_manifest_lines))

    print(f"Restored {restored_count} files.")
    print(f"Saved new manifest to {RESTORED_MANIFEST}")

    # Swap manifests
    os.replace(RESTORED_MANIFEST, MANIFEST_FILE)
    print("Updated manifest.jsonl")


if __name__ == "__main__":
    main()
