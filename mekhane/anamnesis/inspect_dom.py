#!/usr/bin/env python3
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
                    data = await page.evaluate('''() => {
                        const selector = 'div, button, li, span, a';
                        const elements = Array.from(document.querySelectorAll(selector));
                        const total = elements.length;
                        const items = elements.slice(0, 100).map((el, i) => {
                             const tag = el.tagName;
                             const cls = el.getAttribute('class') || '';
                             const role = el.getAttribute('role') || '';
                             const data_attrs = Object.keys(el.dataset).join(',');
                             const text = (el.textContent || '').slice(0, 40).replace(/\\n/g, ' ').trim();
                             return { index: i, tag, cls, role, data_attrs, text };
                        });
                        return { total, items };
                    }''')

                    results.append(f'  Total elements: {data["total"]}')
                    
                    # 最初の100要素を調査
                    for item in data['items']:
                        if item['cls'] or item['role'] or item['data_attrs']:
                            results.append(f'  [{item["index"]}] <{item["tag"]}> class="{item["cls"][:50]}" role="{item["role"]}" data=[{item["data_attrs"]}] text="{item["text"]}"')
                except Exception as e:
                    results.append(f'  Error: {e}')
        
        await browser.close()
    
    OUTPUT_FILE.write_text('\n'.join(results), encoding='utf-8')
    print(f'Output saved to {OUTPUT_FILE}')

if __name__ == "__main__":
    asyncio.run(inspect_dom())
