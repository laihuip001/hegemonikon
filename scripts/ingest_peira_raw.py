#!/usr/bin/env python3
"""
Ingest peira/Raw + raw markdown files from git history into Gnōsis.

Usage:
    python3 scripts/ingest_peira_raw.py [--dry-run]

Sources:
    - aidb: YAML frontmatter with title:, source_url:, tags:
    - brain_kb: # heading as title
    - raw/note: # heading as title, Source: in blockquote
"""
# PROOF: [L3/ユーティリティ] <- scripts/ O4→一時投入スクリプト

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mekhane.anamnesis.models.paper import Paper
from mekhane.anamnesis.index import GnosisIndex


COMMIT_REF = "HEAD~1"  # peira/Raw+raw が存在する最後のコミット


def get_deleted_md_files() -> list[str]:
    """git diff で削除された .md ファイル一覧を取得"""
    result = subprocess.run(
        ["git", "diff", "--name-only", COMMIT_REF, "HEAD",
         "--", "mekhane/peira/Raw", "mekhane/peira/raw"],
        capture_output=True, text=True, cwd=ROOT
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".md")]


def read_file_from_git(filepath: str) -> str:
    """git show でファイル内容を復元"""
    result = subprocess.run(
        ["git", "show", f"{COMMIT_REF}:{filepath}"],
        capture_output=True, text=True, cwd=ROOT
    )
    return result.stdout


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """YAML フロントマターを抽出して (metadata, body) を返す"""
    metadata = {}
    body = content
    
    # YAML frontmatter: --- ... ---
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        for line in fm_text.split("\n"):
            line = line.strip().rstrip("\r")
            if ":" in line:
                key, _, val = line.partition(":")
                metadata[key.strip()] = val.strip().strip('"').strip("'")
    
    return metadata, body


def extract_title(filepath: str, metadata: dict, body: str) -> str:
    """ファイルからタイトルを抽出"""
    # 1. YAML frontmatter の title: フィールド
    if "title" in metadata and metadata["title"]:
        return metadata["title"]
    
    # 2. 本文の最初の # ヘッダー
    for line in body.split("\n")[:10]:
        line = line.strip().rstrip("\r")
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            # " - AIDB" のようなサフィックスを除去
            title = re.sub(r'\s*-\s*AIDB\s*$', '', title)
            return title
    
    # 3. ファイル名 (brain_kb は日本語ファイル名)
    stem = Path(filepath).stem
    return stem.replace("_", " ")


def extract_url(filepath: str, metadata: dict, body: str) -> str:
    """ソース URL を抽出"""
    if "source_url" in metadata:
        return metadata["source_url"]
    if "source" in metadata and metadata["source"].startswith("http"):
        return metadata["source"]
    # body から Source: を探す
    for line in body.split("\n")[:10]:
        if "Source" in line and "http" in line:
            match = re.search(r'https?://\S+', line)
            if match:
                return match.group(0)
    return ""


def md_to_paper(filepath: str, content: str) -> Paper:
    """Markdown ファイルを Paper オブジェクトに変換"""
    path = Path(filepath)
    metadata, body = extract_frontmatter(content)
    
    # Determine source from path
    if "aidb" in filepath:
        source = "aidb"
        source_id = path.stem
    elif "brain_kb" in filepath:
        source = "brain_kb"
        source_id = path.stem[:50]  # Long JP filenames
    elif "raw/note" in filepath:
        source = "note"
        source_id = path.stem[:50]
    else:
        source = "peira_raw"
        source_id = path.stem
    
    title = extract_title(filepath, metadata, body)
    url = extract_url(filepath, metadata, body)
    
    # Tags/categories from frontmatter
    categories = ["peira_raw", source]
    if "tags" in metadata:
        tags_str = metadata["tags"].strip("[]")
        for tag in tags_str.split(","):
            tag = tag.strip().strip('"').strip("'")
            if tag:
                categories.append(tag)
    
    # Published date
    published = metadata.get("publish_date") or metadata.get("created") or None
    
    return Paper(
        id=f"gnosis_{source}_{source_id}",
        source=source,
        source_id=source_id,
        title=title,
        abstract=body[:2000],
        url=url,
        published=published,
        categories=categories,
    )


def main():
    dry_run = "--dry-run" in sys.argv
    
    print("=== peira/Raw → Gnōsis 投入 ===")
    
    # 1. Get file list
    md_files = get_deleted_md_files()
    print(f"対象 .md ファイル: {len(md_files)}")
    
    if not md_files:
        print("投入対象なし")
        return
    
    # 2. Convert to Papers
    papers = []
    errors = []
    for filepath in md_files:
        try:
            content = read_file_from_git(filepath)
            if not content.strip():
                continue
            paper = md_to_paper(filepath, content)
            papers.append(paper)
        except Exception as e:
            errors.append((filepath, str(e)))
    
    print(f"Paper 変換成功: {len(papers)}")
    if errors:
        print(f"エラー: {len(errors)}")
        for path, err in errors[:5]:
            print(f"  {path}: {err}")
    
    if dry_run:
        print("\n[DRY RUN] サンプル:")
        for p in papers[:5]:
            print(f"  [{p.source}] {p.title[:70]}")
            if p.url:
                print(f"          URL: {p.url[:60]}")
        print(f"\n...他 {len(papers) - 5} 件")
        print(f"\n投入せず終了 (--dry-run 解除で実行)")
        return
    
    # 3. Ingest into Gnōsis
    print("\nGnōsis に投入中...")
    index = GnosisIndex(ROOT / "gnosis_data")
    added = index.add_papers(papers)
    print(f"\n✅ 完了: {added} 件を Gnōsis に投入")


if __name__ == "__main__":
    main()
