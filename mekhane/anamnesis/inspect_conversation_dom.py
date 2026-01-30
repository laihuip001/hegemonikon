#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→DOM調査が必要→inspect_conversation_dom が担う
"""
会話ビュー DOM 調査（クリックなし）

現在表示されている状態のまま DOM を調査する。
Agent Manager で会話を手動で開いた状態で実行してください。
"""

import asyncio
from pathlib import Path


CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\current_dom.txt")


async def main():
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
        
        print("[*] Inspecting current view DOM (no clicks)...")
        
        lines = ["=== Current Agent Manager DOM ===\n"]
        
        # 1. 全体のHTML構造を取得
        html = await page.content()
        lines.append(f"Total HTML length: {len(html)}\n")
        
        # 2. 様々なセレクタを試す
        selectors_to_try = [
            # メッセージ関連
            '.prose',
            '.markdown',
            '.markdown-body',
            '[role="article"]',
            '[role="log"]',
            '[role="feed"]',
            # スクロール可能領域
            '.overflow-y-auto',
            '.overflow-auto',
            '.overflow-y-scroll',
            # 一般的なコンテナ
            'article',
            'main',
            # Agent Manager 固有
            '[class*="message"]',
            '[class*="chat"]',
            '[class*="thread"]',
            '[class*="conversation"]',
        ]
        
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    lines.append(f"\n=== {selector}: {len(elements)} matches ===")
                    for i, el in enumerate(elements[:3]):
                        tag = await el.evaluate("el => el.tagName")
                        classes = await el.get_attribute('class') or ""
                        text = await el.text_content()
                        text_len = len(text) if text else 0
                        preview = (text[:300] + "...") if text and len(text) > 300 else (text or "")
                        lines.append(f"\n  [{i}] <{tag}> class='{classes[:100]}'")
                        lines.append(f"      text_len={text_len}")
                        lines.append(f"      preview: {preview[:200]}")
            except Exception as e:
                pass
        
        # 3. テキストが多いdivを探す
        lines.append("\n\n=== Large div analysis ===")
        all_divs = await page.query_selector_all('div')
        large_divs = []
        
        for div in all_divs[:300]:
            try:
                text = await div.text_content()
                if text and len(text) > 2000:
                    classes = await div.get_attribute('class') or ""
                    children_count = await div.evaluate("el => el.children.length")
                    large_divs.append({
                        'el': div,
                        'classes': classes,
                        'text_len': len(text),
                        'children': children_count
                    })
            except:
                pass
        
        large_divs.sort(key=lambda x: x['text_len'], reverse=True)
        
        for i, item in enumerate(large_divs[:10]):
            lines.append(f"\n[Large {i}] text_len={item['text_len']}, children={item['children']}")
            lines.append(f"    class='{item['classes'][:150]}'")
            
            # 子要素の構造を調査
            children = await item['el'].query_selector_all(':scope > *')
            for j, child in enumerate(children[:5]):
                try:
                    c_tag = await child.evaluate("el => el.tagName")
                    c_class = await child.get_attribute('class') or ""
                    c_text = await child.text_content()
                    c_len = len(c_text) if c_text else 0
                    lines.append(f"      child[{j}] <{c_tag}> class='{c_class[:60]}' text_len={c_len}")
                except:
                    pass
        
        # 4. ファイルに書き込み
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
