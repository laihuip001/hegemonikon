#!/usr/bin/env python3
"""
全ページを列挙し、内容を確認
"""

import asyncio
from pathlib import Path


CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\all_pages.txt")


async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        lines = ["=== All Browser Pages ===\n"]
        
        for ctx_idx, ctx in enumerate(browser.contexts):
            lines.append(f"\n=== Context {ctx_idx} ===")
            
            for page_idx, page in enumerate(ctx.pages):
                url = page.url
                title = await page.title()
                html_len = len(await page.content())
                
                lines.append(f"\n[Page {ctx_idx}.{page_idx}]")
                lines.append(f"  URL: {url[:100]}")
                lines.append(f"  Title: {title}")
                lines.append(f"  HTML length: {html_len}")
                
                # jetski-agent かどうか
                is_agent_manager = 'jetski-agent' in url
                lines.append(f"  Is Agent Manager: {is_agent_manager}")
                
                # 主要な要素をカウント
                try:
                    buttons = await page.query_selector_all('button')
                    select_none = await page.query_selector_all('button.select-none')
                    divs = await page.query_selector_all('div')
                    
                    lines.append(f"  Buttons: {len(buttons)}")
                    lines.append(f"  button.select-none: {len(select_none)}")
                    lines.append(f"  Divs: {len(divs)}")
                except Exception as e:
                    lines.append(f"  Error: {e}")
                
                # Agent Manager なら詳細調査
                if is_agent_manager:
                    lines.append("\n  --- Agent Manager Details ---")
                    
                    # 会話リスト
                    conv_buttons = await page.query_selector_all('button.select-none')
                    lines.append(f"  Conversation buttons: {len(conv_buttons)}")
                    
                    for i, btn in enumerate(conv_buttons[:5]):
                        try:
                            text = await btn.text_content()
                            lines.append(f"    [{i}] {text[:50] if text else '(empty)'}")
                        except:
                            pass
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
