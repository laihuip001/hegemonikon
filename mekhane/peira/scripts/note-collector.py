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
OUTPUT_DIR = Path("/home/makaron8426/oikos/mneme/.hegemonikon/raw/note")
API_BASE = "https://note.com/api/v2"

async def fetch_page(session, url, params, headers):
    try:
        async with session.get(url, params=params, headers=headers, timeout=30) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data, params["page"]
    except Exception as e:
        print(f"❌ Error on page {params['page']}: {e}")
        return None, params["page"]

# PURPOSE: CLI エントリポイント — データパイプラインの直接実行
async def async_main():
    print(f"🔍 Collecting articles from note.com/{USER_URLNAME}")
    
    # 出力ディレクトリを作成
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_articles_by_page = {}
    page = 1
    
    async with aiohttp.ClientSession() as session:
        pending = []
        
        # 全ページを取得 (並行処理だがディレイを入れる)
        while page <= 20:  # 最大20ページ
            url = f"{API_BASE}/creators/{USER_URLNAME}/contents"
            params = {"kind": "note", "page": page, "per_page": 20}
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            
            print(f"📄 Fetching page {page}...", flush=True)
            task = asyncio.create_task(fetch_page(session, url, params, headers))
            pending.append(task)
            
            # APIのレートリミットを考慮した待機
            await asyncio.sleep(0.5)
            
            # 完了しているタスクを見て、最後のページに到達したかチェック
            last_page_reached = False
            for t in pending:
                if t.done() and not t.cancelled():
                    res = t.result()
                    if res:
                        data, p = res
                        if data:
                            contents = data.get("data", {}).get("contents", [])
                            is_last = data.get("data", {}).get("isLastPage", True)
                            if not contents or is_last:
                                last_page_reached = True
            
            if last_page_reached:
                print(f"📭 No more articles")
                break
            
            page += 1
            
        # 残りのタスクを待機
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

        # 結果を収集
        for t in pending:
            if t.done() and not t.cancelled():
                res = t.result()
                if res and not isinstance(res, Exception):
                    data, p = res
                    if data:
                        contents = data.get("data", {}).get("contents", [])
                        all_articles_by_page[p] = contents
                        print(f"   Found {len(contents)} articles on page {p}", flush=True)

    all_articles = []
    # ページ順に記事を結合
    for p in sorted(all_articles_by_page.keys()):
        all_articles.extend(all_articles_by_page[p])

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
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
