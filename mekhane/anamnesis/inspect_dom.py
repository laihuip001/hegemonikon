#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→DOM調査が必要→inspect_dom が担う
"""DOM構造調査スクリプト"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\dom_output.txt")

async def inspect_dom():
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://localhost:9222')
        contexts = browser.contexts
        if not contexts:
            results.append('No contexts')
            OUTPUT_FILE.write_text('\n'.join(results), encoding='utf-8')
            return
        
        # 全ページを確認
        for ctx_idx, ctx in enumerate(contexts):
            for page_idx, page in enumerate(ctx.pages):
                url = page.url
                results.append(f'[Page {ctx_idx}.{page_idx}] {url}')
                
                try:
                    # 会話リストっぽい要素を探す
                    elements = await page.query_selector_all('div, button, li, span, a')
                    results.append(f'  Total elements: {len(elements)}')
                    
                    # 最初の100要素を調査
                    for i, el in enumerate(elements[:100]):
                        tag = await el.evaluate('el => el.tagName')
                        cls = await el.get_attribute('class') or ''
                        role = await el.get_attribute('role') or ''
                        data_attrs = await el.evaluate("el => Object.keys(el.dataset).join(',')")
                        text = (await el.text_content() or '')[:40].replace('\n', ' ').strip()
                        if cls or role or data_attrs:
                            results.append(f'  [{i}] <{tag}> class="{cls[:50]}" role="{role}" data=[{data_attrs}] text="{text}"')
                except Exception as e:
                    results.append(f'  Error: {e}')
        
        await browser.close()
    
    OUTPUT_FILE.write_text('\n'.join(results), encoding='utf-8')
    print(f'Output saved to {OUTPUT_FILE}')

if __name__ == "__main__":
    asyncio.run(inspect_dom())
