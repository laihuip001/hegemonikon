#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→DOM調査が必要→inspect_message_structure が担う
"""
メッセージ単位の DOM 構造調査

.mx-auto.w-full 内の子要素を詳細調査し、
User と Assistant のメッセージを区別するセレクタを特定する。
"""

import asyncio
from pathlib import Path


CDP_PORT = 9222
OUTPUT_FILE = Path(r"M:\Hegemonikon\mekhane\anamnesis\message_structure.txt")


async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # 正しい Agent Manager ページを選択
        agent_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if 'jetski-agent' in pg.url:
                    try:
                        buttons = await pg.query_selector_all('button.select-none')
                        agent_pages.append((pg, len(buttons)))
                    except:
                        pass
        
        if not agent_pages:
            print("[!] Agent Manager not found")
            return
        
        agent_pages.sort(key=lambda x: x[1], reverse=True)
        page = agent_pages[0][0]
        print(f"[✓] Selected Agent Manager: {agent_pages[0][1]} buttons")
        
        lines = ["=== Message Structure Analysis ===\n"]
        
        # 会話をクリック
        buttons = await page.query_selector_all('button.select-none')
        for btn in buttons:
            try:
                title_el = await btn.query_selector('span[data-testid], span.truncate')
                if title_el:
                    title = await title_el.text_content()
                    if title and len(title.strip()) > 5 and 'Inbox' not in title:
                        print(f"[*] Clicking: {title[:40]}")
                        await btn.click(force=True)
                        await asyncio.sleep(3)
                        lines.append(f"Clicked: {title[:60]}\n")
                        break
            except:
                continue
        
        # メッセージコンテナを探す
        print("[*] Looking for message container...")
        
        # .mx-auto.w-full を探す
        containers = await page.query_selector_all('.mx-auto.w-full')
        lines.append(f"\n=== .mx-auto.w-full containers: {len(containers)} ===")
        
        for i, container in enumerate(containers):
            text = await container.text_content()
            if text and len(text) > 500:
                lines.append(f"\n[Container {i}] text_len={len(text)}")
                
                # 子要素を調査
                children = await container.query_selector_all(':scope > *')
                lines.append(f"  Direct children: {len(children)}")
                
                for j, child in enumerate(children[:20]):
                    try:
                        c_tag = await child.evaluate("el => el.tagName")
                        c_class = await child.get_attribute('class') or ""
                        c_role = await child.get_attribute('role') or ""
                        c_data_role = await child.get_attribute('data-role') or ""
                        c_text = await child.text_content()
                        c_len = len(c_text) if c_text else 0
                        
                        lines.append(f"\n  [{j}] <{c_tag}>")
                        lines.append(f"      class='{c_class[:80]}'")
                        lines.append(f"      role='{c_role}' data-role='{c_data_role}'")
                        lines.append(f"      text_len={c_len}")
                        
                        # 孫要素も調査
                        grandchildren = await child.query_selector_all(':scope > *')
                        lines.append(f"      grandchildren: {len(grandchildren)}")
                        
                        for k, gc in enumerate(grandchildren[:5]):
                            try:
                                gc_tag = await gc.evaluate("el => el.tagName")
                                gc_class = await gc.get_attribute('class') or ""
                                gc_text = await gc.text_content()
                                gc_preview = (gc_text[:80] + "...") if gc_text and len(gc_text) > 80 else (gc_text or "")
                                lines.append(f"        [{k}] <{gc_tag}> class='{gc_class[:50]}' text='{gc_preview.replace(chr(10), ' ')}'")
                            except:
                                pass
                    except:
                        pass
        
        # scrollbar-hide 内を調査
        lines.append("\n\n=== .scrollbar-hide children ===")
        scrollbar_hide = await page.query_selector('.scrollbar-hide')
        if scrollbar_hide:
            children = await scrollbar_hide.query_selector_all(':scope > * > *')  # 孫まで
            lines.append(f"Found {len(children)} grandchildren")
            
            for i, child in enumerate(children[:15]):
                try:
                    c_tag = await child.evaluate("el => el.tagName")
                    c_class = await child.get_attribute('class') or ""
                    c_text = await child.text_content()
                    c_len = len(c_text) if c_text else 0
                    
                    # 特徴を抽出
                    features = []
                    if 'user' in c_class.lower():
                        features.append("USER")
                    if 'assistant' in c_class.lower() or 'agent' in c_class.lower():
                        features.append("ASSISTANT")
                    if 'message' in c_class.lower():
                        features.append("MESSAGE")
                    
                    lines.append(f"\n[{i}] <{c_tag}> text_len={c_len} {' '.join(features)}")
                    lines.append(f"    class='{c_class[:100]}'")
                    
                    if c_text:
                        preview = c_text[:120].replace('\n', ' ')
                        lines.append(f"    preview: '{preview}'")
                except:
                    pass
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[✓] Saved to: {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
