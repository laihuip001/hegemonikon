#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/peira/ A0→note.com記事収集が必要→note-collectorが担う
"""
note.com 記事収集スクリプト v2
シンプル版 - 即時実行
"""

import asyncio
import aiohttp
import json
import os
import time
from pathlib import Path
from datetime import datetime

# 設定
USER_URLNAME = "tasty_dunlin998"
OUTPUT_DIR = Path("/tmp/note_collector_out")
API_BASE = "https://note.com/api/v2"

async def fetch_page(session, page, semaphore):
    url = f"{API_BASE}/creators/{USER_URLNAME}/contents"
    params = {"kind": "note", "page": page, "per_page": 20}
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    async with semaphore:
        try:
            async with session.get(url, params=params, headers=headers, timeout=30) as resp:
                resp.raise_for_status()
                result = await resp.json()
                # 簡易的なレートリミット対策（0.5秒ではなく、同時実行数を絞りつつ少し待つ）
                await asyncio.sleep(0.1)
                return page, result
        except Exception as e:
            print(f"❌ Error fetching page {page}: {e}")
            return page, None

# PURPOSE: CLI エントリポイント — データパイプラインの直接実行
async def amain():
    print(f"🔍 Collecting articles from note.com/{USER_URLNAME}")
    
    # 出力ディレクトリを作成
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_articles = []
    
    print(f"📄 Fetching up to 20 pages concurrently (with rate limiting)...", flush=True)

    # 同時実行数を制限してAPIへの負荷を抑える
    semaphore = asyncio.Semaphore(5)

    # 実際には存在するページ数だけ取得するために、
    # 5ページずつチャンクで取得し、isLastPageが出たら終了する
    async with aiohttp.ClientSession() as session:
        for chunk_start in range(1, 21, 5):
            chunk_end = min(chunk_start + 5, 21)
            tasks = [fetch_page(session, page, semaphore) for page in range(chunk_start, chunk_end)]
            results = await asyncio.gather(*tasks)
            
            last_page_reached = False
            for page, result in results:
                if not result:
                    last_page_reached = True
                    break

                contents = result.get("data", {}).get("contents", [])
                if not contents:
                    last_page_reached = True
                    break

                all_articles.extend(contents)
                print(f"   Found {len(contents)} articles on page {page} (total: {len(all_articles)})", flush=True)

                if result.get("data", {}).get("isLastPage", True):
                    last_page_reached = True
                    break
            
            if last_page_reached:
                break
    
    print(f"\n📊 Total: {len(all_articles)} articles")
    
    # 各記事を保存
    for i, article in enumerate(all_articles, 1):
        key = article.get("key", "unknown")
        title = article.get("name", "untitled")
        body = article.get("body", "")
        publish_at = article.get("publishAt", "")
        
        # ファイル名生成
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title[:40])
        filename = f"{key}_{safe_title}.md"
        
        # Markdown 生成
        md = f"""# {title}

> **Source**: https://note.com/{USER_URLNAME}/n/{key}
> **Published**: {publish_at}
> **Collected**: {datetime.now().isoformat()}

---

{body}
"""
        
        filepath = OUTPUT_DIR / filename
        filepath.write_text(md, encoding="utf-8")
        print(f"[{i}/{len(all_articles)}] ✅ {filename[:50]}", flush=True)
    
    # マニフェスト保存
    manifest = {
        "user": USER_URLNAME,
        "collected_at": datetime.now().isoformat(),
        "total_articles": len(all_articles),
        "articles": [
            {"key": a.get("key"), "name": a.get("name"), "publishAt": a.get("publishAt")}
            for a in all_articles
        ]
    }
    
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n✅ Done! {len(all_articles)} articles saved to {OUTPUT_DIR}")

def main():
    asyncio.run(amain())

if __name__ == "__main__":
    main()
