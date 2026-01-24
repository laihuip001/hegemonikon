#!/usr/bin/env python3
"""
シンプル版: 会話リストのみエクスポート（メッセージ抽出なし）
ファイル生成の動作確認用
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path


OUTPUT_DIR = Path(r"M:\Brain\.hegemonikon\sessions")
CDP_PORT = 9222


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Output: {OUTPUT_DIR} (exists: {OUTPUT_DIR.exists()})")
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # jetski-agent.html を探す
        page = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if 'jetski-agent' in pg.url:
                    page = pg
                    print(f"[*] Found Agent Manager: {pg.url}")
                    break
        
        if not page:
            print("[!] Agent Manager not found")
            return
        
        # 会話ボタンを取得
        await page.wait_for_selector('button.select-none', timeout=5000)
        items = await page.query_selector_all('button.select-none')
        
        conversations = []
        for idx, item in enumerate(items):
            title_el = await item.query_selector('span[data-testid], span.truncate')
            title = await title_el.text_content() if title_el else None
            if title:
                conversations.append({"id": f"conv_{idx}", "title": title.strip()})
        
        print(f"[*] Found {len(conversations)} conversations")
        
        # 各会話をファイルに保存
        for conv in conversations:
            title = conv['title']
            safe_title = ''.join(c if ord(c) < 128 else '_' for c in title)
            safe_title = re.sub(r'[<>:"/\\|?*]', '', safe_title)
            safe_title = re.sub(r'_+', '_', safe_title).strip('_')[:60] or 'untitled'
            
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_{conv['id'][:8]}_{safe_title}.md"
            filepath = OUTPUT_DIR / filename
            
            print(f"  Saving: {filename}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"- **ID**: `{conv['id']}`\n")
                f.write(f"- **Exported**: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write("*メッセージ内容は後で抽出予定*\n")
            
            print(f"    [✓] Saved")
        
        await browser.close()
    
    print(f"\n[✓] Complete: {len(conversations)} files")


if __name__ == "__main__":
    asyncio.run(main())
